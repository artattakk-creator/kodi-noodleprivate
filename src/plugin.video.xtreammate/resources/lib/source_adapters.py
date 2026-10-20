"""Capability-based sources using the existing normalized library index.

Factories/constructors never connect. Only explicit worker methods authenticate,
read remote categories/content, resolve Stalker links, or refresh a playlist.
"""
import hashlib
import json
import os
import time
from urllib.parse import urlsplit

KINDS=('live','vod','series')


class Adapter:
    def __init__(self,portal,filename=None,playlist=None):
        self.portal,self.pid,self.filename=portal,str(portal['id']),filename
        self.playlist=playlist;self._provider=None;self._links={};self._local_urls={};self._catalog_snapshot=None
        self.capabilities=dict(categories=True,live=True,vod=True,series=True,
            series_tree=portal['type']!='m3u',playlist_editor=portal['type']=='m3u',xmltv=bool(portal.get('epg_url')))

    @property
    def provider(self):
        if self._provider is None:
            if self.portal['type']=='xtream':
                from xtream import XtreamClient
                self._provider=XtreamClient(self.portal['xc_host'],self.portal['xc_user'],self.portal['xc_pass'])
            elif self.portal['type']=='stb':
                from stalker import client_for_portal
                self._provider=client_for_portal(self.portal)
                if self._provider is None: raise ValueError('provider unavailable')
        return self._provider

    def authenticate(self,cancel=lambda:False,progress=None):
        if cancel(): raise InterruptedError('source cancelled')
        kind=self.portal['type']
        if kind=='m3u':
            from m3u_store import path,connect,import_playlist
            self.playlist=self.playlist or path(self.pid)
            uri=self.portal.get('m3u_origin') or self.portal.get('m3u_url','')
            if os.path.isfile(self.playlist) and not self.portal.get('m3u_origin'):
                saved=connect(self.playlist)
                try: existing=saved.execute("SELECT v FROM meta WHERE k='active'").fetchone()
                finally: saved.close()
                if existing: return True
            if not uri: raise ValueError('missing playlist')
            import_playlist(uri,self.playlist,cancel,progress)
            return True
        value=self.provider.authenticate()
        if kind=='xtream':
            value=value.get('user_info',{}) if isinstance(value,dict) else {}
            if str(value.get('auth','0')).lower() not in ('1','true'): raise ValueError('authentication failed')
        elif not value: raise ValueError('authentication failed')
        return True

    def categories(self,kind,remote=False):
        if kind not in KINDS: raise ValueError('invalid source kind')
        if not remote:
            from library_index import connect
            db=connect(self.filename)
            if db is not None:
                try:
                    rows=[dict(category_id=r['cid'],category_name=r['title']) for r in db.execute('SELECT cid,title FROM groups WHERE pid=? AND kind=? ORDER BY ordinal',(self.pid,kind))]
                    if rows: return rows
                finally: db.close()
        if self.portal['type']=='m3u':
            from m3u_store import path,categories
            self.playlist=self.playlist or path(self.pid)
            return [dict(category_id=r['gid'],category_name=r['name']) for r in categories(self.playlist,kind)] if os.path.isfile(self.playlist) else []
        if not remote: return []
        method=getattr(self.provider,{'live':'get_live_categories','vod':'get_vod_categories','series':'get_series_categories'}[kind])
        rows=method() or []
        return [dict(category_id=str(r.get('category_id',r.get('id',''))),category_name=str(r.get('category_name') or r.get('title') or r.get('name') or r.get('id')))
                for r in rows if isinstance(r,dict) and r.get('category_id',r.get('id')) is not None]

    def _raw_db(self):
        from library_index import connect
        db=connect(self.filename,write=True)
        db.execute('CREATE TABLE IF NOT EXISTS source_payloads(pid TEXT,ident TEXT,payload TEXT,PRIMARY KEY(pid,ident))')
        return db

    def entries(self,kind,cid,cancel=lambda:False,progress=None,allowed=None):
        cid=str(cid);allowed={str(value) for value in allowed} if allowed is not None else {cid}
        if self.portal['type']=='xtream':
            from library_index import CATALOGS
            yield from self.provider.iter_catalog(CATALOGS[kind][0],cid,cancel=cancel)
            return
        if self.portal['type']=='m3u':
            from m3u_store import entries,path
            self.playlist=self.playlist or path(self.pid)
            for row in entries(self.playlist,kind,cid):
                if cancel(): raise InterruptedError('source cancelled')
                result=dict(name=row['name'],category_id=cid,stream_icon=row['logo'],cover=row['logo'],epg_channel_id=row['epg'],series_flat=kind=='series')
                result['series_id' if kind=='series' else 'stream_id']=row['sid']
                yield result
            return
        # Stalker page generator: no old 50-page ceiling or ten-way fan-out.
        db=self._raw_db();batch=[];rows=[]
        try:
            for row in self._stalker_rows(kind,cid,cancel):
                sid=str(row.get('id') or row.get('stream_id') or '')
                if not sid: continue
                category=str(row.get('tv_genre_id') or row.get('category_id') or cid)
                if category not in allowed: continue
                if len(sid)>256: raise ValueError('provider identity budget exceeded')
                private={k:(v[:8192] if k=='cmd' else v[:4096]) if isinstance(v,str) else v
                    for k,v in row.items() if k in ('id','cmd','name','title','description','screenshot_uri','logo','tv_genre_id','category_id') and isinstance(v,(str,int,float))}
                raw=json.dumps(private,separators=(',',':'))
                if len(raw)>524288: raise ValueError('provider entry budget exceeded')
                ident=hashlib.sha256((kind+'|'+sid+'|'+raw).encode()).hexdigest()
                batch.append((self.pid,ident,raw))
                item=dict(name=str(row.get('name') or row.get('title') or sid),category_id=category,
                    stream_icon=row.get('logo') or row.get('screenshot_uri') or '',cover=row.get('screenshot_uri') or row.get('logo') or '',
                    plot=row.get('description') or '',epg_channel_id=str(row.get('xmltv_id') or ''),source_key=ident)
                item['series_id' if kind=='series' else 'stream_id']=sid;rows.append(item)
                if len(batch)>=256:
                    with db: db.executemany('INSERT OR IGNORE INTO source_payloads VALUES(?,?,?)',batch)
                    yield from rows;batch.clear();rows.clear()
            if batch:
                with db: db.executemany('INSERT OR IGNORE INTO source_payloads VALUES(?,?,?)',batch)
                yield from rows
        finally: db.close()

    def _stalker_rows(self,kind,cid,cancel):
        from utils import http_stream
        from stalker_stream import ArrayReader
        from streaming_json import iter_array
        provider=self.provider
        if not provider.authenticate(): raise ValueError('provider authentication failed')
        last=None;number=0;received=0;deadline=time.monotonic()+300
        while True:
            if cancel(): raise InterruptedError('source cancelled')
            if time.monotonic()>deadline: raise TimeoutError('provider category deadline')
            params=dict(type={'live':'itv','vod':'vod','series':'series'}[kind],action='get_ordered_list',p=number,JsHttpRequest='1-xml',sortby='name',fav='0')
            params['genre' if kind=='live' else 'category']=cid
            count=0;digest=hashlib.sha256()
            with http_stream(provider._portal,params=params,headers=provider._headers(),cancel=cancel) as stream:
                reader=ArrayReader(stream,cancel)
                for row in iter_array(reader,cancel):
                    digest.update(str(row.get('id',row.get('stream_id',''))).encode()+b'\0');count+=1
                    yield row
            if not count: return
            fingerprint=digest.hexdigest()
            if fingerprint==last:
                if number==1: number+=1;continue  # Some MAG APIs alias p=0 to p=1.
                raise ValueError('provider repeats same page')
            received+=count
            metadata=reader.metadata if isinstance(reader.metadata,dict) else {}
            total=int(metadata.get('total_items') or metadata.get('total') or 0)
            if total and received>=total: return
            last=fingerprint;number+=1

    def _reader(self):
        from library_index import Reader
        return Reader(self.pid,self.filename)

    def get_cached_catalog(self,action):
        if self._catalog_snapshot is not None and action in self._catalog_snapshot: return self._catalog_snapshot[action]
        from library_index import CATALOGS
        for kind,(items,cats,id_key) in CATALOGS.items():
            if action==cats: return self.categories(kind)
            if action==items:
                if kind=='live' and self.portal['type']=='m3u':
                    from m3u_store import path,entries
                    self._local_urls={r['sid']:r['url'] for r in entries(self.playlist or path(self.pid),'live')}
                rows=[];offset=0
                while True:
                    chunk,total=self._reader().page(kind,offset=offset,limit=100)
                    rows.extend(dict(r,**{id_key:r['sid']}) for r in chunk);offset+=len(chunk)
                    if not chunk or offset>=total: return rows
        return None

    def _record(self,kind,sid):
        item=self._reader().get(kind,sid)
        if not item: raise ValueError('media is not in active source index')
        if self.portal['type']=='m3u':
            from m3u_store import get,path
            value=get(self.playlist or path(self.pid),sid)
            if not value or not value['enabled'] or value['kind']!=kind: raise ValueError('playlist entry unavailable')
            return value
        db=self._raw_db()
        try:
            row=db.execute('SELECT payload FROM source_payloads WHERE pid=? AND ident=?',(self.pid,item.get('source_key',''))).fetchone()
            if not row: raise ValueError('source payload unavailable')
            return json.loads(row[0])
        finally: db.close()

    def play_uri(self,kind,sid):
        if self.portal['type']=='xtream':
            return (self.provider.live_stream_url(sid,'ts') if kind=='live' else self.provider.vod_stream_url(sid,'mkv')),{}
        row=self._record(kind,sid)
        if self.portal['type']=='m3u': return row['url'],{}
        cmd=str(row.get('cmd') or '')
        if not cmd: raise ValueError('provider command missing')
        provider=self.provider
        uri=provider.get_channel_stream_url(cmd) if kind=='live' else provider.get_vod_stream_url(cmd)
        if not uri: raise ValueError('provider link unavailable')
        return uri,provider.stream_headers()

    def live_stream_url(self,sid,ext='ts'):
        # Called in live callbacks: cache/local only, NEVER create_link/auth.
        if self.portal['type']=='m3u': return self._local_urls.get(str(sid),'')
        return self._links.get(str(sid),'')

    def _cache_key(self,action,extra=None):
        from utils import cache_key
        connection={k:self.portal.get(k) for k in ('m3u_url','stb_url','stb_mac','xc_host','xc_user','xc_pass')}
        return cache_key(json.dumps([self.pid,connection,action,extra],sort_keys=True))

    def _get_json(self,action,extra=None,cached_only=False,**kwargs):
        from utils import cache_get
        value=cache_get(self._cache_key(action,extra),max_age=30*86400)
        return value if value is not None else {}

    def details(self,kind,sid,cancel=lambda:False):
        from utils import cache_get,cache_set
        key=self._cache_key('get_vod_info' if kind=='vod' else 'get_series_info',{'vod_id' if kind=='vod' else 'series_id':str(sid)})
        cached=cache_get(key,max_age=30*86400)
        if cached: return cached
        if cancel(): raise InterruptedError('details cancelled')
        row=self._record(kind,sid)
        if self.portal['type']=='m3u': return {'direct_entry':kind=='series','info':{'plot':''},'episodes':{}}
        if kind=='vod': return {'info':dict(plot=row.get('description') or '')}
        result={'episodes':{}};provider=self.provider
        for season in provider.get_series_seasons(str(sid)):
            if cancel(): raise InterruptedError('details cancelled')
            number=str(season.get('season_number',season.get('season','')))
            if not number.isdigit(): continue  # Never invent season numbers.
            rows=[]
            for episode in provider.get_series_episodes(str(sid),str(season['id'])):
                if cancel(): raise InterruptedError('details cancelled')
                ep=str(episode.get('episode_num',episode.get('episode','')))
                if not ep.isdigit() or not episode.get('id') or not episode.get('cmd'): continue
                rows.append(dict(id=str(episode['id']),episode_num=int(ep),title=episode.get('name') or episode.get('title') or ep,
                    cmd=episode['cmd'],info={}))
            result['episodes'][str(int(number))]=rows
        if result['episodes']: cache_set(key,result)
        return result

    def get_short_epg(self,sid,limit=8,force_refresh=False):
        if self.portal['type']!='stb': return {}
        rows=self.provider.get_short_epg(str(sid),count=limit,force=force_refresh) or []
        result={'epg_listings':[dict(title=r.get('name') or r.get('title') or '',
            start_timestamp=r.get('start_timestamp') or r.get('start') or 0,
            end_timestamp=r.get('stop_timestamp') or r.get('end_timestamp') or r.get('stop') or 0) for r in rows if isinstance(r,dict)]}
        from utils import cache_set
        cache_set(self._cache_key('get_short_epg',{'stream_id':str(sid),'limit':limit}),result)
        return result

    def get_xmltv_epg_url(self):
        if self.portal['type']=='xtream': return self.provider.get_xmltv_epg_url()
        uri=self.portal.get('epg_url','')
        if not uri and self.portal['type']=='m3u':
            from m3u_store import path,connect
            filename=self.playlist or path(self.pid)
            if os.path.isfile(filename):
                db=connect(filename)
                try:
                    row=db.execute("SELECT v FROM meta WHERE k='epg'").fetchone();uri=row[0] if row else ''
                finally: db.close()
        return uri


    def episode_uri(self,series_id,sid,season):
        """Resolve only provider commands in previously cached, validated details."""
        if self.portal['type']!='stb' or not self._reader().get('series',series_id): raise ValueError('episode source unavailable')
        data=self._get_json('get_series_info',{'series_id':str(series_id)},cached_only=True)
        rows=(data.get('episodes') or {}).get(str(season),[])
        episode=next((row for row in rows if str(row.get('id'))==str(sid)),None)
        if not episode or not episode.get('cmd'): raise ValueError('episode metadata unavailable')
        uri=self.provider.get_vod_stream_url(episode['cmd'])
        if not uri: raise ValueError('episode link unavailable')
        return uri,self.provider.stream_headers()


def for_portal(portal,**kwargs):
    if portal.get('type') not in ('xtream','m3u','stb'): raise ValueError('unsupported source')
    return Adapter(portal,**kwargs)

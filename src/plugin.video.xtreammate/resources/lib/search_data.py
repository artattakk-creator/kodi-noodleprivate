"""Worker-only local search; same group filters and guide aliases as the grid."""
import json
import os
import sqlite3
import time
from urllib.parse import quote

KINDS=('live','vod','series')
PAGE=48


def _short_client(portal):
    # Constructing an adapter does not authenticate or fetch. Only cache-only
    # short EPG is read below, just as in the current-time guide viewport.
    if portal.get('type')=='xtream':
        from xtream import XtreamClient
        return XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
    return None


def _now_events(pid,identifiers,now,cancel=lambda:False):
    from guide_store import path
    events={};aliases={};db=None;code='NO_EPG';sources=set()
    if not os.path.exists(path()):return events,aliases,code,0
    try:
        db=sqlite3.connect('file:'+quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.075)
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON')
        deadline=time.monotonic()+1
        db.set_progress_handler(lambda:int(cancel() or time.monotonic()>deadline),1000)
        ids=sorted(identifiers)
        for offset in range(0,len(ids),256):
            chunk=ids[offset:offset+256];marks=','.join('?' for _ in chunk)
            aliases.update(db.execute('SELECT alias,cid FROM guide_alias WHERE pid=? AND alias IN ('+marks+')',[pid]+chunk))
        ids=sorted({aliases.get(ident,ident) for ident in identifiers})
        examined=0
        for offset in range(0,len(ids),256):
            chunk=ids[offset:offset+256];marks=','.join('?' for _ in chunk)
            # No descriptions/full guide hydration, and unrelated channels cannot
            # consume a global result limit before a selected channel is seen.
            cursor=db.execute('SELECT cid,title,source,start,stop FROM programmes WHERE pid=? AND cid IN ('+marks+') AND start<=? AND stop>? ORDER BY source,start DESC',[pid]+chunk+[now,now])
            for row in cursor:
                examined+=1
                if examined>100000:raise ValueError('SEARCH_GUIDE_LIMIT')
                events.setdefault(row['cid'],dict(row));sources.add(row['source'])
        code='READY' if events else 'NO_CURRENT_EPG'
    except (sqlite3.Error,OSError,ValueError):events={};aliases={};code='EPG_UNAVAILABLE';sources.clear()
    finally:
        if db is not None:db.close()
    return events,aliases,code,len(sources)


def revision():
    """Metadata only, never read/deserialize whole databases or cache catalogues."""
    from library_index import path as library_path
    from guide_store import path as guide_path
    from utils import addon_data_dir
    root=addon_data_dir()
    names=[library_path(),guide_path(),os.path.join(root,'xtreammate_groups.json'),
           os.path.join(root,'xtreammate_epg_sources.json')]
    names += [p+'-wal' for p in names[:2]]
    result=[]
    for name in names:
        try:
            value=os.stat(name);result.append((value.st_mtime_ns,value.st_size))
        except OSError:result.append(None)
    return tuple(result)


class LiveSearch:
    """Names first; XML Now and cache-only short EPG in bounded worker slices."""
    def __init__(self,portal,query,reader,now,correlation='',profile=None,cancel=lambda:False):
        from library_index import normalized
        from search_profile import SearchProfile
        self.profile=profile or SearchProfile(correlation);self.cancel=cancel
        self.portal=portal;self.query=query;self.reader=reader;self.now=now
        self.stamp=revision();self.created=time.monotonic();self.expires=now+30;self.final_code=None
        self.tokens=list(dict.fromkeys(normalized(query).split()));self.position=0
        self.channels=None;self.mappings={};self.events={};self.aliases={};self.code='NO_EPG'
        self.client=None;self.client_checked=False;self.phase='names';self.short=[];self.short_position=0
        self.media_cache={};self.slices=0;self.last_trace=0;self.result=[];self.by_sid={}
        self.short_ns=0;self.short_rows=0
        self.counts=dict(channels=0,now_count=0,xml_now=0,short_now=0,manual_count=0,
                         manual_missing=0,alias_count=0,name_hits=0,programme_hits=0,source_count=0)
        self.correlation=self.profile.generation
        with self.profile.span('LIVE_CURSOR_INIT'):
            with self.profile.span('INDEX_QUERY'):
                where='pid=? AND kind=?'+reader._filter('live');args=[portal['id'],'live']
                counts=reader._query('SELECT count(DISTINCT sid) AS n FROM titles WHERE '+where,args,'live')
                self.counts['channels']=counts[0]['n'] if counts else 0
                if self.counts['channels']>50000:raise ValueError('SEARCH_CHANNEL_LIMIT')
                for term in self.tokens:
                    where+=" AND search LIKE ? ESCAPE '\\'"
                    args.append('%'+term.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')
                raw=reader._query('SELECT payload FROM titles WHERE '+where+' GROUP BY sid ORDER BY ordinal LIMIT 50001',args,'live')
                for row in raw:
                    if self.cancel():break
                    item=json.loads(row['payload']);self._add(item,'',False)
                self.counts['name_hits']=len(self.result)
                if self.result:self.profile.emit('FIRST_NAME_MATCH',once=True,rows=len(self.result))

    def valid(self):
        return not self.cancel() and self.stamp==revision() and (not self.done or time.monotonic()-self.created<30 and time.time()<self.expires)

    @property
    def done(self):return self.phase=='done'

    def _add(self,row,title,programme):
        if row['sid'] in self.by_sid:
            pos=self.by_sid[row['sid']]
            # Replace records, never mutate a row already published to Kodi.
            self.result[pos]=dict(row,_now_title=title,_now_match=programme)
        else:
            self.by_sid[row['sid']]=len(self.result)
            self.result.append(dict(row,_now_title=title,_now_match=programme))

    def _prepare(self):
        from epg_sources import configuration
        reader=self.reader
        with self.profile.span('INDEX_QUERY'):
            where='pid=? AND kind=?'+reader._filter('live')
            raw=reader._query('SELECT payload FROM titles WHERE '+where+' GROUP BY sid ORDER BY ordinal LIMIT 50001',
                             (self.portal['id'],'live'),'live')
            if len(raw)>50000:raise ValueError('SEARCH_CHANNEL_LIMIT')
            self.channels=[json.loads(row['payload']) for row in raw]
        if self.cancel():return
        self.mappings=configuration(self.portal['id']).get('mappings',{})
        identifiers=set()
        for row in self.channels:
            manual=self.mappings.get(row['sid'])
            identifiers.update([str(manual)] if manual else [row['sid'],str(row.get('epg_channel_id') or '')])
        identifiers.discard('')
        with self.profile.span('EPG_NOW_SQL'):
            self.events,self.aliases,self.code,count=_now_events(self.portal['id'],identifiers,self.now,self.cancel)
        self.counts['source_count']=count
        stops=[event['stop'] for event in self.events.values() if event.get('stop',0)>self.now]
        if stops:self.expires=min(self.expires,min(stops))
        self.phase='xml'

    def _match(self,row,title,short=False):
        from library_index import normalized
        if title:
            self.counts['now_count']+=1;self.counts['short_now' if short else 'xml_now']+=1
        programme=bool(title and all(t in normalized(title) for t in self.tokens))
        if programme:
            self.counts['programme_hits']+=1;self.profile.emit('FIRST_PROGRAMME_MATCH',once=True,rows=1)
        if row['sid'] in self.by_sid or programme:self._add(row,title,programme)

    def step(self,budget=.2):
        if self.cancel():
            self.phase='done';self.profile.emit('STALE_CANCEL',once=True);return list(self.result),'EPG_PARTIAL'
        if self.done and self.final_code is not None:return list(self.result),self.final_code
        if self.phase=='names':
            self.phase='prepare';return list(self.result),'EPG_PARTIAL'
        self.slices+=1;started=time.monotonic();deadline=started+budget;processed=0
        sampled=self.slices==1 or started-self.last_trace>=1
        if sampled:self.profile.emit('SLICE_BEGIN',slices=self.slices);self.last_trace=started
        if self.phase=='prepare':self._prepare()
        while self.phase=='xml' and not self.cancel():
            if self.position>=len(self.channels):self.phase='short';break
            row=self.channels[self.position];self.position+=1;processed+=1
            manual=self.mappings.get(row['sid']);self.counts['manual_count']+=int(bool(manual))
            keys=[str(manual)] if manual else [row['sid'],str(row.get('epg_channel_id') or '')]
            self.counts['alias_count']+=int(any(self.aliases.get(k,k)!=k for k in keys))
            event=next((self.events[self.aliases.get(k,k)] for k in keys if k and self.aliases.get(k,k) in self.events),None)
            title=event['title'] if event else ''
            if title:self._match(row,title)
            elif manual:self.counts['manual_missing']+=1
            else:self.short.append(row)
            if processed>=256 or time.monotonic()>=deadline:break
        if self.phase=='short':
            self.profile.emit('SHORT_EPG_CACHE_BEGIN',once=True)
            cache_start=time.monotonic_ns();processed=0
            if not self.client_checked:self.client=_short_client(self.portal);self.client_checked=True
            while self.client is not None and self.short_position<len(self.short) and not self.cancel():
                row=self.short[self.short_position];self.short_position+=1;processed+=1
                from epg_views import cached_short_guide
                try:
                    guide=cached_short_guide(self.client,row['sid'],now=self.now);title=guide.get('now','')
                    if title and guide.get('stop',0)>self.now:self.expires=min(self.expires,guide['stop'])
                except (OSError,TimeoutError,ValueError):title=''
                self._match(row,title,short=True)
                if processed>=16 or time.monotonic()>=deadline:break
            self.short_ns+=time.monotonic_ns()-cache_start;self.short_rows+=processed
            if self.client is None or self.short_position>=len(self.short):
                self.phase='done'
                self.profile.emit('SHORT_EPG_CACHE_END',once=True,rows=self.short_rows,duration_ms=self.short_ns//1000000)
        if self.cancel():self.phase='done';self.profile.emit('STALE_CANCEL',once=True)
        code='EPG_PARTIAL' if not self.done else 'READY' if self.counts['now_count'] and self.code!='EPG_UNAVAILABLE' else self.code
        if sampled or self.done:
            from live_diagnostics import record
            record('epg_search',code,matched=len(self.result),scanned=self.position,**self.counts)
            try:
                import xbmc
                xbmc.log('[XCMate][SEARCH_EPG] '+json.dumps(dict(code=code,dispatch=self.correlation,scanned=self.position,matched=len(self.result),**self.counts),sort_keys=True),xbmc.LOGINFO)
            except (ImportError,AttributeError,RuntimeError):pass
        if sampled:self.profile.emit('SLICE_END',slices=self.slices,scanned=self.position,duration_ms=(time.monotonic()-started)*1000)
        if self.done:
            self.final_code=code;self.channels=[];self.short=[];self.events={};self.aliases={}
            self.profile.emit('SCAN_FINAL',once=True,rows=len(self.result),scanned=self.position,**{k:self.counts[k] for k in ('name_hits','programme_hits')})
        return list(self.result),code


def live_matches(portal,query,reader,now):
    cursor=LiveSearch(portal,query,reader,now)
    while True:
        result,code=cursor.step()
        if cursor.done:return result,code


def search(portal,query,kind='vod',offset=0,now=None,incremental=False,continuation=None,correlation='',profile=None,cancel=lambda:False):
    from library_index import Reader,IndexReadError
    from catalog_sync import request
    reader=Reader(portal['id'],timeout=.15,query_seconds=1)
    query=str(query).strip()[:200];result={};cursor=continuation
    if cursor is not None and (cursor.portal['id']!=portal['id'] or cursor.query!=query or not cursor.valid()):cursor=None
    for section in KINDS:
        if cancel():break
        if not portal.get('include_'+section,True):
            result[section]=dict(rows=[],total=0,code='DISABLED');continue
        start=max(0,offset) if section==kind else 0
        cache_key=(section,start)
        if section!='live' and cursor is not None and cache_key in cursor.media_cache:
            result[section]=cursor.media_cache[cache_key];continue
        # The first Live request publishes names before any EPG or media SQL.
        if section!='live' and incremental and kind=='live' and cursor is not None and cursor.phase=='prepare' and cursor.slices==0:
            result[section]=dict(rows=[],total=None,code='INDEX_PENDING');continue
        try:
            state=reader.state(section)
            if not state:
                request(portal,section,portal.get('start_group_id','') if section=='live' else '',priority=5)
                result[section]=dict(rows=[],total=None,code='INDEX_PENDING');continue
            if section=='live':
                if incremental:
                    cursor=cursor or LiveSearch(portal,query,reader,int(time.time() if now is None else now),correlation,profile,cancel)
                    rows,code=cursor.step()
                    result['_cursor']=cursor
                    if not cursor.done:result['_continuation']=cursor
                else:rows,code=live_matches(portal,query,reader,int(time.time() if now is None else now))
                total=len(rows);rows=rows[start:start+PAGE]
            else:rows,total=reader.page(section,query,offset=start,limit=PAGE);code='READY'
            result[section]=dict(rows=rows,total=total,code=code,partial=section=='live' and '_continuation' in result)
            if section!='live' and cursor is not None:
                cursor.media_cache[cache_key]=result[section]
                while len(cursor.media_cache)>12:cursor.media_cache.pop(next(iter(cursor.media_cache)))
        except (IndexReadError,sqlite3.Error,OSError,ValueError):
            result[section]=dict(rows=[],total=None,code='INDEX_ERROR')
    for section in KINDS:result.setdefault(section,dict(rows=[],total=None,code='INDEX_PENDING'))
    if incremental:result['_view']=(kind,offset)
    return result

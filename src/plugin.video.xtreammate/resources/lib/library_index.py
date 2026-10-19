"""Local, versioned SQLite catalog. Writers run in workers; readers never HTTP.

The index contains IDs and provider metadata, never playable stream URLs.
No dependency on SQLite FTS/JSON extensions (not guaranteed by Android Kodi).
"""
import hashlib
import json
import os
import sqlite3
import time
import unicodedata

CATALOGS={'live':('get_live_streams','get_live_categories','stream_id'),
          'vod':('get_vod_streams','get_vod_categories','stream_id'),
          'series':('get_series','get_series_categories','series_id')}
FIELDS=('name','stream_icon','cover','movie_image','backdrop_path','plot','description',
        'year','releaseDate','genre','rating','rating_5based','duration','duration_secs',
        'container_extension','epg_channel_id')
MAX_ROWS=200000


def normalized(value):
    value=unicodedata.normalize('NFKD',str(value or '').casefold())
    return ' '.join(''.join(c for c in value if not unicodedata.combining(c)).split())


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'library_v1.sqlite')


def connect(filename=None, write=False):
    filename=filename or path()
    if not write and not os.path.isfile(filename): return None
    db=sqlite3.connect(filename,timeout=2)
    db.row_factory=sqlite3.Row
    if write:
        page_size=db.execute('PRAGMA page_size').fetchone()[0]
        db.execute('PRAGMA max_page_count='+str((64*1024*1024)//page_size))
        db.executescript('''CREATE TABLE IF NOT EXISTS catalog(
          pid TEXT, kind TEXT, revision TEXT, updated REAL, PRIMARY KEY(pid,kind));
          CREATE TABLE IF NOT EXISTS groups(pid TEXT, kind TEXT, cid TEXT, title TEXT,
          ordinal INTEGER, PRIMARY KEY(pid,kind,cid));
          CREATE TABLE IF NOT EXISTS titles(pid TEXT, kind TEXT, sid TEXT, cid TEXT,
          ordinal INTEGER, title TEXT, search TEXT, added INTEGER, payload TEXT,
          PRIMARY KEY(pid,kind,sid));
          CREATE INDEX IF NOT EXISTS category_titles ON titles(pid,kind,cid,ordinal);
          CREATE INDEX IF NOT EXISTS recent_titles ON titles(pid,kind,added DESC,ordinal);''')
    return db


def revision(client, actions):
    """File metadata, not repeated deserialization of huge catalog JSON files."""
    from utils import cache_dir, _private_cache_dir, addon_data_dir
    roots=set((cache_dir(),_private_cache_dir()))
    paths=[os.path.join(root,client._cache_key(a)+'.json') for root in roots for a in actions]
    paths.append(os.path.join(addon_data_dir(),'xtreammate_groups.json'))
    values=[]
    for filename in paths:
        try:
            st=os.stat(filename); values.append((filename,st.st_mtime_ns,st.st_size))
        except OSError: values.append((filename,0,0))
    return hashlib.sha256(json.dumps(sorted(values)).encode()).hexdigest()


def replace_catalog(pid,kind,entries,groups,allowed=None,seen=None,revision_id='',filename=None):
    from latest_media import added_timestamp
    if not isinstance(entries,list): return False
    if len(entries)>MAX_ROWS: raise ValueError('catalog exceeds index row budget')
    _,_,id_key=CATALOGS[kind]
    allowed=None if allowed is None else set(map(str,allowed))
    def rows():
        unique=set()
        for ordinal,item in enumerate(entries):
            if not isinstance(item,dict): continue
            sid=str(item.get(id_key) or ''); cid=str(item.get('category_id') or '')
            if not sid or sid in unique or (allowed is not None and cid not in allowed): continue
            unique.add(sid)
            title=str(item.get('name') or sid)[:512]
            payload={k:(item[k][:4096] if isinstance(item[k],str) else item[k][:8] if isinstance(item[k],list) else item[k])
                     for k in FIELDS if k in item}
            payload.update(sid=sid,category_id=cid,name=title,kind=kind)
            added=added_timestamp(item.get('added')) or added_timestamp(item.get('date_added')) or (seen or {}).get(sid)
            payload['added_at']=added
            yield (str(pid),kind,sid,cid,ordinal,title,normalized(title),added,json.dumps(payload))
    db=connect(filename,write=True)
    try:
        with db:
            db.execute('DELETE FROM titles WHERE pid=? AND kind=?',(pid,kind))
            db.execute('DELETE FROM groups WHERE pid=? AND kind=?',(pid,kind))
            db.executemany('INSERT INTO titles VALUES(?,?,?,?,?,?,?,?,?)',rows())
            db.executemany('INSERT OR IGNORE INTO groups VALUES(?,?,?,?,?)',[
                (pid,kind,str(g['category_id']),str(g.get('category_name') or g['category_id']),i)
                for i,g in enumerate(groups or []) if isinstance(g,dict) and g.get('category_id') is not None
                and (allowed is None or str(g['category_id']) in allowed)])
            db.execute('INSERT OR REPLACE INTO catalog VALUES(?,?,?,?)',(pid,kind,revision_id,time.time()))
        return True
    finally: db.close()


def refresh(portal,client):
    from group_selection import enabled_ids,load
    from latest_media import first_seen
    for kind,(action,group_action,_) in CATALOGS.items():
        if not portal.get({'live':'include_live','vod':'include_vod','series':'include_series'}[kind],True):
            replace_catalog(portal['id'],kind,[],[])
            continue
        rev=revision(client,(action,group_action))
        state=Reader(portal['id']).state(kind)
        if state and state['revision']==rev: continue
        entries=client.get_cached_catalog(action)
        if not isinstance(entries,list): continue  # Keep previous valid snapshot.
        if not entries and state: continue  # Empty provider result must not empty widgets.
        groups=client.get_cached_catalog(group_action)
        if not isinstance(groups,list):
            groups=[{'category_id':cid,'category_name':cid} for cid in dict.fromkeys(
                str(e.get('category_id') or '') for e in entries if isinstance(e,dict))]
        allowed=enabled_ids(portal['id'],kind,groups)
        seen=first_seen(client._cache_key(action),action,entries) if kind!='live' else {}
        replace_catalog(portal['id'],kind,entries,groups,allowed,seen,rev)


class Reader:
    def __init__(self,pid,filename=None):
        self.pid,self.filename=str(pid),filename
        self._selections={}

    def _filter(self,kind):
        if kind not in self._selections:
            from group_selection import enabled_ids
            groups=self._query('SELECT cid FROM groups WHERE pid=? AND kind=?',(self.pid,kind))
            self._selections[kind]=enabled_ids(self.pid,kind,[{'category_id':g['cid']} for g in groups])
        return ' AND cid IN (SELECT cid FROM selected_categories)'

    def _query(self,sql,args=(),kind=None):
        db=None
        try:
            db=connect(self.filename)
            if db is None: return []
            if kind is not None:
                db.execute('CREATE TEMP TABLE selected_categories(cid TEXT PRIMARY KEY)')
                db.executemany('INSERT INTO selected_categories VALUES(?)',[(cid,) for cid in self._selections[kind]])
            return [dict(r) for r in db.execute(sql,args)]
        except sqlite3.Error: return []
        finally:
            if db is not None: db.close()

    def state(self,kind):
        rows=self._query('SELECT * FROM catalog WHERE pid=? AND kind=?',(self.pid,kind))
        return rows[0] if rows else None

    def groups(self,kind):
        return self._query('SELECT * FROM groups WHERE pid=? AND kind=?'+self._filter(kind)+' ORDER BY ordinal',(self.pid,kind),kind)

    def page(self,kind,query='',category=None,recent=False,offset=0,limit=48,pin=None,include_undated=False):
        where='pid=? AND kind=?'+self._filter(kind); args=[self.pid,kind]
        for token in normalized(query).split():
            where+=' AND search LIKE ? ESCAPE \'\\\''
            args.append('%'+token.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')
        if category is not None: where+=' AND cid=?'; args.append(str(category))
        if recent and not include_undated: where+=' AND added IS NOT NULL'
        counts=self._query('SELECT count(*) AS n FROM titles WHERE '+where,args,kind)
        total=counts[0]['n'] if counts else 0
        order='added IS NULL,added DESC,ordinal' if recent else 'ordinal'
        if pin:
            order='CASE WHEN sid=? THEN 0 ELSE 1 END,'+order
            args=args+[str(pin)]
        rows=self._query('SELECT payload FROM titles WHERE '+where+' ORDER BY '+order+' LIMIT ? OFFSET ?',
                         args+[max(1,min(int(limit),100)),max(0,int(offset))],kind)
        return [json.loads(r['payload']) for r in rows],total

    def get(self,kind,sid):
        rows=self._query('SELECT payload FROM titles WHERE pid=? AND kind=? AND sid=?'+self._filter(kind),(self.pid,kind,str(sid)),kind)
        return json.loads(rows[0]['payload']) if rows else None

    def rail(self,kind,offset=0,limit=24,keep=100):
        keep=max(24,min(int(keep),500))
        rows,total=self.page(kind,recent=True,include_undated=True,offset=offset,limit=min(limit,max(1,keep-offset)))
        return (rows if offset<keep else []),min(total,keep)


def initial_group(portal,groups,start_channel=None,last=''):
    allowed={str(g.get('cid',g.get('category_id',''))) for g in groups}
    candidates=[str((start_channel or {}).get('category_id') or ''),
                str(portal.get('start_group_id') or ''),str(last)]
    return next((cid for cid in candidates if cid in allowed),
                str(groups[0].get('cid',groups[0].get('category_id',''))) if groups else '')

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
FIELDS=('name','stream_icon','cover','cover_big','movie_image','backdrop_path','plot','description',
        'year','releaseDate','genre','rating','rating_5based','duration','duration_secs',
        'container_extension','epg_channel_id','source_key','series_flat',
        'language','languages','quality','video_quality','width','height',
        'num_seasons','season_count','seasons_count','original_name','original_title')
BATCH_ROWS=256


def normalized(value):
    value=unicodedata.normalize('NFKD',str(value or '').casefold())
    return ' '.join(''.join(c for c in value if not unicodedata.combining(c)).split())


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'library_v1.sqlite')


def connect(filename=None, write=False,timeout=2):
    filename=filename or path()
    if not write and not os.path.isfile(filename): return None
    db=sqlite3.connect(filename,timeout=timeout)
    db.row_factory=sqlite3.Row
    if write:
        from import_budget import check_space
        check_space(filename)
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA max_page_count=2147483646')
        db.executescript('''CREATE TABLE IF NOT EXISTS catalog(
          pid TEXT, kind TEXT, revision TEXT, updated REAL, PRIMARY KEY(pid,kind));
          CREATE TABLE IF NOT EXISTS groups(pid TEXT, kind TEXT, cid TEXT, title TEXT,
          ordinal INTEGER, PRIMARY KEY(pid,kind,cid));
          CREATE TABLE IF NOT EXISTS titles(pid TEXT, kind TEXT, sid TEXT, cid TEXT,
          ordinal INTEGER, title TEXT, search TEXT, added INTEGER, payload TEXT,
          PRIMARY KEY(pid,kind,sid));
          CREATE INDEX IF NOT EXISTS category_titles ON titles(pid,kind,cid,ordinal);
          CREATE INDEX IF NOT EXISTS recent_titles ON titles(pid,kind,added DESC,ordinal);
          CREATE TABLE IF NOT EXISTS heads(pid TEXT,kind TEXT,cid TEXT,generation TEXT,
            updated REAL,PRIMARY KEY(pid,kind,cid));
          CREATE TABLE IF NOT EXISTS items_v2(pid TEXT,kind TEXT,sid TEXT,cid TEXT,generation TEXT,
            ordinal INTEGER,title TEXT,search TEXT,added INTEGER,payload TEXT,
            PRIMARY KEY(pid,kind,cid,generation,sid));
          CREATE INDEX IF NOT EXISTS group_order_v2 ON items_v2(pid,kind,cid,generation,ordinal);
          CREATE INDEX IF NOT EXISTS recent_v2 ON items_v2(pid,kind,added DESC);
          CREATE INDEX IF NOT EXISTS identity_v2 ON items_v2(pid,kind,sid);
          CREATE VIEW IF NOT EXISTS readable_titles AS
            SELECT i.pid,i.kind,i.sid,i.cid,i.ordinal,i.title,i.search,i.added,i.payload
              FROM items_v2 i JOIN heads h USING(pid,kind,cid,generation)
            UNION ALL SELECT t.* FROM titles t WHERE NOT EXISTS
              (SELECT 1 FROM heads h WHERE h.pid=t.pid AND h.kind=t.kind AND h.cid=t.cid);
          CREATE TABLE IF NOT EXISTS sync_status(pid TEXT,kind TEXT,cid TEXT,code TEXT,
            updated REAL,received INTEGER,stored INTEGER,discarded INTEGER,error TEXT,
            PRIMARY KEY(pid,kind,cid));
          CREATE TABLE IF NOT EXISTS sync_requests(pid TEXT,kind TEXT,priority INTEGER,
            preferred TEXT,force INTEGER,requested REAL,PRIMARY KEY(pid,kind));
          CREATE TABLE IF NOT EXISTS sync_leases(pid TEXT,kind TEXT,owner TEXT,until REAL,
            PRIMARY KEY(pid,kind));''')
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
    if entries is None or isinstance(entries,(str,bytes,dict)): return False
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
            db.execute('DELETE FROM heads WHERE pid=? AND kind=?',(pid,kind))
            db.execute('DELETE FROM items_v2 WHERE pid=? AND kind=?',(pid,kind))
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


def refresh(portal,client,kinds=None):
    from group_selection import enabled_ids,load
    from latest_media import first_seen
    for kind in (kinds or CATALOGS):
        action,group_action,_=CATALOGS[kind]
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


class IndexReadError(RuntimeError):
    pass


class Reader:
    def __init__(self,pid,filename=None,timeout=2,query_seconds=None):
        self.pid,self.filename=str(pid),filename
        self._selections={}
        self.timeout,self.query_seconds=timeout,query_seconds

    def _filter(self,kind):
        from group_selection import enabled_ids
        groups=self._query('SELECT cid FROM groups WHERE pid=? AND kind=?',(self.pid,kind))
        self._selections[kind]=enabled_ids(self.pid,kind,[{'category_id':g['cid']} for g in groups])
        return ' AND cid IN (SELECT cid FROM selected_categories)'

    def _query(self,sql,args=(),kind=None):
        db=None
        try:
            db=connect(self.filename, timeout=self.timeout)
            if db is None: return []
            # A large catalogue or a temporarily locked legacy database must
            # not monopolize a skin widget/UI invocation. No partial result is
            # published; the caller receives an explicit, retryable error.
            if self.query_seconds is not None:
                deadline=time.monotonic()+self.query_seconds
                db.set_progress_handler(lambda: int(time.monotonic()>=deadline),1000)
            if 'titles' in sql and db.execute("SELECT 1 FROM sqlite_master WHERE name='readable_titles'").fetchone():
                sql=sql.replace('FROM titles','FROM readable_titles')
            if kind is not None:
                db.execute('CREATE TEMP TABLE selected_categories(cid TEXT PRIMARY KEY)')
                db.executemany('INSERT INTO selected_categories VALUES(?)',[(cid,) for cid in self._selections[kind]])
            return [dict(r) for r in db.execute(sql,args)]
        except sqlite3.Error as exc: raise IndexReadError(type(exc).__name__) from exc
        finally:
            if db is not None: db.close()

    def state(self,kind):
        rows=self._query('SELECT * FROM catalog WHERE pid=? AND kind=?',(self.pid,kind))
        return rows[0] if rows else None

    def groups(self,kind):
        return self._query('SELECT * FROM groups WHERE pid=? AND kind=?'+self._filter(kind)+' ORDER BY ordinal',(self.pid,kind),kind)

    def page(self,kind,query='',category=None,recent=False,offset=0,limit=48,pin=None,include_undated=False):
        where='pid=? AND kind=?'+self._filter(kind); args=[self.pid,kind]
        terms=[];term_args=[]
        for token in normalized(query).split():
            terms.append("search LIKE ? ESCAPE '\\'")
            term_args.append('%'+token.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')
        title_where=' AND '.join(terms) or '1'
        genre=None
        if query and kind in ('vod','series'):
            from genre_search import clause
            genre=clause(self,kind,query)
        if genre:
            where+=' AND (('+title_where+') OR ('+genre[0]+'))'
            args+=term_args+genre[1]
        elif terms:
            where+=' AND '+title_where;args+=term_args
        if category is not None: where+=' AND cid=?'; args.append(str(category))
        if recent and not include_undated: where+=' AND added IS NOT NULL'
        counts=self._query('SELECT count(DISTINCT sid) AS n FROM titles AS results WHERE '+where,args,kind)
        total=counts[0]['n'] if counts else 0
        order='added IS NULL,added DESC,ordinal' if recent else 'ordinal'
        if genre:
            order='CASE WHEN search=? THEN 0 WHEN '+title_where+' THEN 1 ELSE 2 END,'+order
            args=args+[normalized(query)]+term_args
        if pin:
            order='CASE WHEN sid=? THEN 0 ELSE 1 END,'+order
            args=args[:-(1+len(term_args))]+[str(pin)]+args[-(1+len(term_args)):] if genre else args+[str(pin)]
        rows=self._query('SELECT payload FROM titles AS results WHERE '+where+' GROUP BY sid ORDER BY '+order+' LIMIT ? OFFSET ?',
                         args+[max(1,min(int(limit),100)),max(0,int(offset))],kind)
        return [json.loads(r['payload']) for r in rows],total

    def get(self,kind,sid):
        rows=self._query('SELECT payload FROM titles WHERE pid=? AND kind=? AND sid=?'+self._filter(kind),(self.pid,kind,str(sid)),kind)
        return json.loads(rows[0]['payload']) if rows else None

    def position(self,kind,sid,category):
        """Read-only ordinal position in one allowed group; never pin/reorder."""
        where='pid=? AND kind=? AND cid=?'+self._filter(kind)
        args=[self.pid,kind,str(category)]
        rows=self._query('SELECT MIN(ordinal) AS n FROM titles WHERE '+where+' AND sid=?',args+[str(sid)],kind)
        ordinal=rows[0]['n'] if rows else None
        if ordinal is None:return None
        rows=self._query('SELECT COUNT(DISTINCT sid) AS n FROM titles WHERE '+where+' AND ordinal<?',args+[ordinal],kind)
        return rows[0]['n'] if rows else None

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


def import_group(pid,kind,cid,entries,filename=None,cancel=lambda:False,progress=None,allowed=None):
    """Batch-committed staging; one small head swap exposes a complete group.

    Staging and previous generation coexist until validation finishes. A crash
    never publishes half JSON; a later sync restarts from the category endpoint.
    Unique SQLite keys replace unbounded Python duplicate/first-seen sets.
    """
    import uuid
    from latest_media import added_timestamp
    from import_budget import check_space
    cid,pid=str(cid),str(pid)
    generation=uuid.uuid4().hex
    db=connect(filename,write=True); target=filename or path()
    action,_,id_key=CATALOGS[kind]
    known_categories={r[0] for r in db.execute('SELECT cid FROM heads WHERE pid=? AND kind=? UNION SELECT cid FROM titles WHERE pid=? AND kind=?',(pid,kind,pid,kind))}
    received=stored=discarded=0; batch=[];touched=set()
    allowed={cid} if allowed is None else set(map(str,allowed))
    def flush():
        nonlocal stored
        if not batch: return
        check_space(target,sum(len(row[-1]) for row in batch)*4)
        previous_changes=db.total_changes
        with db: db.executemany('INSERT OR IGNORE INTO items_v2 VALUES(?,?,?,?,?,?,?,?,?,?)',batch)
        stored+=db.total_changes-previous_changes
        batch.clear()
        if progress: progress(received,stored,discarded)
    try:
        # Clean only this group's abandoned, invisible generations. Bounded
        # deletion also avoids a giant cleanup transaction after a crash.
        _prune(db,pid,kind,cid)
        for item in entries:
            if cancel(): raise InterruptedError('catalogue import cancelled')
            received+=1
            if progress and received % BATCH_ROWS == 0: progress(received,stored,discarded)
            if not isinstance(item,dict): continue
            category=str(item.get('category_id') or '')
            if category not in allowed: discarded+=1;continue
            sid=str(item.get(id_key) or '')[:256]
            if not sid: continue
            title=str(item.get('name') or sid)[:512]
            payload={}
            for key in FIELDS:
                value=item.get(key)
                if isinstance(value,str): payload[key]=value[:4096]
                elif isinstance(value,(int,float,bool)) or value is None: payload[key]=value
                elif isinstance(value,list): payload[key]=[str(v)[:4096] for v in value[:8] if isinstance(v,(str,int,float))]
            added=added_timestamp(item.get('added')) or added_timestamp(item.get('date_added'))
            if not added:
                previous=db.execute('SELECT added FROM readable_titles WHERE pid=? AND kind=? AND sid=? LIMIT 1',
                                    (pid,kind,sid)).fetchone()
                added=previous[0] if previous else (int(time.time()) if category in known_categories else None)
            payload.update(sid=sid,category_id=category,name=title,kind=kind,added_at=added)
            touched.add(category)
            batch.append((pid,kind,sid,category,generation,received,title,normalized(title),added,json.dumps(payload)))
            if len(batch)>=BATCH_ROWS: flush()
        flush()
        if not stored:
            # Empty/filtered/error responses never erase a working group.
            raise ValueError('category response contains no usable entries')
        if cancel(): raise InterruptedError('catalogue import cancelled')
        check_space(target)
        with db:
            for category in touched:
                db.execute('INSERT OR IGNORE INTO groups VALUES(?,?,?,?,?)',(pid,kind,category,category,0))
                db.execute('INSERT OR REPLACE INTO heads VALUES(?,?,?,?,?)',(pid,kind,category,generation,time.time()))
            db.execute('INSERT OR REPLACE INTO catalog VALUES(?,?,?,?)',(pid,kind,generation,time.time()))
        for category in touched: _prune(db,pid,kind,category)
        return dict(received=received,stored=stored,discarded=discarded,categories=sorted(touched))
    except BaseException:
        # Keep the previous head; remove only our uncommitted generation.
        try:
            with db: db.execute('DELETE FROM items_v2 WHERE pid=? AND kind=? AND generation=?',
                                (pid,kind,generation))
        except sqlite3.Error: pass
        raise
    finally: db.close()


def _prune(db,pid,kind,cid):
    while True:
        with db:
            result=db.execute('''DELETE FROM items_v2 WHERE rowid IN
              (SELECT i.rowid FROM items_v2 i WHERE pid=? AND kind=? AND cid=? AND NOT EXISTS
                (SELECT 1 FROM heads h WHERE h.pid=i.pid AND h.kind=i.kind AND h.cid=i.cid
                 AND h.generation=i.generation) LIMIT 256)''',(pid,kind,cid))
        if result.rowcount<256: break


def sync_state(pid,kind,filename=None):
    db=connect(filename)
    if db is None: return []
    try:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='sync_status'").fetchone(): return []
        return [dict(r) for r in db.execute('SELECT * FROM sync_status WHERE pid=? AND kind=? ORDER BY updated DESC',(pid,kind))]
    finally: db.close()


def _sync_note(pid,kind,cid,code,counts=None,exc=None,filename=None):
    from import_budget import safe_failure
    db=connect(filename,write=True)
    counts=counts or {}
    try:
        with db: db.execute('INSERT OR REPLACE INTO sync_status VALUES(?,?,?,?,?,?,?,?,?)',
            (pid,kind,cid,code,time.time(),counts.get('received',0),counts.get('stored',0),counts.get('discarded',0),
             json.dumps(safe_failure(exc)) if exc else ''))
    finally: db.close()


def sync_kind(portal,client,kind,preferred='',force=False,cancel=lambda:False,filename=None,cached_only=False,max_groups=None,requested_at=None,only_categories=None):
    """One kind, enabled categories first, category API only; safe offline fallback."""
    from group_selection import enabled_ids
    import uuid
    pid=str(portal['id']); action,group_action,_=CATALOGS[kind]
    if not portal.get({'live':'include_live','vod':'include_vod','series':'include_series'}[kind],True): return
    db=connect(filename,write=True);owner=uuid.uuid4().hex
    try:
        with db:
            lease=db.execute('SELECT until FROM sync_leases WHERE pid=? AND kind=?',(pid,kind)).fetchone()
            if lease and lease[0]>time.time(): return
            db.execute('INSERT OR REPLACE INTO sync_leases VALUES(?,?,?,?)',(pid,kind,owner,time.time()+330))
        groups=client.get_cached_catalog(group_action)
        if force and not cached_only:
            fresh=client._get_json(group_action,force_refresh=True)
            if isinstance(fresh,list) and fresh: groups=fresh
        if not isinstance(groups,list) and not cached_only:
            groups=client._get_json(group_action)
        if not isinstance(groups,list): raise FileNotFoundError('Category metadata unavailable')
        if only_categories is not None:
            missing=set(map(str,only_categories))-{str(g.get('category_id')) for g in groups}
            if missing and not cached_only:
                fresh=client._get_json(group_action,force_refresh=True)
                if isinstance(fresh,list):groups=fresh
                missing=set(map(str,only_categories))-{str(g.get('category_id')) for g in groups}
            if missing:raise FileNotFoundError('Requested category metadata unavailable')
        allowed=enabled_ids(pid,kind,groups)
        if only_categories is not None:allowed=set(allowed)&set(only_categories)
        active=[g for g in groups if str(g.get('category_id')) in allowed and (only_categories is None or str(g.get('category_id')) in only_categories)]
        active.sort(key=lambda g:str(g['category_id'])!=str(preferred))
        with db:
            db.executemany('INSERT OR REPLACE INTO groups VALUES(?,?,?,?,?)',[
                (pid,kind,str(g['category_id']),str(g.get('category_name') or g['category_id']),i) for i,g in enumerate(groups)])
        completed=set();processed=0
        for group in active:
            if cancel(): return
            cid=str(group['category_id'])
            if cid in completed: continue
            head=db.execute('SELECT updated FROM heads WHERE pid=? AND kind=? AND cid=?',(pid,kind,cid)).fetchone()
            if head and ((not force and time.time()-head[0]<12*3600) or
                         (requested_at is not None and head[0]>=requested_at)): continue
            prior=db.execute('SELECT code,updated FROM sync_status WHERE pid=? AND kind=? AND cid=?',(pid,kind,cid)).fetchone()
            if requested_at is not None and prior and prior[0] in ('FAILED','CANCELLED') and prior[1]>=requested_at: continue
            if max_groups is not None and processed>=max_groups: return True
            processed+=1
            with db: db.execute('UPDATE sync_leases SET until=? WHERE pid=? AND kind=? AND owner=?',(time.time()+330,pid,kind,owner))
            _sync_note(pid,kind,cid,'INDEXING',filename=filename)
            try:
                def progress(received,stored,discarded):
                    _sync_note(pid,kind,cid,'INDEXING',dict(received=received,stored=stored,discarded=discarded),filename=filename)
                try:
                    entries=client.iter_catalog(action,cid,cached_only=cached_only,cancel=cancel)
                    counts=import_group(pid,kind,cid,entries,filename,cancel,progress,allowed)
                except (OSError,ConnectionError,TimeoutError):
                    if cached_only or head: raise
                    # Cold/offline upgrade only. A global cached array is
                    # scanned once for ALL active groups, never once per group.
                    counts=import_group(pid,kind,cid,client.iter_catalog(action,cid,cached_only=True,cancel=cancel),
                                        filename,cancel,progress,allowed)
                completed.update(counts['categories'])
                for category in counts['categories']:
                    _sync_note(pid,kind,category,'READY',counts,filename=filename)
            except Exception as exc:
                _sync_note(pid,kind,cid,'CANCELLED' if isinstance(exc,InterruptedError) else 'FAILED',exc=exc,filename=filename)
                # Other enabled groups can succeed independently.
    finally:
        with db: db.execute('DELETE FROM sync_leases WHERE pid=? AND kind=? AND owner=?',(pid,kind,owner))
        db.close()


def request_sync(portal,kind,preferred='',priority=20,force=False,filename=None):
    """Small persisted intent, consumed by one service worker. No network."""
    if kind not in CATALOGS or portal.get('type') not in ('xtream','m3u','stb'): return
    db=connect(filename,write=True,timeout=0.05)
    try:
        with db:
            db.execute('''INSERT INTO sync_requests VALUES(?,?,?,?,?,?)
              ON CONFLICT(pid,kind) DO UPDATE SET priority=min(priority,excluded.priority),
              preferred=CASE WHEN excluded.priority<=priority THEN excluded.preferred ELSE preferred END,
              force=max(force,excluded.force),
              requested=CASE WHEN excluded.force=1 THEN excluded.requested ELSE requested END''',
              (str(portal['id']),kind,int(priority),str(preferred),int(force),time.time()))
    finally: db.close()

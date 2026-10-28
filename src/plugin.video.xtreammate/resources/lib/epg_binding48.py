"""Source-qualified manual bindings without changing legacy channel strings.

Only explicit Save writes configuration. Preview reads the retained per-source
archive, never changes source priorities/aliases or writes guide SQLite.
"""
import json
import os
import sqlite3
import time
from urllib.parse import quote


class Mappings(dict):
    def __init__(self,legacy=(),sources=None):
        super().__init__(legacy);self.sources48=dict(sources or {})


def sources(portal):
    from epg_sources import configuration
    from guide_publish44 import source_id
    result=[dict(id='provider',name='Anbieter-EPG / Xtream')]
    for rank,source in enumerate(configuration(portal['id'])['sources'],1):
        if source.get('enabled',True):result.append(dict(id=source_id(source,rank),name=str(source.get('name') or 'XMLTV')[:160]))
    return result


def connection():
    from guide_store import path
    filename=path()
    if not os.path.isfile(filename):return None
    db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.03)
    db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
    deadline=time.monotonic()+.15
    db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
    return db


def channels(pid,source,query='',offset=0):
    named=named_channels(pid,source,query,offset)
    if named:return named
    db=connection()
    if db is None:return []
    try:
        # No wildcard escaping ambiguity; instr treats user text literally.
        values=db.execute('''SELECT DISTINCT cid FROM guide44_inputs
          WHERE pid=? AND source_id=? AND instr(lower(cid),lower(?))>0
          ORDER BY cid LIMIT 100 OFFSET ?''',(str(pid),source,str(query)[:160],max(0,int(offset)))).fetchall()
        return [dict(id=r[0],name=r[0],first=None,last=None) for r in values]
    except sqlite3.Error:return []
    finally:db.close()


def read(db,pid,cid,source,start,stop,limit=48):
    """Read exact source even when two XMLTV feeds use identical channel IDs."""
    try:
        rows=db.execute('''SELECT title,description,start,stop,rank FROM guide44_inputs
          WHERE pid=? AND source_id=? AND cid=? AND start<? AND stop>?
          ORDER BY start,stop LIMIT ?''',(str(pid),source,cid,stop,start,min(256,limit))).fetchall()
        if not rows:
            from programme_index46 import window
            return window(pid,cid,start,stop,limit=limit,source48=source)
        return [dict(name=r[0],descr=r[1],start_timestamp=r[2],stop_timestamp=r[3],source=r[4],_source_index=r[4],source_key46=source) for r in rows]
    except sqlite3.Error:return []


def preview(mappings,sid,cid,source):
    value=Mappings(mappings,getattr(mappings,'sources48',{}))
    value[str(sid)]=str(cid);value.sources48[str(sid)]=dict(channel=str(cid),source=str(source))
    return value


def save(portal,sid,cid,source):
    if source not in {r['id'] for r in sources(portal)}:raise ValueError('SOURCE_NOT_CONFIGURED')
    if not str(cid) or len(str(cid))>512:raise ValueError('CHANNEL_REQUIRED')
    from profile_transaction import writing
    from epg_sources import configuration,_save
    with writing(timeout=.2):
        state=configuration(portal['id'])
        state['mappings'][str(sid)]=str(cid)
        state.setdefault('source_mappings48',{})[str(sid)]=dict(channel=str(cid),source=source)
        _save(portal['id'],state)
    return True


def binding(mappings,sid):
    value=getattr(mappings,'sources48',{}).get(str(sid))
    if (isinstance(value,dict) and value.get('channel')==mappings.get(str(sid))
            and isinstance(value.get('source'),str)):
        return value
    return None


def stage_channels(pid,generation,source,rows,guide=None):
    from programme_index46 import connect
    db=None
    try:
        db=connect(True,guide)
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS source_channels48(pid TEXT,source_id TEXT,cid TEXT,name TEXT,PRIMARY KEY(pid,source_id,cid))')
            db.execute('CREATE TABLE IF NOT EXISTS pending_channels48(generation TEXT,pid TEXT,source_id TEXT,cid TEXT,name TEXT,PRIMARY KEY(generation,pid,source_id,cid))')
            db.executemany('INSERT OR REPLACE INTO pending_channels48 VALUES(?,?,?,?,?)',[(generation,str(pid),source,str(cid)[:512],str(name)[:512]) for cid,name in rows])
        return True
    except (OSError,sqlite3.Error,ValueError):return False
    finally:
        if db is not None:db.close()


def finish_channels(pid,generation,publish,guide=None):
    from programme_index46 import connect
    db=None
    try:
        db=connect(False,guide)
        if db is None or not db.execute("SELECT 1 FROM sqlite_master WHERE name='pending_channels48'").fetchone():return
        db.close();db=connect(True,guide)
        with db:
            if publish:
                db.execute('''INSERT OR REPLACE INTO source_channels48 SELECT pid,source_id,cid,name
                  FROM pending_channels48 WHERE pid=? AND generation=?''',(str(pid),generation))
            db.execute('DELETE FROM pending_channels48 WHERE pid=? AND generation=?',(str(pid),generation))
    except (OSError,sqlite3.Error,ValueError):pass
    finally:
        if db is not None:db.close()


def named_channels(pid,source,query='',offset=0):
    from programme_index46 import connect
    db=None
    try:
        db=connect(False)
        if db is None:return []
        deadline=time.monotonic()+.15;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        return [dict(id=r[0],name=r[1],first=None,last=None) for r in db.execute('''SELECT cid,name FROM source_channels48
          WHERE pid=? AND source_id=? AND (instr(lower(cid),lower(?))>0 OR instr(lower(name),lower(?))>0)
          ORDER BY cid LIMIT 100 OFFSET ?''',(str(pid),source,str(query)[:160],str(query)[:160],max(0,int(offset))))]
    except (OSError,sqlite3.Error,ValueError):return []
    finally:
        if db is not None:db.close()


def qualified_cache(cache,mappings,sid):
    """Pure source proof for every Now/Next caller, including startup preload."""
    selected=binding(mappings,sid)
    if not selected:return cache
    cid=selected['channel'];source=selected['source']
    rows=cache.get(cid,[]) if isinstance(cache,dict) else []
    return {cid:[row for row in rows if isinstance(row,dict) and
        (row.get('source_key46') or row.get('epg_source46'))==source]}

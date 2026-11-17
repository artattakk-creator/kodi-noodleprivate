"""Source-qualified manual bindings without changing legacy channel strings.

Only explicit Save writes configuration. Preview reads the retained per-source
archive, never changes source priorities/aliases or writes guide SQLite.
"""
import json
from contextlib import contextmanager
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


def channels(pid,source,query='',offset=0,strict482=False):
    from mapping_search482 import search,MappingReadError
    try:return search(pid,source,str(query)[:160],offset)
    except MappingReadError:
        if strict482:raise
        return []


def read(db,pid,cid,source,start,stop,limit=48,strict=False):
    """Read exact source even when two XMLTV feeds use identical channel IDs."""
    try:
        rows=db.execute('''SELECT title,description,start,stop,rank FROM guide44_inputs
          WHERE pid=? AND source_id=? AND cid=? AND start<? AND stop>?
          ORDER BY start,stop LIMIT ?''',(str(pid),source,cid,stop,start,min(256,limit))).fetchall()
        if not rows:
            from programme_index46 import window
            return window(pid,cid,start,stop,limit=limit,source48=source)
        return [dict(name=r[0],descr=r[1],start_timestamp=r[2],stop_timestamp=r[3],source=r[4],_source_index=r[4],source_key46=source) for r in rows]
    except sqlite3.Error:
        if strict:raise
        return []


def preview(mappings,sid,cid,source):
    value=Mappings(mappings,getattr(mappings,'sources48',{}))
    value[str(sid)]=str(cid);value.sources48[str(sid)]=dict(channel=str(cid),source=str(source))
    return value


def save(portal,sid,cid,source):
    if not str(cid) or len(str(cid))>512:raise ValueError('CHANNEL_REQUIRED')
    if not str(sid) or len(str(sid))>256:raise ValueError('SENDER_REQUIRED')
    from profile_transaction import writing
    from epg_sources import configuration,_save,_load_all
    with writing(timeout=.2):
        if source not in {r['id'] for r in sources(portal)}:raise ValueError('SOURCE_NOT_CONFIGURED')
        # Retain future/unknown portal fields rather than rebuilding the entry.
        state=dict(_load_all().get(str(portal['id']),{}))
        state.update(configuration(portal['id']))
        state['mappings'][str(sid)]=str(cid)
        state.setdefault('source_mappings48',{})[str(sid)]=dict(channel=str(cid),source=source)
        _save(portal['id'],state)
    return True


class MappingSaveError(ValueError):
    def __init__(self,code):
        self.code=code
        super().__init__(code)


def commit_verified(portal,sid,cid,source,prepare=None):
    """Linearize write, cold readback and RO view preparation on the worker."""
    from profile_transaction import writing
    from epg_sources import _load_all,configuration
    from epg_handoff63 import profile_scope
    sid=str(sid);pid=str(portal['id'])
    with writing(timeout=.2):
        before=_load_all().get(pid,{})
        receipt=dict(pid=pid,sid=sid,profile474=profile_scope(),
                     target=dict(channel=str(cid),source=str(source)),before={})
        for field in ('mappings','source_mappings48'):
            values=before.get(field,{})
            receipt['before'][field]=dict(container=field in before,present=sid in values,value=values.get(sid))
        stage='MAPPING_WRITE_FAILED'
        try:
            if not save(portal,sid,cid,source):raise MappingSaveError(stage)
            stage='MAPPING_READBACK_FAILED'
            state=configuration(pid)
            if binding(state['mappings'],sid)!=receipt['target']:raise MappingSaveError(stage)
            stage='MAPPING_RELOAD_FAILED'
            receipt['prepared']=prepare() if prepare is not None else None
            if binding(configuration(pid)['mappings'],sid)!=receipt['target']:raise MappingSaveError('MAPPING_CONFLICT')
            receipt['stamp474']=_stamp474()
            return receipt
        except Exception:
            try:rollback_verified(receipt)
            except Exception as exc:raise MappingSaveError(getattr(exc,'code','MAPPING_ROLLBACK_UNCONFIRMED')) from None
            raise MappingSaveError(stage) from None


def _stamp474():
    from epg_sources import _file_path
    value=os.stat(_file_path())
    return (value.st_dev,value.st_ino,value.st_mtime_ns,value.st_ctime_ns,value.st_size)


@contextmanager
def confirm_verified(receipt):
    """Guard GUI publication by atomic-file identity under the existing .2s lock.

    Only one metadata stat on the GUI owner; no JSON, SQL or network read.
    Every cooperating config writer uses atomic replacement, so another write
    invalidates the receipt even when callbacks or revision notifications fail.
    """
    from profile_transaction import writing
    from epg_handoff63 import profile_scope
    if receipt['profile474']!=profile_scope():raise MappingSaveError('MAPPING_PROFILE_CHANGED')
    with writing(timeout=.2):
        if tuple(receipt['stamp474'])!=_stamp474():raise MappingSaveError('MAPPING_CONFLICT')
        yield


def rollback_verified(receipt):
    """Restore only this unchanged transaction's tuple, never a newer choice."""
    from profile_transaction import writing
    from epg_sources import _load_all,_write_all
    from epg_handoff63 import profile_scope
    if receipt['profile474']!=profile_scope():raise MappingSaveError('MAPPING_PROFILE_CHANGED')
    with writing(timeout=.2):
        data=_load_all();entry=data.get(receipt['pid'],{});sid=receipt['sid']
        actual=dict(channel=entry.get('mappings',{}).get(sid),source=entry.get('source_mappings48',{}).get(sid,{}).get('source'))
        def matches_before(value):
            return all((sid in value.get(field,{}))==old['present'] and value.get(field,{}).get(sid)==old['value'] for field,old in receipt['before'].items())
        if matches_before(entry):return True
        if actual!=receipt['target']:raise MappingSaveError('MAPPING_CONFLICT')
        for field,old in receipt['before'].items():
            values=entry.setdefault(field,{})
            if old['present']:values[sid]=old['value']
            else:values.pop(sid,None)
            if not values and not old['container']:entry.pop(field,None)
        _write_all(data)
        if not matches_before(_load_all().get(receipt['pid'],{})):raise MappingSaveError('MAPPING_ROLLBACK_UNCONFIRMED')
        from epg_status import changed
        changed(receipt['pid'])
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
    from local_epg import for_channel
    cache=for_channel(cache,sid)
    selected=binding(mappings,sid)
    if not selected:return cache
    cid=selected['channel'];source=selected['source']
    rows=cache.get(cid,[]) if isinstance(cache,dict) else []
    return {cid:[row for row in rows if isinstance(row,dict) and
        (row.get('source_key46') or row.get('epg_source46'))==source]}

"""Read-only views of the successfully published guide_v1 snapshot.

Shared by grid, live/mini snapshots and widgets. No importer, DB creation,
provider request or independent persistent cache. Connections stay on the caller
worker; aliases and programmes are read in one SQLite transaction.
"""
import os
import sqlite3
import time
from urllib.parse import quote


def channel_keys(channel, mappings):
    extra=channel.extra if hasattr(channel,'extra') else channel
    sid=str(extra.get('stream_id',extra.get('sid','')))
    provider=str(getattr(channel,'tvg_id',extra.get('epg_channel_id','')) or '')
    manual=(mappings or {}).get(sid)
    return sid,([str(manual)] if manual else list(dict.fromkeys(k for k in (sid,provider) if k)))


class View(dict):
    def __init__(self):
        super().__init__();self.canonical={};self.revision=None;self.code='NOT_CREATED'


def window(pid,channels,mappings,start,stop,limit=48,focus_sid='',history=False,budget=.4):
    from guide_store import path
    filename=path()
    if not filename or not os.path.isfile(filename):return None
    db=None
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON')
        deadline=time.monotonic()+budget
        db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        db.execute('BEGIN')
        meta=db.execute('SELECT * FROM guide_meta WHERE pid=?',(pid,)).fetchone()
        if not meta:return None
        view=View();view.code='OK';record=dict(meta)
        view.revision=(record.get('revision'),record.get('updated'))
        for channel in channels[:16]:
            sid,keys=channel_keys(channel,mappings)
            for ident in keys:
                if ident in view:continue
                alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(pid,ident)).fetchone()
                cid=alias[0] if alias else ident;view.canonical[ident]=cid
                left=start-6*3600 if history and sid==focus_sid else start
                right=start+10*86400 if history and sid==focus_sid else stop
                cap=256 if history and sid==focus_sid else min(256,limit)
                rows=db.execute('SELECT substr(title,1,512) AS title,substr(description,1,8192) AS description,start,stop,source FROM programmes WHERE pid=? AND cid=? AND stop>? AND start<? ORDER BY start,source,stop LIMIT ?',
                                (pid,cid,left,right,cap)).fetchall()
                view[ident]=[dict(name=r['title'],descr=r['description'],start_timestamp=r['start'],
                                  stop_timestamp=r['stop'],source=r['source'],_source_index=r['source']) for r in rows]
        return view
    except (OSError,sqlite3.Error):return None
    finally:
        if db is not None:db.close()


def now_next(pid,channels,mappings,now=None,client=None):
    """Bounded local batch, including strictly cache-only short-EPG fallback."""
    from epg_views import resolve_guide
    ts=time.time() if now is None else now
    cache=window(pid,channels,mappings,ts,ts+2*86400)
    result={}
    for channel in channels[:16]:
        sid,keys=channel_keys(channel,mappings)
        extra=channel.extra if hasattr(channel,'extra') else channel
        provider=str(getattr(channel,'tvg_id',extra.get('epg_channel_id','')) or '')
        info=resolve_guide(cache or {},provider,sid,ts,client,mappings)
        info['snapshot_revision']=cache.revision if cache is not None else None
        result[sid]=info
    return result

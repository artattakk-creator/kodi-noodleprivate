"""Read-only views of the successfully published guide_v1 snapshot.

Shared by grid, live/mini snapshots and widgets. No importer, DB creation,
provider request or independent persistent cache. Connections stay on the caller
worker; aliases and programmes are read in one SQLite transaction.
"""
import os
import sqlite3
import time
from urllib.parse import quote
from programme_read47 import scoped


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
    import guide_store
    filename=getattr(guide_store,'path',lambda:'')()
    if not filename or not os.path.isfile(filename):
        from programme_snapshot47 import fallback_window
        return fallback_window(pid,channels,mappings,start,stop,limit)
    db=None
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON')
        deadline=time.monotonic()+budget
        db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        db.execute('BEGIN')
        meta=db.execute('SELECT * FROM guide_meta WHERE pid=?',(pid,)).fetchone()
        if not meta:
            from programme_snapshot47 import fallback_window
            return fallback_window(pid,channels,mappings,start,stop,limit)
        view=View();view.code='OK';record=dict(meta)
        view.revision=(record.get('revision'),record.get('updated'))
        for channel in channels[:16]:
            sid,keys=channel_keys(channel,mappings)
            for ident in keys:
                if ident in view:continue
                alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(pid,ident)).fetchone()
                cid=alias[0] if alias else ident;view.canonical[ident]=cid
                left=start  # Current/future before SQL LIMIT; no unsolicited history.
                right=start+21*86400 if history and sid==focus_sid else stop
                cap=256 if history and sid==focus_sid else min(256,limit)
                rows=db.execute('SELECT substr(title,1,512) AS title,substr(description,1,8192) AS description,start,stop,source FROM programmes WHERE pid=? AND cid=? AND stop>? AND start<? ORDER BY start,source,stop LIMIT ?',
                                (pid,cid,left,right,cap)).fetchall()
                view[ident]=[dict(name=r['title'],descr=r['description'],start_timestamp=r['start'],
                                  stop_timestamp=r['stop'],source=r['source'],_source_index=r['source']) for r in rows]
                from programme_index46 import window as prepared_window46
                extra46=prepared_window46(pid,cid,left,right,primary=view[ident],limit=cap)
                view[ident]=sorted(view[ident]+extra46,key=lambda e:e['start_timestamp'])[:cap]
        return view
    except (OSError,sqlite3.Error):return None
    finally:
        if db is not None:db.close()


@scoped
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
        compatibility47=cache is None or getattr(cache,'code','')=='SHARED_LASTGOOD47'
        info=resolve_guide(cache if cache is not None else {},provider,sid,ts,client if compatibility47 else None,mappings)
        info['snapshot_revision']=cache.revision if cache is not None else None
        info['canonical46']=cache.canonical.get(info.get('epg_id',''),'') if cache is not None else ''
        from programme_snapshot47 import bind
        result[sid]=bind(pid,channel,info)
    return result


def next_start(pid,identifiers,now):
    """Search expiry at a real upcoming local event, not a fixed tab timer."""
    import guide_store
    filename=getattr(guide_store,'path',lambda:'')()
    ids=sorted(set(str(i) for i in identifiers if i))
    if not filename or not os.path.isfile(filename) or len(ids)>6000:return None
    db=None
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        deadline=time.monotonic()+.2;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        starts=[]
        for offset in range(0,len(ids),256):
            chunk=ids[offset:offset+256];marks=','.join('?' for _ in chunk)
            row=db.execute('SELECT min(start) FROM programmes WHERE pid=? AND cid IN ('+marks+') AND start>?',[pid]+chunk+[now]).fetchone()
            if row and row[0]:starts.append(row[0])
        return min(starts) if starts else None
    except (sqlite3.Error,OSError):return None
    finally:
        if db is not None:db.close()

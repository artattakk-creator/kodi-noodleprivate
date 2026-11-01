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


@scoped
def window(pid,channels,mappings,start,stop,limit=48,focus_sid='',history=False,budget=.4):
    """Pin one RO guide; core text first, bounded optional metadata second."""
    import guide_store
    from programme_read47 import borrowed,retain
    filename=getattr(guide_store,'path',lambda:'')()
    if not filename or not os.path.isfile(filename):
        from programme_snapshot47 import fallback_window
        return fallback_window(pid,channels,mappings,start,stop,limit)
    db=None;started63=time.perf_counter();deadline=time.monotonic()+budget
    try:
        db=borrowed(filename)
        if db is None:
            raw=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
            raw.row_factory=sqlite3.Row;raw.execute('PRAGMA query_only=ON');db=retain(filename,raw)
        db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        meta=db.execute('SELECT * FROM guide_meta WHERE pid=?',(pid,)).fetchone()
        if not meta:
            from programme_snapshot47 import fallback_window
            return fallback_window(pid,channels,mappings,start,stop,limit)
        view=View();view.code='OK';record=dict(meta);view.revision=(record.get('revision'),record.get('updated'))
        prepared={};tasks=[]
        # Core text first; an expensive sidecar cannot erase another sender.
        for channel in channels[:16]:
            sid,keys=channel_keys(channel,mappings)
            for ident in keys:
                if ident in view:continue
                from epg_binding48 import binding,read as read_source48
                selected48=binding(mappings,sid)
                alias=None if selected48 else db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(pid,ident)).fetchone()
                cid=selected48['channel'] if selected48 else alias[0] if alias else ident
                view.canonical[ident]=cid;source48=selected48['source'] if selected48 else None
                left=start;right=start+21*86400 if history and sid==focus_sid else stop
                cap=256 if history and sid==focus_sid else min(256,limit)
                key=(str(sid),cid,source48,bool(mappings.get(sid)),right,cap)
                if key in prepared:view[ident]=prepared[key];continue
                if selected48:values=read_source48(db,pid,cid,source48,left,right,cap)
                else:
                    rows=db.execute('SELECT substr(title,1,512) AS title,substr(description,1,8192) AS description,start,stop,source FROM programmes WHERE pid=? AND cid=? AND stop>? AND start<? ORDER BY start,source,stop LIMIT ?',(pid,cid,left,right,cap)).fetchall()
                    values=[dict(name=row['title'],descr=row['description'],start_timestamp=row['start'],stop_timestamp=row['stop'],source=row['source'],_source_index=row['source']) for row in rows]
                prepared[key]=values;view[ident]=values;tasks.append((key,cid,sid,source48,left,right,cap))
        for key,cid,sid,source48,left,right,cap in tasks:
            if time.monotonic()>deadline:break
            values=prepared[key]
            if not source48:
                from epg_merge52 import window as merged_window52
                values=merged_window52(pid,sid,cid,left,right,primary=values,limit=cap,manual=key[3])
            from programme_flow48 import enrich
            enriched=[]
            for index,value in enumerate(values):
                if index>=4 or time.monotonic()>deadline:
                    enriched.extend(values[index:]);break
                enriched.extend(enrich(pid,cid,[value],source48,sid48=sid,revision48=view.revision))
            prepared[key][:]=enriched
        return view
    except (OSError,sqlite3.Error) as error63:
        from epg_handoff63 import note
        first63=channels[0] if channels else {};sid63=channel_keys(first63,mappings)[0]
        note('DB_READ',pid,sid63,'EPG_DB_BUDGET' if getattr(error63,'sqlite_errorname','')=='SQLITE_INTERRUPT' else 'EPG_CACHE_UNAVAILABLE',(time.perf_counter()-started63)*1000)
        return None
    finally:
        if db is not None:db.close()


@scoped
def now_next(pid,channels,mappings,now=None,client=None):
    """Bounded local batch, including strictly cache-only short-EPG fallback."""
    from epg_views import resolve_guide
    ts=time.time() if now is None else now
    from epg_handoff63 import get as warm63,remember as remember63,note as note63,register as register63
    from epg_status import revision as revision63
    revision_before63=revision63(pid)
    started63=time.perf_counter()
    cache=window(pid,channels,mappings,ts,ts+2*86400)
    if cache is not None:register63(pid,getattr(cache,'revision',None),expected_revision=revision_before63)
    db_ms63=(time.perf_counter()-started63)*1000
    # Workers retain the complete bounded future window. The thin four-event
    # RAM DTO is only a transient-read fallback and the GUI handoff, not a
    # replacement for catalogue/programme preparation.
    warm={}
    if cache is None:
        for c63 in channels[:16]:
            sid63=channel_keys(c63,mappings)[0]
            warm[sid63]=warm63(pid,sid63,now=ts,mappings=mappings)
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
        if not result[sid].get('now') and warm.get(sid) and warm[sid].get('now') and cache is None:
            result[sid]=warm[sid]
        remember63(pid,channel,result[sid],mappings,expected_revision=revision_before63)
        code63=('READY' if info.get('now') else 'EPG_CACHE_UNAVAILABLE' if cache is None else 'EPG_MAPPING_MISSING' if info.get('reason')=='MANUAL_ID_MISSING' else 'EPG_DATA_MISSING')
        note63('DB_READ',pid,sid,code63,db_ms63,facts=info)
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

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


def window(pid,channels,mappings,start,stop,limit=48,focus_sid='',history=False,budget=.4,text_only65=False):
    # The exact full .64 metadata path stays authoritative for matching/art.
    # Only an explicit display request uses the RAM/text latency projection.
    if text_only65:
        return _text_window65(pid,channels,mappings,start,stop,limit,focus_sid,history,budget,True)
    return _full_window65(pid,channels,mappings,start,stop,limit,focus_sid,history,budget)

def _full_window65(pid,channels,mappings,start,stop,limit=48,focus_sid='',history=False,budget=.4):
    import guide_store
    filename=getattr(guide_store,'path',lambda:'')()
    if not filename or not os.path.isfile(filename):
        from programme_snapshot47 import fallback_window
        return fallback_window(pid,channels,mappings,start,stop,limit)
    db=None
    started63=time.perf_counter()
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
        tasks67=[]
        for channel in channels[:16]:
            sid,keys=channel_keys(channel,mappings)
            for ident in keys:
                if ident in view:continue
                from epg_binding48 import binding,read as read_source48
                selected48=binding(mappings,sid)
                if selected48:
                    cid=selected48['channel'];view.canonical[ident]=cid
                    values48=read_source48(db,pid,cid,selected48['source'],start,stop,limit)
                    view[ident]=values48
                    tasks67.append((ident,cid,sid,selected48['source'],start,stop,limit))
                    continue
                alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(pid,ident)).fetchone()
                cid=alias[0] if alias else ident;view.canonical[ident]=cid
                left=start  # Current/future before SQL LIMIT; no unsolicited history.
                right=start+21*86400 if history and sid==focus_sid else stop
                cap=256 if history and sid==focus_sid else min(256,limit)
                rows=db.execute('SELECT substr(title,1,512) AS title,substr(description,1,8192) AS description,start,stop,source FROM programmes WHERE pid=? AND cid=? AND stop>? AND start<? ORDER BY start,source,stop LIMIT ?',
                                (pid,cid,left,right,cap)).fetchall()
                view[ident]=[dict(name=r['title'],descr=r['description'],start_timestamp=r['start'],
                                  stop_timestamp=r['stop'],source=r['source'],_source_index=r['source']) for r in rows]
                tasks67.append((ident,cid,sid,None,left,right,cap))
        # Commit all bounded core text before optional sidecar/schema work.
        from epg_resilience67 import optional
        from epg_merge52 import window as merged_window52
        from programme_flow48 import enrich
        for ident,cid,sid,source67,left,right,cap in tasks67:
            if time.monotonic()>deadline:break
            values67=view[ident]
            if source67 is None:
                values67=optional(pid,sid,values67,lambda:merged_window52(pid,sid,cid,left,right,primary=values67,limit=cap,manual=bool(mappings.get(sid))))
            view[ident]=optional(pid,sid,values67,lambda:enrich(pid,cid,values67[:4],source67,sid48=sid,revision48=view.revision)+values67[4:])
        return view
    except (OSError,sqlite3.Error) as error63:
        from epg_handoff63 import note
        first63=channels[0] if channels else {}
        sid63=channel_keys(first63,mappings)[0]
        note('DB_READ',pid,sid63,'EPG_DB_BUDGET' if getattr(error63,'sqlite_errorname','')=='SQLITE_INTERRUPT' else 'EPG_CACHE_UNAVAILABLE',(time.perf_counter()-started63)*1000)
        __import__('epg_read69').record(error63,pid,sid63,(time.perf_counter()-started63)*1000)
        return None
    finally:
        if db is not None:db.close()


@scoped
def _text_window65(pid,channels,mappings,start,stop,limit=48,focus_sid='',history=False,budget=.4,text_only65=False):
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
        # Source fusion is text work. Prefer gaps before optional rich fields.
        fusion65=sorted(tasks,key=lambda task:any(value['start_timestamp']<=start<value['stop_timestamp'] for value in prepared[task[0]]))
        for key,cid,sid,source48,left,right,cap in fusion65:
            if text_only65 and time.monotonic()>deadline:break
            if not source48:
                from epg_merge52 import window as merged_window52
                from epg_resilience67 import optional
                original67=prepared[key][:]
                prepared[key][:]=optional(pid,sid,original67,lambda:merged_window52(pid,sid,cid,left,right,primary=original67,limit=cap,manual=key[3]))
        for key,cid,sid,source48,left,right,cap in tasks:
            if time.monotonic()>deadline:break
            values=prepared[key]
            from programme_flow48 import enrich
            enriched=[]
            for index,value in enumerate(values):
                if index>=4 or text_only65 and time.monotonic()>deadline:
                    enriched.extend(values[index:]);break
                from epg_resilience67 import optional
                enriched.extend(optional(pid,sid,[value],lambda:enrich(pid,cid,[value],source48,sid48=sid,revision48=view.revision)))
            prepared[key][:]=enriched
        return view
    except (OSError,sqlite3.Error) as error63:
        from epg_handoff63 import note
        first63=channels[0] if channels else {};sid63=channel_keys(first63,mappings)[0]
        note('DB_READ',pid,sid63,'EPG_DB_BUDGET' if getattr(error63,'sqlite_errorname','')=='SQLITE_INTERRUPT' else 'EPG_CACHE_UNAVAILABLE',(time.perf_counter()-started63)*1000)
        __import__('epg_read69').record(error63,pid,sid63,(time.perf_counter()-started63)*1000)
        return None
    finally:
        if db is not None:db.close()


@scoped
def now_next(pid,channels,mappings,now=None,client=None,display_only65=False):
    """Bounded local batch, including strictly cache-only short-EPG fallback."""
    from epg_views import resolve_guide
    ts=time.time() if now is None else now
    from epg_handoff63 import get as warm63,remember as remember63,note as note63,register as register63
    from epg_status import revision as revision63
    revision_before63=revision63(pid)
    if display_only65 and channels:
        prepared74={channel_keys(c,mappings)[0]:warm63(pid,channel_keys(c,mappings)[0],now=ts,mappings=mappings) for c in channels[:16]}
        if prepared74 and all(v and 0<=time.time()-v.get('_published_at63',0)<15 for v in prepared74.values()) and revision63(pid)==revision_before63:
            return prepared74
    started63=time.perf_counter()
    cache=window(pid,channels,mappings,ts,ts+2*86400,**({'text_only65':True} if display_only65 else {}))
    if cache is None:
        from epg_fallback67 import window as fallback67
        cache=fallback67(pid,channels,mappings,ts,ts+2*86400,48)
    if cache is not None:register63(pid,getattr(cache,'revision',None),expected_revision=revision_before63)
    db_ms63=(time.perf_counter()-started63)*1000
    # Workers retain the complete bounded future window. The thin four-event
    # RAM DTO is only a transient-read fallback and the GUI handoff, not a
    # replacement for catalogue/programme preparation.
    warm={channel_keys(c,mappings)[0]:warm63(pid,channel_keys(c,mappings)[0],now=ts,mappings=mappings) for c in channels[:16]}
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
        if (not result[sid].get('now') and warm.get(sid) and warm[sid].get('now')
                and (cache is None or warm[sid].get('snapshot_revision')==info.get('snapshot_revision'))):
            result[sid]=warm[sid]
        if getattr(cache,'code','')!='RAM_LASTGOOD67':remember63(pid,channel,result[sid],mappings,expected_revision=revision_before63)
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

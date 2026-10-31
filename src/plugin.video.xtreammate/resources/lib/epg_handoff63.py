"""Bounded, revision-checked RAM handoff of the ONE local guide's Now/Next.

Kodi Home properties bridge plugin/service interpreters. No database, file,
provider or artwork request is performed by get()/focus callbacks.
"""
import copy
import hashlib
import json
import math
import threading
import time

PREFIX='XCMate.NowNext63.'
MAX_BYTES=24576
_lock=threading.RLock()
_seen={}
_FIELDS=('now','next','description','image','now_time','now_end_time','next_time','next_end_time',
    'start','stop','next_start','next_stop','progress','elapsed','remaining','epg_id','mapping',
    'source_index','reason','snapshot_revision','canonical46','programme_key47')
_EVENT=('title','description','start','stop','source','_source_index','programme_key47','canonical46',
    'source_key46','fact_revision46','subtitle','year','season','episode','genre',
    'xmltv_image','provider_image','epg_source46')


def profile_scope():
    try:
        import xbmcvfs
        value=xbmcvfs.translatePath('special://profile/')
    except (ImportError,AttributeError,RuntimeError):value=''
    return hashlib.sha256(str(value).encode()).hexdigest()


def identity(pid,sid):
    return hashlib.sha256((profile_scope()+'|'+str(pid)+'|'+str(sid)).encode()).hexdigest()


def meta_key(pid):
    return 'XCMate.GuideMeta63.'+identity(pid,'guide')[:32]


def revision_tag(value):
    return json.dumps(value,separators=(',',':'),allow_nan=False)


def observe(pid):
    """Worker-only point read: a DB publication cannot hide behind a warm DTO."""
    import os,sqlite3
    from urllib.parse import quote
    import xbmcgui
    import guide_store
    window=xbmcgui.Window(10000);db=None
    try:
        filename=guide_store.path()
        if not filename or not os.path.isfile(filename):value=None
        else:
            db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.03)
            db.execute('PRAGMA query_only=ON')
            deadline=time.monotonic()+.03
            db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
            row=db.execute('SELECT revision,updated FROM guide_meta WHERE pid=?',(str(pid),)).fetchone()
            value=tuple(row) if row else None
        tag=revision_tag(value)
        if window.getProperty(meta_key(pid))!=tag:window.setProperty(meta_key(pid),tag)
        return tag
    except (OSError,sqlite3.Error,ValueError,TypeError):
        return window.getProperty(meta_key(pid))
    finally:
        if db is not None:db.close()


def note(stage,pid='',sid='',code='READY',duration_ms=0):
    if stage not in ('HOME_FOCUS','HOME_NOW_NEXT_READY','OK_CLICK','FIRST_VIDEO','INFO_VISIBLE',
                     'PLAYER_NOW_NEXT_READY','DB_READ','SNAPSHOT_SEEDED'):return
    codes=('READY','EPG_DATA_MISSING','EPG_MAPPING_MISSING','EPG_CACHE_UNAVAILABLE','EPG_CACHE_STALE',
           'EPG_SNAPSHOT_SCHEDULE_DELAY','EPG_DB_BUDGET','EPG_UI_UPDATE_DELAY')
    if code not in codes:code='EPG_CACHE_UNAVAILABLE'
    try:
        key=(stage,identity(pid,sid),code);now=time.monotonic()
        with _lock:
            if now-_seen.get(key,-100)<2:return
            _seen[key]=now
            while len(_seen)>256:_seen.pop(next(iter(_seen)))
        import xbmc
        xbmc.log('[XCMate][EPG63] stage='+stage+' channel='+key[1][:12]+' code='+code+
                 ' at_ms='+str(int(now*1000))+' duration_ms='+str(max(0,min(300000,int(duration_ms)))),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError):pass


def selector(mappings,sid):
    from epg_binding48 import binding
    return [str((mappings or {}).get(str(sid)) or ''),binding(mappings or {},str(sid))]


def remember(pid,channel,info,mappings=None,expected_revision=None):
    extra=channel.extra if hasattr(channel,'extra') else channel
    sid=str(extra.get('sid',extra.get('stream_id','')))
    if not sid or not isinstance(info,dict):return
    from epg_status import revision
    if expected_revision is not None and expected_revision!=revision(pid):return
    value={k:copy.deepcopy(info[k]) for k in _FIELDS if k in info}
    for k,v in tuple(value.items()):
        if isinstance(v,str):value[k]=v[:1024 if k=='description' else 2048]
    value['events']=[{k:copy.deepcopy(e[k]) for k in _EVENT if k in e}
                     for e in info.get('events',[])[:4] if isinstance(e,dict)]
    for event in value['events']:
        for k,v in tuple(event.items()):
            if isinstance(v,str):event[k]=v[:1024 if k=='description' else 2048]
    record=dict(version=1,key=identity(pid,sid),revision=revision(pid),guide_tag=revision_tag(info.get('snapshot_revision')),binding=selector(mappings,sid),at=time.time(),info=value)
    try:
        raw=json.dumps(record,separators=(',',':'),allow_nan=False)
        if len(raw.encode())>MAX_BYTES:return
        import xbmcgui
        window=xbmcgui.Window(10000)
        # Fixed number of slots: bounded across interpreters and portal changes.
        # A collision is a cache miss, never another station's EPG.
        start=int(record['key'][:8],16)%512;slot=start;oldest=float('inf')
        for offset in range(8):
            candidate=(start+offset)%512
            prior=window.getProperty(PREFIX+str(candidate))
            if not prior:slot=candidate;break
            try:previous=json.loads(prior) if len(prior)<=MAX_BYTES else {}
            except (ValueError,TypeError):previous={}
            if previous.get('key')==record['key']:slot=candidate;break
            stamp=previous.get('at',0)
            if isinstance(stamp,(int,float)) and stamp<oldest:oldest=stamp;slot=candidate
        window.setProperty(PREFIX+str(slot),raw)
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError):pass


def get(pid,sid,now=None,mappings=None):
    ts=time.time() if now is None else now
    key=identity(pid,sid)
    try:
        import xbmcgui
        from epg_status import revision
        window=xbmcgui.Window(10000);record=None;start=int(key[:8],16)%512
        for offset in range(8):
            raw=window.getProperty(PREFIX+str((start+offset)%512))
            if not raw or len(raw.encode())>MAX_BYTES:continue
            value=json.loads(raw)
            if isinstance(value,dict) and value.get('key')==key:record=value;break
        if record is None:return None
        if record.get('version')!=1 or record.get('key')!=key or record.get('revision')!=revision(pid):return None
        tag=window.getProperty(meta_key(pid))
        if tag and record.get('guide_tag')!=tag:return None
        if mappings is not None and record.get('binding')!=selector(mappings,sid):return None
        age=ts-float(record['at'])
        if not math.isfinite(age) or not -1<=age<300:return None
        info=record['info']
        if not isinstance(info,dict) or not isinstance(info.get('events'),list) or len(info['events'])>4:return None
        for e in info['events']:
            if not isinstance(e,dict) or not isinstance(e.get('title'),str):return None
            if any(type(e.get(k)) not in (int,float) or not math.isfinite(e[k]) for k in ('start','stop')):return None
            if not 0<e['start']<e['stop']:return None
        from epg_views import guide_for_channel
        from programme_snapshot47 import bind
        current=guide_for_channel({'v':info['events']},'v',now=ts)
        if isinstance(info.get('snapshot_revision'),list):info['snapshot_revision']=tuple(info['snapshot_revision'])
        for k in ('epg_id','mapping','snapshot_revision','canonical46'):
            if k in info:current[k]=info[k]
        if not current['now'] and not current['next']:return None
        return bind(pid,dict(sid=str(sid)),current)
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,KeyError,OverflowError):return None

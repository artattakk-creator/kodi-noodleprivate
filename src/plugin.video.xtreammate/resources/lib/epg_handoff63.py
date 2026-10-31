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
_states={}
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


def register(pid,value,expected_revision=None):
    """Publish the metadata already read in the SAME guide transaction."""
    if value is None:return
    from epg_status import revision
    if expected_revision is not None and expected_revision!=revision(pid):return
    try:
        import xbmcgui
        window=xbmcgui.Window(10000);key=meta_key(pid)
        old=window.getProperty(key)
        prior=json.loads(old) if old else None
        if isinstance(prior,list) and len(prior)==2 and isinstance(value,(list,tuple)) and len(value)==2:
            if type(prior[1]) in (int,float) and type(value[1]) in (int,float) and value[1]<prior[1]:return
        tag=revision_tag(value)
        if old!=tag:window.setProperty(key,tag)
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError):pass


def note(stage,pid='',sid='',code='READY',duration_ms=0,facts=None):
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
        extra=''
        if isinstance(facts,dict):
            mode=facts.get('mapping')
            if mode in ('MANUAL','PROVIDER_ID','STREAM_ALIAS','SHORT_EPG'):extra+=' mapping='+mode
            source=[facts.get('canonical46',''),facts.get('epg_id',''),facts.get('source_index')]
            extra+=' source='+hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()[:12]
            extra+=' revision='+hashlib.sha256(json.dumps(facts.get('snapshot_revision'),sort_keys=True).encode()).hexdigest()[:12]
        xbmc.log('[XCMate][EPG63] stage='+stage+' channel='+key[1][:12]+' code='+code+
                 ' at_ms='+str(int(now*1000))+' duration_ms='+str(max(0,min(300000,int(duration_ms))))+extra,xbmc.LOGINFO)
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
    def result(code,value=None):
        with _lock:
            _states[key]=code
            while len(_states)>128:_states.pop(next(iter(_states)))
        return value
    try:
        import xbmcgui
        from epg_status import revision
        window=xbmcgui.Window(10000);record=None;start=int(key[:8],16)%512
        for offset in range(8):
            raw=window.getProperty(PREFIX+str((start+offset)%512))
            if not raw or len(raw.encode())>MAX_BYTES:continue
            value=json.loads(raw)
            if isinstance(value,dict) and value.get('key')==key:record=value;break
        if record is None:return result('EPG_CACHE_UNAVAILABLE')
        if record.get('version')!=1 or record.get('key')!=key:return result('EPG_CACHE_UNAVAILABLE')
        if record.get('revision')!=revision(pid):return result('EPG_CACHE_STALE')
        tag=window.getProperty(meta_key(pid))
        if tag and record.get('guide_tag')!=tag:return result('EPG_CACHE_STALE')
        if mappings is not None and record.get('binding')!=selector(mappings,sid):return result('EPG_MAPPING_MISSING')
        # Record freshness uses the real publication clock. The requested
        # EPG moment may be a fixed batch timestamp or a rollover probe.
        age=time.time()-float(record['at'])
        if not math.isfinite(age) or not 0<=age<300:return result('EPG_CACHE_STALE')
        info=record['info']
        if not isinstance(info,dict) or not isinstance(info.get('events'),list) or len(info['events'])>4:return result('EPG_CACHE_UNAVAILABLE')
        for e in info['events']:
            if not isinstance(e,dict) or not isinstance(e.get('title'),str):return result('EPG_CACHE_UNAVAILABLE')
            if any(type(e.get(k)) not in (int,float) or not math.isfinite(e[k]) for k in ('start','stop')):return result('EPG_CACHE_UNAVAILABLE')
            if not 0<e['start']<e['stop']:return result('EPG_CACHE_UNAVAILABLE')
        from epg_views import guide_for_channel
        from programme_snapshot47 import bind
        current=guide_for_channel({'v':info['events']},'v',now=ts)
        if isinstance(info.get('snapshot_revision'),list):info['snapshot_revision']=tuple(info['snapshot_revision'])
        for k in ('epg_id','mapping','snapshot_revision','canonical46'):
            if k in info:current[k]=info[k]
        if not current['now'] and not current['next']:return result('EPG_MAPPING_MISSING' if info.get('reason')=='MANUAL_ID_MISSING' else 'EPG_DATA_MISSING')
        current['_published_at63']=float(record['at'])
        return result('READY' if current['now'] else 'EPG_DATA_MISSING',bind(pid,dict(sid=str(sid)),current))
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,KeyError,OverflowError):return result('EPG_CACHE_UNAVAILABLE')

def state(pid,sid):
    with _lock:return _states.get(identity(pid,sid),'EPG_CACHE_UNAVAILABLE')


def visible(navigator):
    """Numeric UI/publication timing, separate from physical Android pixels."""
    try:
        pid=navigator.portal['id'];sid=str(navigator.sid)
        moment=time.monotonic();wall=time.time()
        prior=getattr(navigator,'_epg_visible63',None)
        if not prior or prior[0]!=sid:
            prior=(sid,wall,moment);navigator._epg_visible63=prior
        note('INFO_VISIBLE',pid,sid)
        info=navigator._guide.get(sid)
        elapsed=(moment-prior[2])*1000
        code='READY' if info.get('now') else state(pid,sid)
        if info.get('now') and elapsed>1000:
            code='EPG_UI_UPDATE_DELAY' if info.get('_published_at63',wall)<=prior[1] else 'EPG_SNAPSHOT_SCHEDULE_DELAY'
        elif not info.get('now') and code=='EPG_CACHE_UNAVAILABLE' and elapsed>1000:
            code='EPG_SNAPSHOT_SCHEDULE_DELAY'
        note('PLAYER_NOW_NEXT_READY',pid,sid,code,elapsed,facts=info)
    except (AttributeError,RuntimeError,KeyError,ValueError,TypeError):pass

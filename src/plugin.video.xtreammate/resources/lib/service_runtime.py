"""Bounded anonymous counters, pressure backoff and service-only cancellation."""
import os,struct,sys,threading,time,weakref,socket
from contextlib import contextmanager
from functools import wraps

_stop=threading.Event();_local=threading.local();_service=False;_pressure=0
_lock=threading.RLock();_calls=0;_reads=0;_bytes=0;_oom=0;_errors=0;_callers={}
_caller_modules={};_portal_outcomes={}
_epg_stats={}
_last_emit=0
_last_portal_sample={}
_portal_ready=False
_next_portal_probe=0
_portal_probe_lock=threading.Lock()
_sockets=weakref.WeakSet()
CALLERS={'service_runtime':'SERVICE','genre_search':'GENRE','widget_fast69':'WIDGET','widget_hooks45':'WIDGET','widget_refresh45':'WIDGET','widget_entry46':'WIDGET','widget_consumer58':'WIDGET','service':'SERVICE','app_services':'LIBRARY','art_store':'ART_SCAN','startup_preload':'STARTUP',
         'xtream':'PROVIDER','catalog_sync':'CATALOG','app_routes':'ROUTE','main':'ROUTE',
         'live_recovery':'LIVE','live_overlay':'LIVE','source_live':'LIVE','search_live':'SEARCH',
         'download_sources':'DOWNLOAD','capture_service':'RECORD','epg':'EPG',
         'epg_config94':'EPG','epg_manager53':'MAPPING','epg_snapshot75':'EPG','epg_sources':'EPG','epg_views':'EPG',
         'hero_epg63':'HERO','programme_display84':'ART_DISPLAY','programme_reference84':'ART_REFERENCE',
         'programme_urls55':'ART_SAFETY','agent_programme100':'AGENT','xmltv_art96':'ART_XMLTV',
         'portal_manager':'CONFIG','provider_baseline96':'CONFIG'}
PORTAL_OUTCOMES = {'MEMORY', 'MEMORY_PAUSE', 'PROFILE_BUSY', 'PROFILE_BUDGET', 'PROFILE_RACE',
                   'INVALID_PROFILE', 'READ_IO', 'UNKNOWN', 'CACHE', 'LOCK_PROOF', 'LOCKED'}
EPG_STAGES={'DB_READ','AGENT_INDEX_READ','AGENT_INDEX_BUILD'}
EPG_OUTCOMES={'READY','OK','CANCELLED','DB_BUSY','SQLITE_INTERRUPT','SQLITE_WRITE_TIMEOUT',
              'EPG_DB_BUDGET','EPG_READ_TIMEOUT','EPG_READ_FAILED','EPG_CACHE_UNAVAILABLE',
              'NO_LOCAL_INDEX','INDEX_READBACK_FAILED','EPG_STORAGE','SOURCE_TIMEOUT'}


def install():
    global _service
    _service=True


def portals_ready():
    """Share a small, time-bounded portal presence probe across service workers."""
    global _portal_ready, _next_portal_probe
    now = time.monotonic()
    if now < _next_portal_probe:
        return _portal_ready
    with _portal_probe_lock:
        if now < _next_portal_probe:
            return _portal_ready
        from portal_snapshot import PortalReadError
        from startup48 import mark
        try:
            from portals import get_active
            ready = bool(get_active())
        except (ImportError, PortalReadError):
            mark('BACKGROUND', 'UNAVAILABLE')
            ready = False
        if ready != _portal_ready or not _next_portal_probe:
            mark('BACKGROUND', 'READY' if ready else 'NO_PORTAL')
        _portal_ready = ready
        _next_portal_probe = now + 5
        return ready


def portal_call():
    global _calls
    frame=sys._getframe(1)
    try:
        while frame is not None:
            name=frame.f_globals.get('__name__')
            if name not in ('portal_snapshot','portals'):
                break
            frame=frame.f_back
        module=name if frame is not None and name in CALLERS else 'OTHER'
        category=CALLERS.get(module,'OTHER')
        with _lock:
            _calls+=1
            _callers[category]=_callers.get(category,0)+1
            _caller_modules[module]=_caller_modules.get(module,0)+1
    finally:del frame


def portal_read(size):
    global _reads,_bytes
    with _lock:_reads+=1;_bytes=int(size)


def portal_failure(code):
    global _oom,_errors
    with _lock:
        if code=='OOM':_oom+=1
        else:_errors+=1


def portal_outcome(code):
    if code in PORTAL_OUTCOMES:
        with _lock:
            _portal_outcomes[code]=_portal_outcomes.get(code,0)+1


def observe_epg(stage, code, duration_ms):
    if stage not in EPG_STAGES:
        return
    code=code if code in EPG_OUTCOMES else 'OTHER'
    elapsed=max(0, min(300_000, int(duration_ms)))
    with _lock:
        entry=_epg_stats.setdefault(stage, {'counts':{}, 'total_ms':0, 'max_ms':0})
        entry['counts'][code]=entry['counts'].get(code,0)+1
        entry['total_ms']+=elapsed
        entry['max_ms']=max(entry['max_ms'],elapsed)


def workload():
    """Observed queues and caches without importing or waking their workers."""
    queues={}
    for name in ('programme_urls55','widget_assets69','artwork_visible'):
        module=sys.modules.get(name)
        if module is None:
            continue
        values=getattr(module,'_queues',None) or {'default':getattr(module,'_queue',None)}
        for lane, queue in values.items():
            if queue is not None:
                queues[name+'.'+lane]=queue.qsize() if hasattr(queue,'qsize') else len(queue)
    caches={}
    module=sys.modules.get('artwork_request100')
    if module is not None:
        for key in ('images','metadata'):
            cache=getattr(module,key,None)
            if cache is not None:
                with cache.changed:
                    caches[key]=dict(entries=len(cache.ready),active=len(cache.active),bytes=cache.bytes)
    with _lock:
        epg={stage:dict(values,counts=dict(values['counts'])) for stage,values in _epg_stats.items()}
    return dict(queues=queues,request_caches=caches,epg_io=epg)


def note_pressure():
    global _pressure
    _pressure=max(_pressure,time.monotonic()+30)


def memory():
    result={}
    try:
        with open('/proc/self/status') as stream:
            for line in stream:
                key,_,value=line.partition(':')
                if key in ('VmRSS','VmSize','Threads'):result[{'VmRSS':'rss_kib','VmSize':'virtual_kib','Threads':'os_threads'}[key]]=int(value.split()[0])
    except (OSError,ValueError):pass
    return result


def pressure():
    if time.monotonic()<_pressure:return True
    try:
        with open('/proc/meminfo') as stream:
            for line in stream:
                if line.startswith('MemAvailable:'):return int(line.split()[1])<64*1024
    except (OSError,ValueError):pass
    return False


def counters():
    with _lock:
        return dict(portal_calls=_calls,portal_disk_reads=_reads,portal_bytes=_bytes,
                    portal_oom=_oom,portal_read_errors=_errors,callers=dict(_callers),
                    caller_modules=dict(_caller_modules),portal_outcomes=dict(_portal_outcomes))


def emit():
    global _last_emit,_last_portal_sample
    now=time.monotonic()
    with _lock:
        interval=now-_last_emit
        if interval<60:return
        value=counters()
        rates={}
        if _last_portal_sample:
            for key in ('portal_calls','portal_disk_reads','portal_oom','portal_read_errors'):
                rates[key]=round((value[key]-_last_portal_sample[key])*60/interval,1)
            rates['callers']={key:round((count-_last_portal_sample['callers'].get(key,0))*60/interval,1)
                              for key,count in value['callers'].items()}
        _last_portal_sample=value
        _last_emit=now
    try:
        import xbmc,json
        xbmc.log('[XCMate][STABILITY] '+json.dumps(dict(value,**memory(),**workload(),pressure=pressure(),
                 portal_per_minute=rates),sort_keys=True),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError,MemoryError):pass


@contextmanager
def scope(cancel=None):
    previous=getattr(_local,'cancel',None)
    if cancel is None:
        try:
            import xbmc
            cancel=xbmc.Monitor().abortRequested
        except (ImportError,AttributeError):cancel=lambda:False
    _local.cancel=cancel
    try:yield
    finally:_local.cancel=previous


def background(function):
    @wraps(function)
    def run(*args,**kwargs):
        with scope():return function(*args,**kwargs)
    return run


def cancelled():
    callback=getattr(_local,'cancel',None)
    if not _service and callback is None:return False
    if _stop.is_set():return True
    return bool(callback and callback())


def timeout(value):return min(value,2) if getattr(_local,'cancel',None) else value


def wait(seconds):
    if _service or getattr(_local,'cancel',None):return _stop.wait(seconds) or cancelled()
    time.sleep(seconds);return False


def track_socket(value):
    if not _service and getattr(_local,'cancel',None) is None:return
    with _lock:
        if _stop.is_set():raise InterruptedError('SERVICE_STOP')
        _sockets.add(value)


def stop():
    _stop.set()
    with _lock:resources=tuple(_sockets)
    for value in resources:
        try:value.shutdown(socket.SHUT_RDWR)
        except OSError:pass  # The IO owner closes its own descriptor/context.



def wait_abort(monitor,seconds,event=None):
    deadline=time.monotonic()+seconds
    while True:
        if event is not None and event.is_set():return True
        if monitor.abortRequested():return True
        remaining=deadline-time.monotonic()
        if remaining<=0:return False
        if monitor.waitForAbort(min(.05,remaining)):return True

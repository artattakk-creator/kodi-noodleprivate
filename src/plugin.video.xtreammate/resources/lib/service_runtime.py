"""Bounded anonymous counters, pressure backoff and service-only cancellation."""
import os,struct,sys,threading,time,weakref,socket
from contextlib import contextmanager
from functools import wraps

_stop=threading.Event();_local=threading.local();_service=False;_pressure=0
_lock=threading.RLock();_calls=0;_reads=0;_bytes=0;_oom=0;_errors=0;_callers={}
_last_emit=0
_sockets=weakref.WeakSet()
CALLERS={'service':'SERVICE','app_services':'LIBRARY','art_store':'ART_SCAN','startup_preload':'STARTUP',
         'xtream':'PROVIDER','catalog_sync':'CATALOG','app_routes':'ROUTE','main':'ROUTE',
         'live_recovery':'LIVE','live_overlay':'LIVE','source_live':'LIVE','search_live':'SEARCH',
         'download_sources':'DOWNLOAD','capture_service':'RECORD','epg':'EPG'}


def install():
    global _service
    _service=True


def portal_call():
    global _calls
    frame=sys._getframe(1)
    try:
        for _ in range(4):
            if frame is None:break
            name=os.path.basename(frame.f_code.co_filename).rsplit('.',1)[0]
            if name not in ('portal_snapshot','portals'):break
            frame=frame.f_back
        category=CALLERS.get(name,'OTHER')
        with _lock:_calls+=1;_callers[category]=_callers.get(category,0)+1
    finally:del frame


def portal_read(size):
    global _reads,_bytes
    with _lock:_reads+=1;_bytes=int(size)


def portal_failure(code):
    global _oom,_errors
    with _lock:
        if code=='OOM':_oom+=1
        else:_errors+=1


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
    with _lock:return dict(portal_calls=_calls,portal_disk_reads=_reads,portal_bytes=_bytes,portal_oom=_oom,portal_read_errors=_errors,callers=dict(_callers))


def emit():
    global _last_emit
    now=time.monotonic()
    if now-_last_emit<60:return
    _last_emit=now
    try:
        import xbmc,json
        xbmc.log('[XCMate][STABILITY] '+json.dumps(dict(counters(),**memory(),pressure=pressure()),sort_keys=True),xbmc.LOGINFO)
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

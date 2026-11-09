"""Worker-only, read-only DB admission and bounded deferred-job receipts.

Never opens/repairs SQLite, resets a failure, or exposes a path/account.
"""
import hashlib,json,os,sqlite3,threading,time

_lock=threading.RLock()
_backoff={}
_logged={}

class Deferred(OSError):
    def __init__(self,code,until,reason='UNKNOWN'):
        self.code82=code;self.retry_at82=until;self.reason82=reason
        super().__init__('ARTWORK_DEFERRED')

def context():
    from artwork_db import path,_identity
    filename=path()
    return filename,tuple(_identity(filename))

def status():
    from artwork_db import diagnostic,_failures
    filename,identity=context()
    value=_failures.get(filename) or diagnostic()
    now=time.time();until=value.get('retry_after',0)
    matching=value.get('identity')==list(identity)
    if matching and isinstance(until,(int,float)) and until>now:
        return dict(code='DB_PAUSED',reason=value.get('code','UNKNOWN'),until=until)
    if value.get('background_paused'):
        return dict(code='DB_MANUAL_PAUSE',reason='MANUAL_PAUSE',until=now+30)
    with _lock:prior=_backoff.get((filename,identity))
    # Explicit retry/identity replacement releases a persisted DB pause.
    if prior and prior[0]>now and not (prior[2] and until!=prior[2]):
        return dict(code=prior[3],reason=prior[1],until=prior[0])
    return dict(code='READY',reason='READY',until=0)

def guard():
    value=status()
    if value['code']!='READY':raise Deferred(value['code'],value['until'],value['reason'])

def defer(error):
    if isinstance(error,Deferred):return error
    from artwork_db import classify
    reason=classify(error) if isinstance(error,sqlite3.Error) else getattr(error,'reason','') or getattr(error,'code','STORAGE_UNAVAILABLE')
    value=status();now=time.time()
    if value['code']!='READY':return Deferred(value['code'],value['until'],value['reason'])
    until=now+(5 if reason=='BUSY' else 30 if isinstance(error,sqlite3.Error) else 60)
    code='DB_DEFERRED' if isinstance(error,sqlite3.Error) else 'STORAGE_DEFERRED'
    filename,identity=context()
    from artwork_db import diagnostic
    receipt=diagnostic();health_until=receipt.get('retry_after',0)
    with _lock:
        _backoff[(filename,identity)]=(until,reason,health_until,code)
        while len(_backoff)>32:_backoff.pop(next(iter(_backoff)))
    return Deferred(code,until,reason)

def note(code,*,reason='READY',until=0,pending=0,alive=True):
    """Only enums, anonymous DB scope, time, counts; no exception message."""
    allowed={'READY','DB_PAUSED','DB_MANUAL_PAUSE','DB_DEFERRED','STORAGE_DEFERRED','JOB_DEFERRED','RECOVERED','FATAL','STOPPED'}
    if code not in allowed:return
    fixed=reason if isinstance(reason,str) and len(reason)<40 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789' for c in reason) else 'UNKNOWN'
    filename,identity=context();scope=hashlib.sha256(repr((filename,identity)).encode()).hexdigest()[:12]
    value=dict(at=time.time(),scope=scope,code=code,reason=fixed,pause_until=int(until),pending=pending,worker_alive=bool(alive))
    import xbmc,xbmcgui
    try:
        xbmcgui.Window(10000).setProperty('XCMate.ArtWorker82',json.dumps(value))
        tag=(scope,code,fixed);now=time.monotonic()
        if now-_logged.get(tag,-1e9)<60:return
        _logged[tag]=now
        while len(_logged)>64:_logged.pop(next(iter(_logged)))
        xbmc.log('[XCMate][ARTWORK82] '+json.dumps(value,separators=(',',':')),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass

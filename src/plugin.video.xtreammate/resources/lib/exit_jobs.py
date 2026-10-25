"""Single-flight Stop dispatcher. Native callbacks only publish intent.

The service starts one daemon worker after window release; SQLite/native Stop
never run inside the GUI callback or block the service watchdog. A stuck native
Stop cannot be forcibly cancelled: report TIMEOUT, never replay or stop foreign
playback. The real Android freeze cause remains unverified without new logs.
"""
import hashlib
import json
import threading
import time

KEY='XCMate.PlaybackExit37'
_thread=None
_lock=threading.Lock()


def state():
    import xbmcgui
    try:
        value=json.loads(xbmcgui.Window(10000).getProperty(KEY))
        if not isinstance(value,dict):return None
        token=value.get('token')
        from playback_exit import _session
        if not isinstance(token,list) or len(token)!=2 or token[0] not in ('live','media') or not _session(json.dumps(token[1])):return None
        if value.get('phase') in ('pending','running','complete','failed','timeout') and 0<=time.time()-value.get('at',0)<86400:
            return value
    except (ValueError,TypeError):pass
    return None


def save(value):
    import xbmcgui
    xbmcgui.Window(10000).setProperty(KEY,json.dumps(value))


def trace(stage,token):
    import xbmc,xbmcgui
    digest=hashlib.sha256(json.dumps([token[0],token[1].get('nonce')]).encode()).hexdigest()[:12]
    try:xbmc.log('[XCMate][PLAYER_EXIT] stage='+stage+' kind='+token[0]+' session='+digest+' window='+str(xbmcgui.getCurrentWindowId()),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def request(player=None,pid=None,expected=None):
    import xbmc
    from playback_exit import identity,_same
    try:token=identity(player or xbmc.Player())
    except (AttributeError,RuntimeError,ValueError,TypeError):return False
    if not token or pid is not None and token[1]['pid']!=str(pid) or expected and not _same(token,expected):return False
    with _lock:
        prior=state()
        if prior and _same(tuple(prior['token']),token):return prior['phase'] in ('pending','running','complete')
        if prior and prior['phase'] in ('pending','running'):return False
        if token[0]=='media' and token[1].get('autoplay_chain'):
            from media_autoplay import request_cancel
            request_cancel(token[1]['autoplay_chain'],token[1]['pid'])
        fields=('pid','sid','nonce','at','kind','series_id','season','episode','autoplay_chain')
        compact=(token[0],{k:token[1][k] for k in fields if k in token[1]})
        save(dict(token=compact,phase='pending',at=time.time(),deadline=time.monotonic()+5,not_before=time.monotonic()+.15))
    trace('EXIT_INTENT',token);return True


def _run(token):
    from playback_exit import stop_owned,_same
    try:ok=stop_owned(expected=token)
    except Exception:ok=False
    with _lock:
        current=state()
        if current and _same(tuple(current['token']),token) and current['phase']=='running':
            current['phase']='complete' if ok else 'failed';save(current)
    trace('PLAYER_STOP_DONE' if ok else 'STOP_REJECTED',token)


def poll():
    global _thread
    import xbmc
    with _lock:
        value=state()
        if not value:return False
        if value['phase'] in ('pending','running') and time.monotonic()>value['deadline']:
            value['phase']='timeout';save(value);trace('STOP_TIMEOUT',tuple(value['token']))
        if value['phase']=='pending' and time.monotonic()>=value['not_before']:
            if _thread is not None and _thread.is_alive():return True
            if getattr(xbmc.Monitor(),'abortRequested',lambda:False)():return True
            value['phase']='running';save(value)
            _thread=threading.Thread(target=_run,args=(tuple(value['token']),),name='XCMate-stop',daemon=True)
            try:_thread.start()
            except (RuntimeError,MemoryError):value['phase']='failed';save(value)
        return value['phase'] in ('pending','running')

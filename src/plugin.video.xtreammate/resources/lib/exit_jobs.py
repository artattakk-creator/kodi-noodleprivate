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


REASONS=('USER_STOP','USER_BACK','USER_HOME','FULLSCREEN_EXIT','OWNER_CHANGED',
         'AUTOPLAY_CANCEL','PLAYBACK_ENDED','STARTUP_ABORT')


def blocked():
    '''No player mutex queries/retry while a native Stop may still be running.

    The Window property survives different plugin/service interpreters. Timeout
    is an observation, not permission to launch a second native Stop.
    '''
    value=state()
    return bool(value and (value['phase'] in ('pending','running') or
                value.get('stop_started') and not value.get('worker_done')))


def trace(stage,token,reason=None):
    import xbmc,xbmcgui
    digest=hashlib.sha256(json.dumps([token[0],token[1].get('nonce')]).encode()).hexdigest()[:12]
    reason=reason or (state() or {}).get('reason','USER_STOP')
    reason=reason if reason in REASONS else 'STARTUP_ABORT'
    try:xbmc.log('[XCMate][PLAYER_EXIT] stage='+stage+' reason='+reason+' kind='+token[0]+' session='+digest+' window='+str(xbmcgui.getCurrentWindowId()),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def request(player=None,pid=None,expected=None,manual=False,reason='USER_STOP'):
    import xbmc
    from playback_exit import identity,_same
    if reason not in REASONS:return False
    prior=state()
    if prior and prior.get('stop_started') and not prior.get('worker_done'):
        return bool(prior['phase']=='running' and expected and _same(tuple(prior['token']),expected))
    try:token=identity(player or xbmc.Player())
    except (AttributeError,RuntimeError,ValueError,TypeError):return False
    if not token or pid is not None and token[1]['pid']!=str(pid) or expected and not _same(token,expected):return False
    with _lock:
        prior=state()
        if prior and _same(tuple(prior['token']),token):
            retry=manual and prior['phase']=='failed' and not prior.get('stop_started') and (_thread is None or not _thread.is_alive())
            if not retry:return prior['phase'] in ('pending','running','complete')
        if prior and (prior['phase'] in ('pending','running') or prior.get('stop_started') and not prior.get('worker_done')):return False
        if token[0]=='media' and token[1].get('autoplay_chain'):
            from media_autoplay import request_cancel
            request_cancel(token[1]['autoplay_chain'],token[1]['pid'])
        fields=('pid','sid','nonce','at','kind','series_id','season','episode','autoplay_chain')
        compact=(token[0],{k:token[1][k] for k in fields if k in token[1]})
        save(dict(token=compact,phase='pending',at=time.time(),deadline=time.monotonic()+5,not_before=time.monotonic()+.15,reason=reason,stop_started=False,worker_done=False))
    trace('EXIT_INTENT',token,reason);return True


def _run(token):
    from playback_exit import stop_owned,_same
    try:ok=stop_owned(expected=token)
    except Exception:ok=False
    with _lock:
        current=state()
        if current and _same(tuple(current['token']),token) and current['phase'] in ('running','timeout'):
            current['worker_done']=True
            current['result']='complete' if ok else 'failed'
            if current['phase']=='running':current['phase']=current['result']
            save(current)
    trace('PLAYER_STOP_DONE' if ok else 'STOP_REJECTED',token)


def poll():
    global _thread
    import xbmc
    with _lock:
        value=state()
        if not value:return False
        if value['phase'] in ('pending','running') and time.monotonic()>value['deadline']:
            value['phase']='timeout'
            if not value.get('stop_started'):value['worker_done']=True
            save(value);trace('STOP_TIMEOUT',tuple(value['token']))
        if value['phase']=='pending' and time.monotonic()>=value['not_before']:
            if _thread is not None and _thread.is_alive():return True
            if getattr(xbmc.Monitor(),'abortRequested',lambda:False)():return True
            # Closing an input callback is asynchronous in Kodi. Wait for
            # actual native dialog release, never force a foreign modal away.
            import xbmcgui
            try:
                dialog=int(getattr(xbmcgui,'getCurrentWindowDialogId',lambda:9999)())
                modal=xbmc.getCondVisibility('System.HasActiveModalDialog')
            except (AttributeError,RuntimeError,ValueError,TypeError):return True
            if dialog not in (0,9999) or modal:
                if not value.get('release_wait'):
                    value['release_wait']=True;save(value);trace('WAIT_NATIVE_RELEASE',tuple(value['token']))
                return True
            value['phase']='running';value['stop_started']=True;save(value)
            _thread=threading.Thread(target=_run,args=(tuple(value['token']),),name='XCMate-stop',daemon=True)
            try:_thread.start()
            except (RuntimeError,MemoryError):value.update(phase='failed',worker_done=True,stop_started=False);save(value)
        return value['phase'] in ('pending','running')

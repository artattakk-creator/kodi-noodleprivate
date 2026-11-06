"""Owned media exit: checkpoint -> fullscreen release -> one native Stop/ACK.

No synchronous Player.stop, no GUI wait, no false ACK from playback callbacks.
Android fullscreen deinitialization precedes codec shutdown, without touching
Kodi decoder settings or the independent .42 Live compatibility preference.
"""
import json,time,uuid
ACK='XCMate.MediaPrepareAck77'

def checkpoint(token):
    from playback_exit import stop_owned,_same
    from exit_jobs import state,save,trace,_lock
    result=stop_owned(expected=token,prepare_only77=True)
    with _lock:
        value=state()
        if not value or not _same(tuple(value['token']),token):return False
        value['checkpoint_done77']=True
        if value['phase']!='running' or time.monotonic()>value['deadline']:
            value.update(phase='failed',worker_done=True,stop_started=False,result='MEDIA_CHECKPOINT_TIMEOUT');save(value);return False
        if not isinstance(result,dict):
            value.update(phase='failed',worker_done=True,stop_started=False,result='CHECKPOINT_OWNER_CHANGED');save(value);return False
        value.update(checkpoint77=True,media_native77=True,snapshot77=result,phase='pending',stop_started=False,worker_done=False,not_before=time.monotonic())
        save(value);trace('MEDIA_CHECKPOINT_READY',token)
    return True

def prepare(value):
    import xbmc,xbmcgui
    from playback_exit import identity,_same
    from exit_jobs import save,trace
    token=tuple(value['token']);window=xbmcgui.Window(10000)
    if not _same(identity(xbmc.Player()),token):
        value.update(phase='failed',worker_done=True,result='MEDIA_OWNER_CHANGED');save(value);return False
    dialog=xbmcgui.getCurrentWindowDialogId()
    if dialog not in (0,-1,9999) or xbmc.getCondVisibility('System.HasActiveModalDialog'):return False
    android=xbmc.getCondVisibility('System.Platform.Android')
    if android and (xbmcgui.getCurrentWindowId()==12005 or xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)')):
        if not value.get('prepare_posted77'):
            nonce=uuid.uuid4().hex
            value.update(prepare_posted77=True,prepare_ack77=nonce);window.clearProperty(ACK);save(value)
            trace('MEDIA_FULLSCREEN_RELEASE_POSTED',token)
            xbmc.executebuiltin('ActivateWindow(Videos)',wait=False)
            xbmc.executebuiltin('SetProperty('+ACK+','+nonce+',home)',wait=False)
        return False
    if value.get('prepare_posted77') and window.getProperty(ACK)!=value.get('prepare_ack77'):return False
    if android and xbmcgui.getCurrentWindowId() not in (10000,10025):return False
    value['prepare_ready77']=True;save(value);return True

def can_post(value,token):
    if not (value.get('media_native77') and value.get('checkpoint77') and value.get('prepare_ready77')):return False
    import xbmc,xbmcgui
    if xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999) or xbmc.getCondVisibility('System.HasActiveModalDialog'):return False
    if xbmc.getCondVisibility('System.Platform.Android'):
        if xbmcgui.getCurrentWindowId() not in (10000,10025) or xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)'):return False
    return True

def finish(value):
    import xbmcgui,media_progress
    from playback_exit import _session
    from media_progress import PROPERTY
    token=value['token'][1];marker=xbmcgui.Window(10000);current=_session(marker.getProperty(PROPERTY))
    if current and current['nonce']==token['nonce']:marker.clearProperty(PROPERTY)
    snapshot=value.get('snapshot77') or {}
    if not snapshot.get('checkpoint_ok',True) and snapshot.get('sample'):
        media_progress.queue_exit_checkpoint(token,tuple(snapshot['sample']))
    if media_progress._current and media_progress._current.get('nonce')==token['nonce']:
        media_progress._current=media_progress._last=None

def observe(value):
    if value.get('token',[None])[0]!='media':return
    if value.get('prepare_posted77') and not value.get('prepare_ready77'):
        import xbmcgui,xbmc
        if xbmcgui.Window(10000).getProperty(ACK)==value.get('prepare_ack77') and xbmcgui.getCurrentWindowId()!=12005 and not xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)'):
            value['prepare_ready77']=True
            from exit_jobs import save,trace
            if value['phase']=='timeout':value.update(phase='failed',worker_done=True,result='MEDIA_RELEASE_TIMEOUT')
            save(value);trace('MEDIA_FULLSCREEN_RELEASE_ACK',tuple(value['token']))
    if not value.get('native_posted'):return
    from exit_jobs import trace
    from native_stop41 import returned
    elapsed=time.monotonic()-value.get('posted_at75',time.monotonic())
    if returned(value):return
    threshold=10 if elapsed>=10 else 5 if elapsed>=5 else 0
    if threshold and value.get('observed77',0)<threshold:
        value['observed77']=threshold
        from exit_jobs import save
        save(value);trace('MEDIA_STOP_WAIT_'+str(threshold)+'S',tuple(value['token']))

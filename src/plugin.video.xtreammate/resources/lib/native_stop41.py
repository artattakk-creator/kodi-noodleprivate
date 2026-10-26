"""Live Stop through Kodi's non-waiting main-thread queue and FIFO barrier.

Kodi21.3 Player.stop uses SendMsg(wait=true). A Python thread waiting there is
not an asynchronous native stop. executebuiltin(wait=false) uses PostMsg. The
following SetProperty runs on that same queue only AFTER StopPlaying returns.
Neither posting nor an early playback callback is treated as completion.
"""
import uuid
ACK='XCMate.NativeStopAck41'


def post(token):
    import xbmc,xbmcgui
    from playback_exit import identity,_same
    if token[0]!='live' or not _same(identity(xbmc.Player()),token):return False
    import exit_jobs
    with exit_jobs._lock:
        value=exit_jobs.state()
        if not value or value['phase']!='running' or not _same(tuple(value['token']),token):return False
        nonce=uuid.uuid4().hex
        value['native_ack']=nonce;value['native_posted']=True
        xbmcgui.Window(10000).clearProperty(ACK);exit_jobs.save(value)
    # Fixed commands only; generated hex nonce cannot inject a builtin.
    exit_jobs.trace('PLAYER_STOP_START',token)
    xbmc.executebuiltin('PlayerControl(Stop)',wait=False)
    xbmc.executebuiltin('SetProperty('+ACK+','+nonce+',home)',wait=False)
    exit_jobs.trace('NATIVE_STOP_POSTED',token)
    return True


def returned(value):
    import xbmcgui
    nonce=value.get('native_ack','')
    return bool(len(nonce)==32 and all(c in '0123456789abcdef' for c in nonce)
                and xbmcgui.Window(10000).getProperty(ACK)==nonce)


def finish(value):
    """Main queue returned; clear only the completed own announcement."""
    import xbmcgui
    from playback_exit import _session
    marker=xbmcgui.Window(10000);key='XtreamMate.LiveSession'
    current=_session(marker.getProperty(key))
    if current and current['nonce']==value['token'][1]['nonce']:marker.clearProperty(key)

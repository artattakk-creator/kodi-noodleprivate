"""Recover the GUI only AFTER a positively acknowledged late native return.

This does not repair a native decoder deadlock. A missing FIFO acknowledgement
stays quarantined; no second stop, player query, window change or fake success.
The timed-out native job remains a timeout in its historical state.
"""
import time


def gui_available():
    import xbmc,xbmcgui
    from window_lifecycle import lease
    return (not lease() and not xbmc.Monitor().abortRequested()
            and int(xbmcgui.getCurrentWindowDialogId()) in (0,9999)
            and not xbmc.getCondVisibility('System.HasActiveModalDialog')
            and not xbmc.getCondVisibility('Container.IsUpdating')
            and int(xbmcgui.getCurrentWindowId()) in (10000,10025))


def resume(value,job):
    from playback_exit import _same
    if (value.get('phase')!='failed' or value.get('recovery46') or not job
            or job.get('phase')!='timeout' or job.get('result')!='complete'
            or not job.get('native_posted') or not job.get('worker_done')
            or not _same(tuple(job['token']),('live',value['session']))):return False
    from native_stop41 import returned
    if not returned(job):return False
    import xbmc,xbmcgui
    if not gui_available():return False
    # A newer item/announcement must never be stopped or navigated away from.
    from live_exit import SESSION,_marker,_save,_trace
    from live_overlay import session_from_property
    announced=session_from_property(_marker().getProperty(SESSION))
    if announced and announced['nonce']!=value['session']['nonce']:return False
    player=xbmc.Player()
    playing=player.isPlaying() if hasattr(player,'isPlaying') else player.isPlayingVideo()
    if playing:return False
    # A separate GUI release allowance; never extend/replay the native Stop.
    value.update(phase='stopping',recovery46='LATE_ACK_VERIFIED',deadline=time.monotonic()+2)
    _save(value);_trace('LATE_RETURN_RECOVERY',value['session']);return True

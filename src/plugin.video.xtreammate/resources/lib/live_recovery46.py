"""Recover the GUI only AFTER a positively acknowledged late native return.

This does not repair a native decoder deadlock. A missing FIFO acknowledgement
stays quarantined; no second stop, player query, window change or fake success.
A late ACK completes the native job; the independent GUI return remains guarded.
"""
import time


def gui_available():
    import xbmc,xbmcgui
    from window_lifecycle import lease
    return (not lease() and not xbmc.Monitor().abortRequested()
            and int(xbmcgui.getCurrentWindowDialogId()) in (0,9999)
            and not xbmc.getCondVisibility('System.HasActiveModalDialog')
            and not xbmc.getCondVisibility('Container.IsUpdating')
            # A positively returned Stop may leave Kodi in its now-empty
            # fullscreen video window. That owned window is a valid return
            # origin, not a foreign modal. resume() still requires the exact
            # native FIFO ACK and verifies no media/new session before routing.
            and int(xbmcgui.getCurrentWindowId()) in (10000,10025,12005))


def resume(value,job):
    from playback_exit import _same
    if (value.get('phase') not in ('failed','return_pending78') or value.get('recovery46') or not job
            or not (job.get('phase')=='timeout' or job.get('phase')=='complete' and job.get('late_ack78')) or job.get('result')!='complete'
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

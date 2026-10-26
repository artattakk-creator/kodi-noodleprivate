"""Recover only Kodi's standard video OSD over a verified own VideoPlayer.

Omega WindowIDs.h: VIDEO_OSD=12901. Never close settings/audio/subtitle/busy or
arbitrary Python dialogs. GUI-owner caller must wait for actual native release.
"""
import time
_last=None


def recover(player,token):
    global _last
    import xbmc,xbmcgui
    from stream_details import own
    if not token or not own(player,token):_last=None;return False
    try:dialog=int(xbmcgui.getCurrentWindowDialogId())
    except (AttributeError,RuntimeError,TypeError,ValueError):return False
    if dialog!=12901:_last=None;return False
    key=(token[0],token[1].get('nonce'))
    if _last is None or _last[0]!=key or time.monotonic()-_last[1]>2:
        if not own(player,token):return False
        _last=(key,time.monotonic())
        xbmc.executebuiltin('Dialog.Close(videoosd)')
        trace('STANDARD_OSD_RELEASE',dialog)
    return True


def trace(phase,dialog=0):
    if phase not in ('STANDARD_OSD_RELEASE','OWN_CAPTURE_RESTORED','FOREIGN_DIALOG_WAIT'):return
    import xbmc
    try:xbmc.log('[XCMate][OSD39] phase='+phase+' dialog='+str(int(dialog)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError,TypeError,ValueError):pass

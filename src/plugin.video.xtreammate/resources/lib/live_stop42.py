"""Opt-in Kodi21.3/Android fullscreen-deinit experiment for OWN Live only.

This changes native lifecycle ORDER, not the Stop thread or timeout. It cannot
repair/cancel a Rockchip native deadlock. Default off; no Kodi settings writes.
The prepare barrier is NOT the existing native Stop completion barrier.
"""
import uuid
import time

ACK = 'XCMate.LivePrepareAck42'
SETTING = 'live_exit_fullscreen42'
FULLSCREEN = 12005
GUI_WINDOWS = (10000, 10025)


def _save(value, stage):
    from exit_jobs import save, trace
    save(value)
    trace(stage, tuple(value['token']))


def _reject(value, stage):
    value.update(phase='failed', worker_done=True, result=stage)
    _save(value, stage)
    return False


def _gui():
    import xbmc, xbmcgui
    return (int(xbmcgui.getCurrentWindowId()),
            int(xbmcgui.getCurrentWindowDialogId()),
            bool(xbmc.getCondVisibility('System.HasActiveModalDialog')),
            bool(xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)')))


def _own(token):
    import xbmc
    from playback_exit import identity, _same
    return token[0] == 'live' and _same(identity(xbmc.Player()), token)


def observe(value):
    """Safe even when native Stop/main queue is wedged: properties only."""
    import xbmcgui
    nonce = value.get('prepare_ack42', '')
    if (value.get('prepare_posted42') and not value.get('prepare_done42')
            and len(nonce) == 32 and all(c in '0123456789abcdef' for c in nonce)
            and xbmcgui.Window(10000).getProperty(ACK) == nonce):
        value['prepare_done42'] = True
        _save(value, 'LATE_FULLSCREEN_RETURN' if value['phase'] == 'timeout' or time.monotonic() > value['deadline']
              else 'FULLSCREEN_EXIT_RETURN')


def prepare(value):
    """Service pending phase; no busy waits, no Stop, no forced dialog close."""
    import xbmc, xbmcgui
    from utils import setting_bool
    if 'strategy42' not in value:
        value['strategy42'] = 'fullscreen42' if setting_bool(SETTING, False) else 'direct41'
        _save(value, 'STRATEGY_FULLSCREEN42' if value['strategy42'] == 'fullscreen42'
              else 'STRATEGY_DIRECT41')
    if value['strategy42'] == 'direct41':
        return True
    token = tuple(value['token'])
    version = xbmc.getInfoLabel('System.BuildVersion').split()
    if not xbmc.getCondVisibility('System.Platform.Android') or not version or version[0].split('.')[:2] != ['21', '3']:
        return _reject(value, 'PREP_UNSUPPORTED_HOST')
    if not _own(token):
        return _reject(value, 'PREP_OWNER_CHANGED')
    window, dialog, modal, visible = _gui()
    if dialog not in (0, 9999) or modal:
        return False  # Never ignore or close a foreign modal.
    if value.get('prepare_posted42'):
        if not value.get('prepare_done42'):
            return False
        if window == FULLSCREEN or visible:
            return False  # Queue ACK alone does not prove native window deinit.
        if window not in GUI_WINDOWS:
            return _reject(value, 'PREP_WINDOW_CHANGED')
        if not value.get('prepare_ready42'):
            value['prepare_ready42'] = True
            _save(value, 'FULLSCREEN_READY')
        return True
    if window in GUI_WINDOWS and not visible:
        value.update(prepare_done42=True, prepare_ready42=True)
        _save(value, 'ALREADY_OUTSIDE_FULLSCREEN')
        return True
    if window != FULLSCREEN:
        return _reject(value, 'PREP_WINDOW_CHANGED')
    nonce = uuid.uuid4().hex
    # Commit before posting: an ambiguous post may not be retried, including
    # after the original five-second deadline or service interpreter restart.
    value.update(prepare_ack42=nonce, prepare_posted42=True, prepare_done42=False)
    xbmcgui.Window(10000).clearProperty(ACK)
    _save(value, 'FULLSCREEN_EXIT_POSTED')
    # Unlike a targeted Fullscreen ShowGui action, ActivateWindow checks
    # HasModalDialog inside Kodi's main thread before deinitializing the old
    # window. A modal arriving AFTER our Python check vetoes the transition.
    xbmc.executebuiltin('ActivateWindow(Videos)', wait=False)
    xbmc.executebuiltin('SetProperty(' + ACK + ',' + nonce + ',home)', wait=False)
    return False


def can_post(value, token):
    """Recheck immediately before native Stop; missing evidence fails closed."""
    if value.get('strategy42') != 'fullscreen42':
        return True
    window, dialog, modal, visible = _gui()
    ok = (value.get('prepare_ready42') and value.get('prepare_done42')
          and window in GUI_WINDOWS and not visible
          and dialog in (0, 9999) and not modal and _own(token))
    if not ok:
        from exit_jobs import trace
        trace('STOP_PREP_GUARD_REJECTED', token)
    return bool(ok)

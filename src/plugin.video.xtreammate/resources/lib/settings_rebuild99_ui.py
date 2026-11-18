"""Kodi entry points for the explicit disk repair and its restart checks."""
from pathlib import Path

import settings_rebuild99 as rebuild

TITLE = 'XCMate'
LABEL = 39033
MESSAGES = {
    'RESTART_REQUIRED': 39035,
    'POST_RESTART_OK': 39036,
    'BACKUP_FAILED': 39037,
    'NO_SPACE': 39038,
    'READBACK_FAILED': 39039,
    'KODI_CACHE_CONFLICT': 39040,
    'REPAIR_BUSY': 39041,
    'REPAIR_STATE_INVALID': 39042,
    'KODI_PROCESS_UNKNOWN': 39043,
    'KODI_SETTINGS_OPEN': 39044,
}


def profile():
    from settings_guard96 import path
    return Path(path()).parent


def text(string_id):
    # Calling localization.tr here could read settings before the boot gate.
    import xbmcaddon
    value = xbmcaddon.Addon().getLocalizedString(string_id)
    if value:
        return value
    from localization import english
    return english()[string_id]


def _native_readback(receipt):
    from settings_guard96 import snapshot
    import xbmcaddon
    if snapshot()['code'] != 'READY':
        return False
    try:
        addon = xbmcaddon.Addon()
        # Kodi's getters can return schema defaults even when it could not load
        # the profile file. This hidden non-default value proves Kodi read it.
        return (addon.getSettingString(rebuild.RECEIPT) == receipt
                and all(addon.getSettingBool(name) is value for name, value in rebuild.DEFAULTS.items()))
    except (RuntimeError, OSError, TypeError, ValueError):
        return False


def _report(code):
    import xbmc
    xbmc.log('[XCMate][SETTINGS99] ' + code, xbmc.LOGINFO)


def _notice(code, modal=False):
    import xbmcgui
    if modal:
        _report(code)
        xbmcgui.Dialog().ok(TITLE, text(MESSAGES[code]))
        return
    try:
        marker = getattr(xbmcgui, 'Window', None)
        if marker is not None:
            window = marker(10000)
            key = 'XCMate.SettingsRebuild99.Notice'
            if window.getProperty(key) == code:
                return
            window.setProperty(key, code)
        _report(code)
        xbmcgui.Dialog().notification(TITLE, text(MESSAGES[code]))
    except (RuntimeError, AttributeError):
        # The Home window may not exist yet in the startup service.
        _report(code)


def preflight():
    """Return True while ordinary Kodi routes/workers must wait."""
    folder = profile()
    if not rebuild.pending(folder):
        return False
    import xbmc
    if xbmc.getCondVisibility('Window.IsActive(addonsettings)'):
        _notice('KODI_SETTINGS_OPEN')
        return True
    try:
        status = rebuild.resume(folder, rebuild.process_identity(), _native_readback, report=_report)
    except rebuild.RebuildError as error:
        _notice(error.code)
        # A concurrent entry is doing the same boot work. The service can
        # retry on its next startup, and the user can reopen a gated route.
        return True
    if status:
        _notice(status)
    return status == 'RESTART_REQUIRED'


def confirm():
    import xbmcgui
    from profile_transaction import writing
    dialog = xbmcgui.Dialog()
    if not dialog.yesno(TITLE, text(39034), defaultbutton=getattr(xbmcgui, 'DLG_YESNO_NO_BTN', 10)):
        return False
    try:
        process = rebuild.process_identity()
        with writing():
            status = rebuild.stage(profile(), process, report=_report)
    except rebuild.RebuildError as error:
        _notice(error.code, modal=True)
        return False
    except TimeoutError:
        _notice('REPAIR_BUSY', modal=True)
        return False
    except OSError:
        _notice('BACKUP_FAILED', modal=True)
        return False
    _notice(status, modal=True)
    return status == 'RESTART_REQUIRED'


def entry(argv):
    """Repair has a direct Kodi route even if the normal router cannot load."""
    from urllib.parse import parse_qs
    if preflight():
        return True
    if len(argv) > 2 and isinstance(argv[2], str) and parse_qs(argv[2].lstrip('?')).get('action') == ['settings_rebuild99']:
        confirm()
        return True
    return False

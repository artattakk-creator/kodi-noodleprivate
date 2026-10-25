"""Small startup tracer: no profile, cache, HTTP or database dependencies.

INFO markers survive playback stop in kodi.log. No argv, exception message,
source lines, portal identity or provider URL is ever logged.
"""
import time
from contextlib import contextmanager

PHASES = frozenset(('ARTWORK_PROFILE','HOME_PORTALS','HOME_FAST','HOME_SUBMITTED','APP_WORKER_STOPPED', 'APP_WORKER_STOP_PENDING', 'ENTRY', 'MAIN_IMPORT', 'ROUTER_INIT', 'DISPATCH',
    'PORTALS_IMPORT', 'PORTALS_LOAD', 'PORTALS_MIGRATION', 'ROOT_MENU',
    'HOME_MENU', 'ART_STATUS_COUNTS', 'ROUTE', 'DIRECTORY_DONE', 'START_FAILED'))
ROUTES = frozenset(('home_start','play_start','play_start_direct','root', 'portal_home', 'xcmate_home', 'portal_manager',
    'setup_wizard', 'import_legacy_settings', 'widget_live_start_group',
    'widget_recent_vod', 'widget_recent_series'))
ROUTES=ROUTES|frozenset(('movies_home','series_home','media_detail','media_favourites',
    'guide_browser','guide_grid','art_status','art_retry','art_db_health','recording_capabilities',
    'appearance_settings','global_search','settings_section','settings'))
ERRORS = frozenset(('RuntimeError', 'OSError', 'PermissionError', 'ValueError',
    'TypeError', 'ImportError', 'ModuleNotFoundError', 'TimeoutError',
    'MemoryError', 'IndexReadError', 'PortalReadError', 'ArtworkDBUnavailable',
    'OperationalError', 'DatabaseError', 'IntegrityError'))


def mark(name, duration_ms=None, action=None, error=None):
    base = name.removesuffix('_BEGIN').removesuffix('_DONE').removesuffix('_FAILED')
    if name not in PHASES and base not in PHASES:
        return
    message = '[XCMate][BOOT] ' + name
    if duration_ms is not None:
        message += ' duration_ms={:.1f}'.format(max(0, duration_ms))
    if action is not None:
        message += ' action=' + (action if action in ROUTES else 'OTHER')
    if error is not None:
        message += ' error=' + (error if error in ERRORS else 'OTHER')
    try:
        import xbmc
        xbmc.log(message, xbmc.LOGINFO)
    except Exception:
        pass  # Diagnostics cannot introduce a second startup failure.


@contextmanager
def phase(name):
    started = time.monotonic()
    mark(name + '_BEGIN')
    try:
        yield
    except BaseException as exc:
        mark(name + '_FAILED', (time.monotonic()-started)*1000,
             error=type(exc).__name__)
        raise
    else:
        mark(name + '_DONE', (time.monotonic()-started)*1000)


def finish_directory(router, *args, **kwargs):
    """Invocation-owned completion; never patch Kodi's global module.

    Keep router objects used by older integrations compatible. A negative
    RunPlugin handle has no directory request to complete.
    """
    if router._handle < 0 or getattr(router, '_directory_done', False):
        return
    import xbmcplugin
    xbmcplugin.endOfDirectory(router._handle, *args, **kwargs)
    router._directory_done = True
    mark('DIRECTORY_DONE')

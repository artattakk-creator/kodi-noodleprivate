"""XCMate Kodi entry point with a visible failure path for Android-TV."""
import sys
import os

ADDON_PATH = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(ADDON_PATH, 'resources', 'lib')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)


def run():
    from boot_diagnostics import phase, mark, finish_directory
    mark('ENTRY')
    from flow46 import entry as timing_entry46
    timing_entry46(sys.argv)
    router = None
    try:
        from artwork_config import initialize
        with phase('ARTWORK_PROFILE'):
            try:initialize()
            except OSError:pass
        from home_entry import HomeRouter,dispatch as home_dispatch
        router=HomeRouter(sys.argv)
        with phase('HOME_FAST'):
            if home_dispatch(sys.argv,router=router):return
        from widget_entry46 import dispatch as widget_dispatch46
        with phase('WIDGET_FAST'):
            if widget_dispatch46(router):return
        with phase('MAIN_IMPORT'):
            from main import Router
        with phase('ROUTER_INIT'):
            router = Router(sys.argv)
        with phase('DISPATCH'):
            router.dispatch()
    except Exception as exc:
        # Kodi otherwise leaves an endless spinner on unhandled plugin errors.
        import xbmcgui
        mark('START_FAILED', error=type(exc).__name__)
        try:
            if router is None:
                # The main import/constructor may have failed before a Router
                # existed. Do not import main again to report that failure.
                from types import SimpleNamespace
                router = SimpleNamespace(_handle=int(sys.argv[1]))
            finish_directory(router, succeeded=False, cacheToDisc=False)
        except Exception:
            pass
        # Non-modal: an error in a widget must not open a blocking OK dialog.
        try:
            xbmcgui.Dialog().notification(
                'XCMate – Startfehler',
                'BOOT START_FAILED. Bitte Kodi-Protokoll prüfen. Daten bleiben erhalten.')
        except Exception:
            pass


if __name__ == '__main__':
    run()

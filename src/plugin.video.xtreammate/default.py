"""XCMate Kodi entry point with a visible failure path for Android-TV."""
import sys
import os

ADDON_PATH = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(ADDON_PATH, 'resources', 'lib')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)


def run():
    try:
        from main import Router
        Router(sys.argv).dispatch()
    except Exception as exc:
        # Kodi otherwise leaves an endless spinner on unhandled plugin errors.
        import traceback
        import xbmc
        import xbmcgui
        import xbmcplugin
        xbmc.log('[XCMate] FATAL (credentials not logged): ' +
                 ''.join(traceback.format_tb(exc.__traceback__)), xbmc.LOGERROR)
        try:
            handle = int(sys.argv[1])
            if handle >= 0:
                xbmcplugin.endOfDirectory(handle, succeeded=False,
                                          cacheToDisc=False)
        except Exception:
            pass
        xbmcgui.Dialog().ok(
            'XCMate – Startfehler',
            '{}. Bitte Kodi-Protokoll prüfen. Deine Senderdaten bleiben erhalten.'.format(
                type(exc).__name__))


if __name__ == '__main__':
    run()

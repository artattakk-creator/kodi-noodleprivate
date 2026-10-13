import time, sys, os
import xbmc, xbmcaddon

ADDON    = xbmcaddon.Addon()
LIB_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'lib')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

from utils import setting_bool, setting_int, info, error


class IPTVMasterService(xbmc.Monitor):

    def __init__(self):
        super().__init__()
        self._last_epg = 0
        info('XtreamMate service started')
        self._overlay = None
        self._last_session_nonce = ''
        self._start_reminders()

    def _start_reminders(self):
        try:
            from reminders import ReminderMonitor
            self._reminder_monitor = ReminderMonitor()
        except Exception as e:
            error(f'reminder monitor: {e}')

    def _maybe_refresh_epg(self):
        if not setting_bool('epg_auto_refresh', True):
            return
        interval = setting_int('epg_refresh_hours', 12) * 3600
        if time.time() - self._last_epg < interval:
            return
        self._last_epg = time.time()
        info('Service: auto-refreshing EPG for all active portals')
        try:
            import portals as P
            from epg import ensure_epg_loaded_for_portal
            for p in P.get_active():
                ensure_epg_loaded_for_portal(p, force=True)
        except Exception as e:
            error(f'Service EPG refresh: {e}')

    def run(self):
        while not self.abortRequested():
            self._maybe_refresh_epg()
            try:
                from live_overlay import start_if_eligible, session_from_property, SESSION_KEY
                import xbmcgui
                player = xbmc.Player()
                if not player.isPlayingVideo():
                    if self._overlay is not None:
                        self._overlay.close()
                        self._overlay = None
                    self._last_session_nonce = ''
                elif self._overlay is None:
                    session = session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
                    candidate = start_if_eligible(self._last_session_nonce)
                    if candidate is not None:
                        self._overlay = candidate
                        self._last_session_nonce = session['nonce'] if session else ''
                        self._overlay.show()
            except Exception as exc:
                error('XtreamMate TV navigation unavailable: {}'.format(type(exc).__name__))
            self.waitForAbort(1)
        if self._overlay is not None:
            self._overlay.close()
        info('XtreamMate service stopped')


if __name__ == '__main__':
    IPTVMasterService().run()

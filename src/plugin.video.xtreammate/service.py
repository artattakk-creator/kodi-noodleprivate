import time, sys, os, threading
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
        self._epg_worker = None
        self._stopped_since = None
        info('XtreamMate service started')
        self._overlay = None
        self._last_session_nonce = ''
        self._last_command_nonce = ''
        self._catalog_worker = None
        self._next_catalog_scan = 0
        self._next_overlay_check = 0
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
        info('Service: scheduling background EPG refresh')
        if self._epg_worker and self._epg_worker.is_alive():
            return
        def refresh():
            try:
                import portals as P
                from epg import ensure_epg_loaded_for_portal
                for portal in P.get_active():
                    if self.abortRequested():
                        return
                    ensure_epg_loaded_for_portal(portal, force=True)
            except Exception as exc:
                error('Service EPG refresh: {}'.format(type(exc).__name__))
        self._epg_worker = threading.Thread(target=refresh, name='XtreamMateEPG', daemon=True)
        self._epg_worker.start()

    def _maybe_warm_catalogs(self):
        """Never fetch Xtream metadata on the Kodi service/remote-control thread."""
        now = time.monotonic()
        if now < self._next_catalog_scan:
            return
        if self._catalog_worker and self._catalog_worker.is_alive():
            return
        self._next_catalog_scan = now + 1800
        def warm():
            try:
                import portals as portal_store
                from xtream import XtreamClient
                for portal in portal_store.get_active():
                    if self.abortRequested():
                        return
                    if portal.get('type') != 'xtream':
                        continue
                    xc = XtreamClient(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
                    xc.warm_catalogs(
                        include_live=portal.get('include_live', True),
                        include_vod=portal.get('include_vod', True),
                        include_series=portal.get('include_series', True))
            except Exception as exc:
                error('XtreamMate background catalog: {}'.format(type(exc).__name__))
        self._catalog_worker = threading.Thread(
            target=warm, name='XtreamMateCatalogCache', daemon=True)
        self._catalog_worker.start()

    def run(self):
        while not self.abortRequested():
            self._maybe_refresh_epg()
            self._maybe_warm_catalogs()
            try:
                from live_overlay import start_if_eligible, session_from_property, SESSION_KEY
                from remote_control import parse_command, COMMAND_KEY
                import xbmcgui
                player = xbmc.Player()
                if not player.isPlayingVideo():
                    # Brief playback gaps are normal when switching IPTV channels.
                    # Keep the session marker intact until the gap is prolonged.
                    if self._stopped_since is None:
                        self._stopped_since = time.monotonic()
                    if time.monotonic() - self._stopped_since > 8:
                        if self._overlay is not None:
                            self._overlay.close()
                            self._overlay = None
                        self._last_session_nonce = ''
                        xbmcgui.Window(10000).clearProperty(SESSION_KEY)
                else:
                    self._stopped_since = None
                    if self._overlay is not None:
                        active_session = session_from_property(
                            xbmcgui.Window(10000).getProperty(SESSION_KEY))
                        if active_session and active_session['nonce'] != self._last_session_nonce:
                            if active_session['pid'] != str(self._overlay.portal['id']):
                                self._overlay.close()
                                self._overlay = None
                            else:
                                self._overlay.sid = active_session['sid']
                                current_channel = next((ch for ch in self._overlay.channels
                                    if str(ch.extra.get('stream_id')) == active_session['sid']), None)
                                if current_channel:
                                    self._overlay.category_id = str(
                                        current_channel.extra.get('category_id') or '*')
                                self._overlay._scroll_to_current = True
                                self._last_session_nonce = active_session['nonce']
                    if self._overlay is None:
                        session = session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
                        candidate = start_if_eligible(self._last_session_nonce)
                        if candidate is not None:
                            self._overlay = candidate
                            self._last_session_nonce = session['nonce'] if session else ''
                            self._overlay.show()
                if self._overlay is not None and player.isPlayingVideo():
                    if time.monotonic() >= self._next_overlay_check:
                        self._next_overlay_check = time.monotonic() + 1.0
                        self._overlay.refresh_from_cache()
                    cmd = parse_command(xbmcgui.Window(10000).getProperty(COMMAND_KEY))
                    if cmd and cmd['nonce'] != self._last_command_nonce:
                        self._last_command_nonce = cmd['nonce']
                        xbmcgui.Window(10000).clearProperty(COMMAND_KEY)
                        self._overlay.handle_command(cmd['action'])
            except Exception as exc:
                error('XtreamMate TV navigation unavailable: {}'.format(type(exc).__name__))
            self.waitForAbort(0.2)
        if self._overlay is not None:
            self._overlay.close()
        info('XtreamMate service stopped')


if __name__ == '__main__':
    IPTVMasterService().run()

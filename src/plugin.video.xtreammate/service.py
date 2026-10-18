import time, sys, os, threading, uuid
import xbmc, xbmcaddon, xbmcgui

ADDON    = xbmcaddon.Addon()
LIB_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'lib')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

from utils import setting_bool, setting_int, info, error


# A direct RunPlugin autoplay announces its session before Player.play() has
# completed. Kodi may need several seconds to open the IPTV stream. An idle
# service must not erase that fresh marker using its pre-existing idle timer.
PENDING_LIVE_START_SECONDS = 60


def pending_live_start(session, last_overlay_nonce, now=None):
    """Protect a newly announced TV session until playback has actually begun.

    Once the matching overlay was activated, a stopped video uses the normal
    short cleanup timeout. Stale or malformed sessions receive no grace.
    """
    if not session or session.get('nonce') == last_overlay_nonce:
        return False
    try:
        age = (time.time() if now is None else now) - float(session['at'])
    except (KeyError, ValueError, TypeError):
        return False
    return 0 <= age < PENDING_LIVE_START_SECONDS


class IPTVMasterService(xbmc.Monitor):

    def __init__(self):
        super().__init__()
        self._last_epg = 0
        self._epg_worker = None
        self._stopped_since = None
        info('XCMate service started')
        self._overlay = None
        self._last_session_nonce = ''
        self._last_command_nonce = ''
        self._catalog_worker = None
        self._next_catalog_scan = 0
        self._next_overlay_check = 0
        self._overlay_failure_reported = False
        self._remote_keymap_checked = False
        self._next_recovery_probe = 0
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
        self._epg_worker = threading.Thread(target=refresh, name='XCMateEPG', daemon=True)
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
                error('XCMate background catalog: {}'.format(type(exc).__name__))
        self._catalog_worker = threading.Thread(
            target=warm, name='XCMateCatalogCache', daemon=True)
        self._catalog_worker.start()

    def run(self):
        from service_health import (inspect, heartbeat, note, INSTANCE,
                                    PHASE, LAST_ERROR, LAST_LIVE,
                                    LAST_OVERLAY, LAST_INPUT)
        marker = xbmcgui.Window(10000)
        if inspect(marker)['alive']:
            info('XCMate service: another worker already reports healthy; skipping duplicate')
            return
        instance = uuid.uuid4().hex
        loops = 0
        heartbeat(marker, instance, loops, phase='gestartet')
        note(marker, LAST_ERROR, 'keine gemeldet')
        while not self.abortRequested():
            loops += 1
            heartbeat(marker, instance, loops, phase='läuft')
            # Safe mode: heavy Xtream catalog and XMLTV downloads stay off
            # unless explicitly enabled. The player/remote service still runs.
            if setting_bool('xc_background_prefetch', False):
                self._maybe_refresh_epg()
                self._maybe_warm_catalogs()
            try:
                from live_overlay import start_if_eligible, session_from_property, SESSION_KEY
                from remote_control import parse_command, COMMAND_KEY
                player = xbmc.Player()
                if player.isPlayingVideo():
                    announced_health = session_from_property(marker.getProperty(SESSION_KEY))
                    if (not announced_health and
                            time.monotonic() >= self._next_recovery_probe):
                        self._next_recovery_probe = time.monotonic() + 3
                        # Only an exact match with an enabled Xtream portal
                        # can restore a missing XCMate marker. No URL logging,
                        # no network/API work and no modification of profiles.
                        try:
                            from live_recovery import recover_from_player_path
                            from portals import get_active
                            from xtream import XtreamClient
                            playing_file = player.getPlayingFile()
                            recovered = recover_from_player_path(
                                playing_file, get_active(), XtreamClient)
                            if recovered:
                                from live_overlay import announce
                                announce(recovered[0], recovered[1])
                                announced_health = session_from_property(
                                    marker.getProperty(SESSION_KEY))
                                marker.setProperty(
                                    'XtreamMate.SessionRecovery', 'XCMate-Live-Stream erkannt')
                            else:
                                marker.setProperty(
                                    'XtreamMate.SessionRecovery',
                                    'keine eindeutige XCMate-Live-Adresse')
                        except Exception as exc:
                            # User-visible error TYPE only; never write the
                            # playing file or the provider credentials.
                            marker.setProperty(
                                'XtreamMate.SessionRecovery',
                                'Prüfung fehlgeschlagen: ' + type(exc).__name__)
                    note(marker, LAST_LIVE,
                         'Video JA / XCMate-Sitzung ' +
                         ('JA' if announced_health else 'NEIN'))
                if not player.isPlayingVideo():
                    # Brief playback gaps are normal when switching IPTV channels.
                    # Keep the session marker intact until the gap is prolonged.
                    if self._stopped_since is None:
                        self._stopped_since = time.monotonic()
                    marker = xbmcgui.Window(10000)
                    announced = session_from_property(marker.getProperty(SESSION_KEY))
                    # Preserve a fresh announcement even when _stopped_since
                    # started long before RunPlugin created this TV session.
                    pending_start = pending_live_start(
                        announced, self._last_session_nonce)
                    if time.monotonic() - self._stopped_since > 8 and not pending_start:
                        if self._overlay is not None:
                            self._overlay.close()
                            self._overlay = None
                        self._last_session_nonce = ''
                        marker.clearProperty(SESSION_KEY)
                        marker.clearProperty('XtreamMate.OverlayStatus')
                    elif pending_start:
                        marker.setProperty('XtreamMate.OverlayStatus',
                                           'warte auf Videostart')
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
                            try:
                                if not self._remote_keymap_checked:
                                    from remote_control import ensure_for_live_tv
                                    status = ensure_for_live_tv()
                                    xbmcgui.Window(10000).setProperty(
                                        'XtreamMate.KeymapStatus', status)
                                    self._remote_keymap_checked = True
                                xbmcgui.Window(10000).setProperty(
                                    'XtreamMate.OverlayStatus', 'wird gestartet')
                                marker.setProperty('XtreamMate.AutoPopupStatus',
                                                   'TV-Popup wird angefordert')
                                self._overlay = candidate
                                self._overlay.show()
                                note(marker, LAST_OVERLAY, 'TV-Dialog gestartet')
                                self._last_session_nonce = session['nonce'] if session else ''
                                self._overlay_failure_reported = False
                            except Exception as exc:
                                self._overlay = None
                                xbmcgui.Window(10000).setProperty(
                                    'XtreamMate.OverlayStatus', 'Fehler: ' + type(exc).__name__)
                                note(marker, LAST_OVERLAY,
                                     'TV-Dialog-Fehler: ' + type(exc).__name__)
                                marker.setProperty('XtreamMate.AutoPopupStatus',
                                                   'Fehler: ' + type(exc).__name__)
                                error('XCMate WindowDialog startup failed: {} {}'.format(
                                    type(exc).__name__, str(exc)[:240]))
                                if not self._overlay_failure_reported:
                                    xbmcgui.Dialog().notification('XCMate',
                                         'TV-Navigation konnte nicht geöffnet werden')
                                    self._overlay_failure_reported = True
                if self._overlay is not None and player.isPlayingVideo():
                    self._overlay.expire_intro()
                    if time.monotonic() >= self._next_overlay_check:
                        self._next_overlay_check = time.monotonic() + 1.0
                        self._overlay.refresh_from_cache()
                    cmd = parse_command(xbmcgui.Window(10000).getProperty(COMMAND_KEY))
                    if cmd and cmd['nonce'] != self._last_command_nonce:
                        self._last_command_nonce = cmd['nonce']
                        xbmcgui.Window(10000).clearProperty(COMMAND_KEY)
                        self._overlay.handle_command(cmd['action'])
                        xbmcgui.Window(10000).setProperty('XtreamMate.LastHandledKey', cmd['action'])
                        note(marker, LAST_INPUT, 'Bridge: ' + cmd['action'])
            except Exception as exc:
                note(marker, LAST_ERROR, 'TV-Loop: ' + type(exc).__name__)
                error('XCMate TV navigation unavailable: {}'.format(type(exc).__name__))
            self.waitForAbort(0.2)
        if self._overlay is not None:
            self._overlay.close()
        if marker.getProperty(INSTANCE) == instance:
            marker.setProperty(PHASE, 'beendet')
        info('XCMate service stopped')


if __name__ == '__main__':
    IPTVMasterService().run()

"""XCMate P0: live session must survive a slow Android autoplay startup.

Kodi-stub regression test only; final device acceptance is separate.
"""
import importlib.util
import json
from pathlib import Path
import sys
import time
import tempfile
import types
import unittest
from unittest import mock

SERVICE = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/service.py'


class FakeWindow:
    def __init__(self):
        self.data = {}

    def getProperty(self, name):
        return self.data.get(name, '')

    def setProperty(self, name, value):
        self.data[name] = value

    def clearProperty(self, name):
        self.data.pop(name, None)


class FakeMonitor:
    def __init__(self):
        self.iterations = 0

    def abortRequested(self):
        return self.iterations >= 1

    def waitForAbort(self, seconds):
        self.iterations += 1


class PendingLiveSessionTests(unittest.TestCase):
    def setUp(self):
        self.window = FakeWindow()
        xbmc = types.ModuleType('xbmc')
        xbmc.Monitor = FakeMonitor
        xbmc.Player = lambda: types.SimpleNamespace(isPlayingVideo=lambda: False)
        xbmcaddon = types.ModuleType('xbmcaddon')
        xbmcaddon.Addon = lambda: object()
        xbmcgui = types.ModuleType('xbmcgui')
        xbmcgui.Window = lambda number: self.window
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        utils = types.ModuleType('utils')
        utils.addon_data_dir=lambda:temp.name
        utils.setting_bool = lambda *args: False
        utils.setting_int = lambda *args: 0
        utils.info = utils.error = lambda *args: None
        live_overlay = types.ModuleType('live_overlay')
        live_overlay.SESSION_KEY = 'XtreamMate.LiveSession'
        live_overlay.session_from_property = lambda raw: json.loads(raw) if raw else None
        live_overlay.start_if_eligible = lambda last_nonce: None
        remote = types.ModuleType('remote_control')
        remote.COMMAND_KEY = 'XtreamMate.RemoteCommand'
        remote.parse_command = lambda raw: None
        p = mock.patch.dict(sys.modules, {
            'xbmc': xbmc, 'xbmcaddon': xbmcaddon, 'xbmcgui': xbmcgui,
            'utils': utils, 'live_overlay': live_overlay,
            'remote_control': remote,
            # This fixture tests idle-session grace, not additive app workers.
            # A real import daemon must not outlive these replaced Kodi stubs.
            'app_services': types.SimpleNamespace(poll=lambda: None, shutdown=lambda: True),
        })
        p.start()
        self.addCleanup(p.stop)
        spec = importlib.util.spec_from_file_location(
            'xcmate_pending_session_test', SERVICE)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def _run_idle_service(self, at, nonce='fresh', overlay_nonce=''):
        self.window.setProperty('XtreamMate.LiveSession', json.dumps({
            'pid': 'portal', 'sid': 'stream', 'nonce': nonce, 'at': at,
        }))
        with mock.patch.object(self.mod.IPTVMasterService,
                               '_start_reminders', lambda obj: None):
            service = self.mod.IPTVMasterService()
        service._maybe_refresh_epg = lambda: None
        service._maybe_warm_catalogs = lambda: None
        # Before the fix, the service's old idle timer would immediately
        # destroy any session announced while Kodi was starting playback.
        service._stopped_since = time.monotonic() - 600
        service._last_session_nonce = overlay_nonce
        service.run()

    def test_new_session_survives_existing_idle_timer(self):
        self._run_idle_service(time.time()-1)
        self.assertTrue(self.window.getProperty('XtreamMate.LiveSession'))
        self.assertEqual(self.window.getProperty('XtreamMate.OverlayStatus'),
                         'warte auf Videostart')

    def test_old_session_is_cleaned_after_grace(self):
        self._run_idle_service(time.time()-65)
        self.assertEqual(self.window.getProperty('XtreamMate.LiveSession'), '')

    def test_confirmed_overlay_is_cleaned_on_stop(self):
        self._run_idle_service(time.time()-1, nonce='played',
                               overlay_nonce='played')
        self.assertEqual(self.window.getProperty('XtreamMate.LiveSession'), '')

    def test_future_or_malformed_announcement_is_not_preserved(self):
        helper = self.mod.pending_live_start
        self.assertFalse(helper({'nonce':'a', 'at': 120}, '', now=100))
        self.assertFalse(helper({'nonce':'a', 'at': 'bogus'}, '', now=100))
        self.assertFalse(helper({}, '', now=100))
        self.assertTrue(helper({'nonce':'a', 'at': 100}, '', now=130))


if __name__ == '__main__':
    unittest.main()

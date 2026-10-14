"""Service heartbeat tests: usable when the IPTV player isn't running.

Mocked Kodi tests do not prove device-specific RunScript success.
"""
import importlib.util
from pathlib import Path
import sys
import time
import types
import unittest
from unittest import mock

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / 'src/plugin.video.xtreammate/resources/lib/service_health.py'
spec = importlib.util.spec_from_file_location('test_xcmate_service_health', SOURCE)
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)


class Marker:
    def __init__(self):
        self.props = {}
    def setProperty(self, name, value):
        self.props[name] = str(value)
    def getProperty(self, name):
        return self.props.get(name, '')


class ServiceHealthTests(unittest.TestCase):
    def test_without_video_or_service_health_is_not_confirmed(self):
        w = Marker()
        s = health.inspect(w, now=500)
        self.assertEqual(s['state'], 'NICHT BESTÄTIGT')
        self.assertFalse(s['alive'])
        self.assertIsNone(s['age'])
        self.assertEqual(s['live'], 'noch nicht geprüft')

    def test_heartbeat_detects_running_stale_and_stopped(self):
        w = Marker()
        health.heartbeat(w, 'worker1', 18, 'läuft', now=100)
        self.assertEqual(health.inspect(w, now=101)['state'], 'LÄUFT')
        self.assertEqual(health.inspect(w, now=101)['loops'], '18')
        self.assertEqual(health.inspect(w, now=106)['state'], 'KEIN AKTUELLES LEBENSZEICHEN')
        w.setProperty(health.PHASE, 'beendet')
        self.assertEqual(health.inspect(w, now=102)['state'], 'GESTOPPT')

    def test_last_stream_and_osd_status_survive_idle(self):
        w = Marker()
        health.note(w, health.LAST_LIVE, 'Video JA / XCMate-Sitzung NEIN')
        health.note(w, health.LAST_OVERLAY, 'TV-Dialog-Fehler: RuntimeError')
        health.note(w, health.LAST_INPUT, 'Bridge: left')
        s = health.inspect(w, now=500)
        self.assertIn('Video JA', s['live'])
        self.assertIn('RuntimeError', s['overlay'])
        self.assertEqual(s['input'], 'Bridge: left')
        with self.assertRaises(ValueError):
            health.note(w, 'XtreamMate.LiveSession', 'secret')

    def test_manual_start_gates_duplicate_and_pending_requests(self):
        w = Marker()
        actions = []
        sleeps = []
        xbmc = types.SimpleNamespace(
            executebuiltin=lambda action: actions.append(action),
            sleep=lambda ms: sleeps.append(ms))
        gui = types.SimpleNamespace(Window=lambda id: w)
        with mock.patch.dict(sys.modules, {'xbmc': xbmc, 'xbmcgui': gui}):
            now = time.time()
            health.heartbeat(w, 'worker2', 1, 'läuft', now=now)
            result = health.request_manual_start(w, now=now)
            self.assertIn('läuft bereits', result)
            self.assertEqual(actions, [])
            w.setProperty(health.PHASE, 'beendet')
            result = health.request_manual_start(w, now=now)
            self.assertIn('angefordert', result)
            self.assertEqual(len(actions), 1)
            self.assertIn('service.py,manual)', actions[0])
            self.assertEqual(sleeps, [1500])
            result = health.request_manual_start(w, now=now+1)
            self.assertIn('vor Kurzem', result)
            self.assertEqual(len(actions), 1)

    def test_service_writes_heartbeat_and_main_has_offline_controls(self):
        service = (BASE / 'src/plugin.video.xtreammate/service.py').read_text(encoding='utf-8')
        main = (BASE / 'src/plugin.video.xtreammate/resources/lib/main.py').read_text(encoding='utf-8')
        self.assertIn("heartbeat(marker, instance, loops, phase='läuft')", service)
        self.assertIn("note(marker, LAST_LIVE", service)
        self.assertIn("note(marker, LAST_OVERLAY", service)
        self.assertIn("'service_recover': self._service_recover", main)
        self.assertIn("XCMate-Hintergrunddienst prüfen / manuell starten", main)
        self.assertIn("'Letzte Live-Beobachtung: ' + health['live']", main)
        self.assertIn("request_manual_start(marker)", main)


if __name__ == '__main__':
    unittest.main()

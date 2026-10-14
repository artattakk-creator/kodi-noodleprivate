"""XCMate v0.1.15: independent focusable Kodi popup and live intro tests.

These are mocked Kodi API tests. Only the user's Android test can establish
whether the native remote actually sends D-pad/OK actions to WindowDialog.
"""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'src/plugin.video.xtreammate/resources/lib'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, LIB / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Control:
    next_id = 1
    def __init__(self, *args, **kwargs):
        self.id = Control.next_id
        Control.next_id += 1
        self.label = ''
    def getId(self):
        return self.id
    def setLabel(self, text):
        self.label = text


class Dialog:
    def __init__(self):
        self.closed = False
        self.focus = None
        self.controls = []
    def getWidth(self):
        return 1280
    def getHeight(self):
        return 720
    def addControl(self, control):
        self.controls.append(control)
    def setFocus(self, control):
        self.focus = control
    def close(self):
        self.closed = True
    def doModal(self):
        self.onInit()
        self.onAction(Action(1))
        self.onAction(Action(3))
        self.onAction(Action(7))
        self.onAction(Action(92))


class Window:
    data = {}
    def __init__(self, wid):
        self.wid = wid
    def setProperty(self, name, value):
        self.data[name] = str(value)
    def getProperty(self, name):
        return self.data.get(name, '')


class Action:
    def __init__(self, key, raw=0):
        self.key = key
        self.raw = raw
    def getId(self):
        return self.key
    def getButtonCode(self):
        return self.raw


class PopupProbeTests(unittest.TestCase):
    def setUp(self):
        Window.data = {}
        Control.next_id = 1
        xbmcgui = types.ModuleType('xbmcgui')
        xbmcgui.WindowDialog = Dialog
        xbmcgui.Window = Window
        xbmcgui.ControlImage = Control
        xbmcgui.ControlLabel = Control
        xbmcgui.ControlButton = Control
        xbmcaddon = types.ModuleType('xbmcaddon')
        xbmcaddon.Addon = lambda: types.SimpleNamespace(
            getAddonInfo=lambda info: '/tmp/fixture-xcmate')
        self.patch = mock.patch.dict(sys.modules, {
            'xbmcgui': xbmcgui, 'xbmcaddon': xbmcaddon,
        })
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.module = load('popup_probe_015', 'popup_probe.py')

    def test_standalone_popup_runs_modal_without_service_or_video(self):
        self.module.run_popup_test()
        self.assertEqual(Window.data['XtreamMate.PopupProbe.Status'],
                         'PER ZURÜCK GESCHLOSSEN')
        self.assertEqual(Window.data['XtreamMate.PopupProbe.KeyCount'], '4')
        self.assertIn('Zurück', Window.data['XtreamMate.PopupProbe.LastKey'])
        self.assertIn('XtreamMate.PopupProbe.LastOpened', Window.data)

    def test_manual_popup_renders_and_tracks_dpad_focus(self):
        dlg = self.module.PopupInputProbe()
        dlg.onInit()
        self.assertGreaterEqual(len(dlg.controls), 8)
        self.assertIs(dlg.focus, dlg.test_button)
        dlg.onAction(Action(2, 22))
        self.assertIs(dlg.focus, dlg.close_button)
        dlg.onAction(Action(1, 21))
        self.assertIs(dlg.focus, dlg.test_button)
        dlg.onAction(Action(7, 23))
        self.assertFalse(dlg.closed)
        self.assertIn('OK', Window.data['XtreamMate.PopupProbe.LastKey'])
        dlg.onAction(Action(92))
        self.assertTrue(dlg.closed)

    def test_ok_click_fallback_for_android_remote(self):
        dlg = self.module.PopupInputProbe()
        dlg.onInit()
        dlg.onClick(dlg.test_button.getId())
        self.assertEqual(Window.data['XtreamMate.PopupProbe.KeyCount'], '1')
        self.assertIn('onClick', Window.data['XtreamMate.PopupProbe.LastKey'])
        dlg.onClick(dlg.close_button.getId())
        self.assertTrue(dlg.closed)

    def test_live_intro_visible_initially_and_hides_without_key(self):
        source = (LIB / 'live_overlay.py').read_text(encoding='utf-8')
        service = (ROOT / 'src/plugin.video.xtreammate/service.py').read_text(
            encoding='utf-8')
        main = (LIB / 'main.py').read_text(encoding='utf-8')
        self.assertIn("self.mode = 'channels'", source)
        self.assertIn("self._intro_deadline = time.monotonic() + 16.0", source)
        self.assertIn("self._switch('hidden')", source)
        self.assertIn('self._overlay.expire_intro()', service)
        self.assertIn("self.url(action='popup_probe')", main)
        self.assertIn("'popup_probe': self._popup_probe", main)
        self.assertIn("'XtreamMate.PopupProbe.KeyCount'", main)
        self.assertIn("'XtreamMate.AutoPopupStatus'", main)


if __name__ == '__main__':
    unittest.main()

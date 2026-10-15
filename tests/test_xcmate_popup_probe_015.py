"""XCMate popup rendering regressions (0.1.17 Android recovery).

Kodi mock APIs prove the dialog dispatch and state transitions, not pixels
or actual focus behavior on a RockChip box with Titan BINGIE MOD.
"""
import importlib.util
from pathlib import Path
import sys
import time
import types
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'src/plugin.video.xtreammate/resources/lib'
XML = ROOT / 'src/plugin.video.xtreammate/resources/skins/Default/720p/XCMatePopupTest.xml'


class Label:
    def __init__(self):
        self.label = ''
    def setLabel(self, label):
        self.label = label


class Window:
    data = {}
    def __init__(self, wid):
        self.wid = wid
    def setProperty(self, key, value):
        self.data[key] = str(value)
    def getProperty(self, key):
        return self.data.get(key, '')


class Action:
    def __init__(self, key, raw=0):
        self.key = key
        self.raw = raw
    def getId(self):
        return self.key
    def getButtonCode(self):
        return self.raw


class XMLDialog:
    instances = []
    def __init__(self, *args):
        self.args = args
        self.controls = {52: Label(), 53: Label()}
        self.focus = None
        self.closed = False
        self.__class__.instances.append(self)
    def getControl(self, key):
        return self.controls[key]
    def setFocusId(self, control_id):
        self.focus = control_id
    def close(self):
        self.closed = True
    def doModal(self):
        self.onInit()
        self.onAction(Action(4, 16))
        self.onAction(Action(1, 15))
        self.onAction(Action(7, 13))
        self.onAction(Action(92, 61448))


class NativeDialog:
    response = 0
    selections = []
    errors = []
    def select(self, title, choices):
        self.__class__.selections.append((title, choices))
        return self.__class__.response
    def ok(self, title, description):
        self.__class__.errors.append((title, description))


class PopupTest(unittest.TestCase):
    def setUp(self):
        Window.data = {}
        NativeDialog.response = 0
        NativeDialog.selections = []
        NativeDialog.errors = []
        XMLDialog.instances = []
        gui = types.ModuleType('xbmcgui')
        gui.WindowXMLDialog = XMLDialog
        gui.Window = Window
        gui.Dialog = NativeDialog
        addon = types.ModuleType('xbmcaddon')
        addon.Addon = lambda: types.SimpleNamespace(
            getAddonInfo=lambda k: '/tmp/fixture-xcmate')
        p = mock.patch.dict(sys.modules, {'xbmcgui': gui, 'xbmcaddon': addon})
        p.start()
        self.addCleanup(p.stop)
        spec = importlib.util.spec_from_file_location('xcmate_popup_xml_test', LIB/'popup_probe.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_visible_native_dialog_precedes_custom_xml(self):
        self.module.run_popup_test()
        self.assertEqual(len(NativeDialog.selections), 1)
        self.assertIn('SICHTBARER POPUP-TEST', NativeDialog.selections[0][0])
        self.assertEqual(len(XMLDialog.instances), 1)
        self.assertEqual(XMLDialog.instances[0].args, (
            'XCMatePopupTest.xml', '/tmp/fixture-xcmate', 'Default', '720p'))
        self.assertEqual(Window.data[self.module.STATUS], 'XML: PER ZURÜCK GESCHLOSSEN')
        self.assertEqual(Window.data[self.module.KEY_COUNT], '4')
        self.assertIn('Zurück', Window.data[self.module.LAST_KEY])

    def test_native_only_option_keeps_tv_off(self):
        NativeDialog.response = 1
        self.module.run_popup_test()
        self.assertEqual(XMLDialog.instances, [])
        self.assertIn('KODI-DIALOG SICHTBAR', Window.data[self.module.STATUS])
        self.assertEqual(Window.data[self.module.KEY_COUNT], '0')

    def test_native_back_does_not_open_xml(self):
        NativeDialog.response = -1
        self.module.run_popup_test()
        self.assertEqual(XMLDialog.instances, [])
        self.assertIn('MIT ZURÜCK', Window.data[self.module.STATUS])

    def test_xml_action_focus_and_click(self):
        dialog = self.module.PopupXMLProbe('XCMatePopupTest.xml', '/addon', 'Default', '720p')
        dialog.onInit()
        self.assertEqual(dialog.focus, self.module.BUTTON_TEST)
        dialog.onAction(Action(1, 21))
        self.assertEqual(dialog.focus, self.module.BUTTON_CLOSE)
        dialog.onAction(Action(2, 22))
        self.assertEqual(dialog.focus, self.module.BUTTON_TEST)
        dialog.onAction(Action(7, 23))
        self.assertFalse(dialog.closed)
        self.assertIn('OK', Window.data[self.module.LAST_KEY])
        dialog.onClick(self.module.BUTTON_CLOSE)
        self.assertTrue(dialog.closed)
        self.assertIn('GESCHLOSSEN', Window.data[self.module.STATUS])

    def test_xml_load_failure_reports_type_only_and_visible_native_message(self):
        NativeDialog.response = 0
        with mock.patch.object(XMLDialog, 'doModal', side_effect=RuntimeError('private stuff')):
            self.module.run_popup_test()
        self.assertEqual(Window.data[self.module.STATUS], 'XML-FEHLER: RuntimeError')
        self.assertNotIn('private stuff', str(NativeDialog.errors))
        self.assertEqual(len(NativeDialog.errors), 1)

    def test_xml_layout_is_self_owned_and_has_focused_controls(self):
        root = ET.parse(XML).getroot()
        self.assertEqual(root.tag, 'window')
        buttons = [x for x in root.iter('control') if x.get('type') == 'button']
        self.assertEqual({x.get('id') for x in buttons}, {'100', '101'})
        self.assertTrue(all(x.find('texturefocus') is not None for x in buttons))
        ids = {x.get('id') for x in root.iter('control')}
        self.assertGreaterEqual(len(ids), 5)
        self.assertIn('52', ids)
        self.assertIn('53', ids)
        self.assertTrue(XML.read_text(encoding='utf-8').count('special://home/addons/plugin.video.xtreammate/') >= 2)

    def test_live_intro_still_exists_and_no_autostart_for_popup(self):
        source = (LIB / 'live_overlay.py').read_text(encoding='utf-8')
        service = (ROOT / 'src/plugin.video.xtreammate/service.py').read_text(
            encoding='utf-8')
        main = (LIB / 'main.py').read_text(encoding='utf-8')
        self.assertIn("self.mode = 'channels'", source)
        self.assertIn("self._intro_deadline = time.monotonic() + 16.0", source)
        self.assertIn("self._overlay.expire_intro()", service)
        self.assertIn("'popup_probe': self._popup_probe", main)
        self.assertIn("self.url(action='popup_probe')", main)
        self.assertIn("setting_bool('autoplay_diagnostics_safe', True)", main)


if __name__ == '__main__':
    unittest.main()

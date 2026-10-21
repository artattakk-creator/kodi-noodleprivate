"""XCMate 0.1.29.3 first-install remote focus and safe setup diagnostics."""
import importlib.util
from pathlib import Path
import sys
import threading
import types
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/plugin.video.xtreammate/resources/lib/setup_window.py"
XML = ROOT / "src/plugin.video.xtreammate/resources/skins/Default/720p/XCMateSetup.xml"


class FakeControl:
    def __init__(self):
        self.visible = True
        self.label = ""
        self.text = ""
        self.percent = -1
        self.items = []
    def setText(self, val):
        self.text = str(val)
    def setPercent(self, val):
        self.percent = val
    def setLabel(self, val):
        self.label = str(val)
    def setVisible(self, val):
        self.visible = val
    def reset(self):
        self.items = []
    def addItems(self, vals):
        self.items.extend(vals)
    def selectItem(self, pos):
        self.position = pos
    def getSelectedPosition(self):
        return getattr(self, "position", -1)


class FakeWindowXML:
    def __init__(self, *args):
        self.controls = {}
        self.focus = None
        self.closed = False
    def getControl(self, cid):
        return self.controls.setdefault(cid, FakeControl())
    def setFocusId(self, cid):
        self.focus = cid
    def close(self):
        self.closed = True


class FakeDraft:
    def __init__(self):
        self.categories = {"live": [], "vod": [], "series": []}
        self.selected = {"live": set(), "vod": set(), "series": set()}
        self.data = {"name": "Testportal", "type": "xtream"}
        self.report = {"live": 0, "vod": 0, "series": 0, "epg": 0,
                       "sources": [], "warnings": []}
        self.disposed = False
    def dispose(self):
        self.disposed = True


class SetupFirstRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_gui = types.ModuleType("xbmcgui")
        fake_gui.WindowXML = FakeWindowXML
        fake_gui.ListItem = lambda label: types.SimpleNamespace(label=label)
        localization = types.ModuleType("localization")
        localization.tr = lambda key, *a: "localized:{}:{}".format(key, a)
        with patch.dict(sys.modules, {"xbmcgui": fake_gui,
                                      "localization": localization}):
            spec = importlib.util.spec_from_file_location(
                "_xcmate_first_run_test_module", SOURCE)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def new_window(self):
        window = self.module.SetupWindow()
        window.configure(FakeDraft())
        self.addCleanup(window._pool.shutdown, wait=False, cancel_futures=True)
        # Simulate queued async tasks without network/GUI thread races.
        self.addCleanup(patch.stopall)
        patcher = patch.object(self.module.WorkWindow, "work",
                               lambda win, job, apply: setattr(win, "_test_job", job))
        patcher.start()
        return window

    def test_discovery_has_visible_cancel_focus_not_empty_list(self):
        win = self.new_window()
        win.onInit()
        self.assertEqual(win.focus, 18)
        self.assertTrue(win.getControl(18).visible)
        self.assertFalse(win.getControl(100).visible)
        self.assertFalse(win.getControl(17).visible)
        self.assertEqual(win.stage, "discover")

    def test_known_auth_failure_uses_safe_diagnosis(self):
        code, message = self.module._failure_details(
            ValueError("authentication failed"))
        self.assertEqual(code, "XM-SETUP-AUTH")
        self.assertIn("Benutzername", message)

    def test_other_provider_value_does_not_echo_credentials(self):
        sensitive = "https://example.invalid/api?username=abc&password=secret"
        code, message = self.module._failure_details(ValueError(sensitive))
        self.assertEqual(code, "XM-SETUP-DATA")
        self.assertNotIn("secret", message)
        self.assertNotIn("example.invalid", message)

    def test_group_or_selection_errors_are_distinguished(self):
        for problem, expected in [
            ("no usable categories", "XM-SETUP-GROUPS"),
            ("select at least one category", "XM-SETUP-SELECT"),
            ("no selected content imported", "XM-SETUP-EMPTY"),
        ]:
            with self.subTest(problem=problem):
                self.assertEqual(
                    self.module._failure_details(ValueError(problem))[0],
                    expected)

    def test_failed_discovery_is_navigable_with_retry_button(self):
        win = self.new_window()
        win.onInit()
        stub = types.ModuleType("utils")
        stub.warn = lambda msg: None
        with patch.dict(sys.modules, {"utils": stub}):
            win.failed_work(ValueError("authentication failed"))
        self.assertEqual(win.stage, "failed")
        self.assertEqual(win.focus, 17)
        self.assertTrue(win.getControl(17).visible)
        self.assertTrue(win.getControl(18).visible)
        self.assertFalse(win.getControl(100).visible)
        self.assertIn("XM-SETUP-AUTH", win.getControl(3).text)
        win.onClick(17)
        self.assertEqual(win.stage, "discover")
        self.assertEqual(win.focus, 18)
        self.assertFalse(win.getControl(100).visible)

    def test_cancel_still_operates_during_discovery(self):
        win = self.new_window()
        win.onInit()
        win.onClick(18)
        self.assertTrue(win.closed)

    def test_discovery_auto_focuses_first_nonempty_group_kind(self):
        win = self.new_window()
        win.draft.categories["vod"] = [
            {"category_id": "7", "category_name": "Filme"}]
        win.onInit()
        win.discovered(win.draft.categories)
        self.assertEqual(win.stage, "groups")
        self.assertEqual(win.kind, "vod")
        self.assertEqual(win.focus, 100)
        self.assertEqual(len(win.getControl(100).items), 1)

    def test_xml_has_focus_marker_and_colored_buttons(self):
        root = ET.parse(XML).getroot()
        lst = root.find("./controls/control[@id='100']")
        self.assertIsNotNone(lst)
        focused = lst.find("focusedlayout")
        self.assertIn("▶", focused.find(".//label").text)
        button = root.find("./controls/control[@id='17']")
        self.assertEqual(button.findtext("focusedcolor"), "FF00E5FF")


if __name__ == "__main__":
    unittest.main()

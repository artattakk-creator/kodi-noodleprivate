"""XCMate 0.1.11 remote regression: XCMate-only bridge and native Android GUI.

This uses a Kodi API simulation, NOT hardware acceptance evidence.
"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

LIB = Path(__file__).resolve().parents[1] / "src/plugin.video.xtreammate/resources/lib"


def import_module(name, file):
    spec = importlib.util.spec_from_file_location(name, LIB / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestXCMateKeymap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        xbmc = types.ModuleType("xbmc")
        self.builtins = []
        xbmc.executebuiltin = lambda cmd: self.builtins.append(cmd)
        xbmc.Player = lambda: types.SimpleNamespace(isPlayingVideo=lambda: False)
        gui = types.ModuleType("xbmcgui")
        gui.WindowDialog = type("WindowDialog", (), {})
        vfs = types.ModuleType("xbmcvfs")
        vfs.translatePath = lambda x: self.tmp.name
        utils = types.ModuleType("utils")
        utils.addon_data_dir = lambda: self.tmp.name
        utils.info = utils.warn = lambda *args, **kw: None
        # Legacy test explicitly opts in to the optional fallback keymap.
        utils.setting_bool = lambda key, default=False: True
        p = mock.patch.dict(sys.modules, {
            "xbmc": xbmc, "xbmcgui": gui, "xbmcvfs": vfs, "utils": utils,
        })
        p.start()
        self.addCleanup(p.stop)
        self.remote = import_module("test_xcmate_011_remote", "remote_control.py")

    def test_keymap_includes_video_keys_and_longpress_without_global(self):
        xml = self.remote.build_keymap()
        root = ET.fromstring(xml[xml.index("<keymap>"):])
        self.assertIsNone(root.find("./global"))
        self.assertIsNone(root.find("./Global"))
        for dev, key in (("keyboard", "left"), ("keyboard", "right"),
                         ("keyboard", "return"), ("keyboard", "escape"),
                         ("remote", "left"), ("remote", "right"),
                         ("remote", "select"), ("remote", "back")):
            self.assertIsNotNone(root.find("./FullscreenVideo/{}/{}".format(dev, key)))
        self.assertIsNotNone(root.find('./FullscreenVideo/remote/select[@mod="longpress"]'))
        self.assertIsNotNone(root.find('./FullscreenVideo/keyboard/left[@mod="longpress"]'))

    def test_autokeymap_preserves_explicit_disable_and_foreign_maps(self):
        remote = self.remote
        self.assertEqual(remote.ensure_for_live_tv(), "aktiviert")
        self.assertTrue(remote.is_enabled())
        self.assertEqual(remote.ensure_for_live_tv(), "aktiv")
        remote.disable()
        self.assertTrue(remote.opted_out())
        self.assertFalse(remote.is_enabled())
        self.assertEqual(remote.ensure_for_live_tv(), "vom Nutzer deaktiviert")
        self.assertFalse(Path(remote.keymap_path()).exists())
        flag = Path(remote._opt_out_path())
        flag.unlink()
        foreign = Path(remote.keymap_path())
        foreign.write_text("<keymap>foreign</keymap>", encoding="utf-8")
        self.assertIn("Konflikt", remote.ensure_for_live_tv())
        self.assertEqual(foreign.read_text(encoding="utf-8"), "<keymap>foreign</keymap>")

    def test_bridge_active_and_falls_back_outside_xcmate(self):
        bridge = import_module("test_xcmate_011_bridge", "remote_bridge.py")
        props = {}
        class Window:
            def getProperty(self, name): return props.get(name, "")
            def setProperty(self, name, value): props[name] = value
        win = Window()
        active = types.SimpleNamespace(isPlayingVideo=lambda: True)
        idle = types.SimpleNamespace(isPlayingVideo=lambda: False)
        self.assertFalse(bridge.route("left", win, idle, now=100))
        self.assertEqual(self.builtins[-1], "Action(left)")
        self.assertFalse(bridge.route("menu", win, idle, now=100))
        self.assertEqual(self.builtins[-1], "Action(contextmenu)")
        self.assertFalse(bridge.route("not_a_key", win, idle, now=100))
        props["XtreamMate.LiveSession"] = json.dumps({
            "pid": "test", "sid": "42", "nonce": "one", "at": 100,
        })
        self.assertTrue(bridge.route("left", win, active, now=100))
        self.assertEqual(json.loads(props["XtreamMate.RemoteCommand"])["action"], "left")
        self.assertTrue(bridge.route("long_ok", win, active, now=101))
        self.assertEqual(json.loads(props["XtreamMate.RemoteCommand"])["action"], "long_ok")
        self.assertFalse(bridge.route("right", win, idle, now=102))
        self.assertEqual(self.builtins[-1], "Action(right)")
        self.assertFalse(bridge.route("right", win, active, now=86500))
        self.assertEqual(self.builtins[-1], "Action(right)")


class TestNativeOverlayKeyHandling(unittest.TestCase):
    def test_command_mapping_bypasses_kodi_osd(self):
        xbmc = types.ModuleType("xbmc")
        paused = []
        player = types.SimpleNamespace(
            pause=lambda: paused.append("pause"), stop=lambda: paused.append("stop"))
        xbmc.Player = lambda: player
        gui = types.ModuleType("xbmcgui")
        gui.WindowDialog = type("WindowDialog", (), {})
        properties = {}
        class Window:
            def setProperty(self, k, v): properties[k] = v
            def getProperty(self, k): return properties.get(k, "")
        gui.Window = lambda number: Window()
        utils = types.ModuleType("utils")
        utils.info = utils.warn = lambda *args: None
        remote_profile = types.ModuleType("remote_profiles")
        remote_profile.mapped_action = lambda key: {
            1: "left", 3: "up", 4: "down", 7: "ok", 92: "left",
            117: "epg",
        }.get(key)
        with mock.patch.dict(sys.modules, {
            "xbmc": xbmc, "xbmcgui": gui, "utils": utils,
            "remote_profiles": remote_profile,
        }):
            mod = import_module("test_011_overlay", "live_overlay.py")
            overlay = mod.LiveNavigator.__new__(mod.LiveNavigator)
            overlay.mode = "hidden"
            overlay._info_timeout = 8
            overlay._accept_input = lambda: True
            overlay._focus_main = 0
            overlay._focus_extra = 0
            overlay.main_buttons = [1, 2, 3, 4, 5]
            overlay._main_indices = [0,1,2,3,4]
            overlay.extra_buttons = [1, 2, 3, 4, 5]
            overlay._recent = lambda: seen.append("recent")
            overlay._zap = lambda step: seen.append(("zap", step))
            overlay._switch = lambda mode: setattr(overlay, "mode", mode)
            overlay._render = lambda: None
            overlay._execute = lambda mode, idx: seen.append((mode, idx))
            overlay._select = lambda: seen.append("select")
            overlay._epg = lambda: seen.append("info")
            overlay.close = lambda: seen.append('closed')
            seen = []
            action = lambda key: types.SimpleNamespace(
                getId=lambda: key, getButtonCode=lambda: 0)
            overlay.onAction(action(1))
            self.assertEqual(overlay.mode, "channels")
            overlay.onAction(action(92))
            self.assertEqual(overlay.mode, "hidden")
            overlay.onAction(action(3))
            overlay.onAction(action(4))
            self.assertEqual(seen[:2], [("zap", 1), ("zap", -1)])
            overlay.onAction(action(2))
            self.assertIn("recent", seen)
            overlay.handle_command("ok")
            self.assertEqual(overlay.mode, "info")
            overlay.handle_command("ok")
            self.assertEqual(overlay.mode, "controls")
            overlay.onAction(action(2))
            self.assertEqual(overlay._focus_main, 1)
            overlay.onAction(action(1))
            self.assertEqual(overlay._focus_main, 0)
            overlay.handle_command("ok")
            self.assertIn(("controls", 0), seen)
            overlay.onAction(action(117))
            self.assertEqual(overlay.mode, "extras")
            overlay.onAction(action(92))
            self.assertEqual(overlay.mode, "controls")
            overlay.onAction(action(92))
            self.assertEqual(overlay.mode, "info")
            overlay.onAction(action(92))
            self.assertEqual(overlay.mode, "hidden")
            overlay.onAction(action(92))
            self.assertIn('closed',seen)
            overlay.onAction(action(12))
            self.assertEqual(paused, ["pause"])
            self.assertGreaterEqual(int(properties["XtreamMate.NativeActionCount"]), 10)
            self.assertEqual(properties["XtreamMate.LastHandledKey"], "play_pause")


if __name__ == "__main__":
    unittest.main()

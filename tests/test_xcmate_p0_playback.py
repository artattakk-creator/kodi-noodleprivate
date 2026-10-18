"""XCMate P0: Kodi playable-item, RunPlugin and privacy regression tests.

A lightweight Kodi API stand-in distinguishes setResolvedUrl from Player.play;
these are API contract tests, not an Android device acceptance test.
"""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "src/plugin.video.xtreammate/resources/lib"


class _Item:
    def __init__(self, path=""):
        self._path = path

    def getPath(self):
        return self._path


class _Window:
    def __init__(self):
        self.properties = {}

    def getProperty(self, name):
        return self.properties.get(name, "")

    def setProperty(self, name, value):
        self.properties[name] = value


class _Player:
    def __init__(self):
        self.played = []

    def isPlayingVideo(self):
        return False

    def play(self, path, item):
        self.played.append((path, item))


class StartupKodiContractTests(unittest.TestCase):
    def setUp(self):
        path=mock.patch.object(sys,'path',[str(LIB),*sys.path])
        path.start()
        self.addCleanup(path.stop)
        self.resolved = []
        self.announced = []
        self.builtins = []
        self.notifications = []
        self.window = _Window()
        self.player = _Player()
        self.settings = {}
        self.portal = {
            "id": "portal-1", "type": "xtream",
            "xc_host": "https://example.invalid", "xc_user": "test-user",
            "xc_pass": "test-password", "start_stream_id": "27",
            "autoplay_start": True,
        }
        utils = types.ModuleType("utils")
        for name in ("setting", "setting_int",
                     "load_favourites", "toggle_favourite", "is_favourite",
                     "cache_clear", "apply_lang_sort", "_L"):
            setattr(utils, name, lambda *args, **kw: "")
        utils.setting_bool = lambda name, default=False: self.settings.get(name, default)
        for name in ("debug", "info", "warn", "error"):
            setattr(utils, name, lambda *args, **kw: None)
        utils.notify = lambda *args: self.notifications.append(args)
        xbmc = types.ModuleType("xbmc")
        xbmc.Player = lambda: self.player
        xbmc.executebuiltin = lambda command: self.builtins.append(command)
        gui = types.ModuleType("xbmcgui")
        gui.Window = lambda number: self.window
        gui.ListItem = _Item
        plugin = types.ModuleType("xbmcplugin")
        plugin.setResolvedUrl = lambda *args: self.resolved.append(args)
        addon = types.ModuleType("xbmcaddon")
        addon.Addon = lambda: types.SimpleNamespace(
            getAddonInfo=lambda key: "plugin.video.xtreammate" if key == "id" else "/tmp/xcmate")
        portals = types.ModuleType("portals")
        portals.get_by_id = lambda pid: self.portal if pid == "portal-1" else None
        xtream = types.ModuleType("xtream")
        class Client:
            def __init__(inner, host, user, password):
                self.assertEqual(password, "test-password")
            def get_cached_catalog(inner, action):
                self.assertEqual(action, "get_live_streams")
                return [{"stream_id": 27, "name": "Example TV", "stream_icon": ""}]
            def live_stream_url(inner, sid, ext):
                return "https://example.invalid/live/stream.ts"
        xtream.XtreamClient = Client
        player_module = types.ModuleType("player")
        player_module.build_playable_item = lambda url, title, logo: _Item(url)
        live = types.ModuleType("live_overlay")
        live.announce = lambda *args: self.announced.append(args)
        modules = {
            "xbmc": xbmc, "xbmcgui": gui, "xbmcplugin": plugin,
            "xbmcaddon": addon, "xbmcvfs": types.ModuleType("xbmcvfs"),
            "utils": utils, "portals": portals, "xtream": xtream,
            "player": player_module, "live_overlay": live,
        }
        patcher = mock.patch.dict(sys.modules, modules)
        patcher.start()
        self.addCleanup(patcher.stop)
        spec = importlib.util.spec_from_file_location("xcmate_p0_contract_main", LIB / "main.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.router = module.Router([
            "plugin://plugin.video.xtreammate", "41",
            "?action=play_start&pid=portal-1",
        ])

    def test_manual_playable_uses_resolver_and_never_direct_player(self):
        self.router._play_start()
        self.assertEqual(len(self.resolved), 1)
        self.assertEqual(self.resolved[0][:2], (41, True))
        self.assertEqual(self.resolved[0][2].getPath(),
                         "https://example.invalid/live/stream.ts")
        self.assertEqual(self.player.played, [])
        self.assertEqual(self.announced[0][:2], ("portal-1", "27"))

    def test_runplugin_autoplay_uses_direct_player_only(self):
        # This old playback contract applies when diagnostics guard is explicitly off.
        self.settings["autoplay_diagnostics_safe"] = False
        self.router._maybe_autoplay_start(self.portal)
        self.assertEqual(len(self.builtins), 1)
        self.assertIn("action=play_start_direct", self.builtins[0])
        self.assertNotIn("PlayMedia(", self.builtins[0])
        self.router._play_start_direct()
        self.assertEqual(len(self.player.played), 1)
        self.assertEqual(self.resolved, [])
        self.assertEqual(self.player.played[0][0],
                         "https://example.invalid/live/stream.ts")

    def test_autoplay_diagnostic_safe_by_default_keeps_manual_play(self):
        # Primary regression: initial single-portal entry must not autostart
        # while the foreground popup test is about to open.
        self.assertTrue(self.portal["autoplay_start"])
        self.router._maybe_autoplay_start(self.portal)
        self.assertEqual(self.builtins, [])
        self.assertIn("PAUSIERT", self.window.getProperty(
            "XtreamMate.AutoplayDiagnosticState"))
        self.router._play_start_direct()
        self.assertEqual(len(self.player.played), 1)
        self.assertTrue(self.portal["autoplay_start"])

    def test_invalid_start_returns_failed_playable_not_empty_directory(self):
        self.router._params["pid"] = "missing"
        self.router._play_start()
        self.assertEqual([(handle, success) for handle, success, _ in self.resolved],
                         [(41, False)])
        self.assertEqual(self.player.played, [])

    def test_playback_debug_does_not_log_stream_url(self):
        source = (LIB / "player.py").read_text(encoding="utf-8")
        self.assertIn("direct playback: stream URL redacted", source)
        self.assertNotIn("debug(f'direct playback: {final", source)


if __name__ == "__main__":
    unittest.main()

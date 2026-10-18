"""XCMate 0.1.21: no accidental global keymap and incremental XMLTV parsing."""
import gzip
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
import xml.etree.ElementTree as ET
from unittest import mock

LIB = Path(__file__).resolve().parents[1] / "src/plugin.video.xtreammate/resources/lib"
sys.path.insert(0, str(LIB))


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, LIB / file)
    instance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(instance)
    return instance


class RemoteSafetyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = temp.name
        self.prefs = {"xc_remote_keymap_fallback": False}
        self.commands = []
        xbmc = types.ModuleType("xbmc")
        xbmc.executebuiltin = self.commands.append
        gui = types.ModuleType("xbmcgui")
        vfs = types.ModuleType("xbmcvfs")
        vfs.translatePath = lambda *_: self.path
        utils = types.ModuleType("utils")
        utils.addon_data_dir = lambda: self.path
        utils.setting_bool = lambda key, default=False: self.prefs.get(key, default)
        self.patch = mock.patch.dict(sys.modules, {
            "xbmc": xbmc, "xbmcgui": gui, "xbmcvfs": vfs, "utils": utils,
        })
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.remote = _module("xcmate_remote_safety_021", "remote_control.py")

    def test_default_never_installs_global_keymap(self):
        result = self.remote.ensure_for_live_tv()
        self.assertIn("native", result)
        self.assertFalse(os.path.exists(self.remote.keymap_path()))

    def test_retire_only_old_owned_keymap(self):
        self.remote.enable()
        self.assertTrue(os.path.exists(self.remote.keymap_path()))
        self.assertTrue(self.remote.release_unrequested_keymap())
        self.assertFalse(os.path.exists(self.remote.keymap_path()))
        self.assertFalse(self.remote.release_unrequested_keymap())
        self.assertIn("Action(reloadkeymaps)", self.commands)

    def test_foreign_keymap_is_never_removed(self):
        f = Path(self.remote.keymap_path())
        f.write_text("<keymap><FullscreenVideo/></keymap>", encoding="utf-8")
        self.assertFalse(self.remote.release_unrequested_keymap())
        self.assertIn("FullscreenVideo", f.read_text(encoding="utf-8"))

    def test_explicit_optin_preserves_fallback_keymap(self):
        self.prefs["xc_remote_keymap_fallback"] = True
        self.assertEqual(self.remote.ensure_for_live_tv(), "aktiviert")
        self.assertFalse(self.remote.release_unrequested_keymap())
        self.assertTrue(self.remote.is_enabled())


class EpgIncrementalTests(unittest.TestCase):
    def setUp(self):
        vfs = types.ModuleType("xbmcvfs")
        utils = types.ModuleType("utils")
        utils.info = lambda *a, **kw: None
        utils.error = lambda *a, **kw: None
        for name in ("http_get", "cache_get", "cache_set", "cache_key", "setting_bool",
                     "setting_int", "setting", "debug", "warn"):
            setattr(utils, name, lambda *args, **kw: None)
        patch = mock.patch.dict(sys.modules, {"xbmcvfs": vfs, "utils": utils})
        patch.start()
        self.addCleanup(patch.stop)
        self.epg = _module("xcmate_epg_incremental_021", "epg.py")

    def test_xmltv_still_returns_guide_and_sorted_entries(self):
        sample = b'''<tv><channel id="sky.test"><display-name>Sky Cinema</display-name></channel>
<programme channel="sky.test" start="20261018130000 +0200" stop="20261018140000 +0200">
<title>Film B</title><desc>Description</desc><category>Film</category>
<episode-num system="xmltv_ns">0.1.</episode-num></programme>
<programme channel="sky.test" start="20261018110000 +0200" stop="20261018120000 +0200">
<title>Film A</title></programme></tv>'''
        # The former ET.fromstring created a full XML tree.
        with mock.patch.object(self.epg.ET, "fromstring", side_effect=AssertionError("bulk parse")):
            channels, programmes = self.epg.parse_xmltv(gzip.compress(sample))
        self.assertEqual(channels, {"sky.test": "Sky Cinema"})
        self.assertEqual([x["name"] for x in programmes["sky.test"]], ["Film A", "Film B"])
        self.assertEqual(programmes["sky.test"][1]["episode"], "S01E02")
        self.assertEqual(programmes["sky.test"][1]["descr"], "Description")

    def test_large_guide_and_invalid_xml(self):
        data = ["<tv><channel id='ch'><display-name>CH</display-name></channel>"]
        for idx in range(2500):
            data.append("<programme channel='ch' start='20261018120000 +0200' "
                        "stop='20261018130000 +0200'><title>%d</title></programme>" % idx)
        data.append("</tv>")
        channels, programs = self.epg.parse_xmltv("".join(data).encode("utf-8"))
        self.assertEqual(channels["ch"], "CH")
        self.assertEqual(len(programs["ch"]), 2500)
        self.assertEqual(self.epg.parse_xmltv(b"<tv><programme>"), ({}, {}))


if __name__ == "__main__":
    unittest.main()

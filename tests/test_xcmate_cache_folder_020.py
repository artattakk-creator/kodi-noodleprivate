"""Regression checks for the XCMate browse-and-save cache directory and startup safety."""
import ast
import os
import pathlib
import tempfile
import unittest
import time
import uuid
import xml.etree.ElementTree as ET
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1] / "src/plugin.video.xtreammate"


class MemoryVFS:
    def __init__(self, root, missing=None):
        self.root = root
        self.dirs = {root}
        self.files = set()
        self.deleted = []
        self.missing = missing

    def translatePath(self, path):
        return path.replace("special://userdata/addon_data/plugin.video.xtreammate/cache/", self.root)

    def exists(self, path):
        return path in self.dirs or path in self.files

    def mkdirs(self, path):
        if path == self.missing:
            return False
        self.dirs.add(path)
        return True

    def File(self, path, mode='r'):
        class File:
            def __enter__(inner): return inner
            def __exit__(inner, *args): pass
            def write(inner, value):
                self.files.add(path)
                return True
        return File()

    def listdir(self, path):
        return [], [os.path.basename(f) for f in self.files if os.path.dirname(f) == path]

    def delete(self, path):
        self.deleted.append(path)
        self.files.discard(path)


class CacheFolderRegression(unittest.TestCase):
    def test_kodi_folder_browser_is_saved_in_standard_setting(self):
        tree = ET.parse(ROOT / "resources/settings.xml")
        item = tree.find(".//setting[@id='cache_dir']")
        self.assertIsNotNone(item)
        self.assertEqual(item.get("type"), "folder")
        self.assertEqual(item.get("option"), "writeable")
        self.assertEqual(item.get("source"), "auto")
        self.assertEqual(item.get("default"), "")

    def _load_cache_functions(self, location, missing=None):
        source = (ROOT / "resources/lib/utils.py").read_text(encoding="utf-8")
        parsed = ast.parse(source)
        names = ("cache_dir", "cache_clear", "_cache_is_writable", "_private_cache_dir")
        nodes = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name in names]
        self.assertEqual(len(nodes), len(names))
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        vfs = MemoryVFS(temp.name, missing)
        notices = []
        ns = dict(os=os, time=time, uuid=uuid, _CACHE_WRITABLE={}, xbmcvfs=vfs, ADDON_ID="plugin.video.xtreammate",
                  setting=lambda key: location if key == "cache_dir" else "",
                  warn=notices.append, info=lambda *a: None)
        exec(compile(ast.Module(body=nodes, type_ignores=[]), "<cache>", "exec"), ns)
        return ns, vfs, notices

    def test_chosen_folder_is_used_and_default_still_works(self):
        ns, vfs, _ = self._load_cache_functions("")
        self.assertEqual(ns["cache_dir"](), vfs.root)
        location = os.path.join(vfs.root, "manual")
        ns, vfs, _ = self._load_cache_functions(location)
        self.assertEqual(ns["cache_dir"](), location)

    def test_unavailable_folder_falls_back_without_destroying_settings(self):
        bad = "/unavailable/device/cache"
        ns, vfs, messages = self._load_cache_functions(bad, missing=bad)
        self.assertEqual(ns["cache_dir"](), vfs.root)
        self.assertTrue(messages)

    def test_clear_cache_keeps_unrelated_json_files(self):
        ns, vfs, _ = self._load_cache_functions("")
        good = os.path.join(vfs.root, "a"*32 + ".json")
        other = os.path.join(vfs.root, "personal.json")
        vfs.files.update([good, other])
        ns["cache_clear"]()
        self.assertEqual(vfs.deleted, [good])
        self.assertIn(other, vfs.files)

    def test_heavy_background_jobs_are_opt_in_on_new_installations(self):
        settings = (ROOT / "resources/settings.xml").read_text(encoding="utf-8")
        service = (ROOT / "service.py").read_text(encoding="utf-8")
        self.assertIn('id="xc_background_prefetch" type="bool"', settings)
        self.assertIn('default="false"', settings.split('id="xc_background_prefetch"', 1)[1].split('/>', 1)[0])
        self.assertIn("if setting_bool('xc_background_prefetch', False):", service)
        self.assertIn("self._maybe_refresh_epg()", service)
        self.assertIn("self._maybe_warm_catalogs()", service)

    def test_preset_selection_does_not_force_multiple_downloads(self):
        source=(ROOT/"resources/lib/epg_sources.py").read_text(encoding="utf-8")
        piece=source.split("def _choose_preset(portal):",1)[1].split("def _manage_source(",1)[0]
        self.assertNotIn("warmup_async(",piece)


if __name__ == "__main__":
    unittest.main()

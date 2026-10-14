"""Remote zapping and XtreamMate keymap regression tests without Kodi runtime."""
import importlib.util
import os
import sys
import tempfile
import types
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

LIB = Path(__file__).resolve().parents[1] / "src/plugin.video.xtreammate/resources/lib"

def load(name, file):
    spec=importlib.util.spec_from_file_location(name,LIB/file)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class RemoteTest(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        xbmc=types.ModuleType("xbmc")
        xbmc.executebuiltin=lambda *_:None
        gui=types.ModuleType("xbmcgui")
        gui.WindowDialog=type("WindowDialog",(),{})
        vfs=types.ModuleType("xbmcvfs")
        vfs.translatePath=lambda *_:self.directory.name
        utils=types.ModuleType("utils")
        utils.info=utils.warn=lambda *_:None
        utils.addon_data_dir=lambda:self.directory.name
        patch=mock.patch.dict(sys.modules,{"xbmc":xbmc,"xbmcgui":gui,"xbmcvfs":vfs,"utils":utils})
        patch.start()
        self.addCleanup(patch.stop)
        self.overlay=load("xtreammate_test_overlay_012","live_overlay.py")
        self.remote=load("xtreammate_test_remote_012","remote_control.py")

    def test_zapping_stays_in_group_and_wraps(self):
        class Channel:
            def __init__(self,sid,cat):self.extra={"stream_id":sid,"category_id":cat}
        c=[Channel("1","de"),Channel("2","de"),Channel("3","other"),Channel("4","de")]
        step=self.overlay.adjacent_channel
        self.assertEqual(step(c,"de",{"de"},"1",1).extra["stream_id"],"2")
        self.assertEqual(step(c,"de",{"de"},"4",1).extra["stream_id"],"1")
        self.assertEqual(step(c,"de",{"de"},"1",-1).extra["stream_id"],"4")
        self.assertIsNone(step(c,"other",{"de"},"3",1))

    def test_keymap_is_only_fullscreen_and_supports_all_keys(self):
        content=self.remote.build_keymap()
        root=ET.fromstring(content[content.index("<keymap>"):])
        self.assertIsNone(root.find("./Global"))
        for code in ("left","up","down","select"):
            self.assertIsNotNone(root.find("./FullscreenVideo/remote/"+code))
        self.assertIsNotNone(root.find('./FullscreenVideo/remote/select[@mod="longpress"]'))

    def test_keymap_never_replaces_foreign_file(self):
        file=Path(self.remote.keymap_path())
        file.write_text("<keymap/>",encoding="utf-8")
        with self.assertRaises(OSError):self.remote.enable()
        self.assertEqual(file.read_text(),"<keymap/>")
        file.unlink()
        self.assertTrue(self.remote.enable())
        self.assertTrue(self.remote.disable())
        self.assertFalse(file.exists())

if __name__ == "__main__":
    unittest.main()

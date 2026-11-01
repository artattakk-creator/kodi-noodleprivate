"""GS Media Repository 1.8 upgrade and branded artwork release gates."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "src" / "repository.gsmedia"
MANIFEST = REPO / "addon.xml"


class GsMediaRepo180Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = ET.parse(MANIFEST).getroot()

    def test_repo_id_and_incremental_update(self):
        self.assertEqual(self.manifest.get("id"), "repository.gsmedia")
        self.assertEqual(self.manifest.get("version"), "1.8.0")
        self.assertEqual(self.manifest.get("provider-name"), "GS Media")

    def test_upstreams_unchanged_in_safe_upgrade(self):
        dirs = self.manifest.findall("./extension[@point='xbmc.addon.repository']/dir")
        self.assertEqual(len(dirs), 8)
        info = [d.findtext("info") for d in dirs]
        self.assertEqual(len(set(info)), 8)
        expected_sources = (
            "artattakk-creator/kodi-noodleprivate/main/addons.xml",
            "dobbelina/repository.dobbelina/master/addons.xml",
            "Gujal00/smrzips/master/addons.xml",
            "mojomedia1812/xVAULT/main/docs/addons.xml",
            "AchillesPunks/repository.titan.bingie.mod/master/nexus/addons.xml",
            "AchillesPunks/repository.titan.bingie.mod/master/omega/addons.xml",
            "peno64/repository.peno64/master/repo/zips/addons.xml",
            "mr-evil1/kodi-media-repo/main/addons.xml",
        )
        for actual, expected in zip(info, expected_sources):
            self.assertTrue(actual.startswith("https://raw.githubusercontent.com/"))
            self.assertTrue(actual.endswith(expected), (actual, expected))
        self.assertEqual(dirs[5].get("minversion"), "20.9.1")
        self.assertEqual(dirs[5].findtext("checksum"), dirs[5].findtext("info"))
        for d in dirs:
            self.assertTrue(d.findtext("datadir").startswith("https://"))
            self.assertTrue(d.findtext("checksum").startswith("https://"))

    def test_repository_icon_is_first_class_asset(self):
        self.assertEqual(self.manifest.findtext(
            "./extension[@point='xbmc.addon.metadata']/assets/icon"), "icon.png")
        self.assertEqual(self.manifest.findtext(
            "./extension[@point='xbmc.addon.metadata']/assets/fanart"), "fanart.png")

    def test_rendered_icon_is_real_png_with_branding(self):
        from PIL import Image, ImageStat
        import importlib.util
        source = ROOT / "tools" / "render_gsmedia_icon.py"
        spec = importlib.util.spec_from_file_location("gsmedia_renderer_180", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as td:
            dest = module.render(Path(td) / "icon.png")
            self.assertGreater(dest.stat().st_size, 5000)
            with Image.open(dest) as picture:
                self.assertEqual(picture.format, "PNG")
                self.assertEqual(picture.size, (256, 256))
                self.assertGreater(sum(ImageStat.Stat(picture.convert("RGB")).stddev), 50)

    def test_xcmate_release_unchanged(self):
        addon = ET.parse(ROOT / "src" / "plugin.video.xtreammate" / "addon.xml").getroot()
        self.assertEqual(addon.get("version"), "0.1.29.66")
        self.assertEqual(addon.get("id"), "plugin.video.xtreammate")


if __name__ == "__main__":
    unittest.main()

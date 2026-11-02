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
        self.assertEqual(self.manifest.get("version"), "1.8.1")
        self.assertEqual(self.manifest.get("provider-name"), "GS Media")

    def test_only_first_party_catalogue_is_exposed(self):
        dirs = self.manifest.findall("./extension[@point='xbmc.addon.repository']/dir")
        self.assertEqual(len(dirs), 1)
        allowed = "https://raw.githubusercontent.com/artattakk-creator/kodi-noodleprivate/main/"
        self.assertEqual(dirs[0].findtext("info"), allowed + "addons.xml")
        self.assertEqual(dirs[0].findtext("checksum"), allowed + "addons.xml.md5")
        self.assertEqual(dirs[0].findtext("datadir"), allowed)
        self.assertEqual(dirs[0].findtext("hashes"), "false")

    def test_only_three_approved_addon_ids_in_builder(self):
        import ast
        script = ROOT / "tools" / "build_repository.py"
        module = ast.parse(script.read_text(encoding="utf-8"))
        expr = next(
            n.value for n in module.body
            if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "APPROVED_ADDON_IDS" for t in n.targets)
        )
        self.assertIsInstance(expr, ast.Call)
        self.assertEqual(expr.func.id, "frozenset")
        approved = set(ast.literal_eval(expr.args[0]))
        self.assertEqual(approved, {
            "repository.gsmedia", "plugin.video.xtreammate", "plugin.video.noodleprivate"
        })
        source_ids = {p.parent.name for p in (ROOT / "src").glob("*/addon.xml")}
        self.assertEqual(source_ids, approved)

    def test_repository_icon_is_first_class_asset(self):
        self.assertEqual(self.manifest.findtext(
            "./extension[@point='xbmc.addon.metadata']/assets/icon"), "icon-1.8.png")
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
        self.assertEqual(addon.get("version"), "0.1.29.70")
        self.assertEqual(addon.get("id"), "plugin.video.xtreammate")


if __name__ == "__main__":
    unittest.main()

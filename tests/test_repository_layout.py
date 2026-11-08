"""Central GS Media Kodi repository layout and update-source checks."""
import pathlib
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

class RepositoryLayoutTests(unittest.TestCase):
    def test_unique_managed_repository(self):
        repos = sorted(p.name for p in SRC.glob("repository.*") if (p / "addon.xml").is_file())
        self.assertEqual(repos, ["repository.gsmedia"])
    def test_gs_media_only_update_origin(self):
        manifest = ET.parse(SRC / "repository.gsmedia" / "addon.xml").getroot()
        self.assertEqual(manifest.get("id"), "repository.gsmedia")
        self.assertEqual(manifest.get("version"), "1.8.1")
        dirs = manifest.findall("./extension[@point='xbmc.addon.repository']/dir")
        # Lite repository must not aggregate unaudited third-party catalogues.
        self.assertEqual(len(dirs), 1)
        self.assertIn("/kodi-noodleprivate/main/addons.xml", dirs[0].findtext("info"))
        self.assertTrue(dirs[0].findtext("checksum").endswith("/addons.xml.md5"))
        self.assertTrue(dirs[0].findtext("datadir").endswith("/main/"))
    def test_repo_icon_renders_before_publish(self):
        # Repository icon is a first-class package asset, never a placeholder.
        source = (ROOT / "tools" / "render_gsmedia_icon.py")
        self.assertTrue(source.is_file(), "GS Media icon renderer must be versioned")
        manifest = ET.parse(SRC / "repository.gsmedia" / "addon.xml").getroot()
        self.assertEqual(manifest.findtext("./extension[@point='xbmc.addon.metadata']/assets/icon"), "icon-1.8.png")

    def test_no_legacy_repository_in_generated_index(self):
        xml = ET.parse(ROOT / "addons.xml").getroot()
        ids = [entry.get("id") for entry in xml.findall("addon")]
        self.assertNotIn("repository.noodleprivate", ids)
        self.assertEqual([x for x in ids if x.startswith("repository.")], ["repository.gsmedia"])
        self.assertIn("plugin.video.noodleprivate", ids)
        self.assertIn("plugin.video.xtreammate", ids)
    def test_xtreammate_manifest_and_remote_service(self):
        addon_dir = SRC / "plugin.video.xtreammate"
        addon = ET.parse(addon_dir / "addon.xml").getroot()
        self.assertEqual(addon.get("id"), "plugin.video.xtreammate")
        self.assertEqual(addon.get("version"), "0.1.29.81")
        self.assertEqual(addon.get("name"), "XCMate")
        self.assertIsNotNone(addon.find("./extension[@point='xbmc.service']"))
        self.assertTrue((addon_dir / "resources/lib/live_overlay.py").is_file())
        self.assertTrue((addon_dir / "resources/lib/setup_wizard.py").is_file())
        self.assertTrue((addon_dir / "resources/lib/group_selection.py").is_file())
        self.assertTrue((addon_dir / "resources/lib/remote_control.py").is_file())
        self.assertTrue((addon_dir / "resources/lib/remote_bridge.py").is_file())
        self.assertTrue((addon_dir / "resources/lib/startup_preferences.py").is_file())
    def test_plugin_migration_version(self):
        manifest = ET.parse(SRC / "plugin.video.noodleprivate" / "addon.xml").getroot()
        self.assertEqual(manifest.get("version"), "0.4.2")
        self.assertEqual(manifest.get("id"), "plugin.video.noodleprivate")

if __name__ == "__main__":
    unittest.main()

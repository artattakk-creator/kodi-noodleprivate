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
        self.assertEqual(manifest.get("version"), "1.3.0")
        dirs = manifest.findall("./extension[@point='xbmc.addon.repository']/dir")
        self.assertEqual(len(dirs), 4)
        self.assertIn("/kodi-noodleprivate/main/addons.xml", dirs[0].findtext("info"))
    def test_no_legacy_repository_in_generated_index(self):
        xml = ET.parse(ROOT / "addons.xml").getroot()
        ids = [entry.get("id") for entry in xml.findall("addon")]
        self.assertNotIn("repository.noodleprivate", ids)
        self.assertEqual([x for x in ids if x.startswith("repository.")], ["repository.gsmedia"])
        self.assertIn("plugin.video.noodleprivate", ids)
    def test_plugin_migration_version(self):
        manifest = ET.parse(SRC / "plugin.video.noodleprivate" / "addon.xml").getroot()
        self.assertEqual(manifest.get("version"), "0.4.2")
        self.assertEqual(manifest.get("id"), "plugin.video.noodleprivate")

if __name__ == "__main__":
    unittest.main()

"""Offline GS Media setup wizard tests: no Kodi service or network required."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "src" / "script.gsmedia.setup"
MANIFEST = ADDON / "addon.xml"
PLAN = ADDON / "resources" / "lib" / "setup_plan.py"
ENTRY = ADDON / "default.py"

spec = importlib.util.spec_from_file_location("gsmedia_setup_plan", PLAN)
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


class GsMediaWizardScaffoldTests(unittest.TestCase):
    def test_manifest_is_script_not_service_and_requires_only_kodi_python(self):
        root = ET.parse(MANIFEST).getroot()
        self.assertEqual(root.attrib["id"], "script.gsmedia.setup")
        self.assertEqual(root.attrib["version"], "0.1.0")
        self.assertIsNotNone(root.find("./extension[@point='xbmc.python.script']"))
        self.assertIsNone(root.find("./extension[@point='xbmc.service']"))
        deps = [x.attrib["addon"] for x in root.findall("./requires/import")]
        self.assertEqual(deps, ["xbmc.python"])

    def test_four_profiles_are_unique(self):
        names = planner.profile_names()
        self.assertEqual(len(names), 4)
        self.assertEqual(len({x[0] for x in names}), len(names))

    def test_core_includes_bingie_and_tmdb_and_deep_shortcuts(self):
        ids = {r["addon_id"] for r in planner.plan_for("core")}
        self.assertIn("plugin.video.xtreammate", ids)
        self.assertIn("skin.titan.bingie.mod", ids)
        self.assertIn("script.skinshortcuts", ids)
        self.assertIn("plugin.video.themoviedb.helper", ids)
        self.assertIn("script.module.jurialmunkey", ids)
        self.assertIn("script.module.simpleeval", ids)
        self.assertIn("script.module.simplejson", ids)

    def test_slyguy_not_forced_into_bingie_core(self):
        ids = {r["addon_id"] for r in planner.plan_for("core")}
        self.assertNotIn("script.module.slyguy", ids)
        self.assertNotIn("repository.slyguy", ids)

    def test_music_is_optional_and_not_core(self):
        core = {r["addon_id"] for r in planner.plan_for("core")}
        music = {r["addon_id"] for r in planner.plan_for("music")}
        self.assertNotIn("plugin.audio.m3sr2019", core)
        self.assertIn("plugin.audio.m3sr2019", music)
        self.assertIn("plugin.audio.shoutcast", music)

    def test_media_not_forced_into_core(self):
        core = {r["addon_id"] for r in planner.plan_for("core")}
        media = {r["addon_id"] for r in planner.plan_for("media")}
        self.assertNotIn("plugin.video.xvault", core)
        self.assertIn("plugin.video.xvault", media)
        self.assertIn("plugin.video.cumination", media)

    def test_deduplicated_dependency_closure(self):
        rows = planner.plan_for("all")
        ids = [r["addon_id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            next(r["minimum"] for r in rows if r["addon_id"] == "xbmc.python"),
            "3.0.1",
        )

    def test_unknown_addon_manifests_are_not_fake_pass(self):
        rows = planner.plan_for("all")
        by_id = {r["addon_id"]: r for r in rows}
        self.assertFalse(by_id["plugin.audio.shoutcast"]["manifest_known"])
        self.assertFalse(by_id["plugin.video.cumination"]["manifest_known"])
        self.assertTrue(by_id["skin.titan.bingie.mod"]["manifest_known"])

    def test_invalid_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            planner.plan_for("../delete-all")

    def test_scaffold_contains_no_install_uninstall_or_userdata_calls(self):
        source = ENTRY.read_text(encoding="utf-8")
        for forbidden in (
            "InstallAddon(", "UninstallAddon(", "SetEnabled(",
            "executeBuiltin(", "rmtree(", "os.remove(", "unlink(",
            "addon_data", "shutil.rmtree(", "executeJSONRPC(",
        ):
            self.assertNotIn(forbidden, source)
        self.assertNotIn('point="xbmc.service"', MANIFEST.read_text())


if __name__ == "__main__":
    unittest.main()

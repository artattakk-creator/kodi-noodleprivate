"""Safe, offline GS Media Setup 0.2.1 tests; no Kodi runtime needed."""
import importlib
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "src" / "script.gsmedia.setup"
LIB = ADDON / "resources" / "lib"
sys.path.insert(0, str(LIB))
planner = importlib.import_module("setup_plan")
inventory = importlib.import_module("setup_inventory")
gate = importlib.import_module("setup_gate")


class SetupPreflightTests(unittest.TestCase):
    def test_manifest_script_only(self):
        addon = ET.parse(ADDON / "addon.xml").getroot()
        self.assertEqual(addon.get("id"), "script.gsmedia.setup")
        self.assertEqual(addon.get("version"), "0.2.1")
        self.assertIsNotNone(addon.find("./extension[@point='xbmc.python.script']"))
        self.assertIsNone(addon.find("./extension[@point='xbmc.service']"))
        self.assertEqual([e.get("addon") for e in addon.findall("./requires/import")], ["xbmc.python"])

    def test_profiles_preserved(self):
        self.assertEqual({x[0] for x in planner.profile_names()}, {"standard"})

    def test_core_contains_needed_bingie_dependencies(self):
        ids = {r["addon_id"] for r in planner.plan_for("standard")}
        self.assertTrue({"skin.titan.bingie.mod", "plugin.video.xtreammate",
                         "script.skinshortcuts", "script.module.simplejson",
                         "script.module.pil", "script.module.jurialmunkey"} <= ids)
        self.assertIn("repository.slyguy", ids)
        self.assertIn("slyguy.trailers", ids)
        self.assertIn("plugin.video.cumination", ids)

    def test_install_order_is_dependency_first(self):
        rows = planner.plan_for("standard")
        ids = [r["addon_id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        index = {name: i for i, name in enumerate(ids)}
        for name in ids:
            for child, _min in planner.DEPENDENCIES.get(name, ()):
                self.assertLess(index[child], index[name], (child, name))
        self.assertLess(index["skin.titan.bingie.mod"], index["plugin.video.xtreammate"])

    def test_xcmate_pil_and_music_deps(self):
        ids = {r["addon_id"] for r in planner.plan_for("standard")}
        self.assertTrue({"script.module.pil", "script.module.xbmcswift2",
                         "script.module.xmltodict", "script.module.routing"} <= ids)

    def test_all_nine_mandatory_apps_and_cumination_imports(self):
        rows = planner.plan_for("standard")
        ids = {r["addon_id"] for r in rows}
        self.assertEqual(len(planner.MANDATORY), 9)
        self.assertEqual({x["addon_id"] for x in rows if x["mandatory"]}, set(planner.MANDATORY))
        self.assertTrue(set(planner.MANDATORY) <= ids)
        for dep in ("script.module.six", "script.module.kodi-six",
                    "script.module.resolveurl", "script.module.resolveurl.xxx",
                    "script.common.plugin.cache", "script.module.websocket",
                    "script.module.inputstreamhelper", "script.module.requests"):
            self.assertIn(dep, ids)
        for dep in ("slyguy.dependencies", "script.module.slyguy", "repository.slyguy"):
            self.assertIn(dep, ids)
        self.assertNotIn("repository.slyguy.youtube", ids)

    def test_xvault_optional_imports_are_not_falsely_required(self):
        rows = planner.plan_for("standard")
        xvault = next(r for r in rows if r["addon_id"] == "plugin.video.xvault")
        self.assertIn("script.module.download-m3u8", xvault["optional_imports"])
        self.assertIn("script.module.pyqrcode", xvault["optional_imports"])
        self.assertIn("script.module.pydevd", xvault["optional_imports"])
        self.assertNotIn("script.module.pydevd", {r["addon_id"] for r in rows})

    def test_extras_not_implicitly_installed(self):
        ids = {r["addon_id"] for r in planner.plan_for("standard")}
        for addon_id in planner.BACKUP_EXTRAS_FOR_REVIEW:
            self.assertNotIn(addon_id, ids)

    def test_inventory_reads_only_installed_state(self):
        def stub(arg):
            request = json.loads(arg)
            self.assertEqual(request["method"], "Addons.GetAddons")
            self.assertEqual(request["params"]["installed"], True)
            return json.dumps({"jsonrpc": "2.0", "id": 1, "result": {
                "addons": [{"addonid": "plugin.video.xtreammate",
                            "version": "0.1.29.68", "enabled": True},
                           {"addonid": "skin.titan.bingie.mod", "version": "2.2.3", "enabled": False}]}})
        result = inventory.collect(stub)
        self.assertEqual(result["code"], "READY")
        self.assertEqual(result["addons"]["skin.titan.bingie.mod"]["enabled"], False)
        self.assertEqual(len(result["addons"]), 2)

    def test_failed_inventory_does_not_mark_missing(self):
        failed = inventory.collect(lambda _msg: '{"error":{"message":"not ready"}}')
        self.assertEqual(failed["code"], "UNKNOWN")
        result = gate.inspect("standard", failed)
        self.assertEqual(next(r for r in result["rows"] if r["addon_id"] == "skin.titan.bingie.mod")["state"], "INVENTORY_UNKNOWN")

    def test_missing_addons_blocked_and_installer_off(self):
        snap = inventory.collect(lambda _: '{"result":{"addons":[]}}')
        report = gate.inspect("standard", snap)
        self.assertFalse(report["installation_enabled"])
        self.assertGreater(report["blocking"], 0)
        self.assertEqual(next(r for r in report["rows"] if r["addon_id"] == "plugin.audio.m3sr2019")["source"], "BLOCKED_SOURCE_404")

    def test_disabled_skin_never_marked_ready(self):
        data = {"code": "READY", "addons": {"skin.titan.bingie.mod": {"version": "2.2.3", "enabled": False}}}
        report = gate.inspect("standard", data)
        skin = next(x for x in report["rows"] if x["addon_id"] == "skin.titan.bingie.mod")
        self.assertEqual(skin["state"], "INSTALLED_DISABLED")
        self.assertTrue(skin["install_blocked"])

    def test_unknown_or_invalid_profile(self):
        with self.assertRaises(ValueError):
            planner.plan_for("../delete")

    def test_no_mutating_kodi_calls_or_userdata_access(self):
        sources = [ADDON / "default.py", LIB / "setup_inventory.py", LIB / "setup_gate.py", LIB / "setup_plan.py"]
        for path in sources:
            value = path.read_text("utf-8")
            for bad in ("InstallAddon(", "UninstallAddon(", "EnableAddon(",
                        "SetAddonEnabled", "shutil.rmtree(", "addon_data",
                        "xbmc.executebuiltin(", "open("):
                # "open(" would block safe code if these modules read local files; they do not.
                self.assertNotIn(bad, value, (path.name, bad))

if __name__ == "__main__":
    unittest.main()

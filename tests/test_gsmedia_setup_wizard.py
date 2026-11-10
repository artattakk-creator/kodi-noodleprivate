"""Safe, offline GS Media Setup 0.4.0 tests; no Kodi runtime needed."""
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
layout = importlib.import_module("setup_layout")
handoff = importlib.import_module("setup_handoff")
tmdb_player = importlib.import_module("setup_tmdb_player")


class SetupPreflightTests(unittest.TestCase):
    def test_manifest_script_only(self):
        addon = ET.parse(ADDON / "addon.xml").getroot()
        self.assertEqual(addon.get("id"), "script.gsmedia.setup")
        self.assertEqual(addon.get("version"), "0.4.0")
        self.assertIsNotNone(addon.find("./extension[@point='xbmc.python.script']"))
        self.assertIsNotNone(addon.find("./extension[@point='xbmc.service']"))
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
        self.assertEqual(len(planner.MANDATORY), 11)
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

    def test_maintenance_and_log_tools_are_mandatory(self):
        ids = {row["addon_id"] for row in planner.plan_for("standard")}
        self.assertIn("script.ezmaintenanceplus", ids)
        self.assertIn("script.cabertoss", ids)
        self.assertIn("script.module.requests", ids)
        self.assertEqual(planner.DEPENDENCIES["script.ezmaintenanceplus"][0][0], "script.module.requests")
        report = gate.inspect("standard", {"code": "READY", "addons": {}})
        self.assertEqual(next(r for r in report["rows"] if r["addon_id"] == "script.cabertoss")["source"], "OFFICIAL_KODI_REVIEW")
        self.assertFalse(report["installation_enabled"])

    def test_bingie_menu_from_archived_user_shortcuts(self):
        report = layout.verify()
        menu = {x["label"]: x["target"] for x in report["menu"]}
        self.assertIn("plugin.video.cumination", menu["XXX"])
        self.assertIn("plugin.audio.shoutcast", menu["Radio"])
        self.assertIn("plugin.audio.m3sr2019", menu["MP3 Streams Echoed"])
        self.assertNotIn("plugin.audio.mp3streams", str(report))
        for label, pid in layout.PROVIDERS:
            self.assertIn("with_watch_providers=" + pid, menu[label])
            self.assertIn("watch_region=DE", menu[label])
        self.assertEqual(report["hero"], "PENDING_XCMATE_069_ROUTE_AND_ARTWORK")
        self.assertFalse(report["apply_enabled"])

    def test_bingie_widgets_are_source_verified_only(self):
        widgets = layout.verify()["widgets"]
        self.assertTrue(any(title == "Im Kino" and "now_playing" in path for _menu,title,path,_ in widgets))
        self.assertTrue(any(title == "Diese Woche im Trend" and "trending_week" in path for _menu,title,path,_ in widgets))
        self.assertTrue(any(title == "Disney Plus" and "with_watch_providers=337" in path for _menu,title,path,_ in widgets))
        self.assertTrue(any("m3sr2019" in path for _menu,title,path,_ in widgets))

    def test_xcmate_first_three_widget_routes(self):
        rows = layout.verify()["widgets"]
        self.assertEqual(tuple(r[1] for r in rows[:3]),
                         ("XCMate Live-TV", "XCMate Filme", "XCMate Serien"))
        self.assertEqual(tuple(r[2] for r in rows[:3]),
                         ("plugin://plugin.video.xtreammate/?action=widget_live_start_group",
                          "plugin://plugin.video.xtreammate/?action=widget_recent_vod",
                          "plugin://plugin.video.xtreammate/?action=widget_recent_series"))
        self.assertEqual(layout.verify()["menu"][0]["label"], "Live-TV (XCMate)")

    def _fixture_handoff(self):
        inventory = {"code": "READY", "addons": {}}
        for row in planner.plan_for("standard"):
            if not row["builtin"]:
                inventory["addons"][row["addon_id"]] = {
                    "version": row["minimum"] or "999.0", "enabled": True,
                }
        marker = {
            "origin": "GS_MEDIA_NEW_INSTALL",
            "phase": "RESTART_PENDING",
            "user_confirmed": True,
            "stages": {x: True for x in handoff.REQUIRED_STAGES},
            "before_restart_boot": "first-boot",
            "wizard_launch_attempted": False,
        }
        return marker, inventory

    def test_handoff_waits_for_restart_and_all_packages(self):
        marker, inventory = self._fixture_handoff()
        self.assertEqual(handoff.assess(marker, inventory, "first-boot")["code"],
                         "WAIT_FOR_NEW_KODI_BOOT")
        ready = handoff.assess(marker, inventory, "second-boot")
        self.assertTrue(ready["launch_allowed"])
        self.assertEqual(ready["target"], "plugin://plugin.video.xtreammate/?action=setup_wizard")
        self.assertFalse(handoff.launch_contract()["autorun_implemented"])
        self.assertTrue(handoff.launch_contract()["write_one_shot_attempt_before_launch"])

    def test_handoff_blocks_missing_stage_and_missing_dependency(self):
        marker, inventory = self._fixture_handoff()
        marker["stages"]["bingie_widgets_applied"] = False
        self.assertEqual(handoff.assess(marker, inventory, "second-boot")["code"],
                         "MANDATORY_STAGE_MISSING")
        marker["stages"]["bingie_widgets_applied"] = True
        del inventory["addons"]["script.module.slyguy"]
        result = handoff.assess(marker, inventory, "second-boot")
        self.assertEqual(result["code"], "DEPENDENCY_NOT_READY")
        self.assertIn("script.module.slyguy", result["unready_addons"])

    def test_handoff_never_relaunches_on_existing_box(self):
        marker, inventory = self._fixture_handoff()
        self.assertEqual(handoff.assess(None, inventory, "second-boot")["code"],
                         "NO_NEW_INSTALL_HANDOFF")
        self.assertEqual(handoff.assess(marker, inventory, "second-boot", True)["code"],
                         "ALREADY_CONFIGURED")
        self.assertEqual(handoff.assess(marker, {"code": "UNKNOWN"}, "second-boot")["code"],
                         "INVENTORY_UNAVAILABLE")
        marker["wizard_launch_attempted"] = True
        self.assertEqual(handoff.assess(marker, inventory, "second-boot")["code"],
                         "ALREADY_ATTEMPTED")

    def test_tmdb_default_player_matches_archived_xvault_settings(self):
        self.assertEqual(tmdb_player.PLAYER_FILE, "xvault_stable.json")
        self.assertEqual(tmdb_player.TARGET_SETTINGS, (
            ("default_player_movies", "xvault_stable.json play_movie"),
            ("default_player_episodes", "xvault_stable.json play_episode"),
        ))
        self.assertIn("tmdb_xvault_default_player_configured", handoff.REQUIRED_STAGES)

    def test_tmdb_player_requires_installed_enabled_and_verification(self):
        inventory = {"code": "READY", "addons": {
            "plugin.video.themoviedb.helper": {"version": "5.4.16", "enabled": True},
            "plugin.video.xvault": {"version": "2026.10.20.1", "enabled": True},
        }}
        self.assertEqual(tmdb_player.proposal(inventory)["status"], "EXISTING_PROFILE_UNCHANGED")
        self.assertEqual(tmdb_player.proposal(inventory, fresh_install=True)["status"], "PLAYER_JSON_NOT_VERIFIED")
        result = tmdb_player.proposal(inventory, player_file_verified=True, fresh_install=True)
        self.assertTrue(result["can_apply"])
        self.assertFalse(result["apply_enabled"])
        inventory["addons"]["plugin.video.xvault"]["enabled"] = False
        self.assertFalse(tmdb_player.proposal(inventory, player_file_verified=True, fresh_install=True)["can_apply"])

    def test_tmdb_player_json_route_validation(self):
        example = {
            "name": "xVAULT", "plugin": "plugin.video.xvault",
            "play_movie": "plugin://plugin.video.xvault/?action=playTMDbHelper&title={title_url}&tmdb_id={tmdb}&imdb={imdb}",
            "play_episode": "plugin://plugin.video.xvault/?action=playTMDbHelper&season={season}&tmdb_id={tmdb}&imdb={imdb}",
        }
        self.assertTrue(tmdb_player.verify_source_json(example))
        example["plugin"] = "another.addon"
        self.assertFalse(tmdb_player.verify_source_json(example))

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
        sources = [ADDON / "default.py", LIB / "setup_inventory.py", LIB / "setup_gate.py", LIB / "setup_plan.py", LIB / "setup_layout.py", LIB / "setup_handoff.py", LIB / "setup_tmdb_player.py"]
        for path in sources:
            value = path.read_text("utf-8")
            for bad in ("InstallAddon(", "UninstallAddon(", "EnableAddon(",
                        "SetAddonEnabled", "shutil.rmtree(", "addon_data",
                        "xbmc.executebuiltin(", "open("):
                # The TMDB player proposal may name the documented target folder
                # without ever opening it or changing any user profile.
                if bad == "addon_data" and path.name == "setup_tmdb_player.py":
                    self.assertIn("special://profile/addon_data/", value)
                    continue
                self.assertNotIn(bad, value, (path.name, bad))

if __name__ == "__main__":
    unittest.main()

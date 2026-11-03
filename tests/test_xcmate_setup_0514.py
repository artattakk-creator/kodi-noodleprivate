"""Regression tests for Kodi 21 native version upgrades and safe resume.

No Android, add-ons or network required. A Kodi-hardware acceptance is separate.
"""
from pathlib import Path
from unittest.mock import patch
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "src/script.gsmedia.setup/resources/lib"
sys.path.insert(0, str(LIB))
import setup_auto50 as sut


def installed(addons):
    return {"code": "READY", "addons": {
        addon_id: {"version": version, "enabled": enabled}
        for addon_id, (version, enabled) in addons.items()
    }}


class NativeUpgradeAndResumeTests(unittest.TestCase):
    def test_all_bingie_source_bridges_have_pinned_versions(self):
        specs = {s["target"]: s for s in sut.upgrade_bridges()}
        self.assertGreaterEqual(len(specs), 15)
        self.assertEqual(specs["resource.images.skinicons.wide"]["minimum"], "1.0.5")
        self.assertEqual(specs["script.skin.helper.backgrounds"]["minimum"], "1.0.36")
        self.assertEqual(specs["resource.images.skinicons.wide"]["source"],
                         "repository.titan.bingie.mod")
        self.assertNotIn("script.skinshortcuts", specs)
        self.assertTrue(all(s["id"].startswith("script.gsmedia.upgrade.")
                            for s in specs.values()))

    def test_old_skin_icons_explicit_native_upgrade(self):
        box = installed({
            sut.TEST_CHANNEL: ("1.9.7", True),
            "repository.titan.bingie.mod": ("2.0.1", True),
            "resource.images.skinicons.wide": ("1.0.4", True)
        })
        row = [{"id":"resource.images.skinicons.wide", "minimum":"1.0.5",
                "repo":"repository.titan.bingie.mod", "notes":"",
                "mandatory":False, "manifest_known":True}]
        with patch.object(sut, "manifest", return_value=row):
            step = sut.next_step(sut.new_state(), box)
            self.assertEqual(step["code"], "INSTALL_UPGRADE")
            self.assertEqual(step["bridge"],
                             "script.gsmedia.upgrade.resource.images.skinicons.wide")
            self.assertEqual(step["actual"], "1.0.4")
            state = sut.after_request(sut.new_state(), step["id"])
            box["addons"]["resource.images.skinicons.wide"]["version"] = "1.0.5"
            self.assertEqual(sut.next_step(state, box)["code"], "CONFIRM")
            self.assertIn(step["id"], sut.after_confirm(state, box)["completed"])

    def test_retry_required_backgrounds_cleared_without_deletion(self):
        row = [{"id":"script.skin.helper.backgrounds", "minimum":"1.0.36",
                "repo":"repository.titan.bingie.mod", "notes":"",
                "mandatory":False, "manifest_known":True}]
        box = installed({sut.TEST_CHANNEL:("1.9.7",True),
                         "repository.titan.bingie.mod":("2.0.1",True)})
        with patch.object(sut, "manifest", return_value=row):
            state = sut.after_request(sut.new_state(), "script.skin.helper.backgrounds")
            state = sut.stop(state, "KODI_INSTALL_NOT_CONFIRMED")
            recovered = sut.reconcile_restart(state, box)
            self.assertEqual(recovered["pending"], "")
            self.assertNotIn("script.skin.helper.backgrounds", recovered["attempted"])
            self.assertEqual(sut.next_step(sut.resume(recovered), box)["code"],
                             "INSTALL_ADDON")

    def test_late_install_is_confirmed_without_second_install_request(self):
        row = [{"id":"script.skin.helper.backgrounds", "minimum":"1.0.36",
                "repo":"repository.titan.bingie.mod", "notes":"",
                "mandatory":False, "manifest_known":True}]
        box = installed({sut.TEST_CHANNEL:("1.9.7",True),
                         "repository.titan.bingie.mod":("2.0.1",True),
                         "script.skin.helper.backgrounds":("1.0.36",True)})
        with patch.object(sut, "manifest", return_value=row):
            s = sut.stop(sut.after_request(sut.new_state(),
                         "script.skin.helper.backgrounds"), "STOP")
            recovered = sut.reconcile_restart(s,box)
            self.assertEqual(recovered["completed"],
                             ["script.skin.helper.backgrounds"])
            self.assertEqual(sut.next_step(sut.resume(recovered), box)["code"],
                             "APPS_PRESENT")

    def test_disabled_at_compliant_version_is_enable_not_upgrade(self):
        row = [{"id":"resource.images.skinicons.wide", "minimum":"1.0.5",
                "repo":"repository.titan.bingie.mod", "notes":"",
                "mandatory":False, "manifest_known":True}]
        box = installed({sut.TEST_CHANNEL:("1.9.7",True),
                         "repository.titan.bingie.mod":("2.0.1",True),
                         "resource.images.skinicons.wide":("1.0.5",False)})
        with patch.object(sut, "manifest", return_value=row):
            self.assertEqual(sut.next_step(sut.new_state(),box)["code"],"ENABLE_ADDON")

    def test_untrusted_outdated_dependency_never_triggers_bridge(self):
        row = [{"id":"script.badsource", "minimum":"1.2.0",
                "repo":"repository.unknown", "notes":"",
                "mandatory":False, "manifest_known":True}]
        box = installed({sut.TEST_CHANNEL:("1.9.7",True),
                         "repository.unknown":("1.0.0",True),
                         "script.badsource":("1.1.0",True)})
        with patch.object(sut, "manifest", return_value=row):
            step = sut.next_step(sut.new_state(),box)
            self.assertEqual(step["code"],"SOURCE_BLOCKED")
            self.assertEqual(step["reason"],"NO_TRUSTED_UPGRADE_BRIDGE")

    def test_recovery_keeps_prior_completed_and_no_secrets(self):
        row = [{"id":"resource.images.skinicons.wide", "minimum":"1.0.5",
                "repo":"repository.titan.bingie.mod", "notes":"",
                "mandatory":False, "manifest_known":True},
               {"id":"script.skin.helper.backgrounds", "minimum":"1.0.36",
                "repo":"repository.titan.bingie.mod", "notes":"",
                "mandatory":False, "manifest_known":True}]
        box=installed({sut.TEST_CHANNEL:("1.9.7",True),
                       "repository.titan.bingie.mod":("2.0.1",True),
                       "resource.images.skinicons.wide":("1.0.5",True)})
        with patch.object(sut,"manifest",return_value=row):
            state=sut.after_request(sut.new_state(),"resource.images.skinicons.wide")
            state=sut.after_confirm(state,box)
            state=sut.after_request(state,"script.skin.helper.backgrounds")
            state=sut.stop(state,"KODI_INSTALL_NOT_CONFIRMED")
            recovered=sut.reconcile_restart(state,box)
            self.assertIn("resource.images.skinicons.wide",recovered["completed"])
            self.assertEqual(recovered["attempted"],
                             ["resource.images.skinicons.wide"])
            self.assertNotIn("password",str(recovered))
            self.assertEqual(sut.next_step(sut.resume(recovered),box)["id"],
                             "script.skin.helper.backgrounds")


if __name__=="__main__":
    unittest.main()

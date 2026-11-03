"""xcMate Setup 0.5.17: original BINGIE Repo+Helper one-step bootstrap.

Kodi 21 Omega must resolve these as ordinary original dependencies from the
xcMate pilot. Integration on Android requires an actual Kodi runtime.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/"src/script.gsmedia.setup/resources/lib"
sys.path.insert(0,str(LIB))
import setup_auto50 as controller


def inventory(entries):
    return {"code":"READY","addons":{
      k:{"version":v, "enabled":True} for k,v in entries.items()
    }}


class BingieOneStepBootstrapTests(unittest.TestCase):
    def test_bingie_repo_and_helper_present_in_same_approved_catalog(self):
        data={s["id"]:s for s in controller.rows()}
        self.assertEqual(len(data),48)
        self.assertEqual(data["script.bingie.helper"]["repo"],
                         controller.TEST_CHANNEL)
        self.assertEqual(data["script.bingie.helper"]["minimum"],"1.1.2")
        self.assertIn("repository.titan.bingie.mod", controller.REPO_ALLOWLIST)

    def test_new_box_requests_bingie_repo_without_manual_bootstrap(self):
        # Restricted to a minimal manifest, preserving actual setup controller.
        rows=[
          {"id":"script.module.simplejson","minimum":"3.17.0",
           "repo":"repository.xbmc.org","notes":"","manifest_known":True},
          {"id":"script.bingie.helper","minimum":"1.1.2",
           "repo":controller.TEST_CHANNEL,"notes":"","manifest_known":True},
        ]
        box=inventory({
            controller.TEST_CHANNEL:"1.9.10",
            "script.module.simplejson":"3.19.1+matrix.1"
        })
        with patch.object(controller,"manifest",return_value=rows):
            step=controller.next_step(controller.new_state(),box)
        self.assertEqual(step["code"],"INSTALL_REPOSITORY")
        self.assertEqual(step["id"],"repository.titan.bingie.mod")
        self.assertEqual(step["source"],"GS_MEDIA_APPROVED_TEST_CATALOG")

    def test_native_parent_installs_both_and_resumes_past_them(self):
        rows=[
          {"id":"script.module.simplejson","minimum":"3.17.0",
           "repo":"repository.xbmc.org","notes":"","manifest_known":True},
          {"id":"script.bingie.helper","minimum":"1.1.2",
           "repo":controller.TEST_CHANNEL,"notes":"","manifest_known":True},
        ]
        box=inventory({
           controller.TEST_CHANNEL:"1.9.10",
           "script.module.simplejson":"3.19.1+matrix.1"
        })
        with patch.object(controller,"manifest",return_value=rows):
            step=controller.next_step(controller.new_state(),box)
            s=controller.after_request(controller.new_state(),step["id"])
            box["addons"]["repository.titan.bingie.mod"]={
                "version":"2.0.1","enabled":True}
            box["addons"]["script.bingie.helper"]={
                "version":"1.1.2","enabled":True}
            self.assertEqual(controller.next_step(s,box)["code"],"CONFIRM")
            s=controller.after_confirm(s,box)
            self.assertEqual(controller.next_step(s,box)["code"],"APPS_PRESENT")

    def test_failed_bootstrap_is_recoverable_from_existing_journal(self):
        rows=[
          {"id":"script.bingie.helper","minimum":"1.1.2",
           "repo":controller.TEST_CHANNEL,"notes":"","manifest_known":True},
        ]
        box=inventory({controller.TEST_CHANNEL:"1.9.10"})
        with patch.object(controller,"manifest",return_value=rows):
            s=controller.new_state()
            s=controller.after_request(s,"repository.titan.bingie.mod")
            s=controller.stop(s,"KODI_INSTALL_NOT_CONFIRMED")
            fixed=controller.reconcile_restart(s,box)
            self.assertFalse(fixed["pending"])
            self.assertEqual(fixed["attempted"],[])
            self.assertEqual(controller.next_step(controller.resume(fixed),box)["code"],
                             "INSTALL_REPOSITORY")

    def test_installer_uses_native_parent_before_installaddon(self):
        ui=(LIB/"setup_auto_ui50.py").read_text(encoding="utf-8")
        self.assertIn('install_id = "script.gsmedia.bingie.bootstrap"',ui)
        self.assertIn('probe_kodi_catalog(xbmc.executeJSONRPC, install_id)',ui)
        self.assertIn('KODI_CATALOG_NOT_READY:',ui)
        self.assertLess(ui.index('install_id = "script.gsmedia.bingie.bootstrap"'),
                        ui.index('state = _persist(profile, after_request(state, ident))'))
        self.assertNotIn("InstallFromZip(",ui)
        self.assertNotIn("os.system(",ui)


if __name__=="__main__":
    unittest.main()

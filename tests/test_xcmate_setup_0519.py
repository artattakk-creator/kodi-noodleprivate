"""Real Kodi Omega FindDependencyByParentRepo failure at 39/48.

Root cause in uploaded Android 21.3 kodi.log at 20:04:59:
  CAddonInstallJob[script.gsmedia.slyguy.bootstrap]:
    failed to find dependency slyguy.dependencies
Kodi Omega resolves third-party dependency via the PARENT addon origin repo.
Never install our xcMate-origin bootstrap as the SlyGuy dependency parent.
"""
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch
import sys

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/"src/script.gsmedia.setup/resources/lib"
sys.path.insert(0,str(LIB))
import setup_auto50 as setup
from setup_catalog_0516 import probe
import json


class SlyGuySameOriginTests(TestCase):
    def test_previously_reproduced_39_of_48_is_recovered(self):
        row={"id":"slyguy.dependencies","repo":"repository.slyguy",
             "minimum":"0.0.30","mandatory":False,"manifest_known":True,"notes":""}
        inv={"code":"READY","addons":{
             setup.TEST_CHANNEL:{"version":"1.9.12","enabled":True},
             "repository.slyguy":{"version":"0.0.9","enabled":True}}}
        with patch.object(setup,"manifest",return_value=[row]):
            state=setup.after_request(setup.new_state(),row["id"])
            state=setup.stop(state,"KODI_INSTALL_NOT_CONFIRMED:slyguy.dependencies")
            resumed=setup.resume(setup.reconcile_restart(state,inv))
            first=setup.next_step(resumed,inv)
            self.assertEqual(first["code"],"INSTALL_ADDON")
            self.assertEqual(first["id"],"slyguy.dependencies")
            self.assertEqual(first["source"],"repository.slyguy")
            inv["addons"]["slyguy.dependencies"]={"version":"0.0.30","enabled":True}
            inv["addons"]["script.module.slyguy"]={"version":"0.87.6","enabled":True}
            state=setup.after_request(resumed,row["id"])
            self.assertEqual(setup.next_step(state,inv)["code"],"CONFIRM")
            state=setup.after_confirm(state,inv)
            self.assertEqual(setup.next_step(state,inv)["code"],"APPS_PRESENT")

    def test_original_parent_source_and_dependencies_both_preflighted(self):
        ui=(LIB/"setup_auto_ui50.py").read_text(encoding="utf-8")
        self.assertIn('native_slyguy_origin_parent = (',ui)
        self.assertIn('and step.get("source") == "repository.slyguy"',ui)
        self.assertIn('install_id = "script.module.slyguy"',ui)
        self.assertIn('probe_kodi_catalog(xbmc.executeJSONRPC, install_id)',ui)
        self.assertIn('xbmc.executeJSONRPC, "slyguy.dependencies"',ui)
        self.assertIn('SLYGUY_ORIGINAL_DEP_NOT_VISIBLE',ui)
        self.assertIn('SLYGUY_ORIGINAL_SAME_REPO_PARENT',ui)
        self.assertIn('SLYGUY_PARENT_PRESENT_DEPENDENCY_MISSING:',ui)
        self.assertIn('KODI_CATALOG_NOT_READY:" + missing_catalog_id',ui)
        self.assertNotIn('install_id = "script.gsmedia.slyguy.bootstrap"',ui)
        # Repo includes only our unneeded inert old bridge for catalog stability,
        # never any SlyGuy upstream ZIP without licensed redistributable rights.
        pilot=(ROOT/"tools/build_gsmedia_pilot050.py").read_text(encoding="utf-8")
        self.assertNotIn('slyguy.dependencies-0.0.30.zip',pilot)

    def test_original_installer_preflight_checks_matching_versions(self):
        ui=(LIB/"setup_auto_ui50.py").read_text(encoding="utf-8")
        self.assertIn('_version(visible.get("version", "")) < (0, 87, 6)',ui)
        self.assertIn('_version(dependency.get("version", "")) < (0, 0, 30)',ui)
        self.assertIn('reason = "SLYGUY_ORIGINAL_CATALOG_VERSION_TOO_OLD"',ui)
        self.assertLess(ui.index('SLYGUY_ORIGINAL_DEP_VISIBLE'),
                        ui.index('state = _persist(profile, after_request(state, ident))'))

    def test_catalog_preflight_wont_falsely_claim_visible(self):
        def fake_rpc(request):
            params=json.loads(request)["params"]
            assert params["installed"] is False
            return json.dumps({"result":{"limits":{"start":0,"end":1,"total":1},
              "addons":[{"addonid":"script.module.slyguy","version":"0.87.6"}]}})
        self.assertEqual(probe(fake_rpc,"script.module.slyguy")["code"],"AVAILABLE")
        self.assertEqual(probe(fake_rpc,"slyguy.dependencies")["code"],"NOT_LISTED")

    def test_controller_keeps_all_48_steps_and_original_source(self):
        rows=setup.rows()
        self.assertEqual(len(rows),48)
        by_id={r["id"]:r for r in rows}
        self.assertEqual(by_id["slyguy.dependencies"]["repo"],"repository.slyguy")
        self.assertEqual(by_id["script.module.slyguy"]["repo"],"repository.slyguy")
        self.assertEqual(by_id["slyguy.trailers"]["repo"],"repository.slyguy")


if __name__=="__main__":
    main()

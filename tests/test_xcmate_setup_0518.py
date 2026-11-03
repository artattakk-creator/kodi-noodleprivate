"""Kodi 21.3 39/48 SlyGuy native dependency bootstrap regression.

The uploaded Kodi log verifies 'slyguy.dependencies' 0.0.30 available,
InstallAddon requested at 19:32:19, no confirmation after 240 seconds.
Original archive has no declared license, so it is NOT redistributed.
"""
import json
import sys
import tempfile
from pathlib import Path
from unittest import TestCase,main
from unittest.mock import patch
import zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/"src/script.gsmedia.setup/resources/lib"
TOOLS=ROOT/"tools"
sys.path.insert(0,str(LIB))
sys.path.insert(0,str(TOOLS))
import setup_auto50 as setup
import setup_origin_guard52 as guard
from build_gsmedia_pilot050 import (
    _create_slyguy_native_bootstrap,
    SLYGUY_NATIVE_BRIDGE_ID,SLYGUY_NATIVE_BRIDGE_VERSION)


def inv(values):
    return {"code":"READY","addons":{
        k:{"version":v,"enabled":True} for k,v in values.items()
    }}


class OriginalSlyGuyBootstrap(TestCase):
    def test_48_unchanged_steps_and_original_repository_sources(self):
        rows=setup.rows()
        self.assertEqual(len(rows),48)
        by_id={x["id"]:x for x in rows}
        for dep in ("slyguy.dependencies","script.module.slyguy","slyguy.trailers"):
            self.assertEqual(by_id[dep]["repo"],"repository.slyguy")
        self.assertEqual(by_id["slyguy.dependencies"]["minimum"],"0.0.30")

    def test_existing_checkpoint_39_of_48_resumes_native_dependency(self):
        row={"id":"slyguy.dependencies","repo":"repository.slyguy",
             "minimum":"0.0.30","mandatory":False,
             "notes":"","manifest_known":True}
        box=inv({setup.TEST_CHANNEL:"1.9.11","repository.slyguy":"0.0.9"})
        with patch.object(setup,"manifest",return_value=[row]):
            state=setup.after_request(setup.new_state(),"slyguy.dependencies")
            state=setup.stop(state,"KODI_INSTALL_NOT_CONFIRMED:slyguy.dependencies")
            recovered=setup.reconcile_restart(state,box)
            self.assertEqual(recovered["attempted"],[])
            step=setup.next_step(setup.resume(recovered),box)
            self.assertEqual(step["code"],"INSTALL_ADDON")
            self.assertEqual(step["source"],"repository.slyguy")
            self.assertEqual(step["id"],"slyguy.dependencies")

    def test_native_parent_reuses_originals_without_republishing_any(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon=_create_slyguy_native_bootstrap(tmp)
            self.assertEqual(addon.get("id"),SLYGUY_NATIVE_BRIDGE_ID)
            bridge=Path(tmp)/SLYGUY_NATIVE_BRIDGE_ID/(
                   SLYGUY_NATIVE_BRIDGE_ID+"-"+SLYGUY_NATIVE_BRIDGE_VERSION+".zip")
            with zipfile.ZipFile(bridge) as z:
                members=z.namelist()
                self.assertEqual(len(members),2)
                root=ET.fromstring(z.read(SLYGUY_NATIVE_BRIDGE_ID+"/addon.xml"))
                deps={(i.get("addon"),i.get("version"))
                      for i in root.findall("./requires/import")}
                self.assertEqual(deps,{
                    ("xbmc.python","3.0.0"),
                    ("repository.slyguy","0.0.9"),
                    ("slyguy.dependencies","0.0.30"),
                    ("script.module.slyguy","0.87.6"),
                    ("slyguy.trailers","0.2.2")})
                code=z.read(SLYGUY_NATIVE_BRIDGE_ID+"/default.py").decode()
                self.assertNotIn("urllib",code)
                self.assertNotIn("os.system",code)
                self.assertNotIn("subprocess",code)

    def test_script_uses_native_bridge_and_not_a_direct_unlicensed_mirror(self):
        ui=(LIB/"setup_auto_ui50.py").read_text(encoding="utf-8")
        self.assertIn('install_id = "script.module.slyguy"',ui)
        self.assertIn('SLYGUY_ORIGINAL_SAME_REPO_PARENT',ui)
        self.assertNotIn('install_id = "script.gsmedia.slyguy.bootstrap"',ui)
        self.assertIn('addon_id="slyguy.dependencies"',ui)
        self.assertIn('probe_kodi_catalog(xbmc.executeJSONRPC, install_id)',ui)
        pilot=(TOOLS/"build_gsmedia_pilot050.py").read_text(encoding="utf-8")
        self.assertNotIn("slyguy.dependencies-0.0.30.zip",pilot)
        self.assertIn('slyguy_bridge_xml = _create_slyguy_native_bootstrap(destination)',pilot)

    def test_consent_scope_slyguy_is_crash_recoverable(self):
        class Kodi:
            def __init__(self):
                self.mode={guard.MODE:0,guard.UPDATES:0}
            def __call__(self,payload):
                req=json.loads(payload)
                name=req["params"]["setting"]
                if req["method"]=="Settings.GetSettingValue":
                    return json.dumps({"result":{"value":self.mode[name]}})
                if req["method"]=="Settings.SetSettingValue":
                    self.mode[name]=req["params"]["value"]
                    return json.dumps({"result":True})
                raise AssertionError()
        with tempfile.TemporaryDirectory() as tmp:
            profile=str(Path(tmp)/"script.gsmedia.setup")
            kodi=Kodi()
            with guard.TemporaryOfficialAddonSource(
                     profile,kodi,addon_id="slyguy.dependencies"):
                self.assertEqual(kodi.mode,{guard.MODE:1,guard.UPDATES:2})
                self.assertEqual(guard._read_marker(profile)["addon"],
                                 "slyguy.dependencies")
            self.assertEqual(kodi.mode,{guard.MODE:0,guard.UPDATES:0})
            self.assertIsNone(guard._read_marker(profile))


if __name__=="__main__":
    main()

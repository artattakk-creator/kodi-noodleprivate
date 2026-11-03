"""Pure Kotlin-independent Kodi 21 package catalog readiness regression tests.

No Kodi runtime, network, filesystem modification, or user profile required.
"""
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/"src/script.gsmedia.setup/resources/lib"
sys.path.insert(0,str(LIB))
from setup_catalog_0516 import probe


class KodiCatalogReadiness(unittest.TestCase):
    def test_installed_false_queries_kodi_index_not_installed_set(self):
        requests=[]
        def rpc(raw):
            req=json.loads(raw)
            requests.append(req)
            return json.dumps({"jsonrpc":"2.0","id":216,
                "result":{"limits":{"start":0,"end":1,"total":1},
                          "addons":[{"addonid":"repository.titan.bingie.mod",
                                     "version":"2.0.1"}]}})
        got=probe(rpc,"repository.titan.bingie.mod")
        self.assertEqual(got["code"],"AVAILABLE")
        self.assertEqual(got["version"],"2.0.1")
        self.assertEqual(requests[0]["method"],"Addons.GetAddons")
        self.assertIs(requests[0]["params"]["installed"],False)
        self.assertEqual(requests[0]["params"]["enabled"],"all")

    def test_bingie_helper_visible_after_catalog_refresh(self):
        def rpc(_raw):
            return json.dumps({"result":{"limits":{"start":0,"end":1,"total":1},
                 "addons":[{"addonid":"script.bingie.helper","version":"1.1.2"}]}})
        self.assertEqual(probe(rpc,"script.bingie.helper")["code"],"AVAILABLE")

    def test_missing_package_is_not_listed_instead_of_faked_success(self):
        def rpc(_raw):
            return json.dumps({"result":{"limits":{"start":0,"end":1,"total":1},
                 "addons":[{"addonid":"script.module.simplejson","version":"3.19.1"}]}})
        self.assertEqual(probe(rpc,"script.bingie.helper")["code"],"NOT_LISTED")

    def test_paginates_without_false_negative_on_later_page(self):
        names=[{"addonid":"plugin.check."+str(i), "version":"1.0.0"}
               for i in range(240)]
        names[235]={"addonid":"script.bingie.helper","version":"1.1.2"}
        requests=[]
        def rpc(raw):
            req=json.loads(raw); requests.append(req)
            start=req["params"]["limits"]["start"]
            end=req["params"]["limits"]["end"]
            return json.dumps({"result":{"limits":{
              "total":len(names), "start":start, "end":min(end,len(names))},
              "addons":names[start:end]}})
        self.assertEqual(probe(rpc,"script.bingie.helper")["code"],"AVAILABLE")
        self.assertEqual(len(requests),2)
        self.assertEqual(requests[1]["params"]["limits"]["start"],200)

    def test_distinguishes_rpc_error_from_absent_package(self):
        self.assertEqual(probe(lambda raw:'{"error":{"code":-32601}}',
                      "script.bingie.helper")["code"],"RPC_ERROR")
        self.assertEqual(probe(lambda raw:'bad json',
                      "script.bingie.helper")["code"],"RPC_ERROR")
        self.assertEqual(probe(lambda raw:'{"result":{"addons":[]}}',
                      "script.bingie.helper")["code"],"RPC_ERROR")

    def test_inventory_changes_midscan_is_not_trusted(self):
        def rpc(raw):
            r=json.loads(raw)
            start=r["params"]["limits"]["start"]
            return json.dumps({"result":{
                "limits":{"start":start,"end":start+200,
                          "total":250 if start==0 else 251},
                "addons":[{"addonid":"other.%d"%i,"version":"1"} for i in range(200)]
                 if start==0 else [{"addonid":"other.200","version":"1"}]}})
        self.assertEqual(probe(rpc,"script.bingie.helper")["code"],"RPC_ERROR")

    def test_addon_ids_validated_and_ui_never_records_plain_urls(self):
        with self.assertRaises(ValueError):
            probe(lambda raw:"{}", "script.bingie.helper);Quit()")
        ui=(LIB/"setup_auto_ui50.py").read_text(encoding="utf-8")
        self.assertIn('probe_kodi_catalog(xbmc.executeJSONRPC, install_id)',ui)
        self.assertIn('"UpdateAddonRepos"',ui)
        self.assertLess(ui.index("probe_kodi_catalog(xbmc.executeJSONRPC, install_id)"),
                        ui.index("state = _persist(profile, after_request(state, ident))"))
        self.assertIn("KODI_CATALOG_NOT_READY:",ui)
        self.assertIn("CATALOG_STOP_NO_INSTALL_REQUEST",ui)
        self.assertIn("KODI_INSTALL_CONFIRMED",ui)
        self.assertIn("KODI_INSTALL_REQUESTED",ui)
        self.assertNotIn("password=",ui)
        self.assertNotIn("token=",ui)


if __name__=="__main__":
    unittest.main()

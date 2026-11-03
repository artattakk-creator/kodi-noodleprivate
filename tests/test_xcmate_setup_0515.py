"""Kodi 21 Omega 0.5.15 BINGIE backgrounds dependency + stale journal checks."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/"src/script.gsmedia.setup/resources/lib"
sys.path.insert(0,str(LIB))
import setup_auto50 as setup


def invent(entries):
    return {"code":"READY","addons": {
        ident:{"version":version,"enabled":enabled}
        for ident,(version,enabled) in entries.items()}}


class BackgroundsRecoveryTests(unittest.TestCase):
    def test_full_parent_dependency_order_and_verified_sources(self):
        rows=setup.rows()
        ids=[x["id"] for x in rows]
        self.assertEqual(len(ids),48)
        self.assertEqual(len(set(ids)),48)
        for dep in ("script.module.simplecache","script.module.metadatautils",
                    "script.module.thetvdb","script.module.musicbrainz",
                    "script.module.arrow"):
            self.assertIn(dep,ids)
            self.assertLess(ids.index(dep),ids.index("script.skin.helper.backgrounds"))
        metadata={x["id"]:x for x in rows}
        self.assertEqual(metadata["script.module.simplecache"]["minimum"],"2.0.2")
        self.assertEqual(metadata["script.module.metadatautils"]["minimum"],"1.30.0")
        self.assertEqual(metadata["script.module.thetvdb"]["minimum"],"1.0.34")
        self.assertEqual(metadata["script.module.musicbrainz"]["minimum"],"0.7.0")
        self.assertEqual(metadata["script.module.arrow"]["repo"],"repository.xbmc.org")
        self.assertEqual(metadata["script.module.arrow"]["minimum"],"1.1.0")
        for dep in ("script.module.simplecache","script.module.metadatautils",
                    "script.module.thetvdb","script.module.musicbrainz"):
            self.assertEqual(metadata[dep]["repo"],"repository.titan.bingie.mod")

    def test_resume_removes_stale_completed_backgrounds_and_prior_attempt(self):
        row={"id":"script.skin.helper.backgrounds","minimum":"1.0.36",
             "repo":"repository.titan.bingie.mod","notes":"",
             "mandatory":False,"manifest_known":True}
        box=invent({setup.TEST_CHANNEL:("1.9.8",True),
                    "repository.titan.bingie.mod":("2.0.1",True)})
        with patch.object(setup,"manifest",return_value=[row]):
            s=setup.after_request(setup.new_state(),row["id"])
            box["addons"][row["id"]]={"version":"1.0.36","enabled":True}
            s=setup.after_confirm(s,box)
            box["addons"][row["id"]]={"version":"1.0.36","enabled":False}
            s=setup.stop(s,"RETRY_REQUIRED:"+row["id"])
            recovered=setup.reconcile_restart(s,box)
            self.assertEqual(recovered["attempted"],[])
            self.assertEqual(recovered["completed"],[])
            self.assertEqual(setup.next_step(setup.resume(recovered),box)["code"],
                             "ENABLE_ADDON")

    def test_resume_accepts_late_install_and_keeps_confirmed(self):
        row={"id":"script.skin.helper.backgrounds","minimum":"1.0.36",
             "repo":"repository.titan.bingie.mod","notes":"",
             "mandatory":False,"manifest_known":True}
        box=invent({setup.TEST_CHANNEL:("1.9.8",True),
                    "repository.titan.bingie.mod":("2.0.1",True),
                    row["id"]:("1.0.36",True)})
        with patch.object(setup,"manifest",return_value=[row]):
            s=setup.stop(setup.after_request(setup.new_state(),row["id"]),
                         "KODI_INSTALL_NOT_CONFIRMED")
            restored=setup.reconcile_restart(s,box)
            self.assertEqual(restored["pending"],"")
            self.assertEqual(restored["attempted"],[row["id"]])
            self.assertEqual(restored["completed"],[row["id"]])
            self.assertEqual(setup.next_step(setup.resume(restored),box)["code"],
                             "APPS_PRESENT")

    def test_stale_repo_is_retained_only_if_still_installed(self):
        row={"id":"script.skin.helper.backgrounds","minimum":"1.0.36",
             "repo":"repository.titan.bingie.mod","notes":"",
             "mandatory":False,"manifest_known":True}
        box=invent({setup.TEST_CHANNEL:("1.9.8",True)})
        with patch.object(setup,"manifest",return_value=[row]):
            s=setup.new_state()
            s["attempted"]=["repository.titan.bingie.mod"]
            s["completed"]=["repository.titan.bingie.mod"]
            s=setup.stop(s,"RETRY_REQUIRED:repository.titan.bingie.mod")
            fixed=setup.reconcile_restart(s,box)
            self.assertEqual(fixed["attempted"],[])
            self.assertEqual(fixed["completed"],[])
            self.assertEqual(setup.next_step(setup.resume(fixed),box)["code"],
                             "INSTALL_REPOSITORY")

    def test_corrupt_or_unknown_kodi_inventory_is_not_reconciled(self):
        row={"id":"script.skin.helper.backgrounds","minimum":"1.0.36",
             "repo":"repository.titan.bingie.mod","notes":"",
             "mandatory":False,"manifest_known":True}
        with patch.object(setup,"manifest",return_value=[row]):
            s=setup.stop(setup.new_state(),"UNKNOWN")
            with self.assertRaises(ValueError):
                setup.reconcile_restart(s,{"code":"UNKNOWN","addons":{}})


if __name__=="__main__":
    unittest.main()

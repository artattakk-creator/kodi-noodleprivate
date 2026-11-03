"""Kodi 21.3 SlyGuy 39/48 regression: catalog visible but install not confirmed.

Source of diagnosis: 03.11.2026 kodi.log 19:32:19-19:36:27, actual
slyguy.dependencies 0.0.30 never installed despite catalog visibility.
"""
import sys
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/"src/script.gsmedia.setup/resources/lib"
sys.path.insert(0,str(LIB))
import setup_auto50 as setup


def inv(values):
    return {"code":"READY","addons":{
        ident:{"version":version,"enabled":True}
        for ident,version in values.items()}}


class SlyGuyOriginalMirrorsTests(TestCase):
    def test_full_48_step_plan_remains_unchanged_and_native_originals_are_pinned(self):
        rows=setup.rows()
        self.assertEqual(len(rows),48)
        by_id={x["id"]:x for x in rows}
        self.assertEqual(len(rows),len(by_id))
        for ident,version in (
            ("slyguy.dependencies","0.0.30"),
            ("script.module.slyguy","0.87.6"),
            ("slyguy.trailers","0.2.2")
        ):
            self.assertEqual(by_id[ident]["repo"],setup.TEST_CHANNEL)
            self.assertEqual(by_id[ident]["minimum"],version)
        ordered=[x["id"] for x in rows]
        self.assertLess(ordered.index("slyguy.dependencies"),
                        ordered.index("script.module.slyguy"))
        self.assertLess(ordered.index("script.module.slyguy"),
                        ordered.index("slyguy.trailers"))

    def test_39_of_48_resume_uses_approved_first_party_source(self):
        minimal=[
          {"id":"slyguy.dependencies","repo":setup.TEST_CHANNEL,
           "minimum":"0.0.30","notes":"","manifest_known":True}
        ]
        box=inv({setup.TEST_CHANNEL:"1.9.11",
                 "repository.slyguy":"0.0.9"})
        with patch.object(setup,"manifest",return_value=minimal):
            state=setup.new_state()
            row=setup.next_step(state,box)
            self.assertEqual(row["code"],"INSTALL_ADDON")
            self.assertEqual(row["id"],"slyguy.dependencies")
            self.assertEqual(row["source"],setup.TEST_CHANNEL)
            state=setup.after_request(state,"slyguy.dependencies")
            state=setup.stop(state,"KODI_INSTALL_NOT_CONFIRMED:slyguy.dependencies")
            recovered=setup.reconcile_restart(state,box)
            self.assertEqual(recovered["attempted"],[])
            self.assertEqual(recovered["completed"],[])
            self.assertEqual(setup.next_step(setup.resume(recovered),box)["id"],
                             "slyguy.dependencies")

    def test_installed_slyguy_past_checkpoint_is_not_reinstalled(self):
        minimal=[
          {"id":"slyguy.dependencies","repo":setup.TEST_CHANNEL,
           "minimum":"0.0.30","notes":"","manifest_known":True},
          {"id":"script.module.slyguy","repo":setup.TEST_CHANNEL,
           "minimum":"0.87.6","notes":"","manifest_known":True},
        ]
        box=inv({setup.TEST_CHANNEL:"1.9.11",
                "slyguy.dependencies":"0.0.30",
                "script.module.slyguy":"0.87.6"})
        with patch.object(setup,"manifest",return_value=minimal):
            self.assertEqual(setup.next_step(setup.new_state(),box)["code"],
                             "APPS_PRESENT")

    def test_original_packages_pinned_with_unchanged_git_blobs(self):
        sys.path.insert(0,str(ROOT/"tools"))
        from build_gsmedia_pilot050 import SLYGUY_ORIGINAL_MODULES,SLYGUY_REPOSITORY_REV
        self.assertEqual(
          SLYGUY_REPOSITORY_REV,
          "42ea97aca5987db6ce3e2cdfa1a129bc8b0b0281")
        self.assertEqual(SLYGUY_ORIGINAL_MODULES,(
            ("slyguy.dependencies","0.0.30",
             "e17c3724d44ea019ea8c8e74e46a8a83d9185a6a",2558733),
            ("script.module.slyguy","0.87.6",
             "5efcd7e536af5eef1b960b2e8b6042a10a1eae0f",248134),
            ("slyguy.trailers","0.2.2",
             "d142fbf9aa771a875ea8fde966cf9fe89ccddc46",626463),
        ))


if __name__ == "__main__":
    main()

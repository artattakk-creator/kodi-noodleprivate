"""GS Media 1.8.2 priority addon audit – must never fake release readiness."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools"/"gsmedia_core_release_gate.py"
spec=importlib.util.spec_from_file_location("gsmedia_core_gate", SCRIPT)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class CoreInstallPlanTests(unittest.TestCase):
    def setUp(self):
        self.data=gate.read_matrix()

    def test_all_priority_addons_are_covered(self):
        self.assertEqual(
            {r["id"] for r in self.data["core"]},
            {"plugin.video.xtreammate", "plugin.video.xvault",
             "plugin.audio.m3sr2019", "plugin.audio.shoutcast"})

    def test_xvault_bootstrap_modules_have_provenance(self):
        x=next(r for r in self.data["core"] if r["id"]=="plugin.video.xvault")
        self.assertIn("script.module.resolveurl",x["required"])
        for component in ("script.module.requests", "script.module.six",
                          "script.module.pyaes", "script.module.infotagger"):
            self.assertIn(component,x["required"])
        self.assertIn("inputstream.ffmpegdirect",x["optional"])
        self.assertTrue(x["official_repo"].startswith("https://"))

    def test_shoutcast_has_real_kodi_dependencies(self):
        x=next(r for r in self.data["core"] if r["id"]=="plugin.audio.shoutcast")
        self.assertEqual(set(x["required"]),
                         {"xbmc.python","script.module.xbmcswift2",
                          "script.module.xmltodict"})
        self.assertIn("mirrors.kodi.tv/addons/omega",x["artifact"])

    def test_mp3_does_not_declare_missing_source_published(self):
        x=next(r for r in self.data["core"] if r["id"]=="plugin.audio.m3sr2019")
        self.assertEqual(x["status"],"blocked_upstream_404")
        self.assertNotIn(x["id"],gate.check_publication_eligibility(self.data))

    def test_incomplete_core_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Core release NOT READY"):
            gate.assert_ready_for_core_release(self.data)

    def test_current_kodi_index_has_only_approved_previous_addons(self):
        self.assertEqual(gate.current_published_ids(),frozenset({
            "repository.gsmedia", "plugin.video.noodleprivate",
            "plugin.video.xtreammate"}))

    def test_no_sensitive_backup_data_or_tokens_in_matrix(self):
        raw=json.dumps(self.data).lower()
        for marker in ("password=", "bearer eyj", "xtream_username",
                       "xtream_password", "tmdb_token=", "special://masterprofile/"):
            self.assertNotIn(marker,raw)

    def test_no_unreviewed_addon_auto_promoted(self):
        for row in self.data["core"]:
            if row["status"] not in gate.PUBLISHABLE:
                self.assertFalse(row.get("approved_for_publication",False))


if __name__=="__main__":
    unittest.main()

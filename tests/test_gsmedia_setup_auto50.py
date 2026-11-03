"""GS Media Setup .50 offline protection tests (no Kodi installed)."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "src" / "script.gsmedia.setup" / "resources" / "lib"
sys.path.insert(0, str(LIB))
import setup_auto50 as setup


def inventory(identifiers):
    return {"code": "READY",
            "addons": {key: {"version": version, "enabled": True}
                       for key, version in identifiers.items()}}


class AutoSetupTests(unittest.TestCase):
    def setUp(self):
        self.sample = [
            {"id": "script.bingie.helper", "minimum": "1.1.2",
             "repo": "repository.titan.bingie.mod", "notes": "",
             "mandatory": False, "manifest_known": True},
            {"id": "skin.titan.bingie.mod", "minimum": "2.2.3",
             "repo": "repository.titan.bingie.mod", "notes": "",
             "mandatory": True, "manifest_known": True},
            {"id": "plugin.video.xtreammate", "minimum": "0.1.29.70",
             "repo": "repository.gsmedia", "notes": "",
             "mandatory": True, "manifest_known": True},
        ]

    def test_order_repo_helper_skin(self):
        with patch.object(setup, "manifest", return_value=self.sample):
            blank = inventory({setup.TEST_CHANNEL: "1.8.2"})
            first = setup.next_step(setup.new_state(), blank)
            self.assertEqual(first["code"], "INSTALL_REPOSITORY")
            self.assertEqual(first["id"], "repository.titan.bingie.mod")
            supplied = dict(blank["addons"])
            supplied["repository.titan.bingie.mod"] = {"version": "2.0.1", "enabled": True}
            second = setup.next_step(setup.new_state(), {"code": "READY", "addons": supplied})
            self.assertEqual((second["code"], second["id"]),
                             ("INSTALL_ADDON", "script.bingie.helper"))
            supplied["script.bingie.helper"] = {"version": "1.1.2", "enabled": True}
            third = setup.next_step(setup.new_state(), {"code": "READY", "addons": supplied})
            self.assertEqual((third["code"], third["id"]),
                             ("INSTALL_ADDON", "skin.titan.bingie.mod"))

    def test_current_box_repo_and_helper_are_skipped(self):
        with patch.object(setup, "manifest", return_value=self.sample):
            inv = inventory({setup.TEST_CHANNEL: "1.8.2",
                             "repository.titan.bingie.mod": "2.0.1",
                             "script.bingie.helper": "1.1.2"})
            next_ = setup.next_step(setup.new_state(), inv)
            self.assertEqual(next_["id"], "skin.titan.bingie.mod")

    def test_pilot_repo_handles_xtreammate(self):
        with patch.object(setup, "manifest", return_value=self.sample):
            r = setup.rows()
            self.assertEqual(r[-1]["repo"], setup.TEST_CHANNEL)

    def test_requested_is_not_installed(self):
        with patch.object(setup, "manifest", return_value=self.sample):
            before = setup.new_state()
            queued = setup.after_request(before, "repository.titan.bingie.mod")
            self.assertEqual(setup.next_step(queued, inventory({
                setup.TEST_CHANNEL: "1.8.2"}))["code"], "WAITING")
            with self.assertRaises(ValueError):
                setup.after_confirm(queued, inventory({setup.TEST_CHANNEL: "1.8.2"}))
            available = inventory({setup.TEST_CHANNEL: "1.8.2",
                                   "repository.titan.bingie.mod": "2.0.1"})
            installed = setup.after_confirm(queued, available)
            self.assertEqual(installed["pending"], "")
            self.assertIn("repository.titan.bingie.mod", installed["completed"])

    def test_bingie_shortcuts_prefer_approved_210_pilot(self):
        shortcut = {"id": "script.skinshortcuts", "minimum": "2.1.0",
                    "repo": "repository.xbmc.org", "notes": "",
                    "mandatory": False, "manifest_known": True}
        with patch.object(setup, "manifest", return_value=[shortcut]):
            entries = setup.rows()
            self.assertEqual(entries[0]["repo"], setup.TEST_CHANNEL)
            result = setup.next_step(setup.new_state(), inventory({
                setup.TEST_CHANNEL: "1.8.4", "script.skinshortcuts": "2.0.3"
            }))
            self.assertEqual(result["code"], "INSTALL_UPGRADE")
            self.assertEqual(result["minimum"], "2.1.0")
            self.assertEqual(result["actual"], "2.0.3")
            queued = setup.after_request(setup.new_state(), "script.skinshortcuts")
            self.assertEqual(setup.next_step(queued, inventory({
                setup.TEST_CHANNEL: "1.8.4", "script.skinshortcuts": "2.0.3"
            }))["code"], "WAITING")
            newer = inventory({setup.TEST_CHANNEL: "1.8.4",
                               "script.skinshortcuts": "2.1.0"})
            self.assertEqual(setup.next_step(queued, newer)["code"], "CONFIRM")
            verified = setup.after_confirm(queued, newer)
            self.assertIn("script.skinshortcuts", verified["completed"])

    def test_jurialmunkey_0235_is_reachable_from_pilot_without_extra_repo(self):
        upstream_row = {"id": "script.module.jurialmunkey", "minimum": "0.2.2",
                        "repo": "repository.jurialmunkey", "notes": "",
                        "mandatory": False, "manifest_known": True}
        with patch.object(setup, "manifest", return_value=[upstream_row]):
            row = setup.rows()[0]
            self.assertEqual(row["repo"], setup.TEST_CHANNEL)
            self.assertEqual(row["minimum"], "0.2.35")
            current = inventory({setup.TEST_CHANNEL: "1.8.7"})
            selected = setup.next_step(setup.new_state(), current)
            self.assertEqual((selected["code"], selected["id"]),
                             ("INSTALL_ADDON", "script.module.jurialmunkey"))
            requested = setup.after_request(setup.new_state(),
                                            "script.module.jurialmunkey")
            self.assertEqual(setup.next_step(requested, current)["code"], "WAITING")
            present = inventory({setup.TEST_CHANNEL: "1.8.7",
                                 "script.module.jurialmunkey": "0.2.35"})
            self.assertEqual(setup.next_step(requested, present)["code"], "CONFIRM")
            confirmed = setup.after_confirm(requested, present)
            self.assertIn("script.module.jurialmunkey", confirmed["completed"])

    def test_batch_resolveurl_adult_resolver_and_cumination_from_pilot(self):
        batch = [
            ("script.module.resolveurl", "5.0.00", "repository.resolveurl", "5.1.212"),
            ("script.module.resolveurl.xxx", "2.0.1", "repository.dobbelina", "2.1.44"),
            ("plugin.video.cumination", "", "repository.dobbelina", "1.1.206"),
        ]
        rows = [{"id": name, "minimum": old, "repo": repo, "notes": "",
                 "mandatory": False, "manifest_known": True}
                for name, old, repo, pinned in batch]
        with patch.object(setup, "manifest", return_value=rows):
            for row, (_, _, _, version) in zip(setup.rows(), batch):
                self.assertEqual(row["repo"], setup.TEST_CHANNEL)
                self.assertEqual(row["minimum"], version)
            original = inventory({setup.TEST_CHANNEL: "1.8.8"})
            state = setup.new_state()
            for name, _, _, version in batch:
                step = setup.next_step(state, original)
                self.assertEqual((step["code"], step["id"]), ("INSTALL_ADDON", name))
                state = setup.after_request(state, name)
                original["addons"][name] = {"version": version, "enabled": True}
                self.assertEqual(setup.next_step(state, original)["code"], "CONFIRM")
                state = setup.after_confirm(state, original)
            self.assertEqual(setup.next_step(state, original)["code"], "APPS_PRESENT")
            self.assertEqual(len(state["completed"]), 3)

    def test_xvault_official_repository_is_bootstrapped_before_plugin(self):
        row = {"id": "plugin.video.xvault", "minimum": "",
               "repo": "repository.xvault", "notes": "https://xvault.repowork.de/",
               "mandatory": True, "manifest_known": True}
        with patch.object(setup, "manifest", return_value=[row]):
            self.assertIn("repository.xvault", setup.REPO_ALLOWLIST)
            box = inventory({setup.TEST_CHANNEL: "1.8.9"})
            first = setup.next_step(setup.new_state(), box)
            self.assertEqual((first["code"], first["id"]),
                             ("INSTALL_REPOSITORY", "repository.xvault"))
            request = setup.after_request(setup.new_state(), "repository.xvault")
            self.assertEqual(setup.next_step(request, box)["code"], "WAITING")
            box["addons"]["repository.xvault"] = {
                "version": "1.0.3", "enabled": True}
            self.assertEqual(setup.next_step(request, box)["code"], "CONFIRM")
            completed = setup.after_confirm(request, box)
            self.assertEqual(setup.next_step(completed, box)["code"], "INSTALL_ADDON")
            self.assertEqual(setup.next_step(completed, box)["id"], "plugin.video.xvault")
            box["addons"]["plugin.video.xvault"] = {
                "version": "2026.11.01.1", "enabled": True}
            self.assertEqual(setup.next_step(completed, box)["code"], "APPS_PRESENT")

    def test_slyguy_native_repository_then_dependency_and_trailers(self):
        sample = [
            {"id": "repository.slyguy", "minimum": "0.0.9",
             "repo": "EXTERNAL_REPOSITORY", "notes": "", "mandatory": False,
             "manifest_known": True},
            {"id": "slyguy.dependencies", "minimum": "0.0.30",
             "repo": "repository.slyguy", "notes": "", "mandatory": False,
             "manifest_known": True},
            {"id": "script.module.slyguy", "minimum": "0.86.96",
             "repo": "repository.slyguy", "notes": "", "mandatory": False,
             "manifest_known": True},
            {"id": "slyguy.trailers", "minimum": "0.2.2",
             "repo": "repository.slyguy", "notes": "", "mandatory": True,
             "manifest_known": True},
        ]
        with patch.object(setup, "manifest", return_value=sample):
            self.assertIn("repository.slyguy", setup.REPO_ALLOWLIST)
            rows = setup.rows()
            self.assertEqual(rows[0]["repo"], setup.TEST_CHANNEL)
            inv = inventory({setup.TEST_CHANNEL: "1.9.0"})
            state = setup.new_state()
            result = setup.next_step(state, inv)
            self.assertEqual(result["id"], "repository.slyguy")
            self.assertIn(result["code"], ("INSTALL_ADDON", "INSTALL_REPOSITORY"))
            state = setup.after_request(state, "repository.slyguy")
            inv["addons"]["repository.slyguy"] = {"version": "0.0.9", "enabled": True}
            state = setup.after_confirm(state, inv)
            self.assertEqual(setup.next_step(state, inv)["id"], "slyguy.dependencies")
            for ident, version in (("slyguy.dependencies", "0.0.30"),
                                   ("script.module.slyguy", "0.87.6"),
                                   ("slyguy.trailers", "0.2.2")):
                nxt = setup.next_step(state, inv)
                self.assertEqual((nxt["code"], nxt["id"]), ("INSTALL_ADDON", ident))
                state = setup.after_request(state, ident)
                inv["addons"][ident] = {"version": version, "enabled": True}
                state = setup.after_confirm(state, inv)
            self.assertEqual(setup.next_step(state, inv)["code"], "APPS_PRESENT")
            self.assertEqual(len(state["completed"]), 4)

    def test_unknown_repo_stops_with_no_install(self):
        rows = [dict(self.sample[0], id="script.not-approved", repo="repository.unknown")]
        with patch.object(setup, "manifest", return_value=rows):
            result = setup.next_step(setup.new_state(), inventory({setup.TEST_CHANNEL: "1.8.2"}))
            self.assertEqual(result["code"], "SOURCE_BLOCKED")

    def test_disabled_addon_is_not_verified(self):
        with patch.object(setup, "manifest", return_value=self.sample):
            inv = inventory({setup.TEST_CHANNEL: "1.8.2",
                             "repository.titan.bingie.mod": "2.0.1"})
            inv["addons"]["script.bingie.helper"] = {"version": "1.1.2", "enabled": False}
            self.assertEqual(setup.next_step(setup.new_state(), inv)["id"], "script.bingie.helper")

    def test_stop_resume_rejects_untrusted_history(self):
        with patch.object(setup, "manifest", return_value=self.sample):
            state = setup.stop(setup.new_state())
            self.assertEqual(setup.next_step(state, inventory({}))["code"], "STOPPED")
            self.assertFalse(setup.resume(state)["stopped"])
            bad = dict(state, attempted=["repository.bad"])
            with self.assertRaises(ValueError):
                setup.validate(bad)

    def test_source_verification_not_bypassed(self):
        with patch.object(setup, "manifest", return_value=[
            dict(self.sample[0], id="script.not-approved", repo="ZIP_REQUIRES_PROVENANCE")]):
            s = setup.next_step(setup.new_state(), inventory({setup.TEST_CHANNEL: "1.8.2"}))
            self.assertEqual(s["code"], "SOURCE_BLOCKED")
            self.assertEqual(s["reason"], "ORIGIN_UNVERIFIED")

    def test_stage_sequence_cannot_skip(self):
        with patch.object(setup, "manifest", return_value=self.sample):
            state = setup.new_state()
            with self.assertRaises(ValueError):
                setup.advance_stage(state, "skin")
            state = setup.advance_stage(state, "apps")
            self.assertEqual(state["stage"], "skin")
            state = setup.advance_stage(state, "skin")
            self.assertEqual(state["stage"], "player")
            state = setup.advance_stage(state, "player")
            self.assertEqual(state["stage"], "check")
            with self.assertRaises(ValueError):
                setup.advance_stage(state, "check")

    def test_no_secrets_in_state(self):
        state = setup.new_state()
        self.assertNotIn("token", state)
        self.assertNotIn("password", state)
        with self.assertRaises(ValueError):
            setup.validate(dict(state, portal_password="secret"))


if __name__ == "__main__":
    unittest.main()

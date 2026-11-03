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

    def test_unknown_repo_stops_with_no_install(self):
        rows = [dict(self.sample[0], repo="repository.unknown")]
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
            dict(self.sample[0], repo="ZIP_REQUIRES_PROVENANCE")]):
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

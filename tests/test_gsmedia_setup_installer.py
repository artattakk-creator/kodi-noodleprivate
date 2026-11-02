"""Offline tests for opt-in GS Media Setup 0.3.0 Kodi install pilot."""
import importlib
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import ModuleType

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src" / "script.gsmedia.setup" / "resources" / "lib"))
flow = importlib.import_module("setup_install_pilot")
ui = importlib.import_module("setup_install_ui")
from setup_plan import MANDATORY


def sample_inventory(*, present=(), repos=("repository.xbmc.org", "repository.gsmedia"),
                     disabled=()):
    from collections import defaultdict
    known = {
        "repository.xbmc.org": "3.4.0",
        "repository.gsmedia": "1.8.1",
        "script.cabertoss": "1.0.2",
        "plugin.audio.shoutcast": "2.5.2+matrix.1",
        "plugin.video.xtreammate": "0.1.29.69",
    }
    addons = {x: {"version": known[x], "enabled": x not in disabled}
              for x in tuple(repos) + tuple(present)}
    return {"code": "READY", "addons": addons}


class InstallerPilotTests(unittest.TestCase):
    def test_exact_three_pinned_source_allowlist(self):
        self.assertEqual(flow.APPROVED_IDS, ("script.cabertoss", "plugin.audio.shoutcast", "plugin.video.xtreammate"))
        self.assertEqual([r[1] for r in flow.APPROVED],
                         ["repository.xbmc.org", "repository.xbmc.org", "repository.gsmedia"])
        self.assertTrue(set(flow.APPROVED_IDS) <= set(MANDATORY))

    def test_first_action_install_caber_toss(self):
        outcome = flow.assess(flow.blank_state(), sample_inventory())
        self.assertEqual(outcome, {"code": "REQUEST_INSTALL", "addon_id": "script.cabertoss"})

    def test_no_install_without_approved_repository(self):
        result = flow.assess(flow.blank_state(), sample_inventory(repos=("repository.gsmedia",)))
        self.assertEqual(result["code"], "REPOSITORY_UNAVAILABLE")
        self.assertEqual(result["repository"], "repository.xbmc.org")

    def test_no_install_if_unknown_inventory(self):
        result = flow.assess(flow.blank_state(), {"code": "UNKNOWN", "addons": {}})
        self.assertEqual(result["code"], "INVENTORY_UNAVAILABLE")

    def test_asynchronous_request_not_success(self):
        state = flow.after_request(flow.blank_state(), "script.cabertoss")
        self.assertEqual(flow.assess(state, sample_inventory())["code"], "AWAITING_KODI_INSTALL")
        self.assertNotIn("script.cabertoss", state["completed"])

    def test_installed_but_disabled_is_not_success(self):
        state = flow.after_request(flow.blank_state(), "script.cabertoss")
        current = sample_inventory(present=("script.cabertoss",), disabled=("script.cabertoss",))
        self.assertEqual(flow.assess(state, current)["code"], "AWAITING_KODI_INSTALL")

    def test_installed_too_old_is_not_success(self):
        state = flow.after_request(flow.blank_state(), "script.cabertoss")
        inv = sample_inventory(present=("script.cabertoss",))
        inv["addons"]["script.cabertoss"]["version"] = "1.0.1"
        self.assertEqual(flow.assess(state, inv)["code"], "AWAITING_KODI_INSTALL")

    def test_verified_transition_to_next_app(self):
        state = flow.after_request(flow.blank_state(), "script.cabertoss")
        inv = sample_inventory(present=("script.cabertoss",))
        self.assertEqual(flow.assess(state, inv)["code"], "CONFIRM_INSTALLED")
        next_state = flow.after_confirm(state, "script.cabertoss")
        self.assertEqual(flow.assess(next_state, inv),
                         {"code": "REQUEST_INSTALL", "addon_id": "plugin.audio.shoutcast"})

    def test_full_approved_pilot_not_full_setup(self):
        inv = sample_inventory(present=flow.APPROVED_IDS)
        self.assertEqual(flow.assess(flow.blank_state(), inv)["code"], "PILOT_DONE_NOT_FULL_SETUP")

    def test_failed_request_explicit_retry_only(self):
        state = flow.after_request(flow.blank_state(), "script.cabertoss")
        with self.assertRaises(ValueError):
            flow.after_request(state, "plugin.audio.shoutcast")
        retry = flow.retry_explicitly(state, "script.cabertoss")
        self.assertEqual(flow.assess(retry, sample_inventory())["code"], "REQUEST_INSTALL")

    def test_strict_approved_addon_ids(self):
        with self.assertRaises(ValueError):
            flow.after_request(flow.blank_state(), "plugin.video.cumination")
        state = flow.blank_state()
        state["pending"] = "plugin.video.evil"
        self.assertEqual(flow.assess(state, sample_inventory())["code"], "INVALID_PENDING")

    def test_existing_bingie_box_guard(self):
        inv = sample_inventory(present=flow.APPROVED_IDS)
        inv["addons"]["skin.titan.bingie.mod"] = {"version": "2.2.3", "enabled": True}
        self.assertEqual(flow.protected_existing(inv), ("skin.titan.bingie.mod",))
        self.assertEqual(flow.protected_existing({"code": "UNKNOWN"}), ("INVENTORY_UNKNOWN",))

    def test_actual_kodi_builtin_once_only_after_explicit_confirmation(self):
        with tempfile.TemporaryDirectory() as root:
            profile = Path(root) / "script.gsmedia.setup"
            calls = []
            class Dialog:
                def yesno(self, *args, **kwargs):
                    return True
                def notification(self, *args, **kwargs):
                    calls.append("notification")
                def textviewer(self, *args, **kwargs):
                    calls.append("textviewer")
            fake_xbmc = ModuleType("xbmc")
            fake_gui = ModuleType("xbmcgui")
            fake_xbmc.executebuiltin = lambda command: calls.append(command)
            fake_gui.Dialog = lambda: Dialog()
            with patch.dict(sys.modules, {"xbmc": fake_xbmc, "xbmcgui": fake_gui}):
                with patch.object(ui, "_profile", return_value=str(profile)), patch.object(ui, "snapshot", return_value=sample_inventory()):
                    ui.run()
            self.assertEqual([x for x in calls if x.startswith("InstallAddon")], ["InstallAddon(script.cabertoss)"])
            self.assertIn("notification", calls)
            self.assertNotIn("textviewer", calls)
            saved = flow.load(profile)
            self.assertEqual(saved["pending"], "script.cabertoss")
            self.assertFalse(saved["completed"])

    def test_no_kodi_request_on_existing_bingie_profile(self):
        with tempfile.TemporaryDirectory() as root:
            profile = Path(root) / "script.gsmedia.setup"
            calls = []
            class Dialog:
                def yesno(self, *args, **kwargs):
                    raise AssertionError("Should not confirm install on existing profile")
                def textviewer(self, *args, **kwargs):
                    calls.append("blocked")
            fake_xbmc = ModuleType("xbmc")
            fake_gui = ModuleType("xbmcgui")
            fake_xbmc.executebuiltin = lambda cmd: calls.append(cmd)
            fake_gui.Dialog = lambda: Dialog()
            inv = sample_inventory()
            inv["addons"]["skin.titan.bingie.mod"] = {"version": "2.2.3", "enabled": True}
            with patch.dict(sys.modules, {"xbmc": fake_xbmc, "xbmcgui": fake_gui}):
                with patch.object(ui, "_profile", return_value=str(profile)), patch.object(ui, "snapshot", return_value=inv):
                    ui.run()
            self.assertEqual(calls, ["blocked"])
            self.assertIsNone(flow.load(profile))

    def test_atomic_journal_restart_and_repeat(self):
        with tempfile.TemporaryDirectory() as root:
            profile = Path(root) / "script.gsmedia.setup"
            state = flow.after_request(flow.blank_state(), "script.cabertoss")
            flow.save(profile, state)
            actual = flow.load(profile)
            self.assertEqual(actual["pending"], "script.cabertoss")
            self.assertEqual(flow.assess(actual, sample_inventory())["code"], "AWAITING_KODI_INSTALL")
            self.assertFalse((profile / (flow.JOURNAL_FILE + ".tmp")).exists())
            confirmed = flow.after_confirm(actual, "script.cabertoss")
            flow.save(profile, confirmed)
            self.assertEqual(flow.load(profile)["completed"], ["script.cabertoss"])

    def test_corrupt_journal_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as root:
            profile = Path(root) / "script.gsmedia.setup"
            profile.mkdir()
            (profile / flow.JOURNAL_FILE).write_text("{bad", encoding="utf-8")
            with self.assertRaises(ValueError):
                flow.load(profile)
            with self.assertRaises(ValueError):
                flow.save(profile, dict(flow.blank_state(), completed=["malicious.addon"]))

    def test_outside_profile_path_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                flow.save(Path(root) / "script.someoneelse", flow.blank_state())

    def test_symlink_journal_cannot_read_or_write(self):
        with tempfile.TemporaryDirectory() as root:
            profile = Path(root) / "script.gsmedia.setup"
            profile.mkdir()
            external = Path(root) / "precious.json"
            external.write_text("do-not-touch", encoding="utf-8")
            (profile / flow.JOURNAL_FILE).symlink_to(external)
            with self.assertRaises(ValueError):
                flow.load(profile)
            with self.assertRaises(ValueError):
                flow.save(profile, flow.blank_state())
            self.assertEqual(external.read_text("utf-8"), "do-not-touch")

if __name__ == "__main__":
    unittest.main()

"""Kodi Omega temporary official-add-on origin exception regression tests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

LIB = (Path(__file__).resolve().parents[1] / "src" / "script.gsmedia.setup"
       / "resources" / "lib")
sys.path.insert(0, str(LIB))
import setup_origin_guard52 as m


class FakeKodi:
    def __init__(self, mode=0, updates=0):
        self.values = {m.MODE: mode, m.UPDATES: updates}
        self.fail_set_once = ""
        self.calls = []

    def __call__(self, payload):
        d = json.loads(payload)
        method = d["method"]
        key = d["params"]["setting"]
        self.calls.append((method, key))
        if method == "Settings.GetSettingValue":
            return json.dumps({"id": 52, "jsonrpc": "2.0",
                               "result": {"value": self.values[key]}})
        if method == "Settings.SetSettingValue":
            if self.fail_set_once == key:
                self.fail_set_once = ""
                return json.dumps({"error": {"code": -32602, "message": "Denied"},
                                   "id": 52, "jsonrpc": "2.0"})
            self.values[key] = d["params"]["value"]
            return json.dumps({"id": 52, "jsonrpc": "2.0", "result": True})
        raise AssertionError(method)


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.profile = str(Path(self.temp.name) / "script.gsmedia.setup")

    def test_temporary_permission_rollback(self):
        fake = FakeKodi()
        with m.TemporaryOfficialAddonSource(self.profile, fake):
            self.assertEqual(fake.values, {m.MODE: 1, m.UPDATES: 2})
            self.assertIsNotNone(m._read_marker(self.profile))
        self.assertEqual(fake.values, {m.MODE: 0, m.UPDATES: 0})
        self.assertIsNone(m._read_marker(self.profile))

    def test_existing_any_repo_preserved(self):
        fake = FakeKodi(mode=1, updates=1)
        with m.TemporaryOfficialAddonSource(self.profile, fake):
            self.assertEqual(fake.values, {m.MODE: 1, m.UPDATES: 2})
        self.assertEqual(fake.values, {m.MODE: 1, m.UPDATES: 1})

    def test_exception_restores_policy(self):
        fake = FakeKodi()
        with self.assertRaisesRegex(RuntimeError, "failed"):
            with m.TemporaryOfficialAddonSource(self.profile, fake):
                raise RuntimeError("install failed")
        self.assertEqual(fake.values, {m.MODE: 0, m.UPDATES: 0})
        self.assertIsNone(m._read_marker(self.profile))

    def test_change_permission_denied_rolls_back_updates(self):
        fake = FakeKodi()
        fake.fail_set_once = m.MODE
        with self.assertRaises(RuntimeError):
            with m.TemporaryOfficialAddonSource(self.profile, fake):
                pass
        self.assertEqual(fake.values, {m.MODE: 0, m.UPDATES: 0})
        self.assertIsNone(m._read_marker(self.profile))

    def test_crash_recovery_on_next_boot(self):
        fake = FakeKodi()
        transaction = m.TemporaryOfficialAddonSource(self.profile, fake)
        transaction.__enter__()
        self.assertEqual(fake.values, {m.MODE: 1, m.UPDATES: 2})
        # Simulate crash: context __exit__ never executes.
        self.assertTrue(m.restore(self.profile, fake))
        self.assertEqual(fake.values, {m.MODE: 0, m.UPDATES: 0})
        self.assertFalse(m.restore(self.profile, fake))

    def test_restore_failure_keeps_recovery_marker(self):
        fake = FakeKodi()
        transaction = m.TemporaryOfficialAddonSource(self.profile, fake)
        transaction.__enter__()
        fake.fail_set_once = m.MODE
        with self.assertRaises(RuntimeError):
            m.restore(self.profile, fake)
        self.assertIsNotNone(m._read_marker(self.profile))
        self.assertTrue(m.restore(self.profile, fake))
        self.assertIsNone(m._read_marker(self.profile))
        self.assertEqual(fake.values[m.MODE], 0)

    def test_invalid_setting_and_corrupt_journal_stop(self):
        fake = FakeKodi(mode=9)
        with self.assertRaises(RuntimeError):
            with m.TemporaryOfficialAddonSource(self.profile, fake):
                pass
        self.assertFalse(Path(self.profile, m.JOURNAL_FILE).exists())
        Path(self.profile).mkdir(parents=True, exist_ok=True)
        Path(self.profile, m.JOURNAL_FILE).write_text(
            '{"schema":1,"mode":1,"updates":0,"addon":"evil"}')
        with self.assertRaises(ValueError):
            m.restore(self.profile, fake)


if __name__ == "__main__":
    unittest.main()

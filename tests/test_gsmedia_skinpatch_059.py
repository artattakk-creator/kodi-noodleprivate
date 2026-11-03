"""Regression tests for Kodi 21 GS Media 0.5.9 BINGIE backup-path safety contract."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "src/script.gsmedia.setup/resources/lib"
sys.path.insert(0, str(LIB))
import setup_patch


class BingieBackupPathContract(unittest.TestCase):
    def fixtures(self, temporary):
        root = Path(temporary)
        original = root / "addons" / "skin.titan.bingie.mod"
        patch = root / "skinpatch"
        backup = root / "userdata" / "addon_data" / "script.gsmedia.setup" / "skinpatch-060"
        meta = {}
        for name in setup_patch.FILES:
            before = ("BINGIE ORIGINAL " + name).encode()
            after = ("GS MEDIA PATCH " + name).encode()
            (original / name).parent.mkdir(parents=True, exist_ok=True)
            (patch / name).parent.mkdir(parents=True, exist_ok=True)
            (original / name).write_bytes(before)
            (patch / name).write_bytes(after)
            sha = lambda x: hashlib.sha256(x).hexdigest()
            meta[name] = {"before": sha(before), "after": sha(after)}
        (patch / "manifest.json").write_text(json.dumps({
            "skin_version": "2.2.3", "files": meta
        }), encoding="utf-8")
        (patch / "LICENSE.BINGIE").write_text("Test fixture, not upstream license")
        return original, patch, backup

    def test_wizard_and_patch_share_exact_valid_backup_folder(self):
        ui = (LIB / "setup_auto_ui50.py").read_text(encoding="utf-8")
        self.assertIn('backup_root = os.path.join(profile, "skinpatch-060")', ui)
        self.assertNotIn('backup_root = os.path.join(profile, "skinpatch-050")', ui)
        self.assertIn('SKIN_PATCH_FAILED:', ui)

    def test_backup_apply_and_retry_uses_existing_verified_patch(self):
        with tempfile.TemporaryDirectory() as tmp:
            skin, patch, backup = self.fixtures(tmp)
            self.assertEqual(setup_patch.inspect(patch, skin, "2.2.3")["code"], "READY")
            result = setup_patch.apply(patch, skin, backup, "2.2.3", user_approved=True)
            self.assertEqual(result["code"], "APPLIED_AND_VERIFIED", result)
            for relative in setup_patch.FILES:
                self.assertTrue((backup / relative).is_file())
                self.assertEqual((backup / relative).read_bytes(), ("BINGIE ORIGINAL " + relative).encode())
                self.assertEqual((skin / relative).read_bytes(), ("GS MEDIA PATCH " + relative).encode())
            self.assertEqual(setup_patch.apply(
                patch, skin, backup, "2.2.3", user_approved=True)["code"], "ALREADY_PATCHED")

    def test_untrusted_050_folder_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            skin, patch, backup = self.fixtures(tmp)
            old = backup.with_name("skinpatch-050")
            self.assertEqual(setup_patch.apply(patch, skin, old, "2.2.3", user_approved=True)["code"],
                             "UNTRUSTED_BACKUP_PATH")
            self.assertFalse(old.exists())
            for relative in setup_patch.FILES:
                self.assertEqual((skin / relative).read_bytes(), ("BINGIE ORIGINAL " + relative).encode())

    def test_modified_skin_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            skin, patch, backup = self.fixtures(tmp)
            relative = setup_patch.FILES[0]
            (skin / relative).write_bytes(b"PERSONALISED")
            result = setup_patch.apply(patch, skin, backup, "2.2.3", user_approved=True)
            self.assertEqual(result["code"], "SOURCE_HASH_MISMATCH", result)
            self.assertFalse(backup.exists())
            self.assertEqual((skin / relative).read_bytes(), b"PERSONALISED")


if __name__ == "__main__":
    unittest.main()

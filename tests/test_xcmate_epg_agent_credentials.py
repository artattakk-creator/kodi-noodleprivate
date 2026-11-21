"""Owner-only PAT provisioning for real private EPG transport."""
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

LIB = Path(__file__).resolve().parents[1] / "src/plugin.video.xtreammate/resources/lib"
sys.path.insert(0, str(LIB))

from epg_agent_credentials import NAME, clear_token, store_token
from epg_agent_github import DeliveryError, read_token

PAT = "github_pat_" + "z" * 48


class TokenProvisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "epg-agent"

    def test_owner_write_and_readback(self):
        self.assertTrue(store_token(self.root, PAT))
        self.assertEqual(read_token(self.root / NAME), PAT)
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE((self.root / NAME).stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(self.root.stat().st_mode), 0o700)
        self.assertTrue(store_token(self.root, PAT))
        self.assertEqual(read_token(self.root / NAME), PAT)

    def test_no_empty_or_invalid_credential(self):
        for value in ("", "github_pat_short", "ghp_whitespace ", "Authorization: Bearer abc",
                      PAT + "\\n", "not_a_github_token", PAT + "/injected"):
            with self.subTest(value=value[:10]):
                with self.assertRaises(DeliveryError):
                    store_token(self.root, value)
        self.assertFalse(self.root.exists())

    def test_symlink_directory_rejected(self):
        alternate = Path(self.tmp.name) / "alternate"
        alternate.mkdir()
        self.root.symlink_to(alternate, target_is_directory=True)
        with self.assertRaisesRegex(DeliveryError, "CANDIDATE_DIRECTORY_UNSAFE"):
            store_token(self.root, PAT)
        self.assertFalse((alternate / NAME).exists())

    def test_clear_removes_local_token_only(self):
        store_token(self.root, PAT)
        clear_token(self.root)
        with self.assertRaisesRegex(DeliveryError, "AUTH_NOT_PROVISIONED"):
            read_token(self.root / NAME)
        clear_token(self.root)


if __name__ == "__main__":
    unittest.main()

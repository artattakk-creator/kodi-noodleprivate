"""Public Kodi updater must not require or distribute a private read token."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

LIB = Path(__file__).resolve().parents[1] / "src" / "plugin.video.xtreammate" / "resources" / "lib"
sys.path.insert(0, str(LIB))

from epg_agent_github import DeliveryError, read_token
from epg_agent_token_bootstrap import ensure_local_token


class TestTokenBootstrap(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.profile = self.root / "userdata" / "addon_data" / "plugin.video.xtreammate" / "epg-agent"
        self.bundle = self.root / "PRIVATE_OWNER_ZIP" / "xcmate_epg_read_token.txt"
        self.bundle.parent.mkdir(parents=True)
        self.sample = "github_pat_" + "a" * 48
        self.bundle.write_text(self.sample + "\n", encoding="ascii")

    def test_private_first_install_then_public_update_without_bundle(self):
        destination = ensure_local_token(self.profile, self.bundle)
        self.assertEqual(read_token(destination), self.sample)
        self.assertEqual(destination.parent, self.profile)
        self.bundle.unlink()  # Regular public ZIP carries no credential.
        again = ensure_local_token(self.profile, self.bundle)
        self.assertEqual(again, destination)
        self.assertEqual(read_token(again), self.sample)

    def test_token_kept_even_if_later_private_zip_has_different_value(self):
        destination = ensure_local_token(self.profile, self.bundle)
        self.bundle.write_text("github_pat_" + "b" * 48 + "\n", encoding="ascii")
        self.assertEqual(ensure_local_token(self.profile, self.bundle), destination)
        self.assertEqual(read_token(destination), self.sample)

    def test_public_fresh_install_without_bundle_reports_missing_token(self):
        self.bundle.unlink()
        destination = ensure_local_token(self.profile, self.bundle)
        self.assertFalse(destination.exists())
        with self.assertRaises(DeliveryError):
            read_token(destination)

    def test_invalid_private_bundle_never_persisted(self):
        self.bundle.write_text("unvalidated", encoding="ascii")
        with self.assertRaises(DeliveryError):
            ensure_local_token(self.profile, self.bundle)
        self.assertFalse((self.profile / "reader-token.txt").exists())

    def test_symlink_bundle_not_used(self):
        self.bundle.unlink()
        other = self.root / "accidental-secret"
        other.write_text(self.sample, encoding="ascii")
        try:
            self.bundle.symlink_to(other)
        except (OSError, NotImplementedError):
            self.skipTest("No symlink support")
        with self.assertRaises(DeliveryError):
            ensure_local_token(self.profile, self.bundle)

    def test_symlink_destination_never_overwritten(self):
        self.profile.mkdir(parents=True)
        victim = self.root / "unrelated"
        victim.write_text("do not replace", encoding="utf-8")
        try:
            (self.profile / "reader-token.txt").symlink_to(victim)
        except (OSError, NotImplementedError):
            self.skipTest("No symlink support")
        with self.assertRaises(DeliveryError):
            ensure_local_token(self.profile, self.bundle)
        self.assertEqual(victim.read_text(), "do not replace")

    @unittest.skipIf(os.name == "nt", "Windows ACLs are not POSIX modes")
    def test_local_file_is_owner_only(self):
        path = ensure_local_token(self.profile, self.bundle)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.profile.stat().st_mode & 0o777, 0o700)

    def test_public_source_has_no_embedded_credential(self):
        source = (LIB / "epg_agent_token_bootstrap.py").read_text(encoding="utf-8")
        self.assertNotIn(self.sample, source)
        self.assertNotIn("PRIVATE_EPG_READER_TOKEN=", source)

    def test_kodi_service_bootstraps_before_ordinary_refresh(self):
        source = (LIB.parents[1] / "service.py").read_text(encoding="utf-8")
        self.assertIn("ensure_local_token(epg_agent_profile())", source)
        self.assertLess(source.index("ensure_local_token(epg_agent_profile())"),
                        source.index("self._last_epg = 0"))

    def test_public_release_builder_refuses_bundled_secrets(self):
        source = (LIB.parents[3] / "tools" / "build_repository.py").read_text(
            encoding="utf-8")
        self.assertIn("Private XCMate credentials prohibited in public Kodi repository",
                      source)
        self.assertIn("private_assets = SRC / addon / 'resources' / 'private'", source)


if __name__ == "__main__":
    unittest.main()

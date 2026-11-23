"""Owner-only PAT provisioning for real private EPG transport."""
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

LIB = Path(__file__).resolve().parents[1] / "src/plugin.video.xtreammate/resources/lib"
sys.path.insert(0, str(LIB))

from epg_agent_credentials import (NAME, MAX_TOKEN_FILE_BYTES, clear_token,
                                   import_token_file, store_token)
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



class MockKodiVfs:
    """Mimic Kodi VFS's bytearray API without touching real USB/SMB shares."""
    def __init__(self, data, *, fails=False):
        self.data = data
        self.fails = fails
        self.paths = []
        self.files = []

    def File(self, location, mode="rb"):
        self.paths.append((location, mode))
        if self.fails:
            raise OSError("a secret path must never be logged")
        parent = self

        class Stream:
            closed = False
            def readBytes(self, size):
                assert size == MAX_TOKEN_FILE_BYTES + 1
                return bytearray(parent.data[:size])
            def close(self):
                self.closed = True

        opened = Stream()
        self.files.append(opened)
        return opened


class KodiVfsImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "epg-agent"

    def test_usb_internal_special_and_network_files_all_work(self):
        locations = (
            "/storage/ABCD-1234/github-token.txt",
            "/home/osmc/github-token.txt",
            "special://home/github-token.txt",
            "smb://storage.home.local/secrets/github-token.txt",
            "nfs://192.168.1.10/export/github-token.txt",
            "C:\\Secrets\\github-token.txt",
            "\\\\server\\share\\github-token.txt",
        )
        for location in locations:
            with self.subTest(location=location):
                mock_vfs = MockKodiVfs((PAT + "\n").encode("ascii"))
                self.assertTrue(import_token_file(self.root, location, mock_vfs))
                self.assertEqual(read_token(self.root / NAME), PAT)
                self.assertEqual(mock_vfs.paths, [(location, "rb")])
                self.assertTrue(mock_vfs.files[0].closed)

    def test_json_token_file_with_bom_is_accepted(self):
        vfs = MockKodiVfs(b"\xef\xbb\xbf" + ('{"token": "' + PAT + '"}').encode())
        self.assertTrue(import_token_file(self.root, "smb://nas/private/token.json", vfs))
        self.assertEqual(read_token(self.root / NAME), PAT)

    def test_bad_input_does_not_replace_existing_token(self):
        original = "github_pat_" + "b" * 48
        store_token(self.root, original)
        bad_files = [
            b"",
            b"not-a-token",
            b'{"token": "invalid", "secret": "extra"}',
            b"\xff" * 20,
            b"X" * (MAX_TOKEN_FILE_BYTES + 1),
            b"Authorization: Bearer abc",
        ]
        for data in bad_files:
            with self.subTest(size=len(data)):
                with self.assertRaises(DeliveryError):
                    import_token_file(self.root, "/storage/USB/token.txt", MockKodiVfs(data))
                self.assertEqual(read_token(self.root / NAME), original)

    def test_reject_web_or_embedded_url_credentials_without_opening(self):
        location_list = (
            "https://example.com/token",
            "http://example.com/token",
            "ftp://example.com/token",
            "plugin://untrusted/token",
            "smb://admin:password@nas/secrets/token.txt",
            "nfs://nas/share/token.txt?credential=abc",
            "special://home/token.txt#fragment",
            "file:///tmp/token.txt",
        )
        for path in location_list:
            with self.subTest(scheme=path.split(":")[0]):
                mock_vfs = MockKodiVfs(PAT.encode())
                with self.assertRaisesRegex(DeliveryError, "TOKEN_FILE_INVALID_PATH"):
                    import_token_file(self.root, path, mock_vfs)
                self.assertFalse(mock_vfs.paths)
        self.assertFalse(self.root.exists())

    def test_missing_share_does_not_expose_path_or_remove_saved_token(self):
        store_token(self.root, PAT)
        location = "smb://nas/private/secret-path-token.txt"
        mock_vfs = MockKodiVfs(b"", fails=True)
        with self.assertRaises(DeliveryError) as raised:
            import_token_file(self.root, location, mock_vfs)
        self.assertEqual(raised.exception.code, "TOKEN_FILE_READ_FAILED")
        self.assertNotIn(location, str(raised.exception))
        self.assertEqual(read_token(self.root / NAME), PAT)


if __name__ == "__main__":
    unittest.main()

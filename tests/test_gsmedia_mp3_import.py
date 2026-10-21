"""Offline, no-network regression tests for importing upstream MP3 Streams Echoed."""
import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import import_mp3_streams as mp3

XML = (b'<addon id="plugin.audio.m3sr2019" version="2026.1.0" '
       b'name="MP3 Streams Echoed" provider-name="Upstream">'
       b'<requires><import addon="xbmc.python" version="3.0.0"/></requires>'
       b'<extension point="xbmc.addon.metadata"><license>GPL-3.0</license>'
       b'</extension></addon>')


def make_zip(files=None):
    files = files or {
        "plugin.audio.m3sr2019/addon.xml": XML,
        "plugin.audio.m3sr2019/default.py": b"print(1)",
    }
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        for name, value in files.items():
            archive.writestr(name, value)
    return out.getvalue()


def expected_hash(blob):
    return hashlib.sha1(
        b"blob " + str(len(blob)).encode() + b"\0" + blob
    ).hexdigest()


class Mp3StreamImportTests(unittest.TestCase):
    def test_normal_package_and_checksum(self):
        payload = make_zip()
        with patch.object(mp3, "UPSTREAM_GIT_BLOB", expected_hash(payload)):
            with tempfile.TemporaryDirectory() as tmp:
                manifest = mp3.add_to_repository(tmp, payload)
                self.assertIn("plugin.audio.m3sr2019", manifest)
                target = Path(tmp) / mp3.ADDON_ID / (
                    mp3.ADDON_ID + "-" + mp3.VERSION + ".zip"
                )
                self.assertTrue(target.exists())
                with zipfile.ZipFile(target) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertIn(mp3.ADDON_ID + "/addon.xml", archive.namelist())
                checksum = target.with_name(target.name + ".sha256").read_text()
                self.assertIn(hashlib.sha256(target.read_bytes()).hexdigest(),
                              checksum)

    def test_upstream_zip_without_root_folder(self):
        payload = make_zip({"addon.xml": XML, "default.py": b"pass"})
        with patch.object(mp3, "UPSTREAM_GIT_BLOB", expected_hash(payload)):
            archive, _ = mp3.repackage(payload)
        with zipfile.ZipFile(io.BytesIO(archive)) as pkg:
            self.assertIn(mp3.ADDON_ID + "/addon.xml", pkg.namelist())

    def test_changed_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "changed"):
            mp3.repackage(make_zip())

    def test_unsafe_traversal_is_rejected(self):
        payload = make_zip({"addon.xml": XML, "../bad.py": b"evil"})
        with patch.object(mp3, "UPSTREAM_GIT_BLOB", expected_hash(payload)):
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                mp3.repackage(payload)

    def test_wrong_addon_id_is_rejected(self):
        payload = make_zip({
            "addon.xml": XML.replace(b"plugin.audio.m3sr2019", b"plugin.bad"),
            "default.py": b"pass",
        })
        with patch.object(mp3, "UPSTREAM_GIT_BLOB", expected_hash(payload)):
            with self.assertRaisesRegex(ValueError, "mismatch"):
                mp3.repackage(payload)

    def test_size_budget_is_enforced(self):
        with self.assertRaisesRegex(ValueError, "size budget"):
            mp3.repackage(b"x" * (mp3.MAX_DOWNLOAD + 1))


if __name__ == "__main__":
    unittest.main()

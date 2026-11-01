"""Isolated official Omega add-on packaging tests, no external network needed."""
import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import import_kodi_omega_selected as official


def source_zip(addon_id, version, *, malicious=None):
    doc = (f'<addon id="{addon_id}" name="Test" version="{version}" '
           f'provider-name="Kodi">'
           '<requires><import addon="xbmc.python" version="3.0.1"/></requires>'
           '<extension point="xbmc.python.pluginsource" library="default.py">'
           '<provides>video audio</provides></extension>'
           '<extension point="xbmc.addon.metadata">'
           '<license>GPL-3.0</license></extension></addon>').encode()
    content = {
        addon_id + "/addon.xml": doc,
        addon_id + "/default.py": b"print('test')",
    }
    if malicious is not None:
        content[malicious] = b"bad"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as output:
        for name, data in content.items():
            output.writestr(name, data)
    return buffer.getvalue()


class KodiOmegaMirrorTests(unittest.TestCase):
    def test_approved_targets_and_urls(self):
        self.assertEqual(len(official.APPROVED), 2)
        self.assertIn("mirrors.kodi.tv",
                      official.upstream_url(*official.APPROVED[0]))
        with self.assertRaises(ValueError):
            official.upstream_url("plugin.unknown", "1.0")

    def test_original_archives_are_preserved(self):
        payloads = {official.upstream_url(a, v): source_zip(a, v)
                    for a, v in official.APPROVED}
        with tempfile.TemporaryDirectory() as temp:
            entries = official.import_selected(temp, provider=payloads.__getitem__)
            self.assertEqual(len(entries), 2)
            for addon_id, version in official.APPROVED:
                zipname = addon_id + "-" + version + ".zip"
                target = Path(temp) / addon_id / zipname
                self.assertEqual(target.read_bytes(),
                                 payloads[official.upstream_url(addon_id, version)])
                checksum = target.with_name(zipname + ".sha256").read_text()
                self.assertIn(hashlib.sha256(target.read_bytes()).hexdigest(),
                              checksum)

    def test_no_partial_build_on_second_package_error(self):
        name, version = official.APPROVED[0]
        good = source_zip(name, version)
        other_name, other_version = official.APPROVED[1]
        manifest = {official.upstream_url(name, version): good,
                    official.upstream_url(other_name, other_version): b"corrupt"}
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                official.import_selected(temp, provider=manifest.__getitem__)
            self.assertEqual(list(Path(temp).rglob("*.zip")), [])

    def test_reject_zip_traversal(self):
        name, version = official.APPROVED[0]
        malicious = source_zip(name, version, malicious="../outside.py")
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            official.validate(malicious, name, version)

    def test_reject_wrong_manifest_identity(self):
        name, version = official.APPROVED[0]
        bad = source_zip(name, "99.99")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            official.validate(bad, name, version)

    def test_reject_unknown_version(self):
        name, version = official.APPROVED[0]
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            official.validate(source_zip(name, version), name, "0.0.0")


if __name__ == "__main__":
    unittest.main()

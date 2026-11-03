"""Release checks against pinned merged baseline, not an installed Kodi profile."""
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import publish_pilot354 as release
BASELINE = 'f0a1bb40050e89e0220687722273e7cc859b9b5b'


def baseline(path):
    return subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT)


class PilotRelease(unittest.TestCase):
    def test_complete_index_packages_checksums_assets(self):
        self.assertEqual(release.verify_local()['index_entries'], 54)

    def test_unrelated_52_addon_entries_unchanged(self):
        old = release.entries(baseline('online-test/addons.xml'))
        new = release.entries((ROOT / 'online-test/addons.xml').read_bytes())
        self.assertEqual(old.keys(), new.keys())
        for aid in old.keys() - release.PACKAGES.keys():
            self.assertEqual(ET.tostring(old[aid]), ET.tostring(new[aid]), aid)

    def test_native_checksum_changes_for_repository_refresh(self):
        old = hashlib.md5(baseline('online-test/addons.xml')).hexdigest()
        new = (ROOT / 'online-test/addons.xml.md5').read_text().strip()
        self.assertNotEqual(old, new)

    def test_repository_and_all_old_packages_preserved(self):
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE, 'online-test'], cwd=ROOT).decode().splitlines()
        for path in paths:
            if path.endswith('.zip'):
                self.assertEqual((ROOT / path).read_bytes(), baseline(path), path)

    def test_version_ordering_no_id_changes(self):
        old = release.entries(baseline('online-test/addons.xml'))
        for aid, (version, _) in release.PACKAGES.items():
            self.assertGreater(tuple(map(int, version.split('.'))), tuple(map(int, old[aid].get('version').split('.'))))

    def test_setup_only_reviewed_delta(self):
        p = ROOT / 'online-test/script.gsmedia.setup'
        with zipfile.ZipFile(p / 'script.gsmedia.setup-0.5.19.zip') as a, zipfile.ZipFile(p / 'script.gsmedia.setup-0.5.20.zip') as b:
            changed = {n for n in set(a.namelist()) | set(b.namelist()) if n not in a.namelist() or n not in b.namelist() or a.read(n) != b.read(n)}
        self.assertEqual(changed, {'script.gsmedia.setup/addon.xml', 'script.gsmedia.setup/service.py', 'script.gsmedia.setup/resources/lib/setup_postboot71.py'})

    def test_xcmate_exact_source_bytes(self):
        with zipfile.ZipFile(ROOT / 'online-test' / release.package_path('plugin.video.xtreammate')) as archive:
            for name in archive.namelist():
                self.assertEqual(archive.read(name), (ROOT / 'src' / name).read_bytes())

    def test_manifest_only_incremental_provenance(self):
        old = json.loads(baseline('online-test/manifest.json'))
        new = json.loads((ROOT / 'online-test/manifest.json').read_text())
        allowed = {'wizard', 'zip_sha256', 'incremental_update_354'}
        for key in old.keys() - allowed:
            self.assertEqual(old[key], new[key], key)
        for aid in old['zip_sha256'].keys() - release.PACKAGES.keys():
            self.assertEqual(old['zip_sha256'][aid], new['zip_sha256'][aid])

    def test_only_two_index_blocks_changed(self):
        def remove(data):
            for aid in release.PACKAGES:
                data = re.sub(rb'<addon\b(?=[^>]*\bid="' + aid.encode() + rb'")[^>]*>.*?</addon>', b'', data, flags=re.S)
            return data
        self.assertEqual(remove(baseline('online-test/addons.xml')), remove((ROOT / 'online-test/addons.xml').read_bytes()))


if __name__ == '__main__':
    unittest.main(verbosity=2)

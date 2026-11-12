"""Exact RC bytes, immutable successful artwork paths and offline Pilot gates."""
import ast
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import release_candidate91 as rc
from release_contract91 import metadata91, without_release91

class Release91(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = subprocess.check_output(['git', 'archive', rc.BASE, 'src/plugin.video.xtreammate'], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            cls.baseline = {m.name: archive.extractfile(m).read() for m in archive if m.isfile()}

    def test_only_two_metadata_files_change_all_runtime_and_artwork_bytes_are_preserved(self):
        source = ROOT/'src/plugin.video.xtreammate'
        current = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in source.rglob('*')
                   if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store'}
        self.assertEqual(current.keys(), self.baseline.keys())
        changed = {p for p in current if current[p] != self.baseline[p]}
        self.assertEqual(changed, {'src/plugin.video.xtreammate/addon.xml',
                                  'src/plugin.video.xtreammate/changelog.txt'})
        for name in current:
            self.assertEqual(without_release91(current[name], name), self.baseline[name], name)

    def test_metadata_normalizer_rejects_unknown_extra_edits_and_foreign_paths(self):
        for name, delta in metadata91()['modules'].items():
            raw = (ROOT/name).read_bytes()
            self.assertEqual(rc.sha(raw), delta['new_sha256'])
            self.assertEqual(rc.sha(self.baseline[name]), delta['old_sha256'])
            self.assertEqual(without_release91(raw+b'\nUNREVIEWED\n', name), raw+b'\nUNREVIEWED\n')
            self.assertEqual(without_release91(raw, 'foreign/'+name), raw)

    def test_historical_metadata_contract_does_not_require_history_in_shallow_ci(self):
        from release_contract91 import original91
        original91.cache_clear()
        with mock.patch('subprocess.check_output', side_effect=AssertionError('NO_HISTORY_FOR_NORMALIZER')):
            for name in metadata91()['modules']:
                self.assertEqual(without_release91((ROOT/name).read_bytes(), name), self.baseline[name])

    def test_rc_zip_is_complete_and_byte_reproducible_with_the_repository_builder(self):
        from package_xcmate71 import build
        package = ROOT/'docs/XCMate/test-builds/02991'/rc.NAME
        with tempfile.TemporaryDirectory() as folder:
            proof = build(folder)
            self.assertEqual(proof, rc.inspect_package(package))
            self.assertEqual((Path(folder)/rc.NAME).read_bytes(), package.read_bytes())

    def test_unknown_duplicate_or_traversing_archive_members_are_rejected(self):
        package = ROOT/'docs/XCMate/test-builds/02991'/rc.NAME
        with tempfile.TemporaryDirectory() as folder:
            for extra in ('plugin.video.xtreammate/addon.xml', '../private.xml', 'credentials.json'):
                target = Path(folder)/'bad.zip'
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)
                    with zipfile.ZipFile(target, 'w') as out, zipfile.ZipFile(package) as original:
                        for info in original.infolist():
                            out.writestr(info, original.read(info.filename))
                        out.writestr(extra, b'UNREVIEWED')
                with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, 'RC91_FILE_SET'):
                    rc.inspect_package(target)

    def test_modified_runtime_payload_is_not_accepted_as_the_exact_candidate(self):
        package = ROOT/'docs/XCMate/test-builds/02991'/rc.NAME
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'bad.zip'
            with zipfile.ZipFile(target, 'w') as out, zipfile.ZipFile(package) as original:
                for info in original.infolist():
                    raw = original.read(info.filename)
                    if info.filename.endswith('/resources/lib/tmdb_token61.py'):
                        raw += b'\nUNREVIEWED\n'
                    out.writestr(info, raw)
            with self.assertRaisesRegex(ValueError, 'RC91_SOURCE_BYTES'):
                rc.inspect_package(target)

    def test_pilot_proposal_verifies_update_detection_md5_and_only_nested_pilot_package(self):
        folder = ROOT/'docs/XCMate/test-builds/02991'
        result = rc.verify(folder)
        self.assertFalse(result['repository_released'])
        self.assertEqual(result['android'], 'ANDROID_NOT_TESTED')
        expected = rc.proposal_files(folder/rc.NAME)
        self.assertEqual(len(expected), 5)
        self.assertNotIn('addons.xml', expected)
        self.assertNotIn('online-test/'+rc.NAME, expected)
        index = expected['online-test/addons.xml']
        self.assertEqual(expected['online-test/addons.xml.md5'].decode().strip(), hashlib.md5(index).hexdigest())
        nodes = E.fromstring(index)
        addon = next(n for n in nodes if n.get('id') == rc.ADDON)
        self.assertEqual(addon.get('version'), '0.1.29.91')
        installer = next(n for n in nodes if n.get('id') == 'script.gsmedia.setup')
        self.assertEqual(installer.get('version'), '0.5.26')

    def test_staging_and_rechecking_cannot_touch_live_channels(self):
        before = rc.frozen()
        with tempfile.TemporaryDirectory() as folder:
            result = rc.stage(folder)
            self.assertFalse(result['repository_released'])
            self.assertEqual(before, rc.frozen())
            bad = Path(folder)/'pilot-proposal/online-test/addons.xml.md5'
            bad.write_text('0'*32+'\n')
            with self.assertRaisesRegex(ValueError, 'RC91_PROPOSAL_BYTES'):
                rc.verify(folder)
        self.assertEqual(before, rc.frozen())

    def test_staging_into_live_or_source_locations_is_refused_before_any_build(self):
        for dest in (ROOT, ROOT/'online-test', ROOT/'src', ROOT/'plugin.video.xtreammate', ROOT/'new-live'):
            with self.subTest(dest=dest), self.assertRaisesRegex(ValueError, 'RC91_OUTPUT'):
                rc.stage(dest)

    def test_existing_channels_old_packages_and_installer_have_no_delta_from_main(self):
        paths = ['addons.xml', 'addons.xml.md5', 'index.html', 'online-test',
                 'plugin.video.xtreammate', 'script.gsmedia.setup', 'src/script.gsmedia.setup']
        result = subprocess.check_output(['git', 'diff', '--name-only', rc.BASE, '--']+paths, cwd=ROOT)
        self.assertEqual(result, b'')

    def test_release_notes_supply_five_offline_popup_entries_with_preservation_notice(self):
        sys.path.insert(0, str(ROOT/'src/plugin.video.xtreammate/resources/lib'))
        import update_notes53 as notes
        entries = notes.entries('0.1.29.91')
        self.assertEqual(len(entries), 5)
        text = '\n'.join(entries)
        for value in ('clock50', 'MP3s', 'TVMaze', 'TMDB', 'manuelle Bildzuordnung', 'Token'):
            self.assertIn(value, text)
        self.assertIn('Android-Abnahme offen', text)

    def test_no_implicit_all_channel_release_authorization(self):
        import release_channel75
        self.assertFalse(release_channel75.regular_allowed())
        self.assertFalse((ROOT/'docs/XCMate/releases/android-approved-0.1.29.91.json').exists())

    def test_previous_test_methods_and_skip_conditions_are_not_removed(self):
        names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', rc.BASE, 'tests'], cwd=ROOT).decode().splitlines()
        for name in names:
            if not Path(name).name.startswith('test_') or not name.endswith('.py'):
                continue
            old = ast.parse(subprocess.check_output(['git', 'show', rc.BASE+':'+name], cwd=ROOT))
            new = ast.parse((ROOT/name).read_bytes())
            def methods(tree):
                return {(c.name, m.name): [ast.unparse(d) for d in m.decorator_list if 'skip' in ast.unparse(d)]
                        for c in tree.body if isinstance(c, ast.ClassDef)
                        for m in c.body if isinstance(m, ast.FunctionDef) and m.name.startswith('test_')}
            before, after = methods(old), methods(new)
            for key in before:
                self.assertIn(key, after, name)
                self.assertEqual(before[key], after[key], (name, key))

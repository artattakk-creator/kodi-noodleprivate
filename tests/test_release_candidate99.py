"""The repair candidate is reproducible and isolated from release channels."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
BASE = '81bd2ad0c9c5f2d49de47c693d363a686f886111'


class Release99(unittest.TestCase):
    def contract(self):
        self.assertIsNotNone(importlib.util.find_spec('release_candidate99'),
                             'Missing review-only .99 packaging contract')
        import release_candidate99
        import release_candidate98
        from stabilization_contract100 import snapshot99
        for module in (release_candidate99, release_candidate98):
            patch = mock.patch.object(module, "ROOT", snapshot99())
            patch.start()
            self.addCleanup(patch.stop)
        return release_candidate99

    def test_build_is_byte_reproducible_and_installable(self):
        candidate = self.contract()
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            proof = candidate.stage(first)
            self.assertEqual(candidate.stage(second), proof)
            self.assertEqual(candidate.verify(first), proof)
            name = 'plugin.video.xtreammate-0.1.29.99.zip'
            archive = Path(first, name)
            self.assertEqual(archive.read_bytes(), Path(second, name).read_bytes())
            self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), proof['sha256'])
            self.assertEqual(Path(first, name + '.sha256').read_text().split(),
                             [proof['sha256'], name])
            self.assertEqual(proof['source_base'], BASE)
            self.assertEqual(proof['android'], 'ANDROID_NOT_TESTED')
            self.assertEqual(proof['status'], 'REVIEW_PACKAGE_ONLY')
            self.assertFalse(proof['repository_released'])
            self.assertFalse(proof['merge_or_publish_authorized'])
            self.assertEqual({path.name for path in Path(first).iterdir()}, {name, name + '.sha256'})
            with zipfile.ZipFile(archive) as zipped:
                self.assertIsNone(zipped.testzip())
                self.assertEqual(zipped.read('plugin.video.xtreammate/addon.xml'),
                                 (candidate.ROOT / 'src/plugin.video.xtreammate/addon.xml').read_bytes())

    def test_rejects_release_destinations_and_output_links(self):
        candidate = self.contract()
        root = candidate.ROOT
        for destination in (root.parent, root, root / 'online-test', root / 'src',
                            root / 'docs/XCMate/test-builds/02998'):
            with self.subTest(destination=destination):
                with self.assertRaisesRegex(ValueError, 'RC99_OUTPUT'):
                    candidate.stage(destination)
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder)
            existing = parent / 'existing'
            existing.mkdir()
            alias = parent / 'alias'
            alias.symlink_to(existing, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'RC99_OUTPUT_SYMLINK'):
                candidate.stage(alias)
            (existing / candidate.NAME).symlink_to(parent / 'outside.zip')
            with self.assertRaisesRegex(ValueError, 'RC99_OUTPUT_SYMLINK'):
                candidate.stage(existing)
            self.assertFalse((parent / 'outside.zip').exists())

    def test_verification_rejects_tampered_sidecar_and_archive_members(self):
        candidate = self.contract()
        with tempfile.TemporaryDirectory() as folder:
            candidate.stage(folder)
            archive = Path(folder, candidate.NAME)
            sidecar = Path(folder, candidate.NAME + '.sha256')
            sidecar.write_text('0' * 64 + '  ' + candidate.NAME + '\n')
            with self.assertRaisesRegex(ValueError, 'RC99_SHA256'):
                candidate.verify(folder)
            with zipfile.ZipFile(archive) as zipped:
                members = {name: zipped.read(name) for name in zipped.namelist()}
            manifest = 'plugin.video.xtreammate/addon.xml'
            for error in ('extra', 'missing', 'duplicate', 'changed', 'old_manifest'):
                with self.subTest(error=error):
                    edited = dict(members)
                    if error == 'extra':
                        edited['plugin.video.xtreammate/settings.xml'] = b'<settings/>'
                    elif error == 'missing':
                        edited.pop(manifest)
                    elif error == 'changed':
                        edited[manifest] += b'\n'
                    elif error == 'old_manifest':
                        edited[manifest] = edited[manifest].replace(b'0.1.29.99', b'0.1.29.98')
                    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zipped:
                        for name, raw in edited.items():
                            zipped.writestr(name, raw)
                        if error == 'duplicate':
                            with warnings.catch_warnings():
                                warnings.simplefilter('ignore', UserWarning)
                                zipped.writestr(manifest, edited[manifest])
                    with self.assertRaisesRegex(ValueError, 'RC99_FILE_SET|RC99_SOURCE_BYTES'):
                        candidate.inspect_package(archive)

    def test_inspector_rejects_symlink_mode_even_with_exact_source_bytes(self):
        candidate = self.contract()
        with tempfile.TemporaryDirectory() as folder:
            candidate.stage(folder)
            archive = Path(folder, candidate.NAME)
            disguised = Path(folder, 'disguised.zip')
            with zipfile.ZipFile(archive) as original, zipfile.ZipFile(disguised, 'w') as rewritten:
                for member in original.infolist():
                    data = original.read(member)
                    if member.filename == 'plugin.video.xtreammate/addon.xml':
                        member.external_attr = 0o120777 << 16
                    rewritten.writestr(member, data)
            with self.assertRaisesRegex(ValueError, 'RC99_PRIVATE_OR_UNSAFE_MEMBER'):
                candidate.inspect_package(disguised)

    def test_protected_release_paths_match_pinned_98(self):
        candidate = self.contract()
        self.assertEqual(candidate.publication_changes(), False)
        self.assertEqual(subprocess.run(['git', 'diff', '--quiet', BASE, '--',
                                         'addons.xml', 'online-test', 'repository-programme',
                                         'repository.gsmedia', 'script.gsmedia.setup', 'index.html'],
                                        cwd=ROOT).returncode, 0)

    def test_current_source_delta_is_exact_and_unknown_edits_are_never_normalized(self):
        from stabilization_contract99 import baseline_runtime, current_runtime, delta99
        from stabilization_contract99 import digest, runtime_without99, without99

        from stabilization_contract100 import runtime_without100
        original, current = baseline_runtime(), runtime_without100(current_runtime())
        delta = delta99()
        self.assertEqual(delta['base'], BASE)
        self.assertEqual(set(current), set(original) | set(delta['added']))
        self.assertEqual(set(delta['changed']),
                         {name for name in original if original[name] != current[name]})
        self.assertEqual(runtime_without99(current), original)
        for name, revision in delta['changed'].items():
            self.assertEqual(digest(current[name]), revision['new_sha256'])
            unexpected = current[name]+b'\nUNREVIEWED99\n'
            self.assertEqual(without99(unexpected, name), unexpected)
        for name, revision in delta['added'].items():
            self.assertEqual(digest(current[name]), revision)
            changed = dict(current)
            changed[name] += b'\nUNREVIEWED99\n'
            with self.assertRaisesRegex(ValueError, 'UNREVIEWED99_ADDED_BYTES'):
                runtime_without99(changed)


if __name__ == '__main__':
    unittest.main()

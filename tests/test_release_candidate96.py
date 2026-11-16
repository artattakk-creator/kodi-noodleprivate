"""Exact .96 source overlay and review-only package; every live channel frozen."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))


class Release96(unittest.TestCase):
    def test_entire_runtime_matches_reviewed_delta_and_no_unknown_edit_is_admitted(self):
        from stabilization_contract96 import delta96, runtime_without96, without96, baseline_runtime
        delta = delta96()
        current = {'src/plugin.video.xtreammate/'+p.relative_to(ROOT/'src/plugin.video.xtreammate').as_posix(): p.read_bytes()
                   for p in (ROOT/'src/plugin.video.xtreammate').rglob('*')
                   if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store'}
        baseline = baseline_runtime()
        self.assertEqual(set(current), set(baseline)|set(delta['added']))
        for name, change in delta['modules'].items():
            self.assertEqual(hashlib.sha256(current[name]).hexdigest(), change['new_sha256'], name)
            self.assertEqual(without96(current[name], name), baseline[name], name)
            unknown = current[name]+b'\nUNREVIEWED96\n'
            self.assertEqual(without96(unknown, name), unknown)
            self.assertEqual(without96(current[name], 'foreign/'+name), current[name])
        self.assertEqual(runtime_without96(current), baseline)
        if delta['added']:
            name = next(iter(delta['added']))
            unknown = dict(current); unknown[name] += b'\nUNREVIEWED96\n'
            with self.assertRaisesRegex(ValueError, 'UNREVIEWED96_ADDED_BYTES'):
                runtime_without96(unknown)

    def test_contract_normalizer_needs_no_git_history_and_checks_fixture_integrity(self):
        import stabilization_contract96 as contract
        delta = contract.delta96()
        name, change = next(iter(delta['modules'].items()))
        source = (ROOT/name).read_bytes()
        with mock.patch('subprocess.check_output', side_effect=AssertionError('NO_HISTORY_FOR_NORMALIZER')):
            self.assertEqual(contract.without96(source, name), change['old'].encode())
        corrupt = json.loads(json.dumps(delta)); corrupt['modules'][name]['old'] += '\nCORRUPTED\n'
        with mock.patch.object(contract, 'delta96', return_value=corrupt):
            with self.assertRaisesRegex(ValueError, 'CORRUPT_96_REVIEW_FIXTURE'):
                contract.without96(source, name)

    def test_live_publication_files_match_current_main_including_pilot95_and_fallback90(self):
        import release_candidate96 as candidate
        self.assertEqual(candidate.frozen(), candidate.baseline_frozen())
        for relative in ('plugin.video.xtreammate/', 'online-test/plugin.video.xtreammate/'):
            fallback = ROOT/relative/'plugin.video.xtreammate-0.1.29.90.zip'
            self.assertEqual(candidate.sha(fallback.read_bytes()), 'e95b0a0cc46e745a3318a609e6e57a005ee3a88965f6e7de0c4b21c68f30f17f')
        pilot = ROOT/'online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.95.zip'
        self.assertEqual(candidate.sha(pilot.read_bytes()), '1eed4d84c1317190f1936883eee2d9393368117f5a1e84516605c8ba141beb3b')

    def test_current_zip_is_reproducible_crc_clean_and_matches_all_source_bytes(self):
        import release_candidate96 as candidate
        from package_xcmate71 import build
        original = ROOT/'docs/XCMate/test-builds/02996'/candidate.NAME
        with tempfile.TemporaryDirectory() as folder:
            proof = build(folder)
            self.assertEqual(proof, candidate.inspect_package(original))
            self.assertEqual((Path(folder)/candidate.NAME).read_bytes(), original.read_bytes())

    def test_review_package_never_stages_or_authorizes_any_channel(self):
        import release_candidate96 as candidate
        before = candidate.frozen()
        with tempfile.TemporaryDirectory() as folder:
            proof = candidate.stage(folder)
            self.assertFalse(proof['repository_released'])
            self.assertFalse(proof['merge_or_publish_authorized'])
            self.assertEqual(proof['repository_staged'], 'NONE')
            self.assertEqual(proof['android'], 'ANDROID_NOT_TESTED')
            self.assertEqual(candidate.frozen(), before)
            self.assertEqual(candidate.verify(folder), proof)
            self.assertEqual({p.name for p in Path(folder).iterdir()}, {candidate.NAME, candidate.NAME+'.sha256', 'review-plan96.json'})
            plan = Path(folder)/'review-plan96.json'
            data = json.loads(plan.read_text()); data['merge_or_publish_authorized'] = True
            plan.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'RC96_PLAN_OR_BASELINE_CHANGED'):
                candidate.verify(folder)
        self.assertEqual(candidate.frozen(), before)

    def test_output_guards_reject_live_source_and_parent_paths_before_build(self):
        import release_candidate96 as candidate
        for path in (ROOT, ROOT/'online-test', ROOT/'src', ROOT/'plugin.video.xtreammate', ROOT/'new-live'):
            with self.subTest(path=path), mock.patch('package_xcmate71.build') as build:
                with self.assertRaisesRegex(ValueError, 'RC96_OUTPUT'):
                    candidate.stage(path)
                build.assert_not_called()

    def test_inspector_rejects_unknown_duplicate_or_changed_zip_members(self):
        import release_candidate96 as candidate
        original = ROOT/'docs/XCMate/test-builds/02996'/candidate.NAME
        with zipfile.ZipFile(original) as archive:
            contents = {name: archive.read(name) for name in archive.namelist()}
        for changed in ('extra', 'bytes'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as folder:
                path = Path(folder)/candidate.NAME
                values = dict(contents)
                if changed == 'extra': values['plugin.video.xtreammate/UNREVIEWED96.txt'] = b'unknown'
                else:
                    name = next(iter(values)); values[name] += b'changed'
                with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for name, value in values.items(): archive.writestr(name, value)
                with self.assertRaisesRegex(ValueError, 'RC96_FILE_SET|RC96_SOURCE_BYTES'):
                    candidate.inspect_package(path)


if __name__ == '__main__':
    unittest.main()

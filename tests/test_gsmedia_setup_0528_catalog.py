"""Piers RC2 catalogue responses, bounded restart, and provenance contracts."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'tools/gsmedia_setup0527/overlays/resources/lib'
HOTFIX = ROOT / 'tools/gsmedia_setup0528/overlays/resources/lib'


def load(name, directory):
    spec = importlib.util.spec_from_file_location(name, directory / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(number=0, *, path=None, version='1.0.0'):
    return {'addonid': f'script.fixture.{number}', 'version': version, 'broken': False,
            'dependencies': [], 'path': path or f'https://slyguy.uk/.repo/repository.slyguy/fixture-{number}.zip'}


def response(source, requested_start, requested_end):
    """Kodi 22.0RC2 CJSONUtils::HandleLimits, including empty results."""
    end = min(requested_end, len(source)) if requested_end > 0 else len(source)
    start = min(requested_start, end)
    payload = {'limits': {'total': len(source), 'start': start, 'end': end}}
    if start < end:
        payload['addons'] = source[start:end]
    return payload


class Scripted:
    def __init__(self, *pages):
        self.pages = iter(pages)
        self.starts = []

    def __call__(self, raw):
        request = json.loads(raw)
        assert request['method'] == 'Addons.GetAddons'
        params = request['params']
        assert params['installed'] is False and params['enabled'] == 'all'
        start, end = params['limits']['start'], params['limits']['end']
        self.starts.append(start)
        page = next(self.pages)
        result = page if isinstance(page, dict) else response(page, start, end)
        return json.dumps({'id': request['id'], 'jsonrpc': '2.0', 'result': result})


class Catalog528(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = TemporaryDirectory()
        cls.addClassCleanup(folder.cleanup)
        with zipfile.ZipFile(ROOT / 'script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip') as archive:
            archive.extractall(folder.name)
        lib = str(Path(folder.name) / 'script.gsmedia.setup/resources/lib')
        sys.path.insert(0, lib)
        cls.addClassCleanup(sys.path.remove, lib)
        cls.compat = load('setup_compat27', HOTFIX if (HOTFIX/'setup_compat27.py').exists() else OLD)
        with patch.dict(sys.modules, {'setup_compat27': cls.compat}):
            cls.source = load('setup_source27', HOTFIX if (HOTFIX/'setup_source27.py').exists() else OLD)

    def test_native_clamp_after_repo_shrinks_restarts_at_zero_without_mixing_pages(self):
        before = [row(i) for i in range(201)]
        during = before[:199]   # page 2 now legally returns [199, 199) and no addons.
        after = [row(543)]
        api = Scripted(before, during, after)
        self.assertEqual(self.compat.read_catalog(api), {after[0]['addonid']: after[0]})
        self.assertEqual(api.starts, [0, 200, 0])

    def test_native_zero_and_bounded_multi_page_catalogues(self):
        self.assertEqual(self.compat.read_catalog(Scripted([])), {})
        complete = [row(i) for i in range(2400)]
        api = Scripted(*([complete] * 12))
        self.assertEqual(len(self.compat.read_catalog(api)), 2400)
        self.assertEqual(api.starts, list(range(0, 2400, 200)))
        with self.assertRaisesRegex(self.compat.Blocked, 'CATALOG_TOO_LARGE:ROW_LIMIT:[0-9a-f]+'):
            self.compat.read_catalog(Scripted(complete + [row(2400)]))

    def test_kodi_valid_unrelated_identifiers_count_but_never_become_install_targets(self):
        entries = [dict(row(), addonid='script.dev@kodi!$'), row(2)]
        api = Scripted(entries)
        self.assertEqual(self.compat.read_catalog(api), {entries[1]['addonid']: entries[1]})
        self.assertEqual(api.starts, [0])

    def test_optional_markers_only_accepted_when_first_page_proves_total_coverage(self):
        entry = row()
        self.assertEqual(self.compat.read_catalog(Scripted({'limits': {'total': 1}, 'addons': [entry]})),
                         {entry['addonid']: entry})
        api = Scripted({'limits': {'total': 201}, 'addons': [entry]*200})
        with self.assertRaisesRegex(self.compat.Blocked, 'PAGE_MARKERS_MISSING'):
            self.compat.read_catalog(api)
        self.assertEqual(api.starts, [0])

    def test_structural_fault_is_fatal_and_diagnostics_never_include_raw_fields(self):
        invalid = dict(row(), addonid='secret portal password')
        cases = (
            ({'limits': {'total': 1, 'start': 0, 'end': 1}, 'addons': [invalid]}, 'ADDON_ID_INVALID'),
            ({'limits': {'total': 1, 'start': 2, 'end': 1}, 'addons': [row()]}, 'PAGE_RANGE_INVALID'),
            ({'limits': {'total': 1, 'start': 0, 'end': 1}}, 'PAGE_ROW_COUNT'),
            ({'limits': {'total': True, 'start': 0, 'end': 0}}, 'TOTAL_INVALID'),
        )
        for payload, code in cases:
            with self.subTest(code=code):
                api, diagnostics = Scripted(payload), []
                with self.assertRaisesRegex(self.compat.Blocked, code + ':[0-9a-f]+'):
                    self.compat.read_catalog(api, diagnose=diagnostics.append)
                self.assertEqual(api.starts, [0])
                self.assertEqual(diagnostics[-1]['code'], code)
                self.assertNotIn('secret portal password', json.dumps(diagnostics))
                self.assertNotIn('slyguy.uk', json.dumps(diagnostics))

    def test_page_overlap_preserves_no_partial_catalogue_and_is_bounded(self):
        initial = [row(i) for i in range(201)]
        overlap = initial[:-1] + [initial[0]]
        api = Scripted(initial, overlap, initial, overlap, initial, overlap)
        delay = Mock()
        with self.assertRaisesRegex(self.compat.Blocked, 'PAGE_OVERLAP'):
            self.compat.read_catalog(api, wait=delay)
        self.assertEqual(api.starts, [0, 200] * 3)
        self.assertEqual(delay.call_count, 2)

    def test_duplicate_requires_matching_payload_and_independent_origin(self):
        first = row()
        conflicting = dict(first, path='https://other.invalid/path.zip')
        callback = Mock(return_value=True)
        with self.assertRaisesRegex(self.compat.Blocked, 'DUPLICATE_CONFLICT'):
            self.compat.read_catalog(Scripted([first, conflicting]), confirm_duplicate=callback)
        callback.assert_not_called()
        with self.assertRaisesRegex(self.compat.Blocked, 'DUPLICATE_UNVERIFIED'):
            self.compat.read_catalog(Scripted([first, first]))
        self.assertEqual(self.compat.read_catalog(Scripted([first, first]), confirm_duplicate=callback),
                         {first['addonid']: first})
        callback.assert_called_once_with(first)

    def test_cancellation_between_full_attempts_never_starts_another_scan(self):
        initial = [row(i) for i in range(201)]
        cancelled = False
        def wait(_):
            nonlocal cancelled
            cancelled = True
        api = Scripted(initial, [])
        with self.assertRaisesRegex(self.compat.Blocked, 'CANCELLED_OR_SHUTDOWN'):
            self.compat.read_catalog(api, cancelled=lambda: cancelled, wait=wait)
        self.assertEqual(api.starts, [0, 200])

    def test_catalogue_generation_also_covers_final_validation(self):
        before, after = [row(1)], [row(2)]
        api = Scripted(before, after)
        values = iter([1, 1, 2, 2, 2, 2])
        actual = []
        output = self.compat.read_catalog(api, revision=lambda: next(values), validate=actual.append)
        self.assertEqual(list(output.values()), after)
        self.assertEqual([list(catalog.values()) for catalog in actual], [before, after])
        self.assertEqual(api.starts, [0, 0])

    def test_source_check_failure_during_a_known_cache_change_is_rechecked_from_zero(self):
        before, after = [row(1)], [row(2)]
        api = Scripted(before, after)
        stamps = iter([1, 1, 2, 2, 2, 2])
        def validate(catalog):
            if before[0]['addonid'] in catalog:
                raise self.compat.Blocked('BLOCKED_REPOSITORY_ORIGIN_UNVERIFIED')
        self.assertEqual(list(self.compat.read_catalog(
            api, revision=lambda: next(stamps), validate=validate).values()), after)
        self.assertEqual(api.starts, [0, 0])

    def test_stable_source_failure_is_not_retried(self):
        api = Scripted([row()])
        validate = Mock(side_effect=self.compat.Blocked('BLOCKED_REPOSITORY_ORIGIN_AMBIGUOUS'))
        with self.assertRaisesRegex(self.compat.Blocked, 'ORIGIN_AMBIGUOUS'):
            self.compat.read_catalog(api, revision=lambda: 1, validate=validate)
        self.assertEqual(api.starts, [0])

    def test_readonly_database_clock_detects_writes_even_with_same_repo_checksum(self):
        with TemporaryDirectory() as tmp:
            db = Path(tmp)/'Addons33.db'
            with sqlite3.connect(db) as writer:
                writer.execute('CREATE TABLE addons (entry TEXT)')
                writer.commit()
                with self.source.catalog_revision(db) as revision:
                    original = revision()
                    writer.execute('INSERT INTO addons VALUES ("catalog-update")')
                    writer.commit()
                    self.assertNotEqual(revision(), original)

    def test_duplicate_database_proof_requires_one_approved_origin_and_matching_metadata(self):
        candidate = row()
        trusted = 'repository.slyguy'
        raw = json.dumps({'path': candidate['path'], 'lifecycletype': 0, 'dependencies': []})
        with patch.object(self.source, 'database', return_value=Path('/placeholder')),                 patch.object(self.source, 'providers', return_value={candidate['addonid']: [(trusted,'1.0.0',raw)]}) as providers:
            self.assertTrue(self.source.confirm_catalog_duplicate(candidate))
            providers.return_value[candidate['addonid']].append(('repository.other','1.0.0',raw))
            self.assertFalse(self.source.confirm_catalog_duplicate(candidate))
            providers.return_value[candidate['addonid']] = [(trusted,'1.0.0',raw)]
            self.assertFalse(self.source.confirm_catalog_duplicate(dict(candidate, broken=True)))

    def test_install_provenance_checks_the_actual_rpc_selected_path_and_dependencies(self):
        candidate = row()
        ident, trusted = candidate['addonid'], 'repository.slyguy'
        raw = json.dumps({'path': candidate['path'], 'lifecycletype': 0, 'dependencies': []})
        with patch.object(self.source, 'providers', return_value={ident: [(trusted,'1.0.0',raw)]}):
            self.source.verify_source(ident, ident, trusted, {ident:'1.0.0'}, {},
                                      db=Path('/placeholder'), rpc_catalog={ident: candidate})
            with self.assertRaisesRegex(self.compat.Blocked, 'BLOCKED_REPOSITORY_ORIGIN_UNVERIFIED'):
                self.source.verify_source(ident, ident, trusted, {ident:'1.0.0'}, {},
                    db=Path('/placeholder'), rpc_catalog={ident: dict(candidate, path='https://other.invalid/a.zip')})


if __name__ == '__main__':
    unittest.main()

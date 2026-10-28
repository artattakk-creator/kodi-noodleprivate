"""Cumulative .46 protection, no settings/skin/native-stop regression allowance."""
import ast,hashlib,json,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from stabilization_contract_02947 import without_stabilization47
ROOT=Path(__file__).resolve().parents[1]


class Scope47(unittest.TestCase):
    def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02947_protection.json').read_text())
    def test_every_published_46_source_file_is_preserved_except_exact_reviewed_hooks(self):
        baseline=self.baseline()
        self.assertEqual(baseline['base'],'d9afbc309bd809587013238dfc638cd339c10ee9')
        self.assertEqual(len(baseline['source_sha256']),540)
        for path,digest in baseline['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization47((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
    def test_all_1877_previous_test_methods_remain_without_skips(self):
        total=0
        for path,cases in self.baseline()['test_methods'].items():
            present={(c.name,n.name) for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef)
                     for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            self.assertTrue(set(map(tuple,cases))<=present,path);total+=len(cases)
        self.assertEqual(total,1877)
    def test_native_42_engine_series_autoplay_profile_settings_icons_and_keymaps_are_exact(self):
        baseline=self.baseline()
        names=('live_stop42.py','native_stop41.py','exit_jobs.py','playback_exit.py','media_autoplay.py',
               'media_state.py','media_sequence.py','group_selection.py','guide_publish44.py','guide_backup44.py',
               'epg_sources.py','portals.py','widget_adapter46.py','widget_hooks45.py','infobar45.py','widget_group46.py')
        for path,digest in baseline['source_sha256'].items():
            if Path(path).name in names or '/keymaps/' in path or path.endswith(('/resources/settings.xml','/icon.png','/XCMateMedia.xml')):
                self.assertEqual(hashlib.sha256(__import__('stabilization_contract_02948').without_stabilization48((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
    def test_new_reader_snapshot_and_asset_helpers_never_trigger_guide_reset_or_skin_write(self):
        for name in ('programme_assets47','programme_snapshot47','programme_read47','widget_movie47','widget_sql47'):
            text=(ROOT/'src/plugin.video.xtreammate/resources/lib'/ (name+'.py')).read_text()
            for forbidden in ('DELETE FROM programmes','ALTER TABLE programmes','DROP TABLE','ResetDatabase','ReloadSkin(',
                              'request_refresh','import_cache(', 'set_mapping('):self.assertNotIn(forbidden,text,(name,forbidden))

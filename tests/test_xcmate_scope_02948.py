"""Exact .47 baseline, retained host contracts and P0 data/skin boundaries."""
import ast
import hashlib
import json
from pathlib import Path
import unittest
from stabilization_contract_02948 import without_stabilization48
ROOT=Path(__file__).resolve().parents[1]

class Scope48(unittest.TestCase):
    def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02948_protection.json').read_text())
    def test_all_550_published_source_files_are_preserved_with_exact_reviewed_differences(self):
        data=self.baseline();self.assertEqual(data['base'],'b047ffe7fc26a02f1ae74d99cb3546ce42735275');self.assertEqual(len(data['source_sha256']),550)
        for path,digest in data['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization48((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
    def test_all_1952_existing_methods_remain_and_none_is_skipped(self):
        count=0;baseline=self.baseline()
        for path,cases in baseline['test_methods'].items():
            tree=ast.parse((ROOT/path).read_bytes());actual={(c.name,f.name):f for c in tree.body if isinstance(c,ast.ClassDef) for f in c.body if isinstance(f,ast.FunctionDef) and f.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),actual,path)
                decorators=[ast.unparse(d) for d in actual[tuple(case)].decorator_list if 'skip' in ast.unparse(d)]
                expected=baseline['existing_skip_conditions'].get(path+'|'+case[0]+'|'+case[1],[])
                self.assertEqual(decorators,expected,(path,case))
            count+=len(cases)
        self.assertEqual(count,1952)
    def test_native_42_media_widgets_autoplay_resume_mappings_and_skin_adapters_frozen(self):
        protected={'live_stop42.py','native_stop41.py','exit_jobs.py','playback_exit.py','media_autoplay.py','media_progress.py','media_window.py','media_data.py','media_sequence.py','media_state.py','widget_items45.py','widget_group46.py','widget_movie47.py','widget_query44.py','widget_refresh45.py','widget_hooks45.py','widget_adapter45.py','widget_adapter46.py','guide_publish44.py','guide_backup44.py','portals.py','group_selection.py','infobar45.py'}
        for path,digest in self.baseline()['source_sha256'].items():
            if Path(path).name in protected or '/keymaps/' in path or path.endswith(('/resources/settings.xml','/XCMateMedia.xml','/icon.png')):
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
    def test_new_modules_have_no_skin_installer_reset_or_native_decoder_override(self):
        for path in (ROOT/'src/plugin.video.xtreammate/resources/lib').glob('*48.py'):
            text=path.read_text()
            for forbidden in ('ReloadSkin(', 'ResetDatabase(', 'PlayerControl(Stop)', 'Player().stop(', 'System.Exec(', 'SetSkin(', 'ActivateWindow(Settings', 'os.system('):self.assertNotIn(forbidden,text,path.name)
    def test_private_logs_databases_and_android_profiles_are_not_delivery_sources(self):
        addon=ROOT/'src/plugin.video.xtreammate'
        for path in addon.rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:continue
            self.assertFalse(path.name.endswith(('.sqlite','.sqlite-wal','kodi.log','kodi.old.log')),str(path))

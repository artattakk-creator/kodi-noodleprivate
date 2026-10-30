"""Cumulative .57 protection, exact .58 deltas and routing/source URL freeze."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02958 import without_stabilization58
ROOT=Path(__file__).resolve().parents[1];LIB='src/plugin.video.xtreammate/resources/lib/'


class Scope58(unittest.TestCase):
    def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02958_protection.json').read_text())
    def test_all_606_prior_source_files_survive_only_exact_reviewed_edits(self):
        base=self.baseline();self.assertEqual(base['base'],'cb58e38ff450a56a97178708db193ad0ad8b670f')
        self.assertEqual(len(base['source_sha256']),606)
        for path,digest in base['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization58((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
    def test_all_2418_previous_test_methods_and_skip_conditions_remain(self):
        base=self.baseline();count=0
        for path,cases in base['test_methods'].items():
            methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),methods,path)
                self.assertEqual([ast.unparse(d) for d in methods[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
            count+=len(cases)
        self.assertEqual(count,2418)
    def test_widget_folder_saved_urls_player_exit_modes_wizard_and_skin_writers_are_raw_frozen(self):
        base=self.baseline()['source_sha256']
        names={'main.py','home_entry.py','home_menu.py','widget_sources49.py','widget_entry46.py','widget_binding50.py','settings_sections45.py','window_navigation.py','live_exit.py','exit_jobs.py','native_stop41.py','live_stop42.py','live_recovery46.py','live_return47.py','playback_exit.py','media_progress.py','media_autoplay.py','widget_manager50.py','widget_skin50.py','widget_transaction50.py','stream_epg.py','xmltv_stream.py','epg_binding48.py','guide_mapping48.py'}
        for path,digest in base.items():
            name=Path(path).name
            if name in names or name.startswith(('setup_','wizard_','XCMateSetup')) or '/bingie50/' in path or '/skins/' in path and name!='XCMateEPGManager53.xml':
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
    def test_app_route_dispatch_and_all_other_route_functions_are_unchanged(self):
        hooks=json.loads((ROOT/'tests/fixtures/xcmate_02958_reviewed_hooks.json').read_text())['modules']
        path=LIB+'app_routes.py'
        keep=lambda raw:[ast.dump(n,include_attributes=False) for n in ast.parse(raw).body if not isinstance(n,ast.FunctionDef) or n.name!='widget']
        self.assertEqual(keep(hooks[path]['old']),keep((ROOT/path).read_text()))
    def test_new_modules_do_not_delete_profiles_reset_caches_or_write_skins(self):
        for name in ('provider_epg58.py','widget_consumer58.py','live_stop58.py'):
            tree=ast.parse((ROOT/LIB/name).read_text())
            for n in ast.walk(tree):
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):
                    self.assertNotIn(n.func.attr,('unlink','remove','rmtree','executebuiltin','setSetting','Player'))
                if isinstance(n,ast.Constant) and isinstance(n.value,str):self.assertNotIn('DELETE FROM',n.value.upper())

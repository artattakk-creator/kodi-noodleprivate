"""Cumulative .58, source URLs/skin/Wizard freeze and exact .59 deltas."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02959 import without_stabilization59
from stabilization_contract_02960 import without_stabilization60
ROOT=Path(__file__).resolve().parents[1];LIB='src/plugin.video.xtreammate/resources/lib/'


class Scope59(unittest.TestCase):
 def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02959_protection.json').read_text())
 def test_all_609_prior_source_files_remain_with_exact_reviewed_deltas(self):
  base=self.baseline();self.assertEqual(base['base'],'5fa6166e884ecced4c28ae303c7f88fc374a0446');self.assertEqual(len(base['source_sha256']),609)
  for path,digest in base['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization59((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_2463_prior_test_methods_and_skip_conditions_remain(self):
  base=self.baseline();count=0
  for path,cases in base['test_methods'].items():
   methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
   for case in cases:
    self.assertIn(tuple(case),methods,path);self.assertEqual([ast.unparse(d) for d in methods[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
   count+=len(cases)
  self.assertEqual(count,2463)
 def test_saved_widget_urls_root_routing_native_stop_wizard_and_skin_writers_raw_unchanged(self):
  names={'default.py','main.py','home_entry.py','home_menu.py','widget_sources49.py','widget_binding50.py','widget_manager50.py','widget_skin50.py','widget_transaction50.py','settings_sections45.py','window_navigation.py','native_stop41.py','live_stop42.py','exit_jobs.py','playback_exit.py','media_autoplay.py','media_progress.py','epg_binding48.py','guide_mapping48.py'}
  for path,digest in self.baseline()['source_sha256'].items():
   name=Path(path).name
   if name in names or name.startswith(('setup_','wizard_','XCMateSetup')) or '/bingie50/' in path or '/skins/' in path and name not in ('XCMateEPGManager53.xml',):self.assertEqual(hashlib.sha256(without_stabilization60((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_widget_dispatch_adds_only_safe_entry_log_without_route_changes(self):
  hooks=json.loads((ROOT/'tests/fixtures/xcmate_02959_reviewed_hooks.json').read_text())['modules'];path=LIB+'widget_entry46.py'
  tree=ast.parse(without_stabilization60((ROOT/path).read_text(),path));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef))
  fn.body=[n for n in fn.body if not (isinstance(n,ast.ImportFrom) and n.module=='boot_diagnostics' and any(a.name=='mark' for a in n.names))]
  fn.body=[n for n in fn.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='mark')]
  self.assertEqual(ast.dump(tree,include_attributes=False),ast.dump(ast.parse(hooks[path]['old']),include_attributes=False))
 def test_tvmaze_experiment_is_not_included_in_candidate(self):
  self.assertFalse((ROOT/LIB/'programme_tvmaze59.py').exists())
  names=[p.name for p in (ROOT/LIB).glob('*tvmaze*')];self.assertEqual(names,[])
 def test_new_helper_modules_never_delete_profiles_or_write_skin_settings(self):
  for name in ('live_return59.py','programme_diagnostics59.py','widget_home_probe59.py'):
   for n in ast.walk(ast.parse((ROOT/LIB/name).read_text())):
    if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):self.assertNotIn(n.func.attr,('unlink','rmtree','remove','setSetting','stop','play','executebuiltin'))

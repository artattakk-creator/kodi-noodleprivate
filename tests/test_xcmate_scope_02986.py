"""All .85 source/test methods survive; every production channel stays .85."""
import ast,hashlib,json,subprocess,unittest
from pathlib import Path
from stabilization_contract_02986 import without_stabilization86
ROOT=Path(__file__).resolve().parents[1];BASE='c6124922d067361e37db4dd325710ea89a96002e'
class Scope86(unittest.TestCase):
 def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02986_protection.json').read_text())
 def test_previous_source_files_have_only_exact_reviewed_deltas(self):
  for path,digest in self.data()['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization86((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_previous_methods_and_skip_conditions_are_preserved(self):
  data=self.data();count=0
  for path,cases in data['test_methods'].items():
   methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
   for cls,name in cases:
    count+=1;self.assertIn((cls,name),methods,path);self.assertEqual([ast.unparse(d) for d in methods[cls,name].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+cls+'|'+name])
  self.assertGreaterEqual(count,3451)
 def test_released_main_pilot_direct_and_installer_bytes_are_frozen(self):
  from channel_contract_02986 import verify
  for path in ('addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json','index.html','online-test/index.html','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.85.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.85.zip','online-test/plugin.video.xtreammate-0.1.29.85.zip','script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip'):self.assertTrue(verify(path,committed=True),path)
 def test_player_exit_portals_credentials_and_storage_policy_have_no_code_change(self):
  names=('live_exit.py','exit_jobs.py','playback_exit.py','native_stop41.py','portals.py','window_navigation.py','art_storage.py','artwork_config.py','artwork_migration.py')
  for name in names:
   path='src/plugin.video.xtreammate/resources/lib/'+name;current=__import__('stabilization_contract_02987').without_stabilization87((ROOT/path).read_bytes(),path);self.assertEqual(current,subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT))

"""Current source is cumulative; actual published .84 and protected files freeze."""
import ast,hashlib,json,subprocess,unittest
from pathlib import Path
from stabilization_contract_02985 import without_stabilization85
ROOT=Path(__file__).resolve().parents[1]
BASE='faf83b833a14ac1cc937692e10a058d6a4dd462b'
class Scope85(unittest.TestCase):
 def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02985_protection.json').read_text())
 def test_every_previous_source_file_has_reviewed_delta_or_identical_bytes(self):
  for path,digest in self.data()['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization85((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_previous_test_methods_and_skips_are_preserved(self):
  data=self.data()
  for path,cases in data['test_methods'].items():
   methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
   for cls,name in cases:
    self.assertIn((cls,name),methods,path)
    self.assertEqual([ast.unparse(d) for d in methods[cls,name].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+cls+'|'+name])
 def test_player_skin_routing_installer_and_migration_unchanged(self):
  prefixes=('src/script.gsmedia.setup/','src/plugin.video.xtreammate/resources/skins/')
  names={'live_exit.py','exit_jobs.py','playback_exit.py','native_stop41.py','app_routes.py','window_navigation.py','portals.py','artwork_config.py','art_storage.py','artwork_migration.py','artwork_ui.py'}
  for path in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src'],cwd=ROOT).decode().splitlines():
   if path.startswith(prefixes) or Path(path).name in names:self.assertEqual(without_stabilization85((ROOT/path).read_bytes(),path),subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT),path)
 def test_published_channels_frozen_and_no_release_authorization(self):
  from channel_contract_02985 import verify
  for path in ('addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json'):self.assertTrue(verify(path,committed=True))
  paths=('script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.84.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.84.zip','online-test/plugin.video.xtreammate-0.1.29.84.zip','index.html','online-test/index.html')
  for path in paths:self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show','c5b7c18ab2f8a9f6be740f3b8cd2f0d1814ec467'+':'+path],cwd=ROOT),path)
  import sys
  sys.path.insert(0,str(ROOT/'tools'))
  try:
   from release_channel75 import regular_allowed
   self.assertFalse(regular_allowed())
  finally:sys.path.remove(str(ROOT/'tools'))

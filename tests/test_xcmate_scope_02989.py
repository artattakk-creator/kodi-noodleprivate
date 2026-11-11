"""Exact published baseline, all channels and every prior test remain protected."""
import ast,hashlib,json,subprocess,unittest,zipfile
from pathlib import Path
from stabilization_contract_02989 import without_stabilization89
ROOT=Path(__file__).resolve().parents[1]
BASE='c5b7c18ab2f8a9f6be740f3b8cd2f0d1814ec467'
class Scope89(unittest.TestCase):
 def test_every_previous_source_file_has_only_reviewed_changes(self):
  data=json.loads((ROOT/'tests/fixtures/xcmate_02989_protection.json').read_bytes())
  for name,digest in data['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization89((ROOT/name).read_bytes(),name)).hexdigest(),digest,name)
 def test_every_previous_test_method_and_skip_condition_is_retained(self):
  data=json.loads((ROOT/'tests/fixtures/xcmate_02989_protection.json').read_bytes())
  for path,cases in data['test_methods'].items():
   methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
   for cls,name in cases:
    self.assertIn((cls,name),methods,path);self.assertEqual([ast.unparse(d) for d in methods[cls,name].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+cls+'|'+name])
 def test_new_archive_matches_every_source_file_hash_crc_and_reproduction(self):
  source=ROOT/'src/plugin.video.xtreammate';archive=ROOT/'docs/XCMate/test-builds/02989/plugin.video.xtreammate-0.1.29.89.zip'
  self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),Path(str(archive)+'.sha256').read_text().split()[0])
  files=[p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc') and p.name!='.DS_Store']
  with zipfile.ZipFile(archive) as z:
   self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),len(files))
   for p in files:self.assertEqual(z.read('plugin.video.xtreammate/'+p.relative_to(source).as_posix()),p.read_bytes())
 def test_all_three_release_channels_installer_and_token_code_remain_published_88(self):
  names=['addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json','index.html','online-test/index.html','script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip','src/plugin.video.xtreammate/resources/lib/tmdb_token61.py','src/plugin.video.xtreammate/resources/lib/token_write64.py','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.88.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.88.zip','online-test/plugin.video.xtreammate-0.1.29.88.zip']
  for name in names:self.assertEqual((ROOT/name).read_bytes(),subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT),name)
 def test_approved_home_design_and_player_sources_are_byte_unchanged(self):
  names=['widget_skin88.py','widget_skin87.py','programme_window46.py','live_exit.py','playback_exit.py','exit_jobs.py','native_stop41.py','hero_art86.py']
  for name in names:
   path='src/plugin.video.xtreammate/resources/lib/'+name
   self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT),name)

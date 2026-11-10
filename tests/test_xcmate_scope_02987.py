"""Every published .86 source/test remains reviewed; all channels stay frozen."""
import ast,hashlib,json,subprocess,unittest
from pathlib import Path
from stabilization_contract_02987 import without_stabilization87
ROOT=Path(__file__).resolve().parents[1]
class Scope87(unittest.TestCase):
 def protection(self):return json.loads((ROOT/'tests/fixtures/xcmate_02987_protection.json').read_text())
 def test_all_811_prior_source_files_have_only_reviewed_deltas(self):
  data=self.protection();self.assertGreaterEqual(len(data['source_sha256']),811)
  for path,digest in data['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization87((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_previous_test_methods_and_skip_conditions_remain(self):
  data=self.protection();count=0
  for path,cases in data['test_methods'].items():
   methods={(cls.name,fn.name):fn for cls in ast.parse((ROOT/path).read_bytes()).body if isinstance(cls,ast.ClassDef) for fn in cls.body if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_')}
   for cls,name in cases:
    count+=1;self.assertIn((cls,name),methods,path);self.assertEqual([ast.unparse(d) for d in methods[cls,name].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+cls+'|'+name])
  self.assertGreaterEqual(count,3510)
 def test_original_pilot_direct_installer_and_all_indexes_are_byte_exact(self):
  from channel_contract_02987 import verify
  paths=('addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json','index.html','online-test/index.html','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.86.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.86.zip','online-test/plugin.video.xtreammate-0.1.29.86.zip','script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip')
  for path in paths:self.assertTrue(verify(path,committed=True),path);self.assertTrue(verify(path),path)
 def test_player_exit_provider_and_token_implementations_have_no_changes(self):
  for name in ('live_exit.py','exit_jobs.py','playback_exit.py','native_stop41.py','portals.py','tmdb_token61.py'):
   path='src/plugin.video.xtreammate/resources/lib/'+name;self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',self.protection()['base']+':'+path],cwd=ROOT))
 def test_review_zip_matches_every_source_file_with_reproducible_sha_and_crc(self):
  import zipfile,xml.etree.ElementTree as E
  source=ROOT/'src/plugin.video.xtreammate';package=ROOT/'docs/XCMate/test-builds/02987/plugin.video.xtreammate-0.1.29.87.zip'
  self.assertEqual(E.parse(source/'addon.xml').getroot().get('version'),'0.1.29.87')
  self.assertEqual(hashlib.sha256(package.read_bytes()).hexdigest(),Path(str(package)+'.sha256').read_text().split()[0])
  with zipfile.ZipFile(package) as archive:
   self.assertIsNone(archive.testzip());files=[p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='.DS_Store']
   self.assertEqual(len(archive.namelist()),len(files))
   for path in files:self.assertEqual(archive.read('plugin.video.xtreammate/'+path.relative_to(source).as_posix()),path.read_bytes(),str(path))

 def test_native_wrapper_waits_for_its_own_complete_report(self):
  script=(ROOT/'tools/kodi_home87_host/gui87.py').read_text();prefix=script.split("# Every final Hero screenshot")[0]
  legacy=(ROOT/'tools/kodi_home86_host/gui86.py').read_text()
  class FixturePath:
   def __init__(self,*args):pass
   def read_text(self):return legacy
  namespace={'Path':FixturePath};exec(prefix.replace('from pathlib import Path',''),namespace)
  tree=ast.parse(namespace['base87'])
  calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='write_text']
  self.assertFalse(any("visible84.json" in ast.unparse(call) and "post75.json" in ast.unparse(call) for call in calls))
  self.assertIn('.replace(',namespace['base87'])
  self.assertIn("'post75.json' if cold else 'visible84.json'",namespace['base87'])

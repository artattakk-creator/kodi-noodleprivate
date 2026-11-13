"""Historical .90 source/package gate; published .90 remains immutable."""
import ast,hashlib,json,subprocess,unittest,zipfile
from pathlib import Path
from stabilization_contract_02990 import without_stabilization90
ROOT=Path(__file__).resolve().parents[1]
BASE='cb37de7103bd335a344c6738c33c4b5560ba2d4c'
def original(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
class Scope90(unittest.TestCase):
 def test_every_previous_source_file_is_identical_or_an_exact_reviewed_delta(self):
  data=json.loads((ROOT/'tests/fixtures/xcmate_02990_protection.json').read_bytes())
  for name,digest in data['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization90((ROOT/name).read_bytes(),name)).hexdigest(),digest,name)
 def test_all_existing_test_methods_and_skip_conditions_are_retained(self):
  data=json.loads((ROOT/'tests/fixtures/xcmate_02990_protection.json').read_bytes())
  for path,cases in data['test_methods'].items():
   methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
   for cls,name in cases:
    self.assertIn((cls,name),methods,path)
    self.assertEqual([ast.unparse(d) for d in methods[cls,name].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+cls+'|'+name])
 def test_review_zip_contains_every_current_source_byte_and_no_private_data(self):
  source=ROOT/'src/plugin.video.xtreammate';archive=ROOT/'docs/XCMate/test-builds/02990/plugin.video.xtreammate-0.1.29.90.zip'
  self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),Path(str(archive)+'.sha256').read_text().split()[0])
  files=[ROOT/name for name in subprocess.check_output(['git','ls-tree','-r','--name-only','4336dd56a707f80b3784fa11f179d2a427cd5727','src/plugin.video.xtreammate'],cwd=ROOT).decode().splitlines()]
  with zipfile.ZipFile(archive) as z:
   self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),len(files))
   self.assertFalse(any(n.endswith(('.log','.sqlite','.db','.pyc')) for n in z.namelist()))
   for p in files:self.assertEqual(z.read('plugin.video.xtreammate/'+p.relative_to(source).as_posix()),subprocess.check_output(['git','show','4336dd56a707f80b3784fa11f179d2a427cd5727:'+p.relative_to(ROOT).as_posix()],cwd=ROOT))
 def test_published_channels_installer_and_all_89_packages_remain_exact_main(self):
  names=['addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json','index.html','online-test/index.html','script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.89.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.89.zip','online-test/plugin.video.xtreammate-0.1.29.89.zip']
  from published_channels90 import retained,approved
  for name in names:self.assertEqual(retained(name),approved(name),name)
 def test_player_token_ui_geometry_and_installer_sources_are_not_rewritten(self):
  paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src'],cwd=ROOT).decode().splitlines()
  protected={'live_exit.py','playback_exit.py','exit_jobs.py','native_stop41.py','hero_art86.py','widget_skin87.py','widget_skin88.py','tmdb_token61.py','token_write64.py','art_storage.py','artwork_config.py','artwork_migration.py'}
  for path in paths:
   if path.startswith(('src/script.gsmedia.setup/','src/plugin.video.xtreammate/resources/skins/')) or Path(path).name in protected:self.assertEqual(__import__('stabilization_contract92').without92((ROOT/path).read_bytes(),path),original(path),path)
  path='src/plugin.video.xtreammate/resources/lib/live_overlay.py';before=ast.parse(original(path));after=ast.parse((ROOT/path).read_bytes())
  def methods(tree):return {n.name:ast.dump(n,include_attributes=False) for c in tree.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef)}
  old,new=methods(before),methods(after)
  for name in old:
   if name not in ('_load_catalog_from_disk','refresh_from_cache'):self.assertEqual(new[name],old[name],name)

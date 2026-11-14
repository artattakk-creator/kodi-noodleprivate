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
  archive_base='0deaafa17bb5e5b5ad69c55cea3750a453a2a9db'
  names=subprocess.check_output(['git','ls-tree','-r','--name-only',archive_base,'src/plugin.video.xtreammate'],cwd=ROOT).decode().splitlines()
  names=[p for p in names if '__pycache__' not in p and not p.endswith(('.pyc','/.DS_Store'))]
  with zipfile.ZipFile(archive) as z:
   self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),len(names))
   for name in names:self.assertEqual(z.read(name.removeprefix('src/')),subprocess.check_output(['git','show',archive_base+':'+name],cwd=ROOT),name)
 def test_all_three_release_channels_installer_and_token_code_remain_published_88(self):
  names=['addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json','index.html','online-test/index.html','script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip','src/plugin.video.xtreammate/resources/lib/tmdb_token61.py','src/plugin.video.xtreammate/resources/lib/token_write64.py','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.88.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.88.zip','online-test/plugin.video.xtreammate-0.1.29.88.zip']
  from published_channels90 import retained,approved
  for name in names:self.assertEqual(retained(name),approved(name),name)
 def test_approved_home_design_and_player_sources_are_byte_unchanged(self):
  names=['widget_skin88.py','widget_skin87.py','programme_window46.py','live_exit.py','playback_exit.py','exit_jobs.py','native_stop41.py','hero_art86.py']
  for name in names:
   path='src/plugin.video.xtreammate/resources/lib/'+name
   actual=__import__('stabilization_contract93').without93((ROOT/path).read_bytes(),path)
   # P0-H explicitly adds the current-programme bookmark-only explanation.
   # Keep every other approved layout/player byte protected; this one delta
   # must match the separately reviewed exact patch, not an arbitrary rewrite.
   if name=='programme_window46.py':actual=without_stabilization89(actual,path)
   self.assertEqual(actual,subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT),name)

 def test_native89_all_generated_wrapper_layers_compile_and_keep_pixel_gates(self):
  source=(ROOT/'tools/kodi_home89_host/gui89.py').read_text().split("exec(compile(base,'/base_gui88.py','exec'),globals())")[0]
  class P:
   def __init__(self,name):self.name=name
   def read_text(self,*args,**kwargs):return (ROOT/('tools/kodi_home'+{'/base_gui88.py':'88','/base_gui86.py':'86','/base_gui84.py':'84'}[self.name]+'_host/gui'+{'/base_gui88.py':'88','/base_gui86.py':'86','/base_gui84.py':'84'}[self.name]+'.py')).read_text()
  namespace={'Path':P};exec(source.replace('from pathlib import Path',''),namespace);compile(namespace['base'],'native88','exec')
  namespace2={'Path':P};exec(namespace['base'].split("exec(compile(base87,'/base_gui86.py','exec'),globals())")[0].replace('from pathlib import Path',''),namespace2)
  compile(namespace2['base87'],'native86','exec')
  namespace3={'Path':P};exec(namespace2['base87'].split("exec(compile(base,")[0].replace('from pathlib import Path',''),namespace3)
  compile(namespace3['base'],'native84','exec')
  for name in ('tools/run_kodi_home82_contract.py','tools/kodi_home80_host/gui80.py','tools/kodi_home82_host/post82.py'):self.assertIn("'0.1.29.89'",(ROOT/name).read_text())
  self.assertIn('UNEXPECTED89_NON_LOGO_ARCHIVE',namespace3['base']);self.assertIn('(1350,50,1800,520)',namespace3['base']);self.assertIn("logos89(portal,live_rows(portal),pump,capture,cold,check,home)",namespace['base'])

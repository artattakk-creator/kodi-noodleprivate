""".88 source/ZIP/channel isolation: every published .87 file remains reviewable."""
import hashlib,json,subprocess,unittest,zipfile
from pathlib import Path
from stabilization_contract_02988 import without_stabilization88
ROOT=Path(__file__).resolve().parents[1]
class Scope88(unittest.TestCase):
 def test_all_published_source_files_have_only_exact_reviewed_changes(self):
  protection=json.loads((ROOT/'tests/fixtures/xcmate_02988_protection.json').read_bytes())
  for name,digest in protection['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization88((ROOT/name).read_bytes(),name)).hexdigest(),digest,name)
 def test_current_review_archive_is_complete_reproducible_and_crc_checked(self):
  source=ROOT/'src/plugin.video.xtreammate';archive=ROOT/'docs/XCMate/test-builds/02988/plugin.video.xtreammate-0.1.29.88.zip'
  self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),Path(str(archive)+'.sha256').read_text().split()[0])
  with zipfile.ZipFile(archive) as z:
   self.assertIsNone(z.testzip());base='c5b7c18ab2f8a9f6be740f3b8cd2f0d1814ec467'
   files=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'src/plugin.video.xtreammate'],cwd=ROOT).decode().splitlines()
   files=[p for p in files if '__pycache__' not in p and not p.endswith('.pyc') and not p.endswith('/.DS_Store')]
   self.assertEqual(len(files),len(z.namelist()))
   for p in files:self.assertEqual(z.read(p.removeprefix('src/')),subprocess.check_output(['git','show',base+':'+p],cwd=ROOT),p)
 def test_three_released_packages_indexes_installer_and_token_code_are_frozen(self):
  base='cb37de7103bd335a344c6738c33c4b5560ba2d4c'
  paths=['addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json','index.html','online-test/index.html','script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip','src/plugin.video.xtreammate/resources/lib/tmdb_token61.py','src/plugin.video.xtreammate/resources/lib/token_write64.py']
  paths+=['plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.87.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.87.zip','online-test/plugin.video.xtreammate-0.1.29.87.zip']
  from published_channels90 import retained,approved
  for name in paths:self.assertEqual(retained(name),approved(name),name)
 def test_native_wrapper_compiles_actual_nested_geometry_and_caption(self):
  script=(ROOT/'tools/kodi_home88_host/gui88.py').read_text().split("exec(compile(base87,'/base_gui86.py','exec'),globals())")[0]
  class P:
   def __init__(self,name):self.name=name
   def read_text(self):return (ROOT/('tools/kodi_home86_host/gui86.py' if self.name=='/base_gui86.py' else 'tools/kodi_home84_host/gui84.py')).read_text()
  ns={'Path':P};exec(script.replace('from pathlib import Path',''),ns)
  compile(ns['base87'],'nested86','exec')
  prefix=ns['base87'].split("exec(compile(base,")[0];ns2={'Path':P};exec(prefix.replace('from pathlib import Path',''),ns2)
  compile(ns2['base'],'nested84','exec');self.assertIn('(680,560)',ns2['base']);self.assertIn('(155,300)',ns2['base']);self.assertIn('Synthetic Linux Kodi .88',ns2['base']);self.assertIn('(1350,50,1800,520)',ns2['base']);self.assertNotIn('pixels(hero_color,(1000,50,1800,520))',ns2['base'])

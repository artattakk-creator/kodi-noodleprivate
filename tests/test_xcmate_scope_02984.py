"""Current source is cumulative; actual published .83 and protected files freeze."""
import ast,hashlib,json,subprocess,unittest
from pathlib import Path
from xml.etree import ElementTree
from stabilization_contract_02984 import without_stabilization84
ROOT=Path(__file__).resolve().parents[1]
BASE='ee42712655cb9adcdcb11b09d591a1737d899844'
APPROVED_102_SHA256={
 # #514 derives image permission directly from the selected sources (c874ecff).
 'src/plugin.video.xtreammate/resources/lib/artwork_config.py':'6f9bc0422540d18cdaaa531ed871ccc003c5baacdd8a419516619e90ba8b6c8b',
 # #506 programme detail layout and independently identified portrait references (a2f0f7fe).
 'src/plugin.video.xtreammate/resources/skins/Default/720p/XCMateProgramme46.xml':'ad6d7ea402c0bd26a313b7226ed71c0f1f27116612cdba4729bac4d235b56914',
}
APPROVED_103_SHA256={
 **APPROVED_102_SHA256,
 # #517 separates the programme backdrop and poster and adds details.
 'src/plugin.video.xtreammate/resources/skins/Default/720p/XCMateProgramme46.xml':'eb3f1fac9dd1f7805306e277930309ab8f73d7641bb118af45dff1ddea32c54a',
}
class Scope84(unittest.TestCase):
 def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02984_protection.json').read_text())
 def test_every_previous_source_file_has_reviewed_delta_or_identical_bytes(self):
  for path,digest in self.data()['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization84((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
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
  version=ElementTree.parse(ROOT/'src/plugin.video.xtreammate/addon.xml').getroot().get('version')
  approved={'0.1.29.102':APPROVED_102_SHA256,'0.1.29.103':APPROVED_103_SHA256}.get(version,{})
  for path in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src'],cwd=ROOT).decode().splitlines():
   if not (path.startswith(prefixes) or Path(path).name in names):continue
   contents=(ROOT/path).read_bytes()
   if path in approved:self.assertEqual(hashlib.sha256(contents).hexdigest(),approved[path],path)
   else:self.assertEqual(without_stabilization84(contents,path),subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT),path)
 def test_published_channels_frozen_and_no_release_authorization(self):
  from channel_contract_02984 import verify
  for path in ('addons.xml','addons.xml.md5','online-test/addons.xml','online-test/addons.xml.md5','online-test/manifest.json'):self.assertTrue(verify(path,committed=True))
  paths=('script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip','plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.83.zip','online-test/plugin.video.xtreammate/plugin.video.xtreammate-0.1.29.83.zip','online-test/plugin.video.xtreammate-0.1.29.83.zip','index.html','online-test/index.html')
  from published_channels90 import retained,approved
  for path in paths:self.assertEqual(retained(path),approved(path,BASE),path)
  import sys
  sys.path.insert(0,str(ROOT/'tools'))
  try:
   from release_channel75 import regular_allowed
   self.assertFalse(regular_allowed())
  finally:sys.path.remove(str(ROOT/'tools'))

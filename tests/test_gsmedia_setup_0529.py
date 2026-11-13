"""Review-only installer storage extension; never executes the 48-component plan."""
import importlib.util
import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
build=load(ROOT/'tools/build_gsmedia_setup_0529.py','build0529')
storage=load(ROOT/'tools/gsmedia_setup0529/overlays/resources/lib/setup_storage92.py','setup_storage92')
class Installer529(unittest.TestCase):
 def setUp(self):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.folder=Path(temp.name);self.properties={};self.calls=[];self.version='0.1.29.92'
  window=SimpleNamespace(getProperty=lambda k:self.properties.get(k,''),clearProperty=lambda k:self.properties.pop(k,None))
  def execute(command):
   self.calls.append(command);nonce=command.split('setupnonce92=')[1].rstrip(')');self.properties['XCMate.Storage92.SetupAck']=json.dumps(dict(nonce=nonce,state='PREPARED'))
  dialog=SimpleNamespace(ok=lambda *a:None,yesno=lambda *a:True)
  def addon(ident):
   self.assertEqual(ident,'plugin.video.xtreammate');return SimpleNamespace(getAddonInfo=lambda key:self.version)
  patch=mock.patch.dict(sys.modules,dict(xbmc=SimpleNamespace(executebuiltin=execute,Monitor=lambda:SimpleNamespace(abortRequested=lambda:False,waitForAbort=lambda n:None)),xbmcgui=SimpleNamespace(Dialog=lambda:dialog,Window=lambda n:window),xbmcaddon=SimpleNamespace(Addon=addon)))
  patch.start();self.addCleanup(patch.stop)
 def test_upgrade_does_not_create_journal_or_run_installer(self):
  storage.initialize(self.folder,False);self.assertIsNone(storage.read(self.folder));self.assertEqual(storage.run(self.folder),'PRESERVED');self.assertFalse(self.calls)
 def test_fresh_setup_handsoff_only_to_named_xcmate_and_confirms_nonce(self):
  storage.initialize(self.folder,True);self.assertEqual(storage.run(self.folder),'PREPARED');self.assertEqual(len(self.calls),1)
  self.assertEqual(storage.read(self.folder)['state'],'PREPARED');self.assertEqual(storage.run(self.folder),'PRESERVED');self.assertEqual(len(self.calls),1)
 def test_pre92_installation_is_deferred_without_wrong_addon_settings(self):
  self.version='0.1.29.91';storage.initialize(self.folder,True);self.assertEqual(storage.run(self.folder),'DEFERRED_VERSION');self.assertFalse(self.calls)
 def test_deferred_choice_is_not_repeated_after_restart(self):
  storage.write(self.folder,dict(v=1,state='DEFERRED'));storage.initialize(self.folder,True);self.assertEqual(storage.run(self.folder),'PRESERVED');self.assertFalse(self.calls)
 def test_corrupt_and_symlink_journals_fail_closed(self):
  file=self.folder/storage.NAME;file.write_text('{bad')
  with self.assertRaises(ValueError):storage.read(self.folder)
  file.unlink();original=self.folder/'keep';original.write_text('KEEP');file.symlink_to(original)
  with self.assertRaises(OSError):storage.read(self.folder)
  self.assertEqual(original.read_text(),'KEEP')
 def test_near_full_disk_does_not_publish_unverified_choice(self):
  facts=SimpleNamespace(f_bavail=1,f_frsize=1,f_bsize=1)
  with mock.patch.object(storage.os,'statvfs',return_value=facts),self.assertRaisesRegex(OSError,'RESERVE_BLOCKED'):storage.initialize(self.folder,True)
  self.assertIsNone(storage.read(self.folder))
 def test_builder_is_reproducible_and_preserves_all_unrelated_members(self):
  with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
   proof=build.build(a);self.assertEqual(proof,build.build(b));self.assertEqual((Path(a)/build.NAME).read_bytes(),(Path(b)/build.NAME).read_bytes())
   baseline=ROOT/'online-test/script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip';self.assertEqual(hashlib.sha256(baseline.read_bytes()).hexdigest(),build.BASE_SHA)
   with zipfile.ZipFile(baseline) as old,zipfile.ZipFile(Path(a)/build.NAME) as new:
    self.assertEqual(set(new.namelist())-set(old.namelist()),{build.PREFIX+'resources/lib/setup_storage92.py'})
    changed={name for name in old.namelist() if old.read(name)!=new.read(name)}
    self.assertEqual(changed,{build.PREFIX+'addon.xml',build.PREFIX+'resources/lib/setup_auto_ui50.py'})
 def test_hook_closes_modal_after_component_stage_before_skin_and_prefetch(self):
  text=(ROOT/'tools/gsmedia_setup0529/overlays/resources/lib/setup_auto_ui50.py').read_text();part=text.split('if code == "STAGE_SKIN":',1)[1].split('if code == "STAGE_PLAYER":',1)[0]
  self.assertLess(part.index('progress.close()'),part.index('storage92_run(profile)'));self.assertLess(part.index('storage92_run(profile)'),part.index('_apply_skin('))
  self.assertNotIn('storage92_run(profile)',text.split('if code == "STAGE_SKIN":',1)[0])
if __name__=='__main__':unittest.main()

"""Separate installer-only extension; .86 and published .5.26 stay unchanged."""
import hashlib,importlib.util,io,sys,tempfile,types,unittest,zipfile
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
class Pairing527(unittest.TestCase):
 def setUp(self):self.builder=load('build527',ROOT/'tools/build_gsmedia_setup_0527.py');self.ui=load('pair527',ROOT/'tools/gsmedia_setup0527/overlays/resources/lib/setup_tmdb87.py')
 def test_reproducible_zip_preserves_every_unrelated_0526_member_and_all_channels(self):
  with tempfile.TemporaryDirectory() as temp:
   folder=Path(temp);a=self.builder.build(folder);first=(folder/a['version'].replace('0.5.27','script.gsmedia.setup-0.5.27.zip')).read_bytes();self.builder.build(folder);self.assertEqual(first,(folder/'script.gsmedia.setup-0.5.27.zip').read_bytes())
   with zipfile.ZipFile(ROOT/'script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip') as old,zipfile.ZipFile(io.BytesIO(first)) as new:
    delta=set(a['changed']);self.assertEqual(len(delta),5)
    for name in old.namelist():
     if name not in delta:self.assertEqual(old.read(name),new.read(name),name)
    self.assertIsNone(new.testzip());self.assertIn(b'TMDB_PAIRING',new.read(self.builder.PREFIX+'resources/lib/setup_auto_ui50.py'))
   self.assertEqual(hashlib.sha256((ROOT/'script.gsmedia.setup/script.gsmedia.setup-0.5.26.zip').read_bytes()).hexdigest(),self.builder.BASE)
 def test_one_hundred_skip_pending_resume_pair_error_cycles_never_run_component_installer(self):
  states=['NOT_CONFIGURED','LOCAL_TOKEN_VALID','OPTED_OUT','PENDING','GATEWAY_PAIRED','AUTH_FAILED','SERVER_UNAVAILABLE'];records=[]
  addon=types.SimpleNamespace(getAddonInfo=lambda key:'0.1.29.87' if key=='version' else '/synthetic-xcmate',setSetting=lambda k,v:records.append((k,v)))
  current=['NOT_CONFIGURED'];client=types.SimpleNamespace(status=lambda:current[0]);shown=[]
  modules={'xbmcaddon':types.SimpleNamespace(Addon=lambda *args:addon),'xbmcgui':types.SimpleNamespace(Dialog=lambda:types.SimpleNamespace(yesno=lambda *a,**k:True)), 'tmdb_gateway_client87':client,'tmdb_gateway_ui87':types.SimpleNamespace(show=lambda:shown.append(True))}
  for i in range(100):
   for state in states:
    current[0]=state
    with mock.patch.dict(sys.modules,modules):result=self.ui.offer('/synthetic-setup',manual=bool(i%2))
    self.assertIn(result,self.ui.CODES);self.assertTrue(all(key=='tmdb_pairing_state87' and value in self.ui.CODES for key,value in records))
  self.assertEqual(len(records),700);self.assertTrue(shown)
 def test_old_client_and_declined_setup_are_optional_not_install_failures(self):
  records=[];addon=types.SimpleNamespace(getAddonInfo=lambda key:'0.1.29.86',setSetting=lambda *v:records.append(v))
  with mock.patch.dict(sys.modules,{'xbmcaddon':types.SimpleNamespace(Addon=lambda *a:addon),'xbmcgui':types.SimpleNamespace()}):self.assertEqual(self.ui.offer('ignored'),'SKIPPED')
  self.assertEqual(records,[('tmdb_pairing_state87','SKIPPED')])

 def test_successful_optional_import_records_pairing_without_credential_values(self):
  records=[];addon=types.SimpleNamespace(getAddonInfo=lambda key:'0.1.29.87' if key=='version' else '/synthetic-xcmate',setSetting=lambda *v:records.append(v))
  states=iter(['NOT_PAIRED','LOCAL_TOKEN_VALID']);client=types.SimpleNamespace(status=lambda:next(states))
  modules={'xbmcaddon':types.SimpleNamespace(Addon=lambda *args:addon),'xbmcgui':types.SimpleNamespace(Dialog=lambda:types.SimpleNamespace()),'tmdb_gateway_client87':client,'tmdb_gateway_ui87':types.SimpleNamespace(show=lambda:None)}
  with mock.patch.dict(sys.modules,modules):self.assertEqual(self.ui.offer('ignored',manual=True),'PAIRED')
  self.assertEqual(records,[('tmdb_pairing_state87','PAIRED')])

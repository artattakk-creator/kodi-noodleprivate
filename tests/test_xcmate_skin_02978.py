"""Full active BINGIE graph, variables, safe reload and old user rows."""
import base64,importlib,json,lzma,sys,time,unittest
from pathlib import Path
from unittest import mock
from xcmate050_fixture import Fixture50
from xcmate027_fixture import ROOT

class Skin78(Fixture50,unittest.TestCase):
 def setUp(self):
  super().setUp();self.m=importlib.import_module('widget_skin78')
  data=json.loads(lzma.decompress(base64.b64decode((ROOT/'tests/fixtures/bingie223_graph78.json.xz.b64').read_bytes())))
  for name,text in data.items():(self.skin/name).write_text(text)
  self.saved.append(['mainmenu','10000','widgetName.3','Neu im Kino']);self.saved.append(['mainmenu','10000','widgetPath.3','plugin://foreign.cinema/?list=now_playing'])
  self.prop.write_text(repr(self.saved));self.original={name:(self.skin/name).read_bytes() for name in self.m.FILES}
 def plan(self):
  with mock.patch('xbmcvfs.translatePath',return_value=str(self.profile)):return self.skinmod.prepare(self.skin)
 def test_registry_and_home_hook_are_part_of_verified_transaction_and_idempotent(self):
  before=self.menu.read_bytes(),self.prop.read_bytes();plan=self.plan();self.assertEqual(len(plan['entries']),8)
  self.assertEqual({n:(self.skin/n).read_bytes() for n in self.m.FILES},self.original)
  self.skinmod.apply(plan['id'],self.skin,confirmed=True)
  self.assertTrue(self.m.installed(self.skin));current={n:(self.skin/n).read_bytes() for n in self.m.FILES};self.assertEqual(self.m.build(current),current)
  self.assertEqual((self.menu.read_bytes(),self.prop.read_bytes()),before)
  self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True);self.assertEqual({n:(self.skin/n).read_bytes() for n in self.m.FILES},self.original)
 def test_disk_patch_is_not_runtime_pass_until_actual_controls_and_variable_resolve(self):
  p=self.plan();self.skinmod.apply(p['id'],self.skin,confirmed=True)
  with mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmc.getInfoLabel',return_value=''):
   self.assertFalse(self.skinmod.applied(self.skin))
  with mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmc.getInfoLabel',return_value=self.m.READY),mock.patch('xbmcgui.Window',return_value=mock.Mock()):
   self.assertTrue(self.skinmod.applied(self.skin))
 def test_missing_include_or_variable_does_not_pass_static_gate(self):
  data=self.m.build(self.original);self.assertTrue(self.m.verify(data))
  bad=dict(data);bad['xml/Includes.xml']=bad['xml/Includes.xml'].replace(b'IncludesHomeWidgets.xml',b'Unused.xml')
  with self.assertRaises(ValueError):self.m.verify(bad)
  bad=dict(data);bad['xml/IncludesVariables.xml']=bad['xml/IncludesVariables.xml'].replace(b'XCMate75.Title',b'Wrong75.Title')
  with self.assertRaises(ValueError):self.m.verify(bad)
 def test_user_backup_inventory_contains_kino_source_and_never_changes_original(self):
  p=self.plan();folder=self.folder/'home78_inventory'/p['metadata']['inventory78']
  from utils import addon_data_dir
  folder=Path(addon_data_dir())/'home78_inventory'/p['metadata']['inventory78'];index=json.loads((folder/'inventory.json').read_text())
  copy=next(v for v in index['files'] if v['target']==str(self.prop));self.assertEqual((folder/copy['file']).read_bytes(),self.prop.read_bytes());self.assertEqual((folder/copy['file']).stat().st_mode&0o777,0o600)
 def test_interruption_rolls_back_eight_targets_and_keeps_user_rows(self):
  p=self.plan();original=self.tx.replace;calls=[]
  def fail(target,*a,**k):
   calls.append(str(target))
   if len(calls)==4:raise OSError('synthetic write failure')
   return original(target,*a,**k)
  with mock.patch.object(self.tx,'replace',side_effect=fail):
   with self.assertRaises(OSError):self.skinmod.apply(p['id'],self.skin,confirmed=True)
  self.assertEqual({n:(self.skin/n).read_bytes() for n in self.m.FILES},self.original);self.assertIn('Neu im Kino',self.prop.read_text())
 def test_activation_waits_for_foreign_modal_and_posts_exactly_one_reload(self):
  import types
  a=importlib.import_module('home_activation78');props={};home=types.SimpleNamespace(getProperty=lambda k:props.get(k,''),setProperty=lambda k,v:props.__setitem__(k,v))
  with mock.patch('xbmcgui.Window',return_value=home),mock.patch('time.monotonic',return_value=100):a.request('a'*32)
  value=json.loads(props[a.KEY]);value['consumer_prepared78']=True;props[a.KEY]=json.dumps(value)
  with mock.patch('xbmcgui.Window',return_value=home),mock.patch.object(self.m,'runtime',return_value={'code':'VARIABLES_NOT_LOADED'}),mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmc.getCondVisibility',return_value=False),mock.patch('xbmc.executebuiltin') as builtin:
   with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=10100),mock.patch('time.monotonic',return_value=103):a._next=0;a.poll();builtin.assert_not_called()
   with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=9999),mock.patch('time.monotonic',return_value=104):a._next=0;a.poll();a._next=0;a.poll();builtin.assert_called_once_with('ReloadSkin()',wait=False)
   with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=9999),mock.patch('time.monotonic',return_value=121):a._next=0;a.poll();self.assertEqual(json.loads(props[a.KEY])['phase'],'RELOAD_UNCONFIRMED');builtin.assert_called_once()
 def test_ready_files_without_prepared_consumers_never_claim_runtime_ready(self):
  import types
  a=importlib.import_module('home_activation78');props={};home=types.SimpleNamespace(getProperty=lambda k:props.get(k,''),setProperty=lambda k,v:props.__setitem__(k,v))
  with mock.patch('xbmcgui.Window',return_value=home):
   a.request('b'*32)
   with mock.patch.object(self.m,'runtime',return_value={'code':'RUNTIME_READY'}),mock.patch('xbmc.getSkinDir',return_value='other',create=True):a._next=0;a.poll()
  self.assertEqual(json.loads(props[a.KEY])['phase'],'FILES_VERIFIED')
 def test_only_known_released_77_adapter_qualifies_for_automatic_upgrade(self):
  previous=importlib.import_module('widget_skin77');nav=importlib.import_module('widget_skin75')
  for name in self.m.FILES[:4]:(self.skin/name).write_bytes(previous.candidate(name,self.original[name]))
  (self.skin/self.m.FILES[4]).write_bytes(nav.navigation_candidate(self.original[self.m.FILES[4]]))
  self.assertTrue(self.m.previous_owned(self.skin))
  target=self.skin/self.m.FILES[0];target.write_bytes(target.read_bytes()+b'<!-- unknown user edit -->')
  self.assertFalse(self.m.previous_owned(self.skin))

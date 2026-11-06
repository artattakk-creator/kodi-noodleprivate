"""Space Blue exact compatibility, control absence, fixed full-bleed image."""
import importlib,json,types,unittest
from pathlib import Path
from unittest import mock
from xcmate050_fixture import Fixture50
from xcmate027_fixture import Fixture,ADDON

class Skin77(Fixture50,unittest.TestCase):
 def test_exact_space_blue_layout_applies_and_restores_branding_and_bindings(self):
  skin77=importlib.import_module('widget_skin77');target=self.skin/'xml/IncludesHomeBingie.xml';raw=target.read_bytes();self.assertEqual(raw.count(skin77.OLD),1)
  branded=raw.replace(skin77.OLD,skin77.NEW).replace(skin77.RED,skin77.BLUE);target.write_bytes(branded)
  before=self.skin_bytes();bindings=(self.menu.read_bytes(),self.prop.read_bytes())
  plan=self.skinmod.prepare(self.skin);self.assertEqual(self.skin_bytes(),before);self.skinmod.apply(plan['id'],self.skin,confirmed=True)
  self.assertIn(skin77.NEW,target.read_bytes());self.assertNotIn(skin77.OLD,target.read_bytes())
  from xml.etree import ElementTree as E
  image=E.parse(self.skin/'xml/IncludesHomeWidgets.xml').find(".//control[@id='296751']")
  self.assertEqual(image.findtext('aspectratio'),'scale');self.assertEqual((image.findtext('left'),image.findtext('top'),image.findtext('width'),image.findtext('height')),('270','20','1080','580'))
  self.assertEqual((self.menu.read_bytes(),self.prop.read_bytes()),bindings)
  self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),before)
 def test_space_blue_with_unrecognized_additional_edit_is_not_accepted(self):
  skin77=importlib.import_module('widget_skin77');target=self.skin/'xml/IncludesHomeBingie.xml';target.write_bytes(target.read_bytes().replace(skin77.OLD,skin77.NEW)+b'<!-- private edit -->');before=self.skin_bytes()
  with self.assertRaises(ValueError):self.skinmod.prepare(self.skin)
  self.assertEqual(self.skin_bytes(),before)
 def test_newly_prepared_skin_is_never_written_without_approval(self):
  before=self.skin_bytes();plan=self.skinmod.prepare(self.skin)
  with self.assertRaises(PermissionError):self.skinmod.apply(plan['id'],self.skin)
  self.assertEqual(self.skin_bytes(),before)
 def test_previous_75_adapter_can_upgrade_then_restore_both_levels(self):
  from widget_skin75 import candidate as released
  from widget_transaction50 import prepare,apply
  before=self.skin_bytes();old=prepare('skin',[(self.skin/name,released(name,raw)) for name,raw in before.items()],dict(skin=str(self.skin.resolve()),meta_sha=importlib.import_module('widget_transaction50').sha((self.skin/'addon.xml').read_bytes())))
  apply(old['id'],'skin',[self.skin/name for name in self.skinmod.FILES],confirmed=True);version75=self.skin_bytes()
  plan=self.skinmod.prepare(self.skin);self.skinmod.apply(plan['id'],self.skin,confirmed=True);self.assertTrue(self.skinmod.applied(self.skin))
  self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),version75)
  self.skinmod.apply(old['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),before)

class Runtime77(Fixture,unittest.TestCase):
 def test_missing_control_is_negatively_cached_without_losing_text_publishing(self):
  module=importlib.import_module('home_runtime77');module._missing.clear();get=mock.Mock(side_effect=RuntimeError('missing'))
  window=types.SimpleNamespace(getControl=get,setProperty=self.properties.__setitem__)
  for _ in range(20):self.assertEqual(module.publish(window)['code'],'CONTROL_MISSING')
  self.assertEqual(get.call_count,1)
 def test_native_control_binding_reports_visibility_but_never_visual_android_pass(self):
  module=importlib.import_module('home_runtime77');module._missing.clear();control=types.SimpleNamespace(getPosition=lambda:(270,20),getWidth=lambda:1080,getHeight=lambda:580)
  window=types.SimpleNamespace(getControl=lambda cid:control,setProperty=self.properties.__setitem__)
  with mock.patch('xbmc.getCondVisibility',return_value=True):value=module.publish(window,image='https://approved.invalid/test.png')
  self.assertEqual(value['code'],'CONTROL_READY');self.assertTrue(value['image_bound']);self.assertTrue(value['visible']);self.assertNotIn('PASS',json.dumps(value))
 def test_texture_cache_is_separate_from_reference_and_android_screenshot(self):
  pipeline=importlib.import_module('programme_pipeline77');event=dict(pid='p',sid='1',key='a'*64,title='Synthetic',start=self.now,stop=self.now+100)
  art=dict(code='READY',source='xmltv_event',image='/synthetic/test.png')
  result=dict(result=dict(textures=[dict(url=art['image'],cachedurl='abc.png',sizes=[dict(width=320,height=180)])]))
  with mock.patch('xbmc.executeJSONRPC',return_value=json.dumps(result),create=True):
   self.assertEqual(pipeline.texture(event,art)['code'],'TEXTURE_CACHED')
  self.assertNotIn('PASS',json.dumps(pipeline.texture(event,{})))
 def test_repeated_missing_epg_reads_reuse_generation_bound_worker_lease(self):
  local=importlib.import_module('local_epg');cache=importlib.import_module('epg_poll77');cache._values.clear()
  row=dict(sid='1',name='Synthetic',epg_channel_id='xml')
  view=local.View();view.revision=('r',1);view.code='OK'
  with mock.patch.object(local,'window',return_value=view) as read:
   for _ in range(10):local.now_next('p',[row],{},now=self.now)
  self.assertEqual(read.call_count,1)
 def test_mapping_change_or_real_event_boundary_invalidates_read_lease(self):
  cache=importlib.import_module('epg_poll77');cache._values.clear();row=dict(sid='1',epg_channel_id='xml')
  first=cache.key('p',[row],{},False);second=cache.key('p',[row],{'1':'mapped'},False);self.assertNotEqual(first,second)
  cache.remember(first,{'1':dict(now='Synthetic',start=self.now-5,stop=self.now+5)},self.now)
  self.assertIsNotNone(cache.read(first,self.now));self.assertIsNone(cache.read(first,self.now+6))

 def test_same_channel_id_from_different_sources_never_shares_poll_lease(self):
  cache=importlib.import_module('epg_poll77');binding=importlib.import_module('epg_binding48');row=dict(sid='1',epg_channel_id='xml')
  a=binding.preview({},'1','xml','provider');b=binding.preview({},'1','xml','external')
  self.assertNotEqual(cache.key('p',[row],a,False),cache.key('p',[row],b,False))

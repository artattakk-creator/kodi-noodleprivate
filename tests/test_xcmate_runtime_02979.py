"""Directory/generation ACK vs counts; targeted bounded recovery and no GUI IO."""
import importlib,json,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Runtime79(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.m=importlib.import_module('widget_runtime79');self.tag='a'*64;self.state={'count':'24','tag':self.tag,'visible':True,'missing':False};self.commands=[]
  self.window=types.SimpleNamespace(getProperty=lambda k:self.properties.get(k,''),setProperty=self.properties.__setitem__,getControl=lambda cid:self.control(cid))
  self.patches=[mock.patch('xbmcgui.Window',return_value=self.window),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=9999),mock.patch('xbmc.getCondVisibility',side_effect=lambda c:self.state['visible'] if c.startswith('Control.IsVisible') else False),mock.patch('xbmc.getInfoLabel',side_effect=self.label)]
  for p in self.patches:p.start();self.addCleanup(p.stop)
  self.slot=self.m.slot(self.portal,'vod');self.properties[self.slot]=json.dumps(dict(tag=self.tag,count=24,at=time.time()))
  self.m._plans[('p','vod')]=dict(portal=self.portal,scope=importlib.import_module('epg_handoff63').profile_scope(),slot=self.slot,ids=[2520],hooks=['XCMate.Widget45.Reload.vod'],at=time.monotonic())
 def control(self,cid):
  if self.state['missing']:raise RuntimeError('missing native control')
  return types.SimpleNamespace()
 def label(self,key):return self.state['count'] if key.endswith('.NumItems') else self.state['tag'] if key.endswith('Property(XCMate.Directory79)') else '/synthetic.png' if key.endswith('.ListItem.Art(poster)') else ''
 def stages(self):
  with mock.patch.object(self.m,'note') as note:self.m.poll()
  return [c.args[2] for c in note.call_args_list]
 def test_count_alone_is_not_reload_or_active_consumer_ack(self):
  self.state['tag']='b'*64;stages=self.stages();self.assertNotIn('RELOAD_ACK',stages);self.assertNotIn('ACTIVE_CONTROL',stages)
 def test_actual_item_generation_ack_is_distinct_from_texture_visibility(self):
  stages=self.stages();self.assertIn('RELOAD_ACK',stages);self.assertIn('ACTIVE_CONTROL',stages);self.assertIn('TEXTURE_REQUESTED',stages);self.assertNotIn('TEXTURE_VISIBLE',stages)
 def test_missing_control_is_not_classified_as_empty_directory(self):
  self.state['missing']=True;stages=self.stages();self.assertIn('CONTROL_MISSING',stages);self.assertNotIn('CONTROL_EMPTY',stages)
 def test_hidden_row_is_retained_without_empty_retry(self):
  self.state.update(visible=False,count='0');self.assertIn('CONTROL_HIDDEN',self.stages());self.assertEqual(self.m._tries,{})
 def test_empty_consumer_gets_two_targeted_retries_without_rebuild_or_focus(self):
  self.state['count']='0';start=time.monotonic();events=[]
  for elapsed in (0,3,20,40,80):
   self.m._plans[('p','vod')]['at']=start+elapsed
   with mock.patch('time.monotonic',return_value=start+elapsed),mock.patch.object(self.m,'note') as note:self.m.poll();events += [c.args[2] for c in note.call_args_list]
  self.assertEqual(events.count('RELOAD_REQUESTED'),2);self.assertIn('.retry79.1',self.properties['XCMate.Widget45.Reload.vod']);self.assertFalse(self.builtins)
 def test_gui_poll_never_reads_files_or_sql(self):
  with mock.patch('os.stat',side_effect=AssertionError('GUI file IO')),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI SQL')):self.assertIn('ACTIVE_CONTROL',self.stages())
 def test_unchanged_frame_announces_again_after_interpreter_notice_state_loss(self):
  import test_xcmate_home_02974 as h
  model=h.Home74(methodName='runTest');model.setUp();self.addCleanup(model.doCleanups);rows=model.rows();model.frame(rows)
  notice=importlib.import_module('widget_notice46');notice._pending.clear();model.w.publish(model.portal,'vod',rows)
  self.assertIn(('p','vod'),notice._pending)
 def test_changed_consumers_require_reload_even_with_ready_hero_controls(self):
  a=importlib.import_module('home_activation78');start=time.monotonic()
  a.request('consumer79',consumers_changed=True);value=json.loads(self.properties[a.KEY]);value.update(consumer_prepared78=True,at=start-3);self.properties[a.KEY]=json.dumps(value)
  with mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('widget_skin78.runtime',return_value=dict(code='RUNTIME_READY')),mock.patch('xbmc.executebuiltin') as command:
   a._next=0;a.poll();self.assertEqual(json.loads(self.properties[a.KEY])['phase'],'RELOAD_POSTED');command.assert_called_once_with('ReloadSkin()',wait=False)
 def test_paged_live_frame_reannounces_all_eighty_eight_unchanged_items(self):
  import test_xcmate_home_02974 as h
  model=h.Home74(methodName='runTest');model.setUp();self.addCleanup(model.doCleanups)
  rows=[dict(sid=str(i),name='Live '+str(i),category_id='a') for i in range(88)]
  with mock.patch('programme_assets47.read_many',return_value={}):
   model.frame(rows,kind='live');notice=importlib.import_module('widget_notice46');notice._pending.clear()
   from pathlib import Path
   before=Path(model.w.path('p','live')).read_bytes();model.w.publish(model.portal,'live',rows)
  self.assertEqual(notice._pending[('p','live')][1],88);self.assertEqual(Path(model.w.path('p','live')).read_bytes(),before)

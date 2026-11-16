"""Real profile/SQLite regressions; never Android acceptance."""
import ast,importlib,sys,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture,LIB


class EPG94(Fixture,unittest.TestCase):
 def real_sources(self):
  sys.modules.pop('epg_status',None)
  sys.modules.pop('epg_sources',None)
  return importlib.import_module('epg_sources')
 def test_new_xtream_defaults_to_actual_provider_xmltv_without_external_choice(self):
  self.client.get_xmltv_epg_url=lambda:'https://provider.invalid/xmltv.php'
  draft=importlib.import_module('setup_draft').Draft(self.portal)
  self.addCleanup(draft.dispose)
  self.assertTrue(draft.provider_epg)
 def test_adding_dach_enables_only_known_implicit_global_disable(self):
  self.portal.update(epg_show=False,epg_opt_out94=False)
  import portals
  with mock.patch.object(portals,'update',side_effect=lambda pid,v:self.portal.update(v) or True):
   sources=self.real_sources();sources.add_presets('p',['de_master','de_epgshare','at_epgshare','ch_epgshare'])
  self.assertTrue(self.portal['epg_show'])
  self.assertEqual(len(sources.configuration('p')['sources']),4)
  self.assertEqual(sources.add_presets('p',['de_master']),[])
 def test_adding_source_archives_legacy_xtream_optout_under_96_baseline(self):
  self.portal.update(epg_show=False,epg_opt_out94=True)
  sources=self.real_sources();sources.add_presets('p',['de_master'])
  self.assertTrue(self.portal['epg_show'])
  self.assertEqual(self.portal['provider_baseline_history96'][0]['values']['epg_opt_out94'],True)
 def test_full_index_missing_selected_group_also_requests_targeted_rows(self):
  tree=ast.parse((LIB/'live_overlay.py').read_text())
  cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='LiveNavigator')
  node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_list_content')
  ns={'CHANNEL_PAGE_SIZE':100};exec(compile(ast.Module(body=[node],type_ignores=[]),'real-list-content','exec'),ns)
  channels=[SimpleNamespace(name='Unterhaltung '+str(i),extra={'stream_id':str(i)}) for i in range(137)]
  nav=SimpleNamespace(mode='channels',category_id='b',enabled={'a','b'},index=SimpleNamespace(selection=lambda *a:([],{})),_catalog_partial46=False,_catalog_ready=True,_highlight={'channels':0},_scroll_to_current=False)
  with mock.patch('live_group93.rows',return_value=channels) as read:
   labels=ns['_list_content'](nav)
  self.assertEqual(len(nav.visible_channels),137);self.assertEqual(len(labels),100);read.assert_called_once()
 def test_group_change_does_not_apply_foreign_portal_future(self):
  from concurrent.futures import Future
  m=importlib.import_module('live_group93');future=Future();future.set_result(dict(pid94='old',base_index93=None,channels=['WRONG'],merged_channels93=['WRONG'],merged_index93=None))
  nav=SimpleNamespace(portal=self.portal,xc=self.client,category_id='disabled',enabled={'b'},_group_task93=('b',future),_group_rows93={'b':['OLD']},_group_owner94='old',index=None)
  nav.category_id='b'
  with mock.patch.object(m._slots,'acquire',return_value=False):self.assertIsNone(m.rows(nav))
  self.assertEqual(nav._group_rows93,{})
 def test_confirmed_empty_requires_published_group_head(self):
  m=importlib.import_module('live_catalog46')
  self.index.import_group('p','live','b',[dict(stream_id='9',category_id='b',name='Previous')])
  # Simulate an independently verified empty generation, not a failed API.
  with self.index.connect() as db:db.execute("DELETE FROM items_v2 WHERE pid='p' AND kind='live' AND cid='b'")
  proof={};_,rows=m.read(self.portal,only='b',receipt94=proof)
  self.assertEqual(rows,[]);self.assertTrue(proof['generation']);self.assertEqual(proof['count'],0)
 def test_reselecting_full_group_probes_new_local_generation(self):
  from concurrent.futures import Future
  m=importlib.import_module('live_group93');nav=SimpleNamespace(portal=self.portal,xc=self.client,category_id='b',enabled={'a','b'},index=None,_group_rows93={'b':['OLD']})
  m.selected(nav)
  with mock.patch.object(m._slots,'acquire',return_value=False):self.assertEqual(m.rows(nav),['OLD'])
  self.assertIn('b',nav._group_verify94)
 def test_manager_status_poll_does_not_reset_items_or_remote_selection(self):
  from xcmate027_fixture import ADDON,QueuedPool
  module=importlib.import_module('epg_manager53')
  with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool):
   w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.portal)
  self.addCleanup(w.close);w.show();w._pool.drain();w.pump()
  control=w.getControl(200);before=list(control.items);control.selectItem(0)
  j=dict(id='a'*32,ack=12345,state='RUNNING',source='provider',sources={'provider':dict(phase='PARSE',channels=5,programmes=12,staged=7)},stalled=False)
  with mock.patch.object(control,'reset',side_effect=AssertionError('STATUS_MUST_NOT_RESET_LIST')):
   w._job_loaded94(j);w._job_loaded94(j)
  self.assertEqual(control.items,before);self.assertEqual(control.getSelectedPosition(),0)
  self.assertEqual(control.getListItem(0).getProperty('Busy94'),'true')
  self.assertEqual(w.rows[0]['last_attempt66'],12345)
 def test_xtream_legacy_optout_survives_as_history_with_96_baseline(self):
  self.client.get_xmltv_epg_url=lambda:'https://provider.invalid/xmltv.php'
  for values in (dict(epg_show=False),dict(provider_epg_enabled=False),dict(epg_opt_out94=True)):
   draft=importlib.import_module('setup_draft').Draft(dict(self.portal,**values))
   try:
    self.assertTrue(draft.provider_epg)
    previous=draft.data['provider_baseline_history96'][0]['values']
    for key,value in values.items():self.assertEqual(previous[key],value)
   finally:draft.dispose()
 def test_unknown_legacy_false_is_archived_without_claiming_artwork_consent(self):
  self.portal['epg_show']=False;self.portal.pop('epg_opt_out94',None)
  self.real_sources().add_presets('p',['de_master'])
  self.assertTrue(self.portal['epg_show'])
  previous=self.portal['provider_baseline_history96'][0]['values']
  self.assertFalse(previous['epg_show']);self.assertNotIn('epg_opt_out94',previous)

 def test_job_control_storage_failure_is_readable_not_an_uncaught_gui_callback(self):
  self.real_sources()  # Load the production status module, not the minimal GUI fixture.
  import importlib.util
  spec=importlib.util.spec_from_file_location('epg94_storage_case',LIB/'epg.py');epg=importlib.util.module_from_spec(spec);spec.loader.exec_module(epg)
  with mock.patch('epg_gate46.access',return_value='NOT_CREATED'),mock.patch('epg_jobs94.request',side_effect=OSError(28,'synthetic private storage detail')),mock.patch('epg_status.update') as status:
   self.assertFalse(epg.request_refresh('p',self.portal,force=True))
   status.assert_called_with('p','refresh','CONTROL_STORAGE_UNAVAILABLE',running=False)

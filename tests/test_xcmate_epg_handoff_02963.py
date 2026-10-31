"""One real local guide, cache-only Home text and immutable warm player handoff."""
import importlib,sqlite3,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class Handoff63(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  self.local=importlib.import_module('local_epg');self.bridge=importlib.import_module('epg_handoff63')
  self.row=dict(sid='1',name='Local station',category_id='a',epg_channel_id='xml')
  self.events={'xml':[dict(name='Current local event',descr='Local description',start_timestamp=self.now-60,stop_timestamp=self.now+120),dict(name='Following local event',descr='Next description',start_timestamp=self.now+120,stop_timestamp=self.now+300)]}
  importlib.import_module('guide_store').import_cache('p',self.events,'fixture63',now=self.now,trusted_feed=True)
 def read(self):return self.local.now_next('p',[self.row],{},now=self.now)['1']
 def test_local_database_identity_survives_warm_player_constructor_without_sql_or_network(self):
  before=self.read();self.assertEqual(before['now'],'Current local event')
  model=importlib.import_module('tv_data')
  with mock.patch('sqlite3.connect',side_effect=AssertionError('GUI SQL')),mock.patch('builtins.open',side_effect=AssertionError('GUI file')):
   started=time.perf_counter();snapshot=model.GuideSnapshot(self.portal,self.client,initial_sid='1');after=snapshot.get('1',now=self.now)
   self.assertLess(time.perf_counter()-started,.1)
  for k in ('now','next','start','stop','next_start','next_stop','canonical46','programme_key47','snapshot_revision'):self.assertEqual(after[k],before[k],k)
  self.assertTrue(after['programme_key47'])
 def test_source_mapping_revision_stale_age_and_event_rollover_never_show_previous_station(self):
  before=self.read()
  self.assertIsNone(self.bridge.get('other-portal','1',now=self.now))
  self.assertIsNone(self.bridge.get('p','wrong-sid',now=self.now))
  with mock.patch('epg_status.revision',return_value='new-revision'):
   self.assertIsNone(self.bridge.get('p','1',now=self.now))
  self.assertIsNone(self.bridge.get('p','1',now=self.now+301))
  after=self.bridge.get('p','1',now=self.now+180);self.assertEqual(after['now'],'Following local event')
  self.assertNotEqual(before['programme_key47'],after['programme_key47'])
 def test_qualified_source_selection_is_part_of_the_cache_identity(self):
  binding=importlib.import_module('epg_binding48')
  info=self.read()
  a=binding.Mappings({'1':'xml'},{'1':{'source':'source-a','channel':'xml'}})
  b=binding.Mappings({'1':'xml'},{'1':{'source':'source-b','channel':'xml'}})
  self.bridge.remember('p',self.row,info,a)
  self.assertIsNotNone(self.bridge.get('p','1',now=self.now,mappings=a))
  self.assertIsNone(self.bridge.get('p','1',now=self.now,mappings=b))
  self.assertIsNone(self.bridge.get('p','1',now=self.now,mappings={}))
 def test_optional_art_failure_keeps_real_now_next_and_exact_native_click(self):
  self.read()
  values=importlib.import_module('live_items62')
  with mock.patch('widget_render47.values',side_effect=sqlite3.OperationalError('fixture optional art failure')):
   result=values.values(self.portal,[self.row])[0]
  self.assertEqual(result['props']['XCMate.ProgrammeTitle46'],'Current local event')
  self.assertEqual(result['props']['XCMate.ProgrammeNext46'],'Following local event')
  self.assertIn('action=play_live',result['url']);self.assertIn('sid=1',result['url'])
  self.assertIn('neutral.png',result['props']['XCMate.ProgrammeImage46'])
 def test_all_eighty_eight_prepared_station_snapshots_are_bounded_and_independent(self):
  info=self.read()
  for i in range(88):
   row=dict(self.row,sid=str(i));self.bridge.remember('p',row,info,{})
  for i in range(88):
   value=self.bridge.get('p',str(i),now=self.now);self.assertIsNotNone(value,'warm station '+str(i));self.assertEqual(value['now'],'Current local event')
  self.assertLessEqual(sum(k.startswith(self.bridge.PREFIX) for k in self.properties),512)
 def test_revision_changed_during_read_cannot_stamp_old_data_as_new(self):
  info=self.read();self.properties.clear()
  with mock.patch('epg_status.revision',return_value='new'):
   self.bridge.remember('p',self.row,info,{},expected_revision='old')
  self.assertIsNone(self.bridge.get('p','1',now=self.now))
 def test_focus_publishes_complete_inactive_bank_then_switches_atomically_without_gui_io(self):
  self.read();hero=importlib.import_module('hero_epg63')
  hero._next=0;hero._last=None;hero._focus=None;hero._art=None
  from localization import tr
  selected={'XCMate.NoEpg63':tr(36102),'XCMate.RemainingFormat63':tr(36668,'{0}'),'XCMate.Home50':'true','XCMate.PortalId':'p','XCMate.MediaId':'1','XCMate.WidgetToken41':'1'*32}
  info=lambda expr:selected.get(expr.removeprefix('ListItem.Property(').removesuffix(')'),'')
  writes=[]
  win=types.SimpleNamespace(getProperty=lambda k:self.properties.get(k,''),setProperty=lambda k,v:(writes.append(k),self.properties.__setitem__(k,v)),clearProperty=mock.Mock(side_effect=AssertionError('blank frame')))
  with mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('xbmc.getInfoLabel',side_effect=info),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.Window',return_value=win),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI SQL')),mock.patch('builtins.open',side_effect=AssertionError('GUI disk')):
   hero.poll()
   self.assertEqual(writes[-1],'XCMate.Hero63.Active')
   bank=self.properties['XCMate.Hero63.Active'];self.assertEqual(self.properties['XCMate.Hero63.'+bank+'.Title'],'Current local event')
   self.assertEqual(self.properties['XCMate.Hero63.'+bank+'.Identity'],'1'*32)
   previous=len(writes);hero._next=0;hero.poll();self.assertEqual(len(writes),previous)
 def test_new_database_publication_invalidates_warm_dto_on_worker_without_gui_sql(self):
  before=self.read();updated={'xml':[dict(name='New committed local event',start_timestamp=self.now-60,stop_timestamp=self.now+120)]}
  importlib.import_module('guide_store').import_cache('p',updated,'fixture63-new',now=self.now+1,trusted_feed=True)
  after=self.read();self.assertEqual(after['now'],'New committed local event');self.assertNotEqual(before['snapshot_revision'],after['snapshot_revision'])
 def test_same_portal_and_station_in_another_kodi_profile_never_reuse_cached_data(self):
  self.read()
  import xbmcvfs
  translate=xbmcvfs.translatePath
  with mock.patch('xbmcvfs.translatePath',side_effect=lambda p:'/different-local-profile/' if p=='special://profile/' else translate(p)):
   self.assertIsNone(self.bridge.get('p','1',now=self.now))
  self.assertIsNotNone(self.bridge.get('p','1',now=self.now))
 def test_safe_reason_codes_distinguish_missing_mapping_stale_cache_and_late_ui(self):
  self.assertIsNone(self.bridge.get('p','unprepared'));self.assertEqual(self.bridge.state('p','unprepared'),'EPG_CACHE_UNAVAILABLE')
  info=self.read()
  with mock.patch('epg_status.revision',return_value='changed'):
   self.assertIsNone(self.bridge.get('p','1'));self.assertEqual(self.bridge.state('p','1'),'EPG_CACHE_STALE')
  wall=time.time();mono=time.monotonic()
  nav=types.SimpleNamespace(portal=self.portal,sid='1',_guide=types.SimpleNamespace(get=lambda sid:dict(info,_published_at63=wall-5)),_epg_visible63=('1',wall-2,mono-2))
  with mock.patch.object(self.bridge,'note') as note:self.bridge.visible(nav)
  self.assertEqual(note.call_args.args[3],'EPG_UI_UPDATE_DELAY')

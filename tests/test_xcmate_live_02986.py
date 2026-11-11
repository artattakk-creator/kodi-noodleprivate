"""A: isolated complete rail, independent durable provider logo receipts."""
import importlib,io,json,os,time,unittest
from unittest import mock
from pathlib import Path
from xcmate027_fixture import Fixture
class Live86(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.portal=dict(id='p',name='Synthetic',type='xtream',start_group_id='g');self.rows=[dict(sid=str(i),name='Station '+str(i),category_id='g',stream_icon='https://example.org/logo'+str(i)+'.png') for i in range(88)]
 def test_complete_first_rail_has_no_epg_sql_artwork_or_network_calls(self):
  rail=importlib.import_module('live_rail86')
  __import__('localization').english()
  with mock.patch('logo_manifest86.read',return_value={'0':'/verified/logo0.png'}),mock.patch('epg_handoff63.get',return_value=None),mock.patch('sqlite3.connect',side_effect=AssertionError('SQL')),mock.patch('widget_assets69.read',side_effect=AssertionError('artwork')),mock.patch('widget_art44.art',side_effect=AssertionError('artwork')),mock.patch('builtins.open',side_effect=AssertionError('filesystem')),mock.patch('socket.getaddrinfo',side_effect=AssertionError('DNS')):
   started=time.monotonic();items=rail.values(self.portal,self.rows);elapsed=time.monotonic()-started
  self.assertEqual([i['props']['XCMate.MediaId'] for i in items],[str(i) for i in range(88)]);self.assertLess(elapsed,.25)
  self.assertEqual(items[0]['art']['thumb'],'/verified/logo0.png');self.assertEqual(items[0]['props']['XCMate.HeroImage63'],'/verified/logo0.png')
  from widget_focus41 import token
  self.assertEqual(items[37]['props']['XCMate.WidgetToken41'],token(self.portal,self.rows[37]));self.assertIn('action=play_live',items[37]['url'])
 def test_source_play_route_preserved_for_non_xtream(self):
  with mock.patch('logo_manifest86.read',return_value={}),mock.patch('epg_handoff63.get',return_value=None):items=importlib.import_module('live_rail86').values(dict(self.portal,type='m3u'),self.rows[:1])
  self.assertIn('action=source_play',items[0]['url'])
 def test_manifest_cold_read_checks_profile_account_source_and_stat(self):
  m=importlib.import_module('logo_manifest86');from artwork_backend import LocalArtworkStorage
  folder=self.folder/'logos86';folder.mkdir();backend=LocalArtworkStorage(str(folder));row=self.rows[0]
  body=__import__('test_xcmate_02988').png((300,100));digest=__import__('hashlib').sha256(body).hexdigest();file=Path(backend.resolve_target(digest));file.write_bytes(body);s=file.stat()
  record=dict(context=m.context(self.portal),sha256=digest,stamp=[s.st_mtime_ns,s.st_size],width=300,height=100)
  (folder/'manifest86.json').write_text(json.dumps(dict(format=1,records={m.key(self.portal,row):record})))
  with mock.patch('logo_manifest86.location',return_value=(backend,str(folder/'manifest86.json'))):
   self.assertEqual(m.read(self.portal,[row]),{'0':str(file)})
   self.assertEqual(m.read(dict(self.portal,xc_user='different'),[row]),{})
   self.assertEqual(m.read(self.portal,[dict(row,stream_icon='https://example.org/changed.png')]),{})
   file.write_bytes(b'changed');self.assertEqual(m.read(self.portal,[row]),{})
 def test_reserve_block_never_downloads_or_claims_persistence(self):
  module=importlib.import_module('logo_manifest86');module._due.clear()
  with mock.patch('art_storage.check',side_effect=OSError('RESERVE_BLOCKED')),mock.patch('programme_transport77.verified',side_effect=AssertionError('network')):
   self.assertEqual(module.prepare(self.portal,self.rows[:2]),'EXTERNAL_UNAVAILABLE')
 def test_media_admission_after_identity_does_not_need_hero_image(self):
  m=importlib.import_module('home_schedule75');m._window().setProperty('XCMate.Home86.IdentityReady','true');m._window().setProperty('XCMate.Home86.Profile',__import__('epg_handoff63').profile_scope())
  with mock.patch('home_schedule75.applicable',return_value=True),mock.patch('home_schedule75._read',return_value={'phase':0}):
   self.assertTrue(m.allowed('vod',self.portal));self.assertTrue(m.allowed('series',self.portal))

 def test_existing_legacy_provider_logos_bootstrap_without_sql_or_new_decode(self):
  from artwork_backend import active_backend
  import hashlib
  m=importlib.import_module('logo_manifest86');backend=active_backend('media');path=Path(backend.resolve_target(hashlib.sha256(m.source(self.rows[0]).encode()).hexdigest()))
  path.parent.mkdir(parents=True,exist_ok=True)
  from PIL import Image
  Image.new('RGB',(120,60),(20,90,150)).save(path,format='PNG')
  with mock.patch('sqlite3.connect',side_effect=AssertionError('SQL')),mock.patch('media_sources43.validate_image',side_effect=AssertionError('decode on directory')):
   self.assertEqual(m.read(self.portal,self.rows[:1])['0'],str(path))
  self.assertEqual(m.read(self.portal,self.rows[:1],with_fallback=False),{})

 def test_legacy_source_retains_its_start_station_pin_without_changing_home50_order(self):
  from types import SimpleNamespace
  m=importlib.import_module('widget_home50');items=[dict(props={'XCMate.MediaId':str(i)}) for i in range(88)];portal=dict(self.portal,start_stream_id='37')
  ordered=m.ordered(SimpleNamespace(_params={}),portal,items)
  self.assertEqual(ordered[0]['props']['XCMate.MediaId'],'37');self.assertEqual(len(ordered),88);self.assertEqual(len({v['props']['XCMate.MediaId'] for v in ordered}),88)
  self.assertEqual(m.ordered(SimpleNamespace(_params={'home50':'1'}),portal,items),items)

 def test_live_status_reports_pending_then_hides_only_after_verified_readiness(self):
  m=__import__('home_status86');w=m.window();scope=__import__('epg_handoff63').profile_scope()
  w.setProperty('XCMate.Home86.Rail',json.dumps(dict(profile=scope,pid='p',total=88,local=88,first_at=time.monotonic())))
  with mock.patch('xbmc.getSkinDir',create=True,return_value='skin.titan.bingie.mod'),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000):
   m.observe();self.assertEqual(w.getProperty('XCMate.Home86.State'),'READY_PARTIAL');self.assertTrue(w.getProperty('XCMate.Home86.Text'))
   w.setProperty('XCMate.Hero63.Active','A');w.setProperty('XCMate.Hero63.A.Title','Verified local EPG');w.setProperty('XCMate.Hero63.A.Kind86','hero_backdrop')
   # .87 requires the exact native directory generation, not count alone.
   m.observe();self.assertEqual(w.getProperty('XCMate.Home86.State'),'READY_PARTIAL')
   runtime=__import__('widget_runtime79');runtime._plans[('p','live')]=dict(ids=[2510],slot='fixture87.directory',scope=scope,at=time.monotonic())
   w.setProperty('fixture87.directory',json.dumps(dict(tag='a'*64,count=88)))
   with mock.patch('xbmc.getInfoLabel',side_effect=lambda label:'88' if label.endswith('.NumItems') else 'a'*64),mock.patch('xbmc.getCondVisibility',return_value=True):m.observe()
   self.assertEqual(w.getProperty('XCMate.Home86.State'),'REFERENCE_READY');self.assertEqual(w.getProperty('XCMate.Home86.Text'),'')
 def test_missing_artwork_ends_in_static_diagnostic_not_endless_loading(self):
  m=__import__('home_status86');w=m.window();scope=__import__('epg_handoff63').profile_scope()
  w.setProperty('XCMate.Home86.Rail',json.dumps(dict(profile=scope,pid='p',total=88,local=0,first_at=time.monotonic()-61)))
  with mock.patch('xbmc.getSkinDir',create=True,return_value='skin.titan.bingie.mod'),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000):m.observe()
  self.assertEqual(w.getProperty('XCMate.Home86.State'),'ERROR');self.assertIn('88',w.getProperty('XCMate.Home86.Text'))

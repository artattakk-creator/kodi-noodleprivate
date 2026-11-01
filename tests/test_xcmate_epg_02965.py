"""Stored test events, real SQLite contention and RAM-first identity checks."""
import importlib,sqlite3,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class EPG65(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.mappings={}
  patch=mock.patch('epg_sources.configuration',side_effect=lambda pid:dict(mappings=self.mappings,sources=[]));patch.start();self.addCleanup(patch.stop)
  self.local=importlib.import_module('local_epg');self.store=importlib.import_module('guide_store')
  names=('DMAX','WELT','VOX','Nitro')
  self.channels=[dict(sid=str(i),stream_id=str(i),name=name,epg_channel_id='fixture.'+str(i)) for i,name in enumerate(names,1)]
  events={row['epg_channel_id']:[dict(name='Stored fixture '+row['name'],channel=row['epg_channel_id'],start_timestamp=self.now-60,stop_timestamp=self.now+600),dict(name='Next fixture '+row['name'],channel=row['epg_channel_id'],start_timestamp=self.now+600,stop_timestamp=self.now+1200)] for row in self.channels}
  self.store.import_cache('p',events,'epg65',now=self.now,trusted_feed=True)
 def test_warm_home_uses_same_valid_snapshot_without_sql_or_http(self):
  expected=self.local.now_next('p',self.channels,{},now=self.now)
  with mock.patch('sqlite3.connect',side_effect=AssertionError('WARM_WIDGET_SQL')),mock.patch('urllib.request.urlopen',side_effect=AssertionError('WARM_WIDGET_HTTP')):
   got=importlib.import_module('widget_group46')._infos63(self.portal,self.channels)
  for row in self.channels:
   sid=row['sid'];self.assertEqual(got[sid]['now'],expected[sid]['now']);self.assertEqual(got[sid]['next'],expected[sid]['next']);self.assertEqual(got[sid]['programme_key47'],expected[sid]['programme_key47'])
 def test_mapping_change_rejects_warm_sender_and_resolves_current_manual_channel(self):
  self.local.now_next('p',self.channels,{},now=self.now)
  self.mappings['1']='fixture.3'
  value=importlib.import_module('widget_group46')._infos63(self.portal,self.channels)['1']
  self.assertEqual(value['now'],'Stored fixture VOX');self.assertEqual(value['mapping'],'MANUAL')
 def test_same_sid_on_another_portal_never_reuses_old_programme(self):
  self.local.now_next('p',self.channels,{},now=self.now)
  got=importlib.import_module('widget_group46')._infos63(dict(self.portal,id='other'),self.channels)
  self.assertFalse(any(row.get('now') for row in got.values()))
 def test_expensive_metadata_cannot_erase_already_read_text_for_other_channels(self):
  clock=[100.];calls=[]
  def metadata(pid,cid,values,*args,**kwargs):
   calls.append(cid);clock[0]+=.6;return values
  with mock.patch('local_epg.time.monotonic',side_effect=lambda:clock[0]),mock.patch('programme_flow48.enrich',side_effect=metadata):
   view=self.local.window('p',self.channels,{},self.now,self.now+3600,budget=.4,text_only65=True)
  self.assertIsNotNone(view);self.assertEqual(len(calls),1)
  for row in self.channels:self.assertEqual(view[row['epg_channel_id']][0]['name'],'Stored fixture '+row['name'])
 def test_sqlite_exclusive_contention_is_bounded_and_warm_handoff_remains_usable(self):
  self.local.now_next('p',self.channels,{},now=self.now)
  lock=sqlite3.connect(self.store.path());lock.execute('PRAGMA journal_mode=DELETE');lock.execute('BEGIN EXCLUSIVE')
  try:
   started=time.monotonic();self.assertIsNone(self.local.window('p',self.channels,{},self.now,self.now+3600,budget=.1))
   self.assertLess(time.monotonic()-started,1.)
   with mock.patch('sqlite3.connect',side_effect=AssertionError('WARM_CONTENTION_SQL')):
    got=importlib.import_module('widget_group46')._infos63(self.portal,self.channels)
   self.assertEqual(got['2']['now'],'Stored fixture WELT')
  finally:lock.rollback();lock.close()
 def test_live_worker_does_not_reload_large_compatibility_cache_after_master_budget_failure(self):
  self.local.now_next('p',self.channels,{},now=self.now)
  snapshot=importlib.import_module('tv_data').GuideSnapshot(self.portal,None,initial_sid='2')
  wanted=types.SimpleNamespace(extra=dict(stream_id='2',epg_channel_id='fixture.2'),tvg_id='fixture.2')
  snapshot.request([wanted])
  with mock.patch('guide_viewport.cache',return_value=None),mock.patch('epg.load_cache',side_effect=AssertionError('CONTENTION_FULL_RELOAD')),mock.patch('guide_store.events',side_effect=AssertionError('CONTENTION_SECOND_POINT_READ')):
   snapshot.refresh()
  self.assertEqual(snapshot.get('2',now=self.now)['now'],'Stored fixture WELT')

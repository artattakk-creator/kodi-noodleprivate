"""Actual SQLite groups/ordering with fake Kodi, never Android acceptance."""
import importlib,sqlite3,time,unittest
from concurrent.futures import Future
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture

class Groups96(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.m=importlib.import_module('live_catalog46')
  self.index.import_group('p','live','b',[dict(stream_id=str(100+i),name='Target '+str(i),category_id='b') for i in range(137)])
 def test_target_group_does_not_require_unrelated_enabled_group_index(self):
  import group_selection
  group_selection.save('p',['a','b','not-imported'],'live')
  receipt={};result=self.m.read(self.portal,only='b',receipt94=receipt)
  self.assertIsNotNone(result);self.assertEqual(len(result[1]),137);self.assertTrue(receipt['generation'])
 def test_target_group_survives_slow_state_reads_without_widget_global_budget(self):
  from widget_data41 import WidgetReader
  real=WidgetReader._query
  def slow(reader,*a,**k):time.sleep(.28);return real(reader,*a,**k)
  with mock.patch.object(WidgetReader,'_query',slow):self.assertEqual(len(self.m.read(self.portal,only='b')[1]),137)
 def test_stale_selected_group_cannot_replace_new_selection_index(self):
  m=importlib.import_module('live_group93');base=object();new=object();future=Future()
  future.set_result(dict(pid94='p',base_index93=base,channels=['OLD_A'],merged_channels93=['OLD_A'],merged_index93=new))
  nav=SimpleNamespace(portal=self.portal,xc=self.client,category_id='b',enabled={'a','b'},index=base,channels=['CURRENT_B'],_group_task93=('a',future))
  with mock.patch.object(m._slots,'acquire',return_value=False):m.rows(nav)
  self.assertIs(nav.index,base);self.assertEqual(nav.channels,['CURRENT_B'])
 def nav(self):
  return SimpleNamespace(portal=self.portal,xc=self.client,category_id='b',enabled={'a','b'},index=None,channels=[])
 def test_busy_retries_are_bounded_and_keep_lastgood_rows(self):
  m=importlib.import_module('live_group93');nav=self.nav();nav._group_rows93={'b':['LAST_GOOD']};m.selected(nav)
  for attempt in (1,2,3):
   future=Future();future.set_exception(importlib.import_module('live_target96').failure('SQLITE_BUSY'))
   nav._group_task93=('b',future);nav._group_attempts96={'b':attempt}
   with mock.patch.object(m._slots,'acquire',return_value=False):self.assertEqual(m.rows(nav),['LAST_GOOD'])
   nav._group_due96['b']=0
  self.assertEqual(m.rows(nav),['LAST_GOOD']);self.assertEqual(m.state(nav),'GROUP_RETRY_EXHAUSTED')
  self.assertFalse(m.refresh_due(nav))
 def test_catalog_generation_change_rearms_exhausted_group_without_new_remote_action(self):
  m=importlib.import_module('live_group93');nav=self.nav();m.selected(nav)
  nav._group_attempts96={'b':3};nav._group_catalog_token96='old'
  with mock.patch('live_warm68.token',return_value='new'):self.assertTrue(m.refresh_due(nav))
  self.assertEqual(nav._group_attempts96['b'],0)
 def test_cached_empty_is_not_published_as_verified_empty_while_probe_pending(self):
  m=importlib.import_module('live_group93');nav=self.nav();nav._group_rows93={'b':[]};m.selected(nav)
  with mock.patch.object(m.threading,'Thread'):
   # A held worker slot is returned because the mocked thread never runs.
   try:self.assertIsNone(m.rows(nav))
   finally:m._slots.release()

"""Mixed-batch backoff and exact XMLTV IDs, no fuzzy station matching."""
import importlib,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class EPG79(Fixture,unittest.TestCase):
 def setUp(self):super().setUp();self.m=importlib.import_module('epg_poll79');self.a=dict(sid='1',name='Station',epg_channel_id='xml');self.b=dict(sid='2',name='Other',epg_channel_id='other');self.now=time.time()
 def test_missing_channel_backoff_survives_different_focus_batch(self):
  no=dict(now='',next='',next_start=0);self.m.remember('p',[self.a],{},self.now,True,{'1':no})
  parked,todo=self.m.select('p',[self.b,self.a],{},self.now,True);self.assertEqual(parked,{'1':no});self.assertEqual(todo,[self.b])
 def test_manual_binding_and_committed_guide_revision_invalidate_immediately(self):
  self.m.remember('p',[self.a],{},self.now,True,{'1':dict(now='',next='',next_start=0)})
  self.assertEqual(self.m.select('p',[self.a],{'1':'manual'},self.now,True)[1],[self.a])
  with mock.patch('epg_status.revision',return_value='new-guide'):self.assertEqual(self.m.select('p',[self.a],{},self.now,True)[1],[self.a])
 def test_positive_event_boundary_never_reuses_previous_programme(self):
  info=dict(now='Current',start=self.now-30,stop=self.now+1)
  self.m.remember('p',[self.a],{},self.now,True,{'1':info});self.assertEqual(self.m.select('p',[self.a],{},self.now+2,True)[1],[self.a])
 def test_next_only_event_is_revisited_at_actual_start(self):
  self.m.remember('p',[self.a],{},self.now,True,{'1':dict(now='',next='Next',next_start=self.now+1)})
  self.assertEqual(self.m.select('p',[self.a],{},self.now+2,True)[1],[self.a])
 def test_tvg_xmltv_exact_ids_are_preserved_and_manual_mapping_is_exclusive(self):
  m=importlib.import_module('local_epg');self.assertEqual(m.channel_keys(dict(sid='1',tvg_id='exact.xml'),{}),('1',['1','exact.xml']))
  self.assertEqual(m.channel_keys(dict(sid='1',tvg_id='exact.xml'),{'1':'manual'}),('1',['manual']))
 def test_missing_cache_is_bounded_and_not_a_permanent_negative(self):
  self.m.remember('p',[self.a],{},self.now,True,{'1':dict(now='',next='',next_start=0)})
  with mock.patch('time.monotonic',return_value=time.monotonic()+61):self.assertEqual(self.m.select('p',[self.a],{},self.now,True)[1],[self.a])

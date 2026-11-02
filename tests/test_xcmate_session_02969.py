"""Bounded event outcomes survive churn; retry persistence without API replay."""
import importlib,sys,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Session69(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  for name in ('programme_session69','programme_writes69'):sys.modules.pop(name,None)
  self.session=importlib.import_module('programme_session69')
 def event(self,index=1):
  from programme_events46 import describe
  return describe(self.portal,dict(sid=str(index),name='Synthetic'),dict(title='Synthetic Film '+str(index),start=self.now-30,stop=self.now+1800,genre='Spielfilm',year=2024),'a',('revision',1))
 def test_667_distinct_events_do_not_replay_first_outcome(self):
  for i in range(667):self.session.remember(self.event(i),dict(source='placeholder',code='NO_MATCH',until=time.time()+300))
  self.assertIsNotNone(self.session.get(self.event(0)));self.assertLessEqual(len(self.session._values),128)
  self.assertLessEqual(len(self.session._outcomes),1024);self.assertLessEqual(self.session._outcome_bytes,4*1024*1024)
 def test_volatile_metadata_persists_after_recovery_without_matching(self):
  event=self.event();self.session.remember(event,dict(source='placeholder',code='NO_MATCH',until=time.time()+300))
  with mock.patch('programme_session69.time.time',return_value=time.time()+6),mock.patch('programme_writes69.permit',return_value=True),mock.patch('programme_index46.publish_result69',return_value=True),mock.patch('programme_requests68.completed') as done:
   self.assertTrue(self.session.flush());done.assert_called_once()
  self.assertTrue(self.session.get(event)['persisted69'])
 def test_blocked_write_flush_performs_no_sqlite_write(self):
  self.session.remember(self.event(),dict(source='placeholder',code='NO_MATCH',until=time.time()+300))
  with mock.patch('programme_writes69.permit',return_value=False),mock.patch('programme_index46.publish_result69') as writer:
   self.assertFalse(self.session.flush());writer.assert_not_called()
 def test_epg_read_timeout_has_separate_numeric_diagnostic(self):
  import sqlite3,epg_read69
  error=sqlite3.OperationalError('synthetic');error.sqlite_errorname='SQLITE_INTERRUPT'
  epg_read69.record(error,'p','1')
  self.assertEqual(epg_read69.last('p','1'),'EPG_READ_TIMEOUT')
 def test_news_sport_do_not_enter_tmdb_helper_fallback(self):
  from programme_sources57 import attempts
  for genre in ('Nachrichten','Sport','Wetter'):
   self.assertEqual(list(attempts(dict(title='Synthetic',genre=genre))),[])
 def test_provider_reference_rejects_credentials_and_private_hosts(self):
  from widget_assets69 import safe
  for uri in ('https://name:pass@images.example.org/a.jpg','http://images.example.org/a.jpg','https://127.0.0.1/a.jpg','https://images.example.org/a.jpg?token=SECRET','https://images.example.org/SECRET/a.jpg'):
   self.assertFalse(safe(self.portal,uri))
  self.assertTrue(safe(self.portal,'https://images.example.org/cover.jpg'))
 def test_generic_placeholder_is_not_renderable(self):
  from widget_assets69 import renderable
  for uri in ('','/synthetic/resources/media/vod.png','/synthetic/resources/media/series.png','/synthetic/resources/media/programme46/tv.png'):self.assertFalse(renderable(uri))
  self.assertTrue(renderable('https://images.example.org/cover.jpg'))

 def test_dynamic_provider_refs_work_without_programme_db_and_expire(self):
  import hashlib,json
  from widget_assets69 import identity,_slot,read
  from artwork_visible import KODI_OPTIONS
  from epg_handoff63 import profile_scope
  row=dict(sid='1',name='Synthetic',cover='https://images.example.org/cover.jpg')
  # Same approval payload that the worker publishes, then a GUI-only read.
  from programme_assets47 import sources
  for role,source in sources(row,provider_only=True).items():
   key=identity(self.portal,'vod',row,role,source)
   self.properties[_slot(key)]=json.dumps(dict(key=key,profile=profile_scope(),uri=source+KODI_OPTIONS,until=time.time()+20))
  with mock.patch('artwork_config.persistent',return_value=False),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI_SQL')),mock.patch('builtins.open',side_effect=AssertionError('GUI_IO')):
   refs=read(self.portal,'vod',[row])
  self.assertTrue(refs.get('1'));self.assertTrue(all(uri.startswith('https://images.example.org/') for uri in refs['1'].values()))
  with mock.patch('widget_assets69.time.time',return_value=time.time()+31),mock.patch('artwork_config.persistent',return_value=False):self.assertEqual(read(self.portal,'vod',[row]),{})
 def test_dynamic_provider_refs_are_bound_to_portal_and_credentials(self):
  from widget_assets69 import identity
  row=dict(sid='1')
  uri='https://images.example.org/cover.jpg'
  first=identity(self.portal,'vod',row,'poster',uri)
  self.assertNotEqual(first,identity(dict(self.portal,id='other'),'vod',row,'poster',uri))
  self.assertNotEqual(first,identity(dict(self.portal,xc_pass='OTHER'),'vod',row,'poster',uri))

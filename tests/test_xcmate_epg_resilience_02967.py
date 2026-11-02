"""Reproduce actual .66 data loss with committed local guide, no device/network."""
import importlib,sqlite3,unittest
from unittest import mock
import test_xcmate_epg_02952 as data52
class Resilience67(unittest.TestCase):
 def setUp(self):
  self.fixture=data52.EPG52();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
  self.fixture.put('a',[self.fixture.event(title='Committed programme')])
 def test_optional_schema_failure_preserves_full_guide_text(self):
  from local_epg import window
  m=self.fixture
  with mock.patch('programme_flow48.enrich',side_effect=sqlite3.OperationalError('synthetic private SQL text')):
   view=window('p',[m.channel],{},m.now,m.now+3600)
  self.assertIsNotNone(view);self.assertEqual(view['a'][0]['name'],'Committed programme')
 def test_optional_schema_failure_preserves_display_text(self):
  from local_epg import now_next
  m=self.fixture
  with mock.patch('programme_flow48.enrich',side_effect=sqlite3.OperationalError('synthetic unrelated table unavailable')):
   info=now_next('p',[m.channel],{},m.now,display_only65=True)['1']
  self.assertEqual(info['now'],'Committed programme')
 def test_metadata_failure_never_logs_exception_sql_or_credentials(self):
  import epg_resilience67
  import sys
  with mock.patch.object(sys.modules['xbmc'],'log',create=True) as log:
   epg_resilience67._seen.clear()
   self.assertEqual(epg_resilience67.optional('private-portal','private-sid',[1],lambda:(_ for _ in ()).throw(sqlite3.OperationalError('https://secret-user:secret-pass@private.invalid SELECT private'))),[1])
  output=str(log.call_args_list)
  for secret in ('secret-user','secret-pass','private.invalid','SELECT private','private-portal','private-sid'):self.assertNotIn(secret,output)
 def test_expired_alias_does_not_mask_current_provider_programme(self):
  from epg_views import resolve_guide
  m=self.fixture
  cache={'1':[dict(name='Expired',start_timestamp=m.now-1800,stop_timestamp=m.now-900)],'provider':[dict(name='Provider current',start_timestamp=m.now-60,stop_timestamp=m.now+1800)]}
  result=resolve_guide(cache,'provider','1',m.now,mappings={})
  self.assertEqual(result['now'],'Provider current');self.assertEqual(result['mapping'],'PROVIDER_ID')
 def test_explicit_mapping_is_not_replaced_by_provider_fallback(self):
  from epg_views import resolve_guide
  m=self.fixture
  cache={'1':[dict(name='Expired',start_timestamp=m.now-1800,stop_timestamp=m.now-900)],'provider':[dict(name='Provider current',start_timestamp=m.now-60,stop_timestamp=m.now+1800)]}
  result=resolve_guide(cache,'provider','1',m.now,mappings={'1':'1'})
  self.assertEqual(result['now'],'');self.assertEqual(result['mapping'],'MANUAL')
 def test_valid_stream_alias_retains_priority_over_provider(self):
  from epg_views import resolve_guide
  m=self.fixture
  event=dict(start_timestamp=m.now-60,stop_timestamp=m.now+1800)
  result=resolve_guide({'1':[dict(event,name='Verified alias')],'provider':[dict(event,name='Provider alternative')]},'provider','1',m.now)
  self.assertEqual(result['now'],'Verified alias');self.assertEqual(result['mapping'],'STREAM_ALIAS')

 def test_primary_sql_failure_keeps_validated_lastgood_without_blessing_revision(self):
  from local_epg import now_next
  from epg_handoff63 import register,get
  m=self.fixture;before=now_next('p',[m.channel],{},m.now)
  register('p',('newer-known-guide',before['1']['snapshot_revision'][1]+1))
  self.assertIsNone(get('p','1',now=m.now,mappings={}))
  with mock.patch('local_epg.sqlite3.connect',side_effect=sqlite3.OperationalError('synthetic lock')):
   after=now_next('p',[m.channel],{},m.now)
  self.assertEqual(after['1']['now'],before['1']['now'])
  self.assertIsNone(get('p','1',now=m.now,mappings={}))
 def test_fallback_rejects_changed_manual_mapping(self):
  from local_epg import now_next
  from epg_fallback67 import window
  m=self.fixture;now_next('p',[m.channel],{},m.now)
  self.assertIsNone(window('p',[m.channel],{'1':'different'},m.now,m.now+3600,4))

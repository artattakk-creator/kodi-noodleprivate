"""Status lifetime, explicit retry and readable source failures, no private API."""
import importlib,json,sys,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class ArtStatus70(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  for name in ('programme_requests68','programme_urls55','programme_session69'):sys.modules.pop(name,None)
  self.b=importlib.import_module('programme_requests68');self.q=importlib.import_module('programme_urls55')
 def event(self):
  from programme_events46 import describe
  return describe(self.portal,dict(sid='1',name='Synthetic'),dict(title='Synthetic film',year=2024,genre='Spielfilm',start=self.now-60,stop=self.now+3600),'a',('revision',1))
 def art(self,event):
  candidate=dict(url='https://image.tmdb.org/t/p/w500/SYNTHETIC_ONLY.jpg',source='tmdb_movie',match='EXACT_TITLE_YEAR',attribution='TMDB')
  with mock.patch('programme_index46.publish_result69',return_value=False):
   return self.q.resolve(event,allow_lookup=True,url_mode69=True,match=lambda *a,**kw:candidate,check=mock.Mock())
 def test_verified_url_does_not_disappear_after_five_minutes(self):
  event=self.event();value=self.art(event);self.b.completed(event,value)
  with mock.patch('time.time',return_value=time.time()+360):
   self.assertEqual(self.b.result(event)['image'],value['image'])
 def test_negative_status_retains_its_actual_retry_lifetime(self):
  event=self.event();value=dict(source='placeholder',code='HELPER_TIMEOUT',until=time.time()+1800,policy69=__import__('programme_status70').policy())
  self.b.completed(event,value)
  with mock.patch('time.time',return_value=time.time()+360):self.assertEqual(self.b.result(event)['code'],'HELPER_TIMEOUT')
 def test_expired_or_wrong_profile_status_is_rejected(self):
  event=self.event();value=self.art(event);self.b.completed(event,value)
  with mock.patch('time.time',return_value=value['until']+1):self.assertFalse(self.b.result(event).get('image'))
  with mock.patch('programme_requests68.scope',return_value='different-profile'):self.assertFalse(self.b.result(event))
 def test_policy_change_invalidates_long_lived_negative(self):
  from programme_status70 import valid
  record=dict(at=time.time()-360,art=dict(until=time.time()+600,policy69='obsolete'))
  self.assertFalse(valid(record))
 def test_missing_ack_is_requested_not_not_scheduled(self):
  event=self.event();self.assertTrue(self.b.request(event,priority=True))
  self.assertEqual(self.b.result(event)['code'],'REQUESTED')
 def test_status_envelope_without_expiry_keeps_old_five_minute_bound(self):
  from programme_status70 import valid
  self.assertFalse(valid(dict(at=time.time()-360,art={})))
 def test_invalid_times_are_not_admitted(self):
  from programme_status70 import valid
  for at in (float('nan'),float('inf'),time.time()+10,'private'):
   self.assertFalse(valid(dict(at=at,art=dict(until=time.time()+900))))
 def test_explicit_retry_is_observed_without_consuming_marker(self):
  from programme_refresh63 import request
  from programme_status70 import retry
  event=self.event();old=dict(source='placeholder',code='HELPER_TIMEOUT',resolved_at55=time.time()-10)
  request()
  self.assertTrue(retry(event,old));self.assertTrue(retry(event,old))
  self.assertFalse(retry(event,dict(old,resolved_at55=time.time()+1)))
 def test_explicit_retry_reaches_resolver_despite_ram_negative(self):
  event=self.event();lookup=mock.Mock(return_value=None)
  with mock.patch('programme_index46.publish_result69',return_value=False):
   self.q.resolve(event,allow_lookup=True,url_mode69=True,match=lookup,check=mock.Mock())
   self.q.resolve(event,allow_lookup=True,url_mode69=True,match=lookup,check=mock.Mock())
   self.assertEqual(lookup.call_count,1)
   from programme_refresh63 import request
   request()
   self.q.resolve(event,allow_lookup=True,url_mode69=True,match=lookup,check=mock.Mock())
   self.q.resolve(event,allow_lookup=True,url_mode69=True,match=lookup,check=mock.Mock())
  self.assertEqual(lookup.call_count,2)
 def test_positive_and_rate_limit_results_are_not_manually_invalidated(self):
  from programme_refresh63 import request
  from programme_status70 import retry
  request();event=self.event()
  for value in (dict(source='tmdb_movie',code='READY'),dict(source='placeholder',code='HTTP_RATE_LIMIT')):
   self.assertFalse(retry(event,value))
 def test_error_is_not_described_as_a_pending_image_download(self):
  from programme_diagnostics59 import message
  value=dict(code='HELPER_TIMEOUT',source='placeholder',storage69='RAM_ONLY',storage_code69='SAFE_RESERVE_BLOCKED')
  text=message(self.event(),value)
  self.assertIn('nicht rechtzeitig',text);self.assertIn('kein gefundenes Bild',text)
  self.assertNotIn('Ergebnis für diese Sitzung vorgemerkt',text)
 def test_own_source_reason_survives_helper_failure(self):
  from programme_diagnostics59 import message
  value=dict(code='HELPER_BACKGROUND_UNAVAILABLE',source='placeholder',storage69='RAM_ONLY',sources70=[dict(source='tmdb',code='HTTP_AUTH'),dict(source='helper',code='HELPER_BACKGROUND_UNAVAILABLE')],lookup70=dict(own=True))
  self.assertIn('Zugriff abgewiesen',message(self.event(),value))
 def test_source_outcomes_never_publish_raw_error_or_url(self):
  from programme_outcomes70 import clean
  self.assertEqual(clean([dict(source='helper',code='SECRET https://private.invalid')]),[dict(source='helper',code='REMOTE_ERROR')])
  self.assertEqual(clean([dict(source='https://user:SECRET@private.invalid',code='FOUND')]),[])
 def test_disabled_own_lookup_is_explained_without_changing_settings(self):
  from programme_diagnostics59 import message
  value=dict(code='HELPER_TIMEOUT',lookup70=dict(own=False),source='placeholder')
  before=dict(self.options);self.assertIn('ausgeschaltet',message(self.event(),value));self.assertEqual(self.options,before)
 def test_gui_status_read_does_not_open_files_sql_or_network(self):
  event=self.event();value=self.art(event);self.b.completed(event,value)
  with mock.patch('builtins.open',side_effect=AssertionError('GUI_IO')),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI_SQL')),mock.patch('media_sources43.get',side_effect=AssertionError('GUI_HTTP')):
   self.assertEqual(self.b.result(event)['image'],value['image'])

 def test_legacy_helper_negative_is_lazily_rechecked_once(self):
  from programme_art46 import fingerprint
  event=self.event();legacy=dict(key=event['key'],fingerprint=fingerprint(event),url_version55=1,source='placeholder',code='HELPER_TIMEOUT',matching_policy57=1,source_policy57=[False,False],until=time.time()+21600,negative_scope68=__import__('programme_policy68').negative_scope(event))
  lookup=mock.Mock(return_value=dict(url='https://image.tmdb.org/t/p/w500/SYNTHETIC_ONLY.jpg',source='tmdb_movie',match='EXACT_TITLE_YEAR',attribution='TMDB'))
  with mock.patch('programme_index46.art',return_value=legacy),mock.patch('programme_index46.publish_result69',return_value=False):
   first=self.q.resolve(event,allow_lookup=True,url_mode69=True,match=lookup,check=mock.Mock())
   second=self.q.resolve(event,allow_lookup=True,url_mode69=True,match=lookup,check=mock.Mock())
  self.assertEqual(first['code'],'READY');self.assertEqual(first['image'],second['image']);self.assertEqual(lookup.call_count,1)

 def test_real_supplier_chain_keeps_own_api_reason_before_helper_error(self):
  from media_sources43 import SourceError
  from helper_rpc57 import Error
  self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_helper57=True,programme_catalog57=False)
  event=self.event()
  with mock.patch('programme_match46.candidate',side_effect=SourceError('HTTP_AUTH')),mock.patch('programme_tvmaze67.candidate',return_value=None),mock.patch('programme_helper57.lookup',side_effect=Error('HELPER_TIMEOUT')),mock.patch('programme_index46.publish_result69',return_value=False):
   value=self.q.resolve(event,allow_lookup=True,url_mode69=True,check=mock.Mock())
  self.assertIn(dict(source='tmdb',code='HTTP_AUTH'),value['sources70'])
  self.assertIn(dict(source='helper',code='HELPER_TIMEOUT'),value['sources70'])
  self.assertIn('Zugriff abgewiesen',__import__('programme_diagnostics59').message(event,value))

 def test_repeated_focus_does_not_reset_waiting_service_age(self):
  event=self.event()
  with mock.patch('time.time',return_value=1000):self.b.request(event)
  with mock.patch('time.time',return_value=1005):self.b.request(event)
  with mock.patch('time.time',return_value=1016):
   self.b.request(event);self.assertEqual(self.b.result(event)['code'],'WAITING_SERVICE')
 def test_supplier_trace_is_pseudonymized_and_fixed_code_only(self):
  import programme_outcomes70 as outcomes
  xbmc=sys.modules['xbmc']
  with mock.patch.object(xbmc,'log',create=True) as log,mock.patch.object(xbmc,'LOGINFO',1,create=True):
   outcomes.trace(self.event(),'tmdb','HTTP_AUTH')
  text=log.call_args.args[0]
  self.assertIn('source=tmdb code=HTTP_AUTH',text)
  for private in ('Synthetic film','SECRET','provider.invalid'):self.assertNotIn(private,text)

 def test_waiting_or_queued_request_does_not_hide_valid_previous_image(self):
  event=self.event();art=self.art(event)
  self.b.request(event)
  self.assertEqual(self.b.result(event,art)['image'],art['image'])
  self.assertEqual(self.b.result(event,art)['code'],'READY')
  self.b.status(event,'QUEUED')
  self.assertEqual(self.b.result(event,art)['code'],'READY')
 def test_pending_request_does_not_resurrect_wrong_event_image(self):
  event=self.event();art=self.art(event)
  other=dict(event,sid='different');self.b.request(other)
  self.assertEqual(self.b.result(other,art)['code'],'REQUESTED')

 def test_shared_rpc_error_does_not_misidentify_kodi_library_as_tmdb_helper(self):
  from programme_diagnostics59 import message
  value=dict(code='HELPER_BACKGROUND_UNAVAILABLE',source='placeholder',sources70=[dict(source='kodi',code='HELPER_BACKGROUND_UNAVAILABLE')])
  text=message(self.event(),value)
  self.assertIn('Kodi-Katalogabfrage',text);self.assertNotIn('TMDB Helper',text)

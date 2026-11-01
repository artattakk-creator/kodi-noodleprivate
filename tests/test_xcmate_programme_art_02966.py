"""Synthetic TMDB API/image fixtures: authenticated connection is not artwork proof."""
import importlib,io,json,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
class Artwork66(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_helper57=False,programme_catalog57=False)
  self.tv=importlib.import_module('programme_tv66');self.sources=importlib.import_module('media_sources43')
  self.event=dict(pid='p',sid='1',canonical='xml',title='MacGyver',genre='Krimiserie',description='Actual stored episode description',start=int(self.now-60),stop=int(self.now+1800))
  self.patch=mock.patch.object(self.sources,'tmdb_token',return_value='synthetic-test-secret');self.patch.start();self.addCleanup(self.patch.stop)
 def replies(self,year='2016',backdrop='/fixture.png'):
  return [dict(total_pages=1,total_results=1,results=[dict(id=66,name='MacGyver',original_name='MacGyver',first_air_date=year+'-01-01')]),dict(id=66,name='MacGyver',original_name='MacGyver',first_air_date=year+'-01-01',backdrop_path=backdrop)]
 def test_series_without_episode_numbers_gets_verified_series_art_with_label(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.replies()) as request:
   result=self.tv.candidate(self.event)
  self.assertEqual(result['source'],'tmdb_series');self.assertEqual(result['image_scope57'],'series_fallback')
  self.assertIn('kein Episodenbild',result['attribution']);self.assertEqual(request.call_count,2)
 def test_remakes_without_year_are_ambiguous_not_a_random_first_hit(self):
  data=self.replies()[0];data['results'].append(dict(id=85,name='MacGyver',first_air_date='1985-01-01'));data['total_results']=2
  with mock.patch('tmdb_connection60.request',return_value=data):
   with self.assertRaises(self.sources.SourceError) as error:self.tv.candidate(self.event)
  self.assertEqual(error.exception.code,'NO_MATCH_AMBIGUOUS')
 def test_proven_year_selects_correct_remake_and_verifies_independent_details(self):
  data=self.replies()[0];data['results'].append(dict(id=85,name='MacGyver',first_air_date='1985-01-01'));data['total_results']=2
  with mock.patch('tmdb_connection60.request',side_effect=[data,self.replies()[1]]):
   self.assertEqual(self.tv.candidate(dict(self.event,year=2016))['remote_id'],66)
 def test_conflicting_details_cannot_bind_another_series_image(self):
  values=self.replies();values[1]['id']=999
  with mock.patch('tmdb_connection60.request',side_effect=values):
   with self.assertRaises(self.sources.SourceError) as error:self.tv.candidate(self.event)
  self.assertEqual(error.exception.code,'NO_MATCH')
 def test_exact_series_without_backdrop_is_no_artwork_not_auth_failure(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.replies(backdrop=None)):
   with self.assertRaises(self.sources.SourceError) as error:self.tv.candidate(self.event)
  self.assertEqual(error.exception.code,'NO_ARTWORK')
 def test_incomplete_search_page_cannot_prove_unique_match(self):
  values=self.replies();values[0]['total_pages']=2
  with mock.patch('tmdb_connection60.request',return_value=values[0]):
   with self.assertRaises(self.sources.SourceError) as error:self.tv.candidate(self.event)
  self.assertEqual(error.exception.code,'NO_MATCH_AMBIGUOUS')
 def test_news_and_sports_never_receive_a_same_named_series_poster(self):
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('NO_NEWS_LOOKUP')):
   for genre in ('Nachrichten','Sport','Talk'):self.assertIsNone(self.tv.candidate(dict(self.event,genre=genre)))
 def test_disabled_opt_in_does_not_change_settings_or_call_network(self):
  self.options['programme_tmdb46']=False;before=dict(self.options)
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('NO_DISABLED_LOOKUP')):self.assertIsNone(self.tv.candidate(self.event))
  self.assertEqual(self.options,before)
 def test_parenthetical_year_is_only_used_when_not_conflicting(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.replies()):
   self.assertEqual(self.tv.candidate(dict(self.event,title='MacGyver (2016)'))['matched_year56'],2016)
  with self.assertRaises(self.sources.SourceError):self.tv.candidate(dict(self.event,title='MacGyver (2016)',year=1985))
 def test_unsafe_or_missing_artwork_is_not_materialized(self):
  values=self.replies(backdrop='https://private.invalid/x')
  with mock.patch('tmdb_connection60.request',side_effect=values):
   with self.assertRaises(self.sources.SourceError):self.tv.candidate(self.event)
 def test_tv_lookup_download_cache_restart_and_widget_share_exact_event_image(self):
  from PIL import Image
  import programme_art46 as art
  from programme_urls55 import resolve
  from programme_events46 import describe
  from programme_widgets46 import decorate
  event=describe(self.portal,dict(sid='1',name='NITRO fixture'),dict(self.event,year=2016),'xml')
  event.update(genre='Krimiserie',year=2016)
  Path(art.root()).mkdir(parents=True,exist_ok=True)
  image=io.BytesIO();Image.new('RGB',(160,90),(25,90,150)).save(image,'PNG')
  with mock.patch('tmdb_connection60.request',side_effect=self.replies()),mock.patch.object(self.sources,'get',return_value=image.getvalue()),mock.patch.object(art,'space'):
   result=resolve(event,allow_lookup=True,match=self.tv.candidate,local_image63=True)
  self.assertEqual(result['code'],'READY');self.assertTrue(Path(result['image']).is_file())
  with art._lock:art._memory.clear()
  with mock.patch.object(self.sources,'get',side_effect=AssertionError('CACHE_MUST_SURVIVE')):
   cached=art.indexed(event,verify=True)
  self.assertEqual(cached['image'],result['image']);self.assertEqual(cached['sha256'],result['sha256'])
  self.assertEqual(cached['image_scope57'],'series_fallback')
 def test_readable_status_distinguishes_match_artwork_and_cache_failures(self):
  from programme_diagnostics59 import message
  for code,word in [('NO_MATCH_AMBIGUOUS','Mehrere'),('NO_ARTWORK','kein geeignetes'),('CACHE_IO_ERROR','Bildspeicherung'),('GUI_NOT_UPDATED','Kodi-Ausgabe')]:
   self.assertIn(word,message(self.event,dict(code=code,source='placeholder')))

 def test_failure_of_both_persistent_stores_is_cache_error_and_preserves_image_bytes(self):
  import hashlib
  from PIL import Image
  import programme_art46 as art
  from programme_events46 import describe
  from programme_urls55 import resolve
  event=describe(self.portal,dict(sid='1',name='Synthetic NITRO'),dict(self.event,year=2016),'xml');event.update(genre='Krimiserie',year=2016)
  out=io.BytesIO();Image.new('RGB',(160,90),(25,90,150)).save(out,'PNG');data=out.getvalue()
  Path(art.root()).mkdir(parents=True,exist_ok=True)
  image=Path(art.root())/('blob46-'+hashlib.sha256(data).hexdigest()+'.png');image.write_bytes(data)
  with mock.patch('tmdb_connection60.request',side_effect=self.replies()),mock.patch.object(self.sources,'get',return_value=data),mock.patch.object(art,'space'),mock.patch('programme_index46.art',return_value=None),mock.patch.object(art,'atomic',side_effect=OSError(13,'synthetic cache denied')):
   result=resolve(event,allow_lookup=True,match=self.tv.candidate,local_image63=True)
  self.assertEqual(result['code'],'CACHE_ERROR');self.assertEqual(image.read_bytes(),data)
  self.assertEqual(art.peek(event)['code'],'CACHE_ERROR')
 def test_match_and_fetch_failure_have_distinct_fixed_evidence_stages(self):
  from PIL import Image
  import programme_art46 as art
  from programme_events46 import describe
  from programme_urls55 import resolve
  event=describe(self.portal,dict(sid='1',name='Synthetic NITRO'),dict(self.event,year=2016),'xml');event.update(genre='Krimiserie',year=2016)
  Path(art.root()).mkdir(parents=True,exist_ok=True)
  with mock.patch('tmdb_connection60.request',side_effect=self.replies()),mock.patch.object(self.sources,'get',side_effect=self.sources.SourceError('HTTP_NOT_FOUND')),mock.patch.object(art,'space'),mock.patch('programme_flow48.trace') as trace:
   result=resolve(event,allow_lookup=True,match=self.tv.candidate,local_image63=True)
  self.assertEqual(result['code'],'HTTP_NOT_FOUND')
  self.assertTrue(any(call.args[0]=='MATCH' and call.args[2]=='READY' for call in trace.call_args_list))
  self.assertTrue(any(call.args[0]=='FETCH' and call.args[2]=='HTTP_NOT_FOUND' for call in trace.call_args_list))

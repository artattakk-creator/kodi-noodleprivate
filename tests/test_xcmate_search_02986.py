"""D: manual research remains usable without EPG; save requires current scope."""
import importlib,json,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Search86(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_tvmaze67=True,tmdb_read_token43='SYNTHETIC_86_NOT_A_TOKEN');self.m=importlib.import_module('work_search86')
  self.tv=dict(id=1980,name='Charmed',original_name='Charmed',first_air_date='1998-10-07',origin_country=['US'],poster_path='/poster.png',backdrop_path='/backdrop.png',overview='Original series')
  self.movie=dict(id=200,title='Monk: The Movie',original_title='Monk: The Movie',release_date='2023-01-01',poster_path='/movie.png',overview='Movie fixture')
 def reply(self,url,**kwargs):
  if '/search/' in url:return dict(page=1,total_pages=1,results=[self.movie] if '/movie?' in url else [self.tv])
  return self.movie if '/movie/' in url else self.tv
 def test_charmed_and_monk_manual_search_do_not_require_epg_genre_or_episode(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.reply),mock.patch('programme_urls55.probe',side_effect=OSError('fixture no network')):
   for query in ('Charmed – Zauberhafte Hexen','Charmed','Monk'):
    result=self.m.search(query);self.assertEqual(result['code'],'READY');self.assertEqual(result['rows'][0]['year'],1998)
 def test_movie_identity_is_typed_separately_from_tv(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.reply),mock.patch('programme_urls55.probe',side_effect=OSError()):result=self.m.search('Monk: The Movie',kind='movie')
  self.assertEqual(result['rows'][0]['media_type86'],'movie');self.assertEqual(result['rows'][0]['id'],200)
 def test_zero_results_is_distinct_and_editable(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(page=1,total_pages=0,results=[])):result=self.m.search('Unknown exact work')
  self.assertEqual(result['code'],'ZERO_RESULTS')
 def test_disabled_source_never_makes_network_request(self):
  self.options['programme_tmdb_optout77']=True
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('network')):
   with self.assertRaisesRegex(Exception,'SOURCE_DISABLED'):self.m.search('Monk')
 def test_independent_identity_mismatch_is_not_accepted(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(self.tv,id=999)):
   with self.assertRaisesRegex(Exception,'CANDIDATES_REJECTED'):self.m.details(1980,'tv')
 def test_search_intent_requires_no_epg_read_and_reports_zero_results(self):
  m=importlib.import_module('work_requests86');event=dict(pid='p',sid='1',title='Monk')
  nonce=m.request(event,query='Monk')
  with mock.patch('programme_events46.load',side_effect=AssertionError('EPG gate')),mock.patch('work_search86.search',return_value=dict(code='ZERO_RESULTS',rows=[])):
   m.drain()
  self.assertEqual(m.result(nonce)['code'],'ZERO_RESULTS');m.cancel(nonce)
 def test_missing_epg_prevents_false_saved_and_preserves_old_mapping(self):
  m=importlib.import_module('work_requests86');event=dict(pid='p',sid='1',title='Monk',start=self.now,stop=self.now+3600)
  with mock.patch('work_requests86.authoritative',side_effect=__import__('media_sources43').SourceError('EPG_REVISION_CHANGED')),mock.patch('programme_mapping85.set_mapping',side_effect=AssertionError('write')):
   nonce=m.request(event,'save',action='automatic');m.drain()
  self.assertEqual(m.result(nonce)['code'],'EPG_REVISION_CHANGED')
 def test_cancelled_request_does_not_publish_or_save(self):
  m=importlib.import_module('work_requests86');nonce=m.request(dict(pid='p',sid='1',title='Monk'),query='Monk');m.cancel(nonce)
  with mock.patch('work_search86.search',side_effect=AssertionError('cancelled')):m.drain()
  self.assertIsNone(m.result(nonce))
 def test_movie_mapping_is_persistent_legacy_tv_mapping_stays_compatible(self):
  m=importlib.import_module('programme_mapping85');event=dict(pid='p',sid='1',canonical='xml',title='Monk',start=self.now,stop=self.now+3600)
  m.set_mapping(event,dict(source='tmdb',id=200,verified85=True,year=2023,media_type86='movie'))
  self.assertEqual(m.current(event)['media_type86'],'movie');m.reload();self.assertEqual(m.current(event)['id'],200)
 def test_selected_candidate_url_is_never_trusted_for_save(self):
  m=importlib.import_module('work_requests86');event=dict(pid='p',sid='1',title='Monk',media_kind86='vod')
  candidate=dict(source='tmdb',id=200,media_type86='movie',year=2023,title='Monk: The Movie',url='http://127.0.0.1/credentials')
  decoded=dict(_body81=b'synthetic fully verified image')
  with mock.patch('work_requests86.authoritative',return_value=event),mock.patch('work_search86.details',return_value=dict(candidate,poster='https://image.tmdb.org/t/p/w500/safe.png')),mock.patch('programme_urls55.probe',return_value=decoded) as probe,mock.patch('media_overrides43.save',return_value=True):
   self.assertTrue(m.save(event,dict(candidate=candidate),m.binding(event)))
  self.assertEqual(probe.call_args.args[0],'https://image.tmdb.org/t/p/w500/safe.png')

 def test_identical_numeric_tv_movie_ids_cannot_reuse_tv_candidate_for_movie_mapping(self):
  e=dict(pid='p',sid='1',canonical='xml',title='Monk',start=self.now,stop=self.now+1800,key='collision')
  maps=importlib.import_module('programme_mapping85');engine=importlib.import_module('programme_candidates85')
  maps.set_mapping(e,dict(source='tmdb',id=200,year=2023,media_type86='movie',verified85=True))
  wrong=dict(id=200,source='tmdb',title='A TV work',year=2023,role='backdrop',url='https://image.tmdb.org/t/p/w500/tv.png',verified85=True)
  engine.remember(e,[wrong])
  movie=dict(id=200,source='tmdb',title='Monk: The Movie',year=2023,media_type86='movie',role='poster',url='https://image.tmdb.org/t/p/w500/movie.png',verified85=True)
  with mock.patch('work_search86.details',return_value=movie) as checked:value=engine.candidate(e)
  checked.assert_called_once();self.assertEqual(value['source'],'tmdb_movie');self.assertIn('movie.png',value['url'])
 def test_save_details_respects_a_source_disabled_after_search(self):
  self.options['programme_tmdb_optout77']=True
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('network despite optout')):
   with self.assertRaisesRegex(Exception,'SOURCE_DISABLED'):self.m.details(200,'movie')
 def test_invalid_work_year_is_not_independently_verified(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(self.movie,release_date='9999-01-01')):
   with self.assertRaisesRegex(Exception,'CANDIDATES_REJECTED'):self.m.details(200,'movie')

 def test_foreign_modal_is_not_ignored_by_new_manager(self):
  from types import SimpleNamespace
  with mock.patch('programme_window46.permitted',return_value=False),mock.patch('work_manager86.event_for',side_effect=AssertionError('foreign modal')):
   self.assertFalse(__import__('work_manager86').open(SimpleNamespace(_closed=False)))
 def test_confirmed_epg_mapping_requests_a_fresh_image_without_reopening_details(self):
  from xcmate027_fixture import ADDON
  m=__import__('programme_window46');view=m.ProgrammeWindow46('XCMateProgramme46.xml',str(ADDON),'Default','720p');view.configure(self.portal,dict(sid='1',name='Station'))
  view.event=dict(pid='p',sid='1',title='Monk');view._series_menu85=True;view._art_signature='old';view._art68={'source':'old'}
  with mock.patch('programme_lifecycle69.pulse',return_value=False),mock.patch('work_manager86.open',return_value=True),mock.patch('programme_requests68.request') as queued:view.pump()
  self.assertIsNone(view._art_signature);self.assertEqual(view._art68,{});queued.assert_called_once_with(view.event,priority=True)

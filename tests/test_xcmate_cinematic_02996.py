"""Bounded cinematic selection after independent work identity, synthetic only."""
import importlib, unittest
from unittest import mock
from xcmate027_fixture import Fixture


def backdrop(path, width=1920, height=1080, language=None, votes=20, rating=7):
 return dict(file_path=path,width=width,height=height,aspect_ratio=width/height,iso_639_1=language,vote_count=votes,vote_average=rating)


class Cinematic96(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True,tmdb_read_token43="SYNTHETIC_CINEMATIC_TOKEN")
  context=mock.patch('home_schedule75.applicable',return_value=True);context.start();self.addCleanup(context.stop)
  self.m=importlib.import_module('cinematic_images96');self.m._cache.clear()
  self.e=dict(pid='p',sid='1',key='event',title='Exact Cinema',genre='Film',year=2020,start=self.now,stop=self.now+1800)
  self.art=dict(source='tmdb_movie',remote_id=96,match='EXACT_TITLE_YEAR',role81='backdrop',url='https://image.tmdb.org/t/p/w500/old.jpg',official_poster86='https://image.tmdb.org/t/p/w500/poster.jpg')
 def test_rank_filters_language_portrait_small_and_unsafe_and_bounds_five(self):
  rows=[backdrop('/fr.jpg',language='fr'),backdrop('/small.jpg',width=960,height=540),backdrop('/portrait.jpg',width=1280,height=1920),backdrop('https://foreign.invalid/x.jpg')]
  rows += [backdrop('/good%d.jpg'%i,votes=10+i) for i in range(9)]
  result=self.m.rank(dict(id=96,backdrops=rows),96)
  self.assertEqual(len(result),5);self.assertTrue(all('good' in r['url'] for r in result))
  self.assertTrue(all('/w1280/' in r['url'] for r in result))
 def test_aspect_dimensions_votes_and_rating_each_affect_order(self):
  ideal=backdrop('/ideal.jpg')
  for worse in (backdrop('/aspect.jpg',width=1920,height=1000),backdrop('/size.jpg',width=1280,height=720),backdrop('/votes.jpg',votes=1),backdrop('/rating.jpg',rating=4)):
   with self.subTest(path=worse['file_path']):self.assertEqual(self.m.rank(dict(id=96,backdrops=[worse,ideal]),96)[0]['url'].rsplit('/',1)[1],'ideal.jpg')
 def test_one_safe_endpoint_cached_per_identity_without_replacing_proof(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(id=96,backdrops=[backdrop('/best.jpg'),backdrop('/next.jpg',language='de')])) as request:
   result=self.m.enrich(self.art,self.e)
   again=self.m.enrich(self.art,self.e)
  self.assertEqual(request.call_count,1);self.assertIn('/movie/96/images?',request.call_args.args[0]);self.assertEqual(result,again)
  self.assertTrue(result['url'].endswith('/best.jpg'));self.assertEqual(result['match'],self.art['match']);self.assertEqual(len(result['cinematic_backdrops96']),2)
 def test_disabled_cancelled_unproved_and_non_tmdb_never_lookup(self):
  for art in (dict(self.art,match='PROVISIONAL_TV85'),dict(self.art,provisional85=True),dict(self.art,source='xmltv_event'),dict(self.art,remote_id=True)):
   with mock.patch('tmdb_connection60.request',side_effect=AssertionError('unproved request')) as request:
    self.assertEqual(self.m.enrich(art,self.e),art);request.assert_not_called()
  with mock.patch('tmdb_connection60.request') as request:
   self.assertEqual(self.m.enrich(self.art,self.e,lambda:True),self.art);request.assert_not_called()
  self.options['programme_tmdb_optout77']=True
  with mock.patch('tmdb_connection60.request') as request:self.assertEqual(self.m.enrich(self.art,self.e),self.art);request.assert_not_called()
 def test_missing_malformed_wrong_identity_and_network_failure_keep_verified_image(self):
  for response in ({},dict(id=95,backdrops=[backdrop('/foreign.jpg')]),dict(id=96,backdrops=[]),dict(id=96,backdrops='bad')):
   self.m._cache.clear()
   with mock.patch('tmdb_connection60.request',return_value=response):self.assertEqual(self.m.enrich(self.art,self.e),self.art)
  self.m._cache.clear()
  with mock.patch('tmdb_connection60.request',side_effect=__import__('media_sources43').SourceError('TIMEOUT')):self.assertEqual(self.m.enrich(self.art,self.e),self.art)
 def test_movie_independent_details_must_pass_before_image_endpoint(self):
  row=dict(id=96,title=self.e['title'],release_date='2020-01-01',backdrop_path='/old.jpg')
  def api(url,**kwargs):
   if '/search/' in url:return dict(total_pages=1,total_results=1,results=[row])
   if '/images?' in url:return dict(id=96,backdrops=[backdrop('/best.jpg')])
   return row
  with mock.patch('tmdb_connection60.request',side_effect=api) as request:
   matched=__import__('programme_match46').candidate(self.e)
   value=__import__('hero_art86').expand([matched],self.e)[0]
  self.assertTrue(value['url'].endswith('/best.jpg'));self.assertEqual(len(request.call_args_list),3)
  self.m._cache.clear()
  with mock.patch('tmdb_connection60.request',side_effect=[dict(total_pages=1,total_results=1,results=[row]),dict(row,title='Wrong identity')]) as request:
   self.assertIsNone(__import__('programme_match46').candidate(self.e))
  self.assertEqual(len(request.call_args_list),2)
 def test_ambiguous_tv_never_requests_images(self):
  rows=[dict(id=i,name='Exact Cinema',first_air_date='2020-01-01',backdrop_path='/old.jpg') for i in (96,97)]
  def api(url,**kwargs):
   self.assertNotIn('/images',url)
   if '/search/' in url:return dict(total_pages=1,total_results=2,results=rows)
   return rows[0] if '/96?' in url else rows[1]
  with mock.patch('tmdb_connection60.request',side_effect=api):
   with self.assertRaisesRegex(Exception,'NO_MATCH_AMBIGUOUS'):__import__('programme_candidates85').candidate(dict(self.e,genre='Series'))
 def test_hero_tries_ranked_wide_before_xmltv_then_portrait(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(id=96,backdrops=[backdrop('/best.jpg'),backdrop('/second.jpg',votes=2)])):
   art=self.m.enrich(self.art,self.e)
  feed=dict(source='xmltv_event',url='https://example.org/event.jpg')
  ordered=__import__('hero_art86').ordered([art],[feed])
  self.assertEqual([v['source'] for v in ordered],['tmdb_movie','tmdb_movie','xmltv_event','tmdb_movie'])
  self.assertEqual(ordered[-1]['role81'],'poster');self.assertTrue(ordered[1]['url'].endswith('/second.jpg'))

 def test_optional_error_is_negatively_cached_without_retry_in_nested_match(self):
  from media_sources43 import SourceError
  with mock.patch('tmdb_connection60.request',side_effect=SourceError('HTTP_SERVER')) as request:
   self.assertEqual(self.m.enrich(self.m.enrich(self.art,self.e),self.e),self.art)
  self.assertEqual(request.call_count,1)
 def test_unique_tv_details_are_verified_before_tv_images_lookup(self):
  row=dict(id=96,name='Exact Cinema',first_air_date='2020-01-01',backdrop_path='/old.jpg')
  def api(url,**kwargs):
   if '/search/' in url:return dict(total_pages=1,total_results=1,results=[row])
   if '/images?' in url:return dict(id=96,backdrops=[backdrop('/best.jpg')])
   return row
  with mock.patch('tmdb_connection60.request',side_effect=api) as request:
   event=dict(self.e,genre='Series')
   matched=__import__('programme_candidates85').candidate(event)
   value=__import__('hero_art86').expand([matched],event)[0]
  urls=[call.args[0] for call in request.call_args_list]
  self.assertIn('/tv/96?',urls[1]);self.assertIn('/tv/96/images?',urls[2]);self.assertEqual(len(urls),3)
  self.assertTrue(value['url'].endswith('/best.jpg'));self.assertEqual(value['image_scope57'],'series_fallback')
 def test_exact_episode_still_keeps_its_separate_role_and_does_not_call_work_images(self):
  still=dict(source='tmdb_episode',remote_id=96,match='EXACT_SEASON_EPISODE',url='https://image.tmdb.org/t/p/w500/still.jpg')
  with mock.patch('tmdb_connection60.request') as request:self.assertEqual(self.m.enrich(still,self.e),still);request.assert_not_called()


class CinematicAdmission96(Fixture,unittest.TestCase):
 def setUp(self):
  Fixture.setUp(self);self.options.update(programme_tmdb46=True,tmdb_research43=True,tmdb_read_token43="SYNTHETIC_CINEMATIC_TOKEN")
  context=mock.patch('home_schedule75.applicable',return_value=True);context.start();self.addCleanup(context.stop)
  self.m=importlib.import_module('cinematic_images96');self.m._cache.clear()
  self.e=dict(pid='p',sid='1',key='event',title='Exact Cinema',genre='Film',year=2020,start=self.now,stop=self.now+1800)
  self.art=dict(source='tmdb_movie',remote_id=96,match='EXACT_TITLE_YEAR',role81='backdrop',url='https://image.tmdb.org/t/p/w500/old.jpg')
 def test_non_home_confirmed_movie_keeps_two_identity_requests_without_images(self):
  row=dict(id=96,title=self.e['title'],release_date='2020-01-01',backdrop_path='/old.jpg')
  def api(url,**kwargs):
   if '/search/' in url:return dict(total_pages=1,total_results=1,results=[row])
   if '/images?' in url:return dict(id=96,backdrops=[backdrop('/best.jpg')])
   return row
  with mock.patch('home_schedule75.applicable',return_value=False),mock.patch('tmdb_connection60.request',side_effect=api) as request:
   result=__import__('programme_match46').candidate(self.e)
  self.assertEqual([call.args[0].split('/3/')[1].split('?')[0] for call in request.call_args_list],['search/movie','movie/96'])
  self.assertTrue(result['url'].endswith('/old.jpg'));self.assertEqual(result['match'],'EXACT_TITLE_YEAR')
 def test_detail_on_home_skin_never_requests_optional_cinematic_endpoint(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(id=96,backdrops=[backdrop('/best.jpg')])) as request:
   result=self.m.enrich(self.art,dict(self.e,_detail93=True))
  request.assert_not_called();self.assertEqual(result,self.art)
 def test_non_home_and_detail_keep_existing_image_even_when_cinematic_cache_is_warm(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(id=96,backdrops=[backdrop('/best.jpg')])) as request:
   hero=self.m.enrich(self.art,self.e)
   self.assertTrue(hero['url'].endswith('/best.jpg'))
   with mock.patch('home_schedule75.applicable',return_value=False):
    self.assertEqual(self.m.enrich(self.art,self.e),self.art)
   self.assertEqual(self.m.enrich(self.art,dict(self.e,_detail93=True)),self.art)
  self.assertEqual(request.call_count,1)

 def test_home_skin_matching_stays_identity_only_until_explicit_hero_selection(self):
  row=dict(id=96,title=self.e['title'],release_date='2020-01-01',backdrop_path='/old.jpg')
  def api(url,**kwargs):
   if '/search/' in url:return dict(total_pages=1,total_results=1,results=[row])
   if '/images?' in url:return dict(id=96,backdrops=[backdrop('/best.jpg')])
   return row
  with mock.patch('tmdb_connection60.request',side_effect=api) as request:
   matched=__import__('programme_match46').candidate(self.e)
   self.assertEqual(request.call_count,2)
   self.assertTrue(matched['url'].endswith('/old.jpg'))
   selected=__import__('hero_art86').expand([matched],self.e)
  self.assertEqual(request.call_count,3);self.assertTrue(selected[0]['url'].endswith('/best.jpg'))
  self.assertEqual(selected[0]['match'],matched['match']);self.assertEqual(selected[0]['remote_id'],96)
 def test_manual_reference_is_identical_in_home_and_details_without_images_lookup(self):
  chosen=dict(self.art,match='MANUAL_CONFIRMED',manual85=True)
  mapping=dict(source='tmdb',id=96)
  for detail in (False,True):
   self.m._cache.clear()
   event=dict(self.e,placeholder='/neutral.png',_detail93=detail)
   with self.subTest(detail=detail),mock.patch('programme_mapping85.current',return_value=mapping),mock.patch('programme_candidates85.candidate',return_value=chosen),mock.patch('hero_render86.recovered_candidate',return_value=None),mock.patch('programme_art46.prepare',side_effect=lambda event,**kwargs:kwargs['resolved60']),mock.patch('tmdb_connection60.request',return_value=dict(id=96,backdrops=[backdrop('/best.jpg')])) as request:
    result=__import__('programme_urls55').resolve(event,allow_lookup=True)
   self.assertEqual(result['url'],chosen['url'])
   request.assert_not_called()
   self.assertEqual(result['match'],'MANUAL_CONFIRMED')

 def test_manual_flags_keep_explicit_reference_even_with_warm_cinematic_cache(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(id=96,backdrops=[backdrop('/best.jpg')])) as request:
   automatic=self.m.enrich(self.art,self.e)
  self.assertTrue(automatic['url'].endswith('/best.jpg'));self.assertEqual(request.call_count,1)
  for proof in (dict(match='MANUAL_CONFIRMED'),dict(manual85=True)):
   chosen=dict(self.art,**proof)
   with self.subTest(proof=proof),mock.patch('tmdb_connection60.request') as request:
    self.assertEqual(self.m.enrich(chosen,self.e),chosen)
    self.assertEqual(__import__('hero_art86').expand([chosen],self.e),[chosen])
   request.assert_not_called()
 def test_manual_art_never_substitutes_previously_ranked_alternatives_or_poster(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(id=96,backdrops=[backdrop('/best.jpg'),backdrop('/next.jpg')])):
   automatic=self.m.enrich(self.art,self.e)
  chosen=dict(automatic,url=self.art['url'],match='MANUAL_CONFIRMED',manual85=True,official_poster86='https://image.tmdb.org/t/p/w500/poster.jpg')
  self.assertEqual(self.m.alternatives(chosen),[chosen])
  self.assertEqual(__import__('hero_art86').ordered([chosen],[]),[chosen])
 def test_stored_manual_work_reference_precedes_other_cached_art_for_same_work_id(self):
  chosen=dict(source='tmdb',id=96,verified85=True,work_match85=True,title='Exact Cinema',year=2020,country=[],role='backdrop',url=self.art['url'],poster='')
  mapping=dict(source='tmdb',id=96,year=2020,country=[],media_type86='movie',work87=dict(title=chosen['title'],role=chosen['role'],url=chosen['url']))
  other=dict(chosen,media_type86='movie',url='https://image.tmdb.org/t/p/w500/other.jpg')
  with mock.patch('programme_mapping85.current',return_value=mapping),mock.patch('programme_candidates85.read',return_value=dict(rows=[other])),mock.patch('tmdb_connection60.request') as request:
   value=__import__('programme_candidates85').candidate(self.e)
  self.assertEqual(value['url'],chosen['url']);self.assertEqual(value['match'],'MANUAL_CONFIRMED');self.assertTrue(value['manual85']);request.assert_not_called()

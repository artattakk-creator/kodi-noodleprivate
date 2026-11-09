"""Unknown-genre TV work proof, official AKA, no still invention, film regression."""
import importlib,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Series84(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_tvmaze67=False,tmdb_read_token43='SYNTHETIC_E84_NOT_A_TOKEN')
  self.event=dict(pid='p',sid='1',key='event84',title='The Middle',start=self.now,stop=self.now+3600,genre='')
  self.tv=importlib.import_module('programme_tv66');self.tmdb=importlib.import_module('tmdb_epg60')
 def api(self,title='The Middle',year=2009,aliases=(),movie_conflict=False):
  row=dict(id=84,name=title,original_name=title,first_air_date=str(year)+'-01-01',backdrop_path='/series84.jpg')
  def reply(url,**kwargs):
   if '/alternative_titles' in url:return dict(id=84,results=[dict(title=a) for a in aliases])
   if '/search/movie' in url:return dict(total_pages=1 if movie_conflict else 0,total_results=int(movie_conflict),results=[dict(id=85,title='The Middle',release_date='2009-01-01')] if movie_conflict else [])
   if '/search/tv' in url:return dict(total_pages=1,total_results=1,results=[row])
   return dict(row)
  return reply
 def test_short_middle_without_genre_year_or_episode_requires_full_cross_media_proof(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.api()) as rpc:value=self.tmdb.candidate(self.event)
  self.assertEqual(value['source'],'tmdb_series');self.assertEqual(value['image_scope57'],'series_fallback');self.assertEqual(value['matched_year56'],2009)
  self.assertEqual(value['role81'],'backdrop');self.assertTrue(any('/search/movie' in c.args[0] for c in rpc.call_args_list))
 def test_middle_with_correct_year_also_uses_work_fallback(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.api()):value=self.tv.candidate(dict(self.event,year=2009))
  self.assertEqual(value['match'],'EXACT_TV_TITLE_YEAR66')
 def test_short_same_named_film_makes_unknown_classification_ambiguous(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.api(movie_conflict=True)):
   with self.assertRaisesRegex(Exception,'NO_MATCH_AMBIGUOUS'):self.tv.candidate(self.event)
 def test_multiple_middle_works_are_not_resolved_by_first_result(self):
  rows=[dict(id=i,name='The Middle',first_air_date=str(2000+i)+'-01-01') for i in (1,2)]
  with mock.patch('tmdb_connection60.request',return_value=dict(total_pages=1,total_results=2,results=rows)):
   with self.assertRaisesRegex(Exception,'NO_MATCH_AMBIGUOUS'):self.tv.candidate(self.event)
 def test_incomplete_tv_or_movie_search_cannot_establish_uniqueness(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(total_pages=2,total_results=20,results=[])):
   with self.assertRaisesRegex(Exception,'NO_MATCH_AMBIGUOUS'):self.tv.candidate(self.event)
  base=self.api()
  with mock.patch('tmdb_connection60.request',side_effect=lambda url,**kw:dict(total_pages=2,total_results=40,results=[]) if '/search/movie' in url else base(url,**kw)):
   with self.assertRaisesRegex(Exception,'NO_MATCH_AMBIGUOUS'):self.tv.candidate(self.event)
 def test_king_title_alias_requires_official_independent_aka_response(self):
  event=dict(self.event,title='King of Queens')
  with mock.patch('tmdb_connection60.request',side_effect=self.api('The King of Queens',1998,('King of Queens',))) as rpc:value=self.tmdb.candidate(event)
  self.assertEqual(value['source'],'tmdb_series');self.assertEqual(value['remote_id'],84)
  self.assertTrue(any('/alternative_titles' in c.args[0] for c in rpc.call_args_list))
 def test_unverified_king_article_variant_is_not_a_match(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.api('The King of Queens',1998)):
   self.assertIsNone(self.tv.candidate(dict(self.event,title='King of Queens')))
 def test_wrong_series_id_or_year_cannot_satisfy_independent_details(self):
  base=self.api()
  def bad(url,**kw):
   value=base(url,**kw)
   if '/tv/84?' in url:value['id']=999
   return value
  with mock.patch('tmdb_connection60.request',side_effect=bad):
   with self.assertRaisesRegex(Exception,'NO_MATCH'):self.tv.candidate(self.event)
  with mock.patch('tmdb_connection60.request',side_effect=base):
   with self.assertRaisesRegex(Exception,'NO_MATCH'):self.tv.candidate(dict(self.event,year=2012))
 def test_verified_episode_missing_still_uses_labelled_independently_verified_work(self):
  row=dict(id=84,name='The Middle',original_name='The Middle',first_air_date='2009-01-01')
  def reply(url,**kw):
   if '/search/tv' in url:return dict(total_pages=1,total_results=1,results=[row])
   if '/episode/' in url:return dict(id=841,season_number=1,episode_number=2,name='Exact episode',still_path=None)
   return dict(row,backdrop_path='/series84.jpg')
  with mock.patch('tmdb_connection60.request',side_effect=reply):value=self.tmdb.candidate(dict(self.event,season=1,episode=2,year=2009,subtitle='Exact episode'))
  self.assertEqual(value['image_scope57'],'series_fallback');self.assertEqual(value['source'],'tmdb_series');self.assertIn('kein Episodenbild',value['attribution'])
 def test_wrong_episode_subtitle_does_not_get_an_invented_still_or_fallback(self):
  row=dict(id=84,name='The Middle',first_air_date='2009-01-01')
  with mock.patch('tmdb_connection60.request',side_effect=[dict(total_pages=1,total_results=1,results=[row]),dict(id=841,season_number=1,episode_number=2,name='Wrong episode')]):
   self.assertIsNone(self.tmdb.candidate(dict(self.event,season=1,episode=2,year=2009,subtitle='Exact episode')))
 def test_explicit_film_never_uses_tv_and_future_epg_slots_keep_movie_path(self):
  row=dict(id=84,title='Synthetic exact film',original_title='Synthetic exact film',release_date='2014-01-01',backdrop_path='/movie84.jpg')
  for future in (0,6*3600,12*3600):
   with mock.patch('tmdb_connection60.request',side_effect=[dict(total_pages=1,total_results=1,results=[row]),row]) as rpc:
    value=self.tmdb.candidate(dict(self.event,title=row['title'],genre='Spielfilm',year=2014,start=self.now+future,stop=self.now+future+3600))
   self.assertEqual(value['source'],'tmdb_movie');self.assertTrue(all('/tv/' not in c.args[0] and '/search/tv' not in c.args[0] for c in rpc.call_args_list))
 def test_series_lookup_optout_does_not_change_or_reimport_token(self):
  self.options['programme_tmdb_optout77']=True;before=dict(self.options)
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('disabled lookup')):self.assertIsNone(self.tv.candidate(self.event))
  self.assertEqual(self.options,before)

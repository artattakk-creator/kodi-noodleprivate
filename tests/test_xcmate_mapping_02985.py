"""B: Ghosts UK/US, bounded pages, explicit reversible per-work user choice."""
import importlib,json,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Mapping85(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_tvmaze67=False,tmdb_read_token43='SYNTHETIC_85_NO_REAL_TOKEN')
  self.engine=importlib.import_module('programme_candidates85');self.maps=importlib.import_module('programme_mapping85')
  self.event=dict(pid='p',sid='1',canonical='xml',epg_source46='sourceA',source_key46='stableSource',title='Ghosts',genre='Serie',start=self.now,stop=self.now+1800,key='event')
  self.uk=dict(id=19,name='Ghosts',original_name='Ghosts',first_air_date='2019-01-01',origin_country=['GB'],backdrop_path='/uk.jpg',poster_path='/ukposter.jpg',overview='Alison and Mike')
  self.us=dict(id=21,name='Ghosts',original_name='Ghosts',first_air_date='2021-01-01',origin_country=['US'],backdrop_path='/us.jpg',poster_path='/usposter.jpg',overview='Samantha and Jay')
  self.maps.reload()
 def reply(self,rows=None,multipage=False,aliases=None):
  rows=rows or [self.uk,self.us];lookup={r['id']:r for r in rows}
  def request(url,**kwargs):
   from urllib.parse import urlsplit,parse_qs
   args=parse_qs(urlsplit(url).query)
   if '/search/movie' in url:return dict(page=1,total_pages=0,total_results=0,results=[])
   if '/search/tv' in url:
    page=int(args.get('page',['1'])[0]);return dict(page=page,total_pages=(len(rows)+19)//20,total_results=len(rows),results=rows[(page-1)*20:page*20])
   ident=int(url.split('/tv/')[1].split('/')[0].split('?')[0])
   if '/alternative_titles' in url:return dict(id=ident,results=[dict(title=x) for x in (aliases or [])])
   return dict(lookup[ident])
  return request
 def test_two_ghosts_are_not_confirmed_by_server_ranking(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):
   with self.assertRaisesRegex(Exception,'NO_MATCH_AMBIGUOUS'):self.engine.candidate(self.event)
  proposed=self.engine.suggestion(self.event)
  self.assertTrue(proposed['provisional85']);self.assertEqual(proposed['match'],'PROVISIONAL_TV85');self.assertIn('nicht bestätigt',proposed['attribution']);self.assertEqual(proposed['role81'],'poster');self.assertNotIn('episode',proposed['source'])
 def test_trusted_work_year_selects_correct_ghosts_after_independent_details(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):value=self.engine.candidate(dict(self.event,year=2021))
  self.assertEqual(value['remote_id'],21);self.assertFalse(value['manual85'])
 def test_country_disambiguation_uses_work_country_not_channel_brand(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):value=self.engine.candidate(dict(self.event,country='GB'))
  self.assertEqual(value['remote_id'],19)
 def test_three_bounded_pages_can_find_exact_work_beyond_first_page(self):
  rows=[dict(self.uk,id=100+i,name='Other show '+str(i),original_name='Other show '+str(i)) for i in range(45)];rows[24]=self.us
  with mock.patch('tmdb_connection60.request',side_effect=self.reply(rows)) as rpc:value=self.engine.candidate(dict(self.event,year=2021))
  self.assertEqual(value['remote_id'],21);self.assertEqual(sum('/search/tv' in c.args[0] for c in rpc.call_args_list),3)
 def test_more_than_three_pages_is_never_claimed_complete(self):
  rows=[dict(self.uk,id=100+i,name='Other '+str(i),original_name='Other '+str(i)) for i in range(80)];rows[0]=self.us
  with mock.patch('tmdb_connection60.request',side_effect=self.reply(rows)) as rpc:
   with self.assertRaisesRegex(Exception,'NO_MATCH_AMBIGUOUS'):self.engine.candidate(self.event)
  self.assertLessEqual(sum('/search/tv' in c.args[0] for c in rpc.call_args_list),3)
 def test_manual_choice_is_persistent_across_cold_read_and_new_broadcast(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):rows,_=self.engine.search(self.event)
  self.maps.set_mapping(self.event,rows[1]);saved=self.maps.path().read_bytes();self.assertNotIn(b'SYNTHETIC_85',saved)
  self.maps.window().clearProperty(self.maps.PREFIX+'Records');self.assertTrue(self.maps.reload())
  later=dict(self.event,start=self.now+86400,stop=self.now+86400+1800,key='future')
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):value=self.engine.candidate(later)
  self.assertEqual(value['remote_id'],21);self.assertEqual(value['match'],'MANUAL_CONFIRMED');self.assertEqual(value['image_scope57'],'series_fallback')
 def test_other_portal_profile_source_channel_and_work_year_do_not_inherit(self):
  row=dict(id=19,source='tmdb',year=2019,country=['GB'],verified85=True);self.maps.set_mapping(self.event,row)
  for changes in (dict(pid='other'),dict(sid='other'),dict(epg_source46='sourceB'),dict(year=2021),dict(title='Modern Family')):
   self.assertIsNone(self.maps.current(dict(self.event,**changes)))
  with mock.patch('epg_handoff63.profile_scope',return_value='otherProfile'):self.assertIsNone(self.maps.current(self.event))
 def test_changing_and_resetting_mapping_preserves_other_works_and_increments_epoch(self):
  row=dict(id=19,source='tmdb',year=2019,country=['GB'],verified85=True);other=dict(self.event,title='Modern Family')
  self.maps.set_mapping(self.event,row);epoch=self.maps.epoch(self.event);self.maps.set_mapping(other,row)
  self.assertEqual(self.maps.epoch(self.event),epoch);self.maps.set_mapping(self.event,dict(row,id=21,year=2021));self.assertEqual(self.maps.current(self.event)['id'],21)
  self.maps.set_mapping(self.event,automatic=True);self.assertIsNone(self.maps.current(self.event));self.assertIsNotNone(self.maps.current(other));self.assertGreater(self.maps.epoch(self.event),epoch)
 def test_failed_reserve_write_cannot_report_saved_or_remove_previous(self):
  row=dict(id=19,source='tmdb',year=2019,country=['GB'],verified85=True);self.maps.set_mapping(self.event,row);before=self.maps.path().read_bytes()
  with mock.patch('storage_metadata92.check',side_effect=OSError('RESERVE_BLOCKED')):
   with self.assertRaises(OSError):self.maps.set_mapping(self.event,dict(row,id=21))
  self.assertEqual(self.maps.path().read_bytes(),before);self.assertEqual(self.maps.current(self.event)['id'],19)
 def test_hiding_suggestion_is_per_work_and_reversible(self):
  self.maps.set_mapping(self.event,hidden=True)
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('hidden work lookup')):self.assertIsNone(self.engine.candidate(self.event))
  self.maps.set_mapping(self.event,automatic=True)
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):self.assertTrue(self.engine.search(self.event)[0])
 def test_without_preview_consent_ambiguity_keeps_no_image(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):self.engine.search(self.event)
  self.options['programme_suggestions85']=False;self.assertIsNone(self.engine.suggestion(self.event))
 def test_suggestions_never_cross_a_film_conflict(self):
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):self.assertIsNone(self.engine.candidate(dict(self.event,genre='Spielfilm')))
 def test_mash_punctuation_is_exact_canonical_acronym_not_substring_guessing(self):
  from programme_mapping85 import name
  self.assertEqual(name('M*A*S*H'),name('M.A.S.H.'));self.assertNotEqual(name('M*A*S*H'),name('Mashup'))
 def test_explicit_picker_allows_correction_of_wrong_epg_year_without_polluting_automatic_cache(self):
  event=dict(self.event,year=2026)
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):rows,done=self.engine.search(dict(event,_manager85=True))
  self.assertTrue(done);self.assertEqual({r['year'] for r in rows},{2019,2021});self.assertFalse(self.engine.read(event));self.assertIsNone(self.engine.suggestion(event))
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):
   with self.assertRaisesRegex(Exception,'NO_MATCH'):self.engine.candidate(event)
 def test_user_confirmed_work_overrides_conflicting_automatic_work_id_without_changing_epg_facts(self):
  event=dict(self.event,external_ids={'imdb_id':'wrong_epg_fixture_id'},_work_ids_verified85=True);before=dict(event)
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):rows,_=self.engine.search(dict(event,_manager85=True))
  self.maps.set_mapping(event,rows[0])
  with mock.patch('tmdb_connection60.request',side_effect=self.reply()):value=self.engine.candidate(event)
  self.assertEqual(value['match'],'MANUAL_CONFIRMED');self.assertEqual(value['remote_id'],19);self.assertEqual(event,before);self.assertNotIn('episode',value)

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
 def test_verified_series_reaches_decoded_lease_detail_control_and_live_listitem(self):
  import io,types
  from PIL import Image
  from xcmate027_fixture import ADDON
  channel=dict(sid='1',name='Synthetic station',kind='live')
  body=io.BytesIO();Image.new('RGB',(320,180),(30,100,150)).save(body,'PNG');data=body.getvalue()
  def dns(url):
   from urllib.parse import urlsplit
   import artwork_visible
   artwork_visible._dns_cache[(urlsplit(url).hostname,443)]=(time.monotonic()+30,True);return True
  def check(url,cancel=lambda:False):
   stream=io.BytesIO(data);response=types.SimpleNamespace(status=200,headers={'Content-Type':'image/png'},read=stream.read,close=stream.close)
   return importlib.import_module('programme_transport77').verified(url,cancel=cancel,connect=lambda *a:response,resolver=lambda u:['93.184.216.34'],keep_data81=True)
  usage=types.SimpleNamespace(free=27*1024**2,total=4*1024**3,used=4*1024**3-27*1024**2)
  for title,official,year,aliases in [('The Middle','The Middle',2009,()),('King of Queens','The King of Queens',1998,('King of Queens',))]:
   with self.subTest(title=title):
    raw=dict(title=title,start=self.now-30,stop=self.now+1800,_metadata_verified48=True)
    event=importlib.import_module('programme_events46').describe(self.portal,channel,raw,'xml',None)
    with mock.patch('tmdb_connection60.request',side_effect=self.api(official,year,aliases)),mock.patch('shutil.disk_usage',return_value=usage),mock.patch('artwork_visible.public_dns',side_effect=dns):
     result=importlib.import_module('programme_urls55').resolve(event,allow_lookup=True,url_mode69=True,check=check)
    self.assertTrue(result['decoded77']);self.assertTrue(result['decoded88']);self.addCleanup(__import__('decoded_assets88').shutdown);self.assertEqual(result['source'],'tmdb_series')
    self.assertEqual(result['image_scope57'],'series_fallback');self.assertEqual(result['storage69'],'RAM_ONLY')
    importlib.import_module('programme_requests68').completed(event,result)
    window=importlib.import_module('programme_window46').ProgrammeWindow46('XCMateProgramme46.xml',str(ADDON),'Default','720p')
    window.configure(self.portal,channel,raw);window._ready=True;window.event=event
    info=dict(now=title,start=raw['start'],stop=raw['stop'],events=[raw],canonical46='xml',snapshot_revision=None,progress=.25)
    value=dict(art={},props={},info=dict(plot='Synthetic local EPG'))
    with mock.patch('tmdb_connection60.request',side_effect=AssertionError('GUI metadata lookup')),mock.patch('programme_urls55.enqueue',side_effect=AssertionError('GUI enqueue')):
     window.pump();importlib.import_module('programme_widgets46').decorate(value,self.portal,channel,info)
    self.assertEqual(window.getControl(110).image,result['image']);self.assertTrue(window.getControl(110).visible)
    self.assertEqual(value['props']['XCMate.ProgrammeImage46'],result['image']);self.assertEqual(value['props']['XCMate.ProgrammeImageScope57'],'series_fallback')
    self.assertEqual(value['art']['landscape'],result['image']);self.assertIn('Serienbild',window.getControl(105).text)
 def test_explicit_probe_uses_its_verified_candidate_without_a_second_metadata_search(self):
  import programme_probe84
  channel=dict(sid='1',name='Synthetic station')
  found=dict(url='https://image.tmdb.org/t/p/w500/series84.jpg',source='tmdb_series',match='EXACT_UNIQUE_TV_TITLE66')
  reader=mock.Mock();reader.get.return_value=channel
  result=dict(decoded77=True,image='https://image.tmdb.org/t/p/w500/series84.jpg',source='tmdb_series',code='READY')
  def resolve(event,**kwargs):
   self.assertTrue(kwargs.get('allow_lookup'));self.assertEqual(kwargs['match'](event),found);return result
  with mock.patch('tmdb_connection60.test_connection',return_value='TMDB_OK'),mock.patch('library_index.Reader',return_value=reader),mock.patch('programme_events46.load',return_value=self.event),mock.patch('programme_match46.candidate',return_value=found) as match,mock.patch('programme_urls55.resolve',side_effect=resolve),mock.patch('programme_requests68.completed') as completed,mock.patch('programme_image69.eligible',return_value=True):
   rows=dict(programme_probe84.inspect(self.portal))
  self.assertEqual(rows['MATCH'],'EXACT_REFERENCE');self.assertEqual(rows['IMAGE_DECODE'],'YES');self.assertEqual(rows['DISPLAY_LEASE'],'READY')
  self.assertEqual(rows['GUI_TEXTURE'],'NOT_VERIFIED_OPEN_SAME_EVENT');match.assert_called_once();completed.assert_called_once();reader.close.assert_called_once()
 def test_explicit_probe_respects_source_optout_before_sending_token(self):
  self.options['programme_tmdb_optout77']=True;before=dict(self.options)
  with mock.patch('tmdb_connection60.test_connection',side_effect=AssertionError('optout configuration request')),mock.patch('programme_match46.candidate',side_effect=AssertionError('optout match')):
   rows=dict(importlib.import_module('programme_probe84').inspect(self.portal))
  self.assertEqual(rows['MATCH'],'DISABLED_OR_NO_TOKEN');self.assertEqual(self.options,before)

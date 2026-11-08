"""Independent synthetic metadata/HTTP proof; never claims a real TMDB account."""
import importlib,io,json,threading,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Own81(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True,tmdb_read_token43='SYNTHETIC_TEST_TOKEN')
  import xbmc;xbmc.LOGINFO=1
  self.trace=importlib.import_module('art_trace81');self.trace._results.clear();self.trace._seen.clear()
 def event(self,title,genre='Film'):
  return dict(pid='p',sid='1',key=title,title=title,genre=genre,start=1,stop=self.now+600)
 def test_all_five_requested_titles_require_independent_details_and_alias_proof(self):
  from tmdb_epg60 import candidate
  cases=[('Modern Family','Modern Family','Series',2009),('Yuna & Stitch','Stitch!','Series',2008),('Die Tribute von Panem – Mockingjay (1)','Die Tribute von Panem – Mockingjay Teil 1','Film',2014),('Harry Potter und der Feuerkelch','Harry Potter und der Feuerkelch','Film',2005),('Die Croods: Alles auf Anfang','Die Croods: Alles auf Anfang','Film',2020)]
  for title,official,genre,year in cases:
   with self.subTest(title=title):
    calls=[]
    def api(url,**kwargs):
     calls.append(url);row=dict(id=81,title=official,name=official,release_date=str(year)+'-01-01',first_air_date=str(year)+'-01-01',backdrop_path='/synthetic81.jpg')
     if '/alternative_titles' in url:return dict(id=81,results=[dict(title=title)])
     return dict(total_pages=1,total_results=1,results=[row]) if '/search/' in url else row
    event=self.event(title,genre)
    with mock.patch('tmdb_connection60.request',side_effect=api):value=self.trace.own(event,lambda:candidate(event))
    self.assertIsNotNone(value);self.assertEqual(value['role81'],'backdrop');self.assertGreaterEqual(len(calls),2)
    again=mock.Mock(side_effect=AssertionError('repeat API'))
    self.assertEqual(self.trace.own(event,again),value)
    if title=='Yuna & Stitch':self.assertTrue(any('/alternative_titles' in url for url in calls))
  self.assertEqual(self.options['tmdb_read_token43'],'SYNTHETIC_TEST_TOKEN')
 def test_alias_without_independent_alternative_title_is_rejected(self):
  from programme_tv66 import candidate
  row=dict(id=81,name='Stitch!',first_air_date='2008-01-01',backdrop_path='/synthetic81.jpg')
  with mock.patch('tmdb_connection60.request',side_effect=[dict(total_pages=1,total_results=1,results=[row]),row,dict(id=81,results=[])]):
   with self.assertRaisesRegex(Exception,'NO_MATCH'):candidate(self.event('Yuna & Stitch','Series'))
 def test_optout_disables_cached_result_without_touching_token(self):
  event=self.event('Synthetic');call=mock.Mock(return_value=dict(url='https://image.tmdb.org/t/p/w500/a.jpg',source='tmdb_movie'))
  self.trace.own(event,call);before=dict(self.options);self.options['programme_tmdb_optout77']=True
  self.assertIsNone(self.trace.own(event,call));self.assertEqual(call.call_count,1);self.assertEqual(self.options['tmdb_read_token43'],before['tmdb_read_token43'])
 def test_inflight_dedup_negative_backoff_and_failure_do_not_spin(self):
  event=self.event('Synthetic');entered=threading.Event();release=threading.Event();results=[]
  def call():entered.set();release.wait(2);return None
  thread=threading.Thread(target=lambda:results.append(self.trace.own(event,call)));thread.start();self.assertTrue(entered.wait(1))
  second=mock.Mock(side_effect=AssertionError('duplicate API'));self.assertIsNone(self.trace.own(event,second));release.set();thread.join(2)
  self.assertIsNone(self.trace.own(event,second));second.assert_not_called();self.assertEqual(results,[None])
 def test_transport_trace_records_actual_response_status_and_never_token_or_url(self):
  import media_sources43 as media,xbmc
  for status in (200,401,429,500):
   with self.subTest(status=status):
    self.trace._results.clear();self.trace._seen.clear();logs=[]
    body=io.BytesIO(b'{"ok":true}')
    response=mock.Mock(status=status,headers={'Content-Type':'application/json'},read=body.read)
    with mock.patch('download_redirect.addresses',return_value=['93.184.216.34']),mock.patch.object(xbmc,'log',side_effect=lambda text,*a:logs.append(text),create=True):
     try:self.trace.own(self.event('Private synthetic title'),lambda:media.get('https://api.themoviedb.org/3/configuration',api=True,token='SYNTHETIC_SECRET_81',transport=lambda *a:response))
     except media.SourceError:pass
    text='\n'.join(logs);self.assertIn('HTTP_REQUEST_SENT',text);self.assertIn('"status":'+str(status),text)
    self.assertNotIn('SYNTHETIC_SECRET_81',text);self.assertNotIn('api.themoviedb.org',text);self.assertNotIn('Private synthetic title',text)
 def test_dns_or_connection_failure_never_claims_http_response(self):
  import media_sources43 as media,xbmc
  logs=[]
  with mock.patch('download_redirect.addresses',side_effect=OSError('private host')),mock.patch.object(xbmc,'log',side_effect=lambda text,*a:logs.append(text),create=True):
   with self.assertRaises(media.SourceError):self.trace.own(self.event('Synthetic'),lambda:media.get('https://api.themoviedb.org/3/configuration',api=True))
  self.assertFalse(any('HTTP_REQUEST_SENT' in s or 'HTTP_STATUS' in s for s in logs))
 def test_confirmed_backdrop_uses_large_transport_then_local_pixels_without_repeat_lookup(self):
  from PIL import Image
  from pathlib import Path
  from programme_events46 import describe
  import programme_urls55 as urls
  event=describe(self.portal,dict(sid='1',kind='live',name='Synthetic',epg_channel_id='xml'),dict(title='Synthetic film',start=self.now-60,stop=self.now+600),canonical='xml');event.update(genre='Film',year=2020)
  row=dict(id=81,title='Synthetic film',release_date='2020-01-01',backdrop_path='/large81.jpg')
  data=io.BytesIO();Image.new('RGB',(1280,720),(30,70,140)).save(data,'PNG');body=data.getvalue()
  def image(url,**kwargs):
   self.assertEqual(url,'https://image.tmdb.org/t/p/w1280/large81.jpg')
   return dict(url=url,width=1280,height=720,decoded77=True,_body81=body)
  with mock.patch('tmdb_connection60.request',side_effect=[dict(total_pages=1,total_results=1,results=[row]),row]),mock.patch('programme_art46.space'):
   value=urls.resolve(event,allow_lookup=True,check=image,url_mode69=True)
  self.assertEqual(value['source'],'tmdb_movie');self.assertEqual(Path(value['image']).read_bytes(),body)
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('duplicate API')),mock.patch('programme_urls55.probe',side_effect=AssertionError('repeat download')):
   self.assertEqual(urls.resolve(event,allow_lookup=True,url_mode69=True)['image'],value['image'])

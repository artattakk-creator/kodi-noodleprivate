"""First identity frame, exact control generations and real work-name fixtures."""
import importlib,json,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Home87(Fixture,unittest.TestCase):
 def test_live_first_nonempty_frame_is_not_held_by_the_sixty_second_artwork_gate(self):
  m=importlib.import_module('widget_notice46');hook='XCMate.Widget45.Reload.live';now=time.monotonic()
  m._pending[('p','live')]=('new',88);m._hooks[('p','live')]=[hook];m._seen[hook]=('old',now)
  self.properties['XCMate.Home86.Rail']=json.dumps(dict(pid='p',context='c'*64,total=88))
  with mock.patch('xbmc.getSkinDir',create=True,return_value='skin.titan.bingie.mod'),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('hero_epg63.poll'),mock.patch('skin_upgrade63.poll'),mock.patch('home_schedule75.observe'),mock.patch('home_activation78.poll'),mock.patch('widget_home_probe59.poll'),mock.patch('widget_runtime79.poll'),mock.patch('artwork_display84.enabled',return_value=False),mock.patch('widget_patch85.publication',return_value=False),mock.patch('xbmc.getCondVisibility',return_value=False):
   m._next=0;m.poll();first=self.properties.get(hook);self.assertTrue(first)
   m._pending[('p','live')]=('art-only',88);m._next=0;m.poll();self.assertEqual(self.properties.get(hook),first)
 def test_same_rail_context_does_not_reset_a_stable_status_to_loading(self):
  status=importlib.import_module('home_status86');status.rail(self.portal,88,5)
  self.properties['XCMate.Home86.Text']='Sender 88 · Logos 5/88';self.properties['XCMate.Home86.State']='READY_PARTIAL'
  status.rail(self.portal,88,5);self.assertEqual(self.properties['XCMate.Home86.Text'],'Sender 88 · Logos 5/88');self.assertEqual(self.properties['XCMate.Home86.State'],'READY_PARTIAL')
 def test_desperate_housewives_and_american_dad_use_verified_series_backdrops(self):
  self.options.update(programme_tmdb46=True,tmdb_research43=True,tmdb_read_token43='SYNTHETIC87_NOT_A_TOKEN')
  module=__import__('programme_candidates85')
  for title,official,ident,year in [('Desperate Housewives','Desperate Housewives',693,2004),('American Dad','American Dad!',1433,2005)]:
   tv=dict(id=ident,name=official,original_name=official,first_air_date=str(year)+'-01-01',origin_country=['US'],backdrop_path='/wide.png',poster_path='/poster.png')
   def response(url,**kwargs):
    if '/search/tv' in url:return dict(results=[tv],total_results=1,total_pages=1,page=1)
    if '/search/movie' in url:return dict(results=[],total_results=0,total_pages=0,page=1)
    return tv
   event=dict(pid='p',sid=str(ident),title=title,key=str(ident),start=self.now,stop=self.now+3600)
   with mock.patch('tmdb_connection60.request',side_effect=response):value=module.candidate(event)
   self.assertEqual(value['remote_id'],ident);self.assertEqual(value['role81'],'backdrop');self.assertEqual(value['source'],'tmdb_series')
 def test_event_timing_percentiles_are_bounded_and_do_not_claim_visible_pixels(self):
  m=__import__('hero_timing87');clock=iter([1,1.2,1.5])
  event=dict(pid='p',sid='1',key='event',title='Private programme',start=self.now,stop=self.now+3600)
  with mock.patch.object(m,'time',types.SimpleNamespace(monotonic=lambda:next(clock))):
   m.note(event,'QUEUED');m.note(event,'RENDER_READY');m.note(event,'BANK_SWITCHED')
  value=m.summary();self.assertEqual(value['RENDER_READY']['p95_ms'],200);self.assertNotIn('Private programme',self.properties['XCMate.Hero87.Trace']);self.assertIn('NOT_VISIBLE_PIXELS',self.properties['XCMate.Hero87.Trace'])
 def test_same_verified_hero_can_switch_to_new_decoded_cache_uri_without_black_gap(self):
  m=__import__('hero_render86');w=m.window();event=dict(pid='p',sid='1',key='e',title='American Dad',start=self.now,stop=self.now+1800)
  value=dict(code='READY',source='tmdb_series',role81='backdrop',image='/new-cache.png',sha256='a'*64,image_width77=1280,image_height77=720,source_url='https://image.tmdb.org/t/p/w1280/current.png')
  w.setProperty('XCMate.Hero63.Active','A');w.setProperty(m.PREFIX+'Event',__import__('event_art81').key(event))
  for k,v in dict(Image='/expired-temp.png',ArtSource='tmdb_series',Kind86='hero_backdrop',Rank86='0',SourceUrl86=value['source_url'],Digest87='a'*64).items():w.setProperty('XCMate.Hero63.A.'+k,v)
  with mock.patch('programme_image69.eligible',return_value=True),mock.patch('event_art81.allowed',return_value=True),mock.patch('builtins.open',side_effect=AssertionError('no GUI file IO')):
   # Correct existing picture remains until the successor receipt actually exists.
   self.assertEqual(m.choose(event,value,{},w)['Image'],'/expired-temp.png')
   w.setProperty(m.PREFIX+'Ready',json.dumps(dict(key=m.tag(event,value),at=time.monotonic())))
   result=m.choose(event,value,{},w);self.assertEqual(result['Image'],'/new-cache.png');self.assertEqual(result['Digest87'],'a'*64)
   other=dict(value,image='/different-same-rank.png',source_url='https://image.tmdb.org/t/p/w1280/different.png',sha256='b'*64)
   w.setProperty(m.PREFIX+'Ready',json.dumps(dict(key=m.tag(event,other),at=time.monotonic())))
   self.assertEqual(m.choose(event,other,{},w)['Image'],'/expired-temp.png')
 def test_api_url_decode_and_bank_timing_use_one_redacted_event_correlation(self):
  event=dict(pid='p',sid='1',key='event',title='Private title',start=self.now,stop=self.now+1800)
  calls=[]
  with mock.patch('xbmc.log',create=True,side_effect=lambda line,*args:calls.append(line)),mock.patch('xbmc.LOGINFO',create=True,new=1):
   __import__('art_trace81').note(event,'HTTP_REQUEST_SENT')
   __import__('programme_pipeline77').note(event,'HTTP_RESPONSE','IMAGE_DECODED')
  correlation=__import__('hero_timing87').correlation(event)
  self.assertTrue(all('event='+correlation[:12] in line for line in calls));self.assertEqual(len(calls),2)
  self.assertEqual(json.loads(self.properties['XCMate.Hero87.Trace'])['event'],correlation)
  self.assertIn('IMAGE_RESPONSE',__import__('hero_timing87').summary());self.assertNotIn('Private title',''.join(calls))
 def test_fresh_local_station_logo_replaces_old_remote_fallback_while_programme_lookup_is_pending(self):
  m=__import__('hero_render86');w=m.window();event=dict(pid='p',sid='1',key='e',title='American Dad',start=self.now,stop=self.now+1800)
  w.setProperty('XCMate.Hero63.Active','A');w.setProperty(m.PREFIX+'Event',__import__('event_art81').key(event))
  for k,v in dict(Image='https://example.org/old.png',ArtSource='station_logo',Kind86='station_logo',Rank86='9').items():w.setProperty('XCMate.Hero63.A.'+k,v)
  value=m.choose(event,{},dict(Image='/verified-kodi-logo.png',ArtSource='station_logo'),w)
  self.assertEqual(value['Image'],'/verified-kodi-logo.png');self.assertEqual(value['Kind86'],'station_logo')

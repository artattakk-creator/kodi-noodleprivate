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

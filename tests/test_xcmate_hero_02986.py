"""B: CSI: Vegas source order, quality, renderer ACK and event isolation."""
import importlib,json,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Hero86(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True);self.h=importlib.import_module('hero_art86');self.e=dict(pid='p',sid='1',title='CSI: Vegas',key='e',start=self.now,stop=self.now+1800)
  self.value=dict(code='READY',source='tmdb_series',role81='backdrop',image='/verified/tmdb.png',image_width77=1280,image_height77=720,source_url='https://image.tmdb.org/t/p/w1280/csi.png')
 def test_verified_tmdb_wide_beats_feed_scene_then_official_poster(self):
  tmdb=dict(self.value,url=self.value['source_url'],official_poster86='https://image.tmdb.org/t/p/w500/poster.png');feed=dict(source='xmltv_event',url='https://example.org/scene.png')
  ordered=self.h.ordered([tmdb],[feed]);self.assertEqual([v['source'] for v in ordered],['tmdb_series','xmltv_event','tmdb_series']);self.assertEqual(ordered[-1]['role81'],'poster')
 def test_small_xmltv_and_provider_covers_are_never_hero(self):
  for source in ('xmltv_event','provider_event','tmdb_series'):
   self.assertIsNone(self.h.classify(dict(self.value,source=source,image_width77=160,image_height77=80)))
 def test_verified_official_portrait_has_separate_large_layout_type(self):
  self.assertEqual(self.h.classify(dict(self.value,role81='poster',image_width77=800,image_height77=1200)),('official_poster',2));self.assertIsNone(self.h.classify(dict(self.value,source='provider_event',role81='poster',image_width77=800,image_height77=1200)))
 def test_unconfirmed_candidate_never_becomes_main_hero(self):self.assertIsNone(self.h.classify(dict(self.value,provisional85=True)))
 def bank(self,source='tmdb_series',rank='0'):
  m=importlib.import_module('hero_render86');w=m.window();w.setProperty('XCMate.Hero63.Active','A');w.setProperty(m.PREFIX+'Event',importlib.import_module('event_art81').key(self.e))
  for k,v in dict(Image='/verified/tmdb.png',ArtSource=source,Kind86='hero_backdrop',Rank86=rank).items():w.setProperty('XCMate.Hero63.A.'+k,v)
  return m,w
 def test_csi_null_then_xmltv_thumbnail_does_not_blank_or_downgrade(self):
  m,w=self.bank()
  with mock.patch('event_art81.allowed',return_value=True):
   for art in ({},dict(self.value,source='xmltv_event',image='/small.png',image_width77=160,image_height77=80)):
    result=m.choose(self.e,art,dict(Image='',ArtSource=''),w);self.assertEqual(result['Image'],'/verified/tmdb.png');self.assertEqual(result['ArtSource'],'tmdb_series')
 def test_same_event_upgrade_waits_for_exact_renderer_receipt(self):
  m,w=self.bank('xmltv_event','1')
  with mock.patch('event_art81.allowed',return_value=True):
   self.assertEqual(m.choose(self.e,self.value,{},w)['ArtSource'],'xmltv_event')
   w.setProperty(m.PREFIX+'Ready',json.dumps(dict(key=m.tag(self.e,self.value),at=time.monotonic())))
   self.assertEqual(m.choose(self.e,self.value,{},w)['ArtSource'],'tmdb_series')
 def test_new_event_never_keeps_previous_episode_image(self):
  m,w=self.bank()
  with mock.patch('xbmc.getInfoLabel',return_value='/verified/station.png'):
   result=m.choose(dict(self.e,title='Different work',key='next',start=self.now+1800),{},dict(Image=''),w)
  self.assertEqual(result['Image'],'/verified/station.png');self.assertEqual(result['Kind86'],'station_logo')
 def test_optout_and_revocation_release_last_good(self):
  m,w=self.bank()
  with mock.patch('event_art81.allowed',return_value=False),mock.patch('xbmc.getInfoLabel',return_value='/station.png'):
   self.assertEqual(m.choose(self.e,{},dict(Image=''),w)['ArtSource'],'station_logo')
 def test_texture_url_alone_never_acknowledges_renderer(self):
  m=importlib.import_module('hero_render86')
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[])))):
   m.prepare(self.e,dict(self.value,image=self.value['source_url']))
  self.assertEqual(m.window().getProperty(m.PREFIX+'Pending'),self.value['source_url']);self.assertEqual(m.window().getProperty(m.PREFIX+'Ready'),'')

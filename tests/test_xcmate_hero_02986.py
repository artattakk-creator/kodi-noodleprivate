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

 def test_proved_episode_still_expands_to_verified_work_backdrop_first(self):
  still=dict(source='tmdb_episode',url='https://image.tmdb.org/t/p/w500/still.png',remote_id=100,match='EXACT_SEASON_EPISODE')
  work=dict(source='tmdb',id=100,title='CSI: Vegas',year=2021,role='backdrop',poster='https://image.tmdb.org/t/p/w500/poster.png',url='https://image.tmdb.org/t/p/w500/series.png',work_match85=True)
  with mock.patch('programme_candidates85.details',return_value=work):ordered=self.h.ordered(self.h.expand([still],self.e),[])
  self.assertEqual(ordered[0]['source'],'tmdb_series');self.assertEqual(ordered[1]['source'],'tmdb_episode');self.assertEqual(ordered[2]['role81'],'poster')
  self.assertEqual(ordered[0]['image_scope57'],'series_fallback');self.assertNotIn('episode',ordered[0])

 def test_failed_optional_upgrade_keeps_current_decoded_cold_cache(self):
  self.options.update(programme_helper57=False,programme_catalog57=False)
  event=dict(self.e,xmltv_image='https://image.tmdb.org/t/p/w500/scene.png',placeholder='/neutral.png',genre='Spielfilm',year=2021)
  from programme_art46 import fingerprint
  from programme_requests68 import identity,scope
  cached=dict(self.value,key=event['key'],source='xmltv_event',match='EXACT_EVENT',fingerprint=fingerprint(event),scope69=identity(event),profile69=scope(),until=self.now+3600)
  candidate=dict(url='https://image.tmdb.org/t/p/w500/upgrade.png',source='tmdb_movie',role81='backdrop',match='EXACT_TITLE_YEAR')
  with mock.patch('home_schedule75.applicable',return_value=True),mock.patch('programme_display84.recover',return_value=cached),mock.patch('programme_display84.renew',return_value=None),mock.patch('artwork_display84.observe',return_value=True),mock.patch('event_art81.upgrade',return_value=True),mock.patch('art_trace81.own',return_value=candidate),mock.patch('programme_urls55.probe',side_effect=__import__('media_sources43').SourceError('HTTP_NOT_FOUND')),mock.patch('programme_requests68.completed') as publish:
   value=__import__('programme_urls55').resolve(event,allow_lookup=True,url_mode69=True)
  self.assertEqual(value['image'],cached['image']);self.assertEqual(value['source'],'xmltv_event');self.assertEqual(value['code'],'READY_STALE');publish.assert_called_once()

 def test_typed_role_survives_the_cross_interpreter_status_handoff(self):
  value=dict(self.value,key='e',until=self.now+1800)
  q=__import__('programme_requests68');q.completed(self.e,value)
  self.assertEqual(q.result(self.e)['role81'],'backdrop')
 def test_original_quality_and_kodi_downsample_are_separate_proofs(self):
  m=__import__('hero_render86');value=dict(self.value,image=self.value['source_url'])
  record=dict(width=320,height=180)
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[dict(url=value['image'])])))),mock.patch('widget_cache82.decoded',return_value=record):m.prepare(self.e,value)
  receipt=json.loads(m.window().getProperty(m.PREFIX+'Ready'))
  self.assertEqual((receipt['width'],receipt['decoded_width']),(1280,320))
  with mock.patch('event_art81.allowed',return_value=True),mock.patch('programme_image69.eligible',return_value=True):self.assertEqual(m.choose(self.e,value,{},m.window())['ArtSource'],'tmdb_series')
  m.window().clearProperty(m.PREFIX+'Ready')
  with mock.patch('xbmc.executeJSONRPC',create=True,side_effect=AssertionError('small source is not preloadable')):m.prepare(self.e,dict(value,image_width77=160,image_height77=90))
  self.assertFalse(m.window().getProperty(m.PREFIX+'Ready'))
 def test_wrong_decoded_aspect_cannot_acknowledge_a_different_picture(self):
  m=__import__('hero_render86');value=dict(self.value,image=self.value['source_url'])
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[dict(url=value['image'])])))),mock.patch('widget_cache82.decoded',return_value=dict(width=180,height=320)):m.prepare(self.e,value)
  self.assertFalse(m.window().getProperty(m.PREFIX+'Ready'))

 def test_exact_verified_work_candidate_can_reuse_large_kodi_texture_offline(self):
  m=__import__('hero_render86');url=self.value['source_url'];candidate=dict(source='tmdb_series',role81='backdrop',match='EXACT_UNIQUE_TV_TITLE66',url=url,remote_id=123)
  texture=dict(url=url);record=dict(file='/verified/kodi.png',sha256='a'*64,width=1280,height=720)
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[texture])))),mock.patch('widget_cache82.decoded',return_value=record),mock.patch('socket.getaddrinfo',side_effect=AssertionError('offline cache must not use DNS')):
   value=m.recovered_candidate(self.e,candidate,url)
  self.assertEqual(value['source'],'tmdb_series');self.assertEqual(value['role81'],'backdrop');self.assertEqual(value['image'],'/verified/kodi.png')
  self.assertEqual(value['fingerprint'],__import__('programme_art46').fingerprint(self.e))
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[texture])))),mock.patch('widget_cache82.decoded',return_value=dict(record,width=160,height=90)):
   self.assertIsNone(m.recovered_candidate(self.e,candidate,url))
 def test_disabled_source_or_other_texture_url_cannot_be_recovered(self):
  m=__import__('hero_render86');url=self.value['source_url'];candidate=dict(source='tmdb_series',role81='backdrop',match='EXACT_UNIQUE_TV_TITLE66')
  with mock.patch('event_art81.allowed',return_value=False),mock.patch('xbmc.executeJSONRPC',create=True,side_effect=AssertionError('source is disabled')):self.assertIsNone(m.recovered_candidate(self.e,candidate,url))
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[dict(url='https://image.tmdb.org/t/p/w1280/foreign.png')])))),mock.patch('widget_cache82.decoded',side_effect=AssertionError('foreign texture')):self.assertIsNone(m.recovered_candidate(self.e,candidate,url))

 def test_resolver_reuses_the_current_matched_candidate_before_image_network(self):
  from programme_art46 import fingerprint
  from programme_requests68 import identity,scope
  event=dict(self.e,placeholder='/neutral.png',genre='Spielfilm',year=2021)
  candidate=dict(source='tmdb_movie',role81='backdrop',match='EXACT_TITLE_YEAR',url='https://image.tmdb.org/t/p/w500/current.png',remote_id=123)
  cached=dict(self.value,source='tmdb_movie',key=event['key'],image='/verified/cold.png',fingerprint=fingerprint(event),scope69=identity(event),profile69=scope(),until=self.now+3600)
  with mock.patch('home_schedule75.applicable',return_value=True),mock.patch('artwork_temp85.lookup',return_value=None),mock.patch('event_art81.prior',return_value=None),mock.patch('programme_display84.recover',return_value=None),mock.patch('programme_display84.renew',return_value=None),mock.patch('artwork_display84.observe',return_value=True),mock.patch('art_trace81.own',return_value=candidate),mock.patch('hero_render86.recovered_candidate',return_value=cached) as recovery,mock.patch('programme_urls55.probe',side_effect=AssertionError('cached candidate must not be downloaded again')):
   value=__import__('programme_urls55').resolve(event,allow_lookup=True,url_mode69=True)
  recovery.assert_called_once();self.assertEqual(value['image'],cached['image']);self.assertEqual(value['source'],'tmdb_movie')

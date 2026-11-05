"""Rollover, source invalidation, consent and bounded source retries."""
import importlib,json,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class EpgArt74(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.local=importlib.import_module('local_epg');self.bridge=importlib.import_module('epg_handoff63');self.row=dict(sid='1',name='Synthetic',epg_channel_id='xml')
  self.events={'xml':[dict(name='Current exact programme',descr='Description',start_timestamp=self.now-60,stop_timestamp=self.now+900),dict(name='Actual next programme',start_timestamp=self.now+900,stop_timestamp=self.now+7200)]}
  importlib.import_module('guide_store').import_cache('p',self.events,'synthetic74',now=self.now,trusted_feed=True)
 def read(self):return self.local.now_next('p',[self.row],{},now=self.now)['1']
 def age(self,seconds):
  for key,raw in tuple(self.properties.items()):
   if key.startswith(self.bridge.PREFIX):
    value=json.loads(raw);value['at']-=seconds;self.properties[key]=json.dumps(value)
 def test_active_event_survives_old_three_hundred_second_handoff_expiry(self):
  before=self.read();self.age(301)
  with mock.patch('epg_refresh74.request') as refresh:
   value=self.bridge.get('p','1',now=self.now)
  self.assertEqual(value['now'],before['now']);refresh.assert_called()
 def test_actual_event_rollover_returns_next_instead_of_freezing_old_programme(self):
  self.read();value=self.bridge.get('p','1',now=self.now+901)
  self.assertEqual(value['now'],'Actual next programme')
 def test_after_last_event_end_no_old_title_is_served(self):
  self.read();value=self.bridge.get('p','1',now=self.now+7201);self.assertFalse(value and value.get('now'))
 def test_source_revision_mismatch_is_not_hidden_by_longer_lease(self):
  self.read()
  with mock.patch('epg_status.revision',return_value='changed'):
   self.assertIsNone(self.bridge.get('p','1',now=self.now))
 def test_profile_and_manual_binding_still_invalidate(self):
  self.read()
  with mock.patch('epg_handoff63.profile_scope',return_value='different'):self.assertIsNone(self.bridge.get('p','1',now=self.now))
  self.assertIsNone(self.bridge.get('p','1',now=self.now,mappings={'1':'other'}))
 def test_transient_empty_same_revision_does_not_replace_active_text(self):
  value=self.read();self.bridge.remember('p',self.row,dict(value,now='',events=[]),{})
  self.assertEqual(self.bridge.get('p','1',now=self.now)['now'],value['now'])
 def test_warm_display_lookup_avoids_repeat_sql_and_network(self):
  self.read()
  with mock.patch('local_epg.window',side_effect=AssertionError('REPEATED_SQL')),mock.patch('utils.http_get',side_effect=AssertionError('GUI_HTTP')):
   value=self.local.now_next('p',[self.row],{},now=self.now,display_only65=True)['1']
  self.assertEqual(value['now'],'Current exact programme')
 def test_tmdb_requires_both_existing_consents(self):
  tmdb=importlib.import_module('tmdb_epg60')
  for own,research in ((False,False),(True,False),(False,True)):
   self.options['programme_tmdb46']=own;self.options['tmdb_research43']=research
   with mock.patch('media_sources43.get',side_effect=AssertionError('OPT_OUT_HTTP')):self.assertIsNone(tmdb.candidate(dict(title='Synthetic film',genre='Film',year=2024)))
 def test_tvmaze_optout_never_calls_network(self):
  tv=importlib.import_module('programme_tvmaze67');self.options['programme_tvmaze67']=False
  with mock.patch('media_sources43.get',side_effect=AssertionError('OPT_OUT_HTTP')):self.assertIsNone(tv.candidate(dict(title='Synthetic series',season=1,episode=1)))
 def test_live_sports_news_and_talk_without_genre_are_not_blind_films(self):
  from programme_sources57 import unsuitable69
  for name in ('Live: UEFA Champions League','LIVE Bundesliga','Tagesschau','Nachrichten','Talkshow'):
   self.assertTrue(unsuitable69(dict(title=name)),name)
 def test_preview_layout_has_eight_nonoverlapping_rows_and_larger_image(self):
  from xcmate027_fixture import ADDON
  import xml.etree.ElementTree as E
  tree=E.parse(ADDON/'resources/skins/Default/720p/XCMateGuideGrid.xml')
  import guide_grid_window
  self.assertIn('(920,518,320,180)',__import__('pathlib').Path(guide_grid_window.__file__).read_text())
  for n in tree.findall('.//control'):
   if n.get('id','').isdigit() and 730<=int(n.get('id'))<738:
    self.assertLessEqual(int(n.findtext('top'))+int(n.findtext('height')),518)

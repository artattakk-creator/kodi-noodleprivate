"""Independent source identity, local-only presentation and bounded repair."""
import importlib,sys,types,unittest,time
from unittest import mock
from xcmate027_fixture import Fixture
class Control67:
 def __init__(self,*a,**kw):self.args=a;self.visible=False;self.image='';self.label=''
 def setVisible(self,v):self.visible=v
 def setImage(self,v):self.image=v
 def setLabel(self,v):self.label=v
class Artwork67(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  for name in ('programme_preview67','programme_tvmaze67','programme_refresh63','live_feedback67'):sys.modules.pop(name,None)
 def details(self,**kw):return dict(dict(id=67,name='Synthetic Series',premiered='2020-01-01',image=dict(original='https://static.tvmaze.com/uploads/images/original_untouched/1/67.jpg')),**kw)
 def event(self):return dict(pid='p',sid='1',key='synthetic',title='Synthetic Series',genre='Serie',year=2020,start=self.now-60,stop=self.now+600)
 def lookup(self,responses,event=None):
  from programme_tvmaze67 import candidate
  self.options['programme_tvmaze67']=True
  with mock.patch('media_sources43.get',side_effect=responses):return candidate(event or self.event())
 def test_tvmaze_ambiguous_exact_names_do_not_guess(self):
  from media_sources43 import SourceError
  with self.assertRaises(SourceError):self.lookup([[dict(show=self.details()),dict(show=self.details(id=68))]])
 def test_tvmaze_details_cannot_substitute_another_id(self):
  from media_sources43 import SourceError
  with self.assertRaises(SourceError):self.lookup([[dict(show=self.details())],self.details(id=68)])
 def test_tvmaze_image_host_and_directory_are_pinned(self):
  from media_sources43 import SourceError
  for uri in ('https://private.invalid/1.jpg','http://static.tvmaze.com/uploads/images/original_untouched/1/67.jpg','https://static.tvmaze.com/../../1.jpg'):
   with self.subTest(uri=uri),self.assertRaises(SourceError):self.lookup([[dict(show=self.details())],self.details(image=dict(original=uri))])
 def test_tvmaze_unverified_episode_does_not_receive_a_guessed_image(self):
  from media_sources43 import SourceError
  e=dict(self.event(),season=1,episode=2,subtitle='Exact episode')
  with self.assertRaises(SourceError):self.lookup([[dict(show=self.details())],self.details(),dict(season=1,number=3,name='Other',image=self.details()['image'])],e)
 def test_tvmaze_news_and_sport_do_not_send_title_to_network(self):
  from programme_tvmaze67 import candidate
  self.options['programme_tvmaze67']=True
  with mock.patch('media_sources43.get',side_effect=AssertionError('UNEXPECTED_HTTP')):
   self.assertIsNone(candidate(dict(self.event(),genre='Sportserie')));self.assertIsNone(candidate(dict(self.event(),genre='Nachrichten')))
 def test_old_helper_negative_retry_is_targeted_rate_limited_and_profile_scoped(self):
  from programme_refresh63 import retry67
  self.options.update(programme_tmdb46=True,tmdb_research43=True)
  p=dict(source='placeholder',code='HELPER_TIMEOUT');e=self.event()
  self.assertFalse(retry67(e,dict(source='tmdb_series',code='READY')))
  with mock.patch('epg_handoff63.profile_scope',return_value='A'),mock.patch('programme_refresh63.time.monotonic',return_value=10):
   self.assertTrue(retry67(e,p));self.assertFalse(retry67(e,p))
   self.assertFalse(retry67(dict(e,key='other'),dict(source='placeholder',code='HTTP_RATE_LIMIT')))
  with mock.patch('epg_handoff63.profile_scope',return_value='B'),mock.patch('programme_refresh63.time.monotonic',return_value=10):self.assertTrue(retry67(e,p))
 def preview(self):
  from programme_preview67 import Preview
  gui=sys.modules['xbmcgui'];owner=types.SimpleNamespace(addControls=mock.Mock())
  with mock.patch.object(gui,'ControlImage',Control67,create=True),mock.patch.object(gui,'ControlLabel',Control67,create=True):return Preview(owner,(0,0,160,90))
 def test_preview_gui_does_no_sql_file_read_or_http_and_marks_only_real_tmdb(self):
  import programme_preview67 as m
  preview=self.preview();e=self.event();row=dict(sid='1',name='Synthetic')
  fake_thread=mock.Mock();fake_thread.is_alive.return_value=True;m._thread=fake_thread
  for source,logo in [('tmdb_series',True),('tvmaze_series',False),('xmltv_event',False),('provider_event',False)]:
   with mock.patch('programme_events46.key',return_value='event'),mock.patch('programme_art46.cached',side_effect=AssertionError('GUI_DISK_IO')),mock.patch('programme_events46.describe',side_effect=AssertionError('GUI_SQL_IO')),mock.patch('media_sources43.get',side_effect=AssertionError('GUI_HTTP')):
    preview._key='event';preview._next=time.monotonic()+60
    m._done[preview.token]=('event',dict(code='READY',source=source,image='/synthetic/cached.png'))
    preview.render(self.portal,row,e)
   self.assertTrue(preview.image.visible);self.assertEqual(preview.logo.visible,logo)
  preview.hide();self.assertNotIn(preview.token,m._done);self.assertNotIn(preview.token,m._wanted);self.assertFalse(preview.image.visible);self.assertFalse(preview.logo.visible)
 def test_preview_rejects_urls_placeholders_and_incomplete_images(self):
  from programme_preview67 import eligible
  for art in (dict(code='READY',source='tmdb_series',image='https://image.tmdb.org/foo.jpg'),dict(code='READY',source='placeholder',image='/synthetic/fallback.png'),dict(code='PENDING',source='tmdb_series',image='/synthetic/cached.png'),dict(code='READY',source='tmdb_series',image='/synthetic/cached.png',url_version55=1)):
   self.assertFalse(eligible(art))
 def test_preview_late_result_for_previous_focus_is_not_displayed(self):
  import programme_preview67 as m
  preview=self.preview();m._thread=mock.Mock();m._thread.is_alive.return_value=True
  preview._key='new';preview._next=time.monotonic()+60;m._done[preview.token]=('old',dict(code='READY',source='tmdb_series',image='/wrong.png'))
  with mock.patch('programme_events46.key',return_value='new'):preview.render(self.portal,dict(sid='1',name='Synthetic'),self.event())
  self.assertFalse(preview.image.visible);self.assertFalse(preview.logo.visible)
 def test_official_logo_remains_a_separate_control_at_lower_right(self):
  p=self.preview();self.assertEqual(p.logo.args[:4],(114,66,42,20));self.assertTrue(p.logo.args[4].endswith('resources/media/tmdb60/tmdb.png'))
 def test_own_opted_in_token_supplier_runs_before_optional_helper(self):
  self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_helper57=True,programme_catalog57=False)
  import programme_sources57 as m
  with mock.patch('programme_match46.candidate',return_value=dict(source='tmdb_series')) as own,mock.patch('programme_helper57.lookup',side_effect=AssertionError('HELPER_NOT_REQUIRED')):
   self.assertEqual(next(m.attempts(self.event()))()['source'],'tmdb_series');own.assert_called_once()
 def test_credits_keep_exact_required_attribution_and_official_logo(self):
  from credits67 import ATTRIBUTION
  from xcmate027_fixture import ADDON
  self.assertEqual(ATTRIBUTION,'This product uses the TMDB API but is not endorsed or certified by TMDB.')
  xml=(ADDON/'resources/skins/Default/720p/XCMateCredits67.xml').read_text()
  self.assertIn('tmdb60/tmdb.png',xml)

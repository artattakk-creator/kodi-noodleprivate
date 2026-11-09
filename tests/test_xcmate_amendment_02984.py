"""DS9 precise work fallback, dark panel, bounded logo and ordinary UI text."""
import importlib,unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON
class Amendment84(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_tvmaze67=True,tmdb_read_token43='SYNTHETIC_NOT_A_REAL_TOKEN')
  self.event=dict(pid='p',sid='0',key='synthetic84',title='Star Trek: Deep Space Nine',start=self.now,stop=self.now+3600,genre='')
 def row(self):return dict(id=84,name='Star Trek: Deep Space Nine',original_name='Star Trek: Deep Space Nine',first_air_date='1993-01-03',backdrop_path='/synthetic84.jpg')
 def test_exact_full_ds9_title_without_genre_uses_verified_series_not_invented_episode(self):
  row=self.row()
  with mock.patch('tmdb_connection60.request',side_effect=[dict(total_pages=1,total_results=1,results=[row]),row,dict(total_pages=0,total_results=0,results=[])]) as api:
   value=importlib.import_module('tmdb_epg60').candidate(self.event)
  self.assertEqual(value['image_scope57'],'series_fallback');self.assertEqual(value['source'],'tmdb_series')
  self.assertEqual(value['remote_id'],84);self.assertIn('Serienbild',value['attribution'])
  self.assertTrue(all('/episode/' not in c.args[0] for c in api.call_args_list))
 def test_ds9_ambiguous_year_mismatch_or_inconsistent_details_is_rejected(self):
  from programme_tv66 import candidate
  from media_sources43 import SourceError
  row=self.row()
  with mock.patch('tmdb_connection60.request',return_value=dict(total_pages=1,total_results=2,results=[row,dict(row,id=85)])):
   with self.assertRaises(SourceError):candidate(self.event)
  with mock.patch('tmdb_connection60.request',return_value=dict(total_pages=1,total_results=1,results=[row])):
   with self.assertRaises(SourceError):candidate(dict(self.event,year=2024))
  with mock.patch('tmdb_connection60.request',side_effect=[dict(total_pages=1,total_results=1,results=[row]),dict(row,name='A different show',original_name='A different show')]):
   with self.assertRaises(SourceError):candidate(self.event)
 def test_shortened_title_is_not_automatically_classified_as_ds9(self):
  with mock.patch('tmdb_connection60.request',return_value=dict(total_pages=0,total_results=0,results=[])):
   self.assertIsNone(importlib.import_module('programme_tv66').candidate(dict(self.event,title='Star Trek: Deep Space')))
 def test_tvmaze_fallback_also_requires_independent_exact_series_details(self):
  row=dict(id=84,name=self.event['title'],premiered='1993-01-03',image=dict(original='https://static.tvmaze.com/uploads/images/original_untouched/1/84.jpg'))
  with mock.patch('media_sources43.get',side_effect=[[dict(show=row)],row]):value=importlib.import_module('programme_tvmaze67').candidate(self.event)
  self.assertEqual(value['image_scope57'],'series_fallback');self.assertEqual(value['source'],'tvmaze_series')
 def test_both_explicit_optouts_prevent_api_calls_and_preserve_token(self):
  self.options.update(programme_tmdb_optout77=True,programme_tvmaze_optout77=True)
  with mock.patch('tmdb_connection60.request',side_effect=AssertionError('optout TMDB')),mock.patch('media_sources43.get',side_effect=AssertionError('optout TVmaze')):
   self.assertIsNone(importlib.import_module('programme_tv66').candidate(self.event));self.assertIsNone(importlib.import_module('programme_tvmaze67').candidate(self.event))
  self.assertEqual(self.options['tmdb_read_token43'],'SYNTHETIC_NOT_A_REAL_TOKEN')
 def test_internal_codes_are_available_in_diagnostics_but_not_ordinary_details(self):
  from programme_diagnostics59 import message
  for code in ('KODI_LIBRARY_MISSING_VIEWS','IMAGE_READY','SAFE_RESERVE_BLOCKED','NOT_SCHEDULED'):
   art=dict(code=code,source='placeholder')
   self.assertNotIn(code,message(self.event,art));self.assertIn(code,message(self.event,art,diagnostic=True))
 def test_actual_panel_rgba_is_ninety_percent_navy_and_white_text_has_contrast(self):
  from PIL import Image
  with Image.open(ADDON/'resources/media/panel84.png') as im:r,g,b,a=im.getpixel((0,0))
  self.assertTrue(.85<=a/255<=.92)
  composite=[v*a/255+255*(1-a/255) for v in (r,g,b)]
  self.assertLess(max(composite),65)

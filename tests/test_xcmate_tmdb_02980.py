"""Conservative title/part proofs using synthetic API replies, never real tokens."""
import unittest
from unittest import mock
from xcmate027_fixture import Fixture

class Titles80(Fixture,unittest.TestCase):
 def replies(self,title,official,*,genre='Film',part_two=False,tv_collision=False,remake=False):
  from tmdb_epg60 import candidate
  row=dict(id=8001,title=official,release_date='2014-01-01')
  calls=[]
  def api(url,**kwargs):
   calls.append(url)
   if '/search/tv?' in url:return dict(total_pages=int(tv_collision),total_results=int(tv_collision),results=[dict(id=8002,name=title)] if tv_collision else [])
   if '/search/movie?' in url:return dict(total_pages=1,total_results=2 if remake else 1,results=[row,dict(row,id=8003)] if remake else [row])
   return dict(row,backdrop_path='/synthetic80.jpg')
  event=dict(title=title,genre=genre,start=1000,stop=1000+9900)
  with mock.patch('utils.setting_bool',return_value=True),mock.patch('media_sources43.tmdb_token',return_value='synthetic-test-only'),mock.patch('tmdb_connection60.request',side_effect=api):value=candidate(event)
  return value,calls
 def test_mockingjay_part_one_matches_official_part_without_losing_number(self):
  value,_=self.replies('Die Tribute von Panem – Mockingjay (1)','Die Tribute von Panem – Mockingjay Teil 1')
  self.assertEqual(value['match'],'EXACT_UNIQUE_FILM_TITLE')
 def test_wrong_part_and_yearless_remakes_are_rejected(self):
  value,_=self.replies('Die Tribute von Panem – Mockingjay (1)','Die Tribute von Panem – Mockingjay Teil 2');self.assertIsNone(value)
  value,_=self.replies('Harry Potter und der Feuerkelch','Harry Potter und der Feuerkelch',remake=True);self.assertIsNone(value)
 def test_unknown_movie_genre_requires_complete_tv_exclusion_and_movie_details(self):
  value,calls=self.replies('Harry Potter und der Feuerkelch','Harry Potter und der Feuerkelch',genre='Fantasyabenteuer')
  self.assertEqual(value['source'],'tmdb_movie');self.assertEqual(len(calls),3)
 def test_same_title_tv_collision_prevents_speculative_movie_picture(self):
  value,calls=self.replies('Harry Potter und der Feuerkelch','Harry Potter und der Feuerkelch',genre='Fantasyabenteuer',tv_collision=True)
  self.assertIsNone(value);self.assertEqual(len(calls),1)

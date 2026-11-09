"""Reference-only import stage never fetches picture bodies or mutates archives."""
import importlib,time,json,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Reference84(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.ref=importlib.import_module('programme_reference84')
  self.event=dict(pid=self.portal['id'],sid='1',key='synthetic',title='Synthetic exact movie',year=2024,genre='Film',start=self.now,stop=self.now+3600)
  self.candidate=dict(url='https://image.tmdb.org/t/p/w500/reference84.png',source='tmdb_movie',match='EXACT_TITLE_YEAR',remote_id=841,role81='backdrop')
 def test_xmltv_reference_registration_fetches_neither_image_nor_title_search(self):
  with mock.patch('programme_transport77.verified',side_effect=AssertionError('image download')),mock.patch('art_trace81.own',side_effect=AssertionError('unnecessary API')):
   value=self.ref.resolve(dict(self.event,xmltv_image=self.candidate['url']))
  self.assertEqual(value['candidate']['source'],'xmltv_event');self.assertNotIn('image',value)
 def test_same_production_on_different_channels_and_days_uses_one_metadata_search(self):
  with mock.patch('art_trace81.own',return_value=self.candidate) as api,mock.patch('programme_transport77.verified',side_effect=AssertionError('picture body')):
   self.ref.resolve(self.event)
   value=self.ref.resolve(dict(self.event,sid='2',start=self.now+86400,stop=self.now+90000,key='another-event'))
  self.assertEqual(api.call_count,1);self.assertEqual(value['candidate'],self.candidate)
 def test_different_episode_or_year_never_inherits_work_reference(self):
  self.ref.put(self.event,self.candidate)
  self.assertIsNone(self.ref.get(dict(self.event,year=2025)))
  self.assertIsNone(self.ref.get(dict(self.event,season=1,episode=2)))
 def test_new_token_policy_account_and_optout_do_not_inherit_reference(self):
  self.ref.put(self.event,self.candidate)
  self.options['programme_tmdb_optout77']=True;self.assertIsNone(self.ref.get(self.event))
  self.options['programme_tmdb_optout77']=False
  with mock.patch('portals.get_by_id',return_value=dict(self.portal,xc_pass='changed')):self.assertIsNone(self.ref.get(self.event))
 def test_negative_cache_is_bounded_and_expires(self):
  with mock.patch('art_trace81.own',return_value=None) as tmdb,mock.patch('programme_tvmaze67.candidate',return_value=None):
   self.ref.resolve(self.event);self.ref.resolve(self.event)
   self.assertEqual(tmdb.call_count,1)
  with mock.patch('time.time',return_value=time.time()+3601):self.assertIsNone(self.ref.get(self.event))
 def test_metadata_journal_is_small_private_and_preserves_all_old_image_bytes(self):
  archive=self.folder/'media_art_v1';archive.mkdir();picture=archive/'legacy.img';picture.write_bytes(b'EXISTING_PICTURE')
  for i in range(400):self.ref.put(dict(self.event,title='Unique '+str(i)),self.candidate)
  self.ref.flush();filename=self.ref.path();data=json.loads(filename.read_bytes())
  self.assertLessEqual(filename.stat().st_size,self.ref.MAX_BYTES);self.assertLessEqual(len(data['works']),256)
  self.assertEqual(filename.stat().st_mode&0o777,0o600);self.assertEqual(picture.read_bytes(),b'EXISTING_PICTURE')
  raw=filename.read_text();self.assertNotIn(self.portal['xc_pass'],raw);self.assertNotIn('Unique ',raw)
 def test_pressure_skips_journal_and_no_global_cache_cleanup(self):
  self.ref.put(self.event,self.candidate)
  with mock.patch('artwork_display84.metadata_allowed',return_value=False),mock.patch('tempfile.mkstemp',side_effect=AssertionError('reserve write')):self.ref.flush()
  self.assertFalse(self.ref.path().exists())
 def test_private_or_credential_bearing_image_url_not_journaled(self):
  for url in ('https://127.0.0.1/x.png','https://public.example.org/'+self.portal['xc_pass']+'/x.png','https://public.example.org/x.png?password=secret'):
   self.assertIsNone(self.ref.put(self.event,dict(self.candidate,url=url)))

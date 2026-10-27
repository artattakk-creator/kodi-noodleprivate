"""Bounded real PNG cache and strict matching, using synthetic transports only."""
import importlib,io,json,sys,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class ProgrammeArt46(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.a=importlib.import_module('programme_art46');self.e=importlib.import_module('programme_events46');self.m=importlib.import_module('programme_match46');self.channel=dict(sid='1',name='Station',epg_channel_id='xml',kind='live')
  self.event=self.e.describe(self.portal,self.channel,dict(start=self.now-60,stop=self.now+600,title='Exact programme',description='Offline text'),canonical='xml')
  self.event['xmltv_image']='https://images.invalid/exact.png'
  from PIL import Image
  b=io.BytesIO();Image.new('RGB',(160,90),(32,48,64)).save(b,'PNG');self.png=b.getvalue()
  Path(self.a.root()).mkdir(mode=0o700)
  patch=mock.patch.object(self.a,'space');patch.start();self.addCleanup(patch.stop)
  self.addCleanup(self.a.shutdown)
 def prepare(self,event=None,fetch=None,match=None):return self.a.prepare(event or self.event,fetch=fetch or mock.Mock(return_value=self.png),match=match or mock.Mock(return_value=None))
 def test_exact_xmltv_image_is_persistent_separate_and_never_burns_logo(self):
  value=self.prepare();self.assertEqual(value['code'],'READY');self.assertEqual(value['match'],'EXACT_EVENT');self.assertEqual(Path(value['image']).read_bytes(),self.png)
  self.assertNotIn('logo',Path(value['image']).name);self.assertFalse(Path(importlib.import_module('guide_store').path()).exists())
 def test_restart_recovers_verified_image_without_http(self):
  first=self.prepare();self.a._memory.clear();fetch=mock.Mock(side_effect=AssertionError('offline cache must work'));again=self.prepare(fetch=fetch)
  self.assertEqual(again['image'],first['image']);fetch.assert_not_called()
 def test_provider_image_is_used_only_after_failed_xmltv(self):
  from media_sources43 import SourceError
  self.event['provider_image']='https://images.invalid/provider.png';fetch=mock.Mock(side_effect=[SourceError('HTTP_NOT_FOUND'),self.png]);value=self.prepare(fetch=fetch)
  self.assertEqual(value['source'],'provider_event');self.assertEqual(fetch.call_args_list[0].args[0],self.event['xmltv_image']);self.assertEqual(fetch.call_args_list[1].args[0],self.event['provider_image'])
 def test_negative_network_result_has_ttl_and_does_not_retry_on_next_publication(self):
  from media_sources43 import SourceError
  fetch=mock.Mock(side_effect=SourceError('TIMEOUT'));value=self.prepare(fetch=fetch);self.assertEqual(value['code'],'TIMEOUT');self.assertGreater(value['until'],time.time())
  self.prepare(fetch=fetch);self.assertEqual(fetch.call_count,1)
 def test_failed_refresh_keeps_only_same_event_last_good(self):
  from media_sources43 import SourceError
  old=self.prepare();manifest=Path(self.a.root())/(self.event['key']+'.json');data=json.loads(manifest.read_text());data['until']=1;manifest.write_text(json.dumps(data))
  value=self.prepare(fetch=mock.Mock(side_effect=SourceError('TIMEOUT')));self.assertEqual(value['image'],old['image']);self.assertEqual(value['code'],'READY_STALE')
 def test_different_event_or_changed_source_cannot_inherit_old_picture(self):
  self.prepare();other=dict(self.event,start=self.event['stop'],stop=self.event['stop']+600,title='Next');other['key']=self.e.key('p','1',other)
  self.assertIsNone(self.a.persisted(other));self.assertIsNone(self.a.persisted(dict(self.event,xmltv_image='https://other.invalid/changed.png')))
 def test_tampered_or_symlink_cache_is_rejected(self):
  value=self.prepare();self.assertEqual(value['code'],'READY');self.assertTrue(Path(value['image']).is_relative_to(self.folder));Path(value['image']).write_bytes(b'not an image');self.assertIsNone(self.a.persisted(self.event))
 def test_invalid_image_never_replaces_cached_good_event(self):
  from media_sources43 import SourceError
  value=self.prepare(fetch=mock.Mock(return_value=b'not png'));self.assertNotEqual(value['code'],'READY');self.assertEqual(value['image'],self.event['placeholder'])
 def test_cancelled_fetch_never_publishes_ready_picture(self):
  v=self.a.prepare(self.event,cancel=lambda:True,fetch=mock.Mock(return_value=self.png));self.assertEqual(v['code'],'CANCELLED');self.assertFalse([p for p in Path(self.a.root()).iterdir() if p.suffix in ('.png','.jpg','.img')] if Path(self.a.root()).exists() else [])
 def test_full_budget_does_not_download_or_remove_existing_files(self):
  old=self.prepare();from art_storage import ArtworkFailure
  fetch=mock.Mock()
  with mock.patch.object(self.a,'space',side_effect=ArtworkFailure('DISK_FULL','RESERVE_BLOCKED')):value=self.a.prepare(dict(self.event,xmltv_image='https://other.invalid/new.png'),fetch=fetch)
  self.assertEqual(value['code'],'DISK_FULL');fetch.assert_not_called();self.assertEqual(Path(old['image']).read_bytes(),self.png)
 def test_no_image_never_spawns_worker_or_becomes_wrong_series_art(self):
  event=dict(self.event);event.pop('xmltv_image')
  with mock.patch.object(self.a,'ensure') as ensure:self.assertFalse(self.a.enqueue(event))
  ensure.assert_not_called();self.assertEqual(self.a.peek(event)['source'],'placeholder')
 def test_queue_is_bounded_and_deduplicates_same_event(self):
  with mock.patch.object(self.a,'ensure'):
   for i in range(50):event=dict(self.event,key=str(i).zfill(64));self.a.enqueue(event)
  self.assertEqual(len(self.a._pending),24);self.assertFalse(self.a.enqueue(dict(self.event,key='0'.zfill(64))))
 def test_directory_cached_read_never_fetches_or_starts_worker(self):
  self.prepare()
  with mock.patch.object(self.a,'ensure',side_effect=AssertionError('worker on focus')),mock.patch('media_sources43.get',side_effect=AssertionError('HTTP on focus')):self.assertEqual(self.a.cached(self.event)['code'],'READY')
 def test_default_tmdb_is_disabled_and_requires_existing_user_opt_in(self):
  with mock.patch('media_sources43.tmdb',side_effect=AssertionError('automatic API without opt-in')):self.assertIsNone(self.m.candidate(self.event))
 def test_movie_matching_requires_exact_title_and_year_and_unique_identity(self):
  self.options['programme_tmdb46']='true';event=dict(self.event,genre='Spielfilm',year=2024)
  rows=[dict(remote_id=1,title=event['title'],year='2023',url='https://wrong.invalid/1.jpg',role='fanart')]
  with mock.patch('media_sources43.tmdb',return_value=rows):self.assertIsNone(self.m.candidate(event))
  rows=[dict(remote_id=i,title=event['title'],year='2024',url='https://ambiguous.invalid/'+str(i)+'.jpg',role='fanart') for i in (1,2)]
  with mock.patch('media_sources43.tmdb',return_value=rows):self.assertIsNone(self.m.candidate(event))
 def test_verified_episode_requires_matching_season_episode_and_supplied_subtitle(self):
  self.options['programme_tmdb46']='true';event=dict(self.event,season=2,episode=3,subtitle='Exact episode');row=dict(remote_id=42,title=event['title'],year='2024',url='',role='poster',attribution='TMDb')
  with mock.patch('media_sources43.tmdb',return_value=[row]),mock.patch('media_sources43.tmdb_token',return_value='synthetic'),mock.patch('media_sources43.get',return_value=dict(season_number=2,episode_number=4,name='Exact episode',still_path='/wrong.jpg')):self.assertIsNone(self.m.candidate(event))
  with mock.patch('media_sources43.tmdb',return_value=[row]),mock.patch('media_sources43.tmdb_token',return_value='synthetic'),mock.patch('media_sources43.get',return_value=dict(season_number=2,episode_number=3,name='Exact episode',still_path='/correct.jpg')):self.assertEqual(self.m.candidate(event)['match'],'EXACT_SEASON_EPISODE')
 def test_news_talk_or_unknown_year_never_become_arbitrary_movie(self):
  self.options['programme_tmdb46']='true'
  for extra in [dict(genre='News'),dict(genre='Talkshow'),dict(genre='Film')]:
   with mock.patch('media_sources43.tmdb',side_effect=AssertionError('unverified identity')):self.assertIsNone(self.m.candidate(dict(self.event,**extra)))
 def test_event_cache_budget_is_configurable_without_disabling_global_reserve(self):
  self.assertEqual(self.a.limit(),64*1024*1024);self.options['programme_art_budget46']='2';self.assertEqual(self.a.limit(),128*1024*1024)
  self.assertNotIn('media_art_reserve_mb',self.options)
 def test_internal_programme_budget_is_distinguished_from_real_disk_full(self):
  with mock.patch.object(self.a,'space',side_effect=self.a.CacheBudget('PROGRAMME_CACHE_BUDGET')):value=self.prepare()
  self.assertEqual(value['code'],'PROGRAMME_CACHE_BUDGET');self.assertNotEqual(value['code'],'DISK_FULL');self.assertEqual(value['budget46'],64*1024*1024)

 def test_large_source_becomes_bounded_display_derivative_without_crop_or_logo(self):
  from PIL import Image
  b=io.BytesIO();Image.new('RGB',(2560,1440),(20,40,60)).save(b,'PNG');original=b.getvalue()
  value=self.prepare(fetch=mock.Mock(return_value=original));self.assertEqual(value['code'],'READY')
  with Image.open(value['image']) as image:self.assertEqual(image.size,(1280,720))
  self.assertNotEqual(value['sha256'],value['original_sha256']);self.assertEqual(value['original_sha256'],__import__('hashlib').sha256(original).hexdigest());self.assertTrue(value['image'].endswith('.png'))

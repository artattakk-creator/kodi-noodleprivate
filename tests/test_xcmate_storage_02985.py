"""A: owned-byte lifecycle, reserve failure, immutable archives and state gates."""
import importlib,io,json,os,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
class Storage85(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.module=importlib.import_module('artwork_temp85');self.now85=1000.
  self.cache=self.module.Cache(self.folder/'new85',max_bytes=4096,max_objects=2,clock=lambda:self.now85)
 def png(self,n):
  from PIL import Image
  b=io.BytesIO();Image.new('RGB',(64,32),(n,40,80)).save(b,'PNG');return b.getvalue()
 def test_lru_evicts_only_owned_unpinned_files_and_keeps_archive(self):
  archive=self.folder/'old-archive.png';archive.write_bytes(self.png(99));before=archive.read_bytes()
  a=self.cache.put(self.png(1));self.now85+=1;b=self.cache.put(self.png(2));self.now85+=1;c=self.cache.put(self.png(3))
  self.assertFalse(Path(a['file']).exists());self.assertTrue(Path(b['file']).exists());self.assertTrue(Path(c['file']).exists());self.assertEqual(archive.read_bytes(),before)
  self.assertLessEqual(sum(self.cache.files().values()),4096);self.assertLessEqual(len(self.cache.files()),2)
 def test_pinned_current_and_next_event_cannot_be_evicted_at_limit(self):
  a=self.cache.put(self.png(1),pin='current',pin_until=2000);b=self.cache.put(self.png(2),pin='next',pin_until=2000)
  with self.assertRaisesRegex(OSError,'PINNED'):self.cache.put(self.png(3))
  self.assertEqual(Path(a['file']).read_bytes(),self.png(1));self.assertEqual(Path(b['file']).read_bytes(),self.png(2))
 def test_event_end_plus_grace_expiry_releases_only_unpinned_owned_bytes(self):
  a=self.cache.put(self.png(1),pin='event',pin_until=1060,expires=1060);b=self.cache.put(self.png(2),pin='other',pin_until=2000)
  self.now85=1061;c=self.cache.put(self.png(3));self.assertFalse(Path(a['file']).exists());self.assertTrue(Path(b['file']).exists());self.assertTrue(Path(c['file']).exists())
 def test_no_allocation_or_directory_when_reserve_is_blocked(self):
  def full(n):raise self.module.Unavailable('RESERVE_BLOCKED')
  with self.assertRaises(OSError):self.cache.put(self.png(1),check=full)
  self.assertFalse(self.cache.root.exists())
 def test_foreign_nonempty_namespace_is_not_adopted_or_deleted(self):
  self.cache.root.mkdir();foreign=self.cache.root/'keep.txt';foreign.write_text('user file')
  with self.assertRaises(OSError):self.cache.put(self.png(1))
  self.assertEqual(foreign.read_text(),'user file');self.assertEqual(list(self.cache.root.iterdir()),[foreign])
 def test_symlink_root_and_objects_are_never_followed(self):
  outside=self.folder/'original';outside.mkdir();self.cache.root.symlink_to(outside,target_is_directory=True)
  with self.assertRaises(OSError):self.cache.put(self.png(1))
  self.assertEqual(list(outside.iterdir()),[])
 def test_corrupt_file_is_not_admitted_as_valid_image(self):
  a=self.cache.put(self.png(1));Path(a['file']).write_bytes(b'bad');self.assertIsNone(self.cache.read(a['sha256']))
 def test_object_larger_than_budget_does_not_remove_old_cache(self):
  a=self.cache.put(self.png(1));self.cache.max_bytes=1
  with self.assertRaises(OSError):self.cache.put(self.png(2))
  self.assertEqual(Path(a['file']).read_bytes(),self.png(1))
 def test_cold_read_validates_persisted_manifest_and_full_hash(self):
  a=self.cache.put(self.png(1));cold=self.module.Cache(self.cache.root,clock=lambda:self.now85)
  self.assertEqual(cold.read(a['sha256']),a['file'])
 def test_unknown_hash_named_orphan_counts_but_is_not_deleted(self):
  a=self.cache.put(self.png(1));foreign=self.cache.root/('f'*64+'.png');foreign.write_bytes(self.png(9))
  with self.assertRaises(OSError):self.module.Cache(self.cache.root,max_objects=1,clock=lambda:self.now85).put(self.png(2))
  self.assertEqual(foreign.read_bytes(),self.png(9))

class State85(Fixture,unittest.TestCase):
 def setUp(self):super().setUp();self.loading=importlib.import_module('home_loading85')
 def test_empty_only_after_successful_catalogue_read_not_offline_or_locked(self):
  self.assertEqual(self.loading.update(self.portal,'vod',[],'READY')['state'],'EMPTY')
  for code in ('LOCKED','BUDGET','UNAVAILABLE'):self.assertEqual(self.loading.update(self.portal,'series',[],code)['state'],'ERROR_RETRYABLE')
 def test_actual_job_drives_loading_and_times_out_without_endless_spinner(self):
  with mock.patch('home_loading85.time.monotonic',return_value=100):x=self.loading.update(self.portal,'vod',[],'LOCKED',pending=True)
  self.assertEqual(x['state'],'LOADING_CATALOG');self.assertTrue(x['busy'])
  with mock.patch('home_loading85.time.monotonic',return_value=161):x=self.loading.update(self.portal,'vod',[],'LOCKED',pending=True)
  self.assertEqual(x['state'],'ERROR_RETRYABLE');self.assertFalse(x['busy'])
 def test_partial_to_ready_keeps_layout_and_real_visible_count(self):
  rows=[dict(sid=str(i),name='Title '+str(i)) for i in range(24)]
  self.assertEqual(self.loading.update(self.portal,'vod',rows,'READY',images=3,pending=True)['state'],'READY_PARTIAL')
  self.assertEqual(self.loading.update(self.portal,'vod',rows,'READY',images=12)['state'],'READY')
 def test_cover_viewport_is_bounded_and_moves_with_media_focus(self):
  rows=[dict(sid=str(i)) for i in range(24)]
  with mock.patch('home_schedule75.focus',return_value=dict(pid=self.portal['id'],kind='vod',left=6)):
   self.assertEqual([x['sid'] for x in self.loading.visible(self.portal,'vod',rows)],[str(i) for i in range(6,18)])
 def test_renewing_lease_does_not_invent_new_image_edition(self):
  from widget_snapshot85 import semantic
  a=dict(props={'XCMate.ArtProof69':json.dumps(dict(key='event',source_url='https://image.tmdb.org/t/p/w500/a.jpg',until=100))},art={'poster':'same'})
  b=dict(a,props={'XCMate.ArtProof69':json.dumps(dict(key='event',source_url='https://image.tmdb.org/t/p/w500/a.jpg',until=200))})
  self.assertEqual(semantic(a),semantic(b));self.assertNotEqual(semantic(a),semantic(dict(b,art={'poster':'new'})))
 def test_invalid_file_reason_is_not_presented_as_epg_revision_change(self):
  from programme_revision85 import outcome
  from programme_diagnostics59 import message
  event=dict(pid='p',sid='1',title='Modern Family',start=self.now-30,stop=self.now+100,key='event',code='LOCAL_EVENT')
  with mock.patch('programme_requests68.request',return_value=True):value=outcome(event,{},'FILE_INVALID')
  self.assertEqual(value['code'],'FILE_INVALID');self.assertNotIn('revision',message(event,value).casefold());self.assertNotIn('FILE_INVALID',message(event,value))

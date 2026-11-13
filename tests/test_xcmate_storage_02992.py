"""Real SQLite/filesystem tests; neither mount fixtures nor Linux prove Android."""
import importlib
import json
import os
import sqlite3
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture

class Storage92(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  self.maintenance=importlib.import_module('storage_maintenance92')
  self.metadata=importlib.import_module('storage_metadata92')
  self.policy=importlib.import_module('storage_policy92')
  self.patches=mock.patch('utils.addon_data_dir',return_value=str(self.folder));self.patches.start();self.addCleanup(self.patches.stop)
 def free(self,n):return mock.patch.object(self.metadata.os,'statvfs',return_value=SimpleNamespace(f_bavail=n,f_frsize=1,f_bsize=1))
 def database(self,filename='guide_v1.sqlite',incremental=False):
  file=self.folder/filename;db=sqlite3.connect(file)
  if incremental:db.execute('PRAGMA auto_vacuum=INCREMENTAL')
  db.execute('PRAGMA journal_mode=WAL');db.execute('CREATE TABLE programmes(pid,cid,start,stop,title)');db.execute('CREATE INDEX expiry ON programmes(stop)')
  db.executemany('INSERT INTO programmes VALUES(?,?,?,?,?)', [('p','c',i,i+1,'x'*1000) for i in range(1600)])
  db.commit();db.close();return file
 def test_small_metadata_can_persist_below_bulk_import_reserve(self):
  with self.free(16*1024**2):
   value=self.metadata.check(self.folder/'programme_manual85.json',2048)
   self.assertEqual(value['reserve'],4*1024**2)
   self.assertEqual(self.policy.choose('yes')['image_epg'],'yes')
  self.assertEqual(self.policy.read()['image_epg'],'yes')
 def test_metadata_preserves_floor_and_rejects_large_bulk_or_wrong_scope(self):
  with self.free(4*1024**2):
   with self.assertRaisesRegex(OSError,'RESERVE_BLOCKED'):self.metadata.check(self.folder/'programme_manual85.json',1)
  for file,n,kind in [('guide_v1.sqlite',10,'mapping'),('programme_manual85.json',2*1024**2,'mapping'),('programme_manual85.json',1,'migration')]:
   with self.assertRaisesRegex(OSError,'METADATA_SCOPE_BLOCKED'):self.metadata.check(self.folder/file,n,kind=kind)
 def test_metadata_symlink_target_rejected(self):
  original=self.folder/'user';original.write_text('KEEP');(self.folder/'programme_manual85.json').symlink_to(original)
  with self.assertRaises(OSError):self.metadata.check(self.folder/'programme_manual85.json',1)
  self.assertEqual(original.read_text(),'KEEP')
 def test_legacy_profile_has_no_automatic_image_policy_change(self):
  self.assertEqual(self.policy.read()['image_epg'],'legacy');self.assertTrue(self.policy.images_enabled())
  self.assertFalse(self.policy.path().exists())
 def test_explicit_no_and_later_disable_new_jobs_but_do_not_delete_images(self):
  image=self.folder/'keep.png';image.write_bytes(b'KEEP')
  for value in ('no','later'):
   self.policy.choose(value);self.assertFalse(self.policy.images_enabled());self.assertEqual(image.read_bytes(),b'KEEP')
 def test_invalid_policy_fails_closed_without_replacing_user_file(self):
  self.policy.path().write_text('{broken');self.assertFalse(self.policy.images_enabled())
  self.assertEqual(self.policy.path().read_text(),'{broken')
 def test_only_week_old_exact_closed_owned_temp_is_removed(self):
  cache=self.folder/'cache';cache.mkdir();old=cache/('.xcmate-cache-'+'a'*32);old.write_bytes(b'x'*8192);os.utime(old,(0,0))
  protect=[]
  for name in ('a.json','.xcmate-cache-short','.manual85-'+32*'b','.xcmate-cache-'+32*'b'):
   path=cache/name;path.write_text('KEEP');protect.append(path)
  result=self.maintenance.expire_temp(lambda:False,time.time())
  self.assertEqual(result,dict(files=1,bytes=8192));self.assertFalse(old.exists())
  self.assertTrue(all(p.read_text()=='KEEP' for p in protect))
 def test_open_owned_temp_is_protected(self):
  cache=self.folder/'cache';cache.mkdir();file=cache/('.xcmate-cache-'+'c'*32);file.write_text('KEEP');os.utime(file,(0,0))
  with file.open('rb'):
   self.assertEqual(self.maintenance.expire_temp(lambda:False,time.time())['files'],0)
  self.assertTrue(file.exists())
 def test_symlink_cache_cannot_delete_external_files(self):
  other=self.folder/'other';other.mkdir();(self.folder/'cache').symlink_to(other,target_is_directory=True)
  original=other/('.xcmate-cache-'+'a'*32);original.write_text('KEEP');os.utime(original,(0,0))
  with self.assertRaises(OSError):self.maintenance.expire_temp(lambda:False,time.time())
  self.assertEqual(original.read_text(),'KEEP')
 def test_retention_deletes_bounded_old_rows_keeps_referenced_and_future(self):
  file=self.database();result=self.maintenance.expire_epg(file,('programmes',),1000,{(0,1)},limit=128,seconds=2)
  self.assertEqual(result['rows'],127);self.assertEqual(result['code'],'MORE')
  with sqlite3.connect(file) as db:
   self.assertEqual(db.execute('SELECT count(*) FROM programmes').fetchone()[0],1473)
   self.assertTrue(db.execute('SELECT 1 FROM programmes WHERE start=0').fetchone())
   self.assertTrue(db.execute('SELECT 1 FROM programmes WHERE start=1500').fetchone())
 def test_sqlite_busy_is_reported_without_database_replacement(self):
  file=self.database();before=file.read_bytes()
  with sqlite3.connect(file) as db:
   db.execute('BEGIN IMMEDIATE');result=self.maintenance.expire_epg(file,('programmes',),1000,set(),seconds=.2)
   self.assertEqual(result['code'],'SQLITE_BUSY_OR_BUDGET');self.assertEqual(result['rows'],0)
  self.assertEqual(file.read_bytes(),before)
 def test_retention_never_unlinks_live_wal_or_forces_vacuum(self):
  file=self.database();withheld=file.with_name(file.name+'-user-backup');withheld.write_bytes(b'KEEP')
  with sqlite3.connect(file) as reader:
   reader.execute('BEGIN');reader.execute('SELECT * FROM programmes').fetchone()
   result=self.maintenance.expire_epg(file,('programmes',),1000,set(),limit=50,seconds=2)
   self.assertEqual(result['full_vacuum'],'NOT_RUN');self.assertTrue(Path(str(file)+'-wal').exists())
  self.assertEqual(withheld.read_bytes(),b'KEEP')
 def test_incremental_compaction_is_only_used_on_incremental_databases(self):
  file=self.database(incremental=True);result=self.maintenance.expire_epg(file,('programmes',),1600,set(),limit=2000,seconds=2)
  self.assertEqual(result['rows'],1600);self.assertIn('observed_file_delta',result)
  with sqlite3.connect(file) as db:self.assertEqual(db.execute('PRAGMA quick_check').fetchone()[0],'ok')
 def test_journal_failure_prevents_any_cleanup(self):
  with mock.patch.object(self.maintenance,'journal',side_effect=OSError('READ_ONLY')),mock.patch('artwork_migration.busy',return_value=False),mock.patch.object(self.maintenance,'expire_temp') as cleanup:
   with self.assertRaises(OSError):self.maintenance.run()
   cleanup.assert_not_called()
 def test_reminders_and_timers_are_read_only_retention_references(self):
  (self.folder/'reminders.json').write_text(json.dumps([dict(start=2,stop=3)]))
  with sqlite3.connect(self.folder/'guide_timers_v1.sqlite') as db:
   db.execute('CREATE TABLE timers(start,stop)');db.execute('INSERT INTO timers VALUES(4,5)')
  self.assertEqual(self.maintenance.reference_intervals(),{(2,3),(4,5)})
 def test_corrupt_reference_source_prevents_retention(self):
  (self.folder/'reminders.json').write_text('{bad')
  with self.assertRaises(ValueError):self.maintenance.reference_intervals()
 def test_reboot_gate_rejects_addon_restart_and_allows_new_kodi_process(self):
  module=importlib.import_module('storage_transfer92');value=dict(storage92=dict(render_boot='a'*64))
  with mock.patch.object(module,'boot',return_value='a'*64):
   with self.assertRaisesRegex(OSError,'REBOOT_READBACK_REQUIRED'):module.require_reboot(value)
  with mock.patch.object(module,'boot',return_value='b'*64):module.require_reboot(value)
 def test_original_cleanup_names_cannot_escape_or_target_databases(self):
  module=importlib.import_module('storage_transfer92');backend=SimpleNamespace(root=str(self.folder))
  for kind,ident in [('media','../guide_v1.sqlite'),('programme87','guide_v1.sqlite'),('other','a'*64)]:
   with self.assertRaises(OSError):module.original_path(backend,dict(kind=kind,ident=ident))
  self.assertEqual(module.original_path(backend,dict(kind='programme87',ident='blob46-'+'a'*64+'.jpg')),str(self.folder/('blob46-'+'a'*64+'.jpg')))
 def test_snapshot_keeps_metadata_and_limits_duplicate_horizon(self):
  module=importlib.import_module('epg_snapshot92');events=[dict(start_timestamp=i*3600,stop_timestamp=(i+1)*3600,title='T',xmltv_image='https://image.invalid/x') for i in range(200)]
  short=module.short({'c':events},now=100*3600)
  self.assertLessEqual(len(short['c']),12);self.assertTrue(all(e['xmltv_image'] for e in short['c']))
  self.assertEqual(len(events),200)
 def test_inventory_protects_kodi_and_does_not_follow_symlinks(self):
  module=importlib.import_module('storage_inventory92');file=self.folder/'guide_v1.sqlite';file.write_bytes(b'A'*16384)
  link=self.folder/'cache';link.symlink_to(self.folder,target_is_directory=True)
  result=module.size(link,time.monotonic()+1);self.assertEqual(result['bytes'],0)
  self.assertEqual(module.size(file,time.monotonic()+1)['bytes'],16384)

class Integration92(Fixture,unittest.TestCase):
 def test_manual_tmdb_mapping_survives_low_space_and_cold_restart_without_token_change(self):
  mapping=importlib.import_module('programme_mapping85');metadata=importlib.import_module('storage_metadata92')
  event=dict(pid='p',sid='1',title='Ghosts',canonical='xml',start=self.now,stop=self.now+3600)
  candidate=dict(source='tmdb',id=1,title='Ghosts',verified85=True,year=2019,media_type86='tv',url='https://image.tmdb.org/t/p/w1280/ghosts.jpg',role='backdrop')
  self.options['tmdb_read_token43']='SYNTHETIC_PRIVATE_TEST_VALUE';before=dict(self.options)
  with mock.patch.object(metadata.os,'statvfs',return_value=SimpleNamespace(f_bavail=16*1024**2,f_frsize=1,f_bsize=1)),mock.patch('programme_urls55.safe',return_value=True):
   self.assertTrue(mapping.set_mapping(event,candidate,operation89='a'*32))
  saved=mapping.path().read_bytes();self.properties.clear();mapping._loaded.clear()
  self.assertTrue(mapping.reload());self.assertEqual(mapping.current(event)['id'],1)
  self.assertEqual(mapping.path().read_bytes(),saved);self.assertEqual(self.options,before)
 def test_home_filter_selects_provider_ids_only_and_leaves_library_and_other_portals_intact(self):
  module=importlib.import_module('home_filter92');policy=importlib.import_module('widget_policy74')
  before={p.name:p.read_bytes() for p in self.folder.iterdir() if p.is_file()};baseline=policy.signature(self.portal,'vod');live=policy.signature(self.portal,'live')
  module.save('p',['adult-safe-id','films'])
  self.assertEqual(module.allowed('p',{'adult','sport','adult-safe-id','films'}),{'adult-safe-id','films'})
  self.assertEqual(module.allowed('other',{'adult','sport'}),{'adult','sport'})
  self.assertNotEqual(policy.signature(self.portal,'vod'),baseline);self.assertEqual(policy.signature(self.portal,'live'),live)
  self.assertEqual(before,{p.name:p.read_bytes() for p in self.folder.iterdir() if p.is_file()})
  # Unknown new categories wait for an explicit user selection.
  self.assertEqual(module.allowed('p',{'brand-new','films'}),{'films'})
 def test_home_filter_uses_real_widget_sql_without_modifying_movie_library(self):
  from widget_movie47 import MovieReader
  from library_index import Reader
  self.index.replace_catalog('p','vod',[dict(stream_id='1',category_id='films',name='Ordinary film',added=1),dict(stream_id='2',category_id='adult',name='Adult film',added=2)],[dict(category_id='films',category_name='Filme'),dict(category_id='adult',category_name='Adult')],revision_id='filter92')
  module=importlib.import_module('home_filter92');module.save('p',['films'])
  reader=MovieReader('p')
  try:self.assertEqual([row['name'] for row in reader.small('vod')],['Ordinary film'])
  finally:reader.close()
  self.assertEqual({row['name'] for row in Reader('p').page('vod')[0]},{'Ordinary film','Adult film'})
 def test_busy_mapping_has_distinct_safe_error_without_losing_previous_assignment(self):
  import contextlib
  requests=importlib.import_module('work_requests86');mapping=importlib.import_module('programme_mapping85')
  event=dict(pid='p',sid='1',title='Monk',canonical='xml',start=self.now,stop=self.now+3600)
  candidate=dict(source='tmdb',id=1,title='Monk',verified85=True,year=2002,media_type86='tv',url='https://image.tmdb.org/t/p/w1280/monk.jpg',role='backdrop')
  with mock.patch('programme_urls55.safe',return_value=True):mapping.set_mapping(event,candidate)
  before=mapping.path().read_bytes()
  @contextlib.contextmanager
  def busy(*args,**kw):raise TimeoutError('private profile detail');yield
  with mock.patch.object(requests,'authoritative',return_value=event),mock.patch('profile_transaction.writing',busy):
   nonce=requests.request(event,'save',action='hide');requests.drain()
  self.assertEqual(requests.result(nonce)['code'],'PROFILE_BUSY');self.assertEqual(mapping.path().read_bytes(),before)

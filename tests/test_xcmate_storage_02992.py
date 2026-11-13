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
 def test_same_volume_free_sample_movement_keeps_lowest_without_borrowing_space(self):
  module=importlib.import_module('art_storage82');unit=4096;total=8*1024**3
  def sample(n):return SimpleNamespace(f_frsize=unit,f_bsize=unit,f_bavail=n//unit,f_blocks=total//unit)
  usage=SimpleNamespace(total=total,free=100*1024**2)
  with mock.patch.object(module.shutil,'disk_usage',return_value=usage),mock.patch.object(module.os,'statvfs',side_effect=[sample(98*1024**2),sample(97*1024**2)]):
   result=module.capacity(str(self.folder))
  self.assertEqual(result['capacity82'],'SAME_VOLUME_VERIFIED');self.assertEqual(result['free'],97*1024**2)
  with mock.patch.object(module.os,'statvfs',return_value=sample(98*1024**2)):
   self.assertEqual(module.capacity(str(self.folder),usage)['capacity82'],'CAPACITY_DISAGREEMENT')
  with mock.patch.object(module.shutil,'disk_usage',return_value=usage),mock.patch.object(module.os,'statvfs',return_value=sample(50*1024**2)):
   self.assertEqual(module.capacity(str(self.folder))['capacity82'],'CAPACITY_DISAGREEMENT')
 def test_playback_headers_preserve_local_vfs_and_rtsp_paths_and_http_auth_headers(self):
  import player
  for uri in ('/root/navigation90.mp4','/storage/emulated/0/Movies/a film.mp4','special://profile/video.mp4','smb://fixture/video.mp4','rtsp://fixture/live','rtmp://fixture/live options'):
   self.assertEqual(player._build_header_string(uri,{'Referer':'https://fixture.invalid'}),(uri,''))
  base,headers=player._build_header_string('https://fixture.invalid/live.ts|Referer=https%3A%2F%2Ffixture.invalid',{'User-Agent':'synthetic92'})
  self.assertEqual(base,'https://fixture.invalid/live.ts');self.assertIn('User-Agent=synthetic92',headers);self.assertIn('Referer=https%3A%2F%2Ffixture.invalid',headers)
 def test_cleanup_audits_before_journal_and_mutation_and_preserves_idle_shortcut(self):
  seen=[];snapshot=dict(at=1,categories=[],measurement='READ_ONLY')
  with mock.patch('storage_inventory92.collect',side_effect=lambda *a,**kw:seen.append('audit') or snapshot),mock.patch.object(self.maintenance,'journal',side_effect=lambda record:seen.append(('journal',record.get('inventory_before')))),mock.patch('artwork_migration.busy',return_value=False),mock.patch.object(self.maintenance,'expire_temp',side_effect=lambda *a:seen.append('delete') or dict(files=0,bytes=0)):
   result=self.maintenance.run(force=True)
  self.assertEqual(seen[:3],['audit',('journal',snapshot),'delete']);self.assertEqual(result['inventory_before'],snapshot)
  with mock.patch.object(self.maintenance,'read',return_value=dict(version=self.maintenance.VERSION,state='DONE',at=time.time())),mock.patch('storage_inventory92.collect',side_effect=AssertionError('idle rescan')):
   self.assertEqual(self.maintenance.run()['state'],'DONE')
 def test_usb_audit_precedes_prepare_without_changing_source_identity(self):
  seen=[];module=importlib.import_module('storage_transfer92');snapshot=dict(at=1,categories=[])
  with mock.patch('storage_inventory92.collect',side_effect=lambda **kw:seen.append('audit') or snapshot),mock.patch('artwork_migration.begin',side_effect=lambda *a,**kw:seen.append('begin') or dict(stage='PREPARED')) as begin:
   result=module.prepare('/synthetic-usb',confirmed=True)
  self.assertEqual(seen,['audit','begin']);self.assertEqual(result['inventory_before'],snapshot);self.assertNotIn('inventory_before',begin.call_args.kwargs)
 def test_selected_normalized_cache_inventory_never_uses_write_probe(self):
  module=importlib.import_module('storage_inventory92');self.options['cache_dir']=str(self.folder/'custom-cache')
  with mock.patch('utils.cache_dir',side_effect=AssertionError('inventory must not write')):
   roots=module.roots()
  self.assertIn(('SELECTED_NORMALIZED_CACHE',self.folder/'custom-cache',False),roots);self.assertFalse((self.folder/'custom-cache').exists())
 def free(self,n):return mock.patch.object(self.metadata.os,'statvfs',return_value=SimpleNamespace(f_bavail=n,f_frsize=1,f_bsize=1))
 def database(self,filename='guide_v1.sqlite',incremental=False):
  file=self.folder/filename;db=sqlite3.connect(file)
  if incremental:db.execute('PRAGMA auto_vacuum=INCREMENTAL')
  db.execute('PRAGMA journal_mode=WAL');db.execute('CREATE TABLE programmes(pid,cid,start,stop,title)');db.execute('CREATE INDEX expiry ON programmes(stop)')
  db.executemany('INSERT INTO programmes VALUES(?,?,?,?,?)', [('p','c',i,i+1,'x'*1000) for i in range(1600)])
  db.commit();db.close();return file
 def test_failed_bulk_reserve_creates_no_empty_epg_or_catalogue_database(self):
  for name,file in [('guide_store','guide_v1.sqlite'),('library_index','library_v1.sqlite')]:
   module=importlib.import_module(name);target=self.folder/('new92-'+file)
   with mock.patch('import_budget.check_space',side_effect=OSError('RESERVE_BLOCKED')),self.assertRaises(OSError):module.connect(str(target),write=True)
   self.assertFalse(target.exists())
 def test_legacy_bookmark_without_timer_is_a_protected_reference(self):
  (self.folder/'guide_bookmarks_v1.json').write_text(json.dumps({'old':dict(start=1,stop=2)}))
  self.assertIn((1,2),self.maintenance.reference_intervals())
 def test_genuinely_fresh_profile_defers_image_epg_but_existing_fresh_origin_is_preserved(self):
  import tempfile
  config=importlib.import_module('artwork_config')
  with tempfile.TemporaryDirectory() as folder,mock.patch('utils.addon_data_dir',return_value=folder):
   self.assertEqual(config.initialize()['origin'],'FRESH');self.assertEqual(self.policy.read()['image_epg'],'later')
   self.assertFalse(self.policy.images_enabled())
   self.policy.path().unlink()  # Simulate the older .91 FRESH-origin profile without .92 policy.
   self.assertEqual(config.initialize()['origin'],'FRESH');self.assertEqual(self.policy.read()['image_epg'],'legacy')
 def test_slow_initial_gui_publication_cannot_block_concurrent_marker_readers(self):
  import threading,tempfile
  fresh=tempfile.TemporaryDirectory();self.addCleanup(fresh.cleanup)
  root_patch=mock.patch('utils.addon_data_dir',return_value=fresh.name);root_patch.start();self.addCleanup(root_patch.stop)
  config=importlib.import_module('artwork_config');entered=threading.Event();release=threading.Event();rows=[];errors=[]
  def publish(enabled):
   self.assertFalse(enabled);entered.set();release.wait(2)
  def initialize():
   try:rows.append(config.initialize())
   except Exception as error:errors.append(type(error).__name__)
  with mock.patch.object(self.policy,'publish',side_effect=publish):
   first=threading.Thread(target=initialize);first.start()
   try:
    self.assertTrue(entered.wait(1));self.assertEqual(config.read()['version'],config.VERSION)
    self.assertEqual(self.policy.read()['image_epg'],'later')
    others=[threading.Thread(target=initialize) for _ in range(3)]
    for thread in others:thread.start()
    for thread in others:thread.join(.4)
    self.assertFalse(any(thread.is_alive() for thread in others));self.assertEqual(errors,[]);self.assertEqual(len(rows),3)
   finally:release.set();first.join(1)
  self.assertEqual(len(rows),4);self.assertTrue(all(row==rows[0] for row in rows));self.assertEqual(rows[0]['mode'],'dynamic')
 def test_explicit_deactivation_rejects_new_gui_intent_without_touching_lastgood(self):
  request=importlib.import_module('programme_requests68');event=dict(pid='p',sid='1',title='Monk',start=self.now,stop=self.now+100)
  self.policy.choose('no');self.assertFalse(request.request(event))
  self.policy.choose('yes');self.assertTrue(request.request(event))
 def test_short_snapshot_cannot_lose_current_programme_behind_dense_past(self):
  short=importlib.import_module('epg_snapshot92').short
  events=[dict(name=str(i),start_timestamp=i*60,stop_timestamp=(i+1)*60) for i in range(100)]
  result=short({'channel':events},now=90*60+1)['channel']
  self.assertIn('90',[e['name'] for e in result]);self.assertIn('91',[e['name'] for e in result])
  self.assertLessEqual(len(result),7)
 def test_short_snapshot_for_3357_channels_keeps_now_next_and_bounds_duplicate_text(self):
  import json
  short=importlib.import_module('epg_snapshot92').short
  events=[dict(name=str(i),start_timestamp=i*60,stop_timestamp=(i+1)*60,description='x'*4096,xmltv_image='https://image.invalid/source.jpg') for i in range(30)]
  data={str(i):events for i in range(3357)};result=short(data,now=10*60+1)
  self.assertEqual(len(result),3357);self.assertTrue(all([r['name'] for r in rows]==['10','11'] for rows in result.values()))
  self.assertLess(len(json.dumps(result).encode()),8*1024**2);self.assertEqual(len(events[10]['description']),4096)
 def test_manual_candidate_manager_accepts_real_reader_api_without_close_method(self):
  manager=importlib.import_module('series_requests85')
  event=dict(pid='p',sid='1',title='Monk',canonical='xml',start=self.now,stop=self.now+100)
  reader=lambda pid:SimpleNamespace(get=lambda kind,sid:dict(sid=sid,name='Station'))
  with mock.patch('programme_mapping85.namespace',return_value='same-scope'),mock.patch('programme_mapping85.refresh_sources'),mock.patch('library_index.Reader',reader),mock.patch('programme_events46.load',return_value=dict(event,code='LOCAL_EVENT')),mock.patch('programme_candidates85.search',return_value=([],True)) as search:
   nonce=manager.request(event);manager.drain()
  search.assert_called_once();self.assertEqual(manager.result(nonce)['code'],'READY')
 def test_92_transfer_verifies_programme_files_restart_and_explicit_dynamic_original_cleanup(self):
  import test_xcmate_storage_02937 as baseline
  fixture=baseline.Storage37(methodName='runTest');fixture.setUp();self.addCleanup(fixture.doCleanups)
  fixture.seed(2);source=fixture.m.folder;programme=source/'programme_images46';programme.mkdir(exist_ok=True)
  # Legacy VFS copy fixture did not need Kodi's native path translator.
  # Give read-only inventory separate nonexistent Kodi roots, never a mock snapshot.
  fixture.vfs.translatePath=lambda uri:str(source/'synthetic-kodi-inventory'/__import__('hashlib').sha256(uri.encode()).hexdigest())
  ident='blob46-'+'c'*64+'.png';(programme/ident).write_bytes(fixture.m.png)
  protected=source/'guide-protected.sqlite';protected.write_bytes(b'PROTECTED')
  with fixture.config.locked():
   initial=dict(fixture.config.read(),mode='dynamic');initial.pop('archive_mode',None);fixture.config._write(initial)
  self.assertEqual(fixture.config.read()['mode'],'dynamic')
  proof=dict(volume='separate-fixture-volume',mount_key='separate-fixture-mount',rows=[],code='SEPARATE_POOL_VERIFIED')
  migration=fixture.migration
  def probe(target,profile,**options):
   fixture.vfsmod.prepare_target(target,profile);return proof
  with mock.patch('android_artwork87.preflight',return_value=proof),mock.patch('android_artwork87.probe',side_effect=probe),mock.patch('storage_transfer92.boot',return_value='a'*64):
   migration.begin(str(fixture.external),shared=True,confirmed=True,strict87=True,reboot92=True)
   migration.copy();self.assertTrue(migration.verify());migration.approve_render(True)
   with self.assertRaisesRegex(OSError,'REBOOT_READBACK_REQUIRED'):migration.activate()
  self.assertTrue((programme/ident).exists())
  with mock.patch('android_artwork87.preflight',return_value=proof),mock.patch('storage_transfer92.boot',return_value='b'*64):
   self.assertTrue(migration.activate());self.assertTrue((programme/ident).exists())
   transfer=migration.status()['transfer'];report=migration.cleanup_report(transfer)
  self.assertGreater(report['image_bytes_unlinked'],0)
  self.assertFalse((programme/ident).exists());self.assertEqual(protected.read_bytes(),b'PROTECTED')
  target=__import__('programme_storage87').target(str(fixture.external),fixture.profile)
  self.assertEqual(target.read(ident,100000),fixture.m.png)
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
  for raw in ('{broken','[]','null'):
   self.policy.path().write_text(raw);self.assertFalse(self.policy.images_enabled())
   self.assertEqual(self.policy.path().read_text(),raw)
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
   self.assertEqual(result['code'],'SQLITE_BUSY');self.assertEqual(result['rows'],0)
  self.assertEqual(file.read_bytes(),before)
 def test_retention_never_unlinks_live_wal_or_forces_vacuum(self):
  file=self.database(incremental=True);withheld=file.with_name(file.name+'-user-backup');withheld.write_bytes(b'KEEP')
  with sqlite3.connect(file) as reader:
   reader.execute('BEGIN');reader.execute('SELECT * FROM programmes').fetchone()
   result=self.maintenance.expire_epg(file,('programmes',),1000,set(),limit=50,seconds=2)
   self.assertEqual(result['full_vacuum'],'NOT_RUN');self.assertTrue(Path(str(file)+'-wal').exists())
   self.assertEqual(result['code'],'WAL_BUSY')
   self.assertEqual(reader.execute('SELECT count(*) FROM programmes').fetchone()[0],1600)
  reader.close()
  self.assertEqual(withheld.read_bytes(),b'KEEP')
 def test_incremental_compaction_is_only_used_on_incremental_databases(self):
  file=self.database(incremental=True)
  with sqlite3.connect(file) as db:
   before_pages=db.execute('PRAGMA page_count').fetchone()[0];page_size=db.execute('PRAGMA page_size').fetchone()[0]
  before_bytes=file.stat().st_size
  from import_budget import check_space
  with mock.patch('import_budget.check_space',wraps=check_space) as reserved:
   result=self.maintenance.expire_epg(file,('programmes',),1600,set(),limit=2000,seconds=2)
  self.assertGreaterEqual(reserved.call_args.args[1],128*page_size+65536)
  self.assertEqual(result['rows'],1600);self.assertIn('observed_file_delta',result)
  with sqlite3.connect(file) as db:
   self.assertEqual(db.execute('PRAGMA quick_check').fetchone()[0],'ok')
   self.assertEqual(before_pages-db.execute('PRAGMA page_count').fetchone()[0],128)
  self.assertEqual(before_bytes-file.stat().st_size,128*page_size)
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

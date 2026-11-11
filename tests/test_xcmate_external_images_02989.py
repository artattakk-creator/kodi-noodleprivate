"""Real files + Kodi-VFS model; no real USB/SD/NAS or Android PASS claimed."""
import hashlib,json,sys,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
from artwork37_vfs_fixture import VFS
from test_xcmate_02988 import png

class External89(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.module=__import__('external_art89');self.config=__import__('artwork_config');self.config.initialize()
  self.root=self.folder/'external';self.root.mkdir();self.vfs=VFS(self.root)
  self.vfs.translatePath=sys.modules['xbmcvfs'].translatePath
  self.row=dict(sid='1',name='Media',year='2026',cover='https://images.example.org/one.png',stream_icon='https://images.example.org/logo.png')
 def activate(self,smb=False):
  target='smb://fixture.invalid/share' if smb else str(self.root)
  if smb:
   patch=mock.patch.dict(sys.modules,{'xbmcvfs':self.vfs});patch.start();self.addCleanup(patch.stop)
  migration=__import__('artwork_migration');migration.begin(target);migration.copy();self.assertTrue(migration.verify());migration.approve_render(True);self.assertTrue(migration.activate())
  return target
 def test_explicit_usb_or_sd_target_has_verified_logos_and_movie_series_covers(self):
  target=self.activate();logo,facts=__import__('logo_store89').persist(self.portal,self.row,png((200,100)))
  self.assertTrue(logo.startswith(target));self.assertEqual(Path(logo).read_bytes(),png((200,100)))
  for kind in ('vod','series'):
   __import__('poster_store89').store(self.portal,kind,self.row,'poster',self.row['cover'],png((300,450)))
   uri=__import__('poster_store89').read(self.portal,kind,[self.row])['1']['poster'];self.assertTrue(uri.startswith(target));self.assertTrue(Path(uri).is_file())
  self.assertEqual(__import__('logo_manifest86').read(self.portal,[self.row],with_fallback=False)['1'],logo)
 def test_smb_uses_existing_vfs_unknown_capacity_and_reader_never_performs_remote_io(self):
  self.activate(True)
  import art_storage82
  measured=art_storage82.capacity
  def only_metadata(path,*a,**kw):
   self.assertEqual(str(path),str(self.folder),'only the separate local receipt may measure userdata');return measured(path,*a,**kw)
  with mock.patch('art_storage82.capacity',side_effect=only_metadata):
   logo,facts=__import__('logo_store89').persist(self.portal,self.row,png((200,100)))
   self.assertIsNone(facts['free']);self.assertTrue(logo.startswith('smb://'))
  __import__('poster_store89').store(self.portal,'vod',self.row,'poster',self.row['cover'],png((300,450)))
  with mock.patch.object(self.vfs,'File',side_effect=AssertionError('GUI must not read NAS')),mock.patch.object(self.vfs,'exists',side_effect=AssertionError('GUI must not stat NAS')):
   self.assertEqual(__import__('logo_manifest86').read(self.portal,[self.row],with_fallback=False)['1'],logo)
   self.assertTrue(__import__('poster_store89').read(self.portal,'vod',[self.row])['1']['poster'].startswith('smb://'))
 def test_offline_or_removed_mount_never_creates_internal_image_fallback_or_changes_choice(self):
  target=self.activate(True);before=self.config.read();self.vfs.online=False
  with self.assertRaises(OSError):__import__('logo_store89').persist(self.portal,self.row,png((200,100)))
  self.assertEqual(self.config.read(),before);self.assertEqual(before['target'],target);self.assertFalse((self.folder/'tv_logos').exists())
 def test_partial_smb_transfer_never_publishes_a_receipt(self):
  self.activate(True);self.vfs.short_copy=True
  with self.assertRaises(OSError):__import__('poster_store89').store(self.portal,'vod',self.row,'poster',self.row['cover'],png((300,450)))
  self.assertFalse(self.module.references(self.portal,'vod',[self.row]))
 def test_programme_bytes_recover_to_existing_decoded_bridge_with_account_event_and_consent_checks(self):
  self.activate(True);self.options.update(programme_tmdb46=True,tmdb_research43=True)
  event=dict(pid='p',sid='1',canonical='xml',title='Monk',start=int(time.time())-60,stop=int(time.time())+1800,key='event89')
  value=dict(source='tmdb_series',match='EXACT_UNIQUE_TV_TITLE66',role81='backdrop',source_url='https://image.tmdb.org/t/p/w1280/a.png')
  proof=__import__('event_cache88').receipt(value);body=png((960,540));key=__import__('programme_lock89').key(event)
  self.module.store('programme',key,body,dict(proof=proof));self.addCleanup(__import__('decoded_assets88').shutdown)
  result=self.module.recover_programme(event);self.assertTrue(result['decoded88']);self.assertEqual(result['sha256'],hashlib.sha256(body).hexdigest());self.assertTrue(result['image'].startswith('http://127.0.0.1:'))
  self.assertTrue(__import__('programme_image69').eligible(result,event),'recovered bytes must reach actual display admission')
  with mock.patch('programme_transport77.verified',side_effect=AssertionError('cold NAS recovery must not query provider/TMDB again')):
   recovered=__import__('programme_urls55').resolve(dict(event,placeholder=''),allow_lookup=True,url_mode69=True);self.assertTrue(__import__('programme_image69').eligible(recovered,event))
  self.assertIsNone(self.module.recover_programme(dict(event,sid='2')))
  self.options['programme_tmdb_optout77']=True;self.assertIsNone(self.module.recover_programme(event))
  self.assertFalse((self.folder/'programme_images46').exists())
 def test_cancel_preserves_unpublished_source_and_no_implicit_activation(self):
  before=self.config.read()
  with self.assertRaises(OSError):self.module.store('logo','a'*64,png((200,100)),{})
  self.assertEqual(self.config.read(),before)
  self.activate(True)
  with self.assertRaises(InterruptedError):self.module.store('logo','a'*64,png((200,100)),{},cancel=lambda:True)
  self.assertFalse(self.module.records('logo'))
 def test_existing_internal_posters_copy_verify_render_gate_resume_and_return_preserve_originals(self):
  poster=__import__('poster_store89');poster.store(self.portal,'vod',self.row,'poster',self.row['cover'],png((300,450)))
  original=poster.read(self.portal,'vod',[self.row])['1']['poster'];before=Path(original).read_bytes()
  target='smb://fixture.invalid/share';patch=mock.patch.dict(sys.modules,{'xbmcvfs':self.vfs});patch.start();self.addCleanup(patch.stop)
  migration=__import__('artwork_migration');migration.begin(target);migration.copy(cancel=lambda:True);self.assertEqual(self.config.read()['mode'],'internal')
  migration.copy();self.assertTrue(migration.verify())
  with self.assertRaises(OSError):migration.activate()
  migration.approve_render(True);self.assertTrue(migration.activate())
  uri=poster.read(self.portal,'vod',[self.row])['1']['poster'];self.assertTrue(uri.startswith('smb://'));self.assertEqual(self.vfs.path(uri).read_bytes(),before);self.assertEqual(Path(original).read_bytes(),before)
  migration.begin('INTERNAL');migration.copy();self.assertTrue(migration.verify());migration.approve_render(True);self.assertTrue(migration.activate())
  restored=poster.read(self.portal,'vod',[self.row])['1']['poster'];self.assertEqual(Path(restored).read_bytes(),before);self.assertTrue(self.vfs.path(uri).is_file())
 def test_external_drive_change_cannot_flush_a_previous_profile_programme_queue(self):
  self.activate(True);self.options.update(programme_tmdb46=True,tmdb_research43=True)
  event=dict(pid='p',sid='1',canonical='xml',title='Monk',start=int(time.time())-60,stop=int(time.time())+1800)
  value=dict(source='tmdb_series',match='EXACT_UNIQUE_TV_TITLE66',role81='backdrop',source_url='https://image.tmdb.org/t/p/w1280/a.png')
  self.module.archive_programme(event,value,png((960,540)));self.assertTrue(self.module._pending)
  with mock.patch.object(self.module,'context',return_value=['other']),mock.patch.object(self.module,'store',side_effect=AssertionError('never write previous profile image')):self.module.drain()
 def test_metadata_reserve_and_external_quota_block_without_publishing_or_changing_selection(self):
  self.activate(True);before=self.config.read()
  with mock.patch('metadata_store89.check',side_effect=OSError('METADATA_SAFETY_FLOOR')):
   with self.assertRaises(OSError):__import__('logo_store89').persist(self.portal,self.row,png((200,100)))
  self.assertFalse(self.module.records('logo'));self.assertEqual(self.config.read(),before)
  storage=self.module.backend('logo')
  with mock.patch.object(storage,'enumerate_for_migration',return_value=iter([dict(ident='b'*64,bytes=17*1024**2)])),mock.patch.object(self.module,'backend',return_value=storage):
   with self.assertRaisesRegex(OSError,'QUOTA'):__import__('logo_store89').persist(self.portal,self.row,png((200,100)))
  self.assertFalse(self.module.records('logo'));self.assertEqual(self.config.read(),before)
 def test_cold_local_receipts_reuse_exact_external_references_without_provider_http(self):
  import importlib
  self.activate(True);logo,_=__import__('logo_store89').persist(self.portal,self.row,png((200,100)))
  __import__('poster_store89').store(self.portal,'vod',self.row,'poster',self.row['cover'],png((300,450)))
  expected=__import__('poster_store89').read(self.portal,'vod',[self.row]);importlib.reload(self.module)
  with mock.patch('station_logos88.fetch',side_effect=AssertionError('no repeated provider HTTP')):
   self.assertEqual(__import__('logo_manifest86').read(self.portal,[self.row],with_fallback=False)['1'],logo);self.assertEqual(__import__('poster_store89').read(self.portal,'vod',[self.row]),expected)
 def test_worker_detects_corrupt_smb_bytes_and_never_publishes_false_verified_reference(self):
  self.activate(True);uri,_=__import__('logo_store89').persist(self.portal,self.row,png((200,100)));key=self.module.key(self.portal,'logo',self.row)
  self.vfs.path(uri).write_bytes(png((201,100)));self.module._checked.clear()
  self.assertFalse(self.module.confirm('logo',key,self.module.records('logo')[key]));self.assertFalse(self.module.references(self.portal,'logo',[self.row]))
  self.assertTrue(self.vfs.path(uri).exists(),'no unrequested deletion of a collision')
 def test_unfinished_nas_part_is_accounted_and_never_silently_deleted(self):
  self.activate(True);storage=self.module.backend('logo');partial=self.vfs.path(storage.root+'/owned.img.part.test89');partial.write_bytes(b'partial')
  with self.assertRaisesRegex(OSError,'INCOMPLETE'):__import__('logo_store89').persist(self.portal,self.row,png((200,100)))
  self.assertEqual(partial.read_bytes(),b'partial');self.assertFalse(self.module.records('logo'))
 def test_old_separate_programme_volume_is_not_silently_rebound_by_generic_target_activation(self):
  self.activate();config=self.config.read();config.update(programme_target87=str(self.root),programme_volume87=dict(volume='old',mount_key='old'));self.config._write(config)
  patch=mock.patch.dict(sys.modules,{'xbmcvfs':self.vfs});patch.start();self.addCleanup(patch.stop)
  migration=__import__('artwork_migration')
  with mock.patch('android_artwork87.check_active'):
   migration.begin('smb://fixture.invalid/other');migration.copy();self.assertTrue(migration.verify());migration.approve_render(True)
   with self.assertRaisesRegex(OSError,'LEGACY_PROGRAMME_MIGRATION_REQUIRED'):migration.activate()
  self.assertEqual(self.config.read(),config)
 def test_smb_logo_reaches_exact_account_hero_fallback_and_external_status_without_gui_network(self):
  self.activate(True);uri,_=__import__('logo_store89').persist(self.portal,self.row,png((200,100)))
  with mock.patch.object(self.vfs,'File',side_effect=AssertionError('no GUI NAS IO')):
   value=__import__('live_rail86').values(self.portal,[self.row])[0];props=value['props'];self.assertEqual(__import__('station_logos88').reference(props),uri)
   __import__('live_text63')._hero(props);self.assertEqual(props['XCMate.HeroImage63'],uri)
   self.assertFalse(__import__('station_logos88').reference(dict(props,**{'XCMate.PortalId':'foreign'})))
  status=json.loads(self.properties['XCMate.Home86.Rail']);self.assertEqual(status['external'],1);self.assertEqual(status['local'],0)
 def test_verified_smb_covers_count_as_available_without_claiming_local_files_or_pixels(self):
  self.activate(True);__import__('poster_store89').store(self.portal,'vod',self.row,'poster',self.row['cover'],png((300,450)))
  refs=__import__('poster_store89').read(self.portal,'vod',[self.row]);count=self.module.ready_count(self.portal,'vod',[self.row],refs);self.assertEqual(count,1)
  status=__import__('home_loading85').update(self.portal,'vod',[self.row],'READY',images=count);self.assertEqual(status['state'],'READY')
  self.assertEqual(self.module.ready_count(self.portal,'vod',[self.row],{'1':dict(poster='smb://foreign.invalid/share/other.png')}),0)
 def test_programme_archive_retries_are_bounded_and_resume_existing_bytes_after_network_return(self):
  self.activate(True);self.options.update(programme_tmdb46=True,tmdb_research43=True)
  event=dict(pid='p',sid='1',canonical='xml',title='Monk',start=int(time.time())-60,stop=int(time.time())+1800)
  value=dict(source='tmdb_series',match='EXACT_UNIQUE_TV_TITLE66',role81='backdrop',source_url='https://image.tmdb.org/t/p/w1280/a.png')
  self.module.archive_programme(event,value,png((960,540)));self.vfs.online=False
  with mock.patch('time.monotonic',return_value=1000):self.module.drain()
  self.assertEqual(len(self.module._pending),1)
  with mock.patch('time.monotonic',return_value=1001),mock.patch.object(self.module,'store',side_effect=AssertionError('respect backoff')):self.module.drain()
  self.vfs.online=True
  with mock.patch('time.monotonic',return_value=1031):self.module.drain()
  self.assertFalse(self.module._pending);self.assertTrue(self.module.records('programme'))
  # A separate real event exhausts at most three attempts, never a retry loop.
  self.module.archive_programme(dict(event,sid='2'),value,png((960,540)))
  with mock.patch.object(self.module,'store',side_effect=OSError('offline')) as write:
   for moment in (2000,2031,2092,2300):
    with mock.patch('time.monotonic',return_value=moment):self.module.drain()
   self.assertEqual(write.call_count,3);self.assertFalse(self.module._pending)

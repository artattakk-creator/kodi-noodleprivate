"""Real files, explicit synthetic separate-volume receipts, no Android claims."""
import hashlib,importlib,io,json,os,unittest
from unittest import mock
from PIL import Image
from xcmate027_fixture import Fixture

class Storage87(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.s=importlib.import_module('android_artwork87');self.config=importlib.import_module('artwork_config');self.config.initialize();self.target=self.folder/'Movies';self.target.mkdir()
 def rows(self,free=2*1024**3,separate=True):
  def row(role,dev):return dict(path=str(self.target),role=role,device=dev,identity_verified=True,mount=dict(device='8:'+str(dev),fs='ext4',source='/dev/synthetic'+str(dev)),volume=str(dev),mount_key='8:'+str(dev),fs='ext4',total=8*1024**3,available=free,free=free,reserve=1024**3,separate_reserve=32*1024**2)
  return [row(kind,1) for kind in ('INTERNAL_MEDIA','INTERNAL_LOGOS','PROGRAMME_IMAGES')]+[row('TARGET',2 if separate else 1)]
 def test_actual_same_filesystem_reports_no_separate_writable_volume_without_writes(self):
  before={str(p):p.read_bytes() for p in self.folder.rglob('*') if p.is_file()}
  with self.assertRaisesRegex(OSError,'NO_SEPARATE_WRITABLE_VOLUME'):self.s.preflight(str(self.target))
  self.assertEqual(before,{str(p):p.read_bytes() for p in self.folder.rglob('*') if p.is_file()})
 def test_verified_target_keeps_one_gib_not_legacy_small_external_reserve(self):
  with mock.patch('android_storage83.inventory',return_value=self.rows(free=240*1024**2)):
   with self.assertRaisesRegex(OSError,'TARGET_RESERVE_BLOCKED'):self.s.preflight(str(self.target))
  with mock.patch('android_storage83.inventory',return_value=self.rows()):
   value=self.s.preflight(str(self.target));self.assertEqual(value['rows'][-1]['reserve'],1024**3)
 def test_explicit_probe_really_fsyncs_renames_and_reads_back_only_own_file(self):
  foreign=self.target/'keep.sqlite';foreign.write_bytes(b'foreign private database')
  with mock.patch('android_storage83.inventory',return_value=self.rows()):
   with self.assertRaisesRegex(OSError,'CONFIRMATION_REQUIRED'):self.s.probe(str(self.target),self.config.read()['profile'])
   result=self.s.probe(str(self.target),self.config.read()['profile'],confirmed=True)
  self.assertEqual(result['code'],'SEPARATE_POOL_VERIFIED');self.assertEqual(foreign.read_bytes(),b'foreign private database');self.assertFalse(list(self.target.rglob('.probe87-*')))
  receipt=json.loads(self.properties['XCMate.Storage87.LastProbe']);self.assertEqual(receipt['code'],'WRITE_FSYNC_RENAME_READBACK');self.assertNotIn(str(self.target),json.dumps(receipt))
 def test_permission_or_rename_failure_cannot_activate_target(self):
  real_replace=os.replace
  def fail_probe(src,dst):
   if '.probe87-' in str(src):raise PermissionError(13,'private path')
   return real_replace(src,dst)
  with mock.patch('android_storage83.inventory',return_value=self.rows()),mock.patch('os.replace',side_effect=fail_probe):
   with self.assertRaises(OSError):self.s.probe(str(self.target),self.config.read()['profile'],confirmed=True)
  self.assertNotEqual(self.config.read()['mode'],'external');self.assertFalse(list(self.target.rglob('.probe87-*')))
 def test_owned_programme_inventory_excludes_sqlite_metadata_and_foreign_images(self):
  module=__import__('programme_storage87');root=self.folder/'programme_images46';root.mkdir()
  good='blob46-'+'a'*64+'.png';(root/good).write_bytes(b'owned name only')
  for name in ('unrelated.png','guide_v1.sqlite','a.json','blob46-not-a-hash.png'):(root/name).write_bytes(b'keep')
  storage=module.ProgrammeStorage(str(root));self.assertEqual([v['ident'] for v in storage.enumerate_for_migration()],[good])
  with self.assertRaises(OSError):storage.resolve_target('../guide_v1.sqlite')
 def test_shared_migration_copies_programme_art_verifies_and_keeps_all_originals(self):
  # Pool identity is injected, while journal, copy, SHA, readback, render gate,
  # activation, resume and all protected originals use actual host files.
  migration=__import__('artwork_migration');module=__import__('programme_storage87')
  raw=io.BytesIO();Image.new('RGB',(96,64),(40,80,120)).save(raw,format='PNG');body=raw.getvalue();ident='blob46-'+hashlib.sha256(body).hexdigest()+'.png'
  source=self.folder/'programme_images46';source.mkdir();(source/ident).write_bytes(body);(source/'keep.sqlite').write_bytes(b'unchanged')
  proof=dict(target=str(self.target),volume='2',mount_key='8:2',code='SEPARATE_POOL_VERIFIED',rows=[])
  with mock.patch('android_artwork87.preflight',return_value=proof):
   migration.begin(str(self.target),shared=True,confirmed=True,strict87=True);migration.inventory();self.assertEqual(migration.status()['files'],1)
   migration.copy(cancel=lambda:True);self.assertNotEqual(self.config.read()['mode'],'external')
   migration.copy();self.assertTrue(migration.verify())
   with self.assertRaisesRegex(OSError,'RENDER_NOT_VERIFIED'):migration.activate()
   migration.approve_render(True);self.assertTrue(migration.activate())
   target=module.target(str(self.target),self.config.read()['profile']);self.assertEqual(target.read(ident,100000),body)
   self.assertEqual(self.s.programme_root(),target.root)
   self.assertEqual((source/ident).read_bytes(),body);self.assertEqual((source/'keep.sqlite').read_bytes(),b'unchanged')
   with self.assertRaisesRegex(OSError,'CLEANUP_NOT_AUTHORIZED'):migration.remove_originals(migration.status()['transfer'])
 def test_public_diagnostics_have_mount_budget_and_no_private_paths(self):
  result=self.s.public_status();self.assertIn('active_mount',result);self.assertGreaterEqual(result['reserve'],1024**3);self.assertNotIn(str(self.folder),json.dumps(result))
 def test_active_migration_target_replaced_or_gone_is_blocked_before_new_directory_write(self):
  config=self.config.read();config.update(mode='external',archive_mode='external',target=str(self.target),programme_target87=str(self.target),programme_volume87=dict(volume='different',mount_key='different'))
  self.config._write(config);before=set(self.target.rglob('*'))
  with self.assertRaisesRegex(OSError,'TARGET_VOLUME_UNVERIFIED'):__import__('programme_art46').space(1024)
  self.assertEqual(set(self.target.rglob('*')),before)
 def test_migrated_logo_manifest_points_to_verified_new_bytes_after_cold_reload(self):
  migration=__import__('artwork_migration');manifest=__import__('logo_manifest86');backend=__import__('artwork_backend').active_backend('logos')
  raw=io.BytesIO();Image.new('RGB',(120,60),(30,90,160)).save(raw,format='PNG');body=raw.getvalue();digest=hashlib.sha256(body).hexdigest();backend.write_verified(digest,body,lambda value:True)
  row=dict(sid='1',stream_icon='https://example.org/logo.png');stat=os.stat(backend.resolve_target(digest));record=dict(context=manifest.context(self.portal),sha256=digest,stamp=[stat.st_mtime_ns,stat.st_size],width=120,height=60)
  with open(os.path.join(backend.root,'manifest86.json'),'w') as stream:json.dump(dict(format=1,records={manifest.key(self.portal,row):record}),stream)
  proof=dict(target=str(self.target),volume='2',mount_key='8:2',code='SEPARATE_POOL_VERIFIED',rows=[])
  with mock.patch('android_artwork87.preflight',return_value=proof):
   migration.begin(str(self.target),shared=True,confirmed=True,strict87=True);migration.copy();migration.verify();migration.approve_render(True);migration.activate()
  loaded=manifest.read(self.portal,[row]);self.assertTrue(loaded['1'].startswith(str(self.target)));self.assertEqual(__import__('pathlib').Path(loaded['1']).read_bytes(),body)
  self.assertEqual(backend.read(digest,100000),body)

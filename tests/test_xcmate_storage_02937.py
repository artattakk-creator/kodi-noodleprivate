"""Real files/SQLite and a Kodi-VFS model. Android/real SMB remains NOT_TESTED."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest import mock
import test_xcmate_artwork_02920 as model
from artwork37_vfs_fixture import VFS


class Storage37(unittest.TestCase):
    def setUp(self):
        self.m=model.Artwork20Tests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.config=importlib.import_module('artwork_config');self.config.initialize()
        self.migration=importlib.import_module('artwork_migration');self.vfsmod=importlib.import_module('artwork_vfs')
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.external=Path(temp.name)
        self.vfs=VFS(self.external);patch=mock.patch.dict(sys.modules,{'xbmcvfs':self.vfs});patch.start();self.addCleanup(patch.stop)
        self.profile=self.config.read()['profile']

    def seed(self,count=7):
        root=Path(self.m.art.folder());root.mkdir(exist_ok=True);keys=[]
        for i in range(count):
            ident=hashlib.sha256(str(i).encode()).hexdigest();(root/(ident+'.img')).write_bytes(self.m.png);keys.append(ident)
        logos=self.m.folder/'tv_logos';logos.mkdir(exist_ok=True)
        for i in range(2):(logos/(hashlib.sha256(('logo'+str(i)).encode()).hexdigest()+'.img')).write_bytes(self.m.png)
        return keys

    def transfer(self,target):
        self.migration.begin(target);self.migration.copy();self.assertTrue(self.migration.verify())
        self.migration.approve_render(True);self.assertTrue(self.migration.activate())

    def test_local_usb_copy_verify_activate_leaves_originals_and_keys_intact(self):
        keys=self.seed();before={p.name:p.read_bytes() for p in Path(self.m.art.folder()).glob('*.img')}
        self.transfer(str(self.external))
        self.assertEqual(self.config.read()['mode'],'external')
        for key in keys:
            target=self.vfsmod.backend_for(str(self.external),self.profile)
            self.assertEqual(target.read(key,100000),self.m.png)
        self.assertEqual(before,{p.name:p.read_bytes() for p in (self.m.folder/'media_art_v1').glob('*.img')})
        self.assertEqual(self.migration.status()['done'],9)

    def test_kodi_smb_vfs_unknown_capacity_and_persistent_display_uri(self):
        keys=self.seed(3);self.transfer('smb://fixture.invalid/share')
        target=self.vfsmod.backend_for('smb://fixture.invalid/share',self.profile)
        with mock.patch('shutil.disk_usage',side_effect=AssertionError('NAS capacity must not use internal mount')):
            self.assertEqual(target.free_or_unknown(),dict(free=None,total=None))
        self.assertEqual(target.read(keys[0],100000),self.m.png)
        self.assertTrue(target.make_display_uri(keys[0]).startswith('smb://fixture.invalid/share/XCMate/Artwork/media/'))
        self.assertTrue(self.vfs.calls)

    def test_short_vfs_copy_never_commits_and_originals_survive(self):
        keys=self.seed(1);self.migration.begin('smb://fixture.invalid/share');self.vfs.short_copy=True
        with self.assertRaises(self.vfsmod.StorageFailure):self.migration.copy()
        target=self.vfsmod.backend_for('smb://fixture.invalid/share',self.profile)
        self.assertFalse(target.exists(keys[0]));self.assertTrue((self.m.folder/'media_art_v1'/(keys[0]+'.img')).exists())
        self.assertEqual(self.config.read()['mode'],'internal')

    def test_pause_restart_resume_skips_verified_and_does_not_delete_source(self):
        keys=self.seed(12);self.migration.begin(str(self.external));checks=[]
        def progress(**value):
            if value.get('stage')=='COPYING':checks.append(value.get('done',0))
        # Cancel after the first committed batch, then reload the coordinator.
        self.migration.copy(lambda:bool(checks),progress)
        self.assertEqual(self.config.read()['mode'],'internal')
        importlib.reload(self.migration).copy()
        self.assertTrue(self.migration.verify());self.assertEqual(self.migration.status()['done'],14)
        self.assertTrue(all((self.m.folder/'media_art_v1'/(key+'.img')).exists() for key in keys))

    def test_activation_requires_full_verification_and_explicit_render_confirmation(self):
        self.seed(2);self.migration.begin(str(self.external))
        with self.assertRaises(self.vfsmod.StorageFailure):self.migration.activate()
        self.migration.copy();self.migration.verify()
        with self.assertRaisesRegex(self.vfsmod.StorageFailure,'RENDER_NOT_VERIFIED'):self.migration.activate()
        self.assertEqual(self.config.read()['mode'],'internal')

    def test_offline_external_preserves_choice_all_ready_rows_and_stops_downloads(self):
        self.m.art.fetch('https://image.invalid/ready37');self.transfer('smb://fixture.invalid/share')
        db=self.m.store.connect();before=[tuple(r) for r in db.execute('SELECT * FROM jobs')];db.close()
        calls=self.m.http.call_count;self.vfs.online=False
        self.assertFalse(self.m.store.run_one())
        with self.assertRaises(self.vfsmod.StorageFailure):self.m.store.enqueue(['https://image.invalid/ready37'])
        db=self.m.store.connect();self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM jobs')],before);db.close()
        self.assertEqual(self.m.http.call_count,calls);self.assertEqual(self.config.read()['mode'],'external')

    def test_external_new_download_is_not_subject_to_internal_image_reserve(self):
        self.transfer('smb://fixture.invalid/share')
        from types import SimpleNamespace
        with mock.patch('shutil.disk_usage',return_value=SimpleNamespace(free=531*1048576,total=3847*1048576)):
            result=self.m.art.fetch('https://image.invalid/external37')
        self.assertTrue(result.startswith('smb://'));self.assertFalse((self.m.folder/'media_art_v1').exists())

    def test_collision_symlink_and_credential_targets_fail_closed(self):
        for uri in ('smb://user:SECRET@fixture.invalid/share','smb://fixture.invalid/share/../secret','smb://fixture.invalid/share/%2e%2e/secret'):
            with self.assertRaises(self.vfsmod.StorageFailure):self.migration.begin(uri)
        (self.external/'XCMate').symlink_to(self.m.folder,target_is_directory=True)
        with self.assertRaises(self.vfsmod.StorageFailure):self.migration.begin(str(self.external))
        self.assertFalse((self.m.folder/'Artwork').exists())

    def test_cleanup_is_separate_defaults_denied_and_never_touches_databases(self):
        keys=self.seed(3);self.transfer(str(self.external));state=self.migration.status()
        protected=self.m.folder/'library_v1.sqlite';before=protected.read_bytes()
        with self.assertRaises(self.vfsmod.StorageFailure):self.migration.remove_originals()
        self.assertTrue((self.m.folder/'media_art_v1'/(keys[0]+'.img')).exists())
        freed=self.migration.remove_originals(state['transfer']);self.assertEqual(freed,5*len(self.m.png))
        self.assertEqual(protected.read_bytes(),before)
        target=self.vfsmod.backend_for(str(self.external),self.profile)
        self.assertEqual(target.read(keys[0],100000),self.m.png)

    def test_target_corruption_blocks_cleanup_and_preserves_originals(self):
        keys=self.seed(1);self.transfer(str(self.external));state=self.migration.status()
        target=self.vfsmod.backend_for(str(self.external),self.profile);Path(target.resolve_target(keys[0])).write_bytes(b'corrupt')
        with self.assertRaises(self.vfsmod.StorageFailure):self.migration.remove_originals(state['transfer'])
        self.assertTrue((self.m.folder/'media_art_v1'/(keys[0]+'.img')).exists())

    def test_two_profiles_have_distinct_external_namespaces(self):
        first=self.vfsmod.backend_for('smb://fixture.invalid/share',self.profile).root
        second=self.vfsmod.backend_for('smb://fixture.invalid/share','b'*32).root
        self.assertNotEqual(first,second)

    def test_twenty_thousand_image_inventory_copy_sha_and_restart_verification(self):
        keys=self.seed(20000);self.migration.begin(str(self.external));self.migration.copy()
        self.assertEqual(self.migration.status()['done'],20002)
        self.assertTrue(importlib.reload(self.migration).verify())
        self.assertEqual(self.config.read()['mode'],'internal')
        self.assertEqual(len(list((self.m.folder/'media_art_v1').glob('*.img'))),20000)
        target=self.vfsmod.backend_for(str(self.external),self.profile)
        self.assertEqual(hashlib.sha256(target.read(keys[-1],100000)).hexdigest(),hashlib.sha256(self.m.png).hexdigest())

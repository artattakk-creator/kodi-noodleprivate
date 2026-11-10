"""Real files/journal + fault injection; no Android capacity/SAF claim."""
import errno
import hashlib
import importlib
import json
import os
from pathlib import Path
import sqlite3
import time
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture
import test_xcmate_storage_02937 as old


class SharedStorage83(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.s=importlib.reload(importlib.import_module('android_storage83'))
        self.config=importlib.import_module('artwork_config');self.config.initialize()
        self.target=self.folder/'Movies';self.target.mkdir()
        self.fail=importlib.import_module('artwork_vfs').StorageFailure

    def row(self,device=1,fs='ext4',mount_device='8:1',free=2*1024**3,total=8*1024**3,role='TARGET'):
        return dict(path=str(self.target),role=role,device=device,identity_verified=True,mount=dict(device=mount_device,fs=fs,source='/dev/mock'+mount_device),volume=str(device),mount_key=mount_device,fs=fs,total=total,available=free,free=free,reserve=1024**3,separate_reserve=64*1024**2)

    def observed(self,source=None,target=None):
        source=source or self.row(role='INTERNAL_MEDIA')
        return [dict(source,role=role) for role in ('INTERNAL_MEDIA','INTERNAL_LOGOS','PROGRAMME_IMAGES')]+[target or self.row(device=2,mount_device='8:2')]

    def test_actual_host_same_pool_different_folders_no_write_or_claimed_gain(self):
        before=set(self.folder.rglob('*'))
        with self.assertRaisesRegex(self.fail,'TARGET_SAME_CAPACITY_POOL'):
            self.s.preflight(str(self.target))
        self.assertEqual(before,set(self.folder.rglob('*')))

    def test_same_device_different_quota_or_total_remains_same_pool(self):
        self.assertEqual(self.s.relation(self.row(),self.row(total=224*1024**3)), 'TARGET_SAME_CAPACITY_POOL')

    def test_bind_alias_same_backing_major_minor_despite_different_stat_devices(self):
        self.assertEqual(self.s.relation(self.row(),self.row(device=2)), 'TARGET_SAME_CAPACITY_POOL')

    def test_fuse_unknown_and_equal_capacity_is_not_proof_of_separation(self):
        for total in (8*1024**3,224*1024**3):
            self.assertEqual(self.s.relation(self.row(fs='fuse'),self.row(device=2,fs='fuse',mount_device='0:8',total=total)), 'TARGET_VOLUME_UNVERIFIED')

    def test_separate_block_filesystems_can_be_verified(self):
        with mock.patch.object(self.s,'inventory',return_value=self.observed()):
            result=self.s.preflight(str(self.target))
        self.assertEqual(result['code'],'SEPARATE_POOL_VERIFIED')

    def test_unverified_mount_namespace_never_proves_separation(self):
        target=self.row(device=2,mount_device='8:2');target['identity_verified']=False
        self.assertEqual(self.s.relation(self.row(),target),'TARGET_VOLUME_UNVERIFIED')

    def test_reserve_cannot_be_disabled_by_target_selection(self):
        rows=self.observed(target=self.row(device=2,mount_device='8:2',free=1024))
        with mock.patch.object(self.s,'inventory',return_value=rows),self.assertRaisesRegex(self.fail,'TARGET_RESERVE_BLOCKED'):
            self.s.preflight(str(self.target))

    def test_unmeasurable_source_blocks_instead_of_inventing_other_pool(self):
        rows=self.observed();rows[0]={'role':'INTERNAL_MEDIA','error':'TARGET_VOLUME_UNVERIFIED'}
        with mock.patch.object(self.s,'inventory',return_value=rows),self.assertRaisesRegex(self.fail,'TARGET_VOLUME_UNVERIFIED'):
            self.s.preflight(str(self.target))

    def test_statvfs_available_and_free_recorded_separately_and_redacted(self):
        actual=os.statvfs(self.target)
        vfs=types.SimpleNamespace(f_frsize=4096,f_bsize=4096,f_blocks=100000,f_bavail=1000,f_bfree=2000)
        with mock.patch('os.statvfs',return_value=vfs):row=self.s.measure(str(self.target),'TARGET',require=True)
        self.assertEqual((row['available'],row['free']),(4096000,8192000))
        self.assertNotIn(str(self.folder),json.dumps(self.s.public([row])))
        self.assertNotIn('source',json.dumps(self.s.public([row])))

    def test_invalid_capacity_and_disappearing_volume_fail_closed(self):
        vfs=types.SimpleNamespace(f_frsize=4096,f_bsize=4096,f_blocks=1,f_bavail=2,f_bfree=3)
        with mock.patch('os.statvfs',return_value=vfs),self.assertRaisesRegex(self.fail,'TARGET_VOLUME_UNVERIFIED'):
            self.s.measure(str(self.target),'TARGET',require=True)
        with self.assertRaisesRegex(self.fail,'TARGET_OFFLINE'):
            self.s.measure(str(self.target/'absent'),'TARGET',require=True)

    def test_api34_eacces_does_not_claim_a_saf_grant(self):
        with mock.patch.object(self.s,'android',return_value=True),mock.patch('os.scandir',side_effect=PermissionError(errno.EACCES,'secret path')):
            with self.assertRaisesRegex(self.fail,'TARGET_SAF_REQUIRED'):self.s.measure(str(self.target),'TARGET',require=True)
        self.assertEqual(self.s.failure(OSError(errno.EROFS,'private')), 'TARGET_NOT_WRITABLE')

    def test_listing_failure_and_root_storage_failure_are_distinct(self):
        real=os.scandir
        def scan(path):
            if str(path)=='/storage':raise PermissionError(errno.EACCES,'hidden root')
            return real(path)
        with mock.patch('os.scandir',side_effect=scan):
            self.assertEqual(self.s.measure(str(self.target),'TARGET',require=True)['path'],str(self.target))
        with mock.patch.object(self.s,'android',return_value=False):
            self.assertEqual(self.s.failure(PermissionError(errno.EACCES,'hidden'),listing=True),'TARGET_NOT_BROWSABLE')

    def test_symlink_and_encoded_traversal_refused_without_writes(self):
        link=self.folder/'alias';link.symlink_to(self.target,target_is_directory=True)
        for path in (str(link),str(self.target/'..'/'other'),str(self.target)+'/%2e%2e/private'):
            with self.assertRaises(self.fail):self.s.measure(path,'TARGET',require=True)
        self.assertEqual(list(self.target.iterdir()),[])

    def test_filesystem_root_never_silently_becomes_working_directory(self):
        self.assertEqual(importlib.import_module('artwork_vfs').target_root('/'),'/')
        self.assertEqual(self.s.local_path('/'),'/')

    def test_namespace_replaced_by_symlink_cannot_redirect_resumed_writes(self):
        vfs=importlib.import_module('artwork_vfs')
        storage=vfs.prepare_target(str(self.target),self.config.read()['profile'])
        other=self.folder/'foreign';other.mkdir();keep=other/'keep';keep.write_bytes(b'private')
        Path(storage.root).rmdir();Path(storage.root).symlink_to(other,target_is_directory=True)
        with self.assertRaisesRegex(self.fail,'TARGET_SYMLINK'):storage.write_verified('a'*64,b'not image',lambda data:True)
        self.assertEqual(list(other.iterdir()),[keep]);self.assertEqual(keep.read_bytes(),b'private')

    def test_discovery_lists_only_existing_reachable_canonical_roots(self):
        with mock.patch.dict(os.environ,{'EXTERNAL_STORAGE':str(self.target)}),mock.patch('storage_sources.kodi_sources',return_value=[]):
            rows=self.s.candidates()
        self.assertIn(str(self.target),[r['path'] for r in rows])
        self.assertNotIn('/storage',[r['path'] for r in rows])
        self.assertTrue(all(Path(r['path']).is_dir() for r in rows))

    def test_probe_requires_explicit_consent_before_any_write(self):
        with mock.patch('tempfile.mkstemp',side_effect=AssertionError('unapproved write')):
            with self.assertRaisesRegex(self.fail,'TARGET_PROBE_CONFIRMATION_REQUIRED'):
                self.s.probe(str(self.target),self.config.read()['profile'])
        self.assertEqual(list(self.target.iterdir()),[])

    def test_confirmed_four_kib_probe_hash_readback_and_only_own_file_cleanup(self):
        keep=self.target/'keep.bin';keep.write_bytes(b'foreign')
        receipt=dict(target=str(self.target),volume='a',mount_key='b',rows=[])
        with mock.patch.object(self.s,'preflight',return_value=receipt):
            self.assertEqual(self.s.probe(str(self.target),self.config.read()['profile'],confirmed=True),receipt)
        self.assertEqual(keep.read_bytes(),b'foreign')
        self.assertEqual(list(self.target.rglob('.probe83-*')),[])
        self.assertFalse(list(self.target.rglob('*.img')))

    def test_probe_denied_write_and_readonly_preserve_originals(self):
        receipt=dict(target=str(self.target),volume='a',mount_key='b',rows=[])
        for number,code in ((errno.EACCES,'TARGET_SAF_REQUIRED'),(errno.EROFS,'TARGET_NOT_WRITABLE'),(errno.ENOSPC,'TARGET_RESERVE_BLOCKED')):
            with mock.patch.object(self.s,'preflight',return_value=receipt),mock.patch.object(self.s,'android',return_value=True),mock.patch('artwork_vfs.prepare_target',side_effect=OSError(number,'private')):
                with self.assertRaisesRegex(self.fail,code):self.s.probe(str(self.target),self.config.read()['profile'],confirmed=True)
        self.assertEqual(list(self.target.iterdir()),[])

    def test_probe_mount_change_blocks_target_activation(self):
        before=dict(target=str(self.target),volume='a',mount_key='b',rows=[])
        with mock.patch.object(self.s,'preflight',side_effect=[before,dict(before,volume='changed')]):
            with self.assertRaisesRegex(self.fail,'TARGET_VOLUME_UNVERIFIED'):
                self.s.probe(str(self.target),self.config.read()['profile'],confirmed=True)
        self.assertNotEqual(self.config.read()['mode'],'external')

    def test_foreign_profile_namespace_never_adopted(self):
        storage=importlib.import_module('artwork_vfs').backend_for(str(self.target),self.config.read()['profile'])
        Path(storage.root).mkdir(parents=True);keep=Path(storage.root)/'private';keep.write_bytes(b'untouched')
        with self.assertRaisesRegex(self.fail,'TARGET_COLLISION'):
            importlib.import_module('artwork_vfs').prepare_target(str(self.target),self.config.read()['profile'])
        self.assertFalse(Path(storage.owner_marker).exists());self.assertEqual(keep.read_bytes(),b'untouched')

    def test_picker_uses_real_folder_type_three_and_never_storage_root(self):
        ui=importlib.import_module('artwork_ui');dialog=mock.Mock();dialog.browseSingle.return_value=str(self.target)
        with mock.patch('xbmcgui.Dialog',return_value=dialog),mock.patch.object(ui,'job',side_effect=lambda f:f(lambda:False,lambda **kw:None)),mock.patch.object(self.s,'candidates',return_value=[dict(path=str(self.target),label='Movies')]),mock.patch('menu_icons45.select',return_value=0):
            self.assertEqual(ui._pick_android(),str(self.target))
        self.assertEqual(dialog.browseSingle.call_args.args[0],3)
        self.assertEqual(dialog.browseSingle.call_args.kwargs['defaultt'],str(self.target))

    def test_no_saf_bridge_is_an_actionable_error_and_does_not_change_settings(self):
        ui=importlib.import_module('artwork_ui');before=self.config.read()
        with mock.patch.object(ui,'job',return_value=[]),self.assertRaisesRegex(self.fail,'TARGET_SAF_REQUIRED'):ui._pick_android()
        self.assertEqual(self.config.read(),before)

    def test_picker_job_cancel_is_not_misreported_as_missing_android_permission(self):
        ui=importlib.import_module('artwork_ui');dialog=mock.Mock();dialog.browseSingle.return_value=str(self.target)
        for sequence in ([None],[[dict(path=str(self.target),label='Movies')],None]):
            with mock.patch('xbmcgui.Dialog',return_value=dialog),mock.patch.object(ui,'job',side_effect=sequence),mock.patch('menu_icons45.select',return_value=0):
                self.assertIsNone(ui._pick_android())

    def test_cancel_probe_confirmation_does_not_prepare_or_start_journal(self):
        ui=importlib.import_module('artwork_ui');dialog=mock.Mock();dialog.yesno.return_value=False
        with mock.patch('xbmcgui.Dialog',return_value=dialog),mock.patch.object(ui,'job',side_effect=lambda f:f(lambda:False,lambda **kw:None)),mock.patch('android_artwork87.preflight',return_value={'rows':[]}),mock.patch('artwork_migration.begin') as begin:
            ui._prepare(str(self.target),shared=True)
        begin.assert_not_called();self.assertFalse((self.folder/'artwork_transfer_v1.sqlite').exists())

    def test_localized_error_does_not_publish_private_exception_or_path(self):
        errors=importlib.import_module('artwork_errors83');dialog=mock.Mock()
        error=self.fail('TARGET_SAME_CAPACITY_POOL');error.private='SECRET_TOKEN'
        errors.show(error,dialog,16)
        text=str(dialog.mock_calls)
        self.assertIn('TARGET_SAME_CAPACITY_POOL',text);self.assertNotIn('SECRET_TOKEN',text)
        self.assertNotIn(str(self.target),text)


class Migration83(unittest.TestCase):
    def setUp(self):
        self.fixture=old.Storage37(methodName='runTest');self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.m=self.fixture.migration;self.s=importlib.import_module('android_storage83')
        self.target=str(self.fixture.external);self.fail=self.fixture.vfsmod.StorageFailure
        self.receipt=dict(target=self.target,volume='verified-host-injection',mount_key='fixture',rows=[],code='SEPARATE_POOL_VERIFIED')

    def test_shared_migration_copy_sha_render_activation_restart_originals_preserved(self):
        keys=self.fixture.seed(6);config=dict(self.fixture.config.read())
        protected=self.fixture.m.folder/'preserved-private-settings';protected.write_bytes(b'provider token EPG widgets')
        with mock.patch.object(self.s,'preflight',return_value=self.receipt):
            self.m.begin(self.target,shared=True,confirmed=True);self.m.copy();self.assertTrue(self.m.verify())
            with self.assertRaisesRegex(self.fail,'RENDER_NOT_VERIFIED'):self.m.activate()
            self.m.approve_render(True);self.assertTrue(self.m.activate());self.assertTrue(importlib.reload(self.m).verify())
        self.assertEqual(protected.read_bytes(),b'provider token EPG widgets')
        self.assertTrue(all((self.fixture.m.folder/'media_art_v1'/(key+'.img')).exists() for key in keys))
        self.assertNotIn('shared_storage83',self.fixture.config.read())
        self.assertEqual(self.fixture.config.read()['profile'],config['profile'])

    def test_shared_begin_without_consent_or_same_pool_is_read_only(self):
        before=set(self.fixture.m.folder.rglob('*'))
        with self.assertRaisesRegex(self.fail,'TARGET_PROBE_CONFIRMATION_REQUIRED'):self.m.begin(self.target,shared=True)
        with self.assertRaisesRegex(self.fail,'TARGET_SAME_CAPACITY_POOL'):self.m.begin(self.target,shared=True,confirmed=True)
        self.assertEqual(before,set(self.fixture.m.folder.rglob('*')));self.assertEqual(list(Path(self.target).iterdir()),[])

    def test_cancel_reload_resume_and_readback(self):
        self.fixture.seed(21)
        with mock.patch.object(self.s,'preflight',return_value=self.receipt):
            self.m.begin(self.target,shared=True,confirmed=True)
            self.m.copy(cancel=lambda:True);self.assertEqual(self.m.status()['stage'],'PAUSED')
            importlib.reload(self.m).copy();self.assertTrue(self.m.verify())
        self.assertEqual(self.m.status()['done'],23)

    def test_rejected_new_render_revokes_earlier_confirmation(self):
        self.fixture.seed(1)
        self.m.begin(self.target);self.m.copy();self.m.verify();self.m.approve_render(True)
        self.m.approve_render(False)
        self.assertFalse(self.m.status()['rendered'])
        with self.assertRaisesRegex(self.fail,'RENDER_NOT_VERIFIED'):self.m.activate()
        self.assertEqual(self.fixture.config.read()['mode'],'internal')

    def test_changed_mount_after_copy_refuses_activation_without_deleting_source(self):
        self.fixture.seed(1)
        with mock.patch.object(self.s,'preflight',return_value=self.receipt):
            self.m.begin(self.target,shared=True,confirmed=True);self.m.copy();self.m.verify();self.m.approve_render(True)
        with mock.patch.object(self.s,'preflight',return_value=dict(self.receipt,volume='other')):
            with self.assertRaisesRegex(self.fail,'TARGET_VOLUME_UNVERIFIED'):self.m.activate()
        self.assertEqual(self.fixture.config.read()['mode'],'internal')

    def test_sha_corruption_keeps_target_inactive_and_originals_intact(self):
        keys=self.fixture.seed(1)
        with mock.patch.object(self.s,'preflight',return_value=self.receipt):
            self.m.begin(self.target,shared=True,confirmed=True);self.m.copy()
            destination=self.fixture.vfsmod.backend_for(self.target,self.fixture.profile)
            Path(destination.resolve_target(keys[0])).write_bytes(b'corrupt')
            with self.assertRaisesRegex(self.fail,'IMAGE_VERIFY_FAILED'):self.m.verify()
        self.assertEqual(self.fixture.config.read()['mode'],'internal')
        self.assertEqual((self.fixture.m.folder/'media_art_v1'/(keys[0]+'.img')).read_bytes(),self.fixture.m.png)

    def test_offline_copy_pauses_journal_and_resumes_same_transfer(self):
        self.fixture.seed(2)
        with mock.patch.object(self.s,'preflight',return_value=self.receipt):
            self.m.begin(self.target,shared=True,confirmed=True);ident=self.m.status()['transfer']
            with mock.patch.object(self.fixture.vfsmod.ExternalLocalStorage,'write_verified',side_effect=OSError(errno.ENODEV,'private mount')):
                with self.assertRaises(OSError):self.m.copy()
            self.assertEqual(self.m.status()['stage'],'PAUSED');self.assertEqual(self.m.status()['transfer'],ident)
            self.m.copy();self.assertTrue(self.m.verify())

    def test_internal_journal_reserve_has_its_own_code(self):
        from import_budget import ReserveBlocked
        with mock.patch('import_budget.check_space',side_effect=ReserveBlocked(1,32*1024**2,65536)):
            with self.assertRaisesRegex(self.fail,'ARTWORK_JOURNAL_RESERVE_BLOCKED'):self.m._db()

    def test_journal_busy_is_bounded_specific_and_can_resume(self):
        self.fixture.seed(2);self.m.begin(self.target)
        blocker=sqlite3.connect(self.m.path());blocker.execute('BEGIN EXCLUSIVE')
        start=time.monotonic()
        try:
            with self.assertRaisesRegex(self.fail,'ARTWORK_DB_BUSY'):self.m.copy()
        finally:blocker.rollback();blocker.close()
        self.assertLess(time.monotonic()-start,1)
        self.m.copy();self.assertTrue(self.m.verify());self.assertEqual(self.m.status()['done'],4)

    def test_existing_journal_read_open_has_no_create_or_schema_rebuild(self):
        self.m.begin(self.target);statements=[];connect=sqlite3.connect
        def traced(*args,**kwargs):
            db=connect(*args,**kwargs);db.set_trace_callback(statements.append);return db
        with mock.patch.object(self.m.sqlite3,'connect',side_effect=traced):
            db=self.m._db()
            try:self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            finally:db.close()
        self.assertFalse(any('CREATE ' in sql.upper() or 'ALTER ' in sql.upper() for sql in statements))

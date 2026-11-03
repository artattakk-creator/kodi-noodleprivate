"""Issue #352: real data writers, native owner, cold readback and failure cases."""
import errno
import importlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading
import types
import unittest
from concurrent.futures import wait
from unittest import mock

import test_xcmate_setup_0294 as old
from xcmate027_fixture import ADDON,Control


class Setup71(unittest.TestCase):
    def setUp(self):
        self.m=old.StorageTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.d=self.m.draft;self.d.phased54=True
        self.ui=importlib.import_module('setup_window')
        self.resume=importlib.import_module('wizard_resume53')
        self.s=self.resume.Session();self.s.live=self.d;self.d.resume53=self.s
        self.storage=importlib.import_module('wizard_storage71')
        p=mock.patch.object(Control,'setPercent',lambda c,v:setattr(c,'percent',v),create=True)
        p.start();self.addCleanup(p.stop)

    def window(self):
        w=self.ui.SetupWindow('XCMateSetup.xml',str(ADDON),'Default','720p');w.configure(self.d)
        self.addCleanup(w._pool.shutdown,wait=True,cancel_futures=True);self.addCleanup(w.close)
        w.show();return w

    def finish(self,w):
        self.assertTrue(wait([w._future],timeout=5).done);w.pump()

    def test_auth_and_group_discovery_are_distinct_not_an_automatic_retry_loop(self):
        auth=mock.Mock(return_value=True);cats=mock.Mock(side_effect=self.d.adapter.categories)
        self.d.adapter.authenticate=auth;self.d.adapter.categories=cats
        w=self.window();w.onInit();w.onInit();self.finish(w);self.finish(w)
        self.assertEqual(w.stage,'groups');self.assertEqual(auth.call_count,1);self.assertEqual(cats.call_count,3)
        for _ in range(10):w.pump()
        self.assertEqual(cats.call_count,3)

    def test_failed_checkpoint_is_storage_not_network_and_can_retry_same_inputs(self):
        write=self.resume.write_file
        def fail(path,value):
            if path.endswith('categories53.json'):raise OSError(errno.ENOSPC,'SECRET private.invalid')
            return write(path,value)
        with mock.patch.object(self.resume,'write_file',side_effect=fail):
            w=self.window();self.finish(w);self.finish(w)
        self.assertEqual(w.stage,'failed');self.assertIn('XM-SETUP-CHECKPOINT',w.getControl(3).text)
        self.assertNotIn('XM-SETUP-NET',w.getControl(3).text);self.assertNotIn('SECRET',w.getControl(3).text)
        self.assertEqual(self.d.data['xc_pass'],'SECRET');self.assertEqual(self.d.selected['live'],{'live-1'})
        w.onClick(17);self.finish(w);self.finish(w);self.assertEqual(w.stage,'groups')

    def test_complete_owner_path_saves_real_groups_and_explicit_start_group(self):
        w=self.window();self.finish(w);self.finish(w)
        self.m.dialog.select.return_value=1
        w.onClick(21);self.assertEqual(self.d.data['start_group_id'],'live-1')
        w.onClick(17);self.finish(w);self.assertEqual(w.stage,'summary')
        w.onClick(17);self.finish(w)
        self.assertIsNotNone(w.result);self.assertEqual(w.result['start_group_id'],'live-1')
        self.assertTrue(self.d.verification['portal']);self.assertTrue(Path(self.d.backup71,'manifest.json').is_file())
        self.assertEqual(self.m.portals.get_by_id('p'),self.m.portal)

    def test_start_choice_cancel_keeps_previous_selection_and_focus(self):
        w=self.window();self.finish(w);self.finish(w)
        self.d.data['start_group_id']='live-1';self.m.dialog.select.return_value=-1
        w.onClick(21);self.assertEqual(self.d.data['start_group_id'],'live-1');self.assertEqual(w.getFocusId(),21)

    def test_start_group_outside_selection_cannot_be_published(self):
        self.d.scan();self.d.data['start_group_id']='foreign'
        with self.assertRaisesRegex(ValueError,'XM-SETUP-START'):self.d.save()
        self.assertIsNone(self.m.portals.get_by_id(self.d.pid))
        self.assertEqual(Path(self.m.portals._db_path()).read_bytes(),self.m.old)

    def test_start_group_survives_resume_and_real_fresh_process_readback(self):
        self.d.data['start_group_id']='live-1'
        self.assertTrue(self.s.checkpoint(self.d,'groups',categories=True))
        self.assertEqual(self.resume.Session.load().data['start_group_id'],'live-1')
        self.d.scan();self.d.save()
        script="""import json,sqlite3,sys
from pathlib import Path
folder=Path(sys.argv[1]);pid=sys.argv[2]
p=next(p for p in json.loads((folder/'portals.json').read_text()) if p['id']==pid)
g=json.loads((folder/'xtreammate_groups.json').read_text())['_v2'][pid]
assert p['start_group_id']=='live-1' and p['xc_pass']=='SECRET'
assert all(g[k]['enabled']==[k+'-1'] and not g[k]['auto_new'] for k in ('live','vod','series'))
print('COLD_READBACK_PASS')
"""
        result=subprocess.run([sys.executable,'-c',script,str(self.m.folder),self.d.pid],text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),'COLD_READBACK_PASS');self.assertEqual(result.stderr,'')

    def test_three_save_attempts_publish_only_once_and_never_duplicate(self):
        self.d.scan()
        for _ in range(3):self.assertEqual(self.d.save()['id'],self.d.pid)
        self.assertEqual(len(self.m.portals.load_all()),2)
        self.assertEqual(len(list(Path(self.m.folder,'setup_backup71').iterdir())),1)

    def test_group_commit_failure_preserves_previous_profiles_and_retry_works(self):
        self.d.scan();groups=importlib.import_module('group_selection');save=groups.save
        def fail(pid,categories,kind='live',**kw):
            if kind=='vod':raise OSError(errno.ENOSPC,'private SECRET')
            return save(pid,categories,kind,**kw)
        with mock.patch.object(groups,'save',side_effect=fail):
            with self.assertRaises(OSError):self.d.save()
        self.assertEqual(self.m.portals.load_all(),[self.m.portal])
        self.assertIsNone(groups.load(self.d.pid))
        self.assertFalse(self.d.saved)
        self.assertEqual(self.d.save()['id'],self.d.pid)

    def test_real_sqlite_writer_lock_never_reports_success_or_changes_old_portal(self):
        self.d.scan();db=self.m.index.connect(write=True)
        db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaises((sqlite3.Error,ValueError)):self.d.save()
        finally:db.rollback();db.close()
        self.assertFalse(self.d.saved);self.assertEqual(self.m.portals.load_all(),[self.m.portal])

    def test_backup_readback_has_exact_hashes_and_settings_remain_untouched(self):
        import hashlib
        settings=Path(self.m.folder,'settings.xml');settings.write_text('<settings>synthetic</settings>')
        self.d.scan();self.d.save();folder=Path(self.d.backup71)
        report=json.loads((folder/'manifest.json').read_text())
        for name,value in report['files'].items():
            if value['existed']:
                raw=(folder/name).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),value['sha256'])
                self.assertEqual(len(raw),value['bytes'])
        self.assertEqual((folder/'portals.json').read_bytes(),self.m.old)
        self.assertEqual(settings.read_text(),'<settings>synthetic</settings>')

    def test_backup_failure_prevents_configuration_publication(self):
        self.d.scan()
        with mock.patch('setup_commit71.tempfile.mkdtemp',side_effect=OSError(errno.EROFS,'synthetic')):
            with self.assertRaises(OSError):self.d.save()
        self.assertEqual(self.m.portals.load_all(),[self.m.portal]);self.assertFalse(self.d.saved)

    def test_verified_backup_can_be_restored_in_isolated_profile_without_touching_live_state(self):
        import hashlib,shutil
        self.d.scan();self.d.save()
        source=Path(self.d.backup71);manifest=json.loads((source/'manifest.json').read_text())
        target=self.m.folder/'restore-proof';target.mkdir()
        for name,record in manifest['files'].items():
            if not record['existed']:continue
            shutil.copyfile(source/name,target/name)
            self.assertEqual(hashlib.sha256((target/name).read_bytes()).hexdigest(),record['sha256'])
        self.assertEqual(json.loads((target/'portals.json').read_text()),[self.m.portal])
        self.assertEqual(len(self.m.portals.load_all()),2)

    def test_discovery_slot_is_nonreentrant_but_retry_after_release_succeeds(self):
        budget=importlib.import_module('wizard_deadline48')
        budget._slot.acquire()
        try:
            with self.assertRaises(OSError) as raised:self.d.discover()
            self.assertEqual(self.ui._failure_details(raised.exception)[0],'XM-SETUP-DISCOVERY-BUSY')
        finally:budget._slot.release()
        self.assertTrue(self.d.discover())

    def test_trace_is_correlated_and_contains_errno_without_private_exception_or_path(self):
        trace=importlib.import_module('setup_diagnostics71')
        with mock.patch('xbmc.log',create=True) as log,mock.patch('xbmc.LOGINFO',0,create=True):
            try:raise OSError(errno.EACCES,'SECRET https://private.invalid/user/password')
            except OSError as exc:trace.emit('FAILED','secret portal',error=exc)
        output=log.call_args.args[0]
        self.assertIn('errno=13',output);self.assertIn('stack=',output)
        for private in ('SECRET','private.invalid','secret portal',str(self.m.folder)):self.assertNotIn(private,output)

    def test_probe_removes_own_files_and_never_writes_database(self):
        trace=importlib.import_module('setup_diagnostics71')
        import xbmcvfs
        with mock.patch.object(xbmcvfs,'translatePath',return_value=str(self.m.folder)):
            report=trace.probe('synthetic')
        self.assertEqual(report['ADDON_DATA']['code'],'READY')
        self.assertGreater(report['ADDON_DATA']['available'],0)
        self.assertFalse(list(self.m.folder.glob('.xcmate-probe71-*')))

    def test_posix_privacy_failure_remains_fail_closed(self):
        folder=self.m.folder/'broad';folder.mkdir();folder.chmod(0o777)
        with mock.patch('os.chmod'),mock.patch.object(self.storage,'android_scoped',return_value=False):
            with self.assertRaises(self.storage.StorageError):self.storage.protect(str(folder),directory=True)

    def test_android_mode_compatibility_never_swallows_real_disk_full(self):
        path=self.m.folder/'owned-file';path.write_text('synthetic')
        with mock.patch.object(self.storage,'android_scoped',return_value=True),mock.patch('os.chmod',side_effect=OSError(errno.ENOSPC,'synthetic')):
            with self.assertRaises(OSError) as raised:self.storage.protect(str(path))
        self.assertEqual(raised.exception.errno,errno.ENOSPC)

    def android_profile(self):
        home=self.m.folder/'Android/data/org.xbmc.kodi/files/.kodi'
        profile=home/'userdata';root=profile/'addon_data/plugin.video.xtreammate';root.mkdir(parents=True)
        import xbmcvfs,utils
        mapping={'special://home/':str(home),'special://profile/':str(profile)}
        patches=[mock.patch('xbmc.getCondVisibility',return_value=True),
                 mock.patch.object(xbmcvfs,'translatePath',side_effect=lambda p:mapping.get(p,p)),
                 mock.patch.object(utils,'addon_data_dir',return_value=str(root))]
        for p in patches:p.start();self.addCleanup(p.stop)
        return root

    def test_owned_android_app_profile_supports_synthetic_modes_and_unsupported_chmod(self):
        root=self.android_profile();path=root/'wizard';path.mkdir();path.chmod(0o777)
        self.assertTrue(self.storage.android_scoped(str(path)))
        with mock.patch('os.chmod',side_effect=OSError(errno.EPERM,'synthetic')):
            self.assertEqual(self.storage.protect(str(path),directory=True),'ANDROID_APP_STORAGE')
            self.assertTrue(self.storage.readable(str(path)))

    def test_android_does_not_allow_other_shared_paths_or_symlinks(self):
        root=self.android_profile();outside=self.m.folder/'shared';outside.mkdir()
        self.assertFalse(self.storage.android_scoped(str(outside)))
        (root/'redirect').symlink_to(outside,target_is_directory=True)
        self.assertFalse(self.storage.android_scoped(str(root/'redirect/file')))
        with self.assertRaises(self.storage.StorageError):self.storage.protect(str(root/'redirect'),directory=True)

    def test_android_foreign_owner_is_not_accepted_as_app_private(self):
        root=self.android_profile();uid=os.getuid()
        with mock.patch('os.getuid',return_value=uid+1):
            self.assertFalse(self.storage.android_scoped(str(root)))

    def test_native_owner_can_complete_with_android_backend_when_chmod_is_unsupported(self):
        # Platform classification has independent positive/negative path tests.
        # This integration exercises the real checkpoint/writer/GUI with the
        # emulated-filesystem capability, not a fake checkpoint success.
        with mock.patch.object(self.storage,'android_scoped',return_value=True),\
             mock.patch('os.chmod',side_effect=OSError(errno.EPERM,'synthetic')) ,\
             mock.patch('os.fchmod',side_effect=OSError(errno.EPERM,'synthetic')):
            w=self.window();self.finish(w);self.finish(w)
            self.assertEqual(w.stage,'groups')
            w.onClick(17);self.finish(w);self.assertEqual(w.stage,'summary')
            w.onClick(17);self.finish(w);self.assertIsNotNone(w.result,w.getControl(3).text)
        self.assertEqual(self.m.portals.get_by_id(self.d.pid)['xc_pass'],'SECRET')
        self.assertEqual(importlib.import_module('group_selection').load(self.d.pid),{'live-1'})

    def test_checkpoint_backend_never_reintroduces_password_into_resume_json(self):
        self.android_profile()
        self.s.data=dict(self.d.data)
        self.assertTrue(self.s.persist())
        text=Path(self.resume.root(),'current.json').read_text()
        self.assertNotIn('SECRET',text);self.assertNotIn('xc_pass',text)

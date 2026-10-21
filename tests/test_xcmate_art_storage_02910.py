"""Real files/SQLite and bounded queue models; Android/USB permissions NOT_RUN."""
import errno
import hashlib
import importlib
import json
import os
from pathlib import Path
import struct
import sys
import threading
import time
import types
import unittest
from unittest import mock
import zlib
from xcmate027_fixture import Fixture,LIB


class ArtStorageTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('art_storage','art_store'):sys.modules.pop(name,None)
        self.storage=importlib.import_module('art_storage');self.store=importlib.import_module('art_store')
        self.art=importlib.reload(importlib.import_module('media_art'))
        patch=mock.patch.object(self.art,'ensure_worker');patch.start();self.addCleanup(patch.stop)
        self.http=sys.modules['utils'].http_get;self.http.side_effect=None
        def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        self.png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',100,150,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'abc'*100)*150))+chunk(b'IEND',b'')
        self.http.return_value=(self.png,{})
        self.url='https://image.invalid/private/TOKEN/one'
        self.destination=self.folder/'usb';self.destination.mkdir()

    def rows(self):
        db=self.store.connect()
        try:return [dict(r) for r in db.execute('SELECT * FROM jobs')]
        finally:db.close()

    def test_legacy_budget_and_explicit_profiles_above_4gib_no_silent_upgrade(self):
        self.assertEqual(self.store.budget(),512*1048576)
        self.options['media_art_budget_mb']=8192;self.assertEqual(self.store.budget(),8192*1048576)
        self.assertFalse((self.folder/'media_art_storage_v1.json').exists())
        self.storage.configure('large',reserve_mb=128);self.assertEqual(self.store.budget(),16384*1048576)
        self.storage.configure('expert',32768,reserve_mb=64);self.assertEqual(self.store.budget(),32768*1048576)
        self.assertEqual(importlib.reload(self.storage).policy()['budget_mb'],32768)
        before=(self.folder/'media_art_storage_v1.json').read_bytes()
        for value in (0,31,1048577):
            with self.assertRaises(ValueError):self.storage.configure('expert',value)
        self.assertEqual((self.folder/'media_art_storage_v1.json').read_bytes(),before)

    def test_auto_budget_tracks_free_bytes_and_keeps_selected_reserve(self):
        self.art.fetch(self.url);self.storage.configure('auto',reserve_mb=128)
        with mock.patch.object(self.storage.shutil,'disk_usage',return_value=types.SimpleNamespace(total=1000*1048576,free=512*1048576)):
            self.assertEqual(self.store.budget(),len(self.png)+384*1048576)
        with mock.patch.object(self.storage.shutil,'disk_usage',return_value=types.SimpleNamespace(total=1000*1048576,free=140*1048576)):
            self.assertEqual(self.store.budget(),len(self.png)+12*1048576)

    def test_usage_includes_orphan_files_and_updates_without_rescanning_per_picture(self):
        root=Path(self.art.folder());root.mkdir();(root/('0'*64+'.img')).write_bytes(b'orphan')
        self.assertEqual(self.store.used(),6)
        with mock.patch.object(self.storage.os,'scandir',wraps=os.scandir) as scan:
            self.art.fetch(self.url);self.art.fetch(self.url+'2')
            self.assertEqual(self.store.used(),6+2*len(self.png));scan.assert_not_called()
        self.storage.invalidate();self.assertEqual(self.store.used(),6+2*len(self.png))

    def test_quota_pause_is_persistent_does_not_consume_network_attempts_or_walk_17000_jobs(self):
        db=self.store.connect()
        with db:
            db.executemany("INSERT INTO jobs VALUES(?,?,'PENDING',20,0,0,0,0)",[(str(n),'https://image.invalid/'+str(n)) for n in range(17638)])
        db.close();stamp=time.time()
        with mock.patch.object(self.store,'budget',return_value=0):
            self.assertTrue(self.store.run_one(now=stamp))
            self.store=importlib.reload(self.store)
            for n in range(30):self.assertFalse(self.store.run_one(now=stamp+1))
        self.http.assert_not_called();rows=self.rows()
        self.assertEqual(sum(r['status']=='QUOTA_FULL' for r in rows),1)
        self.assertTrue(all(r['attempts']==0 for r in rows))
        self.storage.configure('large',reserve_mb=32)
        self.assertTrue(self.store.run_one(now=stamp+2));self.assertEqual(self.http.call_count,1)
        self.assertEqual(sum(r['status']=='READY' for r in self.rows()),1)

    def test_legacy_space_full_three_attempts_resumes_without_touching_ready(self):
        first=self.art.fetch(self.url);before=Path(first).read_bytes()
        db=self.store.connect()
        with db:db.execute("INSERT INTO jobs VALUES('old','https://image.invalid/old','SPACE_FULL',20,3,9999999999,0,0)")
        db.close();self.storage.configure('expert',8192,reserve_mb=32)
        self.assertTrue(self.store.run_one());self.assertEqual(Path(first).read_bytes(),before)
        self.assertEqual(self.http.call_count,2)

    def test_physical_low_and_write_enospc_are_distinct_from_quota(self):
        self.store.enqueue([self.url])
        with mock.patch.object(self.storage.shutil,'disk_usage',return_value=types.SimpleNamespace(total=1000,free=1)):
            self.assertTrue(self.store.run_one())
        self.assertEqual(self.rows()[0]['status'],'DISK_LOW');self.http.assert_not_called()
        self.store.resume_capacity()
        with mock.patch.object(self.art.os,'replace',side_effect=OSError(errno.ENOSPC,'PRIVATE')):self.store.run_one()
        self.assertEqual(self.rows()[0]['status'],'DISK_FULL');self.assertEqual(self.rows()[0]['attempts'],0)

    def test_permission_error_has_own_pause_and_no_private_exception_diagnostic(self):
        self.store.enqueue([self.url])
        with mock.patch.object(self.art.os,'replace',side_effect=PermissionError(errno.EACCES,'SECRET path')):self.store.run_one()
        self.assertEqual(self.rows()[0]['status'],'PERMISSION_DENIED')
        self.assertNotIn('SECRET',json.dumps(self.store.status()))
        self.assertNotIn('TOKEN',json.dumps(self.store.status()))

    def test_verified_migration_preserves_originals_and_works_after_reload(self):
        original=Path(self.art.fetch(self.url));digest=hashlib.sha256(original.read_bytes()).hexdigest()
        self.art.fetch(self.url+'2');result=self.storage.migrate(str(self.destination))
        self.assertEqual(result['code'],'VERIFIED');self.assertEqual(result['verified'],2)
        target=Path(self.art.folder());self.assertNotEqual(target,original.parent)
        self.assertEqual(hashlib.sha256((target/original.name).read_bytes()).hexdigest(),digest)
        self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),digest)
        self.storage=importlib.reload(self.storage);self.art=importlib.reload(self.art)
        self.assertEqual(Path(self.art.cached(self.url)).parent,target)
        self.art.fetch(self.url);self.assertEqual(self.http.call_count,2)

    def test_detached_usb_keeps_fallback_and_never_recreates_missing_volume(self):
        original=self.art.fetch(self.url);self.storage.migrate(str(self.destination));target=Path(self.art.folder())
        self.destination.rename(self.folder/'detached')
        self.assertEqual(self.art.cached(self.url),original)
        with self.assertRaises(self.storage.Paused) as caught:self.art.fetch(self.url+'new')
        self.assertEqual(caught.exception.code,'STORAGE_OFFLINE');self.assertFalse(target.exists())
        self.assertEqual(Path(original).read_bytes(),self.png)

    def test_destination_conflict_retains_policy_and_both_different_files(self):
        original=Path(self.art.fetch(self.url));target=self.destination/'XCMateArtwork/media_art_v1';target.mkdir(parents=True)
        conflict=target/original.name;conflict.write_bytes(b'other existing file')
        result=self.storage.migrate(str(self.destination))
        self.assertEqual(result['code'],'FAILED');self.assertEqual(self.art.folder(),str(original.parent))
        self.assertEqual(conflict.read_bytes(),b'other existing file');self.assertEqual(original.read_bytes(),self.png)

    def test_cancelled_migration_resumes_same_destination_with_full_verification(self):
        original=Path(self.art.fetch(self.url));self.art.fetch(self.url+'2');calls=[0]
        def cancel():calls[0]+=1;return calls[0]>3
        result=self.storage.migrate(str(self.destination),cancel)
        self.assertEqual(result['code'],'CANCELLED');self.assertEqual(self.art.folder(),str(original.parent))
        self.assertEqual(self.storage.migrate(str(self.destination))['code'],'VERIFIED')
        self.assertEqual(original.read_bytes(),self.png)

    def test_low_target_capacity_and_readonly_target_never_switch_policy(self):
        original=Path(self.art.fetch(self.url));real_usage=self.storage.shutil.disk_usage
        def capacity(path):
            return types.SimpleNamespace(total=100,free=0) if str(path).startswith(str(self.destination)) else real_usage(path)
        with mock.patch.object(self.storage.shutil,'disk_usage',side_effect=capacity):result=self.storage.migrate(str(self.destination))
        self.assertEqual(result['code'],'DISK_LOW');self.assertEqual(self.art.folder(),str(original.parent))
        with mock.patch.object(self.storage.os,'makedirs',side_effect=PermissionError(errno.EACCES,'private')):result=self.storage.migrate(str(self.destination))
        self.assertEqual(result['code'],'FAILED');self.assertEqual(original.read_bytes(),self.png)

    def test_copy_verification_failure_never_commits_root(self):
        original=Path(self.art.fetch(self.url));real_hash=self.storage._hash
        def broken(path):return 'bad' if '.partial-' in str(path) else real_hash(path)
        with mock.patch.object(self.storage,'_hash',side_effect=broken):result=self.storage.migrate(str(self.destination))
        self.assertEqual(result['code'],'FAILED');self.assertEqual(self.art.folder(),str(original.parent))
        self.assertEqual(original.read_bytes(),self.png)

    def test_migration_excludes_concurrent_download_without_blocking_gui(self):
        self.art.fetch(self.url);entered=threading.Event();release=threading.Event();real_hash=self.storage._hash
        def pause(path):entered.set();release.wait(5);return real_hash(path)
        with mock.patch.object(self.storage,'_hash',side_effect=pause):
            thread=threading.Thread(target=self.storage.migrate,args=(str(self.destination),));thread.start()
            try:
                self.assertTrue(entered.wait(2));start=time.monotonic()
                with self.assertRaises(self.storage.Paused) as caught:self.art.fetch(self.url+'new')
                self.assertEqual(caught.exception.code,'MIGRATING');self.assertLess(time.monotonic()-start,.2)
            finally:release.set();thread.join(5)
        self.assertFalse(thread.is_alive());self.assertEqual(self.http.call_count,1)

    def test_smb_uri_never_reaches_python_filesystem_and_credentials_stay_private(self):
        self.art.fetch(self.url)
        real_open=open
        def guarded(path,*args,**kw):
            self.assertFalse(str(path).startswith('smb://'));return real_open(path,*args,**kw)
        with mock.patch('builtins.open',side_effect=guarded),mock.patch.object(self.storage.shutil,'disk_usage',wraps=self.storage.shutil.disk_usage) as capacity:
            result=self.storage.migrate('smb://user:SECRET@server/share')
        self.assertEqual(result['code'],'CAPACITY_UNKNOWN');capacity.assert_not_called()
        self.assertNotIn('SECRET',json.dumps(result));self.assertNotIn('smb://',json.dumps(result))

    def test_full_scan_deduplicates_and_reports_missing_urls_and_resumes_after_restart(self):
        self.store.prefetch_selected();db=self.store.connect()
        try:self.assertEqual(db.execute("SELECT offset FROM scan WHERE kind='vod'").fetchone()[0],48)
        finally:db.close()
        self.store=importlib.reload(self.store)
        for _ in range(4):self.store.prefetch_selected()
        result=self.store.status();self.assertEqual(sum(result['counts'].values()),100)
        inventory={r['kind']:r for r in result['inventory']}
        self.assertEqual(inventory['vod']['items'],100);self.assertEqual(inventory['vod']['complete'],1)
        self.assertEqual(inventory['series']['poster_missing'],3)
        self.assertEqual(inventory['vod']['fanart_missing'],100)
        self.http.assert_not_called();self.art.ensure_worker.assert_called()
        self.art.request([dict(cover='https://image.invalid/1',backdrop_path=['https://image.invalid/1'])])
        self.assertEqual(len(self.rows()),100)

    def test_scan_does_not_advance_when_enqueue_fails_and_disabled_kind_is_skipped(self):
        self.portal['include_series']=False
        with mock.patch.object(self.store,'enqueue',side_effect=OSError(errno.ENOSPC,'private')):self.store.prefetch_selected()
        db=self.store.connect()
        try:self.assertEqual(db.execute('SELECT count(*) FROM scan').fetchone()[0],0)
        finally:db.close()
        self.store.prefetch_selected();self.assertEqual(len(self.rows()),48)
        db=self.store.connect()
        try:self.assertEqual([r[0] for r in db.execute('SELECT kind FROM scan')],['vod'])
        finally:db.close()

    def test_priority_continue_favourites_visible_then_rest(self):
        self.state.save_progress(dict(pid='p',kind='vod',sid='3'),600,2700);self.state.toggle('p','vod','2')
        self.store.prefetch_selected();self.art.request([dict(cover='https://image.invalid/1')],priority=10)
        priorities={r['url']:r['priority'] for r in self.rows()}
        self.assertEqual(priorities['https://image.invalid/3'],0);self.assertEqual(priorities['https://image.invalid/2'],5)
        self.assertEqual(priorities['https://image.invalid/1'],10);self.assertEqual(priorities['https://image.invalid/4'],20)
        self.store.run_one();self.assertEqual(self.http.call_args.args[0],'https://image.invalid/3')

    def test_profile_dialog_cancel_makes_no_change_and_action_is_nonfolder(self):
        ui=importlib.import_module('art_storage_ui');self.dialog.select.return_value=-1;ui.configure()
        self.assertFalse((self.folder/'media_art_storage_v1.json').exists())
        home=importlib.import_module('home_menu');home.settings(self.router,self.portal,'storage')
        item=next(row for row in self.added if 'action=art_storage_settings' in row[0])
        self.assertFalse(item[2]);self.assertEqual(item[1].props['IsPlayable'],'false')
        self.router._params['action']='art_storage_settings'
        with mock.patch.object(ui,'configure') as configure:self.routes.dispatch(self.router)
        configure.assert_called_once();self.assertNotEqual(self.ends[-1][1].get('succeeded'),False)

    def test_corrupt_policy_pauses_instead_of_silently_switching_back_to_internal(self):
        (self.folder/'media_art_storage_v1.json').write_text('corrupt')
        with self.assertRaises(self.storage.Paused) as caught:self.storage.policy()
        self.assertEqual(caught.exception.code,'POLICY_INVALID');self.http.assert_not_called()

    def test_volume_file_lock_blocks_another_process_even_if_sqlite_lease_expires(self):
        import subprocess
        child_code="""import sys,types
sys.path.insert(0,sys.argv[1])
sys.modules['utils']=types.SimpleNamespace(addon_data_dir=lambda:sys.argv[2])
from art_storage import lock
with lock(exclusive=True):
 print('locked',flush=True)
 sys.stdin.read()
"""
        child=subprocess.Popen([sys.executable,'-c',child_code,str(LIB),str(self.folder)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(),'locked')
            with self.assertRaises(self.storage.Paused) as caught:self.art.fetch(self.url)
            self.assertEqual(caught.exception.code,'MIGRATING');self.http.assert_not_called()
        finally:
            child.stdin.close();child.wait(timeout=5);child.stdout.close()

    def test_all_indexed_posters_and_fanarts_are_queued_not_only_first_backdrop(self):
        self.art.request([dict(cover='https://image.invalid/a',stream_icon='https://image.invalid/b',
                               movie_image='https://image.invalid/a',backdrop_path=['bad','https://image.invalid/c','https://image.invalid/d'])])
        self.assertEqual({r['url'] for r in self.rows()},{'https://image.invalid/'+name for name in 'abcd'})
        self.assertEqual(self.art.sources(dict(cover='bad',stream_icon='https://image.invalid/b'))[0],'https://image.invalid/b')


    def test_invalid_sources_do_not_create_endlessly_running_jobs(self):
        self.art.request([dict(cover='not a URL',backdrop_path='smb://private/cover')])
        self.assertEqual(self.rows(),[])
        self.store.enqueue(['not a URL']);self.store.run_one()
        self.assertEqual(self.rows()[0]['status'],'FAILED');self.assertEqual(self.rows()[0]['attempts'],1)


    def test_background_pause_after_confirmed_queue_rebuild_remains_respected(self):
        health=importlib.import_module('artwork_db')
        with mock.patch.object(health,'diagnostic',return_value={'background_paused':True}):self.store.prefetch_selected()
        self.art.ensure_worker.assert_not_called();self.http.assert_not_called()


if __name__=='__main__':unittest.main()

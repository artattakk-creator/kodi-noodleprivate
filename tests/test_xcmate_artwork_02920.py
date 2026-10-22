"""Synthetic large libraries, actual SQLite/files, bounded workers and capacity."""
import hashlib
import itertools
import importlib
import json
from pathlib import Path
import sqlite3
import struct
import sys
import time
import threading
import types
import unittest
from unittest import mock
import zlib
from xcmate027_fixture import Fixture,ADDON


class DormantThread:
    def __init__(self,*args,**kwargs):self.alive=False
    def is_alive(self):return self.alive
    def start(self):self.alive=True


class Artwork20Tests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('artwork_db','art_store','art_storage'):sys.modules.pop(name,None)
        self.health=importlib.import_module('artwork_db');self.store=importlib.import_module('art_store')
        self.policy=importlib.import_module('art_storage')
        self.art=importlib.reload(importlib.import_module('media_art'))
        self.request=self.art.request
        patch=mock.patch.object(self.art,'request');patch.start();self.addCleanup(patch.stop)
        def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        self.png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',108,162,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\x20\x30\x40'*108)*162))+chunk(b'IEND',b'')
        self.http=sys.modules['utils'].http_get;self.http.side_effect=None;self.http.return_value=(self.png,{})
        self.thread_errors=[]
        patch=mock.patch.object(threading,'excepthook',side_effect=lambda value:self.thread_errors.append(value.exc_type.__name__));patch.start();self.addCleanup(patch.stop)
        self.addCleanup(lambda:self.assertEqual(self.thread_errors,[]))

    def row(self,url):
        db=self.store.connect()
        try:
            row=db.execute('SELECT * FROM jobs WHERE ident=?',(self.store.key(url),)).fetchone()
            return dict(row) if row else None
        finally:db.close()

    def seed(self,urls,status='SPACE_FULL',attempts=3,priority=20):
        db=self.store.connect()
        try:
            with db:db.executemany('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?)',[(self.store.key(u),u,status,priority,attempts,0,1,0) for u in urls])
        finally:db.close()

    def test_default_auto_has_no_512_mib_or_4096_mib_cap_and_preserves_custom_limit(self):
        self.assertEqual(self.store.budget(),0)
        for value in (512,8192,100000):
            self.options['media_art_budget_mb']=value
            self.assertEqual(self.store.budget(),value*1048576)
        self.options['media_art_reserve_mb']=1;self.assertEqual(self.policy.reserve(),32*1048576)
        self.options['media_art_reserve_mb']=2048;self.assertEqual(self.policy.reserve(),2048*1048576)

    def test_legacy_provider_path_spaces_keep_the_same_local_cache_key(self):
        url='https://image.invalid/Movie Posters/A Film.jpg'
        filename=Path(self.art.fetch(url));calls=self.http.call_count
        self.assertEqual(self.art.sources(dict(cover=url))[0],url)
        self.assertEqual(self.art.local_art(dict(cover=url))['poster'],str(filename))
        self.assertEqual(self.art.fetch(url),str(filename));self.assertEqual(self.http.call_count,calls)
        self.assertFalse(self.art.valid_source('https://bad host.invalid/image.jpg'))
        self.assertFalse(self.art.valid_source('https://image.invalid/a\nSECRET'))

    def test_saved_kodi_default_512_migrates_readonly_but_explicit_512_survives(self):
        filename=self.folder/'settings.xml';self.options['media_art_budget_mb']=512
        for marker,expected in (('true',0),('false',512*1048576)):
            filename.write_text('<settings><setting id="media_art_budget_mb" default="'+marker+'">512</setting></settings>')
            before=filename.read_bytes();self.assertEqual(self.store.budget(),expected);self.assertEqual(filename.read_bytes(),before)
        filename.write_text('<settings><setting id="media_art_budget_mb">512</setting></settings>')
        self.assertEqual(self.store.budget(),512*1048576)

    def test_fixed_budget_and_physical_reserve_have_distinct_codes_and_no_download(self):
        url='https://image.invalid/private-token'
        self.options['media_art_budget_mb']=1
        with mock.patch.object(self.store,'used',return_value=1048576):
            with self.assertRaises(self.policy.ArtworkFailure) as error:self.art.fetch(url)
            self.assertEqual(error.exception.code,'BUDGET_FULL')
        with mock.patch.object(self.policy.shutil,'disk_usage',return_value=types.SimpleNamespace(free=32,total=100)):
            with self.assertRaises(self.policy.ArtworkFailure) as error:self.art.fetch(url)
            self.assertEqual(error.exception.code,'DISK_FULL')
        self.http.assert_not_called();self.assertFalse(list(self.folder.glob('media_art_v1/*.img')))

    def test_auto_storage_can_download_when_recorded_use_already_exceeds_512_mib(self):
        with mock.patch.object(self.store,'used',return_value=514*1048576) as used:
            filename=self.art.fetch('https://image.invalid/beyond-512')
        self.assertTrue(Path(filename).is_file());used.assert_not_called()

    def test_busy_enrolment_keeps_visible_batch_until_delayed_retry(self):
        url='https://image.invalid/visible'
        with mock.patch.object(self.art.threading,'Thread',DormantThread):self.request([dict(cover=url)])
        with mock.patch.object(self.store,'enqueue',side_effect=sqlite3.OperationalError('locked')):
            self.assertTrue(self.art._persist_next());self.assertFalse(self.art._persist_next())
        self.assertIn(url,self.art._inbox)
        now=self.art._inbox[url][3]+1
        with mock.patch.object(self.art.time,'monotonic',return_value=now),mock.patch.object(self.art.threading,'Thread',DormantThread):
            self.assertTrue(self.art._persist_next())
        self.assertFalse(self.art._inbox);self.assertEqual(self.row(url)['status'],'PENDING');self.http.assert_not_called()

    def test_free_storage_is_rechecked_after_http_before_atomic_write(self):
        reserve=self.policy.reserve();full=types.SimpleNamespace(free=reserve+10*self.art.MAX_BYTES,total=100*1048576**2)
        low=types.SimpleNamespace(free=reserve+len(self.png)-1,total=full.total)
        # check_space also probes capacity; it must not consume the post-HTTP probe.
        with mock.patch.object(self.policy,'capacity',side_effect=[dict(free=full.free,total=full.total,reserve=reserve,budget=0),dict(free=low.free,total=full.total,reserve=reserve,budget=0)]):
            with self.assertRaises(self.policy.ArtworkFailure) as error:self.art.fetch('https://image.invalid/one')
        self.assertEqual(error.exception.code,'DISK_FULL');self.assertEqual(self.http.call_count,1)
        self.assertFalse(list(self.folder.glob('media_art_v1/*')))

    def test_network_invalid_source_invalid_image_and_cache_write_are_separate(self):
        for url in ('not a URL','http://[broken','https://host.invalid:bad/x'):
            with self.assertRaises(self.policy.ArtworkFailure) as error:self.art.fetch(url)
            self.assertEqual(error.exception.code,'INVALID_SOURCE')
        self.http.assert_not_called()
        self.http.side_effect=TimeoutError('https://PRIVATE/TOKEN')
        with self.assertRaises(self.policy.ArtworkFailure) as error:self.art.fetch('https://image.invalid/network')
        self.assertEqual(str(error.exception),'[Errno 5] NETWORK_ERROR');self.assertNotIn('PRIVATE',str(error.exception))
        self.http.side_effect=None;self.http.return_value=(b'not an image',{})
        with self.assertRaises(self.policy.ArtworkFailure) as error:self.art.fetch('https://image.invalid/bad')
        self.assertEqual(error.exception.code,'INVALID_IMAGE')
        self.http.return_value=(self.png,{})
        with mock.patch.object(self.art.tempfile,'mkstemp',side_effect=PermissionError(13,'PRIVATE')):
            with self.assertRaises(self.policy.ArtworkFailure) as error:self.art.fetch('https://image.invalid/readonly')
        self.assertEqual(error.exception.code,'CACHE_ERROR')

    def test_recover_exhausted_legacy_space_jobs_in_bounded_idempotent_portions(self):
        ready='https://image.invalid/ready';filename=Path(self.art.fetch(ready));before=filename.read_bytes();readyrow=self.row(ready)
        urls=['https://image.invalid/blocked/'+str(i) for i in range(100)];self.seed(urls)
        self.seed(['https://image.invalid/network'],'NETWORK_ERROR');self.seed(['https://image.invalid/invalid'],'INVALID_IMAGE')
        stamp=time.time()+1
        self.assertEqual([self.store.recover_space(stamp+n*6) for n in range(4)],[32,32,32,4])
        db=self.store.connect()
        with db:db.execute("UPDATE jobs SET status='DISK_FULL',attempts=3 WHERE status='PENDING'")
        db.close()
        self.assertEqual(self.store.recover_space(stamp+30),0)
        self.store=importlib.reload(self.store);self.assertEqual(self.store.recover_space(stamp+40),0)
        self.assertEqual(self.row(ready),readyrow);self.assertEqual(filename.read_bytes(),before)
        self.assertEqual(self.row('https://image.invalid/network')['attempts'],3)
        self.assertEqual(self.row('https://image.invalid/invalid')['status'],'INVALID_IMAGE')
        self.options['media_art_budget_mb']=8192
        self.assertEqual(self.store.recover_space(stamp+50),32)

    def test_queue_enrolment_honours_configured_free_reserve_before_any_db_creation(self):
        value=dict(free=self.policy.reserve()+1,total=100*1048576**2,reserve=self.policy.reserve(),budget=0)
        with mock.patch.object(self.policy,'capacity',return_value=value):
            with self.assertRaises(self.policy.ArtworkFailure) as error:self.store.enqueue(['https://image.invalid/queue'])
        self.assertEqual(error.exception.code,'DISK_FULL')
        self.assertFalse(Path(self.health.path()).exists());self.http.assert_not_called()

    def test_space_recovery_does_nothing_under_physical_or_configured_pressure(self):
        urls=['https://image.invalid/one'];self.seed(urls);before=self.row(urls[0]);stamp=time.time()
        with mock.patch.object(self.policy,'check',side_effect=self.policy.ArtworkFailure('DISK_FULL')):self.assertEqual(self.store.recover_space(stamp),0)
        self.options['media_art_budget_mb']=1
        with mock.patch.object(self.store,'used',return_value=1048576):self.assertEqual(self.store.recover_space(stamp+6),0)
        self.assertEqual(self.row(urls[0]),before)

    def test_repeated_disk_full_does_not_generate_an_infinite_download_retry(self):
        url='https://image.invalid/disk';self.seed([url]);stamp=time.time()+1
        with mock.patch.object(self.art,'fetch',side_effect=self.policy.ArtworkFailure('DISK_FULL')) as fetch:
            for n in range(8):self.store.run_one(stamp+n*600)
        self.assertEqual(fetch.call_count,1);self.assertEqual(self.row(url)['status'],'DISK_FULL')

    def test_network_errors_stop_after_three_and_are_not_reset_by_space_recovery(self):
        url='https://image.invalid/network';self.store.enqueue([url]);stamp=time.time()+1
        self.http.side_effect=TimeoutError('PRIVATE URL TOKEN')
        for delta in (0,61,182,10000,20000):self.store.run_one(stamp+delta)
        self.assertEqual(self.http.call_count,3);self.assertEqual(self.row(url)['status'],'NETWORK_ERROR')
        self.assertEqual(self.row(url)['attempts'],3);self.assertEqual(self.store.recover_space(stamp+30000),0)

    def test_visible_epg_logos_precede_covers_and_oldest_job_gets_a_fair_turn(self):
        with mock.patch.object(self.art.threading,'Thread',DormantThread):
            self.request([dict(kind='vod',cover='https://image.invalid/cover')])
            self.request([dict(kind='live',stream_icon='https://image.invalid/logo')])
            while self.art._persist_next():pass
        self.assertLess(self.row('https://image.invalid/logo')['priority'],self.row('https://image.invalid/cover')['priority'])
        self.store.run_one();self.assertEqual(self.http.call_args.args[0],'https://image.invalid/logo')
        self.seed(['https://image.invalid/oldest'],'PENDING',0,20)
        for n in range(9):self.store.enqueue(['https://image.invalid/high/'+str(n)],-10)
        self.store._served=7;self.store.run_one()
        self.assertEqual(self.http.call_args.args[0],'https://image.invalid/oldest')

    def test_request_callback_never_opens_sqlite_or_http_and_inbox_is_bounded(self):
        with mock.patch.object(self.art.threading,'Thread',DormantThread),mock.patch.object(self.store,'enqueue',side_effect=AssertionError('SQLite on GUI')):
            for start in range(0,2200,48):self.request([dict(cover='https://image.invalid/'+str(i)) for i in range(start,start+48)],20)
            self.request([dict(kind='live',stream_icon='https://image.invalid/foreground')])
        self.assertLessEqual(len(self.art._inbox),self.art.MAX_INBOX)
        self.assertIn('https://image.invalid/foreground',self.art._inbox);self.http.assert_not_called()

    def test_sqlite_enrolment_retries_are_bounded_without_network_or_private_logging(self):
        with mock.patch.object(self.art.threading,'Thread',DormantThread):self.request([dict(cover='https://PRIVATE/TOKEN')])
        with mock.patch.object(self.store,'enqueue',side_effect=sqlite3.OperationalError('database is locked PRIVATE')) as enqueue,mock.patch.object(self.art.time,'monotonic',side_effect=itertools.count(0,6)):
            while self.art._persist_next():pass
        self.assertEqual(enqueue.call_count,3);self.assertFalse(self.art._inbox);self.http.assert_not_called()
        self.assertEqual(self.art.diagnose(dict(cover='https://PRIVATE/TOKEN'))['poster'],'DB_BUSY')

    def test_missing_provider_invalid_source_pending_network_and_cache_status(self):
        self.assertEqual(self.art.diagnose({})['poster'],'NO_SOURCE')
        self.assertEqual(self.art.diagnose(dict(cover='wrong'))['poster'],'INVALID_SOURCE')
        url='https://PRIVATE/TOKEN';self.store.enqueue([url])
        self.assertEqual(self.art.diagnose(dict(cover=url))['poster'],'PENDING')
        self.http.side_effect=TimeoutError('PRIVATE');self.store.run_one()
        value=self.art.diagnose(dict(cover=url));self.assertEqual(value['poster'],'NETWORK_ERROR')
        self.assertNotIn('PRIVATE',json.dumps(value));self.assertNotIn(url,json.dumps(value))
        self.http.side_effect=None;filename=Path(self.art.fetch(url));filename.write_bytes(b'corrupt')
        self.assertEqual(self.art.diagnose(dict(cover=url))['poster'],'CACHE_ERROR')

    def test_download_pause_preserves_jobs_and_ready_images(self):
        url='https://image.invalid/paused';self.store.enqueue([url]);self.options['media_art_paused']=True
        self.assertFalse(self.store.run_one());self.http.assert_not_called();self.assertEqual(self.row(url)['status'],'PENDING')
        self.options['media_art_paused']=False;self.assertTrue(self.store.run_one());self.assertEqual(self.row(url)['status'],'READY')

    def test_five_hundred_movie_and_series_posters_persist_beyond_sliding_window_and_reload(self):
        for kind in ('vod','series'):
            urls=['https://image.invalid/'+kind+'/'+str(i) for i in range(500)]
            records=[dict(stream_id=str(i),series_id=str(i),category_id='a',name='Synthetic '+str(i),stream_icon=url,added=self.now-i) for i,url in enumerate(urls)]
            self.index.import_group('p',kind,'a',records)
            w=self.media_window(kind);w.category='a';w._page('grid',0);self.settle(w)
            while w.offset+len(w.rows)<w.total:w._prefetch(force=True);self.settle(w)
            self.assertGreater(w.offset,240);self.assertLessEqual(len(w.rows),240)
            self.assertTrue(w.getControl(210).items[0].art['poster'].endswith('.png'))
            self.store.enqueue(urls)
            while self.store.run_one():pass
            w._poll_catalog();w._refresh_art()
            self.assertTrue(all(Path(li.art['poster']).suffix=='.img' for li in w.getControl(210).items))
            while w.offset:w._prefetch(-1,force=True);self.settle(w)
            self.assertTrue(all(Path(li.art['poster']).suffix=='.img' for li in w.getControl(210).items))
            before={u:hashlib.sha256(Path(self.art.cached(u)).read_bytes()).hexdigest() for u in urls};calls=self.http.call_count
            self.art=importlib.reload(self.art)
            patch=mock.patch.object(self.art,'request');patch.start();self.addCleanup(patch.stop)
            for url in urls:self.assertEqual(hashlib.sha256(Path(self.art.fetch(url)).read_bytes()).hexdigest(),before[url])
            self.assertEqual(self.http.call_count,calls);w.close()
        self.assertEqual(self.http.call_count,1000)

    def test_read_only_diagnosis_under_writer_lock_does_not_repair_or_reset(self):
        url='https://image.invalid/one';self.store.enqueue([url]);writer=sqlite3.connect(self.health.path());writer.execute('BEGIN EXCLUSIVE')
        try:
            with mock.patch.object(self.health,'maintain',side_effect=AssertionError('repair')):
                value=self.art.diagnose(dict(cover=url));self.assertEqual(value['poster'],'DB_BUSY')
        finally:writer.rollback();writer.close()
        self.assertEqual(self.row(url)['status'],'PENDING')

    def test_old_worker_cannot_overwrite_replacement_ready_or_release_its_lease(self):
        url='https://image.invalid/lease';self.store.enqueue([url])
        def takeover(url):
            self.store.ready(url,123)
            db=self.store.connect()
            with db:db.execute("UPDATE worker SET owner='replacement',until=9999999999 WHERE id=1")
            db.close();raise self.policy.ArtworkFailure('NETWORK_ERROR')
        with mock.patch.object(self.art,'fetch',side_effect=takeover):self.store.run_one()
        self.assertEqual(self.row(url)['status'],'READY')
        db=self.store.connect();self.assertEqual(db.execute('SELECT owner FROM worker').fetchone()[0],'replacement');db.close()

    def test_lost_job_claim_does_not_leave_thirty_second_global_lease(self):
        self.store.enqueue(['https://image.invalid/lost'])
        db=self.store.connect()
        with db:db.execute("CREATE TRIGGER no_claim BEFORE UPDATE ON jobs WHEN NEW.status='RUNNING' BEGIN SELECT RAISE(IGNORE); END")
        db.close();self.assertFalse(self.store.run_one())
        db=self.store.connect();self.assertEqual(db.execute('SELECT until FROM worker').fetchone()[0],0);db.close();self.http.assert_not_called()

    def test_real_enrol_and_download_workers_use_their_own_sqlite_connections(self):
        abort=threading.Event();owner=threading.get_ident();threads=[];real_thread=threading.Thread
        monitor=types.SimpleNamespace(abortRequested=abort.is_set,waitForAbort=lambda seconds:abort.wait(min(seconds,.02)))
        def thread(*args,**kwargs):
            value=real_thread(*args,**kwargs);threads.append(value);return value
        def network(*args,**kwargs):
            self.assertNotEqual(threading.get_ident(),owner);return self.png,{}
        url='https://image.invalid/worker'
        with mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=monitor),mock.patch.object(self.art.threading,'Thread',side_effect=thread):
            self.http.side_effect=network
            try:
                self.request([dict(cover=url)])
                deadline=time.monotonic()+3
                while time.monotonic()<deadline and not self.art.cached(url):abort.wait(.01)
                self.assertTrue(self.art.cached(url))
            finally:
                abort.set()
                for value in threads:value.join(2)
        self.assertEqual(len(threads),2);self.assertTrue(all(not value.is_alive() for value in threads))
        self.assertEqual(self.row(url)['status'],'READY');self.assertEqual(self.thread_errors,[])

    def test_existing_queue_gains_only_additive_retry_metadata_and_keeps_jobs(self):
        # Reproduce .19's complete schema without the new auxiliary table.
        db=sqlite3.connect(self.health.path())
        for statement in self.health._SCHEMA:
            if 'art_recovery' not in statement:db.execute(statement)
        db.execute('INSERT INTO worker(id,until) VALUES(1,0)')
        db.execute("INSERT INTO jobs VALUES('kept','PRIVATE','READY',20,0,0,1,123)");db.commit()
        before=list(db.execute('SELECT * FROM jobs'));db.close()
        self.store.connect().close()
        db=sqlite3.connect(self.health.path())
        self.assertEqual(list(db.execute('SELECT * FROM jobs')),before)
        self.assertEqual(db.execute('SELECT count(*) FROM art_recovery').fetchone()[0],0);db.close()

    def test_enrolment_disk_full_is_distinct_from_database_contention(self):
        url='https://image.invalid/full'
        with mock.patch.object(self.art.threading,'Thread',DormantThread):self.request([dict(cover=url)])
        with mock.patch.object(self.store,'enqueue',side_effect=OSError(28,'PRIVATE')):self.art._persist_next()
        self.assertEqual(self.art.diagnose(dict(cover=url))['poster'],'DISK_FULL');self.http.assert_not_called()

    def test_licences_are_accessible_without_active_portal(self):
        self.portals=[];self.router._params['action']='xcmate_licenses'
        self.routes.dispatch(self.router)
        self.assertIn('GNU GENERAL PUBLIC LICENSE',self.dialog.textviewer.call_args.args[1])
        self.assertEqual(len(self.ends),1)

    def test_footer_describes_current_continue_cover_and_refreshes_without_reopening(self):
        self.state.save_progress(dict(pid='p',kind='vod',sid='2'),300,1200)
        w=self.media_window();self.assertEqual(w.getFocusId(),112)
        self.assertEqual(w._art_selected['sid'],'2')
        self.art.fetch(w.rails[112][0]['stream_icon']);w._poll_catalog()
        self.assertIn('lokal gespeichert',w.getControl(501).label)
        self.assertTrue(w.getControl(112).items[0].art['poster'].endswith('.img'))
        self.assertEqual(w.getFocusId(),112)

    def test_public_title_is_gs_media_and_licence_origin_stay_visible(self):
        import xml.etree.ElementTree as ET
        addon=ET.parse(ADDON/'addon.xml').getroot();self.assertEqual(addon.get('provider-name'),'GS Media');self.assertEqual(addon.get('name'),'XCMate')
        self.assertIn('mr-evil1',' '.join(n.text or '' for n in addon.findall('.//description')))
        self.router._params['action']='xcmate_licenses';self.routes.dispatch(self.router)
        text=self.dialog.textviewer.call_args.args[1]
        self.assertIn('mr-evil1',text);self.assertIn('GNU GENERAL PUBLIC LICENSE',text)
        self.assertEqual(len(self.ends),1)


if __name__=='__main__':unittest.main()

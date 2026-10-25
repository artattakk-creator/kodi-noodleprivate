"""Artwork pipeline on real files/SQLite; simulated storage is never Android PASS."""
import hashlib
import importlib
import json
from pathlib import Path
import sqlite3
import sys
import threading
import time
import types
import unittest
from unittest import mock
from urllib.error import HTTPError,URLError
import socket
import ssl
import test_xcmate_artwork_02920 as model


class Artwork36(unittest.TestCase):
    def setUp(self):
        self.m=model.Artwork20Tests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.art=self.m.art;self.store=self.m.store;self.policy=self.m.policy

    def test_metadata_queue_survives_below_image_reserve_but_download_remains_blocked(self):
        url='https://image.invalid/reserve-repro'
        usage=types.SimpleNamespace(free=512*1048576,total=2*1024**3)
        with mock.patch.object(importlib.import_module('artwork_backend').shutil,'disk_usage',return_value=usage):
            self.store.enqueue([url])
            self.assertEqual(self.m.row(url)['status'],'PENDING')
            self.store.run_one()
        self.assertEqual(self.m.row(url)['status'],'DISK_FULL');self.m.http.assert_not_called()
        self.assertEqual(self.policy.reserve(),1024*1048576)

    def test_persistent_jobs_start_worker_after_restart_without_a_new_ui_enrolment(self):
        self.store.enqueue(['https://image.invalid/restart'])
        self.art._worker=None;self.art._enrol_worker=None
        with mock.patch.object(self.art.threading,'Thread',model.DormantThread):
            self.art.ensure_worker()
        self.assertTrue(self.art._worker.is_alive())
        self.assertIsNone(self.art._enrol_worker);self.assertEqual(self.art._inbox,{})

    def test_cover_big_survives_regular_catalog_import(self):
        self.m.index.replace_catalog('p','vod',[dict(stream_id='99',category_id='a',name='Only big source',cover_big='https://image.invalid/big')],self.m.catalogs['get_vod_categories'])
        row=self.m.index.Reader('p').get('vod','99')
        self.assertEqual(self.art.poster_candidates(row),['https://image.invalid/big'])

    def test_streaming_group_import_also_retains_cover_big(self):
        self.m.index.import_group('p','series','a',[dict(series_id='99',category_id='a',name='Big series',cover_big='https://image.invalid/series')])
        self.assertEqual(self.art.poster_candidates(self.m.index.Reader('p').get('series','99')),['https://image.invalid/series'])

    def test_storage_explanation_distinguishes_physical_headroom_reserve_and_budget(self):
        size=self.art.MAX_BYTES;reserve=self.policy.reserve();headroom=self.policy.WRITE_HEADROOM
        values=dict(free=1,total=2*1024**3,reserve=reserve,budget=0)
        self.assertEqual(self.policy.explain(values,size,0),'BLOCKED_REAL_DISK')
        values['free']=512*1048576
        self.assertEqual(self.policy.explain(values,size,0),'RESERVE_BLOCKED')
        values.update(free=2*1024**3,budget=1048576)
        self.assertEqual(self.policy.explain(values,size,0),'BUDGET_FULL')
        self.assertEqual(self.policy.explain(values,size,None),'UNKNOWN')
        values['budget']=0;self.assertEqual(self.policy.explain(values,size,0),'OK')
        self.assertEqual(self.policy.explain({},size,0),'UNKNOWN')
        values['free']=reserve+size+headroom
        self.assertEqual(self.policy.explain(values,size,0),'OK')

    def test_metadata_real_disk_guard_does_not_create_database_or_consume_http(self):
        usage=types.SimpleNamespace(free=31*1048576,total=2*1024**3)
        with mock.patch.object(importlib.import_module('artwork_backend').shutil,'disk_usage',return_value=usage):
            with self.assertRaises(OSError) as error:self.store.enqueue(['https://image.invalid/one'])
        self.assertEqual(error.exception.errno,28);self.assertFalse(Path(self.m.health.path()).exists())
        self.m.http.assert_not_called()

    def test_existing_artwork_directory_mount_is_the_capacity_target(self):
        root=Path(self.art.folder());root.mkdir()
        with mock.patch.object(importlib.import_module('artwork_backend').shutil,'disk_usage',return_value=types.SimpleNamespace(free=10**10,total=10**11)) as usage:
            self.policy.capacity()
        usage.assert_called_once_with(str(root))

    def test_actual_enospc_reports_distinct_reason_and_preserves_existing_images(self):
        kept=Path(self.art.fetch('https://image.invalid/kept'));before=kept.read_bytes()
        with mock.patch.object(importlib.import_module('artwork_backend').tempfile,'mkstemp',side_effect=OSError(28,'PRIVATE PATH')):
            with self.assertRaises(self.policy.ArtworkFailure) as error:self.art.fetch('https://image.invalid/new')
        self.assertEqual(error.exception.reason,'PHYSICAL_ENOSPC')
        self.assertEqual(kept.read_bytes(),before);self.assertEqual(self.m.row('https://image.invalid/kept')['status'],'READY')

    def test_worker_start_is_idempotent_and_replaces_only_dead_thread(self):
        with mock.patch.object(self.art.threading,'Thread',model.DormantThread) as factory:
            self.assertTrue(self.art.ensure_worker());worker=self.art._worker
            for _ in range(10):self.art.ensure_worker()
            self.assertIs(self.art._worker,worker)
            worker.alive=False;self.assertTrue(self.art.ensure_worker())
            self.assertIsNot(self.art._worker,worker)

    def test_shutdown_prevents_new_worker_and_thread_limit_failure_is_reported(self):
        with mock.patch.object(self.art.threading,'Thread',side_effect=RuntimeError('PRIVATE')):
            self.assertFalse(self.art.ensure_worker())
        diag=importlib.import_module('art_diagnostics')
        self.assertEqual(diag.observation('service')['code'],'START_FAILED')
        self.art._stop.set()
        with mock.patch.object(self.art.threading,'Thread',side_effect=AssertionError('after shutdown')):
            self.assertFalse(self.art.ensure_worker())

    def test_paused_jobs_are_preserved_and_are_not_reactivated_by_liveness(self):
        url='https://image.invalid/paused36';self.store.enqueue([url]);self.m.options['media_art_paused']=True
        with mock.patch.object(self.art.threading,'Thread',model.DormantThread):self.art.ensure_worker()
        self.assertFalse(self.store.run_one());self.m.http.assert_not_called()
        self.assertEqual(self.m.row(url)['status'],'PENDING');self.assertTrue(self.m.options['media_art_paused'])

    def test_service_wake_is_on_background_data_loop_before_optional_warming(self):
        import ast
        source=Path(self.art.__file__).with_name('app_services.py').read_text()
        tree=ast.parse(source);worker=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_run')
        poll=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='poll')
        text=ast.unparse(worker)
        self.assertLess(text.index('ensure_worker()'),text.index('refresh_local(cancelled)'))
        self.assertNotIn('ensure_worker',ast.unparse(poll))

    def checkpoint(self,kind='vod',ack=False):
        reader=self.m.index.Reader('p');state=reader.state(kind)
        revision=state['revision']+str([g['cid'] for g in reader.groups(kind)])+('|persisted36' if ack else '')
        db=self.store.connect()
        with db:db.execute('INSERT OR REPLACE INTO scan VALUES(?,?,?,-1)',('p',kind,revision))
        db.close();return revision

    def test_scan_checkpoint_waits_for_successful_durable_enrolment(self):
        self.m.portal['include_series']=False
        with mock.patch.object(self.store,'enqueue',side_effect=sqlite3.OperationalError('PRIVATE locked')):
            with self.assertRaises(sqlite3.OperationalError):self.store.prefetch_selected()
        db=self.store.connect();self.assertEqual(db.execute('SELECT count(*) FROM scan').fetchone()[0],0);db.close()

    def test_old_completed_scan_with_empty_queue_recovers_one_acknowledged_page(self):
        self.m.portal['include_series']=False;old=self.checkpoint()
        self.store.prefetch_selected()
        db=self.store.connect();row=db.execute('SELECT revision,offset FROM scan').fetchone()
        self.assertEqual(row['revision'],old+'|persisted36');self.assertEqual(row['offset'],48)
        self.assertEqual(db.execute('SELECT count(*) FROM jobs').fetchone()[0],48);db.close()
        self.m.http.assert_not_called()  # This is metadata-only background work.

    def test_acknowledged_empty_scan_is_not_endlessly_restarted(self):
        self.m.portal['include_series']=False;self.checkpoint(ack=True)
        with mock.patch.object(self.store,'enqueue',side_effect=AssertionError('scan restarted')):
            for _ in range(5):self.store.prefetch_selected()

    def test_existing_exhausted_jobs_and_ready_images_do_not_trigger_scan_recovery(self):
        self.m.portal['include_series']=False;self.checkpoint()
        self.m.seed(['https://image.invalid/old-network'],'TIMEOUT',attempts=3)
        kept=Path(self.art.fetch('https://image.invalid/old-ready'));before=kept.read_bytes()
        db=self.store.connect();rows=[tuple(r) for r in db.execute('SELECT * FROM jobs ORDER BY ident')];db.close()
        with mock.patch.object(self.store,'enqueue',side_effect=AssertionError('global replay')):self.store.prefetch_selected()
        db=self.store.connect();self.assertEqual(rows,[tuple(r) for r in db.execute('SELECT * FROM jobs ORDER BY ident')]);db.close()
        self.assertEqual(before,kept.read_bytes())

    def test_http_dns_tls_timeout_and_validation_errors_are_not_reported_as_storage(self):
        cases=[(HTTPError('PRIVATE',403,'SECRET',{},None),'HTTP_AUTH'),
               (HTTPError('PRIVATE',404,'SECRET',{},None),'HTTP_NOT_FOUND'),
               (HTTPError('PRIVATE',429,'SECRET',{'Retry-After':'600'},None),'HTTP_RATE_LIMIT'),
               (HTTPError('PRIVATE',503,'SECRET',{},None),'HTTP_SERVER'),
               (URLError(socket.gaierror('PRIVATE')),'DNS_ERROR'),
               (URLError(ssl.SSLError('PRIVATE')),'TLS_ERROR'),(TimeoutError('PRIVATE'),'TIMEOUT')]
        for i,(error,code) in enumerate(cases):
            url='https://image.invalid/error36/'+str(i);self.store.enqueue([url]);self.m.http.side_effect=error
            self.store.run_one()
            self.assertEqual(self.m.row(url)['status'],code)
        self.m.http.side_effect=None;self.m.http.return_value=(b'<html>not image</html>',{})
        url='https://image.invalid/bad36';self.store.enqueue([url]);self.store.run_one()
        self.assertEqual(self.m.row(url)['status'],'INVALID_IMAGE')

    def test_stale_runtime_and_private_property_values_are_unknown_not_false_success(self):
        diag=importlib.import_module('art_diagnostics')
        self.m.properties['XCMate.Artwork.worker']=json.dumps(dict(code='ACTIVE',at=time.time()-30,worker_alive=1))
        self.assertEqual(diag.observation('worker'),dict(code='UNKNOWN'))
        self.m.properties['XCMate.Artwork.request']=json.dumps(dict(code='READY',at=time.time(),url='https://PRIVATE/TOKEN',items='SECRET',reason='PRIVATE'))
        self.assertNotIn('PRIVATE',json.dumps(diag.observation('request')));self.assertNotIn('SECRET',json.dumps(diag.observation('request')))

    def test_source_presence_invalid_and_no_source_are_separate_and_private(self):
        with mock.patch.object(self.art.threading,'Thread',model.DormantThread):
            self.m.request([dict(kind='vod',cover='https://PRIVATE/TOKEN'),dict(kind='series'),dict(kind='live',stream_icon='bad')])
        diag=importlib.import_module('art_diagnostics');value=diag.observation('request')
        self.assertEqual((value['valid_source'],value['no_source'],value['invalid_source']),(1,1,1))
        self.assertEqual(value['vod_sources'],1);self.assertNotIn('PRIVATE',json.dumps(value))

    def test_status_is_readonly_reports_exact_capacity_and_queue_lease_without_urls(self):
        url='https://PRIVATE/TOKEN';self.store.enqueue([url]);db=self.store.connect()
        with db:db.execute('UPDATE worker SET until=?,owner=? WHERE id=1',(time.time()+20,'SECRET'))
        db.close();before=Path(self.m.health.path()).read_bytes()
        usage=types.SimpleNamespace(free=512*1048576,total=2*1024**3)
        with mock.patch.object(importlib.import_module('artwork_backend').shutil,'disk_usage',return_value=usage),mock.patch.object(self.store,'used',side_effect=AssertionError('adoption')):
            value=self.store.status()
        self.assertEqual(value['storage_result'],'RESERVE_BLOCKED');self.assertEqual(value['free'],usage.free)
        self.assertGreater(value['queue_details']['lease_until'],time.time())
        self.assertEqual(before,Path(self.m.health.path()).read_bytes())
        self.assertNotIn('PRIVATE',json.dumps(value));self.assertNotIn('SECRET',json.dumps(value))

    def test_status_and_source_logs_never_expose_provider_urls_credentials_or_ids(self):
        xbmc=sys.modules['xbmc'];xbmc.LOGINFO=1;logs=[]
        diag=importlib.import_module('art_diagnostics');diag._last.clear()
        with mock.patch.object(xbmc,'log',side_effect=lambda value,*a:logs.append(value),create=True),mock.patch.object(self.art.threading,'Thread',model.DormantThread):
            self.m.request([dict(kind='vod',sid='PRIVATE-ID',cover='https://PRIVATE/TOKEN')]);self.art._persist_next()
        joined='\n'.join(logs)
        for private in ('PRIVATE','TOKEN','PRIVATE-ID','https://'):self.assertNotIn(private,joined)
        self.assertIn('[ARTWORK]',joined)

    def test_status_text_explains_reserve_budget_and_unknown_worker_with_numeric_bytes(self):
        ui=importlib.import_module('artwork_health_ui')
        value=dict(code='OK',counts={},bytes=0,free=512*1048576,total=2*1024**3,budget=0,reserve=self.policy.reserve())
        value=importlib.import_module('art_diagnostics').augment(value)
        text=ui.status_text(value)
        self.assertIn('RESERVE_BLOCKED',text);self.assertIn(str(512*1048576),text);self.assertIn('UNKNOWN',text)

    def test_two_callers_share_download_lease_and_expired_lease_recovers_without_reset(self):
        url='https://image.invalid/concurrent36';self.store.enqueue([url]);entered=threading.Event();release=threading.Event();results=[]
        def network(*args,**kwargs):entered.set();release.wait(2);return self.m.png,{}
        self.m.http.side_effect=network
        worker=threading.Thread(target=lambda:results.append(self.store.run_one()));worker.start()
        self.assertTrue(entered.wait(2));self.assertFalse(self.store.run_one());release.set();worker.join(2)
        self.assertFalse(worker.is_alive());self.assertEqual(self.m.http.call_count,1);self.assertEqual(results,[True])
        self.assertEqual(self.m.row(url)['status'],'READY')
        # A dead former process's lease expires; no attempt/global reset needed.
        other='https://image.invalid/expired36';self.store.enqueue([other]);db=self.store.connect()
        with db:db.execute("UPDATE worker SET until=?,owner='dead' WHERE id=1",(time.time()-1,))
        db.close();self.m.http.side_effect=None;self.store.run_one();self.assertEqual(self.m.row(other)['status'],'READY')

    def test_legacy_logo_worker_restarts_and_keeps_all_existing_image_files(self):
        sys.modules.pop('logo_cache',None);logos=importlib.import_module('logo_cache')
        target=self.m.folder/'tv_logos';target.mkdir()
        for i in range(129):(target/(str(i)+'.img')).write_bytes(self.m.png)
        before={p.name:p.read_bytes() for p in target.iterdir()}
        urls=['https://image.invalid/logo36/1','https://image.invalid/logo36/2']
        queue=types.SimpleNamespace(get=mock.Mock(side_effect=urls+[StopIteration]),task_done=mock.Mock())
        with mock.patch.object(logos,'_QUEUE',queue):
            with self.assertRaises(StopIteration):logos._run()
        self.assertEqual(len(list(target.iterdir())),131)
        for name,data in before.items():self.assertEqual((target/name).read_bytes(),data)
        calls=self.m.http.call_count
        logos=importlib.reload(logos)
        queue.get=mock.Mock(side_effect=urls+[StopIteration])
        with mock.patch.object(logos,'_QUEUE',queue):
            with self.assertRaises(StopIteration):logos._run()
        self.assertTrue(all(Path(logos.local_logo(url)).is_file() for url in urls));self.assertEqual(self.m.http.call_count,calls)
        logos._WORKER=model.DormantThread()
        with mock.patch.object(logos.threading,'Thread',model.DormantThread):
            logos.request([types.SimpleNamespace(logo='https://image.invalid/new')])
        self.assertTrue(logos._WORKER.is_alive())

    def test_real_local_http_three_movies_two_series_two_logos_repaint_and_survive_reload(self):
        """Seven generated PNG fixtures, never real-provider/Android acceptance."""
        from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
        from urllib.request import urlopen
        from PIL import Image
        import io
        payloads={}
        for i in range(7):
            stream=io.BytesIO();Image.new('RGB',(90+i,140+i),(20+i*30,40+i*20,80+i*10)).save(stream,format='PNG')
            payloads['/'+str(i)]=stream.getvalue()
        hits=[]
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                data=payloads[self.path.split('?')[0]];hits.append(self.path.split('?')[0])
                self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        serving=threading.Thread(target=server.serve_forever,daemon=True);serving.start()
        self.addCleanup(server.server_close);self.addCleanup(serving.join,2);self.addCleanup(server.shutdown)
        base='http://127.0.0.1:'+str(server.server_port)
        records=[dict(kind='vod' if i<3 else 'series' if i<5 else 'live',sid=str(i),stream_id=str(i),series_id=str(i),
                      category_id='a',name='HTTP fixture '+str(i),added=self.m.now,stream_icon=base+'/'+str(i)+'?token=SYNTHETIC') for i in range(7)]
        self.m.index.replace_catalog('p','vod',records[:3],self.m.catalogs['get_vod_categories'])
        self.m.index.replace_catalog('p','series',records[3:5],self.m.catalogs['get_series_categories'])
        window=self.m.media_window();window.category='a';window._page('grid',0);self.m.settle(window)
        focus=window.getFocusId()
        self.assertTrue(all(li.art['poster'].endswith('.png') for li in window.getControl(210).items))
        kept_url='https://image.invalid/kept-before-http';kept=Path(self.art.fetch(kept_url));before=kept.read_bytes();row_before=self.m.row(kept_url)
        urls=[r['stream_icon'] for r in records];self.store.enqueue(urls)
        abort=threading.Event();owner=threading.get_ident()
        monitor=types.SimpleNamespace(abortRequested=abort.is_set,waitForAbort=lambda seconds:abort.wait(min(seconds,.02)))
        def http(url,**kw):
            self.assertNotEqual(threading.get_ident(),owner)
            with urlopen(url,timeout=kw.get('timeout',4)) as response:return response.read(kw['max_bytes']+1),{}
        self.m.http.side_effect=http
        started=time.perf_counter_ns();first_ready_ms=None
        with mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=monitor),mock.patch('service_runtime.pressure',return_value=False):
            try:
                self.assertIsNone(self.art._enrol_worker)
                self.art.ensure_worker()  # Existing jobs, no new UI enrolment.
                deadline=time.monotonic()+5
                while time.monotonic()<deadline:
                    if first_ready_ms is None and any(self.art.cached(url) for url in urls):first_ready_ms=(time.perf_counter_ns()-started)/1e6
                    if all(self.art.cached(url) for url in urls) and all(self.m.row(url)['status']=='READY' for url in urls):break
                    abort.wait(.01)
                self.assertTrue(all(self.art.cached(url) for url in urls))
            finally:
                abort.set()
                if self.art._worker:self.art._worker.join(2)
        self.assertEqual(len(hits),7);self.assertEqual(len(set(hits)),7)
        for i,url in enumerate(urls):
            self.assertEqual(Path(self.art.cached(url)).read_bytes(),payloads['/'+str(i)])
            self.assertEqual(self.m.row(url)['status'],'READY')
        window._refresh_art()
        self.assertTrue(all(li.art['poster'].endswith('.img') for li in window.getControl(210).items))
        self.assertEqual(window.getFocusId(),focus)
        hashes={url:hashlib.sha256(Path(self.art.cached(url)).read_bytes()).hexdigest() for url in urls}
        self.art=importlib.reload(self.art)
        self.m.http.side_effect=AssertionError('Unexpected re-download after reload')
        for url,digest in hashes.items():self.assertEqual(hashlib.sha256(Path(self.art.cached(url)).read_bytes()).hexdigest(),digest)
        self.assertTrue(all(self.art.local_art(row)['poster'].endswith('.img') for row in records))
        self.assertEqual(self.m.row(kept_url),row_before);self.assertEqual(kept.read_bytes(),before)
        self.assertEqual(self.store.status()['counts']['READY'],8)
        self.metrics=dict(fixture_images=7,movies=3,series=2,logos=2,http_requests=len(hits),
            fixture_bytes=[len(payloads['/'+str(i)]) for i in range(7)],first_ready_ms=first_ready_ms,
            total_host_test_ms=(time.perf_counter_ns()-started)/1e6,all_jobs_ready=True,
            movie_grid_repaint=True,focus_preserved=True,all_local_paths_after_reload=True,
            extra_http_after_reload=0,existing_ready_row_and_file_preserved=True,
            native_kodi_or_android_executed=False)

    def test_legacy_logo_reserve_block_is_numeric_and_never_fake_ready(self):
        sys.modules.pop('logo_cache',None);logos=importlib.import_module('logo_cache');url='https://image.invalid/blocked-logo'
        queue=types.SimpleNamespace(get=mock.Mock(side_effect=[url,StopIteration]),task_done=mock.Mock())
        usage=types.SimpleNamespace(free=512*1048576,total=2*1024**3)
        with mock.patch.object(logos,'_QUEUE',queue),mock.patch.object(importlib.import_module('artwork_backend').shutil,'disk_usage',return_value=usage):
            with self.assertRaises(StopIteration):logos._run()
        self.m.http.assert_not_called();self.assertEqual(logos.local_logo(url),'')
        value=importlib.import_module('art_diagnostics').observation('logo')
        self.assertEqual(value['reason'],'RESERVE_BLOCKED');self.assertEqual(value['free'],usage.free)

    def test_invalid_legacy_logo_is_not_published_as_a_download(self):
        sys.modules.pop('logo_cache',None);logos=importlib.import_module('logo_cache');url='https://image.invalid/invalid-logo'
        self.m.http.return_value=(b'not an image',{})
        queue=types.SimpleNamespace(get=mock.Mock(side_effect=[url,StopIteration]),task_done=mock.Mock())
        with mock.patch.object(logos,'_QUEUE',queue):
            with self.assertRaises(StopIteration):logos._run()
        self.assertEqual(logos.local_logo(url),'')
        self.assertEqual(importlib.import_module('art_diagnostics').observation('logo')['code'],'INVALID_IMAGE')

    def test_readonly_status_api_contract_for_kodi_212_and_213_models(self):
        """Common Omega APIs under both build labels, not native Kodi binaries."""
        diag=importlib.import_module('art_diagnostics')
        for build in ('21.2 (21.2.0)','21.3 (21.3.0)'):
            with self.subTest(build=build),mock.patch.object(sys.modules['xbmc'],'getInfoLabel',return_value=build):
                diag._last.clear();diag.publish('request','REQUESTED',items=1,valid_source=1)
                value=self.store.status()
                self.assertEqual(value['observations']['request']['valid_source'],1)
                self.assertIn(value['storage_result'],('OK','RESERVE_BLOCKED','BLOCKED_REAL_DISK'))

    def test_pending_image_http_does_not_block_native_search_focus_or_live_names(self):
        url='https://image.invalid/held36';self.store.enqueue([url])
        entered=threading.Event();release=threading.Event();results=[]
        def network(*args,**kwargs):entered.set();release.wait(2);return self.m.png,{}
        self.m.http.side_effect=network
        worker=threading.Thread(target=lambda:results.append(self.store.run_one()));worker.start()
        try:
            self.assertTrue(entered.wait(2))
            window=self.m.media_window();self.m.dialog.input.return_value='House';window._search();self.m.settle(window)
            self.assertGreater(window._search_data['live']['total'],0)
            self.assertTrue(worker.is_alive());self.assertFalse(release.is_set())
            window.onClick(700);self.m.settle(window);window.native(4)
            self.assertEqual(window.getFocusId(),710)
            self.assertTrue(worker.is_alive());self.assertFalse(release.is_set())
        finally:release.set();worker.join(2)
        self.assertFalse(worker.is_alive());self.assertEqual(results,[True])

    def test_storage_contract_preserves_legacy_roots_keys_and_read_only_inventory(self):
        backend=importlib.import_module('artwork_backend');storage=backend.active_backend()
        self.assertIsInstance(storage,backend.ArtworkStorageBackend)
        url='https://image.invalid/backend36';ident=self.store.key(url)
        target=Path(self.art.fetch(url));before=target.read_bytes()
        self.assertEqual(target,Path(self.m.folder)/'media_art_v1'/(ident+'.img'))
        self.assertEqual(list(storage.enumerate_for_migration()),[dict(ident=ident,bytes=len(before))])
        self.assertEqual(storage.read(ident,65536),before)
        self.assertEqual(storage.availability(),'AVAILABLE')
        self.assertEqual(target.read_bytes(),before)
        self.assertFalse(hasattr(storage,'remove_confirmed_original'))

    def test_vfs_and_traversal_are_rejected_before_posix_access_without_fallback(self):
        backend=importlib.import_module('artwork_backend')
        with mock.patch.object(backend.os,'stat',side_effect=AssertionError('must not probe URI')):
            for target in ('smb://PRIVATE/SECRET','special://profile/SECRET','relative'):
                with self.assertRaisesRegex(ValueError,'UNSUPPORTED_ARTWORK_BACKEND'):backend.LocalArtworkStorage(target)
        local=backend.active_backend()
        for key in ('../unsafe','a'*63,'a'*63+'/', 'g'*64):
            with self.assertRaisesRegex(ValueError,'INVALID_ARTWORK_KEY'):local.resolve_target(key)

    def test_failed_readback_keeps_original_and_never_commits_ready(self):
        backend=importlib.import_module('artwork_backend');storage=backend.active_backend()
        url='https://image.invalid/verify36';target=Path(self.art.fetch(url));original=target.read_bytes()
        ident=self.store.key(url)
        # A valid image changed on readback must not replace an existing file.
        with mock.patch.object(backend.hashlib,'sha256') as digest:
            digest.return_value.digest.side_effect=[b'actual',b'expected']
            with self.assertRaisesRegex(OSError,'ARTWORK_VERIFY_FAILED'):
                storage.write_verified(ident,self.m.png,lambda data:True)
        self.assertEqual(target.read_bytes(),original)
        self.assertEqual(list(target.parent.glob('.art-*')),[])
        self.assertEqual(self.m.row(url)['status'],'READY')

    def test_fetch_uses_backend_operations_for_read_write_capacity_and_display(self):
        backend=importlib.import_module('artwork_backend')
        class MemoryStorage:
            def __init__(self):self.files={};self.writes=0
            def read(self,key,limit):
                if key not in self.files:raise FileNotFoundError()
                return self.files[key][:limit]
            def write_verified(self,key,data,validate):
                assert validate(data);self.files[key]=data;self.writes+=1
                return self.make_display_uri(key)
            def make_display_uri(self,key):return 'fixture-image://'+key
            def free_or_unknown(self):return dict(free=10**10,total=10**11)
            def stat(self,key=None):return dict(bytes=len(self.files[key]),revision=1)
        storage=MemoryStorage();url='https://image.invalid/adapter36'
        with mock.patch.object(backend,'active_backend',return_value=storage),mock.patch.object(backend.os,'replace',side_effect=AssertionError('POSIX outside adapter')):
            displayed=self.art.fetch(url)
            self.assertEqual(self.art.cached(url),displayed)
            self.assertEqual(self.art.fetch(url),displayed)
        self.assertEqual(storage.writes,1);self.assertEqual(self.m.http.call_count,1)
        self.assertEqual(self.m.row(url)['status'],'READY')

    def test_unknown_backend_capacity_is_not_invented_or_borrowed_from_internal_disk(self):
        backend=importlib.import_module('artwork_backend');storage=mock.Mock()
        storage.free_or_unknown.return_value=dict(free=None,total=None)
        with mock.patch.object(backend,'active_backend',return_value=storage),mock.patch.object(backend.shutil,'disk_usage',side_effect=AssertionError('wrong mount')):
            value=self.policy.capacity();self.assertIsNone(value['free'])
            with self.assertRaises(self.policy.ArtworkFailure) as error:self.policy.check(512)
        self.assertEqual(error.exception.reason,'CAPACITY_UNKNOWN')
        self.m.http.assert_not_called()

    def test_job_metadata_remains_internal_when_image_backend_has_other_root(self):
        backend=importlib.import_module('artwork_backend')
        external=self.m.folder/'simulated-other-mount'
        with mock.patch.object(backend,'active_backend',return_value=backend.LocalArtworkStorage(external)):
            self.store.enqueue(['https://image.invalid/internal-db36'])
        self.assertEqual(Path(self.m.health.path()).parent,self.m.folder)
        self.assertFalse(external.exists())

    def test_internal_ready_metadata_guard_remains_independent_of_image_capacity(self):
        backend=importlib.import_module('artwork_backend');storage=backend.active_backend()
        # The future image target could be large while internal metadata is
        # blocked. Do not download then falsely publish a durable READY.
        with mock.patch.object(storage,'free_or_unknown',return_value=dict(free=10**10,total=10**11)),mock.patch.object(backend,'active_backend',return_value=storage),mock.patch('import_budget.check_space',side_effect=OSError(28,'PRIVATE INTERNAL PATH')):
            with self.assertRaises(self.policy.ArtworkFailure) as error:self.art.fetch('https://image.invalid/internal-full36')
        self.assertEqual(error.exception.reason,'METADATA_RESERVE_BLOCKED')
        self.m.http.assert_not_called();self.assertFalse(Path(self.art.folder()).exists())

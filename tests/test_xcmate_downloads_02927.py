"""Actual SQLite/files, finite stream responses, verified Range and VFS writes."""
import hashlib,importlib,io,json,os,sqlite3,sys,tempfile,time,types,unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1];LIB=ROOT/'src/plugin.video.xtreammate/resources/lib'
PAYLOAD=b'\0\0\0\x18ftypisom'+bytes(range(256))*4096


class Response:
    def __init__(self,data=PAYLOAD,status=200,headers=None):
        self.raw=io.BytesIO(data);self.status=status;self.headers={'Content-Length':str(len(data)),'Content-Type':'video/mp4','ETag':'"fixture-v1"'};self.closed=False
        if headers:self.headers.update(headers)
    def read(self,n):return self.raw.read(n)
    def close(self):self.closed=True;self.raw.close()


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.target=self.root/'media';self.target.mkdir()
        utils=types.ModuleType('utils');utils.addon_data_dir=lambda:str(self.root);utils.setting_int=lambda key,default=0:default;utils.setting=lambda key,default='':str(self.target) if key=='recordings_folder' else default
        patch=mock.patch.dict(sys.modules,utils=utils);patch.start();self.addCleanup(patch.stop)
        patch=mock.patch.object(sys,'path',[str(LIB)]+sys.path);patch.start();self.addCleanup(patch.stop)
        for name in ('download_store','download_worker','download_sources','media_files','downloads','capture_target','direct_ts'):sys.modules.pop(name,None)
        self.store=importlib.import_module('download_store');self.worker=importlib.import_module('download_worker');self.files=importlib.import_module('media_files');self.api=importlib.import_module('downloads')
        self.media=dict(pid='portal-a',kind='vod',sid='1',title='Test Film',series_id='',season='',episode='',target=str(self.target))
        self.ident=self.store.enqueue(self.media);self.resolve=mock.Mock(return_value=('https://fixture.invalid/film.mp4?token=PRIVATE',{}))
    def run_job(self,response=None):
        opened=mock.Mock(return_value=response or Response());self.assertTrue(self.worker.run_one(resolver=self.resolve,opener=opened));return self.store.get(self.ident),opened
    def paused(self,action='pause'):
        response=Response();read=response.read;calls=[0]
        def chunk(n):
            data=read(n);calls[0]+=1
            if calls[0]==1:self.store.command(self.ident,action)
            return data
        response.read=chunk
        with mock.patch.object(self.worker.time,'monotonic',side_effect=iter(range(10000))):row,opened=self.run_job(response)
        return row
    def runnable(self):
        conn=self.store.db()
        with conn:conn.execute('UPDATE jobs SET next_at=0')
        conn.close()
    def test_complete_movie_is_atomic_persistent_and_identity_has_no_source_secrets(self):
        row,_=self.run_job();self.assertEqual(row['state'],'COMPLETE');self.assertEqual(Path(row['file']).read_bytes(),PAYLOAD)
        self.assertEqual(row['digest'],hashlib.sha256(PAYLOAD).hexdigest());self.assertFalse(Path(row['part']).exists())
        self.assertEqual(importlib.reload(self.store).get(self.ident)['file'],row['file'])
        self.assertEqual(self.api.playable(row),row['file'])
        self.assertNotIn('PRIVATE',json.dumps(row));self.assertFalse('https:' in json.dumps(row))
    def test_duplicate_and_other_portal_titles_never_overwrite(self):
        self.assertEqual(self.store.enqueue(self.media),self.ident);first,_=self.run_job();before=Path(first['file']).read_bytes()
        other=self.store.enqueue(dict(self.media,pid='portal-b'));self.assertNotEqual(other,self.ident)
        self.worker.run_one(resolver=self.resolve,opener=lambda *args:Response());second=self.store.get(other)
        self.assertNotEqual(second['file'],first['file']);self.assertEqual(Path(first['file']).read_bytes(),before)
        self.assertFalse(self.worker.run_one(resolver=self.resolve,opener=lambda *a:Response()))
    def test_episode_has_metadata_identity_and_safe_season_path(self):
        self.store.command(self.ident,'cancel');self.ident=self.store.enqueue(dict(self.media,kind='episode',series_id='series-5',series_title='Serie / Test',season='1',episode='2'))
        row,_=self.run_job();self.assertEqual(row['state'],'COMPLETE');self.assertEqual(Path(row['file']).parent,self.target);self.assertTrue(Path(row['file']).name.startswith('Download - '));self.assertIn('S01E02',row['file'])
        self.assertEqual(row['media']['series_id'],'series-5')
    def test_pause_then_range_resume_validates_etag_and_prefix(self):
        row=self.paused();offset=row['bytes'];self.assertEqual(row['state'],'PAUSED');self.assertGreater(offset,0);self.assertLess(offset,len(PAYLOAD))
        self.assertEqual(row['lease'],0);self.assertTrue(self.store.command(self.ident,'resume'))
        response=Response(PAYLOAD[offset:],206,{'Content-Range':f'bytes {offset}-{len(PAYLOAD)-1}/{len(PAYLOAD)}'})
        finished,opened=self.run_job(response);headers=opened.call_args.args[1]
        self.assertEqual(headers['Range'],f'bytes={offset}-');self.assertEqual(headers['If-Range'],'"fixture-v1"')
        self.assertEqual(finished['state'],'COMPLETE');self.assertEqual(Path(finished['file']).read_bytes(),PAYLOAD)
    def test_ignored_range_restarts_cleanly_instead_of_appending_full_response(self):
        row=self.paused();self.store.command(self.ident,'resume');row,_=self.run_job(Response())
        self.assertEqual(row['state'],'COMPLETE');self.assertEqual(Path(row['file']).read_bytes(),PAYLOAD)
    def test_wrong_range_and_changed_etag_never_publish(self):
        row=self.paused();offset=row['bytes'];before=Path(row['part']).read_bytes();self.store.command(self.ident,'resume')
        row,_=self.run_job(Response(PAYLOAD[offset:],206,{'Content-Range':f'bytes 0-{len(PAYLOAD)-1}/{len(PAYLOAD)}'}))
        self.assertEqual((row['state'],row['code']),('FAILED','BAD_RANGE'));self.assertEqual(Path(row['part']).read_bytes(),before);self.assertFalse(row['file'])
    def test_changed_validator_preserves_existing_partial(self):
        row=self.paused();offset=row['bytes'];before=Path(row['part']).read_bytes();self.store.command(self.ident,'resume')
        row,_=self.run_job(Response(PAYLOAD[offset:],206,{'Content-Range':f'bytes {offset}-{len(PAYLOAD)-1}/{len(PAYLOAD)}','ETag':'"other"'}))
        self.assertEqual(row['code'],'SOURCE_CHANGED');self.assertEqual(Path(row['part']).read_bytes(),before)
    def test_modified_partial_forces_full_restart_without_sending_range(self):
        row=self.paused();Path(row['part']).write_bytes(b'x'*row['bytes']);self.store.command(self.ident,'resume');row,opened=self.run_job()
        self.assertNotIn('Range',opened.call_args.args[1]);self.assertEqual(row['state'],'COMPLETE')
    def test_cancel_keeps_own_part_and_never_exposes_as_playable(self):
        row=self.paused('cancel');self.assertEqual(row['state'],'CANCELLED');self.assertTrue(Path(row['part']).exists())
        with self.assertRaisesRegex(Exception,'NOT_COMPLETE'):self.api.playable(row)
        self.assertEqual(list(self.target.rglob('*.mp4')),[])
    def test_three_transient_attempts_have_backoff_and_stop(self):
        opened=mock.Mock(side_effect=TimeoutError('https://PRIVATE'))
        for _ in range(3):
            self.assertTrue(self.worker.run_one(resolver=self.resolve,opener=opened));self.runnable()
        row=self.store.get(self.ident);self.assertEqual((row['state'],row['attempts'],row['code']),('FAILED',3,'TIMEOUT'))
        self.assertFalse(self.worker.run_one(resolver=self.resolve,opener=opened));self.assertEqual(opened.call_count,3)
    def test_invalid_playlist_html_and_oversize_never_become_completed(self):
        for index,(response,code) in enumerate([(Response(b'<html>error</html>'),'INVALID_MEDIA'),(Response(headers={'Content-Type':'application/vnd.apple.mpegurl'}),'UNSUPPORTED_SOURCE'),(Response(headers={'Content-Length':str(65*1024**3)}),'FILE_LIMIT')]):
            with self.subTest(code=code):
                row,_=self.run_job(response);self.assertEqual(row['state'],'FAILED');self.assertEqual(row['code'],code)
                self.store.command(self.ident,'retry',now=time.time()+120*(index+1))
    def test_missing_length_and_truncation_are_not_false_success(self):
        row,_=self.run_job(Response(headers={'Content-Length':''}));self.assertEqual(row['code'],'LENGTH_REQUIRED')
        self.store.command(self.ident,'retry',now=time.time()+120)
        row,_=self.run_job(Response(PAYLOAD[:65536],headers={'Content-Length':str(len(PAYLOAD))}));self.assertNotEqual(row['state'],'COMPLETE');self.assertEqual(row['bytes'],65536)
    def test_hide_keeps_file_and_explicit_delete_refuses_changed_foreign_bytes(self):
        row,_=self.run_job();self.store.command(self.ident,'hide');self.assertEqual(self.store.snapshot(),[]);self.assertTrue(Path(row['file']).exists())
        Path(row['file']).write_bytes(b'FOREIGN')
        with self.assertRaisesRegex(Exception,'FILE_CHANGED'):self.api.delete(self.ident)
        self.assertEqual(Path(row['file']).read_bytes(),b'FOREIGN')
    def test_explicit_delete_only_removes_verified_owned_file(self):
        foreign=self.target/'foreign.mp4';foreign.write_bytes(b'KEEP');row,_=self.run_job()
        self.assertTrue(self.api.delete(self.ident));self.assertFalse(Path(row['file']).exists());self.assertEqual(foreign.read_bytes(),b'KEEP')
    def test_restart_does_not_blindly_restart_expired_transfer(self):
        job=self.store.claim(now=100);self.assertEqual(job['state'],'RUNNING');self.assertIsNone(self.store.claim(now=131))
        row=self.store.get(self.ident);self.assertEqual((row['state'],row['code']),('PAUSED','INTERRUPTED'))
    def test_second_worker_cannot_claim_while_valid_lease_exists(self):
        self.assertIsNotNone(self.store.claim(now=100));self.assertIsNone(self.store.claim(now=101))
    def test_target_probe_round_trips_rename_and_keeps_foreign_files(self):
        foreign=self.target/'keep.txt';foreign.write_text('KEEP');report=self.files.probe(str(self.target));self.assertTrue(report['writable'])
        self.assertGreater(report['free'],0);self.assertEqual(list(self.target.iterdir()),[foreign])
    def test_sqlite_queue_and_ui_index_do_not_include_provider_urls(self):
        self.assertEqual(len(self.store.snapshot()),1)
        self.assertNotIn('https:',json.dumps(self.store.snapshot()))
        self.assertEqual(os.stat(self.store.path()).st_mode&0o777,0o600)
        raw=Path(self.store.path()).read_bytes();self.assertNotIn(b'PRIVATE',raw)
    def test_redirect_policy_never_forwards_authentication_to_foreign_origin(self):
        from urllib.request import Request
        with self.assertRaisesRegex(Exception,'REDIRECT_UNSUPPORTED'):self.worker.SameOrigin().redirect_request(Request('https://one.invalid/file',headers={'Authorization':'PRIVATE'}),None,302,'',{},'https://two.invalid/file')
    def test_playlist_and_drm_sources_are_explicitly_rejected(self):
        source=importlib.import_module('download_sources')
        for uri in ('file:///etc/passwd','https://a.invalid/a.m3u8','https://a.invalid/a.mpd','https://a.invalid/a|token=SECRET'):
            with self.assertRaises(source.DownloadFailure):source.validate(uri)
        with self.assertRaisesRegex(Exception,'PROTECTED_SOURCE'):source.container(b'\0\0\0\x18ftypisompssh'+b'x'*1024)
    def test_true_http_transfer_streams_movie_and_episode_without_url_in_queue(self):
        from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
        import threading
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                self.send_response(200);self.send_header('Content-Length',str(len(PAYLOAD)));self.send_header('Content-Type','video/mp4');self.send_header('ETag','"real-fixture"');self.end_headers()
                for n in range(0,len(PAYLOAD),8192):self.wfile.write(PAYLOAD[n:n+8192])
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            url=f'http://127.0.0.1:{server.server_port}/sample.mp4'
            self.assertTrue(self.worker.run_one(resolver=lambda media:(url,{})))
            movie=self.store.get(self.ident);self.assertEqual(movie['state'],'COMPLETE')
            episode=self.store.enqueue(dict(self.media,kind='episode',series_id='s',season='2',episode='3',series_title='Fixture'))
            self.assertTrue(self.worker.run_one(resolver=lambda media:(url,{})))
            row=self.store.get(episode);self.assertEqual(row['state'],'COMPLETE');self.assertEqual(Path(row['file']).read_bytes(),PAYLOAD)
            self.assertEqual(Path(movie['file']).read_bytes(),PAYLOAD)
        finally:server.shutdown();server.server_close();thread.join(2)
    def test_nonlocal_destination_is_rejected_before_provider_connection(self):
        self.store.command(self.ident,'cancel')
        self.ident=self.store.enqueue(dict(self.media,sid='2',target='smb://test-only/share/archive'))
        row,opened=self.run_job()
        self.assertEqual((row['state'],row['code'].split('@')[0]),('FAILED','STAGING_CONSENT_REQUIRED'))
        self.resolve.assert_not_called();opened.assert_not_called()
    def test_full_part_is_published_after_interrupted_rename_without_new_http(self):
        with mock.patch.object(self.files,'rename',side_effect=self.files.FileFailure('TARGET_RENAME')):row,_=self.run_job()
        self.assertEqual(row['state'],'FAILED');self.assertEqual(row['bytes'],len(PAYLOAD));self.assertTrue(Path(row['part']).exists())
        self.store.command(self.ident,'retry',now=time.time()+60)
        opener=mock.Mock(side_effect=AssertionError('completed payload must not redownload'))
        self.assertTrue(self.worker.run_one(resolver=self.resolve,opener=opener));self.assertEqual(self.store.get(self.ident)['state'],'COMPLETE');opener.assert_not_called()
    def test_storage_failure_never_removes_preexisting_media(self):
        foreign=self.target/'foreign.mp4';foreign.write_bytes(b'KEEP')
        with mock.patch.object(self.files,'capacity',side_effect=self.files.FileFailure('NO_SPACE')):row,_=self.run_job()
        self.assertEqual((row['state'],row['code']),('FAILED','NO_SPACE'));self.assertEqual(foreign.read_bytes(),b'KEEP')

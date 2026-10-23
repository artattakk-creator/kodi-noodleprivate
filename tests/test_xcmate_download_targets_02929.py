"""Real local and signed SMB2 target fixtures; hardware remains NOT_TESTED."""
import errno,hashlib,importlib,importlib.util,io,json,os,sqlite3,subprocess,sys,threading,time,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

SMB_FIXTURE=importlib.util.find_spec('impacket') is not None

PAYLOAD=b'\0\0\0\x18ftypisom'+b'p'*300000


class TargetsFixture(Fixture):
    def setUp(self):
        super().setUp()
        for name in ('download_targets','download_smb','download_target_ui','download_store','download_worker','downloads','media_files'):sys.modules.pop(name,None)
        self.targets=importlib.import_module('download_targets');self.store=importlib.import_module('download_store')
        self.worker=importlib.import_module('download_worker');self.files=importlib.import_module('media_files')
        sys.modules['xbmcvfs'].translatePath=lambda p:p
        self.dialog.browseSingle=mock.Mock(return_value='')

    def response(self):
        response=io.BytesIO(PAYLOAD);response.status=200
        response.headers={'Content-Length':str(len(PAYLOAD)),'Content-Type':'video/mp4','ETag':'"v1"'}
        return response

    def make_media(self,target,sid='one',kind='vod'):
        return dict(pid='p',sid=sid,kind=kind,title='Fixture',target=target,season='1',episode='2',series_id='s')


class Targets29Tests(TargetsFixture,unittest.TestCase):
    def test_new_target_requires_explicit_activation_and_leaves_recording_setting_unchanged(self):
        self.options.update(recordings_folder=str(self.folder/'recordings'),downloads_folder=str(self.folder/'usb'))
        self.assertEqual(self.targets.configured(),self.options['recordings_folder'])
        self.options['downloads_folder_enabled']='1'
        self.assertEqual(self.targets.configured(),self.options['downloads_folder'])
        self.assertEqual(self.options['recordings_folder'],str(self.folder/'recordings'))

    def test_picker_persists_separate_target_and_cancel_does_not_change_any_setting(self):
        import download_target_ui
        root=self.folder/'usb';root.mkdir();before=dict(self.options)
        self.dialog.browseSingle.return_value=str(root);self.dialog.yesno.return_value=False
        with mock.patch('capture_ui.work',side_effect=lambda fn:fn()):download_target_ui.choose()
        self.assertEqual(self.options,before)
        self.dialog.yesno.return_value=True
        with mock.patch('capture_ui.work',side_effect=lambda fn:fn()):download_target_ui.choose()
        self.assertEqual(self.options['downloads_folder'],str(root));self.assertEqual(self.options['downloads_folder_enabled'],'1')
        self.assertEqual(self.options.get('recordings_folder'),before.get('recordings_folder'))

    def test_usb_staged_backend_uses_exclusive_copy_hash_and_keeps_recovery_stage(self):
        import atomic_media
        root=self.folder/'usb';root.mkdir();before=root/'foreign.mp4';before.write_bytes(b'KEEP')
        original=atomic_media.probe
        def probe(path,create=False):
            if str(path)==str(root):raise atomic_media.StorageFailure('TARGET_SYNC_UNSUPPORTED','FSYNC_DIRECTORY',22)
            return original(path,create)
        with mock.patch.object(atomic_media,'probe',side_effect=probe):
            caps=self.targets.assess(str(root));self.assertEqual(caps['backend'],'LOCAL_STAGE_VERIFY');self.assertFalse(caps['atomic_publish'])
            with self.assertRaisesRegex(Exception,'STAGING_CONSENT_REQUIRED'):self.files.probe(str(root))
            self.targets.approved(str(root),save=True)
            ident=self.store.enqueue(self.make_media(str(root)))
            self.worker.run_one(resolver=lambda m:('https://fixture.invalid/one.mp4',{}),opener=lambda *a:self.response())
        row=self.store.get(ident);self.assertEqual(row['state'],'COMPLETE',row['code'])
        self.assertEqual(Path(row['file']).parent,root);self.assertEqual(Path(row['file']).read_bytes(),PAYLOAD)
        self.assertEqual(Path(row['part']).read_bytes(),PAYLOAD);self.assertEqual(before.read_bytes(),b'KEEP')

    def test_usb_copy_pause_and_retry_reuses_full_local_stage_without_http(self):
        import atomic_media,download_targets
        root=self.folder/'usb';root.mkdir();self.targets.approved(str(root),save=True)
        caps=dict(staging=True,type='LOCAL_USB',backend='LOCAL_STAGE_VERIFY')
        ident=self.store.enqueue(self.make_media(str(root)));original=download_targets.publish;once=[False]
        def publish(*args,**kwargs):
            progress=args[8]
            def pause(count):
                progress(count)
                if count and not once[0]:once[0]=True;self.store.command(ident,'pause')
            args=list(args);args[8]=pause
            return original(*args,**kwargs)
        with mock.patch.object(self.files,'probe',return_value=caps),mock.patch.object(download_targets,'publish',side_effect=publish):
            self.worker.run_one(resolver=lambda m:('https://fixture.invalid/one.mp4',{}),opener=lambda *a:self.response())
        row=self.store.get(ident);self.assertEqual(row['state'],'PAUSED');stage=Path(row['part']);self.assertEqual(stage.read_bytes(),PAYLOAD)
        partial=Path(row['file']);self.assertLess(partial.stat().st_size,len(PAYLOAD))
        self.assertTrue(self.store.command(ident,'resume'))
        with mock.patch.object(self.files,'probe',return_value=caps):
            self.worker.run_one(resolver=mock.Mock(side_effect=AssertionError('must not resolve HTTP again')),opener=mock.Mock(side_effect=AssertionError('must not download again')))
        row=self.store.get(ident);self.assertEqual(row['state'],'COMPLETE',row['code']);self.assertNotEqual(row['file'],str(partial))
        self.assertTrue(partial.exists());self.assertEqual(Path(row['file']).read_bytes(),PAYLOAD)

    def test_android_saf_readonly_and_no_space_never_fall_back_or_contact_provider(self):
        for target in ('content://android/tree/usb','ftp://server/share'):
            with self.assertRaisesRegex(Exception,'TARGET_ANDROID_ACCESS_REQUIRED'):self.targets.normalize(target)
        root=self.folder/'usb';root.mkdir();ident=self.store.enqueue(self.make_media(str(root)))
        resolver=mock.Mock()
        with mock.patch.object(self.files,'probe',side_effect=self.targets.Failure('TARGET_PERMISSION','OPEN_FILE',13)):
            self.worker.run_one(resolver=resolver)
        resolver.assert_not_called();row=self.store.get(ident);self.assertIn('TARGET_PERMISSION',row['code']);self.assertEqual(row['media']['target'],str(root))
        with mock.patch.object(self.files.shutil,'disk_usage',return_value=types.SimpleNamespace(free=0)):
            with self.assertRaisesRegex(Exception,'NO_SPACE'):self.files.capacity(str(root),1)

    def test_smb_paths_credentials_and_protocol_errors_are_not_leaked(self):
        import download_smb as smb
        for uri in ('smb://server/share/../other','smb://server/share/%2e%2e','smb://server/share/%2fescape','smb://server/share/f:ads'):
            with self.assertRaises(smb.Failure):smb.normalized(uri)
        uri=smb.configure('smb://fixture:PRIVATE@server/share/folder')
        self.assertEqual(uri,'smb://server/share/folder');self.assertNotIn('PRIVATE',uri)
        self.assertEqual(smb.credentials(uri)[:2],('fixture','PRIVATE'))
        self.assertNotIn('PRIVATE',str(smb.safe_error(RuntimeError('PRIVATE smb://server/share'),'SMB_IO')))
        self.assertEqual(os.stat(self.folder/'download_smb_credentials.sqlite').st_mode&0o777,0o600)

    def test_fat32_limit_stops_before_creating_media_part(self):
        root=self.folder/'fat32';root.mkdir();ident=self.store.enqueue(self.make_media(str(root)))
        response=self.response();response.headers['Content-Length']=str(5*1024**3)
        with mock.patch.object(self.files,'file_limit',return_value=4*1024**3-1):
            self.worker.run_one(resolver=lambda m:('https://fixture.invalid/large.mp4',{}),opener=lambda *a:response)
        row=self.store.get(ident);self.assertEqual((row['state'],row['code']),('FAILED','FILE_LIMIT'))
        self.assertFalse(list(root.glob('*.part')));self.assertEqual(row['bytes'],0)

    def test_smb1_unsigned_and_bad_signed_response_rejected(self):
        import download_smb as smb
        connection=smb.SignedConnection('fixture','fixture','XCMATE','server',is_direct_tcp=True)
        with self.assertRaisesRegex(Exception,'SMB2_REQUIRED'):connection._updateState_SMB1(object())
        message=types.SimpleNamespace(command=0,status=0,payload=types.SimpleNamespace(dialect_revision=0x202,security_mode=0))
        with self.assertRaisesRegex(Exception,'SMB_SIGNING_REQUIRED'):connection._updateState_SMB2(message)
        connection.has_authenticated=True;connection.is_signing_active=True;connection.signing_session_key=b'key'
        message=types.SimpleNamespace(command=9,status=0,raw_data=b'\0'*80,flags=8,signature=b'\0'*16)
        with self.assertRaisesRegex(Exception,'SMB_BAD_SIGNATURE'):connection._updateState_SMB2(message)

    def test_database_upgrade_preserves_existing_jobs_and_adds_copy_progress_only(self):
        ident=self.store.enqueue(self.make_media(str(self.folder)));before=self.store.get(ident)
        connection=self.store.db()
        with connection:connection.execute('ALTER TABLE jobs DROP COLUMN copy_bytes')
        connection.close()
        after=self.store.get(ident)
        self.assertEqual({k:v for k,v in before.items() if k!='copy_bytes'},{k:v for k,v in after.items() if k!='copy_bytes'})
        self.assertEqual(after['copy_bytes'],0)


@unittest.skipUnless(SMB_FIXTURE,'impacket host fixture dependency unavailable')
class SMB2Wire29Tests(TargetsFixture,unittest.TestCase):
    # Inherit setup/helpers only, not duplicate the local tests in discovery.
    def setUp(self):
        super().setUp();self.share=self.folder/'share';self.share.mkdir()
        helper=Path(__file__).parent/'fixtures/smb29_server.py'
        self.server=subprocess.Popen([sys.executable,str(helper),str(self.share)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
        def cleanup():
            self.server.terminate();self.server.wait(timeout=5);self.server.stdout.close()
        self.addCleanup(cleanup)
        ready=self.server.stdout.readline();self.assertTrue(ready,'SMB fixture failed to start')
        port=json.loads(ready)['port']
        self.uri='smb://127.0.0.1:'+str(port)+'/MEDIA'
        self.smb=importlib.import_module('download_smb');self.smb.credentials(self.uri,('fixture','fixture-password',''))

    def test_real_smb2_film_and_episode_store_hash_no_replace_and_vfs_path(self):
        self.targets.approved(self.uri,save=True);caps=self.targets.probe(self.uri)
        self.assertEqual(caps['backend'],'SMB2_STAGE_VERIFY');self.assertFalse(caps['offline'])
        for kind,sid in [('vod','film'),('episode','episode')]:
            ident=self.store.enqueue(self.make_media(self.uri,sid,kind))
            self.worker.run_one(resolver=lambda m:('https://fixture.invalid/media.mp4',{}),opener=lambda *a:self.response())
            row=self.store.get(ident);self.assertEqual(row['state'],'COMPLETE',row['code'])
            self.assertEqual(self.smb.digest(row['file'],len(PAYLOAD)),hashlib.sha256(PAYLOAD).hexdigest())
            self.assertEqual(importlib.import_module('downloads').playable(row),row['file'])
            self.assertEqual(Path(row['part']).read_bytes(),PAYLOAD)
        foreign=self.uri+'/foreign.mp4';source=self.folder/'foreign-source';source.write_bytes(b'KEEP')
        self.smb.upload_exclusive(str(source),foreign)
        with self.assertRaisesRegex(Exception,'TARGET_EXISTS'):self.smb.upload_exclusive(str(source),foreign)
        self.assertEqual((self.share/'foreign.mp4').read_bytes(),b'KEEP')

    def test_smb_copy_disconnect_keeps_stage_retry_uses_no_http_and_only_verified_complete(self):
        self.targets.approved(self.uri,save=True);caps=self.targets.probe(self.uri)
        ident=self.store.enqueue(self.make_media(self.uri));original=self.smb.upload_exclusive
        def disconnect(source,target,cancel=lambda:False,progress=lambda n:None):
            original(source,target,cancel,progress)
            raise self.smb.Failure('SMB_CONNECTION_FAILED','SMB_WRITE')
        with mock.patch.object(self.files,'probe',return_value=caps),mock.patch.object(self.smb,'upload_exclusive',side_effect=disconnect):
            self.worker.run_one(resolver=lambda m:('https://fixture.invalid/file.mp4',{}),opener=lambda *a:self.response())
        row=self.store.get(ident);self.assertEqual(row['state'],'FAILED');self.assertEqual(Path(row['part']).read_bytes(),PAYLOAD)
        self.assertFalse(self.files.exists(row['file']))
        self.assertTrue(self.store.command(ident,'retry',now=time.time()+60))
        with mock.patch.object(self.files,'probe',return_value=caps):
            self.worker.run_one(resolver=mock.Mock(side_effect=AssertionError('no second HTTP resolution')),opener=mock.Mock(side_effect=AssertionError('no second HTTP download')))
        row=self.store.get(ident);self.assertEqual(row['state'],'COMPLETE',row['code'])
        self.assertEqual(self.smb.digest(row['file'],len(PAYLOAD)),hashlib.sha256(PAYLOAD).hexdigest())

    def test_actual_smb_server_disconnect_and_restart_never_reports_partial_complete(self):
        self.targets.approved(self.uri,save=True);caps=self.targets.probe(self.uri)
        ident=self.store.enqueue(self.make_media(self.uri));original=self.smb.upload_exclusive;stopped=[False]
        def upload(source,target,cancel=lambda:False,progress=lambda n:None):
            def drop(count):
                progress(count)
                if count and not stopped[0]:
                    stopped[0]=True;self.server.terminate();self.server.wait(timeout=5)
            return original(source,target,cancel,drop)
        with mock.patch.object(self.files,'probe',return_value=caps),mock.patch.object(self.smb,'upload_exclusive',side_effect=upload):
            self.worker.run_one(resolver=lambda m:('https://fixture.invalid/file.mp4',{}),opener=lambda *a:self.response())
        row=self.store.get(ident);self.assertTrue(stopped[0]);self.assertEqual(row['state'],'FAILED')
        self.assertEqual(Path(row['part']).read_bytes(),PAYLOAD)
        old=self.server;port=self.smb.parse(self.uri)[2];old.stdout.close()
        helper=Path(__file__).parent/'fixtures/smb29_server.py'
        self.server=subprocess.Popen([sys.executable,str(helper),str(self.share),str(port)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
        self.assertTrue(self.server.stdout.readline(),'SMB fixture restart failed')
        self.assertTrue(self.store.command(ident,'retry',now=time.time()+60))
        with mock.patch.object(self.files,'probe',return_value=caps):
            self.worker.run_one(resolver=mock.Mock(side_effect=AssertionError('local stage must survive disconnect')),opener=mock.Mock(side_effect=AssertionError('no HTTP restart')))
        row=self.store.get(ident);self.assertEqual(row['state'],'COMPLETE',row['code'])
        self.assertEqual(self.smb.digest(row['file'],len(PAYLOAD)),hashlib.sha256(PAYLOAD).hexdigest())

    def test_real_smb_corrupted_network_copy_is_not_published_or_complete(self):
        self.targets.approved(self.uri,save=True);caps=self.targets.probe(self.uri)
        ident=self.store.enqueue(self.make_media(self.uri));original=self.smb.upload_exclusive
        def corrupt(source,target,cancel=lambda:False,progress=lambda n:None):
            result=original(source,target,cancel,progress)
            path=self.share/self.smb.parse(target)[4]
            with path.open('r+b') as stream:stream.write(b'CORRUPTED')
            return result
        with mock.patch.object(self.files,'probe',return_value=caps),mock.patch.object(self.smb,'upload_exclusive',side_effect=corrupt):
            self.worker.run_one(resolver=lambda m:('https://fixture.invalid/file.mp4',{}),opener=lambda *a:self.response())
        row=self.store.get(ident);self.assertEqual(row['state'],'FAILED');self.assertIn('TARGET_VERIFY_FAILED',row['code'])
        self.assertFalse(self.smb.exists(row['file']));self.assertEqual(Path(row['part']).read_bytes(),PAYLOAD)

    def test_real_smb_no_replace_rename_and_parallel_exclusive_create(self):
        source=self.folder/'payload';source.write_bytes(PAYLOAD)
        self.smb.upload_exclusive(str(source),self.uri+'/one.part');self.smb.upload_exclusive(str(source),self.uri+'/two.mp4')
        with self.assertRaisesRegex(Exception,'TARGET_EXISTS'):self.smb.rename(self.uri+'/one.part',self.uri+'/two.mp4')
        self.assertEqual((self.share/'one.part').read_bytes(),PAYLOAD);self.assertEqual((self.share/'two.mp4').read_bytes(),PAYLOAD)
        results=[]
        def create():
            try:self.smb.upload_exclusive(str(source),self.uri+'/race.mp4');results.append('OK')
            except self.smb.Failure as exc:results.append(exc.code)
        threads=[threading.Thread(target=create) for _ in range(5)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(15);self.assertFalse(thread.is_alive())
        self.assertEqual(results.count('OK'),1);self.assertEqual(results.count('TARGET_EXISTS'),4)
        self.assertEqual((self.share/'race.mp4').read_bytes(),PAYLOAD)


if __name__=='__main__':unittest.main()

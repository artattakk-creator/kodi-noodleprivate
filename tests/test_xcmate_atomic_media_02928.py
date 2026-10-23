"""Real native no-replace publication, fallback, collisions and crash safety."""
import concurrent.futures,importlib,io,os,stat,sys,tempfile,types,unittest
from pathlib import Path
from unittest import mock

LIB=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'


class Atomic28Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.folder=Path(temp.name)
        patch=mock.patch.object(sys,'path',[str(LIB)]+sys.path);patch.start();self.addCleanup(patch.stop)
        self.api=importlib.import_module('atomic_media')
        self.fd=os.open(self.folder,os.O_RDONLY|os.O_DIRECTORY);self.addCleanup(os.close,self.fd)

    def test_native_rename_works_without_any_hardlink_and_cleans_owned_probe(self):
        keep=self.folder/'keep';keep.write_bytes(b'KEEP')
        with mock.patch.object(self.api.os,'link',side_effect=OSError(95,'not supported')) as link:
            report=self.api.probe(str(self.folder))
        self.assertEqual(report['publish'],'RENAME_NOREPLACE');link.assert_not_called()
        self.assertEqual(list(self.folder.iterdir()),[keep]);self.assertEqual(keep.read_bytes(),b'KEEP')

    def test_hardlink_fallback_requires_exclusive_destination_and_keeps_no_scratch(self):
        with mock.patch.object(self.api,'_rename_noreplace',side_effect=OSError(38,'unavailable')):
            report=self.api.probe(str(self.folder))
        self.assertEqual(report['publish'],'HARDLINK');self.assertEqual(list(self.folder.iterdir()),[])

    def test_both_unsupported_fail_closed_without_plain_rename_or_replace(self):
        (self.folder/'own.part').write_bytes(b'PART')
        with mock.patch.object(self.api,'_rename_noreplace',side_effect=OSError(38,'unavailable')),\
             mock.patch.object(self.api.os,'link',side_effect=OSError(95,'unavailable')),\
             mock.patch.object(self.api.os,'rename') as rename,mock.patch.object(self.api.os,'replace') as replace:
            with self.assertRaises(self.api.StorageFailure) as raised:self.api.publish(self.fd,'own.part','final')
        self.assertEqual((raised.exception.code,raised.exception.step,raised.exception.number),('TARGET_ATOMIC_PUBLISH_UNAVAILABLE','LINK',95))
        rename.assert_not_called();replace.assert_not_called();self.assertEqual((self.folder/'own.part').read_bytes(),b'PART')
        self.assertFalse((self.folder/'final').exists())

    def test_existing_file_and_symlink_destination_are_never_overwritten(self):
        for destination in ('final','link'):
            (self.folder/'own.part').write_bytes(b'NEW');(self.folder/'final').write_bytes(b'KEEP')
            if destination=='link':(self.folder/'link').symlink_to(self.folder/'final')
            with self.assertRaises(self.api.StorageFailure) as raised:self.api.publish(self.fd,'own.part',destination)
            self.assertEqual(raised.exception.code,'TARGET_EXISTS')
            self.assertEqual((self.folder/'final').read_bytes(),b'KEEP');self.assertEqual((self.folder/'own.part').read_bytes(),b'NEW')

    def test_concurrent_publish_has_one_winner_and_losers_keep_their_parts(self):
        for number in range(12):(self.folder/('p'+str(number))).write_bytes(bytes([number]))
        def publish(number):
            try:self.api.publish(self.fd,'p'+str(number),'final');return number
            except self.api.StorageFailure as exc:self.assertEqual(exc.code,'TARGET_EXISTS');return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:results=list(pool.map(publish,range(12)))
        winners=[n for n in results if n is not None];self.assertEqual(len(winners),1)
        self.assertEqual((self.folder/'final').read_bytes(),bytes(winners))
        for number in range(12):self.assertEqual((self.folder/('p'+str(number))).exists(),number!=winners[0])

    def test_symlink_source_and_unsafe_names_fail_without_touching_foreign_data(self):
        (self.folder/'keep').write_bytes(b'KEEP');(self.folder/'alias').symlink_to(self.folder/'keep')
        for source in ('alias','../keep','/absolute',''):
            with self.assertRaises(self.api.StorageFailure):self.api.publish(self.fd,source,'final')
        self.assertEqual((self.folder/'keep').read_bytes(),b'KEEP');self.assertFalse((self.folder/'final').exists())

    def test_directory_sync_is_still_mandatory_before_publication(self):
        (self.folder/'own.part').write_bytes(b'PART');original=self.api.os.fsync
        def sync(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):raise OSError(22,'directory sync unavailable')
            return original(fd)
        with mock.patch.object(self.api.os,'fsync',side_effect=sync),mock.patch.object(self.api,'_rename_noreplace') as rename:
            with self.assertRaises(self.api.StorageFailure) as raised:self.api.publish(self.fd,'own.part','final')
        self.assertEqual((raised.exception.code,raised.exception.step),('TARGET_SYNC_UNSUPPORTED','FSYNC_DIRECTORY'))
        rename.assert_not_called();self.assertTrue((self.folder/'own.part').exists())

    def ts_stream(self,recorder_module):
        import test_xcmate_capture_02926 as helpers
        builder=helpers.CaptureTests();builder.ts=recorder_module
        return builder.stream()*200

    def test_recorder_finishes_without_hardlinks_and_never_reports_recording_at_zero_bytes(self):
        ts=importlib.import_module('direct_ts');recorder=ts.Recorder('https://test.invalid/live.ts',str(self.folder),120,separate_connection=True)
        response=io.BytesIO(self.ts_stream(ts));response.status=200;response.headers={'Content-Type':'video/mp2t'}
        read=response.read;calls=[0];snapshots=[];save=recorder._save
        def consume(n):
            calls[0]+=1
            if calls[0]==2:recorder.finish()
            return read(n)
        def record(fd):snapshots.append(dict(recorder.state));return save(fd)
        response.read=consume
        with mock.patch.object(ts,'build_opener',return_value=types.SimpleNamespace(open=lambda *a,**kw:response)),\
             mock.patch.object(self.api.os,'link',side_effect=OSError(95,'unavailable')),mock.patch.object(recorder,'_save',side_effect=record):
            result=recorder.run()
        self.assertEqual(result['status'],'complete',result);self.assertGreater(result['bytes'],0)
        self.assertTrue((self.folder/result['file']).is_file())
        self.assertTrue(all(s['bytes']>0 for s in snapshots if s['status']=='recording'))
        self.assertTrue(any(s['status']=='recording' for s in snapshots))

    def test_hls_and_dash_are_source_failures_even_when_target_supports_downloads(self):
        ts=importlib.import_module('direct_ts')
        for mime,raw,step in [('application/vnd.apple.mpegurl',b'#EXTM3U\n','SOURCE_HLS'),('application/dash+xml',b'<MPD></MPD>','SOURCE_DASH'),('application/octet-stream',b'#EXTM3U\n'+'x'.encode()*500,'SOURCE_HLS')]:
            recorder=ts.Recorder('https://test.invalid/live',str(self.folder),120,separate_connection=True)
            response=io.BytesIO(raw);response.status=200;response.headers={'Content-Type':mime};read=response.read
            response.read=lambda n:read(min(n,3))
            with mock.patch.object(ts,'build_opener',return_value=types.SimpleNamespace(open=lambda *a,**kw:response)):
                result=recorder.run()
            self.assertEqual((result['status'],result['bytes'],result['code'],result['step']),('failed',0,'UNSUPPORTED_MANIFEST',step))
            self.assertIn(self.api.probe(str(self.folder))['publish'],('RENAME_NOREPLACE','HARDLINK'))


if __name__=='__main__':unittest.main()

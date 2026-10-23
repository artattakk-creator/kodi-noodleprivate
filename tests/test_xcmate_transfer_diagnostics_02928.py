"""Storage/format diagnostics are distinct and direct downloads stay independent."""
import importlib,io,sys,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture


class Diagnostics28Tests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('capture_ui','capture_target','download_store','download_worker','downloads_ui','transfer_diagnostics'):
            sys.modules.pop(name,None)
        self.diag=importlib.import_module('transfer_diagnostics')

    def test_target_syscall_errno_and_source_kind_are_preserved_and_described_separately(self):
        from atomic_media import StorageFailure
        storage=self.diag.encode(StorageFailure('TARGET_SYNC_UNSUPPORTED','FSYNC_DIRECTORY',22))
        source=self.diag.encode(dict(code='UNSUPPORTED_MANIFEST',step='SOURCE_HLS',errno=0))
        self.assertEqual(storage,'TARGET_SYNC_UNSUPPORTED@FSYNC_DIRECTORY:22')
        self.assertIn('Speicherziel',self.diag.describe(storage));self.assertNotIn('Speicherziel',self.diag.describe(source))
        self.assertIn('MPEG-TS',self.diag.describe(source));self.assertIn('SOURCE_HLS',self.diag.describe(source))

    def test_raw_exception_and_private_fields_never_enter_ui_or_public_trace(self):
        value=RuntimeError('https://private.invalid/USER/SECRET')
        rendered=self.diag.describe(value)
        self.assertNotIn('SECRET',rendered);self.assertNotIn('private.invalid',rendered)
        with mock.patch.object(sys.modules['xbmc'],'log',create=True) as log,mock.patch.object(sys.modules['xbmc'],'LOGINFO',1,create=True):
            self.diag.mark('CAPTURE','FAILED',dict(code='NOT_DIRECT_TS',step='SOURCE_READ',errno=0,url='https://private.invalid/SECRET'))
        self.assertNotIn('SECRET',str(log.call_args_list));self.assertIn('NOT_DIRECT_TS',str(log.call_args_list))

    def test_failed_recording_row_displays_technical_reason_instead_of_silent_selection(self):
        store=importlib.import_module('capture_store');ui=importlib.import_module('capture_ui')
        ident=store.add(self.portal,dict(sid='1'),str(self.folder),120)
        store.update(ident,status='failed',code='UNSUPPORTED_MANIFEST@SOURCE_DASH:0')
        self.dialog.select.return_value=0
        with mock.patch.object(ui,'work',side_effect=lambda fn:fn()):ui.manage()
        self.assertIn('SOURCE_DASH',self.dialog.ok.call_args.args[1]);self.assertNotIn('Speicherziel',self.dialog.ok.call_args.args[1])

    def test_sub_megabyte_recordings_show_real_bytes_and_translated_state(self):
        store=importlib.import_module('capture_store');ui=importlib.import_module('capture_ui')
        ident=store.add(self.portal,dict(sid='1'),str(self.folder),120)
        store.update(ident,status='recording',bytes=32768);self.dialog.select.return_value=-1
        with mock.patch.object(ui,'work',side_effect=lambda fn:fn()):ui.manage()
        label=self.dialog.select.call_args.args[1][0]
        self.assertIn('32768 Bytes',label);self.assertIn('Aufnahme läuft',label)

    def test_direct_movie_download_succeeds_even_when_recorder_format_gate_rejects_hls(self):
        import direct_ts,atomic_media
        store=importlib.import_module('download_store');worker=importlib.import_module('download_worker')
        target=self.folder/'shared';target.mkdir()
        recorder=direct_ts.Recorder('https://test.invalid/live.m3u8',str(target),120,separate_connection=True)
        self.assertEqual(recorder.run()['code'],'UNSUPPORTED_MANIFEST')
        payload=b'\0\0\0\x18ftypisom'+b'x'*8192
        ident=store.enqueue(dict(pid='p',kind='vod',sid='1',title='Movie',target=str(target)))
        response=io.BytesIO(payload);response.status=200;response.headers={'Content-Length':str(len(payload)),'Content-Type':'video/mp4'}
        with mock.patch('capture_target.probe',side_effect=AssertionError('download must not use recording format gate')),\
             mock.patch.object(atomic_media.os,'link',side_effect=OSError(95,'unsupported')):
            self.assertTrue(worker.run_one(resolver=lambda m:('https://test.invalid/movie.mp4',{}),opener=lambda *a:response))
        row=store.get(ident);self.assertEqual(row['state'],'COMPLETE',row['code'])
        self.assertEqual(Path(row['file']).read_bytes(),payload);self.assertEqual(Path(row['file']).parent,target)
        self.assertTrue(Path(row['file']).name.startswith('Download - '))

    def test_download_enqueue_error_reaches_specific_owner_ui(self):
        import downloads_ui,downloads
        w=self.media_window();w._details(w.rows[0]);self.settle(w);self.dialog.yesno.return_value=True
        from atomic_media import StorageFailure
        with mock.patch.object(downloads,'enqueue',side_effect=StorageFailure('TARGET_PERMISSION','OPEN_FILE',13)):
            downloads_ui.request(w);self.settle(w)
        text=self.dialog.ok.call_args.args[1]
        self.assertIn('TARGET_PERMISSION@OPEN_FILE:13',text)
        self.assertEqual(w.mode,'detail');self.assertFalse(self.builtins)


if __name__=='__main__':unittest.main()

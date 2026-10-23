"""Manual capture persistence, safe PES finalization, no player dependency."""
import importlib
import io
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture


class CaptureTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('direct_ts','capture_target','capture_store','capture_service','capture_ui'):sys.modules.pop(name,None)
        self.ts=importlib.import_module('direct_ts');self.store=importlib.import_module('capture_store')

    def packet(self,pid,payload=b'',start=False):
        return bytes([71,(64 if start else 0)|(pid>>8),pid&255,16])+payload.ljust(184,b'\xff')

    def stream(self):
        def section(p):return p+self.ts.crc(p).to_bytes(4,'big')
        pat=section(bytes.fromhex('00b00d0001c100000001e100'))
        pmt=section(bytes.fromhex('02b0120001c10000e101f0001be101f000'))
        return self.packet(0,b'\0'+pat,True)+self.packet(256,b'\0'+pmt,True)+b''.join(self.packet(257,b'\0\0\1\xe0'+bytes([i]),True) for i in range(30))

    def test_pes_trim_is_per_pid_and_never_truncates_other_interleaved_track(self):
        root=self.folder/'capture';root.mkdir()
        packets=[self.packet(257,b'A',True),self.packet(258,b'B',True),self.packet(257,b'C'),self.packet(258,b'D',True),self.packet(257,b'E',True),self.packet(258,b'F')]
        part=root/'own.ts.part';part.write_bytes(b''.join(packets));fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
        try:size=self.ts.finalize(fd,part.name,'own.ts',{257,258})
        finally:os.close(fd)
        self.assertEqual((root/'own.ts').read_bytes(),b''.join(packets[:3]));self.assertEqual(size,3*188)
        self.assertEqual(part.read_bytes(),b''.join(packets))

    def test_finalization_never_overwrites_and_keeps_partial_on_failure(self):
        root=self.folder/'capture';root.mkdir();raw=self.stream()
        (root/'own.part').write_bytes(raw);(root/'final.ts').write_bytes(b'KEEP')
        fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
        try:
            with self.assertRaisesRegex(OSError,'TARGET_EXISTS'):self.ts.finalize(fd,'own.part','final.ts',{257})
        finally:os.close(fd)
        self.assertEqual((root/'final.ts').read_bytes(),b'KEEP');self.assertEqual((root/'own.part').read_bytes(),raw)

    def test_manual_finish_produces_playable_target_while_abort_stays_partial(self):
        for finishing in (True,False):
            root=self.folder/str(finishing);root.mkdir()
            recorder=self.ts.Recorder('https://private.invalid/TOKEN',str(root),120,separate_connection=True)
            raw=self.stream()*200;response=io.BytesIO(raw);response.status=200;response.headers={'Content-Type':'video/mp2t'};read=response.read
            calls=[0]
            def consume(n):
                calls[0]+=1
                if calls[0]==2:(recorder.finish if finishing else recorder.stop)()
                return read(n)
            response.read=consume
            with mock.patch.object(self.ts,'build_opener',return_value=types.SimpleNamespace(open=lambda *a,**kw:response)):
                result=recorder.run()
            self.assertEqual(result['status'],'complete' if finishing else 'partial',result)
            self.assertEqual(bool(list(root.glob('*.ts'))),finishing)

    def test_enqueue_is_single_job_private_and_stop_is_id_specific(self):
        target=str(self.folder/'captures')
        ident=self.store.add(self.portal,{'sid':'1','name':'Channel'},target,120)
        with self.assertRaises(ValueError):self.store.add(self.portal,{'sid':'2'},target,120)
        self.store.finish('unknown');self.assertEqual(self.store.rows()[0]['stop'],0)
        self.store.finish(ident);self.assertEqual(self.store.rows()[0]['stop'],1)
        data=Path(self.store.path()).read_bytes()
        self.assertNotIn(b'SECRET',data);self.assertNotIn(b'provider.invalid',data)
        self.assertEqual(os.stat(self.store.path()).st_mode&0o777,0o600)

    def test_interrupted_recording_is_partial_without_deleting_artifacts(self):
        ident=self.store.add(self.portal,{'sid':'1'},str(self.folder/'captures'),120)
        self.store.update(ident,status='recording');artifact=self.folder/'saved.ts.part';artifact.write_bytes(b'KEEP')
        self.store.interrupted();row=self.store.rows()[0]
        self.assertEqual((row['status'],row['code']),('partial','SERVICE_INTERRUPTED'));self.assertEqual(artifact.read_bytes(),b'KEEP')

    def test_service_is_lazy_and_cannot_spawn_without_manual_request_database(self):
        service=importlib.import_module('capture_service')
        with mock.patch.object(service.threading,'Thread') as thread:service.poll()
        thread.assert_not_called()

    def test_ui_cancel_and_connection_refusal_never_enqueue(self):
        ui=importlib.import_module('capture_ui')
        with mock.patch.object(ui,'work',side_effect=lambda fn:fn()),mock.patch.object(self.store,'add') as add:
            self.dialog.input.return_value='';ui.start(self.portal);add.assert_not_called()
            self.dialog.input.return_value='Channel';self.dialog.select.side_effect=[0,0];self.dialog.yesno.return_value=False
            ui.start(self.portal);add.assert_not_called()

    def test_service_records_real_http_and_manual_finish_never_touches_player(self):
        from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
        service=importlib.import_module('capture_service');raw=self.stream()*7
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                self.send_response(200);self.send_header('Content-Type','video/mp2t');self.end_headers()
                try:
                    for _ in range(150):self.wfile.write(raw);self.wfile.flush();time.sleep(.02)
                except (BrokenPipeError,ConnectionResetError):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True
        server_thread=threading.Thread(target=server.serve_forever,daemon=True);server_thread.start()
        aborted=threading.Event()
        monitor=types.SimpleNamespace(abortRequested=aborted.is_set,waitForAbort=lambda n:aborted.wait(min(n,.02)))
        ident=self.store.add(self.portal,{'sid':'1'},str(self.folder/'capture'),120)
        with mock.patch.object(service,'resolve',return_value='http://127.0.0.1:'+str(server.server_port)+'/live.ts') as resolve,\
             mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=monitor),\
             mock.patch.object(sys.modules['xbmc'],'Player') as player:
            worker=threading.Thread(target=service._run);worker.start()
            try:
                deadline=time.monotonic()+5
                while self.store.rows()[0]['status']!='recording' and time.monotonic()<deadline:time.sleep(.02)
                self.assertEqual(self.store.rows()[0]['status'],'recording')
                self.store.finish(ident)
                while self.store.rows()[0]['status']!='complete' and time.monotonic()<deadline:time.sleep(.02)
                row=self.store.rows()[0];self.assertEqual(row['status'],'complete',row)
                self.assertTrue((Path(row['target'])/row['file']).is_file())
                player.assert_not_called();resolve.assert_called_once()
            finally:aborted.set();worker.join(3);server.shutdown();server.server_close();server_thread.join(2)
        self.assertFalse(worker.is_alive())

    def test_recording_management_never_plays_partial_or_foreign_basename(self):
        ui=importlib.import_module('capture_ui')
        ident=self.store.add(self.portal,{'sid':'1'},str(self.folder),120)
        self.dialog.select.return_value=0;self.dialog.yesno.return_value=True
        with mock.patch.object(ui,'work',side_effect=lambda fn:fn()),mock.patch.object(sys.modules['xbmc'],'Player') as player:
            self.store.update(ident,status='partial',file=ident+'.ts')
            ui.manage();player.assert_not_called()
            self.store.update(ident,status='complete',file='../foreign.ts')
            ui.manage();player.assert_not_called()

    def test_target_without_atomic_publication_is_rejected_before_opening_provider(self):
        recorder=self.ts.Recorder('https://private.invalid/TOKEN',str(self.folder),120,separate_connection=True)
        with mock.patch('atomic_media._rename_noreplace',side_effect=OSError(95,'unsupported')),mock.patch.object(self.ts.os,'link',side_effect=OSError(95,'unsupported')),mock.patch.object(self.ts,'build_opener') as provider:
            state=recorder.run()
        self.assertEqual((state['status'],state['code']),('failed','TARGET_ATOMIC_PUBLISH_UNAVAILABLE'))
        provider.assert_not_called();self.assertFalse(list(self.folder.glob('*.probe*')))

    def test_stop_while_resolving_source_cannot_start_a_late_recorder(self):
        service=importlib.import_module('capture_service')
        ident=self.store.add(self.portal,{'sid':'1'},str(self.folder/'captures'),120)
        monitor=types.SimpleNamespace(abortRequested=lambda:False,waitForAbort=lambda n:True)
        def resolve(job):self.store.finish(ident);return 'https://private.invalid/SECRET'
        with mock.patch.object(service,'resolve',side_effect=resolve),mock.patch.object(service.xbmc,'Monitor',return_value=monitor),mock.patch.object(self.ts,'Recorder') as recorder:
            service._run()
        recorder.assert_not_called()
        self.assertEqual((self.store.rows()[0]['status'],self.store.rows()[0]['code']),('failed','CANCELLED'))


if __name__=='__main__':unittest.main()

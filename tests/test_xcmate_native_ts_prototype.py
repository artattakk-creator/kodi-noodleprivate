"""Separate prototype only: synthetic PSI, timed worker and real local HTTP."""
from contextlib import contextmanager
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import types
import unittest
from unittest import mock

SOURCE=Path(__file__).resolve().parents[1]/'experiments/native_ts/recorder.py'
spec=importlib.util.spec_from_file_location('xcmate_direct_ts_prototype',SOURCE)
ts=importlib.util.module_from_spec(spec);spec.loader.exec_module(ts)


def section(payload):return payload+ts.crc(payload).to_bytes(4,'big')


def packet(pid,payload=b'',start=False,flags=0):
    return bytes([0x47,(0x40 if start else 0)|((pid>>8)&31),pid&255,0x10|flags])+payload.ljust(184,b'\xff')


def sample(encrypted=False):
    pat=section(bytes.fromhex('00b00d0001c100000001e100'))
    desc=bytes.fromhex('090400010100') if encrypted else b''
    pmt=section(bytes([2,0xb0,18+len(desc),0,1,0xc1,0,0,0xe1,1,0xf0,len(desc)])+desc+bytes.fromhex('1be101f000'))
    return packet(0,b'\0'+pat,True)+packet(256,b'\0'+pmt,True)+packet(257,b'\0\0\1\xe0')*198


class FormatTests(unittest.TestCase):
    def test_real_crc_pat_pmt_and_fragmented_packet_boundaries(self):
        raw=sample();probe=ts.Transport();written=b''
        for start in range(0,len(raw),137):written+=probe.feed(raw[start:start+137])
        self.assertTrue(probe.ready);self.assertEqual(probe.packets,200)
        self.assertEqual(written,raw);self.assertEqual(probe.tail,b'')

    def test_no_false_acceptance_of_sync_only_garbage_html_or_manifest(self):
        for raw in (b'<html>bad</html>'*100,b'#EXTM3U\n'*100,b'\x47'+b'\0'*187):
            with self.subTest(raw=raw[:6]),self.assertRaises(ts.Failure):ts.Transport().feed(raw)
        probe=ts.Transport();probe.feed(packet(8191)*30);self.assertFalse(probe.ready)

    def test_scrambling_and_conditional_access_are_rejected(self):
        for raw in (packet(257,flags=0x80),sample(encrypted=True)):
            with self.assertRaises(ts.Failure) as error:ts.Transport().feed(raw)
            self.assertEqual(error.exception.code,'ENCRYPTED_TS')

    def test_bad_crc_and_adaptation_length_are_rejected(self):
        raw=bytearray(sample());raw[14]^=1
        with self.assertRaises(ts.Failure) as error:ts.Transport().feed(raw)
        self.assertEqual(error.exception.code,'INVALID_PSI_CRC')
        with self.assertRaises(ts.Failure):ts.Transport().feed(bytes([0x47,0,16,0x30,184])+b'\0'*183)

    def test_http_only_no_userinfo_manifest_or_redirect_downgrade(self):
        for url in ('file:///tmp/x.ts','https://u:SECRET@private/x.ts','https://private/x.m3u8','https://private/x.mpd','https://private:bad/x','https://private/x\nTOKEN'):
            with self.subTest(url=url),self.assertRaises(ts.Failure):ts.validate_url(url)
        req=ts.Request('https://example.invalid/a.ts')
        with self.assertRaises(ts.Failure):ts.Redirects().redirect_request(req,None,302,'',{},'http://other.invalid/x')


class WorkerTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)

    def recorder(self,**kw):
        args=dict(source='https://private.invalid/SECRET.ts?token=TOKEN',directory=str(self.root),duration=.5,separate_connection=True)
        args.update(kw);return ts.Recorder(**args)

    def response(self,data=None,content='video/mp2t'):
        response=io.BytesIO(sample() if data is None else data)
        response.headers={'Content-Type':content};response.status=200
        return response

    def test_connection_confirmation_and_unsupported_target_make_no_request(self):
        for args,code in ((dict(separate_connection=False),'CONNECTION_CONFIRMATION_REQUIRED'),(dict(directory='smb://private/share'),'UNSUPPORTED_TARGET'),(dict(duration=float('nan')),'INVALID_DURATION')):
            with mock.patch.object(ts,'build_opener') as opener:state=self.recorder(**args).run()
            self.assertEqual(state['status'],'failed');self.assertEqual(state['code'],code);opener.assert_not_called()

    def test_early_eof_is_partial_not_complete_and_does_not_leak_source(self):
        recorder=self.recorder(duration=60)
        with mock.patch.object(ts,'build_opener',return_value=types.SimpleNamespace(open=lambda *a,**k:self.response())):
            state=recorder.run()
        self.assertEqual(state['status'],'partial');self.assertEqual(state['code'],'SOURCE_EOF')
        self.assertEqual(list(self.root.glob('*.ts')),[]);self.assertTrue(list(self.root.glob('*.part')))
        text=(self.root/(recorder.ident+'.json')).read_text()
        self.assertNotIn('SECRET',text);self.assertNotIn('TOKEN',text);self.assertNotIn('private.invalid',text)

    def test_timed_valid_recording_finalizes_only_complete_packets_and_keeps_foreign_files(self):
        foreign=self.root/'existing.ts';foreign.write_bytes(b'KEEP')
        recorder=self.recorder()
        clock=iter([0,0,0,0,1,1])
        with mock.patch.object(ts.time,'monotonic',side_effect=lambda:next(clock,2)),mock.patch.object(ts,'build_opener',return_value=types.SimpleNamespace(open=lambda *a,**k:self.response())):
            state=recorder.run()
        self.assertEqual(state['status'],'complete',state)
        data=(self.root/state['file']).read_bytes();self.assertEqual(data,sample());self.assertEqual(len(data)%188,0)
        self.assertFalse(list(self.root.glob('*.part')));self.assertEqual(foreign.read_bytes(),b'KEEP')
        self.assertEqual(json.loads((self.root/(recorder.ident+'.json')).read_text())['status'],'complete')
        with self.assertRaises(ts.Failure):recorder.run()

    def test_cancel_during_read_retains_partial_and_never_creates_final(self):
        recorder=self.recorder(duration=60);response=self.response(sample()*2);read=response.read
        def read_cancel(size):
            value=read(size)
            if response.tell()>188*200:recorder.stop()
            return value
        response.read=read_cancel
        with mock.patch.object(ts,'build_opener',return_value=types.SimpleNamespace(open=lambda *a,**k:response)):
            state=recorder.run()
        self.assertEqual((state['status'],state['code']),('partial','CANCELLED'))
        self.assertFalse(list(self.root.glob('*.ts')))

    def test_disk_limit_and_fake_ts_never_complete(self):
        for data,limit,code in ((sample(),188*20,'FILE_LIMIT'),(b'HTML'*10000,188*2000,'NOT_DIRECT_TS')):
            with mock.patch.object(ts,'build_opener',return_value=types.SimpleNamespace(open=lambda *a,**k:self.response(data))):
                state=self.recorder(max_bytes=limit).run()
            self.assertEqual(state['code'],code);self.assertNotEqual(state['status'],'complete')
        self.assertFalse(list(self.root.glob('*.ts')))

    def test_real_local_http_and_non_ts_content(self):
        from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
        raw=sample()
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                self.send_response(200);self.send_header('Content-Type','video/mp2t' if self.path=='/ts' else 'text/html');self.end_headers();self.wfile.write(raw)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            for suffix,expected in (('/ts','SOURCE_EOF'),('/html','NOT_DIRECT_TS')):
                state=self.recorder(source='http://127.0.0.1:'+str(server.server_port)+suffix,duration=60).run()
                self.assertEqual(state['code'],expected)
        finally:server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()

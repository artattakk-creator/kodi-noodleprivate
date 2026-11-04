"""Trusted TLS + real gzip transport, failure privacy, source and mapping readback."""
import gzip,importlib,importlib.util,json,ssl,subprocess,sys,threading,time,unittest,urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from unittest import mock
from xcmate027_fixture import Fixture,LIB

class FeedProbe73(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.epg=importlib.import_module('international_epg73')
        spec=importlib.util.spec_from_file_location('epg_sources',LIB/'epg_sources.py')
        source_module=importlib.util.module_from_spec(spec);sys.modules['epg_sources']=source_module;spec.loader.exec_module(source_module)
        spec=importlib.util.spec_from_file_location('epg_status',LIB/'epg_status.py')
        status_module=importlib.util.module_from_spec(spec);sys.modules['epg_status']=status_module;spec.loader.exec_module(status_module)
        key=self.folder/'key.pem';cert=self.folder/'cert.pem'
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        owner=self
        self.raw=b'<tv><channel id="demo"><display-name>Demo</display-name></channel><programme channel="demo" start="20991104000000 +0000" stop="20991104010000 +0000"><title>Demo</title></programme></tv>'
        self.body=gzip.compress(self.raw);self.status=200
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                self.send_response(owner.status);self.send_header('Content-Type','application/gzip');self.send_header('Content-Length',str(len(owner.body)));self.end_headers();self.wfile.write(owner.body)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(str(cert),str(key));server.socket=context.wrap_socket(server.socket,server_side=True)
        threading.Thread(target=server.serve_forever,daemon=True).start();self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        self.source=dict(provider='iptv-epg.org',url='https://localhost:'+str(server.server_port)+'/guide.xml.gz')
        trust=ssl.create_default_context(cafile=str(cert));opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=trust))
        # Trust substitutions apply only to the loopback fixture. Production
        # endpoint allowlist/DNS/TLS/redirect rejection is tested independently.
        for target,value in [('endpoint',lambda s:self.epg.urlsplit(s['url'])),('public_dns',lambda host:None),('build_opener',lambda *a:opener)]:
            patch=mock.patch.object(self.epg,target,value);patch.start();self.addCleanup(patch.stop)
    def test_full_gzip_https_verification_then_explicit_activation_retains_manual_mapping(self):
        proof=self.epg.verify(self.source);self.assertEqual(proof['channels'],1);self.assertEqual(proof['programmes'],1)
        sources=importlib.import_module('epg_sources');sources.set_mapping('p','1','manual-id')
        before=dict(sources.configuration('p')['mappings'])
        with mock.patch('epg.request_refresh',return_value=True,create=True):
            self.assertTrue(self.epg.activate(self.portal,dict(code='DE',label='Germany'),self.source,confirmed=True))
        cfg=sources.configuration('p');self.assertEqual(dict(cfg['mappings']),before)
        self.assertEqual(len(cfg['sources']),1);self.assertTrue(cfg['sources'][0]['enabled'])
        self.assertEqual(list((self.folder/'international73').glob('*xml*')),[])
    def test_http_error_or_bad_gzip_never_changes_existing_source_configuration(self):
        sources=importlib.import_module('epg_sources');sources.add_source('p','Existing','https://existing.invalid/epg.xml')
        before=sources._file_path();original=Path(before).read_bytes()
        self.status=503
        with self.assertRaises(Exception):self.epg.verify(self.source)
        self.status=200;self.body=b'\x1f\x8bbroken'
        with self.assertRaises(Exception):self.epg.verify(self.source)
        self.assertEqual(Path(before).read_bytes(),original)

    def test_inert_xmltv_doctype_uses_existing_parser_without_loading_dtd(self):
        import io
        from unittest import mock
        data=b'<!DOCTYPE tv SYSTEM "xmltv.dtd">'+self.raw
        with mock.patch.object(sys.modules['utils'],'http_get',side_effect=AssertionError('DTD network forbidden')):
            result=self.epg.inspect_xml(io.BytesIO(data))
        self.assertEqual(result['programmes'],1)

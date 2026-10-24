"""Trust, DNS pinning and real HTTP redirect transfers; never an Android claim."""
import hashlib,importlib,io,json,socket,sys,threading,types,unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture


class Redirect29Tests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('download_redirect','download_trust','download_trust_ui','download_worker','download_store'):sys.modules.pop(name,None)
        self.policy=importlib.import_module('download_redirect');self.trust=importlib.import_module('download_trust')
        self.source='https://provider.invalid';self.cdn='https://cdn.invalid'

    def response(self,status=200,location=''):
        return types.SimpleNamespace(status=status,headers={'Location':location},close=mock.Mock())

    def grant(self,target=None,pid='p',lan=False):self.trust.grant(dict(pid=pid,source=self.source,target=target or self.cdn),lan)

    def test_explicit_scoped_grant_strips_all_auth_and_custom_headers_then_revokes(self):
        self.grant();responses=[self.response(302,self.cdn+'/movie.mp4?signature=SECRET'),self.response()]
        sent=[]
        def transport(url,ips,headers):sent.append(dict(headers));return responses.pop(0)
        with mock.patch.object(self.policy,'addresses',return_value=['93.184.216.34']):
            self.policy.open_source(self.source+'/movie',{'Authorization':'SECRET','Cookie':'SECRET','X-Api-Key':'SECRET','Referer':'SECRET','Range':'bytes=3-','If-Range':'"v1"'},'p','job',transport)
        self.assertEqual(sent[0]['Authorization'],'SECRET')
        self.assertEqual(set(k.lower() for k in sent[1]),{'accept-encoding','range','if-range'})
        self.assertFalse(self.trust.allowed('foreign',self.source,self.cdn))
        self.assertFalse(self.trust.allowed('p','https://other.invalid',self.cdn))
        self.trust.revoke(self.trust.grants('p')[0]);self.assertFalse(self.trust.allowed('p',self.source,self.cdn))

    def test_unknown_host_not_contacted_and_pending_contains_only_origins(self):
        transport=mock.Mock(return_value=self.response(302,self.cdn+'/user/SECRET?token=SECRET'))
        with mock.patch.object(self.policy,'addresses',return_value=['93.184.216.34']):
            with self.assertRaisesRegex(Exception,'REDIRECT_UNTRUSTED_TARGET'):
                self.policy.open_source(self.source+'/private/SECRET',{},'p','job',transport)
        transport.assert_called_once();value=self.trust.pending('job','p')
        self.assertEqual(value['target'],self.cdn);self.assertNotIn('SECRET',json.dumps(value))
        self.assertIsNone(self.trust.pending('job','other-portal'))

    def test_relative_hops_keep_same_origin_auth_but_cross_and_return_never_restore_it(self):
        self.grant();sent=[];responses=[self.response(302,'/two'),self.response(307,self.cdn+'/three'),self.response(308,self.source+'/four'),self.response()]
        def transport(url,ips,headers):sent.append(dict(headers));return responses.pop(0)
        with mock.patch.object(self.policy,'addresses',return_value=['93.184.216.34']):
            self.policy.open_source(self.source+'/one',{'Authorization':'SECRET'},'p','j',transport)
        self.assertIn('Authorization',sent[1]);self.assertNotIn('Authorization',sent[2]);self.assertNotIn('Authorization',sent[3])

    def test_loop_hop_limit_downgrade_and_invalid_scheme_stop_before_next_connection(self):
        for destination,code in [('http://provider.invalid/file','REDIRECT_DOWNGRADE'),('file:///secret','UNSUPPORTED_SOURCE'),('https://u:SECRET@cdn.invalid/file','UNSUPPORTED_SOURCE')]:
            transport=mock.Mock(return_value=self.response(302,destination))
            with mock.patch.object(self.policy,'addresses',return_value=['93.184.216.34']):
                with self.assertRaisesRegex(Exception,code):self.policy.open_source(self.source+'/file',{},transport=transport)
            transport.assert_called_once()
        with mock.patch.object(self.policy,'addresses',return_value=['93.184.216.34']):
            with self.assertRaisesRegex(Exception,'REDIRECT_LOOP'):
                self.policy.open_source(self.source+'/one',{},transport=lambda *a:self.response(302,'/one'))
            counter=iter(range(20))
            with self.assertRaisesRegex(Exception,'REDIRECT_HOP_LIMIT'):
                self.policy.open_source(self.source+'/first',{},transport=lambda *a:self.response(302,'/'+str(next(counter))))

    def test_private_metadata_numeric_ipv6_mapped_and_mixed_dns_fail_closed(self):
        for ips in [('127.0.0.1',),('169.254.169.254',),('10.1.2.3',),('::1',),('::ffff:127.0.0.1',),('64:ff9b::a9fe:a9fe',),('2002:7f00:1::',),('93.184.216.34','192.168.1.3')]:
            with mock.patch.object(socket,'getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',(ip,443)) for ip in ips]):
                with self.assertRaisesRegex(Exception,'REDIRECT_PRIVATE_ADDRESS'):self.policy.addresses(self.source)
        with mock.patch.object(socket,'getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('192.168.1.3',443))]):
            self.assertEqual(self.policy.addresses(self.source,lan=True),['192.168.1.3'])
        with mock.patch.object(socket,'getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('169.254.169.254',443))]):
            with self.assertRaisesRegex(Exception,'REDIRECT_PRIVATE_ADDRESS'):self.policy.addresses(self.source,lan=True)

    def test_tls_connects_checked_numeric_ip_but_verifies_original_hostname(self):
        raw=mock.Mock();context=mock.Mock();connection=mock.Mock();connection.getresponse.return_value.status=200
        with mock.patch.object(socket,'create_connection',return_value=raw) as connect,\
             mock.patch.object(self.policy.ssl,'create_default_context',return_value=context),\
             mock.patch.object(self.policy.http.client,'HTTPConnection',return_value=connection):
            response=self.policy._connect(self.source+'/file',['93.184.216.34'],{})
        connect.assert_called_once_with(('93.184.216.34',443),timeout=10)
        context.wrap_socket.assert_called_once_with(raw,server_hostname='provider.invalid')
        self.assertEqual(response.source_fingerprint,hashlib.sha256((self.source+'/file').encode()).hexdigest())

    def test_rebinding_second_hop_to_private_ip_is_rejected_even_for_approved_host(self):
        self.grant();transport=mock.Mock(return_value=self.response(302,self.cdn+'/file'))
        with mock.patch.object(socket,'getaddrinfo',side_effect=[[(socket.AF_INET,1,6,'',('93.184.216.34',443))],[(socket.AF_INET,1,6,'',('10.0.0.1',443))]]):
            with self.assertRaisesRegex(Exception,'REDIRECT_PRIVATE_ADDRESS'):
                self.policy.open_source(self.source+'/file',{},'p','j',transport)
        transport.assert_called_once()

    def test_telemetry_never_contains_host_path_query_or_auth(self):
        with mock.patch.object(sys.modules['xbmc'],'log',create=True) as log,mock.patch.object(sys.modules['xbmc'],'LOGINFO',1,create=True):
            self.policy.mark(302,2,True,'https','REDIRECT_UNTRUSTED_TARGET')
        text=str(log.call_args_list)
        self.assertIn('DOWNLOAD_REDIRECT',text);self.assertIn('hop=2',text)
        for private in ('SECRET','provider.invalid','cdn.invalid','https://'):self.assertNotIn(private,text)

    def test_redirect_resume_requires_same_final_source_and_validator(self):
        store=importlib.import_module('download_store');worker=importlib.import_module('download_worker')
        payload=b'\0\0\0\x18ftypisom'+b'x'*200000
        for changed in (False,True):
            ident=store.enqueue(dict(pid='p',kind='vod',sid=str(changed),title='Fixture',target=str(self.folder)))
            response=io.BytesIO(payload);response.status=200
            response.headers={'Content-Length':str(len(payload)),'Content-Type':'video/mp4','ETag':'"v1"'}
            response.source_fingerprint=hashlib.sha256((self.cdn+'/one.mp4').encode()).hexdigest()
            read=response.read;called=[False]
            def pause(count):
                data=read(count)
                if not called[0]:called[0]=True;store.command(ident,'pause')
                return data
            response.read=pause
            with mock.patch.object(worker.time,'monotonic',side_effect=iter(range(1000))):
                worker.run_one(resolver=lambda m:(self.source+'/file',{}),opener=lambda *a:response)
            row=store.get(ident);self.assertEqual(row['state'],'PAUSED');offset=row['bytes'];before=Path(row['part']).read_bytes()
            self.assertTrue(store.command(ident,'resume'))
            resumed=io.BytesIO(payload[offset:]);resumed.status=206
            resumed.headers={'Content-Length':str(len(payload)-offset),'Content-Type':'video/mp4','ETag':'"v1"','Content-Range':f'bytes {offset}-{len(payload)-1}/{len(payload)}'}
            resumed.source_fingerprint=hashlib.sha256((self.cdn+('/two.mp4' if changed else '/one.mp4')).encode()).hexdigest()
            opened=mock.Mock(return_value=resumed)
            worker.run_one(resolver=lambda m:(self.source+'/file',{}),opener=opened)
            self.assertEqual(opened.call_args.args[1]['Range'],f'bytes={offset}-')
            row=store.get(ident)
            if changed:
                self.assertEqual((row['state'],row['code']),('FAILED','SOURCE_CHANGED'))
                self.assertEqual(Path(row['part']).read_bytes(),before)
            else:self.assertEqual(row['state'],'COMPLETE',row['code']);self.assertEqual(Path(row['file']).read_bytes(),payload)

    def test_approved_redirect_still_requires_valid_media_length(self):
        self.grant();store=importlib.import_module('download_store');worker=importlib.import_module('download_worker')
        for length in ('','not-a-length'):
            ident=store.enqueue(dict(pid='p',kind='vod',sid=length or 'empty',title='Fixture',target=str(self.folder)))
            response=io.BytesIO(b'\0\0\0\x18ftypisom'+b'x'*5000);response.status=200;response.headers={'Content-Type':'video/mp4','Content-Length':length}
            values=[self.response(302,self.cdn+'/file.mp4'),response]
            with mock.patch.object(self.policy,'addresses',return_value=['93.184.216.34']):
                worker.run_one(resolver=lambda m:(self.source+'/file',{}),opener=lambda url,headers:self.policy.open_source(url,headers,'p',ident,lambda *a:values.pop(0)))
            row=store.get(ident);self.assertEqual((row['state'],row['code']),('FAILED','LENGTH_REQUIRED'));self.assertEqual(row['bytes'],0)

    def test_real_two_server_movie_and_episode_transfer_with_explicit_trust(self):
        payload=b'\0\0\0\x18ftypisom'+b'x'*90000;seen=[]
        class CDN(BaseHTTPRequestHandler):
            def log_message(self,*a):pass
            def do_GET(self):
                seen.append(dict(self.headers));self.send_response(200);self.send_header('Content-Type','video/mp4');self.send_header('Content-Length',str(len(payload)));self.send_header('ETag','"v1"');self.end_headers();self.wfile.write(payload)
        cdn=ThreadingHTTPServer(('127.0.0.1',0),CDN)
        class Provider(BaseHTTPRequestHandler):
            def log_message(self,*a):pass
            def do_GET(self):
                self.send_response(302);self.send_header('Location',f'http://127.0.0.1:{cdn.server_port}/signed.mp4?token=SECRET');self.end_headers()
        provider=ThreadingHTTPServer(('127.0.0.1',0),Provider)
        threads=[]
        for server in (provider,cdn):
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();threads.append(thread)
        try:
            source=f'http://127.0.0.1:{provider.server_port}';target=f'http://127.0.0.1:{cdn.server_port}'
            self.trust.grant(dict(pid='p',source=source,target=target))
            store=importlib.import_module('download_store');worker=importlib.import_module('download_worker')
            # Deliberate loopback transport fixture only. Real address-policy,
            # private-network and TLS-pin decisions are tested independently.
            with mock.patch.object(self.policy,'addresses',return_value=['127.0.0.1']):
                for kind,sid in [('vod','film'),('episode','episode')]:
                    media=dict(pid='p',kind=kind,sid=sid,title='Fixture',target=str(self.folder),season='1',episode='2',series_id='s')
                    ident=store.enqueue(media)
                    worker.run_one(resolver=lambda m:(source+'/file',{'Authorization':'SECRET','Cookie':'SECRET'}))
                    row=store.get(ident);self.assertEqual(row['state'],'COMPLETE',row['code'])
                    self.assertEqual(Path(row['file']).read_bytes(),payload);self.assertNotIn('SECRET',json.dumps(row))
            self.assertEqual(len(seen),2)
            for headers in seen:self.assertNotIn('Authorization',headers);self.assertNotIn('Cookie',headers)
        finally:
            for server in (provider,cdn):server.shutdown();server.server_close()
            for thread in threads:thread.join(2)


if __name__=='__main__':unittest.main()

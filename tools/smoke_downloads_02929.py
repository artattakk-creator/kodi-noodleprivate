"""Host-only combined redirect/storage/decode fixture (requires impacket+ffmpeg).

Usage: PYTHONPATH=<impacket-path> python tools/smoke_downloads_02929.py fixture.mp4 report.json
No Kodi/user provider/SMB connection. Loopback is allowed only by the test patch.
"""
import argparse,hashlib,json,logging,subprocess,sys,tempfile,threading,types
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from unittest import mock


def main():
    parser=argparse.ArgumentParser();parser.add_argument('fixture',type=Path);parser.add_argument('report',type=Path);args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src/plugin.video.xtreammate/resources/lib'))
    payload=args.fixture.read_bytes();seen=[];rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        folder=Path(tmp);data=folder/'data';data.mkdir();share=folder/'share';share.mkdir()
        sys.modules['utils']=types.SimpleNamespace(addon_data_dir=lambda:str(data),setting_int=lambda k,d:d)
        import download_worker as worker,download_store as store,download_trust as trust,download_targets as targets,download_smb as smb,atomic_media
        class CDN(BaseHTTPRequestHandler):
            def log_message(self,*a):pass
            def do_GET(self):
                seen.append(dict(self.headers));self.send_response(200);self.send_header('Content-Length',str(len(payload)));self.send_header('Content-Type','video/mp4');self.send_header('ETag','"fixture-v1"');self.end_headers();self.wfile.write(payload)
        cdn=ThreadingHTTPServer(('127.0.0.1',0),CDN)
        class Provider(BaseHTTPRequestHandler):
            def log_message(self,*a):pass
            def do_GET(self):
                self.send_response(302);self.send_header('Location',f'http://127.0.0.1:{cdn.server_port}/fixture.mp4?signature=FIXTURE_ONLY');self.end_headers()
        provider=ThreadingHTTPServer(('127.0.0.1',0),Provider);threads=[]
        for server in (cdn,provider):
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();threads.append(thread)
        process=subprocess.Popen([sys.executable,str(root/'tests/fixtures/smb29_server.py'),str(share)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
        try:
            ready=process.stdout.readline()
            if not ready:raise RuntimeError('host SMB fixture unavailable')
            port=json.loads(ready)['port'];uri=f'smb://127.0.0.1:{port}/MEDIA';smb.credentials(uri,('fixture','fixture-password',''))
            source=f'http://127.0.0.1:{provider.server_port}';target=f'http://127.0.0.1:{cdn.server_port}'
            trust.grant(dict(pid='fixture',source=source,target=target))
            native=atomic_media.probe;usb_stage=folder/'usb_stage';usb_stage.mkdir()
            def probe(path,create=False):
                if str(path)==str(usb_stage):raise atomic_media.StorageFailure('TARGET_SYNC_UNSUPPORTED','FSYNC_DIRECTORY',22)
                return native(path,create)
            with mock.patch('download_redirect.addresses',return_value=['127.0.0.1']),mock.patch.object(atomic_media,'probe',side_effect=probe):
                for label,destination in [('INTERNAL',str(folder/'internal')),('USB_NATIVE_SIMULATED',str(folder/'usb_native')),('USB_STAGED_SIMULATED',str(usb_stage)),('SMB2_LOOPBACK',uri)]:
                    if label in ('USB_STAGED_SIMULATED','SMB2_LOOPBACK'):targets.approved(destination,save=True)
                    caps=targets.probe(destination)
                    for kind,sid in [('vod',label+'-film'),('episode',label+'-episode')]:
                        ident=store.enqueue(dict(pid='fixture',sid=sid,kind=kind,title='Fixture',series_title='Fixture series',series_id='s',season='1',episode='2',target=destination))
                        worker.run_one(resolver=lambda m:(source+'/media',{'Authorization':'FIXTURE_ONLY','Cookie':'FIXTURE_ONLY','X-Provider-Key':'FIXTURE_ONLY'}))
                        row=store.get(ident)
                        if row['state']!='COMPLETE':raise RuntimeError(row['code'])
                        file=share/smb.parse(row['file'])[4] if row['file'].startswith('smb://') else Path(row['file'])
                        digest=hashlib.sha256(file.read_bytes()).hexdigest()
                        assert digest==hashlib.sha256(payload).hexdigest() and file.stat().st_size==len(payload)
                        decoded=subprocess.run(['ffmpeg','-v','error','-err_detect','explode','-i',str(file),'-f','null','-'],capture_output=True)
                        assert decoded.returncode==0 and not decoded.stderr
                        rows.append(dict(destination=label,backend=caps['backend'],kind=kind,status='COMPLETE',bytes=row['bytes'],sha256=digest,strict_ffmpeg_decode='PASS',android_playback='NOT_TESTED'))
            assert len(seen)==8
            assert all(not any(k in h for k in ('Authorization','Cookie','X-Provider-Key')) for h in seen)
            report=dict(environment='Host real two-server HTTP redirect + authenticated signed SMB2 fixture',public_ssrf_policy='Unit tests; loopback address validation overridden only in this controlled fixture',credentials_forwarded=False,transfers=rows,actual_android_usb_mount='NOT_TESTED',kodi_vfs_playback='NOT_TESTED',production_publish=False)
            args.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(transfers=len(rows),decode='PASS',credentials_forwarded=False)))
        finally:
            process.terminate();process.wait(timeout=5);process.stdout.close()
            for server in (provider,cdn):server.shutdown();server.server_close()
            for thread in threads:thread.join(2)


if __name__=='__main__':main()

"""Real-time loopback smoke run from a real MPEG-TS fixture; no Kodi claim.

Example: python experiments/native_ts/smoke.py /tmp/fixture.ts /tmp/capture
Generate a 180-second, 600 kbit/s fixture externally; this helper itself never
starts FFmpeg. The recording engine never calls an external executable.
"""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time

from recorder import Recorder


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('fixture',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--seconds',type=float,default=120)
    parser.add_argument('--rate',type=float,default=75000)
    args=parser.parse_args()
    if args.rate<=0 or args.fixture.stat().st_size<args.rate*(args.seconds+10):parser.error('fixture must cover duration plus ten seconds')
    args.output.mkdir(parents=True,exist_ok=True)
    stopped=threading.Event()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*a):pass
        def do_GET(self):
            self.send_response(200);self.send_header('Content-Type','video/mp2t');self.end_headers()
            try:
                with args.fixture.open('rb') as source:
                    start=time.monotonic();sent=0
                    while not stopped.is_set():
                        chunk=source.read(188*200)
                        if not chunk:return
                        self.wfile.write(chunk);self.wfile.flush();sent+=len(chunk)
                        if stopped.wait(max(0,start+sent/args.rate-time.monotonic())):return
            except (BrokenPipeError,ConnectionResetError):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    start=time.monotonic()
    try:
        job=Recorder('http://127.0.0.1:'+str(server.server_port)+'/stream.ts',str(args.output.resolve()),args.seconds,separate_connection=True)
        worker=threading.Thread(target=job.run,name='DirectTS-smoke');worker.start()
        worker.join(args.seconds+20)
        if worker.is_alive():job.stop();worker.join(3);raise RuntimeError('bounded worker completion failed')
        state=dict(job.state);state['host_elapsed_seconds']=round(time.monotonic()-start,3)
        state['kodi_offline_playback']='NOT_TESTED'
        if state['status']!='complete':raise RuntimeError('recording failed: '+state['code'])
        final=args.output/state['file'];state['sha256']=hashlib.sha256(final.read_bytes()).hexdigest()
        assert final.stat().st_size%188==0 and not list(args.output.glob('*.part'))
        (args.output/'smoke-report.json').write_text(json.dumps(state,indent=2)+'\n')
        print(json.dumps(state),flush=True)
    finally:stopped.set();server.shutdown();server.server_close();thread.join(2)


if __name__=='__main__':main()

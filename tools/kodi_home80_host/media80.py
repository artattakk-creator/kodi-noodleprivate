"""Loopback-only ranged synthetic MP4 server for real Kodi resolver tests."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import re
class Media80(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path!='/sample.mp4':self.send_error(404);return
  path=Path('/root/media/sample.mp4');size=path.stat().st_size;start=0;end=size-1
  header=self.headers.get('Range','')
  if header:
   match=re.fullmatch(r'bytes=(\d+)-(\d*)',header)
   if not match:self.send_error(416);return
   start=int(match[1]);end=min(int(match[2]) if match[2] else end,end)
   if start>end:self.send_error(416);return
  self.send_response(206 if header else 200);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if header:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  try:
   with path.open('rb') as stream:
    stream.seek(start);remaining=end-start+1
    while remaining:
     data=stream.read(min(65536,remaining))
     if not data:break
     self.wfile.write(data);remaining-=len(data)
  except (BrokenPipeError,ConnectionResetError):pass
 def log_message(self,*args):pass
ThreadingHTTPServer(('127.0.0.1',18380),Media80).serve_forever()

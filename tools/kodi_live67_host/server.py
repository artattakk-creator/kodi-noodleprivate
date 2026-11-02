"""Disposable loopback-only synthetic media provider; never logs URLs."""
import json
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
stats={}
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_HEAD(self):self.send_error(504)
 def do_GET(self):
  name=Path(urlsplit(self.path).path).name
  if name=='stats':
   data=json.dumps(stats).encode();self.send_response(200);self.end_headers();self.wfile.write(data);return
  key='api' if name=='player_api.php' else name;stats[key]=stats.get(key,0)+1
  if key=='api' or name.startswith('5.'):self.send_error(504);return
  if name.startswith('6.'):data=b'<html>synthetic gateway error</html>';mime='text/html'
  elif name.endswith('.m3u8'):data=Path('/root/media/playlist.m3u8').read_bytes();mime='application/vnd.apple.mpegurl'
  elif name.startswith('segment') and name.endswith('.ts'):data=(Path('/root/media')/name).read_bytes();mime='video/mp2t'
  else:data=Path('/root/media/sample.ts').read_bytes();mime='video/mp2t'
  self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.end_headers()
  try:self.wfile.write(data)
  except (BrokenPipeError,ConnectionResetError):pass
ThreadingHTTPServer(('127.0.0.1',18081),Handler).serve_forever()

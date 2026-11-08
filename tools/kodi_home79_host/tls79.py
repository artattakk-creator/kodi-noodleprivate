"""Disposable synthetic HTTPS image origin; never installed on a user device."""
import argparse,io,json,ssl,subprocess
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
cert=Path('/usr/local/share/ca-certificates/xcmate-synthetic69.crt');key=Path('/root/synthetic69.key')
if args.prepare:
 subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=image.tmdb.org','-addext','subjectAltName=DNS:image.tmdb.org','-addext','basicConstraints=critical,CA:TRUE'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 subprocess.run(['update-ca-certificates'],check=True,stdout=subprocess.DEVNULL)
 # Some Kodi packages select a bundled CA file instead of system defaults.
 for bundle in (Path('/usr/share/kodi/system/certs/cacert.pem'),Path('/usr/lib/x86_64-linux-gnu/kodi/system/certs/cacert.pem')):
  if bundle.is_file() and not bundle.is_symlink():
   with bundle.open('a') as out:out.write('\n'+cert.read_text())
 with Path('/etc/hosts').open('a') as out:out.write('\n127.0.0.1 image.tmdb.org\n')
 raise SystemExit(0)
from PIL import Image
images={}
for sid,format_,color in (('5','PNG',(25,145,100)),('6','JPEG',(145,70,120))):
 image=io.BytesIO();Image.new('RGB',(160,90),color).save(image,format_);images['/t/p/w500/url69-'+sid+'.jpg']=(image.getvalue(),'image/png' if format_=='PNG' else 'image/jpeg')
class Handler(BaseHTTPRequestHandler):
 def do_HEAD(self):self.send(False)
 def do_GET(self):self.send(True)
 def send(self,body):
  data,kind=images.get(self.path,(b'','text/plain'))
  if Path('/root/tls79-off').exists():data=b''
  with Path('/root/tls69-requests.jsonl').open('a') as out:out.write(json.dumps(dict(method=self.command,path=self.path,authorization=bool(self.headers.get('Authorization')),cookie=bool(self.headers.get('Cookie'))))+'\n')
  self.send_response(200 if data else 404);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.end_headers()
  if body:self.wfile.write(data)
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('0.0.0.0',443),Handler);context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(str(cert),str(key));server.socket=context.wrap_socket(server.socket,server_side=True);server.serve_forever()

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
for role,count,size,base in (('logo',88,(160,80),(25,100,160)),('vod',24,(160,240),(180,100,30)),('series',24,(160,240),(100,60,180)),('fanart',24,(1280,720),(35,120,80)),('event',88,(1280,720),(20,80,130))):
 for i in range(count):
  image=io.BytesIO();Image.new('RGB',size,(245,245,245) if role=='event' and i==1 else tuple((c+i*7)%220 for c in base)).save(image,'PNG');images['/t/p/w500/'+role+'84-'+str(i)+'.png']=(image.getvalue(),'image/png')
for i in range(5):
 image=io.BytesIO();Image.new('RGB',(800,1200),(80,120,200)).save(image,'PNG');images['/t/p/w500/official86-'+str(i)+'.png']=(image.getvalue(),'image/png')
for path,value in list(images.items()):
 images[path.replace('/w500/','/w1280/')]=value
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

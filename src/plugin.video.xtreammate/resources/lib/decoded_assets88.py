"""Bounded decoded bytes served ONLY on loopback, never a URL fetch proxy.

Existing workers supply complete validated images. Kodi's cross-interpreter
texture loader reads random capabilities; no private remote URL is admitted.
This is RAM_ONLY, not a filesystem archive or proof of visible pixels.
"""
import hashlib,json,secrets,threading,time
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler,HTTPServer
_lock=threading.RLock();_server=None;_thread=None;_stop=threading.Event();_items=OrderedDict()
MAX_BYTES=16*1024*1024;MAX_OBJECTS=128;PREFIX='XCMate.Decoded88.'
INSTANCE=__import__('secrets').token_hex(16)
def owner_slot():
 from epg_handoff63 import profile_scope
 return PREFIX+'Owner.'+hashlib.sha256(profile_scope().encode()).hexdigest()
def descriptor():
 try:
  value=json.loads(window().getProperty(owner_slot()) or '{}')
  if value.get('until88',0)>time.monotonic():return value
 except (ValueError,TypeError):pass
 return None
def slot(key):
 from epg_handoff63 import profile_scope
 return PREFIX+hashlib.sha256((profile_scope()+key).encode()).hexdigest()
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.client_address[0]!='127.0.0.1':self.send_error(403);return
  with _lock:
   item=_items.get(self.path)
   if not item or item['until']<=time.time():self.send_error(404);return
   body=item['body'];mime=item['mime'];item['active']=time.monotonic()+60
  self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','private, max-age=60');self.end_headers()
  try:self.wfile.write(body)
  except (OSError,TimeoutError):pass
 def do_POST(self):
  if self.client_address[0]!='127.0.0.1' or self.path!='/xcmate88-upload/'+self.server.upload88:self.send_error(403);return
  try:
   import math,re
   size=int(self.headers.get('Content-Length','0'));key=self.headers.get('X-XCMate-Key','');until=float(self.headers.get('X-XCMate-Until','0'));kind=self.headers.get('X-XCMate-Kind','')
   if not 0<size<=3*1024*1024 or not re.fullmatch(r'[a-zA-Z0-9_.-]{1,256}',key) or not math.isfinite(until) or not time.time()<until<=time.time()+86401 or kind not in ('logo','event'):raise ValueError('UPLOAD_LIMIT')
   body=self.rfile.read(size)
   if len(body)!=size:raise ValueError('UPLOAD_INCOMPLETE')
   proof=self.headers.get('X-XCMate-Receipt','')
   if len(proof)>1024:raise ValueError('UPLOAD_PROOF_LIMIT')
   record=put(key,body,until,kind,json.loads(proof) if proof else None)
   raw=json.dumps(record,separators=(',',':')).encode()
   self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  except (OSError,ValueError,__import__('media_sources43').SourceError):self.send_error(400)
 def setup(self):
  super().setup();self.connection.settimeout(3)
def _heartbeat(server):
 until=time.monotonic()+15;instance=server.instance88
 window().setProperty(PREFIX+'Instance.'+instance,str(until))
 window().setProperty(server.owner_slot88,json.dumps(dict(instance88=instance,until88=until,url='http://127.0.0.1:'+str(server.server_port)+'/xcmate88-upload/'+server.upload88),separators=(',',':')))
def _proxy(key,body,until,kind,value,receipt88=None):
 import http.client,re
 from urllib.parse import urlsplit
 parsed=urlsplit(value.get('url',''))
 if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or not parsed.port or parsed.username is not None or parsed.query or parsed.fragment or not re.fullmatch(r'/xcmate88-upload/[a-f0-9]{64}',parsed.path):raise OSError('DECODED_OWNER_INVALID')
 connection=http.client.HTTPConnection('127.0.0.1',parsed.port,timeout=3)
 try:
  connection.request('POST',parsed.path,body,{'Content-Type':'application/octet-stream','X-XCMate-Key':key,'X-XCMate-Until':str(until),'X-XCMate-Kind':kind,'X-XCMate-Receipt':json.dumps(receipt88 or {},separators=(',',':'))})
  response=connection.getresponse();raw=response.read(2049)
  if response.status!=200 or len(raw)>2048:raise OSError('DECODED_OWNER_UNAVAILABLE')
  result=json.loads(raw)
  if not isinstance(result,dict) or result.get('sha256')!=hashlib.sha256(body).hexdigest() or read(key)!=result:raise OSError('DECODED_OWNER_READBACK')
  return result
 except http.client.HTTPException:raise OSError('DECODED_OWNER_UNAVAILABLE') from None
 finally:connection.close()
def _retire(server):
 try:
  window().clearProperty(PREFIX+'Instance.'+server.instance88)
  current=json.loads(window().getProperty(server.owner_slot88) or '{}')
  if current.get('instance88')==server.instance88:window().clearProperty(server.owner_slot88)
 except (ValueError,TypeError,AttributeError,RuntimeError):pass
def _serve(server,stop):
 import xbmc
 aborted=getattr(xbmc.Monitor(),'abortRequested',lambda:False)
 due=0.
 try:
  while not stop.is_set() and not aborted():
   if time.monotonic()>=due:_heartbeat(server);due=time.monotonic()+5
   try:server.handle_request()
   except (OSError,ValueError):
    if not stop.is_set() and not aborted():raise
 finally:
  _retire(server)
  server.server_close()
def put(key,body,until,kind='event',receipt88=None):
 proof88=__import__('event_cache88').encode(key,receipt88) if receipt88 else ''
 if receipt88 and kind!='event':raise ValueError('CACHE88_ROLE')
 from media_sources43 import validate_image
 width,height=validate_image(body)
 if not 0<len(body)<=3*1024*1024 or until<=time.time():raise ValueError('DECODED_LIMIT')
 if kind=='logo' and (width>2048 or height>2048):raise ValueError('LOGO_DIMENSION_LIMIT')
 global _server,_thread,_stop
 # Reuse the already active owner across Kodi plugin interpreters. Uploads
 # carry only decoded bytes and scoped hashes, never source URLs/secrets.
 owner=descriptor()
 if _server is None and owner:return _proxy(key,body,until,kind,owner,receipt88)
 digest=hashlib.sha256(body).hexdigest();now=time.monotonic()
 with _lock:
  old=read(key)
  if old and old.get('sha256')==digest:return old
  for path,item in list(_items.items()):
   if item['until']<=time.time():_remove(path,item)
  while len(_items)>=MAX_OBJECTS or sum(len(v['body']) for v in _items.values())+len(body)>MAX_BYTES:
   candidate=next(((p,v) for p,v in _items.items() if v['active']<=now and not active(v['key'])),None)
   if candidate is None:raise OSError('DECODED_PINNED_LIMIT')
   _remove(*candidate)
  if _server is None:
   # Existing profile coordination lock prevents simultaneous interpreters
   # from starting independent owners. This is not an artwork/DB write.
   from profile_transaction import writing
   with writing(timeout=.2):
    owner=descriptor()
    if owner:return _proxy(key,body,until,kind,owner,receipt88)
    _server=HTTPServer(('127.0.0.1',0),Handler)
    _server.instance88=secrets.token_hex(16);_server.upload88=secrets.token_hex(32);_server.owner_slot88=owner_slot();_heartbeat(_server)
    _server.timeout=.2;_stop=threading.Event()
    _thread=threading.Thread(target=_serve,args=(_server,_stop),name='XCMate-decoded88',daemon=True);_thread.start()
  path='/xcmate88/'+secrets.token_hex(32)+'/'+hashlib.sha256(key.encode()).hexdigest()+'.'+('png' if body.startswith(b'\x89PNG') else 'jpg')
  if proof88:path+='?event88='+key.split('.')[0]+'&body88='+digest+'&proof88='+proof88
  uri='http://127.0.0.1:'+str(_server.server_port)+path
  record=dict(instance88=_server.instance88,uri=uri,key=key,sha256=digest,width=width,height=height,until=min(until,time.time()+86400),storage='RAM_ONLY')
  _items[path]=dict(body=body,mime='image/png' if body.startswith(b'\x89PNG') else 'image/jpeg',until=record['until'],active=now+60,key=key,slot88=slot(key))
  window().setProperty(slot(key),json.dumps(record,separators=(',',':')))
  return record
def _remove(path,item):
 _items.pop(path,None);receipt_slot=item.get('slot88',slot(item['key']))
 try:current=json.loads(window().getProperty(receipt_slot) or '{}')
 except (ValueError,TypeError):current={}
 if current.get('uri','').endswith(path):
  window().clearProperty(receipt_slot);window().clearProperty(receipt_slot+'.active')
def read(key):
 try:
  raw=window().getProperty(slot(key));value=json.loads(raw) if raw and len(raw)<2048 else {}
  if value.get('key')==key and float(window().getProperty(PREFIX+'Instance.'+str(value.get('instance88',''))) or '0')>time.monotonic() and time.time()<value.get('until',0)<=time.time()+86401 and value.get('uri','').startswith('http://127.0.0.1:'):
   if not active(key):window().setProperty(slot(key)+'.active',str(time.monotonic()+60))
   return value
 except (ValueError,TypeError,AttributeError,RuntimeError):pass
 return None
def active(key):
 try:return float(window().getProperty(slot(key)+'.active') or '0')>time.monotonic()+10
 except (ValueError,TypeError):return False
def release(key):window().clearProperty(slot(key)+'.active')
def valid(key,uri,digest=None):
 value=read(key)
 return bool(value and value['uri']==uri and (not digest or value['sha256']==digest))
def shutdown():
 global _server,_thread
 with _lock:
  server,thread,stop=_server,_thread,_stop;_server=None;_thread=None
  for path,item in list(_items.items()):_remove(path,item)
 stop.set()
 if server:
  _retire(server)
  server.server_close()
 if thread and thread is not threading.current_thread():thread.join(timeout=.5)

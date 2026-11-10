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
 def setup(self):
  super().setup();self.connection.settimeout(3)
def _serve(server):
 import xbmc
 aborted=getattr(xbmc.Monitor(),'abortRequested',lambda:False)
 try:
  while not _stop.is_set() and not aborted():
   try:server.handle_request()
   except (OSError,ValueError):
    if not _stop.is_set() and not aborted():raise
 finally:server.server_close()
def put(key,body,until,kind='event'):
 from media_sources43 import validate_image
 width,height=validate_image(body)
 if not 0<len(body)<=3*1024*1024 or until<=time.time():raise ValueError('DECODED_LIMIT')
 if kind=='logo' and (width>2048 or height>2048):raise ValueError('LOGO_DIMENSION_LIMIT')
 global _server,_thread
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
   _server=HTTPServer(('127.0.0.1',0),Handler)
   window().setProperty(PREFIX+'Instance',INSTANCE)
   _server.timeout=.2;_stop.clear()
   _thread=threading.Thread(target=_serve,args=(_server,),name='XCMate-decoded88',daemon=True);_thread.start()
  path='/'+secrets.token_hex(32)+'.'+('png' if body.startswith(b'\x89PNG') else 'jpg')
  uri='http://127.0.0.1:'+str(_server.server_port)+path
  record=dict(instance88=INSTANCE,uri=uri,key=key,sha256=digest,width=width,height=height,until=min(until,time.time()+86400),storage='RAM_ONLY')
  _items[path]=dict(body=body,mime='image/png' if body.startswith(b'\x89PNG') else 'image/jpeg',until=record['until'],active=now+60,key=key)
  window().setProperty(slot(key),json.dumps(record,separators=(',',':')))
  return record
def _remove(path,item):
 _items.pop(path,None);window().clearProperty(slot(item['key']));window().clearProperty(slot(item['key'])+'.active')
def read(key):
 try:
  raw=window().getProperty(slot(key));value=json.loads(raw) if raw and len(raw)<2048 else {}
  if value.get('key')==key and value.get('instance88')==window().getProperty(PREFIX+'Instance') and time.time()<value.get('until',0)<=time.time()+86401 and value.get('uri','').startswith('http://127.0.0.1:'):
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
  server=_server;_server=None
  for path,item in list(_items.items()):_remove(path,item)
 _stop.set()
 if server:server.server_close()
 if _thread and _thread is not threading.current_thread():_thread.join(timeout=.5)
 _thread=None

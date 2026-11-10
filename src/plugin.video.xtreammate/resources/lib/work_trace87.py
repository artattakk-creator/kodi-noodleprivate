"""One bounded, redacted manual-operation receipt; no titles, paths or URLs."""
import hashlib,json,time
PREFIX='XCMate.Work87.'
STAGES=('ENQUEUED','PICKED','SOURCE_REVERIFIED','EPG_SCOPE_REVALIDATED','WRITE_READBACK','DELIVERED','UI_CONSUMED')
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def pulse(code='WORKER_READY'):
 window().setProperty(PREFIX+'Worker',json.dumps(dict(code=code,at=time.time())))
def worker():
 try:
  data=json.loads(window().getProperty(PREFIX+'Worker') or '{}')
  return data.get('code','WORKER_STOPPED') if 0<=time.time()-data.get('at',0)<(35 if data.get('code')=='WORKER_BUSY' else 3) else 'WORKER_STOPPED'
 except (ValueError,TypeError):return 'WORKER_STOPPED'
def mark(nonce,stage,operation='',source=''):
 if not isinstance(nonce,str) or len(nonce)!=32 or stage not in STAGES:return
 win=window();key=PREFIX+'Trace.'+hashlib.sha256(nonce.encode()).hexdigest();now=time.monotonic()
 try:data=json.loads(win.getProperty(key) or '{}')
 except ValueError:data={}
 digest=hashlib.sha256(nonce.encode()).hexdigest()
 if data.get('id')!=digest:data=dict(id=digest,started=now,stages={})
 data['stages'].setdefault(stage,max(0,round((now-data['started'])*1000)))
 if operation in ('search','save','local'):data['operation']=operation
 if source in ('tmdb','tvmaze','user_local86'):data['source']=source
 win.setProperty(key,json.dumps(data,separators=(',',':')))
 win.setProperty(PREFIX+'Trace',json.dumps(data,separators=(',',':')))
 try:keys=json.loads(win.getProperty(PREFIX+'Index') or '[]')
 except ValueError:keys=[]
 if key not in keys:keys.append(key)
 while len(keys)>16:win.clearProperty(keys.pop(0))
 win.setProperty(PREFIX+'Index',json.dumps(keys))
def picked(nonce):
 try:
  data=json.loads(window().getProperty(PREFIX+'Trace.'+hashlib.sha256(nonce.encode()).hexdigest()) or '{}')
  return data.get('id')==hashlib.sha256(nonce.encode()).hexdigest() and 'PICKED' in data.get('stages',{})
 except (ValueError,TypeError):return False

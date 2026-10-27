"""Bounded event-art worker, private persistent cache, no GUI network or writes.

Two workers maximum, 24 waiting events, 128 RAM records, configurable 32/64/128/256 MiB disk ceiling.
Existing cover jobs/files, Kodi textures, artwork mode and guide DB are untouched.
"""
from collections import OrderedDict
import hashlib,json,os,threading,time,tempfile
_lock=threading.Lock();_queue=OrderedDict();_memory=OrderedDict();_pending=set();_workers=[];_stop=threading.Event();_wake=threading.Event()
MAX_DISK=64*1024*1024

class CacheBudget(OSError):pass

def limit():
 from utils import setting_int
 return (32,64,128,256)[max(0,min(3,setting_int('programme_art_budget46',1)))]*1024*1024

def root():
 from utils import addon_data_dir
 return os.path.join(addon_data_dir(),'programme_images46')

def fingerprint(event):
 return hashlib.sha256(json.dumps([event.get(k) for k in ('xmltv_image','provider_image','title','subtitle','year','season','episode','epg_source46')],sort_keys=True).encode()).hexdigest()

def peek(event):
 with _lock:value=_memory.get(event['key'])
 return dict(value) if value and value.get('fingerprint')==fingerprint(event) else dict(code='PENDING',image=event['placeholder'],source='placeholder',match='NONE')

def remember(key,value):
 with _lock:
  _memory[key]=dict(value);_memory.move_to_end(key)
  while len(_memory)>128:_memory.popitem(last=False)

def enqueue(event):
 if not event.get('title') or _stop.is_set():return False
 from utils import setting_bool
 if not event.get('xmltv_image') and not event.get('provider_image') and not setting_bool('programme_tmdb46',False):
  remember(event['key'],dict(key=event['key'],fingerprint=fingerprint(event),code='NO_IMAGE',image=event['placeholder'],source='placeholder',match='NONE',until=time.time()+21600));return False
 key=event['key'];fp=fingerprint(event)
 with _lock:
  old=_memory.get(key)
  if old and old.get('fingerprint')==fp and old.get('until',0)>time.time() and not (old.get('code')=='PROGRAMME_CACHE_BUDGET' and old.get('budget46')!=limit()):return False
  if key in _pending or len(_pending)>=24:return False
  _pending.add(key);_queue[key]=dict(event)
 ensure();_wake.set();return True

def ensure():
 with _lock:
  _workers[:]=[t for t in _workers if t.is_alive()]
  while len(_workers)<2 and not _stop.is_set():
   t=threading.Thread(target=run,name='XCMate-programme46',daemon=True);_workers.append(t);t.start()

def atomic(filename,data):
 fd,temp=tempfile.mkstemp(prefix='.programme46-',dir=root())
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(temp,filename)
 finally:
  if os.path.exists(temp):os.unlink(temp)

def persisted(event,verify=True):
 try:
  p=os.path.join(root(),event['key']+'.json')
  if os.path.islink(p):return None
  with open(p,'rb') as f:raw=f.read(8193)
  if len(raw)>8192:return None
  v=json.loads(raw)
  if v.get('fingerprint')!=fingerprint(event) or v.get('key')!=event['key']:return None
  if v.get('image'):
   name=v['image']
   if os.path.basename(name)!=name:return None
   file=os.path.join(root(),name)
   if os.path.islink(file) or not os.path.isfile(file) or os.path.getsize(file)>3*1024*1024:return None
   if verify:
    with open(file,'rb') as f:data=f.read(3*1024*1024+1)
    if hashlib.sha256(data).hexdigest()!=v.get('sha256'):return None
    from media_sources43 import validate_image
    validate_image(data)
   v['image']=file
  else:v['image']=event['placeholder']
  return v
 except Exception:return None

def space(upcoming):
 folder=root();os.makedirs(folder,mode=0o700,exist_ok=True)
 if os.path.islink(folder):raise OSError('CACHE_UNSAFE')
 total=0;count=0
 for row in os.scandir(folder):
  count+=1
  if count>1024:raise CacheBudget('PROGRAMME_CACHE_BUDGET')
  if row.is_file(follow_symlinks=False):total+=row.stat().st_size
 if total+upcoming>limit():raise CacheBudget('PROGRAMME_CACHE_BUDGET')
 from art_storage import check
 from art_store import used
 check(upcoming,used=used()+total,location=folder)

def display_image(data):
 """Bounded display derivative, never crops or burns station branding."""
 from media_sources43 import validate_image
 width,height=validate_image(data)
 if width<=1280 and height<=720:return data
 import io
 from PIL import Image
 with Image.open(io.BytesIO(data)) as image:
  format=image.format;image.thumbnail((1280,720),getattr(Image,'Resampling',Image).LANCZOS)
  out=io.BytesIO()
  if format=='PNG':image.save(out,'PNG')
  else:image.convert('RGB').save(out,'JPEG',quality=85)
 result=out.getvalue();validate_image(result);return result


def prepare(event,cancel=lambda:False,fetch=None,match=None):
 """Worker-only operation; also callable with synthetic transports in tests."""
 from media_sources43 import get,validate_image,SourceError
 from programme_match46 import candidate
 key=event['key'];fp=fingerprint(event);old=persisted(event)
 if old and old.get('until',0)>time.time() and not (old.get('code')=='PROGRAMME_CACHE_BUDGET' and old.get('budget46')!=limit()):remember(key,old);return old
 value=dict(key=key,fingerprint=fp,code='NO_IMAGE',image=event['placeholder'],source='placeholder',match='NONE',until=time.time()+6*3600)
 if old and old.get('source')!='placeholder':value=dict(old,code='READY_STALE',until=time.time()+300)
 try:
  space(3*1024*1024)
  candidates=[dict(url=event[k],source=source,match='EXACT_EVENT',attribution='XMLTV' if source=='xmltv_event' else 'Provider') for k,source in (('xmltv_image','xmltv_event'),('provider_image','provider_event')) if event.get(k)]
  failure=None
  for c in candidates+[None]:
   if cancel():return dict(value,code='CANCELLED')
   if c is None:
    try:c=(match or candidate)(event,cancel=cancel)
    except SourceError as error:failure=error.code;continue
   if not c or not c.get('url'):continue
   try:
    original=(fetch or get)(c['url'],cancel=cancel);original_sha=hashlib.sha256(original).hexdigest();data=display_image(original)
    if cancel():return dict(value,code='CANCELLED')
    space(len(data));digest=hashlib.sha256(data).hexdigest();name=key+'.'+digest[:20]+('.png' if data.startswith(b'\x89PNG') else '.jpg');filename=os.path.join(root(),name)
    if not os.path.isfile(filename):atomic(filename,data)
    value=dict(key=key,fingerprint=fp,code='READY',image=filename,sha256=digest,original_sha256=original_sha,source=c['source'],match=c['match'],attribution=c.get('attribution',''),until=time.time()+86400)
    break
   except SourceError as error:failure=error.code
  if value['code']=='NO_IMAGE' and failure:value.update(code=failure,until=time.time()+300)
 except OSError as error:
  from art_storage import ArtworkFailure
  value.update(code=error.code if isinstance(error,ArtworkFailure) else 'PROGRAMME_CACHE_BUDGET' if isinstance(error,CacheBudget) else 'CACHE_IO_ERROR',until=time.time()+900,budget46=limit())
 # Only fixed classes are reported; never URLs, IDs, tokens or exception text.
 remember(key,value)
 try:
  out=dict(value)
  out['image']=os.path.basename(value['image']) if value.get('source')!='placeholder' else ''
  os.makedirs(root(),mode=0o700,exist_ok=True)
  if not os.path.islink(root()):atomic(os.path.join(root(),key+'.json'),json.dumps(out).encode())
 except OSError:pass
 return value

def run():
 try:
  while not _stop.is_set():
   import service_runtime as runtime
   if runtime.pressure():_wake.wait(.5);_wake.clear();continue
   with _lock:
    pair=_queue.popitem(last=False) if _queue else None
   if pair is None:
    _wake.wait(.5);_wake.clear();continue
   key,event=pair
   try:prepare(event,cancel=_stop.is_set)
   except MemoryError:
    runtime.note_pressure();remember(key,dict(code='MEMORY_PRESSURE',fingerprint=fingerprint(event),image=event['placeholder'],source='placeholder',match='NONE',until=time.time()+300))
   except Exception:remember(key,dict(code='CACHE_ERROR',fingerprint=fingerprint(event),image=event['placeholder'],source='placeholder',match='NONE',until=time.time()+300))
   finally:
    with _lock:_pending.discard(key)
 finally:pass

def shutdown():_stop.set();_wake.set()


def cached(event):
 """Read-only small manifest/stat lookup for Kodi plugin directories, no HTTP.

The producer verified digest/decoder before publication. Workers reverify full
bytes on startup; directory readers never decode 12 full pictures in RAM.
"""
 value=persisted(event,verify=False)
 if value:
  remember(event['key'],value);return value
 return peek(event)

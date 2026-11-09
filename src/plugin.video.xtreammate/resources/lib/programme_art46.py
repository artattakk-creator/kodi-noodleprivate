"""Bounded event-art worker, private persistent cache, no GUI network or writes.

Two workers maximum, 24 waiting events, 128 RAM records, configurable 32/64/128/256 MiB disk ceiling.
Existing cover jobs/files, Kodi textures, artwork mode and guide DB are untouched.
"""
from collections import OrderedDict
import hashlib,json,os,threading,time,tempfile
_lock=threading.Lock();_queue=OrderedDict();_memory=OrderedDict();_pending=set();_workers=[];_stop=threading.Event();_wake=threading.Event()
MAX_DISK=64*1024*1024
_visual_revision47=0

class CacheBudget(OSError):pass

def limit():
 from utils import setting_int
 return (32,64,128,256)[max(0,min(3,setting_int('programme_art_budget46',1)))]*1024*1024

def root():
 from utils import addon_data_dir
 return os.path.join(addon_data_dir(),'programme_images46')

def fingerprint(event):
 values=[event.get(k) for k in ('xmltv_image','provider_image','title','subtitle','year','season','episode','epg_source46')]
 if not event.get('xmltv_image') and not event.get('provider_image'):
  from utils import setting_bool,setting
  enabled=setting_bool('programme_tmdb46',False)
  values.append('tv-artwork66-v1')
  values.append([enabled,setting_bool('tmdb_research43',False) if enabled else False,__import__('tmdb_token61').token_fingerprint() if enabled else ''])
 return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()

def negative_valid77(event,value):
 if not value or value.get('source')!='placeholder':return True
 from programme_policy68 import negative_scope
 return value.get('negative_scope77')==negative_scope(event)

def peek(event):
 with _lock:value=_memory.get(event['key'])
 if not negative_valid77(event,value):value=None
 return {k:v for k,v in value.items() if k not in ('_verified47','_checked47')} if value and value.get('fingerprint')==fingerprint(event) else dict(code='PENDING',image=event['placeholder'],source='placeholder',match='NONE')

def remember(key,value,verified47=False):
 global _visual_revision47
 with _lock:
  old=_memory.get(key,{})
  if verified47 and any(old.get(k)!=value.get(k) for k in ('fingerprint','image','code','source','sha256')):_visual_revision47+=1
  inherited=bool(old.get('_verified47') and all(old.get(k)==value.get(k) for k in ('fingerprint','image','sha256')))
  checked=time.monotonic() if verified47 else old.get('_checked47',0) if inherited else 0
  _memory[key]=dict(value,_verified47=verified47 or inherited,_checked47=checked);_memory.move_to_end(key)
  while len(_memory)>128:_memory.popitem(last=False)

def enqueue(event):
 if not event.get('title') or _stop.is_set():return False
 from utils import setting_bool
 key=event['key'];fp=fingerprint(event)
 with _lock:old=_memory.get(key)
 if old and negative_valid77(event,old) and old.get('fingerprint')==fp and old.get('until',0)>time.time() and (old.get('source')=='placeholder' or old.get('_verified47') and time.monotonic()-old.get('_checked47',0)<300) and not (old.get('code')=='PROGRAMME_CACHE_BUDGET' and old.get('budget46')!=limit()):return False
 if not event.get('xmltv_image') and not event.get('provider_image') and not any(setting_bool(k,d) for k,d in (('programme_tmdb46',False),('programme_tvmaze67',False),('programme_helper57',True),('programme_catalog57',True))):
  from programme_index46 import art as persisted_art46
  prior=persisted_art46(event)
  if prior and prior.get('until',0)>time.time():remember(key,prior);return False
  value=dict(key=event['key'],fingerprint=fingerprint(event),code='NO_IMAGE',image=event['placeholder'],source='placeholder',match='NONE',until=time.time()+21600,negative_scope77=__import__('programme_policy68').negative_scope(event))
  remember(event['key'],value)
  return False
 with _lock:
  old=_memory.get(key)
  if old and negative_valid77(event,old) and old.get('fingerprint')==fp and old.get('until',0)>time.time() and (old.get('source')=='placeholder' or old.get('_verified47') and time.monotonic()-old.get('_checked47',0)<300) and not (old.get('code')=='PROGRAMME_CACHE_BUDGET' and old.get('budget46')!=limit()):return False
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
 from art_storage import check,budget
 from artwork_health82 import guard
 guard()
 # Unlimited additional budget does not require a DB inventory/adoption.
 if budget():
  from art_store import used
  archive_used=used()
 else:archive_used=0
 check(upcoming,used=archive_used+total,location=folder)

def display_image(data):
 """Bounded display derivative, never crops or burns station branding."""
 from media_sources43 import validate_image
 width,height=validate_image(data)
 if width<=1280 and height<=720 and width*9==height*16:return data
 import io
 from PIL import Image
 with Image.open(io.BytesIO(data)) as image:
  format=image.format
  target_width=min(1280,max(160,((width+15)//16)*16));target=(target_width,target_width*9//16)
  image.thumbnail(target,getattr(Image,'Resampling',Image).LANCZOS)
  canvas=Image.new('RGB',target,(18,29,43));canvas.paste(image.convert('RGB'),((target[0]-image.width)//2,(target[1]-image.height)//2));image=canvas
  out=io.BytesIO()
  if format=='PNG':image.save(out,'PNG')
  else:image.convert('RGB').save(out,'JPEG',quality=85)
 result=out.getvalue();validate_image(result);return result


def prepare(event,cancel=lambda:False,fetch=None,match=None,resolved60=None):
 """Worker-only operation; also callable with synthetic transports in tests."""
 from media_sources43 import get,validate_image,SourceError
 from programme_match46 import candidate
 # Worker-only private-file refresh; GUI fingerprint() remains RAM-only.
 if not event.get('xmltv_image') and not event.get('provider_image'):
  from tmdb_token61 import effective_tmdb_read_token,TokenError
  try:effective_tmdb_read_token()
  except TokenError:pass
 key=event['key'];fp=fingerprint(event);old=indexed(event,verify=True) or persisted(event)
 # A URL-only approval is not a stale local picture. The explicit .63
 # materialization lane must report its real download failure, not READY_STALE.
 if resolved60 is not None and resolved60.get('_local_only63') and old and old.get('url_version55')==1:old=None
 if resolved60 is None and old and negative_valid77(event,old) and old.get('until',0)>time.time() and not (old.get('code')=='PROGRAMME_CACHE_BUDGET' and old.get('budget46')!=limit()):remember(key,old,verified47=True);return old
 value=dict(key=key,fingerprint=fp,code='NO_IMAGE',image=event['placeholder'],source='placeholder',match='NONE',until=time.time()+6*3600,negative_scope77=__import__('programme_policy68').negative_scope(event))
 if old and old.get('source')!='placeholder':value=dict(old,code='READY_STALE',until=time.time()+300)
 try:
  candidates=[dict(url=event[k],source=source,match='EXACT_EVENT',attribution='XMLTV' if source=='xmltv_event' else 'Provider') for k,source in (('xmltv_image','xmltv_event'),('provider_image','provider_event')) if event.get(k)]
  failure=None
  if resolved60 is not None:candidates=[resolved60]
  for c in candidates+([None] if resolved60 is None else []):
   if cancel():return dict(value,code='CANCELLED')
   if c is None:
    try:c=(match or candidate)(event,cancel=cancel)
    except SourceError as error:failure=error.code;continue
   if not c or not c.get('url'):continue
   try:
    from programme_index46 import reused
    prior46=reused(c);data=None
    if prior46:
     filename=prior46.get('image','')
     if os.path.dirname(filename)==root() and not os.path.islink(filename):
      try:
       with open(filename,'rb') as stream:data=stream.read(3*1024*1024+1)
       if hashlib.sha256(data).hexdigest()!=prior46.get('sha256'):data=None
       else:validate_image(data)
      except (OSError,SourceError):data=None
    if data is None:
     space(3*1024*1024)
     original=(fetch or get)(c['url'],cancel=cancel);original_sha=hashlib.sha256(original).hexdigest();data=display_image(original)
     from programme_flow48 import trace as evidence66
     evidence66('FETCH',event,'READY')
    else:original_sha=prior46.get('original_sha256',prior46['sha256'])
    if cancel():return dict(value,code='CANCELLED')
    digest=hashlib.sha256(data).hexdigest();name='blob46-'+digest+('.png' if data.startswith(b'\x89PNG') else '.jpg');filename=os.path.join(root(),name)
    if not os.path.isfile(filename):space(len(data));atomic(filename,data)
    reused46=bool(prior46 and prior46.get('sha256')==digest)
    value=dict(key=key,fingerprint=fp,code='READY',image=filename,thumbnail=filename,sha256=digest,original_sha256=original_sha,source=c['source'],source_url=c['url'],provider_id=c.get('remote_id',''),match=c['match'],attribution=c.get('attribution',''),checked46=prior46.get('checked46',time.time()-86400) if reused46 else time.time(),until=min(time.time()+86400,prior46['until']) if reused46 else time.time()+86400)
    for field60 in ('matched_year56','image_scope57'):
     if c.get(field60):value[field60]=c[field60]
    if resolved60 is not None:value['tvspielfilm55']='BLOCKED_NO_AUTHORIZED_API'
    break
   except SourceError as error:
    failure=error.code
    from programme_flow48 import trace as evidence66
    evidence66('FETCH',event,error.code)
  if value['code']=='NO_IMAGE' and failure:value.update(code=failure,until=time.time()+300)
 except OSError as error:
  from art_storage import ArtworkFailure
  value.update(code=error.code if isinstance(error,ArtworkFailure) else 'PROGRAMME_CACHE_BUDGET' if isinstance(error,CacheBudget) else 'CACHE_IO_ERROR',until=time.time()+900,budget46=limit())
  if isinstance(error,ArtworkFailure):
   value['failure_reason68']=error.reason if error.reason in ('BLOCKED_REAL_DISK','RESERVE_BLOCKED','BUDGET_FULL','CAPACITY_UNKNOWN') else 'STORAGE_UNAVAILABLE'
   value['storage68']={k:error.storage[k] for k in ('free','total','reserve','budget') if isinstance(error.storage.get(k),(int,float))}
 if value.get('source')=='placeholder':
  from programme_policy68 import negative_scope
  value['negative_scope68']=negative_scope(event)
 # Only fixed classes are reported; never URLs, IDs, tokens or exception text.
 remember(key,value,verified47=True)
 from programme_flow48 import trace
 trace('IMAGE',event,value['code'])
 from programme_index46 import event as publish_event46,art as publish_art46
 publish_event46(event,write=True)
 saved66=publish_art46(event,value) is not None
 if not saved66:
  # Conservative fallback only when the additive SQLite cache is unavailable;
  # existing old manifests remain readable and are never erased.
  try:
   out=dict(value);out['image']=os.path.basename(value['image']) if value.get('source')!='placeholder' else ''
   os.makedirs(root(),mode=0o700,exist_ok=True)
   if not os.path.islink(root()):
    atomic(os.path.join(root(),key+'.json'),json.dumps(out).encode());saved66=True
  except OSError:pass
 if not saved66:
  value.update(code='CACHE_ERROR',until=time.time()+300)
  remember(key,value,verified47=True)
 trace('CACHE',event,value['code'] if saved66 else 'CACHE_ERROR')
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
 from programme_requests68 import result as shared69
 value=shared69(event)
 if value.get('until',0)>time.time() and value.get('source')!='placeholder' and __import__('programme_image69').eligible(value,event):return value
 display84=__import__('programme_display84').read(event)
 if display84:return display84
 if value.get('until',0)>time.time() and value.get('source')=='placeholder':return value
 value=indexed(event)
 if value:
  value=__import__('programme_image69').adopt(event,value)
  remember(event['key'],value);return value
 value=persisted(event,verify=False)
 if value:
  value=__import__('programme_image69').adopt(event,value)
  remember(event['key'],value);return value
 value=peek(event)
 if value.get('url_version55')==1:
  from programme_urls55 import display
  return display(event,value) or dict(code='URL_EXPIRED',image=event['placeholder'],source='placeholder',match='NONE')
 if value.get('source')!='placeholder' and not os.path.isfile(value.get('image','')):
  with _lock:
   if event['key'] in _memory:_memory[event['key']]['_verified47']=False
  return dict(code='LOCAL_IMAGE_MISSING',image=event['placeholder'],source='placeholder',match='NONE')
 return value


def indexed(event,verify=False):
 from programme_index46 import art as read_art46
 value=read_art46(event)
 if not value:return None
 if value.get('url_version55')==1:
  from programme_urls55 import display
  return display(event,value)
 if value.get('source')=='placeholder':value['image']=event['placeholder'];return value
 try:
  name=value.get('image','')
  if not name or os.path.dirname(name)!=root() or os.path.islink(name) or not os.path.isfile(name) or os.path.getsize(name)>3*1024*1024:return None
  if verify:
   with open(name,'rb') as f:data=f.read(3*1024*1024+1)
   if hashlib.sha256(data).hexdigest()!=value.get('sha256'):return None
   from media_sources43 import validate_image
   validate_image(data)
  return value
 except (OSError,ValueError,TypeError):return None

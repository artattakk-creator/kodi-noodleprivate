"""Manual intents drained by the existing programme worker, no new daemon."""
import hashlib,json,time,uuid,os,threading
_drain_lock89=threading.Lock()
from media_sources43 import SourceError
KEY='XCMate.Work86.Request';RESULT='XCMate.Work86.Result';_seen=''
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def binding(event):
 from programme_display84 import _account
 from epg_handoff63 import profile_scope
 return hashlib.sha256(json.dumps([profile_scope(),_account(event.get('pid')),str(event.get('pid')),str(event.get('sid')),event.get('media_kind86','live'),event.get('title'),event.get('start'),event.get('stop')],sort_keys=True).encode()).hexdigest()
def request(event,operation='search',**options):
 from programme_requests68 import scope
 from programme_requests68 import _FIELDS
 clean={k:event[k] for k in _FIELDS+('genre','year','country','external_ids','description','work_id','original_title','media_kind86') if k in event}
 nonce=uuid.uuid4().hex;value=dict(nonce=nonce,event=clean,binding=binding(clean),scope=scope(),at=time.time(),deadline89=time.monotonic()+30,operation=operation,options=options)
 raw=json.dumps(value,separators=(',',':'))
 if len(raw.encode())>20000:raise ValueError('REQUEST_LIMIT')
 window().setProperty(KEY,raw);__import__('work_trace87').mark(nonce,'ENQUEUED',operation,options.get('source',''));return nonce
def cancelled(nonce):
 try:return json.loads(window().getProperty(KEY) or '{}').get('nonce')!=nonce
 except ValueError:return True
def cancel(nonce):
 if not cancelled(nonce):window().clearProperty(KEY)
def result(nonce):
 try:
  raw=window().getProperty(RESULT);value=json.loads(raw) if raw and len(raw.encode())<65536 else {}
  return value if value.get('nonce')==nonce else None
 except ValueError:return None

def pending():
 """Nonblocking priority signal for the existing service worker only."""
 try:
  raw=window().getProperty(KEY);data=json.loads(raw) if raw and len(raw.encode())<=20000 else {}
  from programme_requests68 import scope
  return bool(isinstance(data.get('nonce'),str) and len(data['nonce'])==32 and data['nonce']!=_seen and isinstance(data.get('event'),dict) and data.get('binding')==binding(data['event']) and data.get('operation') in ('search','save','local') and data.get('scope')==scope() and 0<=time.time()-data.get('at',0)<30)
 except (ValueError,TypeError):return False

def phase(stage):
 __import__('work_trace87').mark(_seen,stage)

def authoritative(event,expected):
 """Search/preview needs no EPG. A save needs a fresh current work scope."""
 from portals import get_by_id
 from library_index import Reader
 portal=get_by_id(str(event.get('pid')))
 if not portal or binding(event)!=expected:raise SourceError('EPG_REVISION_CHANGED')
 kind=event.get('media_kind86','live');reader=Reader(portal['id'])
 row=reader.get(kind,str(event.get('sid')))  # Reader closes each owned query connection.
 if not row:raise SourceError('EPG_REVISION_CHANGED')
 if kind=='live':
  actual=__import__('programme_events46').load(portal,row,event)
  if actual.get('code')!='LOCAL_EVENT' or any(actual.get(k)!=event.get(k) for k in ('title','start','stop')):raise SourceError('EPG_REVISION_CHANGED')
  __import__('programme_mapping85').refresh_sources(portal['id'])
  if any(event.get(k) and event.get(k)!=actual.get(k) for k in ('canonical','epg_source46','source_key46')):raise SourceError('EPG_REVISION_CHANGED')
  return actual
 if row.get('name')!=event.get('title'):raise SourceError('EPG_REVISION_CHANGED')
 return event

def save(event,options,expected,cancel=lambda:False):
 current=authoritative(event,expected)
 kind=event.get('media_kind86','live');action=options.get('action','save')
 if cancel():raise SourceError('CANCELLED')
 if action in ('automatic','hide'):
  if kind!='live':
   if action=='hide':return __import__('media_overrides43').hide86(event['pid'],kind,str(event['sid']))
   return __import__('media_overrides43').reset(event['pid'],kind,str(event['sid']))
  phase('EPG_SCOPE_REVALIDATED')
  mapping90=__import__('programme_mapping85')
  return mapping90.set_mapping(current,automatic=action=='automatic',hidden=action=='hide',cancel=cancel,alias90=mapping90.namespace(event))
 selected=options.get('candidate') or {};phase('CANDIDATE_SELECTED')
 verified=__import__('work_search86').details(selected.get('id'),selected.get('media_type86'),selected.get('source','tmdb'),cancel)
 # Independently fetch again before Save; caller-supplied URLs are never trusted.
 phase('SOURCE_REVERIFIED')
 if verified['year']!=selected.get('year') or verified['title']!=selected.get('title'):raise SourceError('CANDIDATES_REJECTED')
 if cancel():raise SourceError('CANCELLED')
 # Re-read after network, not just the unchanged caller dictionary.
 current=authoritative(event,expected);phase('EPG_SCOPE_REVALIDATED')
 if kind=='live':
  mapping90=__import__('programme_mapping85')
  return mapping90.set_mapping(current,verified,cancel=cancel,operation89=_seen,alias90=mapping90.namespace(event))
 from programme_urls55 import probe,safe
 url=verified.get('poster') or verified['url']
 if not safe(url):raise SourceError('UNSAFE_SOURCE')
 decoded=probe(url,cancel=cancel)
 authoritative(event,expected)
 if cancel():raise SourceError('CANCELLED')
 return __import__('media_overrides43').save(event['pid'],kind,str(event['sid']),image=decoded['_body81'],source=verified['source'],attribution=verified['source'],provenance=dict(media_type=verified['media_type86'],remote_id=verified['id']))

def drain(cancelled_service=lambda:False):
 # One lease in this profile's existing service interpreter; no parallel saves.
 if not _drain_lock89.acquire(False):return
 try:return _drain89(cancelled_service)
 finally:_drain_lock89.release()

def _drain89(cancelled_service=lambda:False):
 global _seen
 from programme_requests68 import scope
 win=window();nonce=None;event={};expired=False
 try:
  raw=win.getProperty(KEY);data=json.loads(raw) if raw and len(raw.encode())<=20000 else {}
  nonce=data.get('nonce');event=data.get('event');options=data.get('options') or {}
  if not isinstance(nonce,str) or len(nonce)!=32 or nonce==_seen or not isinstance(event,dict) or data.get('scope')!=scope() or binding(event)!=data.get('binding') or not 0<=time.time()-data.get('at',0)<30:return
  _seen=nonce;deadline=min(time.monotonic()+max(0,30-(time.time()-data['at'])),data.get('deadline89',time.monotonic()+30))
  def stop():return cancelled_service() or cancelled(nonce) or time.monotonic()>=deadline
  __import__('work_trace87').mark(nonce,'PICKED',data.get('operation',''),options.get('source',''))
  if data.get('operation')=='search':
   value=__import__('work_search86').search(options.get('query'),options.get('kind','tv'),options.get('source','tmdb'),options.get('page',1),stop);phase('SEARCH_READY')
  elif data.get('operation')=='local':value=dict(code='SAVED' if local_save(event,options.get('path',''),data['binding'],stop) else 'UNCHANGED',rows=[])
  elif data.get('operation')=='save':value=dict(code='SAVED' if save(event,options,data['binding'],stop) else 'UNCHANGED',rows=[])
  else:raise SourceError('CANDIDATES_REJECTED')
  if not cancelled_service() and not cancelled(nonce) and time.monotonic()>=deadline and value.get('code')!='SAVED':value=dict(code='NETWORK_TIMEOUT',rows=[])
  # Once a save returned after verified atomic commit, always deliver its receipt.
  # Cancellation is checked before commit; a post-commit cancel cannot undo it.
  if value.get('code') in ('SAVED','NETWORK_TIMEOUT') or not stop():
   if value.get('code')=='SAVED':phase('WRITE_READBACK')
   if value.get('code')=='SAVED' and event.get('media_kind86') in ('vod','series'):
    win.setProperty(manual_slot(event['pid'],event['media_kind86']),nonce)
   win.setProperty(RESULT,json.dumps(dict(value,nonce=nonce,binding=data['binding']),separators=(',',':')))
   __import__('work_trace87').mark(nonce,'DELIVERED')
 except (SourceError,OSError,TimeoutError,ValueError,TypeError,AttributeError) as error:
  __import__('art_trace81').note(event or {},'MATCH_REJECTED',getattr(error,'code','SAVE_BLOCKED'))
  code=getattr(error,'code','PERSISTENCE_BLOCKED' if isinstance(error,OSError) else 'CANDIDATES_REJECTED')
  if isinstance(error,OSError) and str(error)=='MANUAL_READBACK':code='READBACK_FAILED'
  if isinstance(error,TimeoutError) or code in ('TIMEOUT','HTTP_TIMEOUT') or code=='CANCELLED' and time.monotonic()>=locals().get('deadline',float('inf')):code='NETWORK_TIMEOUT'
  if code in ('DISK_FULL','SPACE_FULL','DB_BUSY','XM-ARTWORK-DB-PAUSED'):code='PERSISTENCE_BLOCKED'
  if code in ('RESEARCH_BUSY','WORKER_QUEUE_FULL'):code='WORKER_BUSY'
  if nonce and not cancelled(nonce):win.setProperty(RESULT,json.dumps(dict(nonce=nonce,code=code,rows=[])))


def local_save(event,path,expected,cancel=lambda:False):
 from pathlib import Path
 from media_sources43 import validate_image,MAX_IMAGE
 from art_storage import check
 from programme_art46 import image_root87 as root,atomic
 current=authoritative(event,expected)
 # Read exactly the explicitly selected image, never enumerate a share.
 if path.startswith('smb://'):
  import xbmcvfs
  before=xbmcvfs.Stat(path);size=before.st_size()
  if not 0<size<=MAX_IMAGE:raise SourceError('IMAGE_LIMIT')
  handle=xbmcvfs.File(path,'rb')
  try:body=bytes(handle.readBytes(MAX_IMAGE+1))
  finally:handle.close()
  after=xbmcvfs.Stat(path)
  if len(body)!=size or size!=after.st_size() or before.st_mtime()!=after.st_mtime():raise SourceError('CANDIDATES_REJECTED')
 elif path.startswith('https://'):
  from programme_urls55 import safe,probe
  if not safe(path):raise SourceError('UNSAFE_SOURCE')
  body=probe(path,cancel=cancel)['_body81']
 else:
  file=Path(path)
  if not file.is_absolute() or file.is_symlink() or not file.is_file() or not 0<file.stat().st_size<=MAX_IMAGE:raise SourceError('UNSAFE_SOURCE')
  before=file.stat();body=file.read_bytes();after=file.stat()
  if (before.st_ino,before.st_mtime_ns,before.st_size)!=(after.st_ino,after.st_mtime_ns,after.st_size):raise SourceError('CANDIDATES_REJECTED')
 width,height=validate_image(body)
 if cancel():raise SourceError('CANCELLED')
 kind=event.get('media_kind86','live')
 if kind!='live':return __import__('media_overrides43').save(event['pid'],kind,str(event['sid']),image=body,source='user_local')
 folder=root();check(len(body)+65536,location=folder)
 os.makedirs(folder,mode=0o700,exist_ok=True)
 if os.path.islink(folder):raise SourceError('UNSAFE_SOURCE')
 digest=hashlib.sha256(body).hexdigest();target=os.path.join(folder,'user86-'+digest+('.png' if body.startswith(b'\x89PNG') else '.jpg'))
 if os.path.islink(target):raise SourceError('UNSAFE_SOURCE')
 if not os.path.exists(target):atomic(target,body)
 with open(target,'rb') as stream:
  if hashlib.sha256(stream.read(MAX_IMAGE+1)).hexdigest()!=digest:raise SourceError('CANDIDATES_REJECTED')
 authoritative(event,expected)
 mapping90=__import__('programme_mapping85')
 return mapping90.set_mapping(current,dict(source='user_local86',id=1,verified85=True,local86=dict(image=target,sha256=digest,width=width,height=height),media_type86='image'),cancel=cancel,alias90=mapping90.namespace(event))

def local_result(event):
 mapping=__import__('programme_mapping85').current(event)
 if not mapping or mapping.get('source')!='user_local86':return None
 from programme_art46 import root,fingerprint
 from media_sources43 import validate_image,MAX_IMAGE
 record=mapping.get('local86') or {};path=record.get('image','')
 if os.path.dirname(path) not in (root(),__import__('programme_art46').image_root87()) or os.path.islink(path):return None
 try:
  with open(path,'rb') as stream:body=stream.read(MAX_IMAGE+1)
  if hashlib.sha256(body).hexdigest()!=record.get('sha256'):return None
  width,height=validate_image(body)
  from programme_requests68 import identity,scope
  return dict(key=event['key'],code='READY',source='user_local86',match='MANUAL_CONFIRMED',image=path,thumbnail=path,sha256=record['sha256'],role81='poster' if height>width else 'backdrop',image_width77=width,image_height77=height,fingerprint=fingerprint(event),scope69=identity(event),profile69=scope(),until=time.time()+86400,mapping_epoch85=__import__('programme_mapping85').epoch(event),attribution='Eigenes Bild · ausdrückliche Benutzerzuordnung')
 except (OSError,ValueError,SourceError):return None


def manual_slot(pid,kind):
 from epg_handoff63 import profile_scope
 return 'XCMate.ManualArtwork86.'+hashlib.sha256((profile_scope()+'|'+str(pid)+'|'+kind).encode()).hexdigest()

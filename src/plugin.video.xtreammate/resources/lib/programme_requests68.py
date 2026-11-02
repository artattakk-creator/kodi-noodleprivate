"""Bounded cross-interpreter visible-event intents, consumed by the service.

UI writers/readers only exchange small Home properties. The singleton service
alone reloads authoritative local event facts and uses the existing URL queue.
No provider URLs, tokens, SQL, files or HTTP in request()/result().
"""
import hashlib,json,threading,time
PREFIX='XCMate.Programme68.'
SLOTS=64
MAX_BYTES=8192
_FIELDS=('pid','sid','start','stop','title','canonical','revision','source_key46','fact_revision46','epg_source46')
_ART=('key','fingerprint','code','source','match','image','thumbnail','sha256','attribution','image_scope57','until','failure_reason68','storage68')
_lock=threading.Lock()
_thread=None
_stop=threading.Event()
_seen={}
_aliases={}
_cursor=0
_traces={}

def scope():
 from epg_handoff63 import profile_scope
 return profile_scope()

def identity(event):
 values=[scope()]+[event.get(k) for k in _FIELDS]
 return hashlib.sha256(json.dumps(values,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def _window():
 import xbmcgui
 return xbmcgui.Window(10000)

def _read(key):
 raw=_window().getProperty(PREFIX+key)
 if not raw or len(raw.encode())>MAX_BYTES:return {}
 try:value=json.loads(raw)
 except (ValueError,TypeError):return {}
 return value if isinstance(value,dict) else {}

def request(event,priority=False):
 """A bounded intent only; callers already possess the displayed local event."""
 try:
  if not event.get('pid') or not event.get('sid') or not event.get('title'):return False
  if not 0<int(event['start'])<int(event['stop']):return False
  value={k:event[k] for k in _FIELDS if k in event}
  if any(isinstance(v,str) and len(v)>1024 for v in value.values()):return False
  tag=identity(value);slot=str(int(tag[:8],16)%SLOTS)
  record=dict(event=value,tag=tag,scope=scope(),at=int(time.time()//5)*5,priority=bool(priority))
  raw=json.dumps(record,separators=(',',':'),allow_nan=False)
  if len(raw.encode())>MAX_BYTES:return False
  marker=_window();key=PREFIX+'request.'+slot
  if marker.getProperty(key)!=raw:marker.setProperty(key,raw)
  return True
 except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,KeyError,OverflowError):return False

def trace(event,code):
 codes={'QUEUED','RUNNING','LOCAL_IMAGE_READY','IMAGE_READY','NOT_SCHEDULED','NO_MATCH','NO_ARTWORK','CACHE_MISS','CACHE_MISMATCH','DB_FULL','FETCH_FAILED','CANCELLED','HTTP_AUTH','HTTP_RATE_LIMIT','TIMEOUT','PROGRAMME_DB_UNAVAILABLE','CACHE_ERROR','CACHE_IO_ERROR','PROGRAMME_CACHE_BUDGET','TMDB_DISABLED','TMDB_TOKEN_MISSING','BLOCKED_IMAGE_HOST_OR_URL','NO_MATCH_AMBIGUOUS','HELPER_TIMEOUT','HELPER_BACKGROUND_UNAVAILABLE','NO_UNIQUE_MATCH','NO_IMAGE','NO_YEAR','NOT_CLASSIFIED_MOVIE','AWAITING_BACKGROUND_REFRESH','RESERVE_BLOCKED','DISK_FULL','BUDGET_FULL'}
 fixed=code if code in codes else 'FETCH_FAILED'
 key=(identity(event),fixed);now=time.monotonic()
 with _lock:
  if now-_traces.get(key,-1e9)<60:return
  _traces[key]=now
  while len(_traces)>256:_traces.pop(next(iter(_traces)))
 import xbmc
 try:xbmc.log('[XCMate][PROGRAMME68] event='+key[0][:12]+' code='+fixed,xbmc.LOGINFO)
 except (AttributeError,RuntimeError):pass

def status(event,code,art=None):
 """Producer-only publication. Never publish URL credentials or raw errors."""
 try:
  trace(event,code)
  tags=[identity(event)]
  with _lock:tags+=list(_aliases.get(tags[0],()))
  payload={k:art[k] for k in _ART if art and k in art}
  for tag in set(tags):
   value=dict(tag=tag,scope=scope(),at=time.time(),code=code,art=payload)
   raw=json.dumps(value,separators=(',',':'),allow_nan=False)
   if len(raw.encode())<=MAX_BYTES:_window().setProperty(PREFIX+'status.'+str(int(tag[:8],16)%SLOTS),raw)
 except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,KeyError):pass

def result(event,previous=None):
 """UI-safe status/art, bound to exact profile, event and source revision."""
 try:
  tag=identity(event);value=_read('status.'+str(int(tag[:8],16)%SLOTS))
  if value.get('tag')!=tag or value.get('scope')!=scope() or not 0<=time.time()-float(value.get('at',0))<300:return previous or {}
  art=value.get('art') or {}
  if art.get('code') in ('READY','READY_STALE') and art.get('source') not in (None,'','placeholder') and art.get('image'):
   if art.get('until',0)<=time.time():return dict(code='CACHE_MISMATCH',source='placeholder')
   return dict(art,status68=value['code'])
  return dict(previous or {},**{k:art[k] for k in ('failure_reason68','storage68') if k in art},code=value['code'],status68=value['code'])
 except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,KeyError):return previous or {}

def completed(event,value):
 if value is None:status(event,'CANCELLED');return
 code=value.get('code','FETCH_FAILED')
 if code in ('READY','READY_STALE') and value.get('source')!='placeholder':
  import os
  code='LOCAL_IMAGE_READY' if os.path.isabs(value.get('image','')) and not value.get('url_version55') else 'IMAGE_READY'
 elif code=='PROGRAMME_DATA_BUDGET':code='DB_FULL'
 elif code=='DISK_FULL' and value.get('failure_reason68')=='RESERVE_BLOCKED':code='RESERVE_BLOCKED'
 status(event,code,value)

def mark_seen(tag,policy,now):
 with _lock:
  _seen[(tag,policy)]=now
  while len(_seen)>256:_seen.pop(next(iter(_seen)))

def drain(cancel=lambda:False):
 """Worker-only bounded intake, fair cyclic slots and authoritative re-read."""
 global _cursor
 from programme_urls55 import enqueue
 from programme_events46 import load
 from portals import get_by_id
 from library_index import Reader
 processed=0
 for offset in range(SLOTS):
  slot=(_cursor+offset)%SLOTS
  if cancel():break
  try:
   value=_read('request.'+str(slot));event=value.get('event')
   if not isinstance(event,dict) or value.get('scope')!=scope() or value.get('tag')!=identity(event):continue
   if not 0<=time.time()-float(value.get('at',0))<20:continue
   portal=get_by_id(str(event.get('pid','')))
   if not portal or not portal.get('enabled',True) or not portal.get('include_live',True):continue
   # Token refresh/file access is deliberately in this worker, never focus.
   from programme_art46 import fingerprint
   from tmdb_token61 import effective_tmdb_read_token,TokenError
   try:effective_tmdb_read_token()
   except TokenError:pass
   policy=fingerprint(event);tag=value['tag'];now=time.monotonic()
   with _lock:prior=_seen.get((tag,policy),-1e9)
   if now-prior<10:continue
   reader=Reader(portal['id'])
   try:channel=reader.get('live',str(event.get('sid','')))
   finally:
    close=getattr(reader,'close',None)
    if close:close()
   if not channel:
    status(event,'CACHE_MISS')
    mark_seen(tag,policy,now)
    continue
   current=load(portal,channel,event)
   # No cached-short fallback may override an explicit source/guide binding.
   if current.get('code')!='LOCAL_EVENT' or any(event.get(k) and event.get(k)!=current.get(k) for k in ('canonical','source_key46','fact_revision46')) or event.get('revision') is not None and json.dumps(event['revision'])!=json.dumps(current.get('revision')):
    status(event,'CACHE_MISMATCH')
    mark_seen(tag,policy,now)
    continue
   with _lock:
    aliases=_aliases.setdefault(identity(current),set());aliases.add(tag)
    while len(_aliases)>128:_aliases.pop(next(iter(_aliases)))
   from utils import setting_bool
   own=setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False)
   allow=own or setting_bool('programme_tvmaze67',False) or setting_bool('programme_helper57',True) or setting_bool('programme_catalog57',True)
   if not allow and not current.get('xmltv_image') and not current.get('provider_image'):
    status(current,'TMDB_LOOKUP_DISABLED')
    mark_seen(tag,policy,now)
    continue
   accepted=enqueue(current,allow_lookup=allow,local_image63=True,priority68=bool(value.get('priority')))
   mark_seen(tag,policy,now if accepted else now-8)
   processed+=1
   if processed>=9:_cursor=(slot+1)%SLOTS;break
  except Exception:
   # Keep private exceptions out of properties and public logs.
   if isinstance(locals().get('event'),dict):status(event,'FETCH_FAILED')
 else:_cursor=(_cursor+9)%SLOTS
 return processed

def _run():
 import xbmc
 monitor=xbmc.Monitor()
 while not _stop.is_set() and not monitor.abortRequested():
  try:
   from startup48 import suspended
   import service_runtime as runtime
   if suspended() or runtime.pressure():
    if monitor.waitForAbort(.5):break
    continue
   from live_warm68 import prepare
   prepare(lambda:_stop.is_set() or monitor.abortRequested())
   drain(lambda:_stop.is_set() or monitor.abortRequested())
  except Exception:pass
  if monitor.waitForAbort(.2):break

def poll():
 """Only called by the already leased service; never by a plugin GUI."""
 global _thread
 if _stop.is_set():return
 import xbmc
 monitor=xbmc.Monitor()
 if not all(callable(getattr(monitor,name,None)) for name in ('abortRequested','waitForAbort')):return
 with _lock:
  if _thread is None or not _thread.is_alive():
   _thread=threading.Thread(target=_run,name='XCMate-visible-programme68',daemon=True);_thread.start()

def shutdown():
 _stop.set()

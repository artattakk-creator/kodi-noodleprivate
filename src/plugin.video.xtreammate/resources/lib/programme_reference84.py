"""Small reference-only production cache on the existing programme worker.

Import signals contain no programme/URL data. Bounded scans enqueue metadata
work; no image body is fetched here. Existing images and Kodi caches untouched.
"""
import hashlib,json,os,time,threading
from collections import OrderedDict
from pathlib import Path
_lock=threading.RLock();_works=OrderedDict();_scans={};_due=0.;_flush=0.;_loaded=set()
MAX_RECORDS=256;MAX_BYTES=512*1024
PREFIX='XCMate.Reference84.Import.'

def context(pid):
 from programme_policy68 import negative_scope
 from programme_display84 import _account
 from utils import setting_bool
 flags=[setting_bool(k,False) for k in ('programme_tmdb_optout77','programme_tvmaze_optout77')]
 return hashlib.sha256((negative_scope({})+_account(pid)+json.dumps(flags)).encode()).hexdigest()

def work_key(event):
 from programme_title80 import key
 facts=[key(str(event.get('title') or '')),event.get('year'),event.get('season'),event.get('episode'),event.get('subtitle'),event.get('genre')]
 return hashlib.sha256(json.dumps([context(event.get('pid')),facts],sort_keys=True).encode()).hexdigest()

def path():
 from utils import addon_data_dir
 return Path(addon_data_dir())/'programme_references84.json'

def load():
 filename=path()
 with _lock:
  if str(filename) in _loaded:return
  _loaded.add(str(filename))
  while len(_loaded)>8:_loaded.pop()
 try:
  if filename.is_symlink() or filename.stat().st_size>MAX_BYTES:return
  data=json.loads(filename.read_bytes())
  if not isinstance(data,dict) or data.get('version')!=1:return
  with _lock:
   for key,value in list(data.get('works',{}).items())[-MAX_RECORDS:]:
    if isinstance(key,str) and len(key)==64 and isinstance(value,dict) and time.time()<value.get('until',0)<=time.time()+86400:_works[key]=value
 except (OSError,ValueError,TypeError,AttributeError):return

def get(event):
 load();key=work_key(event)
 with _lock:
  value=_works.get(key)
  if value and time.time()<value.get('until',0):_works.move_to_end(key);return dict(value)
 return None

def put(event,candidate):
 # Persist only safe public metadata, never title text, API bodies or images.
 from widget_assets69 import safe
 from portals import get_by_id
 portal=get_by_id(str(event.get('pid'))) or {}
 if candidate and (not portal or not safe(portal,candidate.get('url'))):return None
 allowed=('url','source','match','remote_id','provider_id','attribution','image_scope57','role81','matched_year56')
 value=dict(candidate={k:candidate[k] for k in allowed if k in candidate} if candidate else None,until=time.time()+(86400 if candidate else 3600))
 with _lock:
  _works[work_key(event)]=value
  while len(_works)>MAX_RECORDS or len(json.dumps(_works).encode())>MAX_BYTES-128:_works.popitem(last=False)
 return value

def resolve(event,cancel=lambda:False):
 prior=get(event)
 if prior is not None:return prior
 if cancel():return None
 # Exact feed icons are already registered in authoritative local metadata;
 # they need no production/title search or image HTTP in this stage.
 from image_reference78 import canonical
 for field,source in (('xmltv_image','xmltv_event'),('provider_image','provider_event')):
  url=canonical(event.get(field))
  if url:return dict(candidate=dict(url=url,source=source,match='EXACT_EVENT'),until=time.time()+300)
 from programme_sources57 import unsuitable69
 if unsuitable69(event):return put(event,None)
 from programme_match46 import candidate
 from programme_tvmaze67 import candidate as maze
 from art_trace81 import own
 value=own(event,lambda:candidate(event,cancel))
 if not value and not cancel():value=maze(event,cancel)
 return put(event,value)

def signal(pid,generation):
 import xbmcgui
 from epg_handoff63 import profile_scope
 key=hashlib.sha256((profile_scope()+str(pid)).encode()).hexdigest()
 xbmcgui.Window(10000).setProperty(PREFIX+key,str(generation)[:128])

def flush():
 global _flush
 if time.monotonic()<_flush:return
 _flush=time.monotonic()+60
 from artwork_display84 import metadata_allowed
 if not metadata_allowed():return
 from import_budget import check_space
 from profile_transaction import writing
 import tempfile
 filename=path()
 with _lock:
  for key in list(_works):
   if _works[key].get('until',0)<=time.time():_works.pop(key,None)
  raw=json.dumps(dict(version=1,works=_works),separators=(',',':')).encode()
 if len(raw)>MAX_BYTES:return
 with writing(timeout=.1):
  check_space(str(filename),len(raw)+65536)
  if filename.is_symlink():return
  fd,temp=tempfile.mkstemp(prefix='.reference84-',dir=filename.parent)
  try:
   with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
   os.replace(temp,filename)
  finally:
   if os.path.exists(temp):os.unlink(temp)

def tick(cancel=lambda:False):
 """Existing service thread. At most sixteen metadata jobs/minute, resumable RAM cursor.

 A new source generation invalidates the cursor; old cached works remain
 policy/account scoped. No entire-guide scan on every Kodi startup.
 """
 global _due
 if time.monotonic()<_due or cancel():return
 _due=time.monotonic()+15
 import xbmcgui,sqlite3
 from epg_handoff63 import profile_scope
 from portals import get_active
 from programme_index46 import connect
 from programme_urls55 import enqueue
 for portal in get_active()[:4]:
  tag=hashlib.sha256((profile_scope()+str(portal['id'])).encode()).hexdigest();generation=xbmcgui.Window(10000).getProperty(PREFIX+tag)
  if not generation:continue
  key=(context(portal['id']),portal['id'],generation);cursor,done=_scans.get(key,(0,False))
  if done:continue
  db=None
  try:
   db=connect(False)
   if db is None:continue
   deadline=time.monotonic()+.02;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
   rows=db.execute('SELECT rowid,data FROM facts WHERE pid=? AND rowid>? AND stop>? ORDER BY rowid LIMIT 4',(str(portal['id']),cursor,time.time())).fetchall()
   for rowid,raw in rows:
    if cancel():return
    fact=json.loads(raw);event=dict(fact,pid=str(portal['id']),sid='reference:'+str(fact.get('channel','')),start=int(fact['start_timestamp']),stop=int(fact['stop_timestamp']),canonical=str(fact.get('channel','')),revision=generation)
    event['key']=__import__('programme_events46').key(event['pid'],event['sid'],event);event['placeholder']=''
    if not enqueue(event,allow_lookup=True,reference_only84=True):break
    cursor=rowid
   else:done=not rows
   _scans[key]=(cursor,done)
   while len(_scans)>16:_scans.pop(next(iter(_scans)))
  except (OSError,sqlite3.Error,ValueError,TypeError,KeyError):pass
  finally:
   if db is not None:db.close()
 try:flush()
 except (OSError,TimeoutError,ValueError):pass

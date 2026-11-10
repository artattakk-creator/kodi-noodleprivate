"""Volatile public provider references; no programme DB writes or image archive."""
from collections import OrderedDict
import hashlib,json,queue,threading,time,sqlite3
from urllib.parse import urlsplit,unquote
_lock=threading.RLock();_queue=queue.Queue(maxsize=16);_pending=set();_thread=None;_stop=threading.Event();_revision=0
_deferred82={};_local_due82={};_lease_keys82={};_fatal82=False
_cursor84={}
PREFIX='XCMate.WidgetAsset69.'
def profile():
 from epg_handoff63 import profile_scope
 return profile_scope()
def identity(portal,kind,row,role,source):
 values=[profile(),str(portal['id']),kind,str(row['sid']),role,source,[portal.get(k) for k in ('type','xc_host','xc_user','xc_pass')]]
 return hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest()
def safe(portal,uri):
 from artwork_visible import syntactic
 if not syntactic(uri):return False
 try:
  parts=urlsplit(uri)
  if parts.scheme!='https' or parts.port not in (None,443) or not __import__('programme_url77').public_query(parts.query) or parts.fragment:return False
  path=unquote(parts.path)
  return not any(v and (v in path.split('/') or len(v)>=4 and v in path) for v in (str(portal.get('xc_user') or ''),str(portal.get('xc_pass') or '')))
 except (ValueError,TypeError):return False
def _window():
 import xbmcgui
 return xbmcgui.Window(10000)
def _slot(key):return PREFIX+key
def read(portal,kind,rows):
 from artwork_config import persistent
 persistent84=persistent()
 from artwork_display84 import enabled
 remote84=not persistent84 or enabled() or __import__('home_schedule75').applicable()
 from programme_assets47 import sources
 if kind=='live':from station_logos87 import sources
 from artwork_visible import KODI_OPTIONS
 from widget_refs74 import read as retained74
 result=retained74(portal,kind,rows) if not persistent84 else {}
 from widget_cache79 import read as local79
 for sid79,roles79 in local79(portal,kind,rows).items():result.setdefault(sid79,{}).update(roles79)
 for row in rows[:256]:
  for role,source in sources(row,provider_only=True).items():
   from widget_refs74 import revoked
   if not remote84 or not safe(portal,source) or revoked(source):continue
   key=identity(portal,kind,row,role,source)
   try:
    raw=_window().getProperty(_slot(key));value=json.loads(raw) if raw and len(raw)<4096 else {}
    remaining=value.get('until',0)-time.time()
    if value.get('key')==key and value.get('profile')==profile() and 0<remaining<=30 and value.get('uri')==source+KODI_OPTIONS:
     result.setdefault(str(row['sid']),{}).setdefault(role,value['uri'])
   except (ValueError,TypeError,AttributeError,RuntimeError):continue
 from widget_cache82 import read as local82
 for sid82,roles82 in local82(portal,kind,rows).items():result.setdefault(sid82,{}).update(roles82)
 from render_cache81 import references
 for sid81,roles81 in references(portal,kind,rows).items():result.setdefault(sid81,{}).update(roles81)
 return result
def prepare(portal,kind,rows,cancel=lambda:False):
 global _thread
 if kind in ('vod','series'):rows=[row for row in rows if not row.get('_no_art86')]
 if not rows:return False
 from home_schedule75 import allowed,focused_rows
 if not allowed(kind,portal):rows=focused_rows(portal,kind,rows)
 from artwork_config import persistent
 if _fatal82 or _stop.is_set() or not rows or kind not in ('live','vod','series'):return False
 from programme_assets47 import sources
 if kind=='live':from station_logos87 import sources
 if kind=='live':
  head85=__import__('programme_prefetch48').visible75(portal,rows);ids85={str(r['sid']) for r in head85};rows=head85+[r for r in rows if str(r['sid']) not in ids85]
 if kind in ('vod','series') and __import__('home_schedule75').applicable():rows=__import__('home_loading85').visible(portal,kind,rows)
 selected=[dict(row) for row in rows[:256 if kind=='live' else 24]]
 material=[[str(r['sid']),sources(r,provider_only=True)] for r in selected]
 key=hashlib.sha256(json.dumps([profile(),portal['id'],kind,material],sort_keys=True).encode()).hexdigest()
 with _lock:
  if key in _pending:return False
  try:_queue.put_nowait((key,dict(portal),kind,selected))
  except queue.Full:return False
  _pending.add(key)
  if _thread is None or not _thread.is_alive():
   _thread=threading.Thread(target=_run,name='XCMate-provider-art69',daemon=True);_thread.start()
 return True
def _references82(portal,kind,rows):
 global _revision
 from artwork_config import persistent
 from artwork_display84 import enabled,note
 if persistent() and not enabled() and not __import__('home_schedule75').applicable():return
 from artwork_visible import public_dns,KODI_OPTIONS
 from programme_assets47 import sources
 if kind=='live':from station_logos87 import sources
 initial=profile();end=time.monotonic()+.5;retained74=[]
 if kind=='live':
  from programme_prefetch48 import visible75
  visible84=visible75(portal,rows);visible_ids84={str(r['sid']) for r in visible84}
  ordered84=visible84+[r for r in rows if str(r['sid']) not in visible_ids84]
 else:ordered84=list(rows)
 context84=hashlib.sha256(json.dumps([initial,portal.get('id'),portal.get('xc_user'),portal.get('xc_pass'),kind,[[r['sid'],sources(r,provider_only=True)] for r in ordered84]],sort_keys=True).encode()).hexdigest()
 start84=_cursor84.get(context84,0)%max(1,len(ordered84));stop84=min(5,len(ordered84)) if kind=='live' and start84<5 else len(ordered84)
 processed84=0;missing84=blocked84=dns84=0
 for row in ordered84[start84:stop84]:
  if _stop.is_set() or profile()!=initial or time.monotonic()>end:break
  processed84+=1
  for role,source in sources(row,provider_only=True).items():
   if not source:missing84+=1;continue
   if not safe(portal,source):
    blocked84+=1
    if kind=='live' and not __import__('station_logos88').network_safe(portal,source):__import__('station_logos87').note(portal,row,__import__('station_logos87').blocked_reason(portal,source))
    continue
   if not public_dns(source):
    dns84+=1
    if kind=='live':__import__('station_logos87').note(portal,row,'LEASE_PENDING')
    continue
   from artwork_visible import _dns_cache,_lock as dns_lock
   parts=urlsplit(source)
   with dns_lock:lease=_dns_cache.get((parts.hostname,443))
   remaining=min(30,max(0,lease[0]-time.monotonic())) if lease and lease[1] else 0
   if not remaining:continue
   tag=identity(portal,kind,row,role,source);window=_window();prior=window.getProperty(_slot(tag))
   value=dict(key=tag,profile=initial,uri=source+KODI_OPTIONS,until=time.time()+remaining)
   try:old=json.loads(prior) if prior else {}
   except ValueError:old={}
   window.setProperty(_slot(tag),json.dumps(value,separators=(',',':')))
   with _lock:
    _lease_keys82.pop(tag,None);_lease_keys82[tag]=True
    while len(_lease_keys82)>4096:
     oldest=next(iter(_lease_keys82));_lease_keys82.pop(oldest);window.clearProperty(_slot(oldest))
   retained74.append((row['sid'],role,source,remaining))
   if old.get('key')!=tag or old.get('uri')!=value['uri']:
    with _lock:_revision+=1
 from widget_refs74 import remember_many
 remember_many(portal,kind,retained74)
 _cursor84[context84]=(start84+processed84)%max(1,len(ordered84))
 while len(_cursor84)>32:_cursor84.pop(next(iter(_cursor84)))
 if retained74:note(kind,'URL_APPROVED',count=len(retained74))
 if missing84:note(kind,'SOURCE_MISSING',count=missing84)
 if blocked84:note(kind,'SOURCE_BLOCKED',count=blocked84)
 if dns84:note(kind,'DNS_UNAVAILABLE',count=dns84)

def _run():
 global _fatal82
 from artwork_health82 import Deferred,defer,note,status,guard
 import xbmc
 aborted=getattr(xbmc.Monitor(),'abortRequested',lambda:False)
 cancelled=lambda:_stop.is_set() or aborted()
 while not cancelled():
  job=None;queued=False;local_only=False;now=time.time()
  for tag,(until,code,candidate) in list(_deferred82.items()):
   released=code in ('DB_PAUSED','DB_MANUAL_PAUSE') and status()['code']=='READY'
   if now>=until or released:
    job=candidate;_deferred82.pop(tag,None);break
   if now>=_local_due82.get(tag,0):
    job=candidate;local_only=True;_local_due82[tag]=now+2;break
  if job is None:
   try:job=_queue.get(timeout=.5);queued=True
   except queue.Empty:continue
  key,portal,kind,rows=job;deferred=local_only
  try:
   # Independent logo manifest remains useful in Dynamic mode and DB pauses.
   if kind=='live':
    # Approve safe public references and recover decoded Kodi files before
    # optional persistent archive writes, which may be reserve-blocked.
    _references82(portal,kind,rows)
    __import__('station_logos87').recover(portal,rows,cancelled)
    __import__('logo_manifest86').prepare(portal,rows,cancelled)
   # Recover already decoded Kodi files before any optional image write.
   __import__('artwork_display84').observe()
   __import__('widget_cache82').prepare(portal,kind,rows)
   if kind!='live':_references82(portal,kind,rows)
   if __import__('home_schedule75').applicable():__import__('render_temp85').prepare(portal,kind,rows,cancelled)
   if local_only:continue
   guard()
   __import__('render_cache81').prepare(portal,kind,rows,cancelled)
   __import__('media_hero81').prepare(portal,kind,rows,cancelled)
   note('RECOVERED',pending=len(_pending))
  except (sqlite3.Error,OSError) as error:
   pause=defer(error)
   if len(_deferred82)<16 or key in _deferred82:
    _deferred82[key]=(pause.retry_at82,pause.code82,job);_local_due82[key]=now+2;deferred=True
   note(pause.code82,reason=pause.reason82,until=pause.retry_at82,pending=len(_pending))
  except Exception as error:
   # Unexpected bugs/MemoryError are fatal, never reported as successful work.
   # Latch prevents a new fatal daemon on every service poll.
   _fatal82=True;note('FATAL',reason='MEMORY_ERROR' if isinstance(error,MemoryError) else 'PROGRAMMING_ERROR',alive=False,pending=len(_pending));return
  finally:
   if queued:_queue.task_done()
   if not deferred:
    _local_due82.pop(key,None)
    with _lock:_pending.discard(key)

 note('STOPPED',alive=False,pending=len(_pending))

def revision():
 with _lock:return _revision
def renderable(uri):
 if not isinstance(uri,str) or not uri:return False
 return not any(uri.replace('\\','/').endswith('/resources/media/'+name) for name in ('vod.png','series.png','tv.png')) and '/resources/media/programme46/' not in uri
def shutdown():
 _stop.set()
 __import__('decoded_assets88').shutdown()

def home():
 try:
  import xbmc,xbmcgui
  return xbmc.getSkinDir()=='skin.titan.bingie.mod' and xbmcgui.getCurrentWindowId()==10000
 except (AttributeError,RuntimeError):return False

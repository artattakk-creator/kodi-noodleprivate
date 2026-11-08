"""Volatile public provider references; no programme DB writes or image archive."""
from collections import OrderedDict
import hashlib,json,queue,threading,time
from urllib.parse import urlsplit,unquote
_lock=threading.RLock();_queue=queue.Queue(maxsize=16);_pending=set();_thread=None;_stop=threading.Event();_revision=0
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
def _slot(key):return PREFIX+str(int(key[:8],16)%512)
def read(portal,kind,rows):
 from artwork_config import persistent
 if persistent():return {}
 from programme_assets47 import sources
 from artwork_visible import KODI_OPTIONS
 from widget_refs74 import read as retained74
 result=retained74(portal,kind,rows)
 from widget_cache79 import read as local79
 for sid79,roles79 in local79(portal,kind,rows).items():result.setdefault(sid79,{}).update(roles79)
 for row in rows[:256]:
  for role,source in sources(row,provider_only=True).items():
   from widget_refs74 import revoked
   if not safe(portal,source) or revoked(source):continue
   key=identity(portal,kind,row,role,source)
   try:
    raw=_window().getProperty(_slot(key));value=json.loads(raw) if raw and len(raw)<4096 else {}
    remaining=value.get('until',0)-time.time()
    if value.get('key')==key and value.get('profile')==profile() and 0<remaining<=30 and value.get('uri')==source+KODI_OPTIONS:
     result.setdefault(str(row['sid']),{}).setdefault(role,value['uri'])
   except (ValueError,TypeError,AttributeError,RuntimeError):continue
 from render_cache81 import references
 for sid81,roles81 in references(portal,kind,rows).items():result.setdefault(sid81,{}).update(roles81)
 return result
def prepare(portal,kind,rows,cancel=lambda:False):
 global _thread
 if not rows:return False
 from home_schedule75 import allowed,focused_rows
 if not allowed(kind,portal):rows=focused_rows(portal,kind,rows)
 from artwork_config import persistent
 if persistent() or _stop.is_set() or not rows or kind not in ('live','vod','series'):return False
 from programme_assets47 import sources
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
def _run():
 global _revision
 from artwork_visible import public_dns,KODI_OPTIONS
 from programme_assets47 import sources
 while not _stop.is_set():
  try:key,portal,kind,rows=_queue.get(timeout=.5)
  except queue.Empty:continue
  try:
   __import__('render_cache81').prepare(portal,kind,rows,_stop.is_set)
   __import__('media_hero81').prepare(portal,kind,rows,_stop.is_set)
   initial=profile();end=time.monotonic()+.5;retained74=[]
   for row in rows:
    if _stop.is_set() or profile()!=initial or time.monotonic()>end:break
    for role,source in sources(row,provider_only=True).items():
     if not safe(portal,source):continue
     if not public_dns(source):continue
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
     retained74.append((row['sid'],role,source,remaining))
     if old.get('key')!=tag or old.get('uri')!=value['uri']:
      with _lock:_revision+=1
   from widget_refs74 import remember_many
   remember_many(portal,kind,retained74)
   try:__import__('widget_cache79').prepare(portal,kind,rows)
   except (OSError,ValueError,TypeError,RuntimeError,AttributeError):pass
  finally:
   with _lock:_pending.discard(key)
   _queue.task_done()
def revision():
 with _lock:return _revision
def renderable(uri):
 if not isinstance(uri,str) or not uri:return False
 return not any(uri.replace('\\','/').endswith('/resources/media/'+name) for name in ('vod.png','series.png','tv.png')) and '/resources/media/programme46/' not in uri
def shutdown():_stop.set()

def home():
 try:
  import xbmc,xbmcgui
  return xbmc.getSkinDir()=='skin.titan.bingie.mod' and xbmcgui.getCurrentWindowId()==10000
 except (AttributeError,RuntimeError):return False

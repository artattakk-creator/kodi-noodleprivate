"""Small native media publications before bulk warmup; no focus directory reload."""
import hashlib,json,threading,time
_guard=threading.Lock();_thread=None;_stop=threading.Event();_published={};_next=0
def prepare(cancel=lambda:False):
 global _next
 now=time.monotonic()
 if now<_next:return False
 _next=now+1
 from portals import get_active
 from widget_data41 import snapshot,policy
 from widget_assets69 import prepare as approve,read as references
 from widget_live47 import publish
 from epg_handoff63 import profile_scope
 worked=False
 for portal in get_active()[:4]:
  if cancel():break
  for kind in ('vod','series'):
   if cancel():break
   if not portal.get('include_'+kind,True):continue
   rows,code=snapshot(portal,kind)
   if not rows:continue
   approve(portal,kind,rows,cancel)
   refs=references(portal,kind,rows)
   # A publication changes only after rows/policy/references change, never on
   # IR focus. Existing native widget reload hooks retain their own rate limit.
   key=(profile_scope(),str(portal['id']),kind)
   stamp=hashlib.sha256(json.dumps([policy(portal,kind),[[r.get(k) for k in ('sid','name','cover','stream_icon')] for r in rows],refs],sort_keys=True).encode()).hexdigest()
   if _published.get(key)==stamp:continue
   if publish(portal,kind,rows,'READY'):
    _published[key]=stamp;worked=True
   while len(_published)>16:_published.pop(next(iter(_published)))
 return worked
def _run():
 import xbmc
 from startup48 import suspended
 import service_runtime as runtime
 monitor=xbmc.Monitor()
 cancel=lambda:_stop.is_set() or monitor.abortRequested()
 while not cancel():
  try:
   if not suspended() and not runtime.pressure():prepare(cancel)
  except Exception:pass
  if monitor.waitForAbort(.2):break
def poll():
 global _thread
 if _stop.is_set() or _thread is not None and _thread.is_alive():return
 import xbmc
 if not all(callable(getattr(xbmc.Monitor(),n,None)) for n in ('abortRequested','waitForAbort')):return
 with _guard:
  if _thread is None or not _thread.is_alive():
   _thread=threading.Thread(target=_run,name='XCMate-fast-widgets69',daemon=True);_thread.start()
def shutdown():
 _stop.set()
 from widget_assets69 import shutdown as stop_assets
 stop_assets()

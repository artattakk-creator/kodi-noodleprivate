"""Small native media publications before bulk warmup; no focus directory reload."""
import hashlib,json,threading,time
_guard=threading.Lock();_thread=None;_stop=threading.Event();_published={};_next=0
def prepare(cancel=lambda:False):
 global _next
 now=time.monotonic()
 if now<_next:return False
 _next=now+1
 try:__import__('skin_upgrade80').prepare()
 except (OSError,ValueError,RuntimeError,AttributeError):pass
 from portals import get_active
 from widget_data41 import snapshot,policy
 from widget_assets69 import prepare as approve,read as references
 from widget_live47 import publish
 # Refresh the focused Hero receipt on this existing one-second worker lane;
 # it must not wait for bulk catalogue/guide preparation.
 focus87=__import__('hero_epg63')._focus
 if focus87 and not cancel():
  try:__import__('hero_epg63').prepare(focus87[0])
  except (OSError,ValueError,RuntimeError,AttributeError):pass
 from epg_handoff63 import profile_scope
 worked=False
 portals=get_active()[:4]
 try:__import__('widget_runtime79').prepare(portals)
 except (OSError,ValueError,RuntimeError,AttributeError,TypeError):pass
 from home_schedule75 import configure,allowed,focused_rows,prepared,trace
 configure(portals)
 for portal in portals:
  if cancel():break
  # Live logo references need renewal/cache adoption independently of the
  # slower app-services EPG/catalogue warmup. Reuse its complete local memo
  # and the existing provider queue; unchanged refs never trigger a reload.
  if portal.get('include_live',True) and portal.get('start_group_id') and __import__('home_schedule75').applicable():
   live87,code87=snapshot(portal,'live')
   if live87 and code87 in ('READY','CACHE','READ_ONLY'):
    approve(portal,'live',live87,cancel)
    refs87=references(portal,'live',live87)
    key87=(profile_scope(),str(portal['id']),'live')
    stamp87=hashlib.sha256(json.dumps([policy(portal,'live'),[[r.get('sid'),__import__('station_logos87').source(r)] for r in live87],refs87],sort_keys=True).encode()).hexdigest()
    if _published.get(key87)!=stamp87 and publish(portal,'live',live87,code87):
     _published[key87]=stamp87;worked=True
  for kind in ('vod','series'):
   if cancel():break
   if not portal.get('include_'+kind,True):continue
   rows,code=snapshot(portal,kind)
   if not rows:
    __import__('home_loading85').update(portal,kind,rows,code,pending=bool(__import__('widget_assets69')._pending))
    if code in ('READY','CACHE') and allowed(kind,portal) and publish(portal,kind,rows,code):
     prepared(kind,0,portal=portal,rows=rows)
    continue
   admitted=allowed(kind,portal)
   selected=rows if admitted else focused_rows(portal,kind,rows)
   # Cached publication is independent of admission for NEW network work.
   if admitted and kind not in __import__('home_schedule75')._read(__import__('home_schedule75').KEY).get('prepared',[]):trace('MOVIE_WARM_BEGIN' if kind=='vod' else 'SERIES_WARM_BEGIN',count=len(selected))
   if selected:approve(portal,kind,selected,cancel)
   refs=references(portal,kind,rows)
   visible85=__import__('home_loading85').visible(portal,kind,rows)
   images85=__import__('external_art89').ready_count(portal,kind,visible85,refs)
   __import__('home_loading85').update(portal,kind,rows,code,images=images85,pending=bool(__import__('widget_assets69')._pending))
   from home_metrics82 import note as metric82
   # A publication changes only after rows/policy/references change, never on
   # IR focus. Existing native widget reload hooks retain their own rate limit.
   key=(profile_scope(),str(portal['id']),kind)
   stamp=hashlib.sha256(json.dumps([policy(portal,kind),[[r.get(k) for k in ('sid','name','cover','stream_icon','_no_art86','_manual_art43')] for r in rows],refs],sort_keys=True).encode()).hexdigest()
   metric82('CACHED_ITEMS_READY',kind,count=len(rows),local_images=sum(__import__('os').path.isabs(v) for roles in refs.values() for v in roles.values()),approved_refs=sum(len(v) for v in refs.values()),generation=stamp)
   if _published.get(key)==stamp:
    exists85=__import__('os').path.isfile(__import__('widget_refresh45').path(portal['id'],kind))
    if (exists85 or __import__('widget_readonly56').proof84(portal,kind,rows)) and (kind in __import__('home_schedule75')._read(__import__('home_schedule75').KEY).get('prepared',[]) or not admitted or prepared(kind,len(rows),portal=portal,rows=rows)):continue
   if publish(portal,kind,rows,'READY'):
    _published[key]=stamp;worked=True
    metric82('LISTITEM_PUBLISHED',kind,count=len(rows))
    if admitted:prepared(kind,len(rows),portal=portal,rows=rows)
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

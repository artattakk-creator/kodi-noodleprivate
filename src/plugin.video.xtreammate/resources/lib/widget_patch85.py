"""Patch verified unchanged native media rows, without directory/focus resets.

Worker publishes a bounded art-only DTO. GUI validates every item before any
mutation. No SQL/file/network IO, list reset, selection or focus operation.
"""
import hashlib,json,time
PREFIX='XCMate.MediaPatch85.'
MAX_BYTES=256*1024
_sent={}

def slot(pid,kind,profile):return PREFIX+str(int(hashlib.sha256((profile+'|'+str(pid)+'|'+kind).encode()).hexdigest()[:8],16)%16)
def prepare(portal,kind,items,signature):
 if kind not in ('vod','series') or not 0<len(items)<=24:return False
 from epg_handoff63 import profile_scope
 from widget_runtime79 import slot as source_slot,_plans,_lock
 import xbmcgui
 profile=profile_scope()
 with _lock:plan=_plans.get((str(portal['id']),kind),{})
 if plan.get('scope')!=profile or not plan.get('ids'):return False
 clean=[dict(label=v['label'],url=v['url'],art=v['art'],props={k:v for k,v in v['props'].items() if k in ('XCMate.PortalId','XCMate.WidgetKind41','XCMate.MediaId','XCMate.Source85','XCMate.MediaHeroSource81','XCMate.SeriesArt64','XCMate.ArtPending69')}) for v in items]
 record=dict(profile=profile,pid=str(portal['id']),kind=kind,source=source_slot(portal,kind),signature=signature,at=time.time(),items=clean)
 raw=json.dumps(record,separators=(',',':'))
 if len(raw.encode())>MAX_BYTES:return False
 xbmcgui.Window(10000).setProperty(slot(portal['id'],kind,profile),raw);return True

def apply(pid,kind,signature):
 import xbmc,xbmcgui
 from epg_handoff63 import profile_scope
 if kind not in ('vod','series') or xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999) or xbmc.getCondVisibility('Player.HasMedia'):return False
 from widget_runtime79 import _lock,_plans
 profile=profile_scope();window=xbmcgui.Window(10000)
 with _lock:plan=dict(_plans.get((str(pid),kind),{}))
 if plan.get('scope')!=profile or time.monotonic()-plan.get('at',-1e9)>60:return False
 try:
  raw=window.getProperty(slot(pid,kind,profile));record=json.loads(raw) if raw and len(raw.encode())<=MAX_BYTES else {}
  if record.get('profile')!=profile or record.get('pid')!=str(pid) or record.get('kind')!=kind or record.get('signature')!=signature or record.get('source')!=plan.get('slot') or not 0<=time.time()-record.get('at',0)<30:return False
  values=record.get('items',[])
  if not 0<len(values)<=24:return False
  targets=[]
  for ident in plan.get('ids',[])[:8]:
   try:control=__import__('home_runtime77').control(window,ident)
   except (AttributeError,RuntimeError):continue
   count=xbmc.getInfoLabel('Container('+str(ident)+').NumItems')
   if str(count)!=str(len(values)):continue
   # DirectoryProvider's C++ items may be visible while Python size()==0.
   # That is not an empty directory and cannot be patched through getListItem.
   if control.size()==0:
    __import__('gui_guard86').note('LIST_UNEXPOSED',control=ident,count=0,route='widget_recent_vod' if kind=='vod' else 'widget_recent_series')
    continue
   from gui_guard86 import item as guarded86
   items=[guarded86(control,i,ident=ident,expected=len(values),route='widget_recent_vod' if kind=='vod' else 'widget_recent_series') for i in range(len(values))]
   if any(item is None for item in items):continue
   for item,value in zip(items,values):
    props=value['props']
    if item.getProperty('XCMate.PortalId')!=str(pid) or item.getProperty('XCMate.WidgetKind41')!=kind or item.getProperty('XCMate.MediaId')!=props['XCMate.MediaId'] or item.getPath()!=value['url'] or item.getLabel()!=value['label'] or not props.get('XCMate.Source85'):return False
   targets.extend(zip(items,values))
  if not targets:return False
  for item,value in targets:
   same=item.getProperty('XCMate.Source85')==value['props']['XCMate.Source85']
   # Same-source transient gaps keep already accepted pixels. A real source
   # change clears its old image instead of inheriting another edition.
   item.setArt({k:v for k,v in value['art'].items() if v or not same})
   for key,text in value['props'].items():item.setProperty(key,str(text))
  return True
 except (AttributeError,RuntimeError,ValueError,TypeError,KeyError):return False

def publication(hook,values):
 prior=_sent.get(hook,{})
 changed=[v for v in values if prior.get((str(v[0]),v[1]))!=v[2]]
 if any(v[1] not in ('vod','series') for v in changed):return False
 if not all(apply(pid,kind,signature) for pid,kind,signature,_ in changed):return False
 sent(hook,values);return True

def sent(hook,values):
 _sent[hook]={(str(pid),kind):signature for pid,kind,signature,_ in values}
 while len(_sent)>64:_sent.pop(next(iter(_sent)))

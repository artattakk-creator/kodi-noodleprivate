"""Own Guide/detail registry and cooperative close; never closes foreign windows."""
import hashlib,json,time,uuid
PREFIX='XCMate.ProgrammeOwner69.'
def _window():
 import xbmcgui
 return xbmcgui.Window(10000)
def _scope():
 from epg_handoff63 import profile_scope
 return profile_scope()
def _slot(owner):return str(int(hashlib.sha256(owner.encode()).hexdigest()[:8],16)%32)
def register(view,kind):
 import xbmcgui
 from window_lifecycle import lease
 owner=getattr(view,'_native_owner','') or uuid.uuid4().hex
 view._owner69=owner;view._kind69=kind;view._pulse_at69=0
 try:view.setProperty('XCMate.NativeOwner',owner)
 except (AttributeError,RuntimeError):pass
 dialog=xbmcgui.getCurrentWindowDialogId()
 view._dialog69=dialog if isinstance(dialog,int) and dialog>=13000 else None
 view._window69=xbmcgui.getCurrentWindowId()
 view._lease69=lease()
 pulse(view)
def pulse(view):
 owner=getattr(view,'_owner69','')
 if not owner:return False
 portal=getattr(view,'portal',{}) or {}
 try:
  raw=_window().getProperty(PREFIX+'cancel.'+owner)
  cancel=json.loads(raw) if raw and len(raw)<1024 else {}
  if cancel.get('owner')==owner and cancel.get('profile')==_scope() and cancel.get('pid')==str(portal.get('id','')) and 0<=time.time()-cancel.get('at',0)<10:
   from live_exit import state
   exit_=state()
   if exit_ and exit_['session']['nonce']==cancel.get('nonce') and exit_['phase'] in ('home','complete'):
    view.close();return True
 except (AttributeError,RuntimeError,ValueError,TypeError,KeyError):pass
 if time.monotonic()<getattr(view,'_pulse_at69',0):return False
 view._pulse_at69=time.monotonic()+.5
 value=dict(owner=owner,profile=_scope(),pid=str(portal.get('id','')),kind=getattr(view,'_kind69',''),dialog=getattr(view,'_dialog69',None),window=getattr(view,'_window69',None),lease=getattr(view,'_lease69',''),at=time.time(),closed=bool(getattr(view,'_closed',False)))
 try:_window().setProperty(PREFIX+'view.'+_slot(owner),json.dumps(value,separators=(',',':')))
 except (AttributeError,RuntimeError,ValueError):pass
 return False
def unregister(view):
 owner=getattr(view,'_owner69','')
 if not owner:return
 try:
  marker=_window();key=PREFIX+'view.'+_slot(owner)
  raw=marker.getProperty(key);value=json.loads(raw) if raw else {}
  if value.get('owner')==owner:marker.clearProperty(key)
  marker.clearProperty(PREFIX+'cancel.'+owner)
 except (AttributeError,RuntimeError,ValueError,TypeError):pass
def cancel_matching(value,snapshot):
 """Signal only a currently identified own native object; no Dialog.Close."""
 import xbmcgui
 pid=str(value['session']['pid']);count=0
 for slot in range(32):
  try:
   raw=_window().getProperty(PREFIX+'view.'+str(slot))
   view=json.loads(raw) if raw and len(raw)<2048 else {}
   if view.get('profile')!=_scope() or view.get('pid')!=pid or view.get('kind') not in ('GUIDE','DETAIL') or view.get('closed') or not 0<=time.time()-view.get('at',0)<3:continue
   ident=view.get('dialog') or view.get('window')
   if ident not in (snapshot.get('dialog'),snapshot.get('window')) or not isinstance(ident,int) or ident<13000:continue
   if xbmcgui.Window(ident).getProperty('XCMate.NativeOwner')!=view.get('owner'):continue
   owner=view['owner'];_window().setProperty(PREFIX+'cancel.'+owner,json.dumps(dict(owner=owner,pid=pid,profile=_scope(),nonce=value['session']['nonce'],at=time.time())))
   count+=1
  except (AttributeError,RuntimeError,ValueError,TypeError,KeyError):continue
 return count

def mark(view,stage):
 try:
  import xbmc,xbmcgui
  xbmc.log('[XCMate][PROGRAMME_DIALOG69] stage='+stage+' owner='+hashlib.sha256(str(getattr(view,'_owner69','')).encode()).hexdigest()[:12]+' dialog='+str(xbmcgui.getCurrentWindowDialogId()),xbmc.LOGINFO)
 except (AttributeError,RuntimeError):pass
def initialized(function):
 """Capture native callback exceptions and close the actual shown child."""
 def wrapped(view):
  view._shown=True
  try:
   register(view,'DETAIL');mark(view,'INIT_BEGIN')
   function(view);mark(view,'INIT_DONE')
  except Exception:
   view._init_error69=True;view._ready=False;mark(view,'INIT_FAILED')
 return wrapped

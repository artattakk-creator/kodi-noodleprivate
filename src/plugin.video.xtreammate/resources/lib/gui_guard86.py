"""Bounded native-list access; fixed diagnostics, no title/URL/exception text."""
import hashlib,json,os,threading,time,traceback
_seen={}
def note(code,view=None,control=0,index=-1,count=-1,generation=None,error=None,route=''):
 if code not in ('LIST_UNEXPOSED','INDEX_REJECTED','GENERATION_CHANGED','NATIVE_LIST_FAILED','CALLBACK_FAILED','ROUTE_CANCELLED','JOB_CANCELLED','LIST_VALIDATED'):return
 route=route if route in ('media_detail','movies_home','series_home','xcmate_home','guide_grid','global_search','widget_recent_vod','widget_recent_series','programme_details46') else 'OTHER'
 kind=type(error).__name__ if error else ''
 kind=kind if kind in ('IndexError','RuntimeError','AttributeError','ValueError','TypeError','InterruptedError','SystemExit','PortalReadError','TimeoutError','OSError','MemoryError') else 'OTHER' if error else ''
 epoch=getattr(view,'_generation',generation or 0)
 facts=dict(code=code,route=route,control=int(control),index=int(index),count=int(count),generation=int(epoch or 0),thread=threading.get_ident(),exception=kind)
 reason=getattr(error,'reason','')
 if reason in ('PROFILE_BUSY','READ_IO','INVALID_PROFILE','PROFILE_RACE','PROFILE_BUDGET','MEMORY','MEMORY_PAUSE','UNKNOWN'):facts['portal_reason']=reason
 if code=='CALLBACK_FAILED':__import__('startup_diag90').note('CALLBACK_FAIL_REASON',reason=reason if reason in ('PROFILE_BUSY','READ_IO','INVALID_PROFILE','PROFILE_RACE','PROFILE_BUDGET','MEMORY','MEMORY_PAUSE') else 'UNKNOWN')
 try:
  import xbmcgui
  facts['window']=int(xbmcgui.getCurrentWindowId())
 except (ImportError,AttributeError,RuntimeError,TypeError,ValueError):pass
 tag=(code,route,control,index,count,epoch,kind);now=time.monotonic()
 if now-_seen.get(tag,-1e9)<30:return
 _seen[tag]=now
 while len(_seen)>128:_seen.pop(next(iter(_seen)))
 if error is not None:
  # Actual traceback frames, never source lines, locals, arguments or messages.
  root=os.path.dirname(__file__)
  facts['frames']=[dict(file=os.path.basename(f.filename),line=f.lineno,function=f.name) for f in traceback.extract_tb(error.__traceback__) if os.path.dirname(f.filename)==root][-8:]
  facts['callers']=[dict(file=os.path.basename(f.filename),line=f.lineno,function=f.name) for f in traceback.extract_stack(limit=12) if os.path.dirname(f.filename)==root and os.path.basename(f.filename)!='gui_guard86.py'][-6:]
 try:
  import xbmc
  xbmc.log('[XCMate][GUI86] '+json.dumps(facts,separators=(',',':')),xbmc.LOGINFO)
 except (ImportError,AttributeError,RuntimeError):pass

def current(view,generation=None,mode=None):
 return not getattr(view,'_closed',False) and (generation is None or getattr(view,'_generation',generation)==generation) and (mode is None or getattr(view,'mode',mode)==mode)

def item(control,index,view=None,ident=0,generation=None,expected=None,mode=None,route=''):
 if not current(view,generation,mode):
  note('GENERATION_CHANGED',view,ident,index,generation=generation,route=route);return None
 try:count=control.size()
 except (AttributeError,RuntimeError,TypeError,ValueError) as error:
  note('NATIVE_LIST_FAILED',view,ident,index,error=error,route=route);return None
 if type(count) is not int or count<0 or type(index) is not int or not 0<=index<count or expected is not None and count!=expected:
  note('LIST_UNEXPOSED' if count==0 and expected else 'INDEX_REJECTED',view,ident,index,count if type(count) is int else -1,route=route);return None
 try:
  value=control.getListItem(index)
  if not current(view,generation,mode) or control.size()!=count:
   note('GENERATION_CHANGED',view,ident,index,count,generation,route=route);return None
  return value
 except (AttributeError,RuntimeError,IndexError,TypeError,ValueError) as error:
  note('NATIVE_LIST_FAILED',view,ident,index,count,generation,error,route);return None

def position(control,rows,view=None,ident=0,generation=None,route=''):
 if not current(view,generation):return None
 try:count=control.size();index=control.getSelectedPosition()
 except (AttributeError,RuntimeError,IndexError,TypeError,ValueError) as error:
  note('NATIVE_LIST_FAILED',view,ident,error=error,route=route);return None
 if type(count) is not int or type(index) is not int or not 0<=index<min(len(rows),count) or not current(view,generation):
  note('INDEX_REJECTED',view,ident,index if type(index) is int else -1,count if type(count) is int else -1,route=route);return None
 return index

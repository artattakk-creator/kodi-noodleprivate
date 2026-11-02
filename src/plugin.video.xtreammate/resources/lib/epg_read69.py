"""Deadline/lock evidence, distinct from data-size budgets. No writes to EPG."""
import hashlib,threading,time
_lock=threading.Lock();_values={};_logged={}
def _key(pid,sid):
 from epg_handoff63 import profile_scope
 return profile_scope(),str(pid),str(sid)
def record(error,pid,sid,duration_ms=0):
 from programme_writes69 import classify
 code=classify(error,read=True);key=_key(pid,sid);now=time.monotonic()
 with _lock:
  _values[key]=(now,code)
  while len(_values)>256:_values.pop(next(iter(_values)))
  last=_logged.get((key,code),-1e9)
  if now-last<30:return
  _logged[(key,code)]=now
  while len(_logged)>256:_logged.pop(next(iter(_logged)))
 try:
  import xbmc
  token=hashlib.sha256('|'.join(key).encode()).hexdigest()[:12]
  xbmc.log('[XCMate][EPG69] event='+token+' code='+code+' duration_ms='+str(max(0,int(duration_ms))),xbmc.LOGINFO)
 except (ImportError,AttributeError,RuntimeError):pass
def last(pid,sid):
 with _lock:value=_values.get(_key(pid,sid))
 return value[1] if value and time.monotonic()-value[0]<60 else ''

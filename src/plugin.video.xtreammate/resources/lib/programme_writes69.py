"""Classified, profile/file-scoped write circuit. No deletion or limit changes."""
import errno,hashlib,json,os,sqlite3,threading,time
from urllib.parse import quote
_lock=threading.RLock()
_states={}
_last={}
PREFIX='XCMate.ProgrammeWrite69.'
CAPACITY={'SAFE_RESERVE_BLOCKED','REAL_ENOSPC','SQLITE_FULL_POLICY','SQLITE_FULL_STORAGE','SQLITE_FULL_UNKNOWN','FILESYSTEM_QUOTA'}

class Deferred(OSError):
 def __init__(self,code,until):
  self.code69=code;self.retry_at69=until;self.deferred69=True
  super().__init__(errno.EAGAIN,'PROGRAMME_WRITE_BACKOFF')

def key(filename):
 return hashlib.sha256(os.path.abspath(filename).encode()).hexdigest()

def _read(filename):
 ident=key(filename)
 try:
  import xbmcgui
  raw=xbmcgui.Window(10000).getProperty(PREFIX+ident)
  v=json.loads(raw) if raw and len(raw)<2048 else {}
  if isinstance(v,dict) and v.get('key')==ident and 0<=time.time()-v.get('at',0)<86400:return v
 except (ImportError,AttributeError,RuntimeError,ValueError,TypeError):pass
 with _lock:return dict(_states.get(ident,{}))

def _save(filename,value):
 ident=key(filename);value=dict(value,key=ident)
 with _lock:
  _states[ident]=value
  while len(_states)>16:_states.pop(next(iter(_states)))
 try:
  import xbmcgui
  xbmcgui.Window(10000).setProperty(PREFIX+ident,json.dumps(value,separators=(',',':'),allow_nan=False))
 except (ImportError,AttributeError,RuntimeError,ValueError,TypeError):pass

def classify(error,filename=None,read=False):
 specific=getattr(error,'code69','')
 if isinstance(specific,str) and specific:return specific
 name=getattr(error,'sqlite_errorname','') or ''
 if not isinstance(name,str):name=''
 if name.startswith(('SQLITE_BUSY','SQLITE_LOCKED')):return 'SQLITE_BUSY_LOCKED'
 if name=='SQLITE_INTERRUPT' or isinstance(error,TimeoutError):return 'EPG_READ_TIMEOUT' if read else 'SQLITE_WRITE_TIMEOUT'
 if getattr(error,'errno',None)==errno.ENOSPC:return 'REAL_ENOSPC'
 if getattr(error,'errno',None)==getattr(errno,'EDQUOT',122):return 'FILESYSTEM_QUOTA'
 if name=='SQLITE_FULL':
  if filename:
   db=None
   try:
    import shutil
    free=shutil.disk_usage(os.path.dirname(filename)).free
    db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.01)
    db.execute('PRAGMA query_only=ON')
    pages=db.execute('PRAGMA page_count').fetchone()[0]
    if pages>=32768 and free>=32*1024*1024+65536:return 'SQLITE_FULL_POLICY'
    if free<65536:return 'SQLITE_FULL_STORAGE'
   except (OSError,sqlite3.Error,ValueError):pass
   finally:
    if db is not None:db.close()
  return 'SQLITE_FULL_UNKNOWN'
 if isinstance(error,ValueError):return 'SQLITE_SCHEMA'
 return 'SQLITE_IO'

def record(filename,error,stage='art'):
 code=classify(error,filename)
 with _lock:
  _last[(key(filename),stage)]=code
  while len(_last)>64:_last.pop(next(iter(_last)))
 if getattr(error,'deferred69',False):return code
 now=time.time();prior=_read(filename)
 attempts=min(6,prior.get('attempts',0)+1) if prior.get('code')==code else 1
 delays=(30,120,300,900,900,900) if code in CAPACITY or code in ('SQLITE_SCHEMA','SQLITE_IO') else (1,2,5,15,30,60)
 delay=delays[attempts-1]
 value=dict(code=code,at=now,until=now+delay,attempts=attempts,probe_after=now+min(30,delay))
 try:
  import shutil
  value['free_at_failure']=shutil.disk_usage(os.path.dirname(filename)).free
 except OSError:pass
 _save(filename,value)
 try:
  import xbmc
  xbmc.log('[XCMate][PROGRAMME_DB69] stage='+('art' if stage not in ('facts','events','art') else stage)+' code='+code+' backoff_seconds='+str(delay),xbmc.LOGWARNING)
 except (ImportError,AttributeError,RuntimeError):pass
 return code

def permit(filename,now=None):
 now=time.time() if now is None else now;value=_read(filename)
 if not value or value.get('until',0)<=now:return True
 if value.get('code') in CAPACITY and now>=value.get('probe_after',now+1):
  try:
   import shutil
   free=shutil.disk_usage(os.path.dirname(filename)).free
   if free>=32*1024*1024+65536 and free-value.get('free_at_failure',free)>=1024*1024:
    _save(filename,dict(code='HALF_OPEN',at=now,until=0,attempts=value.get('attempts',1)));return True
  except OSError:pass
  value['probe_after']=now+30;_save(filename,value)
 return False

def guard(filename):
 if not permit(filename):
  value=_read(filename);raise Deferred(value.get('code','SQLITE_IO'),value.get('until',time.time()+30))

def success(filename,stage='art'):
 # A small successful metadata write is positive evidence of recovery.
 value=_read(filename)
 if value and value.get('code')!='READY':_save(filename,dict(code='READY',at=time.time(),until=0,attempts=0))
 with _lock:_last.pop((key(filename),stage),None)

def last(filename,stage='art'):
 with _lock:code=_last.get((key(filename),stage))
 return code or _read(filename).get('code','READY')

def state(filename):
 value=_read(filename)
 return {k:value[k] for k in ('code','at','until','attempts','free_at_failure') if k in value}

"""Optional metadata cannot erase committed guide text. No HTTP or writes."""
import hashlib,sqlite3,time
_seen={}
def optional(pid,sid,fallback,read):
 try:
  value=read()
  if not isinstance(value,list):raise ValueError('INVALID_OPTIONAL_DATA')
  return value
 except (OSError,sqlite3.Error,ValueError,TypeError,KeyError,RuntimeError) as error:
  code=getattr(error,'sqlite_errorname','')
  code=code if code in ('SQLITE_BUSY','SQLITE_LOCKED','SQLITE_INTERRUPT','SQLITE_ERROR','SQLITE_CORRUPT','SQLITE_NOTADB','SQLITE_SCHEMA','SQLITE_IOERR','SQLITE_FULL') else type(error).__name__
  digest=hashlib.sha256((str(pid)+'|'+str(sid)).encode()).hexdigest()[:12]
  key=(digest,code);now=time.monotonic()
  if now-_seen.get(key,-1e9)>=60:
   _seen[key]=now
   while len(_seen)>128:_seen.pop(next(iter(_seen)))
   try:
    import xbmc
    xbmc.log('[XCMate][EPG67] stage=OPTIONAL_METADATA code=TEXT_PRESERVED detail='+code+' channel='+digest,xbmc.LOGWARNING)
   except (ImportError,AttributeError,RuntimeError):pass
  return fallback

"""Fixed-code category evidence and conservative cache fallback, no title traces."""
import errno,json,sqlite3,time
class EmptyCategory65(ValueError):
 def __init__(self,received=0,discarded=0):
  self.received=received;self.discarded=discarded
  super().__init__('SOURCE_EMPTY' if not received else 'SOURCE_FILTERED')
def reason(error):
 if error is None:return 'NONE'
 if isinstance(error,EmptyCategory65):return str(error)
 if isinstance(error,TimeoutError):return 'NETWORK_TIMEOUT'
 if isinstance(error,ConnectionError):return 'CONNECTION_ERROR'
 number=getattr(error,'errno',0)
 if number==errno.ENOSPC:return 'DISK_FULL'
 if number in (errno.EACCES,errno.EPERM):return 'ACCESS_DENIED'
 if number==errno.EROFS:return 'READ_ONLY'
 if isinstance(error,sqlite3.Error):return 'DATABASE_ERROR'
 return 'SOURCE_OR_IO_FAILURE'
def note(pid,kind,cid,code,counts=None,transport='REMOTE',filename=None,error=None):
 from library_index import connect
 db=None
 try:
  db=connect(filename,write=True,timeout=.05)
  data={key:max(0,int((counts or {}).get(key,0))) for key in ('received','stored','discarded')}
  data.update(error_code=reason(error),code=code if code in ('READY','SOURCE_EMPTY','SOURCE_FILTERED','CACHED','FAILED','CANCELLED') else 'FAILED',transport=transport if transport in ('REMOTE','LOCAL_CACHE') else 'REMOTE',at=time.time())
  with db:
   db.execute('CREATE TABLE IF NOT EXISTS catalog_evidence65(pid TEXT,kind TEXT,cid TEXT,data TEXT,PRIMARY KEY(pid,kind,cid))')
   db.execute('INSERT OR REPLACE INTO catalog_evidence65 VALUES(?,?,?,?)',(str(pid),kind,str(cid),json.dumps(data)))
 except (OSError,sqlite3.Error,ValueError,TypeError):pass
 finally:
  if db is not None:db.close()
def cold_categories(db,pid,kind,allowed):
 return {str(cid) for cid in allowed if not db.execute('SELECT 1 FROM heads WHERE pid=? AND kind=? AND cid=?',(pid,kind,str(cid))).fetchone() and not db.execute('SELECT 1 FROM titles WHERE pid=? AND kind=? AND cid=? LIMIT 1',(pid,kind,str(cid))).fetchone()}
def selected_cancel(pid,kind,groups,cid,upstream):
 next_check=0;stopped=False
 def check(force=False):
  nonlocal next_check,stopped
  if upstream():return True
  if force or time.monotonic()>=next_check:
   from group_selection import enabled_ids
   stopped=str(cid) not in enabled_ids(pid,kind,groups);next_check=time.monotonic()+.5
  return stopped
 check.verify=lambda:check(True)
 return check

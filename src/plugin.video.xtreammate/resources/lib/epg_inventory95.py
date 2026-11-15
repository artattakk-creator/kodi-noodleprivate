"""Read-only, revision/file-pinned per-source inventory; no global 1s verdict."""
import copy,os,sqlite3,threading,time
from urllib.parse import quote
_cache={};_lock=threading.RLock()
def token(filename):
 result=[]
 for suffix in ('','-wal'):
  try:s=os.stat(filename+suffix);result.append((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns))
  except FileNotFoundError:result.append(None)
 return tuple(result)
def collect(pid,filename,seconds=8,source_seconds=2):
 if not os.path.isfile(filename):return dict(code='NOT_CREATED',sources=[],programmes=0,first=None,last=None)
 started=time.monotonic();end=started+seconds;db=None;rows=[];total=None;first=last=None;code='READY';key=(filename,str(pid));before=token(filename)
 with _lock:cached=_cache.get(key)
 if cached and cached[0]==before:return copy.deepcopy(cached[1])
 try:
  db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.1)
  db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
  db.set_progress_handler(lambda:int(time.monotonic()>=end),1000)
  ids=[r[0] for r in db.execute('SELECT DISTINCT source_id FROM guide44_inputs WHERE pid=? LIMIT 129',(str(pid),))]
  if len(ids)>128:return dict(code='INVENTORY_BUDGET',sources=[],programmes=None,first=None,last=None)
  total=db.execute('SELECT count(*) FROM programmes WHERE pid=?',(str(pid),)).fetchone()[0]
  for source in ids:
   deadline=min(end,time.monotonic()+source_seconds);cursor=None;n=channels=0;previous=None;left=right=None
   db.set_progress_handler(lambda:int(time.monotonic()>=deadline),1000)
   try:
    while True:
     if time.monotonic()>=deadline or n>=1000000:raise TimeoutError('INVENTORY_BUDGET')
     clause=' AND (cid,start,stop)>(?,?,?)' if cursor else ''
     batch=db.execute('SELECT cid,start,stop FROM guide44_inputs WHERE pid=? AND source_id=?'+clause+' ORDER BY cid,start,stop LIMIT 2048',(str(pid),source)+tuple(cursor or ())).fetchall()
     if not batch:break
     for cid,start,stop in batch:
      n+=1;channels+=int(cid!=previous);previous=cid;left=start if left is None else min(left,start);right=stop if right is None else max(right,stop)
     cursor=batch[-1]
    row=dict(id=source,code='READY',channels=channels,programmes=n,first=left,last=right)
    if n:first=left if first is None else min(first,left);last=right if last is None else max(last,right)
   except (TimeoutError,sqlite3.Error) as exc:
    reason='DB_BUSY' if getattr(exc,'sqlite_errorcode',0)&255 in (5,6) else 'INVENTORY_BUDGET'
    row=dict(id=source,code=reason,channels=None,programmes=None,first=None,last=None,records_checked=n);code='PARTIAL'
   rows.append(row)
  result=dict(code=code,sources=rows,programmes=total,first=first,last=last,elapsed_ms=round((time.monotonic()-started)*1000,2))
  if code=='READY' and token(filename)==before:
   with _lock:
    if len(_cache)>=16:_cache.pop(next(iter(_cache)))
    _cache[key]=(before,copy.deepcopy(result))
  return result
 except sqlite3.Error as exc:
  number=getattr(exc,'sqlite_errorcode',0)&255
  return dict(code='DB_BUSY' if number in (5,6) else 'INVENTORY_BUDGET' if number==9 else 'DB_SCHEMA_MISSING',sources=rows,programmes=None,first=None,last=None)
 except OSError:return dict(code='STORAGE_IO',sources=rows,programmes=None,first=None,last=None)
 except (TypeError,ValueError):return dict(code='DB_SCHEMA_MISSING',sources=rows,programmes=None,first=None,last=None)
 finally:
  if db is not None:db.close()

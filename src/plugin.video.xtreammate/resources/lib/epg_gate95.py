"""Worker-only, independent backup proof; never writes the guide or backups.
The local locator is a hint. Authority always requires DB + receipt + SHA.
"""
import errno,hashlib,json,os,re,sqlite3,tempfile,threading,time
from pathlib import Path
from urllib.parse import quote
_lock=threading.RLock();_hashes={};_reports={};_workers={}
NAME=re.compile(r'guide-[0-9]{16,20}\.sqlite$')
class Rejected(Exception):
 def __init__(self,code):self.code=code
def stamp(path):
 s=os.stat(path,follow_symlinks=False)
 if not __import__('stat').S_ISREG(s.st_mode):raise Rejected('BACKUP_RECEIPT_MISMATCH')
 return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def check(end,cancel):
 if cancel():raise Rejected('CANCELLED')
 if time.monotonic()>=end:raise Rejected('BACKUP_GATE_TIMEOUT')
def digest(path,end,cancel):
 before=stamp(path)
 with _lock:cached=_hashes.get(str(path))
 if cached and cached[0]==before:return cached[1]
 h=hashlib.sha256()
 fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
 with os.fdopen(fd,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):
   check(end,cancel);h.update(chunk)
 if stamp(path)!=before:raise Rejected('BACKUP_RECEIPT_MISMATCH')
 value=h.hexdigest()
 with _lock:
  if len(_hashes)>=16:_hashes.pop(next(iter(_hashes)))
  _hashes[str(path)]=(before,value)
 return value
def atomic(path,value):
 fd,tmp=tempfile.mkstemp(prefix='.epg-gate95-',dir=path.parent)
 try:
  os.fchmod(fd,0o600)
  with os.fdopen(fd,'w',encoding='utf-8') as f:fd=None;json.dump(value,f,separators=(',',':'));f.flush();os.fsync(f.fileno())
  os.replace(tmp,path);tmp=None
 finally:
  if fd is not None:os.close(fd)
  if tmp:os.unlink(tmp)
def read_json(path,maximum=4096):
 if path.is_symlink() or stamp(path)[2]>maximum:raise Rejected('BACKUP_RECEIPT_MISMATCH')
 fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
 with os.fdopen(fd,'r',encoding='utf-8') as f:raw=f.read(maximum+1)
 if len(raw)>maximum:raise Rejected('BACKUP_RECEIPT_MISMATCH')
 value=json.loads(raw)
 if not isinstance(value,dict):raise Rejected('BACKUP_RECEIPT_MISMATCH')
 return value
def locate(source,wanted,end,cancel,result):
 folder=source.parent/'guide_backups44'
 if folder.is_symlink() or not folder.is_dir():raise Rejected('BACKUP_DIR_UNAVAILABLE')
 locator=source.parent/'epg_gate_locator95.json';preferred=None
 try:
  hint=read_json(locator)
  if hint.get('sha256')==wanted and NAME.fullmatch(str(hint.get('backup',''))):preferred=hint['backup']+'.json'
 except (OSError,ValueError,Rejected):pass
 def entries():
  if preferred:yield preferred
  try:
   with os.scandir(folder) as rows:
    for n,row in enumerate(rows):
     check(end,cancel);result['files_checked']=n+1
     if n>=16384:raise Rejected('BACKUP_GATE_TIMEOUT')
     if row.name!=preferred and row.name.endswith('.json') and NAME.fullmatch(row.name[:-5]) and not row.is_symlink():yield row.name
  except OSError as exc:raise Rejected('BACKUP_DIR_UNAVAILABLE') from exc
 mismatch=False;missing=False
 for name in entries():
  check(end,cancel)
  try:
   receipt=folder/name;before=stamp(receipt);value=read_json(receipt);backup=name[:-5]
   if value.get('code')!='BACKUP_VERIFIED' or value.get('backup')!=backup or value.get('sha256')!=wanted:mismatch=True;continue
   target=folder/backup
   if not target.exists():missing=True;continue
   if target.is_symlink() or stamp(target)[2]!=value.get('bytes') or digest(target,end,cancel)!=wanted:mismatch=True;continue
   config_sha=value.get('source_config_sha256')
   if config_sha and (not re.fullmatch('[a-f0-9]{64}',str(config_sha)) or digest(folder/(backup+'.sources.json'),end,cancel)!=config_sha):mismatch=True;continue
   if stamp(receipt)!=before:raise Rejected('BACKUP_RECEIPT_MISMATCH')
   try:atomic(locator,dict(version=1,sha256=wanted,backup=backup))
   except OSError:pass
   result['backup_bytes']=value['bytes'];return
  except FileNotFoundError:missing=True
  except (ValueError,TypeError,Rejected) as exc:
   if isinstance(exc,Rejected) and exc.code in ('CANCELLED','BACKUP_GATE_TIMEOUT'):raise
   mismatch=True
 if missing:raise Rejected('BACKUP_MISSING')
 raise Rejected('BACKUP_RECEIPT_MISMATCH' if mismatch else 'BACKUP_MISSING')
def inspect(filename,*,seconds=30,cancel=lambda:False):
 started=time.monotonic();end=started+max(0,seconds);source=Path(filename);db=None
 result=dict(code='BACKUP_GATE_TIMEOUT',checked_at=time.time(),files_checked=0,backup_bytes=0,sha_prefix='')
 try:
  check(end,cancel)
  if not source.exists():result['code']='NOT_CREATED';return result
  if source.is_symlink():raise Rejected('STORAGE_ACCESS_DENIED')
  identity=os.stat(source);identity=(identity.st_dev,identity.st_ino)
  db=sqlite3.connect('file:'+quote(str(source),safe='/')+'?mode=ro',uri=True,timeout=.25)
  db.execute('PRAGMA query_only=ON');db.execute('BEGIN');sql_end=min(end,time.monotonic()+3)
  db.set_progress_handler(lambda:int(cancel() or time.monotonic()>=sql_end),1000)
  tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
  if not {'programmes','guide44_inputs','guide44_authorization'}.issubset(tables):raise Rejected('DB_SCHEMA_MISSING')
  if not db.execute('SELECT 1 FROM programmes LIMIT 1').fetchone():result['code']='IMPORT_AUTHORIZED';return result
  row=db.execute("SELECT backup_sha FROM guide44_authorization WHERE kind='VERIFIED_BACKUP' ORDER BY created DESC LIMIT 1").fetchone()
  if not row or not re.fullmatch('[a-f0-9]{64}',str(row[0])):raise Rejected('DB_AUTHORIZATION_MISSING')
  wanted=row[0];result['sha_prefix']=wanted[:16];db.close();db=None
  locate(source,wanted,end,cancel,result)
  check(end,cancel)
  db=sqlite3.connect('file:'+quote(str(source),safe='/')+'?mode=ro',uri=True,timeout=.25)
  db.set_progress_handler(lambda:int(cancel() or time.monotonic()>=end),1000)
  current=db.execute("SELECT backup_sha FROM guide44_authorization WHERE kind='VERIFIED_BACKUP' ORDER BY created DESC LIMIT 1").fetchone();now=os.stat(source)
  if not current or current[0]!=wanted or (now.st_dev,now.st_ino)!=identity:raise Rejected('DB_AUTHORIZATION_CHANGED')
  result['code']='IMPORT_AUTHORIZED'
 except Rejected as exc:result['code']=exc.code
 except sqlite3.Error as exc:
  code=getattr(exc,'sqlite_errorcode',0)&255
  result['code']='CANCELLED' if cancel() else 'DB_BUSY' if code in (5,6) else 'BACKUP_GATE_TIMEOUT' if code==9 and time.monotonic()>=min(end,locals().get('sql_end',end)) else 'DB_INTERRUPTED' if code==9 else 'DB_SCHEMA_MISSING' if code==1 else 'STORAGE_IO';result['sqlite_code']=code
 except (OSError,ValueError,TypeError) as exc:
  result['code']='STORAGE_FULL' if getattr(exc,'errno',None)==errno.ENOSPC else 'STORAGE_ACCESS_DENIED' if getattr(exc,'errno',None) in (errno.EACCES,errno.EPERM) else 'STORAGE_IO'
 finally:
  if db is not None:db.close()
  result['elapsed_ms']=round((time.monotonic()-started)*1000,2)
  with _lock:
   if len(_reports)>=16:_reports.pop(next(iter(_reports)))
   _reports[str(source)]=dict(result)
  # Redacted durable observation only, never an authorization substitute.
  try:
   if source.parent.is_dir():atomic(source.parent/'epg_gate95_status.json',dict(result,guide_tag=hashlib.sha256(str(source.resolve()).encode()).hexdigest()[:16]))
  except OSError:pass
  try:
   from utils import info
   info('[EPG_GATE95] '+json.dumps(result,separators=(',',':')))
  except Exception:pass # Diagnostics cannot change an authorization verdict.
 return result
def latest(filename):
 with _lock:result=dict(_reports.get(str(filename),{}))
 if result:return result
 try:
  source=Path(filename);value=read_json(source.parent/'epg_gate95_status.json')
  if value.get('guide_tag')==hashlib.sha256(str(source.resolve()).encode()).hexdigest()[:16]:return value
 except (OSError,ValueError,Rejected):pass
 return {}
def request(filename,completed=lambda result:None):
 """Single-flight probe; GUI never scans a directory or hashes a backup."""
 key=str(filename)
 with _lock:
  old=_workers.get(key)
  if old and old.is_alive():return False
  def run():
   result=inspect(key)
   try:completed(result)
   except (RuntimeError,OSError):pass # Kodi may be closing the requesting UI.
  thread=threading.Thread(target=run,name='XCMate-gate95',daemon=True);_workers[key]=thread;thread.start();return True

def message(code):
 from localization import tr
 labels={'IMPORT_AUTHORIZED': 38900, 'DB_BUSY': 38901, 'BACKUP_GATE_TIMEOUT': 38902, 'BACKUP_MISSING': 38903, 'BACKUP_RECEIPT_MISMATCH': 38904, 'BACKUP_DIR_UNAVAILABLE': 38905, 'DB_SCHEMA_MISSING': 38906, 'DB_AUTHORIZATION_MISSING': 38907, 'DB_AUTHORIZATION_CHANGED': 38908, 'DB_INTERRUPTED': 38909, 'STORAGE_FULL': 38910, 'STORAGE_ACCESS_DENIED': 38911, 'STORAGE_IO': 38912, 'CHECKING': 38913}
 return tr(labels.get(code,38914))+' ['+str(code)+']'

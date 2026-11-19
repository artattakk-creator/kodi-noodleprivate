"""Cold-reader proof of a previously locked, validated portal-file generation.
Only file identity + SHA are persisted, never a second credentials database.
"""
import hashlib,json,os,stat,tempfile
from pathlib import Path
def proof(path):return Path(str(path)+'.snapshot95.json')
def record(path,key,raw):
 target=proof(path);value=dict(version=1,stamp=list(key[1:]),sha256=hashlib.sha256(raw).hexdigest())
 fd,tmp=tempfile.mkstemp(prefix='.portal-proof95-',dir=target.parent)
 try:
  os.fchmod(fd,0o600)
  with os.fdopen(fd,'w') as f:fd=None;json.dump(value,f,separators=(',',':'));f.flush();os.fsync(f.fileno())
  os.replace(tmp,target);tmp=None
 finally:
  if fd is not None:os.close(fd)
  if tmp:os.unlink(tmp)
def read(path,types,version):
 target=proof(path)
 if target.is_symlink() or Path(path).is_symlink():return None
 try:
  if target.stat().st_size>2048:return None
  value=json.loads(target.read_bytes());key=version(path)
  if value.get('version')!=1 or value.get('stamp')!=list(key[1:]) or key[1] is None:return None
  fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
  with os.fdopen(fd,'rb') as f:
   s=os.fstat(f.fileno())
   if not stat.S_ISREG(s.st_mode) or s.st_size>4*1024*1024:return None
   raw=f.read(4*1024*1024+1)
  if len(raw)>4*1024*1024 or hashlib.sha256(raw).hexdigest()!=value.get('sha256') or version(path)!=key:return None
  rows=json.loads(raw)
  if not isinstance(rows,list) or any(not isinstance(p,dict) or not isinstance(p.get('id'),str) or not p['id'] or p.get('type') not in types for p in rows):return None
  return key,rows
 except (OSError,ValueError,TypeError,AttributeError):return None

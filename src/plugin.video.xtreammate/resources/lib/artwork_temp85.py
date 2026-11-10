"""Owned temporary bytes only; no archive/Kodi-cache deletion or reserve bypass.

All operations are worker-only, under the existing cross-process profile lock.
Uncommitted crash-orphans stay inside this namespace and count against limits.
"""
import hashlib,json,os,re,tempfile,time
from pathlib import Path
from media_sources43 import SourceError
OWNER={'format':1,'owner':'XCMate temporary artwork 85'}
class Unavailable(OSError):pass
class Cache:
 def __init__(self,root,max_bytes=16*1024*1024,max_objects=64,clock=time.time):
  self.root=Path(root);self.max_bytes=max(1,min(int(max_bytes),64*1024*1024));self.max_objects=max(1,min(int(max_objects),256));self.clock=clock
 def atomic(self,path,body):
  fd,tmp=tempfile.mkstemp(prefix='.txn-',dir=self.root)
  try:
   with os.fdopen(fd,'wb') as f:f.write(body);f.flush();os.fsync(f.fileno())
   os.replace(tmp,path)
   directory=os.open(self.root,os.O_RDONLY)
   try:os.fsync(directory)
   finally:os.close(directory)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
 def checked(self,create=False):
  if self.root.is_symlink() or any(p.is_symlink() for p in self.root.parents):raise Unavailable('UNSAFE_TEMP_ROOT')
  if not self.root.exists():
   if not create:return False
   self.root.mkdir(mode=0o700,parents=True)
  marker=self.root/'owner.json'
  if marker.is_symlink():raise Unavailable('UNSAFE_TEMP_OWNER')
  if not marker.exists():
   if not create or any(self.root.iterdir()):raise Unavailable('UNOWNED_TEMP_ROOT')
   self.atomic(marker,json.dumps(OWNER).encode())
  if marker.stat().st_size>256 or json.loads(marker.read_bytes())!=OWNER:raise Unavailable('UNOWNED_TEMP_ROOT')
  extras=[p for p in self.root.iterdir() if p.name.startswith(('.txn-','.body85-'))]
  metadata=[p for p in extras if p.name.startswith('.txn-')];bodies=[p for p in extras if p.name.startswith('.body85-')]
  if len(metadata)>2 or sum(p.lstat().st_size for p in metadata)>1024*1024 or len(bodies)>1 or sum(p.lstat().st_size for p in bodies)>3*1024*1024:raise Unavailable('TEMP_ORPHAN_METADATA_LIMIT')
  if any(p.is_symlink() for p in extras):raise Unavailable('UNSAFE_TEMP_ORPHAN')
  return True
 def index(self):
  path=self.root/'index.json'
  if path.is_symlink():raise Unavailable('UNSAFE_TEMP_INDEX')
  if not path.exists():return {}
  if path.stat().st_size>512*1024:raise Unavailable('INVALID_TEMP_INDEX')
  data=json.loads(path.read_bytes())
  if data.get('format')!=1 or not isinstance(data.get('entries'),dict):raise Unavailable('INVALID_TEMP_INDEX')
  return data['entries']
 def files(self):
  result={}
  for p in self.root.iterdir():
   if re.fullmatch(r'[a-f0-9]{64}\.(png|jpg)',p.name):
    if p.is_symlink() or not p.is_file():raise Unavailable('UNSAFE_TEMP_FILE')
    result[p.name]=p.stat().st_size
  return result
 def read(self,digest):
  if not re.fullmatch('[a-f0-9]{64}',str(digest)) or not self.checked():return None
  entries=self.index();record=entries.get(digest)
  if not record or record.get('until',0)<=self.clock():return None
  name=record.get('file','')
  if not re.fullmatch(digest+r'\.(png|jpg)',name):return None
  path=self.root/name
  if path.is_symlink() or not path.is_file() or not 0<path.stat().st_size<=3*1024*1024 or path.stat().st_size!=record.get('size'):return None
  body=path.read_bytes()
  if len(body)>3*1024*1024 or hashlib.sha256(body).hexdigest()!=digest:return None
  try:__import__('media_sources43').validate_image(body)
  except SourceError:return None
  return str(path)
 def put(self,body,pin='',pin_until=0,expires=None,check=lambda n:None,context=None,reference=None):
  from profile_transaction import writing
  if not isinstance(body,bytes) or not 0<len(body)<=min(self.max_bytes,3*1024*1024):raise Unavailable('TEMP_OBJECT_LIMIT')
  __import__('media_sources43').validate_image(body)
  check(len(body)+65536)  # caller measures the exact target, preserving reserves
  with writing(timeout=.1):
   self.checked(create=True);self.recover();entries=self.index();files=self.files();now=self.clock();digest=hashlib.sha256(body).hexdigest();name=digest+('.png' if body.startswith(b'\x89PNG') else '.jpg')
   # A matching content hash proves bytes, not ownership. Only our exact
   # index/journal may grant deletion rights; never adopt an unknown file.
   if name in files and (not isinstance(entries.get(digest),dict) or entries[digest].get('file')!=name):raise Unavailable('TEMP_UNOWNED_FILE')
   for key,record in list(entries.items()):
    if not isinstance(record,dict) or not isinstance(record.get('pins',{}),dict):raise Unavailable('INVALID_TEMP_INDEX')
    if record.get('file') not in files:
     entries.pop(key);continue
    record['pins']={k:v for k,v in record.get('pins',{}).items() if type(v) in (int,float) and now<v<=now+31*86400}
    if not record['pins'] and not active(key) and record.get('until',0)<=now:
     owned=record.get('file','')
     if re.fullmatch(str(key)+r'\.(png|jpg)',owned) and owned in files:
      (self.root/owned).unlink();files.pop(owned);presence(key,False)
     entries.pop(key)
   needed=0 if name in files else len(body);objects=len(files)+int(name not in files)
   for key,record in sorted(entries.items(),key=lambda item:item[1].get('at',0)):
    if sum(files.values())+needed<=self.max_bytes and objects<=self.max_objects:break
    if key==digest or record.get('pins') or active(key):continue
    old=record.get('file','')
    if re.fullmatch(str(key)+r'\.(png|jpg)',old) and old in files:
     (self.root/old).unlink();files.pop(old);objects-=1;presence(key,False);entries.pop(key)
   if sum(files.values())+needed>self.max_bytes or objects>self.max_objects:raise Unavailable('TEMP_PINNED_OR_ORPHAN_LIMIT')
   check(len(body)+65536)
   if name in files and hashlib.sha256((self.root/name).read_bytes()).hexdigest()!=digest:raise Unavailable('TEMP_HASH_CONFLICT')
   record=entries.setdefault(digest,dict(file=name,size=len(body),pins={}))
   record.update(at=now,until=min(now+30*86400,max(now+60,expires or now+86400)))
   if pin:record['pins'][hashlib.sha256(pin.encode()).hexdigest()]=min(now+31*86400,max(now+1,pin_until))
   if context and reference is not None:
    refs=record.setdefault('contexts',{})
    if context not in refs and len(refs)>=8:raise Unavailable('TEMP_CONTEXT_LIMIT')
    refs[context]=reference
   raw=json.dumps(dict(format=1,entries=entries),separators=(',',':')).encode()
   if len(raw)>512*1024:raise Unavailable('TEMP_METADATA_LIMIT')
   if name not in files:
    fd,tmp=tempfile.mkstemp(prefix='.body85-',dir=self.root);stat=os.fstat(fd)
    pending=dict(file=name,temp=Path(tmp).name,dev=stat.st_dev,ino=stat.st_ino,sha256=digest,size=len(body),record=record)
    try:
     self.atomic(self.root/'pending85.json',json.dumps(pending,separators=(',',':')).encode())
     with os.fdopen(fd,'wb') as f:f.write(body);f.flush();os.fsync(f.fileno())
     os.replace(tmp,self.root/name)
     self.atomic(self.root/'index.json',raw)
     (self.root/'pending85.json').unlink(missing_ok=True)
    finally:
     if os.path.exists(tmp):os.unlink(tmp)
   else:self.atomic(self.root/'index.json',raw)
   presence(digest,True)
   return dict(file=str(self.root/name),sha256=digest,until=record['until'])

 def recover(self):
  """Recover only an exact journal-owned interrupted body, never unknown files."""
  pending=self.root/'pending85.json'
  if not pending.exists():return
  if pending.is_symlink() or pending.stat().st_size>65536:raise Unavailable('UNSAFE_TEMP_JOURNAL')
  item=json.loads(pending.read_bytes());name=item.get('file','');temp=item.get('temp','');digest=item.get('sha256','')
  if not re.fullmatch('[a-f0-9]{64}',digest) or not re.fullmatch(digest+r'\.(png|jpg)',name) or not re.fullmatch(r'\.body85-[a-zA-Z0-9_-]+',temp):raise Unavailable('INVALID_TEMP_JOURNAL')
  destination=self.root/name;part=self.root/temp
  if destination.is_symlink() or part.is_symlink():raise Unavailable('UNSAFE_TEMP_JOURNAL')
  candidate=destination if destination.exists() else part
  if candidate.exists():
   stat=candidate.stat()
   if candidate==part and (stat.st_dev!=item.get('dev') or stat.st_ino!=item.get('ino')):raise Unavailable('TEMP_JOURNAL_OWNER_CHANGED')
   if stat.st_size==item.get('size') and 0<stat.st_size<=3*1024*1024 and hashlib.sha256(candidate.read_bytes()).hexdigest()==digest:
    if stat.st_dev!=item.get('dev') or stat.st_ino!=item.get('ino'):raise Unavailable('TEMP_JOURNAL_OWNER_CHANGED')
    __import__('media_sources43').validate_image(candidate.read_bytes())
    if candidate==part:os.replace(part,destination)
    entries=self.index();entries[digest]=item['record'];raw=json.dumps(dict(format=1,entries=entries),separators=(',',':')).encode()
    if len(raw)>512*1024:raise Unavailable('TEMP_METADATA_LIMIT')
    self.atomic(self.root/'index.json',raw)
   elif candidate==part:part.unlink()  # exact created inode of this interrupted transfer
   else:raise Unavailable('TEMP_JOURNAL_HASH_CHANGED')
  pending.unlink()

 def context(self,key):
  if not self.checked():return None
  for digest,entry in self.index().items():
   value=entry.get('contexts',{}).get(key)
   if not isinstance(value,dict):continue
   filename=self.read(digest)
   if filename:return dict(value,image=filename,thumbnail=filename,sha256=digest)
  return None

def cache():
 from utils import addon_data_dir,setting_int
 return Cache(Path(os.path.realpath(addon_data_dir()))/'artwork_temporary85',setting_int('programme_temp85_mb',16)*1024*1024,setting_int('programme_temp85_objects',64))
_due=0.
def promote(event,value,body):
 global _due
 if not __import__('home_schedule75').applicable():return value
 if not body or not value.get('decoded77') or time.monotonic()<_due:return value
 from import_budget import check_space
 from programme_art46 import fingerprint
 from programme_requests68 import identity,scope
 from programme_policy68 import negative_scope
 c=cache()
 def capacity(size):
  from art_storage import capacity as measure
  result=measure(str(c.root))
  if result.get('storage_availability')!='AVAILABLE' or result.get('free',0)<result.get('reserve',1024**3)+size:raise Unavailable('TEMP_RESERVE_BLOCKED')
  check_space(str(c.root),size)
 try:
  context85=hashlib.sha256((identity(event)+fingerprint(event)).encode()).hexdigest()
  minimal85={k:value[k] for k in ('key','fingerprint','scope69','profile69','policy69','code','source','match','attribution','image_scope57','mapping_epoch85','provisional85','manual85','decoded77','role81','image_width77','image_height77') if k in value}
  minimal85.update(key=event['key'],fingerprint=fingerprint(event),scope69=identity(event),profile69=scope(),policy69=negative_scope({}))
  record=c.put(body,context=context85,reference=minimal85,pin=identity(event),pin_until=time.time()+60,expires=event.get('stop',time.time())+600,check=capacity)
  result=dict(value,image=record['file'],thumbnail=record['file'],sha256=record['sha256'],until=min(record['until'],time.time()+30),fingerprint=fingerprint(event),scope69=identity(event),profile69=scope(),policy69=negative_scope({}),temp85=True)
  for field in ('url_version55','url_verified69','display84','display_key84'):result.pop(field,None)
  publish(event,result)
  return result
 except (SourceError,OSError,ValueError,TypeError,TimeoutError):_due=time.monotonic()+30;return value


def context_key(event):
 from programme_requests68 import identity
 from programme_art46 import fingerprint
 return hashlib.sha256((identity(event)+fingerprint(event)).encode()).hexdigest()

def publish(event,value):
 import xbmcgui
 xbmcgui.Window(10000).setProperty('XCMate.Temp85.'+context_key(event),json.dumps(dict(value,until=min(value['until'],time.time()+30)),separators=(',',':')))

def published(event):
 import xbmcgui
 try:
  raw=xbmcgui.Window(10000).getProperty('XCMate.Temp85.'+context_key(event));value=json.loads(raw) if raw and len(raw)<8192 else {}
  if value.get('until',0)<=time.time():return {}
  return value if __import__('programme_image69').eligible(value,event) else {}
 except (ValueError,TypeError):return {}

def lookup(event):
 c=cache()
 if not c.root.exists():return None
 try:
  from profile_transaction import writing
  with writing(timeout=.1):
   if not c.checked():return None
   c.recover();value=c.context(context_key(event))
   if not value:return None
   if not __import__('programme_image69').eligible(value,event):return None
   # Refresh a bounded active-view pin without changing image identity.
   entries=c.index();record=entries[value['sha256']];now=time.time()
   from programme_requests68 import identity
   pin=hashlib.sha256(identity(event).encode()).hexdigest()
   old_pin85=record.setdefault('pins',{}).get(pin,0)
   record['pins'][pin]=max(old_pin85,now+60)
   value.update(until=min(record['until'],now+30),temp85=True)
   presence(value['sha256'],True)
   touch(value['sha256'])
   # Optional pin refresh writes are suppressed when reserves are blocked.
   from import_budget import check_space
   try:
    check_space(str(c.root),65536)
    c.atomic(c.root/'index.json',json.dumps(dict(format=1,entries=entries),separators=(',',':')).encode())
   except OSError:
    if old_pin85<=now+30 and not active(value['sha256']):return None
   publish(event,value);return value
 except (SourceError,OSError,ValueError,TypeError,KeyError,TimeoutError):return None


def touch(digest):
 if not re.fullmatch('[a-f0-9]{64}',str(digest)) or not present(digest):return
 try:
  from epg_handoff63 import profile_scope
  import xbmcgui
  xbmcgui.Window(10000).setProperty('XCMate.Temp85.Active.'+hashlib.sha256((profile_scope()+digest).encode()).hexdigest(),str(time.time()+45))
 except (ImportError,AttributeError,RuntimeError):pass

def active(digest):
 try:
  from epg_handoff63 import profile_scope
  import xbmcgui
  raw=xbmcgui.Window(10000).getProperty('XCMate.Temp85.Active.'+hashlib.sha256((profile_scope()+digest).encode()).hexdigest())
  return 0<float(raw)-time.time()<=45
 except (ImportError,AttributeError,RuntimeError,ValueError,TypeError):return False


def presence(digest,exists):
 try:
  from epg_handoff63 import profile_scope
  import xbmcgui
  key=hashlib.sha256((profile_scope()+digest).encode()).hexdigest();w=xbmcgui.Window(10000)
  if exists:w.setProperty('XCMate.Temp85.Present.'+key,'1')
  else:w.clearProperty('XCMate.Temp85.Present.'+key);w.clearProperty('XCMate.Temp85.Active.'+key)
 except (ImportError,AttributeError,RuntimeError):pass

def present(digest):
 try:
  from epg_handoff63 import profile_scope
  import xbmcgui
  return xbmcgui.Window(10000).getProperty('XCMate.Temp85.Present.'+hashlib.sha256((profile_scope()+str(digest)).encode()).hexdigest())=='1'
 except (ImportError,AttributeError,RuntimeError):return False

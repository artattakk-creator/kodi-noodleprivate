"""Bounded mini-asset exception for verified logos on the selected local volume.

No global reserve change, relocation, eviction, database or settings write.
Quota counts every existing image in this owned logo directory. The actual
volume's conservative available capacity and a separate safety floor apply.
"""
import hashlib,io,json,os,tempfile,time
from pathlib import Path
MIB=1024*1024
MAX_ASSET=128*1024
QUOTA=16*MIB
MAX_MANIFEST=512*1024
_verified={}

def identity(portal,row):
 from epg_handoff63 import profile_scope
 from station_logos87 import source
 return hashlib.sha256(json.dumps([profile_scope(),[portal.get(k) for k in ('id','type','xc_host','xc_user','xc_pass')],str(row['sid']),source(row)],sort_keys=True).encode()).hexdigest()

def thumbnail(body):
 from media_sources43 import validate_image
 width,height=validate_image(body)
 if len(body)<=MAX_ASSET and width<=512 and height<=256:return body,width,height
 from PIL import Image
 with Image.open(io.BytesIO(body)) as image:
  image.load();image.thumbnail((512,256));out=io.BytesIO()
  image.save(out,format='PNG');result=out.getvalue()
  if len(result)>MAX_ASSET:
   image.thumbnail((192,96));out=io.BytesIO();image.save(out,format='PNG');result=out.getvalue()
 width,height=validate_image(result)
 if len(result)>MAX_ASSET:raise OSError('LOGO_ASSET_QUOTA')
 return result,width,height

def capacity(backend,upcoming):
 from artwork_backend import LocalArtworkStorage
 from art_storage82 import capacity as measured
 if not isinstance(backend,LocalArtworkStorage):raise OSError('LOGO_LOCAL_REQUIRED')
 root=Path(backend.root)
 if root.is_symlink():raise OSError('LOGO_UNSAFE_ROOT')
 value=measured(str(root))
 if value.get('capacity82')!='SAME_VOLUME_VERIFIED':raise OSError('LOGO_VOLUME_UNVERIFIED')
 total=value.get('total');free=value.get('free')
 if type(total) is not int or type(free) is not int:raise OSError('LOGO_CAPACITY_UNKNOWN')
 floor=max(64*MIB,min(128*MIB,int(total*.02)))
 used=0;files=0
 if root.exists():
  for entry in root.iterdir():
   if entry.is_symlink():raise OSError('LOGO_UNSAFE_ROOT')
   if entry.is_file():
    used+=entry.stat().st_size;files+=1
    if files>1024:raise OSError('LOGO_FILE_QUOTA')
 if used+max(0,upcoming)>QUOTA+MAX_MANIFEST:raise OSError('LOGO_CACHE_QUOTA')
 if free<floor+max(0,upcoming)+256*1024:raise OSError('LOGO_SAFETY_FLOOR')
 return dict(free=free,total=total,reserve=floor,quota=QUOTA,used=used,volume=value.get('volume82'),mount=value.get('mount82'),capacity=value['capacity82'])

def atomic(path,raw):
 path=Path(path)
 if path.is_symlink():raise OSError('LOGO_UNSAFE_FILE')
 path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix='.logo89-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
  if Path(tmp).read_bytes()!=raw:raise OSError('LOGO_WRITE_READBACK')
  os.replace(tmp,path)
  directory=os.open(path.parent,os.O_RDONLY)
  try:os.fsync(directory)
  finally:os.close(directory)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def persist(portal,row,body,cancel=lambda:False):
 from logo_manifest86 import location,key,context,load
 from profile_transaction import writing
 from media_sources43 import SourceError
 body,width,height=thumbnail(body);digest=hashlib.sha256(body).hexdigest()
 backend,manifest=location();target=Path(backend.resolve_target(digest))
 with writing(timeout=.2):
  if cancel():raise SourceError('CANCELLED')
  facts=capacity(backend,len(body)+MAX_MANIFEST)
  if target.is_symlink():raise OSError('LOGO_UNSAFE_FILE')
  if target.exists():
   if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:atomic(target,body)
  else:atomic(target,body)
  if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise OSError('LOGO_WRITE_READBACK')
  if cancel():raise SourceError('CANCELLED')
  records=load(portal,all_records=True);stat=target.stat()
  records[key(portal,row)]=dict(context=context(portal),sha256=digest,stamp=[stat.st_mtime_ns,stat.st_size],width=width,height=height,storage89='PERSISTED_LOGO',stable89=identity(portal,row))
  raw=json.dumps(dict(format=1,records=records),sort_keys=True,separators=(',',':')).encode()
  if len(records)>512 or len(raw)>MAX_MANIFEST:raise OSError('LOGO_MANIFEST_QUOTA')
  # Re-measure just before metadata commit; never borrow another volume.
  if capacity(backend,len(raw)+65536).get('volume')!=facts.get('volume'):raise OSError('LOGO_VOLUME_CHANGED')
  atomic(manifest,raw)
  if load(portal,all_records=True).get(key(portal,row))!=records[key(portal,row)]:raise OSError('LOGO_MANIFEST_READBACK')
  _verified[str(target)]=(stat.st_mtime_ns,stat.st_size,digest)
  while len(_verified)>512:_verified.pop(next(iter(_verified)))
 return str(target),facts

def valid_file(path,record):
 """Verify once per changed file across invokers; no redundant image decode."""
 try:
  path=Path(path)
  if path.is_symlink():return False
  stat=path.stat();stamp=(stat.st_mtime_ns,stat.st_size,record.get('sha256'))
  if record.get('stamp')!=[stat.st_mtime_ns,stat.st_size] or not 0<stat.st_size<=3*MIB:return False
  if _verified.get(str(path))==stamp:return True
  if hashlib.sha256(path.read_bytes()).hexdigest()!=record.get('sha256'):return False
  _verified[str(path)]=stamp
  while len(_verified)>512:_verified.pop(next(iter(_verified)))
  return True
 except (OSError,ValueError,TypeError):return False


def note(code,**facts):
 """Private paths and source URLs are never logged, even on filesystem errors."""
 allowed={'PERSISTED_VERIFIED','LOGO_SAFETY_FLOOR','LOGO_CACHE_QUOTA','LOGO_FILE_QUOTA','LOGO_MANIFEST_QUOTA','LOGO_ASSET_QUOTA','LOGO_VOLUME_UNVERIFIED','LOGO_VOLUME_CHANGED','LOGO_CAPACITY_UNKNOWN','LOGO_LOCAL_REQUIRED','LOGO_UNSAFE_ROOT','LOGO_UNSAFE_FILE','LOGO_WRITE_READBACK','LOGO_MANIFEST_READBACK'}
 if code not in allowed:return
 import xbmc
 safe={k:v for k,v in facts.items() if k in ('free','total','reserve','quota','used') and type(v) is int and v>=0}
 xbmc.log('[XCMate][LOGO89] code='+code+' '+json.dumps(safe,separators=(',',':')),xbmc.LOGINFO)

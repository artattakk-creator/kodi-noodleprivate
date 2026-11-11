"""Bounded own provider-poster cache, independent of DNS lease and catalogue WAL.

No eviction/migration or settings change. Selected local media volume only;
never borrows the logo allowance for arbitrary database/archive writes.
"""
import hashlib,io,json,os,time
from pathlib import Path
MAX_ASSET=512*1024;QUOTA=24*1024*1024;MAX_MANIFEST=512*1024
_due={};_verified={}
def location():
 from artwork_backend import active_backend,LocalArtworkStorage
 backend=active_backend('media')
 if not isinstance(backend,LocalArtworkStorage):raise OSError('POSTER_LOCAL_REQUIRED')
 return Path(backend.root)/'verified_posters89'
def identity(portal,kind,row,role):
 from epg_handoff63 import profile_scope
 values=[profile_scope(),[portal.get(k) for k in ('id','type','xc_host','xc_user','xc_pass')],kind,str(row['sid']),role,str(row.get('name') or ''),str(row.get('year') or ''),row.get('_manual_art43'),bool(row.get('_no_art86'))]
 return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
def manifest():
 root=location();filename=root/'manifest89.json'
 try:
  if root.is_symlink() or filename.is_symlink() or filename.stat().st_size>MAX_MANIFEST:return {}
  value=json.loads(filename.read_bytes())
  return value['records'] if value.get('format')==1 and isinstance(value.get('records'),dict) and len(value['records'])<=512 else {}
 except (OSError,ValueError,TypeError,KeyError):return {}
def capacity(root,upcoming):
 from art_storage82 import capacity as measure
 value=measure(str(root))
 if value.get('capacity82')!='SAME_VOLUME_VERIFIED' or type(value.get('free')) is not int or type(value.get('total')) is not int:raise OSError('POSTER_VOLUME_UNVERIFIED')
 floor=max(96*1024**2,min(128*1024**2,int(value['total']*.02)))
 if value['free']<floor+upcoming+256*1024:raise OSError('POSTER_SAFETY_FLOOR')
 used=count=0
 if root.exists():
  if root.is_symlink():raise OSError('POSTER_UNSAFE_ROOT')
  for p in root.iterdir():
   if p.is_symlink():raise OSError('POSTER_UNSAFE_FILE')
   if p.is_file():used+=p.stat().st_size;count+=1
   if count>1024 or used+upcoming>QUOTA+MAX_MANIFEST:raise OSError('POSTER_QUOTA')
 return value

def validate(record):
 try:
  root=location();digest=record['sha256']
  if not __import__('re').fullmatch('[a-f0-9]{64}',digest):return None
  file=root/(digest+'.img')
  if file.is_symlink():return None
  s=file.stat();stamp=[s.st_mtime_ns,s.st_size]
  if not 0<s.st_size<=MAX_ASSET or record.get('stamp')!=stamp:return None
  tag=(str(file),s.st_mtime_ns,s.st_size,digest)
  if not _verified.get(tag):
   if hashlib.sha256(file.read_bytes()).hexdigest()!=digest:return None
   _verified[tag]=True
   while len(_verified)>256:_verified.pop(next(iter(_verified)))
  return str(file)
 except (OSError,ValueError,TypeError,KeyError):return None

def read(portal,kind,rows):
 if kind not in ('vod','series'):return {}
 if __import__('external_art89').enabled():return __import__('external_art89').references(portal,kind,rows)
 from widget_refs74 import revoked
 records=manifest();result=__import__('external_art89').references(portal,kind,rows,internal=True)
 for row in rows[:24]:
  if row.get('_no_art86') or row.get('_manual_art43'):continue
  for role in ('poster','fanart'):
   record=records.get(identity(portal,kind,row,role),{})
   if not record or revoked(record.get('source','')):continue
   file=validate(record)
   if file:result.setdefault(str(row['sid']),{})[role]=file
 return result

def encode(body,role):
 from media_sources43 import validate_image
 from PIL import Image
 validate_image(body)
 with Image.open(io.BytesIO(body)) as image:
  image.load();image.thumbnail((1024,1536) if role=='poster' else (1280,720))
  if image.mode not in ('RGB','RGBA'):image=image.convert('RGBA')
  out=io.BytesIO();image.save(out,format='PNG');raw=out.getvalue()
  if len(raw)>MAX_ASSET:
   image=image.convert('RGB');out=io.BytesIO();image.save(out,format='JPEG',quality=85);raw=out.getvalue()
  if len(raw)>MAX_ASSET:
   image.thumbnail((640,960) if role=='poster' else (960,540));out=io.BytesIO();image.save(out,format='JPEG',quality=80);raw=out.getvalue()
 if len(raw)>MAX_ASSET:raise OSError('POSTER_ASSET_QUOTA')
 width,height=validate_image(raw);return raw,width,height

def store(portal,kind,row,role,source,body,cancel=lambda:False):
 from logo_store89 import atomic
 from profile_transaction import writing
 from widget_assets69 import safe
 if kind not in ('vod','series') or role not in ('poster','fanart') or row.get('_no_art86') or row.get('_manual_art43') or not safe(portal,source):raise ValueError('POSTER_SCOPE')
 raw,width,height=encode(body,role)
 if __import__('external_art89').enabled():
  uri,facts=__import__('external_art89').store('poster',identity(portal,kind,row,role),raw,dict(source=source,role=role),cancel)
  return dict(uri=uri,storage='EXTERNAL_VERIFIED')
 root=location();digest=hashlib.sha256(raw).hexdigest();key=identity(portal,kind,row,role)
 with writing(timeout=.2):
  if cancel():raise InterruptedError('POSTER_CANCELLED')
  first=capacity(root,len(raw)+MAX_MANIFEST);file=root/(digest+'.img')
  if file.is_symlink():raise OSError('POSTER_UNSAFE_FILE')
  if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest()!=digest:atomic(file,raw)
  if hashlib.sha256(file.read_bytes()).hexdigest()!=digest:raise OSError('POSTER_READBACK')
  s=file.stat();records=manifest();records[key]=dict(sha256=digest,stamp=[s.st_mtime_ns,s.st_size],width=width,height=height,source=source,role=role,storage='PERSISTED_POSTER',at=time.time())
  data=json.dumps(dict(format=1,records=records),separators=(',',':')).encode()
  if len(records)>512 or len(data)>MAX_MANIFEST:raise OSError('POSTER_MANIFEST_QUOTA')
  if cancel():raise InterruptedError('POSTER_CANCELLED')
  if capacity(root,len(data)+65536).get('volume82')!=first.get('volume82'):raise OSError('POSTER_VOLUME_CHANGED')
  atomic(root/'manifest89.json',data)
  if manifest().get(key)!=records[key] or not validate(records[key]):raise OSError('POSTER_READBACK')
 return records[key]

def prepare(portal,kind,rows,cancel=lambda:False):
 if kind not in ('vod','series'):return
 from programme_assets47 import sources,local_uri
 from widget_assets69 import safe
 from widget_cache79 import read as kodi
 from programme_transport77 import verified
 from artwork_visible import public_dns
 from work_requests86 import pending
 external=__import__('external_art89').enabled();records=__import__('external_art89').records('poster') if external else manifest();local=kodi(portal,kind,rows)
 for sid,roles in __import__('widget_cache82').read(portal,kind,rows).items():local.setdefault(sid,{}).update(roles)
 # A full/offline cache is one capacity gate, not a failed HTTP job per item.
 try:
  if external:__import__('art_storage').check(MAX_ASSET+MAX_MANIFEST,limit=0,backend=__import__('external_art89').backend('poster'))
  else:capacity(location(),MAX_ASSET+MAX_MANIFEST)
 except OSError:return
 tasks=[]
 for row in rows[:12]:
  if row.get('_no_art86') or row.get('_manual_art43'):continue
  for role,source in sources(row,provider_only=True).items():
   if role in ('poster','fanart') and source:tasks.append((role!='poster',row,role,source))
 attempts=0;started=time.monotonic()
 for _,row,role,source in sorted(tasks,key=lambda v:v[0]):
  if cancel() or pending() or attempts>=2 or time.monotonic()-started>2:return
  key=identity(portal,kind,row,role);old=records.get(key,{})
  if old.get('source')==source:
   if external:
    try:
     if __import__('external_art89').confirm('poster',key,old):continue
    except OSError:return
   elif validate(old):continue
  tag=(key,hashlib.sha256(source.encode()).hexdigest())
  if time.monotonic()<_due.get(tag,0) or not safe(portal,source):continue
  attempts+=1
  try:
   # Capacity before networking prevents endless downloads on a full quota.
   if external:__import__('art_storage').check(MAX_ASSET+MAX_MANIFEST,limit=0,backend=__import__('external_art89').backend('poster'))
   else:capacity(location(),MAX_ASSET+MAX_MANIFEST)
   file=local.get(str(row['sid']),{}).get(role) or local_uri(source)
   if file:
    with open(file,'rb') as stream:body=stream.read(3*1024*1024+1)
   else:
    if not public_dns(source):raise OSError('POSTER_DNS_UNAVAILABLE')
    body=verified(source,cancel=lambda:cancel() or pending(),keep_data81=True)['_body81']
   store(portal,kind,row,role,source,body,lambda:cancel() or pending());_due.pop(tag,None)
  except (OSError,ValueError,TypeError,RuntimeError,__import__('media_sources43').SourceError):_due[tag]=time.monotonic()+300
  while len(_due)>256:_due.pop(next(iter(_due)))

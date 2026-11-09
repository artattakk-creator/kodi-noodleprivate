"""Durable exact-account/content/role render proofs on the existing art worker.

A short DNS lease is transport permission, never the lifetime of decoded local
pixels. No archive migration, eviction, Kodi DB write or profile reset.
"""
import hashlib,json,os,time,sqlite3
_due={};_records={}

def identity(portal,kind,row,role,source):
 from widget_assets69 import identity as key
 return key(portal,kind,row,role,source)

def root():
 from programme_art46 import root as folder
 return folder()

def metadata(key):return os.path.join(root(),'render81-'+key+'.json')

def read(key):
 try:
  name=metadata(key)
  if os.path.islink(name):return None
  info=os.stat(name);stamp=(info.st_mtime_ns,info.st_size)
  if info.st_size>16384:return None
  hit=_records.get(name)
  if hit and hit[0]==stamp:record=hit[1]
  else:
   with open(name,encoding='utf-8') as stream:record=json.loads(stream.read(16385))
   _records[name]=(stamp,record)
   while len(_records)>1024:_records.pop(next(iter(_records)))
  if not isinstance(record,dict) or record.get('key')!=key or not isinstance(record.get('at'),(int,float)):return None
  filename=record['file']
  if not isinstance(filename,str) or os.path.dirname(filename)!=root() or os.path.islink(filename):return None
  stat=os.stat(filename)
  if [stat.st_mtime_ns,stat.st_size]!=record.get('stamp') or not 0<stat.st_size<=3*1024*1024:return None
  return record
 except (OSError,ValueError,TypeError,KeyError):return None

def store(key,data,enrich=None):
 from media_sources43 import validate_image
 from programme_art46 import atomic,space
 __import__('artwork_health82').guard()
 os.makedirs(root(),mode=0o700,exist_ok=True)
 if os.path.islink(root()):raise OSError('UNSAFE_RENDER_ROOT')
 width,height=validate_image(data);sha=hashlib.sha256(data).hexdigest()
 previous=read(key)
 if previous and previous.get('sha256')==sha and enrich is None:return previous
 filename=os.path.join(root(),'render81-'+key+'-'+sha+('.png' if data.startswith(b'\x89PNG') else '.jpg'))
 if os.path.islink(filename):raise OSError('UNSAFE_RENDER_FILE')
 if not os.path.isfile(filename):space(len(data)+8192);atomic(filename,data)
 with open(filename,'rb') as stream:
  if hashlib.sha256(stream.read(3*1024*1024+1)).hexdigest()!=sha:raise ValueError('RENDER_HASH_MISMATCH')
 stat=os.stat(filename);record=dict(key=key,file=filename,sha256=sha,stamp=[stat.st_mtime_ns,stat.st_size],width=width,height=height,at=time.time(),state='DISK_PERSISTED')
 if enrich:record.update(enrich(record))
 atomic(metadata(key),json.dumps(record,separators=(',',':')).encode())
 return record

def edition(portal,kind,row,role):
 return identity(portal,kind,row,role,json.dumps([row.get('name'),row.get('year')],sort_keys=True))

def record_for(portal,kind,row,role,source):
 from widget_refs74 import revoked
 if source and revoked(source):return None
 return (read(identity(portal,kind,row,role,source)) if source else None) or read(edition(portal,kind,row,role))

def references(portal,kind,rows):
 from programme_assets47 import sources
 result={}
 for row in rows:
  for role,source in sources(row,provider_only=True).items():
   value=record_for(portal,kind,row,role,source)
   if value:result.setdefault(str(row['sid']),{})[role]=value['file']
 return result


def prepare(portal,kind,rows,cancel=lambda:False):
 """Existing provider worker only: at most two acquisitions, bounded backoff."""
 from programme_assets47 import sources,local_uri
 from widget_assets69 import safe
 from media_art import cached
 from media_sources43 import SourceError
 from programme_transport77 import verified
 from programme_writes69 import classify
 from artwork_visible import public_dns
 acquired=0;started=time.monotonic()
 for row in rows:
  for role,source in sources(row,provider_only=True).items():
   if cancel() or acquired>=2 or time.monotonic()-started>2:return
   if not source:continue
   key=identity(portal,kind,row,role,source)
   if read(key) or time.monotonic()<_due.get(key,(0,0))[0]:continue
   acquired+=1
   try:
    __import__('artwork_health82').guard()
    local=local_uri(source) or local_uri(cached(source))
    if not local:
     from widget_cache79 import probe
     prior=probe(source) if safe(portal,source) else None
     local=prior.get('file') if prior else None
    if local:
     with open(local,'rb') as stream:data=stream.read(3*1024*1024+1)
    else:
     if not safe(portal,source):raise SourceError('UNSAFE_SOURCE')
     if not public_dns(source):raise SourceError('DNS_UNAVAILABLE')
     response=verified(source,cancel=cancel,keep_data81=True);data=response['_body81']
    if cancel():return
    record=store(key,data)
    from programme_art46 import atomic
    alias=edition(portal,kind,row,role)
    record=dict(record,key=alias,source81=hashlib.sha256(source.encode()).hexdigest())
    atomic(metadata(alias),json.dumps(record,separators=(',',':')).encode())
    _due.pop(key,None)
   except sqlite3.Error as error:
    raise __import__('artwork_health82').defer(error) from None
   except (OSError,ValueError,TypeError,RuntimeError,KeyError,SourceError) as error:
    if isinstance(error,__import__('artwork_health82').Deferred):raise
    count=min(3,_due.get(key,(0,0))[1]+1);_due[key]=(time.monotonic()+(60,300,21600)[count-1],count)
    from art_trace81 import note
    from programme_art46 import CacheBudget
    reason=getattr(error,'reason','')
    code='PROGRAMME_CACHE_BUDGET' if isinstance(error,CacheBudget) else reason if reason in ('RESERVE_BLOCKED','BLOCKED_REAL_DISK','CAPACITY_UNKNOWN','BUDGET_FULL') else getattr(error,'code',None) or classify(error)
    capacity=getattr(error,'storage',{}) or {}
    note(dict(key=key),'CACHE',code,count=count,free=capacity.get('free'),reserve=capacity.get('reserve'),budget=capacity.get('budget'))
   while len(_due)>512:_due.pop(next(iter(_due)))

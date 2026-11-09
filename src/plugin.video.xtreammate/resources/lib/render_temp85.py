"""Bounded new Home cover/hero bytes, same existing worker and source identities.

Legacy archives remain read-only here. Readers consume short RAM receipts;
only the worker decodes/hashes or changes the owned temporary journal.
"""
import hashlib,json,os,time
from media_sources43 import SourceError
PREFIX='XCMate.RenderTemp85.'
_records={};_due={}
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def slot(key):
 from epg_handoff63 import profile_scope
 return PREFIX+hashlib.sha256((profile_scope()+key).encode()).hexdigest()
def publish(key,record):
 from epg_handoff63 import profile_scope
 raw=json.dumps(dict(key=key,profile=profile_scope(),until=time.time()+30,record=record),separators=(',',':'))
 if len(raw.encode())>8192:raise ValueError('TEMP_RECORD_LIMIT')
 window().setProperty(slot(key),raw)
 _records[key]=record
 while len(_records)>256:
  old=next(iter(_records));_records.pop(old);window().clearProperty(slot(old))
def read(key):
 from epg_handoff63 import profile_scope
 try:
  raw=window().getProperty(slot(key));value=json.loads(raw) if raw and len(raw.encode())<=8192 else {}
  if value.get('key')==key and value.get('profile')==profile_scope() and 0<value.get('until',0)-time.time()<=30:
   record=value['record']
   from artwork_temp85 import present,touch
   if present(record.get('sha256')):touch(record['sha256']);return record
 except (AttributeError,RuntimeError,ValueError,TypeError,KeyError):pass
 return None
def recover(key):
 hit=read(key)
 if hit:
  __import__('artwork_temp85').touch(hit.get('sha256'));return hit
 from artwork_temp85 import cache,touch
 c=cache()
 try:
  result=c.context('render81:'+key)
  if not result:return None
  filename=result['image'];s=os.stat(filename)
  __import__('artwork_temp85').presence(result['sha256'],True)
  result.update(file=filename,stamp=[s.st_mtime_ns,s.st_size],temporary85=True)
  touch(result['sha256']);publish(key,result);return result
 except (SourceError,OSError,ValueError,TypeError,KeyError):return None
def store(key,data,enrich=None):
 from artwork_temp85 import cache,Unavailable,touch
 from media_sources43 import validate_image
 from import_budget import check_space
 from art_storage import capacity
 c=cache();width,height=validate_image(data);digest=hashlib.sha256(data).hexdigest();filename=str(c.root/(digest+('.png' if data.startswith(b'\x89PNG') else '.jpg')))
 result=dict(key=key,file=filename,sha256=digest,width=width,height=height,at=time.time(),state='DISK_PERSISTED',temporary85=True)
 if enrich:result.update(enrich(result))
 def guard(size):
  values=capacity(str(c.root))
  if values.get('storage_availability')!='AVAILABLE' or values.get('free',0)<values.get('reserve',1024**3)+size:raise Unavailable('TEMP_RESERVE_BLOCKED')
  check_space(str(c.root),size)
 try:c.put(data,pin=key,pin_until=time.time()+60,check=guard,context='render81:'+key,reference=result)
 except Unavailable as error:raise __import__('programme_art46').CacheBudget(str(error)) from None
 s=os.stat(filename);result['stamp']=[s.st_mtime_ns,s.st_size];touch(digest);publish(key,result);return result
def alias(key,record):
 with open(record['file'],'rb') as f:data=f.read(3*1024*1024+1)
 return store(key,data,lambda current:{k:v for k,v in dict(record,key=key).items() if k not in ('file','sha256','stamp','at')})
def prepare(portal,kind,rows,cancel=lambda:False):
 from programme_assets47 import sources
 from widget_assets69 import safe,identity
 from programme_transport77 import verified
 from artwork_visible import public_dns
 from artwork_health82 import status
 if status().get('code')=='DB_MANUAL_PAUSE':return
 if kind=='live':rows=__import__('programme_prefetch48').visible75(portal,rows)
 acquired=0;started=time.monotonic();visible=[]
 for row in rows:
  for role,source in sources(row,provider_only=True).items():
   if cancel() or time.monotonic()-started>2:break
   if not source:continue
   key=identity(portal,kind,row,role,source)
   record=recover(key)
   if record:visible.append(record['sha256']);continue
   if acquired>=2 or time.monotonic()<_due.get(key,0) or not safe(portal,source):continue
   # Existing archive/Kodi records are reused without copying or migration.
   from render_cache81 import record_for
   old=record_for(portal,kind,row,role,source)
   if old:continue
   acquired+=1
   try:
    if not public_dns(source):continue
    response=verified(source,cancel=cancel,keep_data81=True)
    if cancel():return
    record=store(key,response['_body81']);visible.append(record['sha256']);_due.pop(key,None)
   except (SourceError,OSError,ValueError,TypeError,RuntimeError):_due[key]=time.monotonic()+60
   while len(_due)>256:_due.pop(next(iter(_due)))
 remember_visible(portal,kind,visible)

def remember_visible(portal,kind,values):
 from epg_handoff63 import profile_scope
 import home_schedule75
 portals=home_schedule75._read(home_schedule75.KEY).get('portals85',[])
 if str(portal['id']) not in portals or kind not in ('live','vod','series'):return
 slot=portals.index(str(portal['id']))*3+('live','vod','series').index(kind)
 record=dict(profile=profile_scope(),pid=str(portal['id']),hashes=list(dict.fromkeys(values))[:24],at=time.time())
 window().setProperty('XCMate.VisibleTemp85.'+str(slot),json.dumps(record,separators=(',',':')))
def pin_visible():
 from epg_handoff63 import profile_scope
 from artwork_temp85 import touch
 import home_schedule75
 portals=home_schedule75._read(home_schedule75.KEY).get('portals85',[])
 for i in range(12):
  try:
   raw=window().getProperty('XCMate.VisibleTemp85.'+str(i));record=json.loads(raw) if raw and len(raw)<4096 else {}
   if record.get('profile')!=profile_scope() or record.get('pid') not in portals or not 0<=time.time()-record.get('at',0)<3600:continue
   for digest in record.get('hashes',[])[:24]:touch(digest)
  except (ValueError,TypeError):continue

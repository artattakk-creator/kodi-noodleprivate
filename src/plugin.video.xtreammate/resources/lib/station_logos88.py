"""Station-only protocol adapter; strict public pinned HTTP(S) or owned VFS.

No provider credentials, private hosts, redirects to arbitrary origins, or
filesystem traversal. Download runs on the existing provider worker, never GUI.
"""
import hashlib,os,time
from pathlib import Path
from urllib.parse import urlsplit,unquote
_due={};_cursor={}
def source(row):return __import__('station_logos87').source(row)
def normalize(uri):
 if not isinstance(uri,str) or len(uri)>2048 or any(ord(c)<32 for c in uri) or any(c in uri for c in ('\\','|')):raise ValueError('UNSAFE_SOURCE')
 if uri.startswith('image://'):
  uri=unquote(uri[8:].removesuffix('/'))
  if uri.startswith('image://'):raise ValueError('UNSAFE_SOURCE')
 return uri
def network_safe(portal,uri):
 from artwork_visible import syntactic
 from programme_url77 import public_query
 try:
  p=urlsplit(uri)
  origin=urlsplit(str(portal.get('xc_host') or ''))
  exact_provider=(p.scheme,p.hostname,p.port)==(origin.scheme,origin.hostname,origin.port)
  if not syntactic(uri) or p.scheme not in ('http','https') or (p.port not in (None,80 if p.scheme=='http' else 443) and not exact_provider) or p.fragment or not public_query(p.query):return False
  path=unquote(p.path)
  if any(v in ('.','..') for v in path.split('/')) or any(c in path for c in ('\\','|','@')):return False
  return __import__('station_logos87').blocked_reason(portal,uri)!='AUTH_SCOPE'
 except (ValueError,TypeError):return False
def local_file(uri):
 import xbmcvfs,xbmcaddon
 uri=normalize(uri)
 if '..' in unquote(uri).replace('\\','/').split('/'):raise ValueError('UNSAFE_SOURCE')
 if '://' in uri and not uri.startswith(('special://home/','special://profile/','special://thumbnails/')):raise ValueError('UNSAFE_VFS')
 file=Path(xbmcvfs.translatePath(uri))
 roots=[Path(xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'))/'resources/media',Path(xbmcvfs.translatePath('special://thumbnails/'))]
 try:
  from logo_manifest86 import location
  roots.append(Path(location()[0].root))
 except OSError:pass
 if not file.is_absolute() or file.is_symlink() or any(p.is_symlink() for p in file.parents) or not any(file.is_relative_to(r.resolve()) for r in roots):raise ValueError('UNSAFE_VFS')
 return str(file)
def fetch(portal,uri,cancel=lambda:False,connect=None,resolver=None):
 from media_sources43 import SourceError,MAX_IMAGE,validate_image
 uri=normalize(uri)
 if not uri.startswith(('http://','https://')):
  filename=local_file(uri)
  import xbmcvfs
  f=xbmcvfs.File(filename)
  try:body=bytes(f.readBytes(MAX_IMAGE+1))
  finally:f.close()
  validate_image(body);return body
 if not network_safe(portal,uri):raise SourceError('UNSAFE_SOURCE')
 from download_redirect import addresses,_connect
 from image_redirect48 import open_image
 origin=urlsplit(uri);response=None;end=time.monotonic()+12
 def guarded(target,ips,headers):
  p=urlsplit(target)
  # Same hostname only; HTTP may upgrade to HTTPS, never downgrade. This
  # narrow logo policy does not widen the shared event/CDN allowlist.
  if p.hostname!=origin.hostname or not network_safe(portal,target) or origin.scheme=='https' and p.scheme!='https':raise SourceError('REDIRECT_BLOCKED')
  return (connect or _connect)(target,ips,headers)
 try:
  response=open_image(uri,{'User-Agent':'XCMate station logos','Accept':'image/png,image/jpeg','Accept-Encoding':'identity'},guarded,resolver or addresses,cancel,end)
  if response.status!=200:raise SourceError('HTTP_AUTH' if response.status in (401,403) else 'HTTP_NOT_FOUND' if response.status in (404,410) else 'HTTP_SERVER')
  if response.headers.get('Content-Type','').partition(';')[0].lower() not in ('image/jpeg','image/png'):raise SourceError('CONTENT_TYPE')
  if response.headers.get('Content-Encoding','identity').lower() not in ('identity',''):raise SourceError('CONTENT_ENCODING')
  data=bytearray()
  while True:
   if cancel():raise SourceError('CANCELLED')
   if time.monotonic()>end:raise SourceError('TIMEOUT')
   part=response.read(min(65536,MAX_IMAGE-len(data)+1))
   if not part:break
   data.extend(part)
   if len(data)>MAX_IMAGE:raise SourceError('IMAGE_LIMIT')
  body=bytes(data);validate_image(body);return body
 finally:
  if response is not None:response.close()
def read(portal,rows):
 from logo_manifest86 import key
 from decoded_assets88 import read as cached
 from widget_refs74 import revoked
 result={}
 for row in rows[:256]:
  record=cached(key(portal,row))
  if record and not revoked(source(row)):result[str(row['sid'])]=record['uri']
 return result
def prepare(portal,rows,cancel=lambda:False):
 from logo_manifest86 import context,key,load,location,read as manifest_read,_save
 from media_sources43 import SourceError,validate_image
 from art_storage import check
 from station_logos87 import note
 existing=manifest_read(portal,rows);scope=context(portal);offset=_cursor.get(scope,0);attempts=0;changed=False
 try:backend,path=location();records=load(portal,all_records=True)
 except OSError:backend=None;records={}
 for row in rows[offset:]+rows[:offset]:
  if cancel() or attempts>=2:break
  tag=key(portal,row);uri=source(row)
  _cursor[scope]=(rows.index(row)+1)%len(rows)
  if not uri:note(portal,row,'SOURCE_MISSING');continue
  if str(row['sid']) in existing:continue
  if time.monotonic()<_due.get(tag,0):continue
  attempts+=1;_due[tag]=time.monotonic()+60
  try:
   body=fetch(portal,uri,cancel)
   # Decode first and publish bounded session bytes regardless of archive
   # reserve. Never call the RAM receipt PERSISTED/LOCAL_READY.
   record=__import__('decoded_assets88').put(tag,body,time.time()+86400,kind='logo')
   note(portal,row,'TEXTURE_CACHED')
   if backend is None:continue
   check(len(body)+65536,limit=0,backend=backend)
   digest=record['sha256'];backend.write_verified(digest,body,lambda raw:bool(validate_image(raw)))
   stat=os.stat(backend.resolve_target(digest))
   records[tag]=dict(context=scope,sha256=digest,stamp=[stat.st_mtime_ns,stat.st_size],width=record['width'],height=record['height']);changed=True
  except (OSError,ValueError,TypeError,SourceError) as error:
   reason=getattr(error,'reason','');code=getattr(error,'code','')
   stage='STORAGE_RESERVE_BLOCKED' if reason in ('RESERVE_BLOCKED','BLOCKED_REAL_DISK') or code in ('DISK_FULL','SPACE_FULL') else 'AUTH_SCOPE' if code=='HTTP_AUTH' else 'IMAGE_INVALID' if code in ('INVALID_IMAGE','IMAGE_LIMIT','CONTENT_TYPE') else 'DOWNLOAD_FAILED'
   note(portal,row,stage,**{k:v for k,v in getattr(error,'storage',{}).items() if k in ('reserve','budget','free')})
 if changed:
  try:_save(backend,path,records)
  except (OSError,TimeoutError):pass
 while len(_due)>512:_due.pop(next(iter(_due)))
 while len(_cursor)>16:_cursor.pop(next(iter(_cursor)))
 hits=manifest_read(portal,rows)
 return 'READY' if len(hits)==len(rows) else 'PARTIAL' if hits else 'EXTERNAL_UNAVAILABLE'

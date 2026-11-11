"""Station-only protocol adapter; strict public pinned HTTP(S) or owned VFS.

No provider credentials, private hosts, redirects to arbitrary origins, or
filesystem traversal. Download runs on the existing provider worker, never GUI.
"""
import hashlib,os,time
from pathlib import Path
from urllib.parse import urlsplit,unquote
_due={};_cursor={};_cache_cursor={}
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
 from download_sources import DownloadFailure
 import http.client
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
 except SourceError:raise
 except (DownloadFailure,OSError,http.client.HTTPException,ValueError) as error:
  raw_code=str(getattr(error,'code',''))
  code='UNSAFE_SOURCE' if raw_code.startswith('REDIRECT_') else 'DNS_ERROR' if raw_code=='DNS_ERROR' else __import__('art_errors').classify(error)
  raise SourceError(code) from None
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
 existing=manifest_read(portal,rows,with_fallback=False);scope=context(portal);offset=_cursor.get(scope,0);attempts=0;changed=False
 if __import__('external_art89').enabled():
  try:__import__('external_art89').backend('logo')
  except OSError:return 'EXTERNAL_UNAVAILABLE'
 try:backend,path=location();records=load(portal,all_records=True)
 except OSError:backend=None;records={}
 for row in rows[:5]+rows[max(5,offset):]+rows[5:max(5,offset)]:
  if cancel() or attempts>=2:break
  tag=key(portal,row);uri=source(row)
  _cursor[scope]=(rows.index(row)+1)%len(rows)
  if not uri:note(portal,row,'SOURCE_MISSING');continue
  if str(row['sid']) in existing and any(v.get('stable89')==__import__('logo_store89').identity(portal,row) for v in records.values()):continue
  if str(row['sid']) in existing and __import__('external_art89').enabled():
   external89=__import__('external_art89');ident89=external89.key(portal,'logo',row);record89=external89.records('logo').get(ident89)
   if record89:
    try:
     if external89.confirm('logo',ident89,record89):continue
    except OSError:return 'EXTERNAL_UNAVAILABLE'
  if time.monotonic()<_due.get(tag,0):continue
  attempts+=1;_due[tag]=time.monotonic()+60;body=None
  try:
   local89=manifest_read(portal,[row]).get(str(row['sid']),'')
   if local89.startswith('/'):
    with open(local89,'rb') as stream:body=stream.read(3*1024*1024+1)
   else:
    ram89=__import__('decoded_assets88').read(tag)
    if ram89:
     import urllib.request
     opener89=urllib.request.build_opener(urllib.request.ProxyHandler({}))
     with opener89.open(ram89['uri'],timeout=2) as reply89:body=reply89.read(3*1024*1024+1)
    else:body=fetch(portal,uri,cancel)
   if backend is None and not __import__('external_art89').enabled():raise OSError('LOGO_LOCAL_REQUIRED')
   _,facts89=__import__('logo_store89').persist(portal,row,body,cancel)
   __import__('logo_store89').note('PERSISTED_VERIFIED',**facts89)
   note(portal,row,'PERSISTED_VERIFIED',**{k:v for k,v in facts89.items() if k in ('free','reserve')})
  except (OSError,ValueError,TypeError,SourceError) as error:
   if body:
    try:
     __import__('decoded_assets88').put(tag,body,time.time()+86400,kind='logo')
     note(portal,row,'DECODED_RAM_READY')
    except (OSError,ValueError,TypeError,SourceError):pass
   __import__('logo_store89').note(str(error))
   reason=getattr(error,'reason','');code=getattr(error,'code','')
   stage='STORAGE_RESERVE_BLOCKED' if str(error).startswith(('LOGO_SAFETY_FLOOR','LOGO_CACHE_QUOTA','LOGO_VOLUME_UNVERIFIED')) else 'STORAGE_RESERVE_BLOCKED' if reason in ('RESERVE_BLOCKED','BLOCKED_REAL_DISK') or code in ('DISK_FULL','SPACE_FULL') else 'AUTH_SCOPE' if code=='HTTP_AUTH' else 'IMAGE_INVALID' if code in ('INVALID_IMAGE','IMAGE_LIMIT','CONTENT_TYPE') else 'DOWNLOAD_FAILED'
   note(portal,row,stage,**{k:v for k,v in getattr(error,'storage',{}).items() if k in ('reserve','budget','free')})
 if changed:
  try:_save(backend,path,records)
  except (OSError,TimeoutError):pass
 while len(_due)>512:_due.pop(next(iter(_due)))
 while len(_cursor)>16:_cursor.pop(next(iter(_cursor)))
 hits=manifest_read(portal,rows)
 return 'READY' if len(hits)==len(rows) else 'PARTIAL' if hits else 'EXTERNAL_UNAVAILABLE'

def reference(props):
 """UI-only exact station/account receipt, never a general localhost grant."""
 from portals import get_by_id
 from logo_manifest86 import key
 pid=str(props.get('XCMate.PortalId',''));sid=str(props.get('XCMate.MediaId',''));portal=get_by_id(pid)
 uri=props.get('XCMate.ProgrammeLogo46','');tag=props.get('XCMate.LogoProof88','');original=props.get('XCMate.LogoSource88','')
 if not portal or not sid or not original or key(portal,dict(sid=sid,stream_icon=original))!=tag:return ''
 if uri.startswith('smb://'):
  return uri if __import__('external_art89').references(portal,'logo',[dict(sid=sid,stream_icon=original)]).get(sid)==uri else ''
 return uri if __import__('decoded_assets88').valid(tag,uri) else ''

def cached_capability(uri,key):
 """Recognize our exact account/source-addressed prior Kodi cache reference.

 The random capability remains unguessable. Its suffix is only a SHA256 of
 the already scoped source key, never a raw provider URL/account/token.
 """
 import re
 try:
  if uri.startswith('image://'):uri=unquote(uri[8:].removesuffix('/'))
  from artwork_visible import KODI_OPTIONS
  if uri.endswith(KODI_OPTIONS):uri=uri[:-len(KODI_OPTIONS)]
  parsed=urlsplit(uri);suffix=hashlib.sha256(key.encode()).hexdigest()
  return bool(parsed.scheme=='http' and parsed.hostname=='127.0.0.1' and parsed.username is None and parsed.password is None and parsed.port and 1<=parsed.port<=65535 and not parsed.query and not parsed.fragment and re.fullmatch(r'/xcmate88/[a-f0-9]{64}/'+suffix+r'\.(png|jpg)',parsed.path))
 except (ValueError,TypeError,AttributeError):return False

def recover(portal,rows,cancel=lambda:False):
 """Read-only cold/warm reuse of Kodi's real decoded scoped logo files.

 No HTTP, DNS, copied files, own JSON/SQLite writes or archive reserve bypass.
 A cached reference is not proof that the current Android control rendered it.
 """
 import json
 import xbmc
 from logo_manifest86 import key
 from widget_cache82 import decoded,remember
 scope=__import__('logo_manifest86').context(portal);offset=_cache_cursor.get(scope,5)
 selected=rows[:5]+rows[offset:offset+11]
 _cache_cursor[scope]=offset+11 if offset+11<len(rows) else 5
 while len(_cache_cursor)>16:_cache_cursor.pop(next(iter(_cache_cursor)))
 ready=__import__('station_logos87').read(portal,selected)
 selected=[row for row in selected if str(row['sid']) not in ready]
 tags={hashlib.sha256(key(portal,row).encode()).hexdigest():row for row in selected}
 if not tags or cancel():return
 try:
  # The suffix survives Kodi restarts even though the loopback port/random
  # capability does not. Filtering is by hash only; full URI grammar, account,
  # source identity, local root and complete image decode are checked below.
  raw=xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=88,method='Textures.GetTextures',params=dict(filter={'or':[dict(field='url',operator='contains',value=tag) for tag in tags]},properties=['url','cachedurl','sizes']))))
  if not isinstance(raw,str) or len(raw)>262144:return
  textures=json.loads(raw).get('result',{}).get('textures',[])
  if not isinstance(textures,list):return
  for texture in textures[:64]:
   if cancel():return
   if not isinstance(texture,dict):continue
   uri=texture.get('url','');row=next((r for tag,r in tags.items() if tag in uri and cached_capability(uri,key(portal,r))),None)
   if row is None:continue
   record=decoded(texture,uri)
   if not record or record['width']>2048 or record['height']>2048:continue
   record['source']=source(row);remember(portal,'live',row,'poster',source(row),record)
   stat=os.stat(record['file']);tag=key(portal,row)
   value=dict(file=record['file'],stamp=[stat.st_mtime_ns,stat.st_size],source_hash=hashlib.sha256(source(row).encode()).hexdigest())
   old=__import__('station_logos87');slot=old.PREFIX+tag;old.window().setProperty(slot,json.dumps(value,separators=(',',':')))
   if slot not in old._keys:old._keys.append(slot)
   while len(old._keys)>512:old.window().clearProperty(old._keys.pop(0))
   old.note(portal,row,'TEXTURE_CACHED')
 except (OSError,ValueError,TypeError,AttributeError,RuntimeError):return

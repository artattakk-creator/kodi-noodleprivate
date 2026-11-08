"""Exact provider -> existing Kodi thumbnail recovery, without new archives.

Worker: query Kodi's texture index, decode and hash an existing local image.
Readers: bounded private journal + verified file stamp. Never fetch, migrate,
change artwork mode, write Kodi DBs or remove any image. No remote stale lease.
"""
import hashlib,json,os,tempfile,time,threading
from pathlib import Path
_lock=threading.RLock();_due={};_cache={};_cursor={}
LIMIT=512*1024

def path(portal,kind):
 from widget_refs74 import path as old
 filename,context=old(portal,kind)
 return filename.replace('widget-refs74-','widget-textures79-'),context

def load(portal,kind):
 filename,context=path(portal,kind)
 try:
  stamp=os.stat(filename);hit=_cache.get(filename)
  if hit and hit[0]==(stamp.st_mtime_ns,stamp.st_size):value=hit[1]
  else:
   if os.path.islink(filename) or stamp.st_size>LIMIT:return {}
   with open(filename,encoding='utf-8') as stream:value=json.loads(stream.read(LIMIT+1))
   with _lock:
    _cache[filename]=((stamp.st_mtime_ns,stamp.st_size),value)
    while len(_cache)>16:_cache.pop(next(iter(_cache)))
  if not isinstance(value,dict) or not isinstance(value.get('refs'),dict):return {}
  if any(not isinstance(roles,dict) or any(not isinstance(record,dict) for record in roles.values()) for roles in value['refs'].values()):return {}
  return value if value.get('context')==context else {}
 except (OSError,ValueError,TypeError):return {}

def permitted(filename):
 import xbmcvfs
 try:
  target=Path(filename);root=Path(xbmcvfs.translatePath('special://thumbnails/')).resolve()
  if not target.is_absolute() or target.is_symlink() or root not in target.resolve().parents:return False
  return all(not p.is_symlink() for p in target.parents if p!=root.parent)
 except (OSError,ValueError,RuntimeError,AttributeError):return False

def valid(value,source):
 try:
  if value.get('source')!=source or value.get('state')!='POSITIVE_LOCAL' or not 0<=time.time()-value['at']<30*86400:return False
  filename=value['file']
  if not permitted(filename):return False
  st=os.stat(filename)
  return 0<st.st_size<=3*1024*1024 and [st.st_mtime_ns,st.st_size]==value.get('stamp') and len(value.get('sha256',''))==64
 except (OSError,KeyError,ValueError,TypeError):return False

def read(portal,kind,rows):
 from programme_assets47 import sources
 records=load(portal,kind).get('refs',{});result={}
 for row in rows[:256]:
  sid=str(row['sid'])
  for role,source in sources(row,provider_only=True).items():
   value=records.get(sid,{}).get(role,{})
   if valid(value,source):result.setdefault(sid,{})[role]=value['file']
 return result

def probe(source):
 import xbmc,xbmcvfs
 from artwork_visible import KODI_OPTIONS
 from urllib.parse import quote,unquote
 # Kodi stores image:// wrappers with lowercase percent escapes, including
 # its HTTP options. Keep the source itself case-sensitive.
 import re
 urls=[source+KODI_OPTIONS,source]
 for original in (source+KODI_OPTIONS,source):
  encoded=quote(original,safe='')
  urls.extend(('image://'+encoded+'/', 'image://'+re.sub(r'%[0-9A-F]{2}',lambda m:m[0].lower(),encoded)+'/'))
 for url in dict.fromkeys(urls):
  request=dict(jsonrpc='2.0',id=79,method='Textures.GetTextures',params=dict(filter=dict(field='url',operator='is',value=url),properties=['url','cachedurl','sizes']))
  response=json.loads(xbmc.executeJSONRPC(json.dumps(request)))
  for row in response.get('result',{}).get('textures',[])[:4]:
   if row.get('url')!=url:continue
   cached=row.get('cachedurl','')
   if not isinstance(cached,str) or not cached:continue
   if cached.startswith('image://'):cached=unquote(cached[len('image://'):].removesuffix('/'))
   if '..' in Path(cached).parts or '://' in cached and not cached.startswith('special://'):continue
   filename=xbmcvfs.translatePath(cached if cached.startswith('special://') else 'special://thumbnails/'+cached) if not os.path.isabs(cached) else cached
   if not permitted(filename):continue
   try:st=os.stat(filename)
   except OSError:continue
   if not 0<st.st_size<=3*1024*1024:continue
   from PIL import Image
   try:
    with Image.open(filename) as im:
     if im.width*im.height>16_000_000 or im.width<1 or im.height<1:continue
     im.load();width,height=im.size
   except (Image.DecompressionBombError,OSError,ValueError,MemoryError):continue
   with open(filename,'rb') as stream:digest=hashlib.sha256(stream.read(3*1024*1024+1)).hexdigest()
   after=os.stat(filename)
   if (st.st_mtime_ns,st.st_size)!=(after.st_mtime_ns,after.st_size):continue
   return dict(source=source,file=filename,sha256=digest,stamp=[st.st_mtime_ns,st.st_size],width=width,height=height,at=time.time(),state='POSITIVE_LOCAL',etag=None)
 return None

def prepare(portal,kind,rows):
 from programme_assets47 import sources
 from widget_assets69 import safe
 if kind not in ('live','vod','series') or not rows:return
 filename,context=path(portal,kind);now=time.monotonic()
 if os.path.islink(filename):return
 with _lock:
  if now<_due.get(context,0):return
  _due[context]=now+15
  while len(_due)>32:_due.pop(next(iter(_due)))
 value=load(portal,kind);records=value.get('refs',{});changed=False;end=now+.35
 selected=rows[:24];cursor=_cursor.get(context,0)%len(selected)
 for offset in range(len(selected)):
  if time.monotonic()>end:break
  row=selected[(cursor+offset)%len(selected)];sid=str(row['sid']);_cursor[context]=(cursor+offset+1)%len(selected)
  for role,source in sources(row,provider_only=True).items():
   if not safe(portal,source):continue
   prior=records.get(sid,{}).get(role,{})
   if valid(prior,source) and time.time()-prior['at']<3600:continue
   try:positive=probe(source)
   except (OSError,ValueError,TypeError,RuntimeError,AttributeError):positive=None
   if positive:records.setdefault(sid,{})[role]=positive;changed=True
 if not changed:return
 # Bound metadata only. Existing Kodi thumbnails are never deleted.
 records=dict(list(records.items())[-256:]);raw=json.dumps(dict(context=context,refs=records),separators=(',',':')).encode()
 if len(raw)>LIMIT:return
 from profile_transaction import writing
 with writing(timeout=.1):
  fd,temp=tempfile.mkstemp(prefix='.widget-textures79-',dir=os.path.dirname(filename))
  try:
   with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
   os.replace(temp,filename)
  finally:
   if os.path.exists(temp):os.unlink(temp)

"""Batch recovery of existing Kodi pixels, independent of the artwork DB.

Only exact current public sources and decoded files below Kodi's texture root.
Never fetches, copies/deletes an image or writes Kodi's databases. A small
receipt uses the existing import reserve; RAM receipts remain useful if full.
"""
import hashlib,json,os,re,tempfile,threading,time
from pathlib import Path
from urllib.parse import quote,unquote
_due={};_cursor={};_ramkeys={};_lock=threading.RLock()
PREFIX='XCMate.LocalArt82.'

def variants(source):
    from artwork_visible import KODI_OPTIONS
    urls=[source,source+KODI_OPTIONS]
    for original in list(urls):
        encoded=quote(original,safe='')
        urls.extend(('image://'+encoded+'/', 'image://'+re.sub(r'%[0-9A-F]{2}',lambda m:m[0].lower(),encoded)+'/'))
    return list(dict.fromkeys(urls))

def scope(portal,kind,row,role,source):
    from widget_assets69 import identity
    return identity(portal,kind,row,role,source)

def slot(key):return PREFIX+key

def remember(portal,kind,row,role,source,record):
    import xbmcgui
    key=scope(portal,kind,row,role,source)
    window=xbmcgui.Window(10000)
    window.setProperty(slot(key),json.dumps(dict(key82=key,record=record),separators=(',',':')))
    with _lock:
        _ramkeys.pop(key,None);_ramkeys[key]=True
        while len(_ramkeys)>4096:
            oldest=next(iter(_ramkeys));_ramkeys.pop(oldest);window.clearProperty(slot(oldest))

def read(portal,kind,rows):
    import xbmcgui
    from programme_assets47 import sources
    from widget_cache79 import valid
    result={};window=xbmcgui.Window(10000)
    for row in rows[:256]:
        for role,source in sources(row,provider_only=True).items():
            key=scope(portal,kind,row,role,source)
            try:
                raw=window.getProperty(slot(key));data=json.loads(raw) if raw and len(raw)<4096 else {}
                if data.get('key82')==key and valid(data.get('record',{}),source):result.setdefault(str(row['sid']),{})[role]=data['record']['file']
            except (ValueError,TypeError,AttributeError):continue
    return result

def decoded(texture,source):
    import xbmcvfs
    from widget_cache79 import permitted
    from media_sources43 import validate_image,SourceError
    cached=texture.get('cachedurl','')
    if not isinstance(cached,str) or not cached:return None
    if cached.startswith('image://'):cached=unquote(cached[8:].removesuffix('/'))
    if '..' in Path(cached).parts or '://' in cached and not cached.startswith('special://'):return None
    filename=xbmcvfs.translatePath(cached if cached.startswith('special://') else 'special://thumbnails/'+cached) if not os.path.isabs(cached) else cached
    if not permitted(filename):return None
    try:
        before=os.stat(filename)
        if not 0<before.st_size<=3*1024*1024:return None
        with open(filename,'rb') as stream:body=stream.read(3*1024*1024+1)
        width,height=validate_image(body);after=os.stat(filename)
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):return None
        return dict(source=source,file=filename,sha256=hashlib.sha256(body).hexdigest(),stamp=[after.st_mtime_ns,after.st_size],width=width,height=height,at=time.time(),state='POSITIVE_LOCAL')
    except (OSError,ValueError,SourceError):return None

def save(portal,kind,found):
    if not __import__('artwork_display84').metadata_allowed():return
    from widget_cache79 import path,load,LIMIT
    from profile_transaction import writing
    from import_budget import check_space
    filename,context=path(portal,kind)
    with writing(timeout=.1):
        if os.path.islink(filename):return
        value=load(portal,kind);records=value.get('refs',{})
        for sid,role,record in found:records.setdefault(str(sid),{})[role]=record
        records=dict(list(records.items())[-256:])
        raw=json.dumps(dict(context=context,refs=records),separators=(',',':')).encode()
        if len(raw)>LIMIT:return
        check_space(filename,len(raw)+65536)
        fd,temp=tempfile.mkstemp(prefix='.texture82-',dir=os.path.dirname(filename))
        try:
            with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            os.replace(temp,filename)
        finally:
            if os.path.exists(temp):os.unlink(temp)

def prepare(portal,kind,rows):
    """One RPC per 16-row batch instead of up to six RPCs per image."""
    import xbmc
    from widget_cache79 import load,valid,path
    from widget_assets69 import safe
    from programme_assets47 import sources
    if kind not in ('live','vod','series') or not rows:return
    _,context=path(portal,kind);now=time.monotonic()
    with _lock:
        if now<_due.get(context,0):return
        _due[context]=now+.5
        while len(_due)>32:_due.pop(next(iter(_due)))
    selected=rows[:256 if kind=='live' else 24];start=_cursor.get(context,0)%len(selected)
    batch=[selected[(start+i)%len(selected)] for i in range(min(16,len(selected)))]
    _cursor[context]=(start+len(batch))%len(selected)
    while len(_cursor)>32:_cursor.pop(next(iter(_cursor)))
    records=load(portal,kind).get('refs',{});wanted={}
    for row in batch:
        for role,source in sources(row,provider_only=True).items():
            if not source or not safe(portal,source):continue
            previous=records.get(str(row['sid']),{}).get(role,{})
            if valid(previous,source):
                remember(portal,kind,row,role,source,previous);continue
            for url in variants(source):wanted.setdefault(url,[]).append((row,role,source))
    if not wanted:return
    request=dict(jsonrpc='2.0',id=82,method='Textures.GetTextures',params=dict(filter={'or':[dict(field='url',operator='is',value=u) for u in wanted]},properties=['url','cachedurl','sizes'],limits=dict(start=0,end=256)))
    raw=xbmc.executeJSONRPC(json.dumps(request))
    if not isinstance(raw,str) or len(raw)>1024*1024:return
    try:response=json.loads(raw)
    except ValueError:return
    found=[];seen=set()
    if not isinstance(response,dict) or not isinstance(response.get('result',{}),dict):return
    textures=response.get('result',{}).get('textures',[])
    if not isinstance(textures,list):return
    for texture in textures[:256]:
        if not isinstance(texture,dict):continue
        url=texture.get('url')
        if not isinstance(url,str):continue
        for row,role,source in wanted.get(url,[]):
            tag=(str(row['sid']),role)
            if tag in seen:continue
            record=decoded(texture,source)
            if record:
                seen.add(tag);found.append((row['sid'],role,record));remember(portal,kind,row,role,source,record)
    if found:
        try:save(portal,kind,found)
        except (OSError,TimeoutError):pass  # Verified RAM receipt is not DISK_PERSISTED.

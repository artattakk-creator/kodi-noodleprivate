"""Explicit per-portal/media artwork/metadata choices; never delete old images.

Worker-only IO. Presentation reads the already loaded bounded RAM snapshot.
No portal, catalogue, artwork queue, resume or EPG database is rewritten.
"""
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import threading

MAX_JSON=1024*1024
FIELDS=frozenset(('plot','genre','year','rating','director','cast','duration_secs'))
ROLES=frozenset(('poster','fanart','replacement'))
_cache=collections.OrderedDict()
_versions={}
_lock=threading.RLock()


def clean_fields(fields):
    import math
    if not isinstance(fields,dict) or not set(fields)<=FIELDS:raise ValueError('INVALID_METADATA_FIELDS')
    result={}
    for key,value in fields.items():
        if key=='year':
            if not isinstance(value,int) or isinstance(value,bool) or not 1880<=value<=2100:raise ValueError('INVALID_YEAR')
        elif key=='duration_secs':
            if not isinstance(value,int) or isinstance(value,bool) or not 0<value<=172800:raise ValueError('INVALID_DURATION')
        elif key=='rating':
            if not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=10:raise ValueError('INVALID_RATING')
        elif key=='cast':
            if isinstance(value,str):value=[part.strip() for part in value[:2000].split(',')]
            if not isinstance(value,list) or any(not isinstance(v,str) for v in value):raise ValueError('INVALID_CAST')
            value=[v[:200] for v in value[:16]]
        else:
            if key in ('genre','director') and isinstance(value,list):value=' / '.join(v[:200] for v in value[:16] if isinstance(v,str))
            if not isinstance(value,str):raise ValueError('INVALID_TEXT')
            value=value[:6000 if key=='plot' else 1000]
        result[key]=value
    return result


def paths(pid):
    from utils import addon_data_dir
    root=Path(addon_data_dir())/'media_choices43'
    return root,root/(hashlib.sha256(str(pid).encode()).hexdigest()+'.json')


def ident(kind,sid):
    if kind not in ('vod','series') or not isinstance(sid,str) or not sid or len(sid)>512:
        raise ValueError('INVALID_MEDIA_ID')
    return json.dumps([kind,sid],separators=(',',':'))


def _read(filename):
    if filename.is_symlink() or filename.parent.is_symlink():raise ValueError('UNSAFE_CHOICE_PATH')
    try:
        with open(filename,'rb') as f:data=f.read(MAX_JSON+1)
    except FileNotFoundError:return {}
    if len(data)>MAX_JSON:raise ValueError('CHOICES_LIMIT')
    value=json.loads(data)
    if not isinstance(value,dict) or len(value)>1024:raise ValueError('CHOICES_INVALID')
    return value


def _snapshot(root,pid,value):
    result={};cachekey=(str(root),str(pid))
    with _lock:prior=_cache.get(cachekey,{})
    for key,entry in value.items():
        if not isinstance(entry,dict):continue
        images={}
        raw=entry.get('images',{})
        if not isinstance(raw,dict):continue
        for role,digest in raw.items():
            if role not in ROLES or not isinstance(digest,str) or not re.fullmatch('[a-f0-9]{64}',digest):continue
            images['poster' if role=='replacement' else role]=digest
        try:meta=clean_fields(entry.get('metadata',{}))
        except ValueError:meta={}
        old=prior.get(key,{})
        same=old.get('image_refs')==images
        result[key]=dict(art=old.get('art',{}) if same else {},image_refs=images,
                         resolved=old.get('resolved',False) if same else False,
                         metadata={k:v for k,v in meta.items() if k in FIELDS},source=entry.get('source',''))
    with _lock:
        _cache[cachekey]=result;_cache.move_to_end(cachekey)
        while len(_cache)>8:
            expired,_=_cache.popitem(last=False);_versions.pop(expired,None)
    return cachekey,result


def apply_many(pid,rows):
    if not rows:return []
    root,filename=paths(pid)
    # Missing manifest is a normal existing profile, no new files/directories.
    cachekey=(str(root),str(pid))
    try:stat=filename.stat();version=(stat.st_mtime_ns,stat.st_size)
    except FileNotFoundError:version=None
    except OSError:version=('UNAVAILABLE',)
    with _lock:
        snapshot=_cache.get(cachekey)
        refresh=snapshot is None or _versions.get(cachekey)!=version
    if refresh:
        try:
            value=_read(filename);cachekey,snapshot=_snapshot(root,pid,value)
            with _lock:_versions[cachekey]=version
        except (OSError,ValueError,TypeError,RecursionError):
            with _lock:snapshot=_cache.get(cachekey,{})
    result=[]
    for row in rows:
        if row.get('kind') not in ('vod','series'):result.append(row);continue
        base=dict(row.get('_provider43',row));base.pop('_art43_key',None);base.pop('_provider43',None)
        item=dict(base);item['_provider43']=base;item['_art43_key']=list(cachekey)
        fallback=row.get('_fallback43')
        if isinstance(fallback,dict):
            item.update({k:v for k,v in fallback.items() if k in ('cover','plot')})
            item['_fallback43']=fallback;item['_metadata_source43']='TMDb'
        entry=snapshot.get(ident(row['kind'],str(row['sid'])),{})
        if entry and not entry['resolved']:
            # Verify only the requested page, never scan/hash every manually
            # chosen image on every catalogue read. No IO in cached_art().
            images={}
            for role,digest in entry['image_refs'].items():
                path=root/'images'/(digest+'.img')
                try:
                    if path.is_symlink() or (root/'images').is_symlink() or not path.is_file() or path.stat().st_size>3*1024*1024:continue
                    if hashlib.sha256(path.read_bytes()).hexdigest()==digest:images[role]=str(path)
                except OSError:continue
            with _lock:entry.update(art=images,resolved=True)
        if entry.get('image_refs'):
            from programme_assets47 import choice as shared_choice47
            for role,digest in entry['image_refs'].items():
                display47=shared_choice47(pid,row['kind'],str(row['sid']),role,digest)
                if display47:entry.setdefault('art',{})[role]=display47
        item.update(entry.get('metadata',{}));item['_metadata_override43']=bool(entry.get('metadata'))
        item['_manual_art43']=dict(entry.get('art',{}));result.append(item)
    return result


def cached_art(item):
    """No stat/open/DNS, even on a focus/IR callback."""
    key=item.get('_art43_key')
    if not isinstance(key,(tuple,list)) or len(key)!=2 or item.get('kind') not in ('vod','series'):return {}
    with _lock:
        snapshot=_cache.get(tuple(key))
        if snapshot is not None:
            value=snapshot.get(ident(item.get('kind'),str(item.get('sid',''))),{})
            return dict(value.get('art',{}))
    # Another portal may evict the bounded RAM cache while an old row remains
    # displayed. Its worker-verified local asset still has stable identity.
    prefix=str(key[0])+os.sep+'images'+os.sep
    return {role:path for role,path in item.get('_manual_art43',{}).items()
            if role in ('poster','fanart') and isinstance(path,str) and path.startswith(prefix)
            and re.fullmatch('[a-f0-9]{64}\\.img',path[len(prefix):])}


def _atomic(filename,data):
    fd,name=tempfile.mkstemp(prefix='.choices43-',dir=filename.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(name,filename)
    finally:
        if os.path.exists(name):os.unlink(name)  # Only this new private temp file.


def save(pid,kind,sid,*,image=None,role='poster',metadata=None,source='',attribution='',provenance=None):
    """Call only after explicit Save; image already fully decoded in a worker."""
    key=ident(kind,sid)
    if role not in ROLES or image is None and metadata is None:raise ValueError('INVALID_CHOICE')
    provenance=provenance or {}
    if not isinstance(provenance,dict) or not set(provenance)<={'media_type','remote_id','source_fingerprint'}:raise ValueError('INVALID_PROVENANCE')
    if len(json.dumps(provenance).encode())>1024:raise ValueError('INVALID_PROVENANCE')
    root,filename=paths(pid);root.mkdir(mode=0o700,parents=True,exist_ok=True)
    if root.is_symlink() or filename.is_symlink() or Path(str(filename)+'.lock').is_symlink():raise ValueError('UNSAFE_CHOICE_PATH')
    import fcntl
    with open(str(filename)+'.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        value=_read(filename);entry=dict(value.get(key,{}))
        if image is not None:
            from media_sources43 import validate_image
            validate_image(image)
            folder=root/'images';folder.mkdir(mode=0o700,exist_ok=True)
            if folder.is_symlink():raise ValueError('UNSAFE_CHOICE_PATH')
            from art_storage import check,budget
            # Small manual store, same physical safety reserve and a finite
            # cap; never evict any old source/cached/manual image to make room.
            used=sum(p.stat().st_size for p in folder.iterdir() if p.is_file() and not p.is_symlink())
            check(len(image)+MAX_JSON,location=str(folder),used=used,limit=min(64*1048576,budget() or 64*1048576))
            digest=hashlib.sha256(image).hexdigest();target=folder/(digest+'.img')
            if target.is_symlink():raise ValueError('UNSAFE_CHOICE_PATH')
            if target.exists():
                if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise ValueError('IMAGE_HASH_MISMATCH')
            else:_atomic(target,image)
            if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise ValueError('IMAGE_HASH_MISMATCH')
            images=dict(entry.get('images',{}));images[role]=digest
            if role=='poster':images.pop('replacement',None)
            if role=='replacement':images.pop('poster',None)
            entry['images']=images
            history=dict(entry.get('image_provenance',{}));history[role]=dict(provenance,source=str(source)[:32],attribution=str(attribution)[:2048]);entry['image_provenance']=history
        if metadata is not None:
            metadata=clean_fields(metadata)
            text=json.dumps(metadata,ensure_ascii=False)
            if len(text.encode())>16384:raise ValueError('METADATA_LIMIT')
            entry['metadata']={**entry.get('metadata',{}),**metadata}
            entry['metadata_provenance']=dict(provenance,source=str(source)[:32],attribution=str(attribution)[:2048])
        entry.update(source=str(source)[:32],attribution=str(attribution)[:2048])
        value[key]=entry;data=json.dumps(value,ensure_ascii=False).encode()
        if len(data)>MAX_JSON:raise ValueError('CHOICES_LIMIT')
        from import_budget import check_space
        check_space(str(filename),len(data))
        _atomic(filename,data);_snapshot(root,pid,value)
    if image is not None:
        try:
            from programme_assets47 import remember_choice
            remember_choice(pid,kind,sid,role,image)
        except Exception:
            # Original verified choice remains valid even if the optional
            # common display reference is unavailable/budget-blocked.
            from widget_diagnostics47 import note
            note(pid,kind,'ASSETS','CHOICE_REFERENCE_UNAVAILABLE')
    return True


def reset(pid,kind,sid,metadata=False):
    """Explicit confirmed reference reset. Never unlink an artwork file."""
    root,filename=paths(pid)
    if not filename.is_file():return False
    if root.is_symlink() or filename.is_symlink() or Path(str(filename)+'.lock').is_symlink():raise ValueError('UNSAFE_CHOICE_PATH')
    import fcntl
    with open(str(filename)+'.lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);value=_read(filename);key=ident(kind,sid)
        entry=dict(value.get(key,{}));entry.pop('metadata' if metadata else 'images',None)
        value[key]=entry;_atomic(filename,json.dumps(value,ensure_ascii=False).encode());_snapshot(root,pid,value)
    return True

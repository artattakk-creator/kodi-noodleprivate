"""Public provider-reference stale-while-revalidate, independent of title rows.

Only previously DNS-approved, exact account/profile/source references. A
positive lease may bridge a bounded 300s refresh gap; confirmed unsafe DNS
revokes immediately. No image files, global cache reset or programme DB writes.
"""
import json,os,time,hashlib,tempfile
from collections import OrderedDict
_cache=OrderedDict()
GRACE=300

def path(portal,kind):
    from utils import addon_data_dir
    from widget_policy74 import signature
    key=signature(portal,kind)
    return os.path.join(addon_data_dir(),'widget-refs74-'+key[:32]+'.json'),key

def read(portal,kind,rows):
    from widget_assets69 import safe
    from programme_assets47 import sources
    from artwork_visible import KODI_OPTIONS,_dns_cache,_lock
    from urllib.parse import urlsplit
    filename,context=path(portal,kind)
    try:
        stamp=os.stat(filename)
        hit=_cache.get(filename)
        if hit and hit[0]==(stamp.st_mtime_ns,stamp.st_size):value=hit[1]
        else:
            with open(filename,encoding='utf-8') as stream:raw=stream.read(262145)
            value=json.loads(raw) if len(raw)<=262144 else {}
            _cache[filename]=((stamp.st_mtime_ns,stamp.st_size),value)
            while len(_cache)>16:_cache.popitem(last=False)
        if value.get('context')!=context:return {}
        result={};now=time.time()
        for row in rows:
            for role,source in sources(row,provider_only=True).items():
                reference=value.get('refs',{}).get(str(row['sid']),{}).get(role,{})
                if reference.get('source')!=source or not safe(portal,source):continue
                if not now<reference.get('until',0)<=now+GRACE+30:continue
                host=urlsplit(source).hostname
                with _lock:known=_dns_cache.get((host,443))
                if known and known[0]>time.monotonic() and not known[1]:continue
                result.setdefault(str(row['sid']),{})[role]=source+KODI_OPTIONS
        return result
    except (OSError,ValueError,TypeError,KeyError,AttributeError):return {}

def revoked(source):
    from artwork_visible import _dns_cache,_lock
    from urllib.parse import urlsplit
    try:
        with _lock:known=_dns_cache.get((urlsplit(source).hostname,443))
        return bool(known and known[0]>time.monotonic() and not known[1])
    except (ValueError,TypeError):return True

def remember_many(portal,kind,records):
    # Optional reference journal cannot terminate the actual artwork worker.
    try:return _remember_many(portal,kind,records)
    except (OSError,ValueError,TypeError,RuntimeError,TimeoutError,AttributeError):return

def _remember_many(portal,kind,records):
    if not records:return
    from widget_assets69 import safe
    from profile_transaction import writing
    with writing(timeout=.1):
        filename,context=path(portal,kind)
        try:
            with open(filename,encoding='utf-8') as stream:value=json.loads(stream.read(262145))
        except (OSError,ValueError):value={}
        if value.get('context')!=context:value=dict(context=context,refs={})
        now=time.time();refs=value['refs'];changed=False
        refs={sid:{k:v for k,v in roles.items() if v.get('until',0)>now} for sid,roles in refs.items()}
        refs={sid:roles for sid,roles in refs.items() if roles}
        for sid,role,source,remaining in records:
            if not remaining or not safe(portal,source):continue
            old=refs.get(str(sid),{}).get(role,{})
            until=now+min(30,remaining)+GRACE
            if old.get('source')==source and old.get('until',0)>until-15:continue
            refs.setdefault(str(sid),{})[role]=dict(source=source,until=until);changed=True
        if not changed or len(refs)>512:return
        value['refs']=refs;raw=json.dumps(value,separators=(',',':')).encode()
        if len(raw)>262144:return
        fd,temp=tempfile.mkstemp(prefix='.widget-refs74-',dir=os.path.dirname(filename))
        try:
            with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            os.replace(temp,filename)
        finally:
            if os.path.exists(temp):os.unlink(temp)

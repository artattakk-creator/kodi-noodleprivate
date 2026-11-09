"""Share short-lived approved Dynamic art references across Kodi interpreters.

No image archive or network IO in presentation. DNS validation uses the existing
worker policy, expiry and Kodi redirect limits; only private bounded metadata is
persisted. Existing locally validated images and explicit choices win.
"""
import hashlib,json,os,tempfile,time
MAX_BYTES=256*1024
_cursor80={}


def path(pid,kind=None):
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'widget_art44_'+hashlib.sha256((str(pid)+('|' + kind if kind in ('live','vod','series') else '')).encode()).hexdigest()[:24]+'.json')


def _read80(pid,kind=None):
    try:
        with open(path(pid,kind),encoding='utf-8') as f:raw=f.read(MAX_BYTES+1)
        data=json.loads(raw) if len(raw)<=MAX_BYTES else {}
        return {k:v for k,v in data.items() if isinstance(k,str) and isinstance(v,dict) and isinstance(v.get('uri'),str) and isinstance(v.get('until'),(int,float))} if isinstance(data,dict) and len(data)<=(512 if kind=='live' else 96) else {}
    except (OSError,ValueError):return {}


def read(pid,kind=None):
    if kind in ('live','vod','series'):
        value=_read80(pid,kind)
        return value or _read80(pid)
    result=_read80(pid)
    for scope80 in ('live','vod','series'):result.update(_read80(pid,scope80))
    return result


def prepare(pid,rows,kind=None):
    kind=kind or (rows[0].get('kind') if rows else None)
    from artwork_config import persistent
    from media_art import sources,request
    request(rows,priority=0)
    if persistent():return
    if not __import__('artwork_display84').metadata_allowed():return
    from artwork_visible import public_dns,syntactic,KODI_OPTIONS,_dns_cache,_lock
    from urllib.parse import urlsplit
    values=read(pid,kind);now=time.time();values={k:v for k,v in values.items() if isinstance(v,dict) and v.get('until',0)>now}
    until=time.monotonic()+.4
    selected80=rows[:256 if kind=='live' else 24];key80=(str(pid),kind);cursor80=_cursor80.get(key80,0)%max(1,len(selected80));processed80=0
    for row in selected80[cursor80:]+selected80[:cursor80]:
        if time.monotonic()>until:break
        processed80+=1
        for url in sources(row):
            if not syntactic(url):continue
            key=hashlib.sha256(url.encode()).hexdigest();old=values.get(key)
            if old and old.get('until',0)>time.time()+15:continue
            if time.monotonic()>until:break
            if not public_dns(url):values.pop(key,None);continue
            p=urlsplit(url)
            with _lock:checked=_dns_cache.get((p.hostname,p.port or (443 if p.scheme=='https' else 80)))
            if checked and checked[1]:
                seconds=max(0,min(30,checked[0]-time.monotonic()))
                if seconds:values[key]=dict(uri=url+KODI_OPTIONS,until=time.time()+seconds)
    _cursor80[key80]=(cursor80+processed80)%max(1,len(selected80))
    while len(_cursor80)>32:_cursor80.pop(next(iter(_cursor80)))
    values=dict(list(values.items())[-(512 if kind=='live' else 96):]);data=json.dumps(values).encode()
    if len(data)>MAX_BYTES:return
    from import_budget import check_space
    check_space(path(pid,kind),len(data)+65536)
    fd,tmp=tempfile.mkstemp(prefix='.widget-art44-',dir=os.path.dirname(path(pid,kind)))
    try:
        with os.fdopen(fd,'wb') as f:f.write(data)
        os.replace(tmp,path(pid,kind))
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def art(item,approved):
    import xbmcaddon
    from artwork_config import persistent
    from media_art import sources,cached
    from artwork_visible import syntactic,KODI_OPTIONS
    from media_overrides43 import cached_art
    placeholder=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media',{'live':'tv','series':'series'}.get(item.get('kind'),'vod')+'.png')
    def resolve(url):
        if not url:return ''
        from programme_assets47 import local_uri
        local75=local_uri(url)
        if local75:return local75
        local=cached(url)
        if local:return local
        if persistent() or not syntactic(url):return ''
        value=approved.get(hashlib.sha256(url.encode()).hexdigest(),{})
        remaining=value.get('until',0)-time.time()
        return value.get('uri','') if 0<remaining<=30 and value.get('uri')==url+KODI_OPTIONS else ''
    poster,fanart=sources(item);manual={} if item.get('kind') in ('vod','series') else cached_art(item)
    poster=manual.get('poster') or resolve(poster) or placeholder
    fanart=manual.get('fanart') or resolve(fanart)
    return dict(poster=poster,thumb=poster,icon=poster,fanart=fanart,landscape=fanart or poster)

"""Persistent budgeted artwork. GUI receives LOCAL paths exclusively."""
import hashlib
import os
import struct
import sqlite3
import tempfile
import threading
import time
from urllib.parse import urlsplit

_lock=threading.RLock()
_queue_lock=threading.RLock()
MAX_BYTES=3*1024*1024
MAX_PIXELS=8*1024*1024
_worker=None
_enrol_worker=None
_inbox={}
_serial=0
_enqueue_code='NOT_REQUESTED'
_choices={}
_choice_revision=0
MAX_INBOX=2048


def dimensions(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n') and len(data)>=24:
        return struct.unpack('>II',data[16:24])
    if data.startswith(b'\xff\xd8'):
        p=2
        while p+4<=len(data):
            if data[p]!=255: break
            while p<len(data) and data[p]==255: p+=1
            if p>=len(data): break
            marker=data[p]; p+=1
            if marker in (0xd9,0xda): break
            if marker in (0x01,0xd8) or 0xd0<=marker<=0xd7: continue
            if p+2>len(data): break
            length=int.from_bytes(data[p:p+2],'big')
            if length<2 or p+length>len(data): break
            if marker in (0xc0,0xc1,0xc2) and length>=7:
                h,w=struct.unpack('>HH',data[p+3:p+7]); return w,h
            p+=length
    raise ValueError('unsupported image')


def folder():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'media_art_v1')


def cached(url):
    if not isinstance(url,str) or not url: return ''
    filename=os.path.join(folder(),hashlib.sha256(url.encode()).hexdigest()+'.img')
    try:
        with open(filename,'rb') as stream: header=stream.read(65536)
        w,h=dimensions(header)
        return filename if 0<w<=4096 and 0<h<=4096 and w*h<=MAX_PIXELS else ''
    except (OSError,ValueError): return ''


def valid_source(value):
    if not isinstance(value,str) or not value or len(value)>8192 or any(ord(c)<32 or ord(c)==127 for c in value):return False
    try:
        parts=urlsplit(value)
        return parts.scheme in ('http','https') and bool(parts.hostname) and not any(c.isspace() for c in parts.hostname) and (parts.port is None or 0<parts.port<65536)
    except ValueError:return False


def fetch(url):
    """Worker-only. Stable names, no eviction, capacity checked before/after IO."""
    from art_storage import check,ArtworkFailure
    if not valid_source(url):raise ArtworkFailure('INVALID_SOURCE')
    with _lock:
        hit=cached(url)
        if hit:
            from art_store import ready
            ready(url,os.path.getsize(hit));return hit
        from art_store import budget,used
        from import_budget import check_space
        root=folder();tmp=''
        try:
            os.makedirs(root,exist_ok=True)
            cap=budget()
            if cap and used()>=cap:raise ArtworkFailure('BUDGET_FULL')
            check(MAX_BYTES,limit=0)
            check_space(os.path.join(root,'pending'),MAX_BYTES)
            from utils import http_get
            try:data,_=http_get(url,timeout=4,max_bytes=MAX_BYTES,max_seconds=6,retry_limit=0)
            except ValueError:raise ArtworkFailure('INVALID_IMAGE') from None
            except Exception as error:
                from art_errors import classify,retry_after
                failure=ArtworkFailure(classify(error));failure.retry_after=retry_after(error)
                raise failure from None
            try:
                w,h=dimensions(data)
                if len(data)>MAX_BYTES or not 0<w<=4096 or not 0<h<=4096 or w*h>MAX_PIXELS:raise ValueError()
            except (ValueError,TypeError,struct.error):raise ArtworkFailure('INVALID_IMAGE') from None
            check(len(data),limit=cap,used=used() if cap else 0)
            filename=os.path.join(root,hashlib.sha256(url.encode()).hexdigest()+'.img')
            fd,tmp=tempfile.mkstemp(prefix='.art-',dir=root)
            with os.fdopen(fd,'wb') as stream:
                stream.write(data);stream.flush();os.fsync(stream.fileno())
            os.replace(tmp,filename);tmp=''
        except ArtworkFailure:raise
        except OSError as exc:
            raise ArtworkFailure('DISK_FULL' if exc.errno==28 else 'CACHE_ERROR') from None
        finally:
            if tmp:
                try:os.unlink(tmp)
                except OSError:pass
        from art_store import ready
        ready(url,len(data));return filename


def poster_candidates(item):
    return list(dict.fromkeys(item.get(k) for k in ('cover','stream_icon','movie_image','cover_big') if valid_source(item.get(k))))


def _choice_key(item):
    return hashlib.sha256('\n'.join(poster_candidates(item)).encode()).hexdigest()


def sources(item):
    candidates=poster_candidates(item)
    with _queue_lock:chosen=_choices.get(_choice_key(item))
    poster=next((u for u in candidates if cached(u)),chosen if chosen in candidates else candidates[0] if candidates else '')
    fanart=[]
    for key in ('backdrop_path','backdrop','fanart','fanart_image'):
        value=item.get(key);fanart.extend(value if isinstance(value,list) else [value])
    return poster,next((value for value in fanart if valid_source(value)),'')


def local_art(item,theme=None):
    import xbmcaddon
    placeholder=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','tv.png' if item.get('kind')=='live' else 'series.png' if item.get('kind')=='series' else 'vod.png')
    if theme:
        from theme_store import asset
        placeholder=asset('icon.live' if item.get('kind')=='live' else 'placeholder.series.poster' if item.get('kind')=='series' else 'placeholder.movie.poster',placeholder,snapshot=theme)
    poster,backdrop=sources(item)
    cached_poster=cached(poster)
    poster=cached_poster or placeholder; backdrop=cached(backdrop)
    provider_landscape=backdrop or cached_poster
    if theme and not backdrop:
        from theme_store import asset
        backdrop=asset('placeholder.series.backdrop' if item.get('kind')=='series' else 'placeholder.movie.backdrop',snapshot=theme)
    return dict(poster=poster,thumb=poster,icon=poster,fanart=backdrop,landscape=provider_landscape or backdrop or poster)


def request(items,priority=0):
    """GUI-safe bounded inbox. SQLite enrolment and HTTP use distinct workers."""
    global _enrol_worker,_serial
    with _queue_lock:
        for item in items[:48]:
            rank=-10 if item.get('kind')=='live' and priority<=0 else priority
            for url in dict.fromkeys(sources(item)):
                if not url or cached(url):continue
                previous=_inbox.get(url)
                _serial+=1
                _inbox[url]=(min(rank,previous[0]) if previous else rank,previous[1] if previous else _serial,previous[2] if previous else 0,previous[3] if previous else 0)
        while len(_inbox)>MAX_INBOX:
            worst=max(_inbox,key=lambda url:(_inbox[url][0],-_inbox[url][1]))
            del _inbox[worst]  # only unpersisted old requests; never existing jobs/files
        if _inbox and (_enrol_worker is None or not _enrol_worker.is_alive()):
            _enrol_worker=threading.Thread(target=_enrol_loop,daemon=True,name='XCMate-art-enrol')
            _enrol_worker.start()


def _persist_next():
    global _worker,_enqueue_code
    with _queue_lock:
        batch=sorted((url for url,value in _inbox.items() if value[3]<=time.monotonic()),key=lambda url:_inbox[url][:2])[:48]
        if not batch:return False
        priority=_inbox[batch[0]][0]
        batch=[url for url in batch if _inbox[url][0]==priority]
        values={url:_inbox[url] for url in batch}
    try:
        from art_store import enqueue
        enqueue(batch,priority);_enqueue_code='NOT_REQUESTED'
        with _queue_lock:
            for url,value in values.items():
                if _inbox.get(url)==value:_inbox.pop(url,None)
    except (OSError,RuntimeError,sqlite3.Error) as exc:
        from artwork_db import classify,diagnostic
        code=classify(exc)
        _enqueue_code=('DB_BUSY' if code=='BUSY' or diagnostic().get('code')=='BUSY' else 'DB_UNAVAILABLE') if isinstance(exc,sqlite3.Error) else 'DISK_FULL' if getattr(exc,'errno',None)==28 else 'CACHE_ERROR'
        with _queue_lock:
            for url,value in values.items():
                current=_inbox.get(url)
                if current is None:continue
                if value[2]<2:_inbox[url]=(current[0],current[1],value[2]+1,time.monotonic()+5)
                else:_inbox.pop(url,None)
        return True
    with _queue_lock:
        if _worker is None or not _worker.is_alive():
            _worker=threading.Thread(target=_prefetch,daemon=True,name='XCMate-artwork');_worker.start()
    return True


def _enrol_loop():
    import xbmc
    global _enrol_worker
    monitor=xbmc.Monitor()
    while not monitor.abortRequested():
        with _queue_lock:
            if not _inbox:_enrol_worker=None;return
        _persist_next()
        if monitor.waitForAbort(.1):break
    with _queue_lock:_enrol_worker=None


def _prefetch():
    import xbmc
    from art_store import run_one
    monitor=xbmc.Monitor()
    while not monitor.abortRequested():
        try: worked=run_one()
        except Exception: worked=False
        if monitor.waitForAbort(.1 if worked else 2): return


def revision():
    try: return os.stat(folder()).st_mtime_ns+_choice_revision
    except OSError: return _choice_revision


def _image_snapshot(item):
    from artwork_db import image_snapshot
    from art_store import key
    return image_snapshot([key(u) for u in [*poster_candidates(item),*sources(item)] if u])


def diagnose(item,_snapshot=None):
    """Worker diagnosis and same-record fallback. Never expose private sources."""
    from art_store import key
    from art_errors import PERMANENT
    global _choice_revision
    candidates=poster_candidates(item)
    urls=sources(item);values,db_code=_image_snapshot(item) if _snapshot is None else _snapshot
    states={ident:value['status'] for ident,value in values.items()}
    chosen=next((u for u in candidates if cached(u)),None)
    exhausted=False
    if urls[0] and states.get(key(urls[0])) not in PERMANENT:
        exhausted=values.get(key(urls[0]),{}).get('attempts',0)>=3
    if not chosen and urls[0] and (states.get(key(urls[0])) in PERMANENT or exhausted):
        chosen=next((u for u in candidates if states.get(key(u)) not in PERMANENT and states.get(key(u)) not in ('NETWORK_ERROR','TIMEOUT','DNS_ERROR','CONNECTION_ERROR','HTTP_SERVER','HTTP_RATE_LIMIT')),None)
    if chosen and chosen!=urls[0]:
        with _queue_lock:
            if len(_choices)>=2048:_choices.pop(next(iter(_choices)))
            _choices[_choice_key(item)]=chosen;_choice_revision+=1
        urls=sources(item)
        if not cached(chosen):request([item])
    result={}
    fields=(('cover','stream_icon','movie_image','cover_big'),('backdrop_path','backdrop','fanart','fanart_image'))
    for name,url,keys in zip(('poster','fanart'),urls,fields):
        if not url:
            result[name]='INVALID_SOURCE' if any(item.get(k) for k in keys) else 'NO_SOURCE';continue
        if cached(url):result[name]='READY';continue
        filename=os.path.join(folder(),key(url)+'.img')
        if os.path.exists(filename):result[name]='CACHE_ERROR';continue
        code=states.get(key(url))
        if code=='READY':code='CACHE_ERROR'
        if code is None:
            with _queue_lock:waiting=url in _inbox
            code=db_code if db_code not in ('OK','NOT_CREATED') else ('PENDING' if _enqueue_code=='NOT_REQUESTED' else _enqueue_code) if waiting else _enqueue_code
        result[name]=code
    return result


def diagnostic_label(code):
    from localization import tr
    codes=('READY','NO_SOURCE','INVALID_SOURCE','NOT_REQUESTED','PENDING','RUNNING',
           'NETWORK_ERROR','INVALID_IMAGE','CACHE_ERROR','SPACE_FULL','BUDGET_FULL',
           'DISK_FULL','DB_BUSY','DB_UNAVAILABLE','FAILED','UNKNOWN')
    if code=='WAIT':return tr(33705)
    from art_errors import CODES
    if code in CODES:return tr(33710+CODES.index(code))
    return tr(33410+codes.index(code) if code in codes else 33425)


def retry_poster(item):
    """Explicit one-poster retry, with alternatives from this exact record only."""
    from art_store import retry_one,key
    global _choice_revision
    candidates=poster_candidates(item)
    if not candidates:return 'NO_SOURCE'
    if any(cached(url) for url in candidates):return 'READY'
    current=sources(item)[0]
    values,db_code=_image_snapshot(item)
    if db_code not in ('OK','NOT_CREATED'):return 'DB_BUSY' if db_code in ('BUSY','DB_BUSY') else 'DB_UNAVAILABLE'
    failed={'HTTP_AUTH','HTTP_NOT_FOUND','HTTP_CLIENT','HTTP_SERVER','HTTP_RATE_LIMIT',
            'INVALID_IMAGE','INVALID_SOURCE','NETWORK_ERROR','TIMEOUT','DNS_ERROR','CONNECTION_ERROR','TLS_ERROR','FAILED','CACHE_ERROR'}
    previous=values.get(key(current),{})
    chosen=current
    if previous.get('status') in failed or previous.get('attempts',0)>=3:
        chosen=next((url for url in candidates if url!=current and values.get(key(url),{}).get('status') not in failed),current)
    if chosen!=current:
        with _queue_lock:
            if len(_choices)>=2048:_choices.pop(next(iter(_choices)))
            _choices[_choice_key(item)]=chosen;_choice_revision+=1
    result=retry_one(chosen)
    if result=='PENDING':
        # Wake the existing bounded queue with just this poster; do not enqueue
        # fanart or unrelated assets when the user retries one selected image.
        request([dict(cover=chosen)],priority=-20)
    return result


def poster_report(item):
    from art_store import key
    snapshot=_image_snapshot(item)
    status=diagnose(item,_snapshot=snapshot)['poster']
    url=sources(item)[0];fields=('cover','stream_icon','movie_image','cover_big')
    values,code=snapshot
    value=values.get(key(url),{}) if url else {}
    return dict(source_field=next((field for field in fields if item.get(field)==url),'NONE'),
                candidate_count=len(poster_candidates(item)),status=status,
                attempts=value.get('attempts',0),updated=value.get('updated',0),next_at=value.get('next_at',0),database=code)

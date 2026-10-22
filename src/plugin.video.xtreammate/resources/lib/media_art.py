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


def fetch(url):
    """Call from a bounded worker only, never from onAction/onFocus."""
    if not isinstance(url,str) or urlsplit(url).scheme not in ('http','https'): return ''
    with _lock:
        hit=cached(url)
        if hit:
            from art_store import ready
            ready(url,os.path.getsize(hit))
            return hit
        from art_store import budget,used
        from import_budget import check_space
        root=folder();os.makedirs(root,exist_ok=True)
        available=budget()-used()
        if available<=0: raise OSError(28,'Artwork budget full')
        check_space(os.path.join(root,'pending'),min(MAX_BYTES,available))
        from utils import http_get
        data,_=http_get(url,timeout=4,max_bytes=min(MAX_BYTES,available),max_seconds=6)
        if len(data)>available: raise OSError(28,'Artwork budget full')
        w,h=dimensions(data)
        if not 0<w<=4096 or not 0<h<=4096 or w*h>MAX_PIXELS:
            raise ValueError('image dimensions exceed budget')
        root=folder();os.makedirs(root,exist_ok=True)
        filename=os.path.join(root,hashlib.sha256(url.encode()).hexdigest()+'.img')
        fd,tmp=tempfile.mkstemp(prefix='.art-',dir=root)
        try:
            with os.fdopen(fd,'wb') as stream: stream.write(data)
            os.replace(tmp,filename)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        from art_store import ready
        ready(url,len(data))
        return filename


def sources(item):
    def valid(value):
        if not isinstance(value,str):return False
        try:return urlsplit(value).scheme in ('http','https') and bool(urlsplit(value).hostname)
        except ValueError:return False
    poster=next((item.get(k) for k in ('cover','stream_icon','movie_image','cover_big') if valid(item.get(k))),'')
    fanart=[]
    for key in ('backdrop_path','backdrop','fanart','fanart_image'):
        value=item.get(key);fanart.extend(value if isinstance(value,list) else [value])
    return poster,next((value for value in fanart if valid(value)),'')


def local_art(item):
    import xbmcaddon
    placeholder=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','tv.png' if item.get('kind')=='live' else 'series.png' if item.get('kind')=='series' else 'vod.png')
    poster,backdrop=sources(item)
    poster=cached(poster) or placeholder; backdrop=cached(backdrop)
    return dict(poster=poster,thumb=poster,icon=poster,fanart=backdrop,landscape=backdrop or poster)


def request(items,priority=0):
    """Persist bounded visible-page requests, then start one worker."""
    global _worker
    urls=[u for item in items[:48] for u in dict.fromkeys(sources(item))
          if isinstance(u,str) and urlsplit(u).scheme in ('http','https') and not cached(u)]
    if not urls: return
    from art_store import enqueue
    try: enqueue(urls,priority)
    except (OSError,RuntimeError,sqlite3.Error): return
    with _queue_lock:
        if _worker is None or not _worker.is_alive():
            _worker=threading.Thread(target=_prefetch,daemon=True,name='XCMate-artwork');_worker.start()


def _prefetch():
    import xbmc
    from art_store import run_one
    monitor=xbmc.Monitor()
    while not monitor.abortRequested():
        try: worked=run_one()
        except Exception: worked=False
        if monitor.waitForAbort(.1 if worked else 2): return


def revision():
    try: return os.stat(folder()).st_mtime_ns
    except OSError: return 0

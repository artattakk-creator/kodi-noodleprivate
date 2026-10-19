"""Bounded background-only image cache. GUI receives LOCAL paths exclusively."""
import hashlib
import os
import struct
import tempfile
import threading
import time
import queue
from urllib.parse import urlsplit

_lock=threading.RLock()
_queue_lock=threading.RLock()
MAX_BYTES=3*1024*1024
MAX_PIXELS=8*1024*1024
MAX_DISK_BYTES=32*1024*1024
_requests=queue.Queue(maxsize=32)
_requested={}
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
    return filename if os.path.isfile(filename) else ''


def fetch(url):
    """Call from a bounded worker only, never from onAction/onFocus."""
    if not isinstance(url,str) or urlsplit(url).scheme not in ('http','https'): return ''
    with _lock:
        hit=cached(url)
        if hit: return hit
        from utils import http_get
        data,_=http_get(url,timeout=4,max_bytes=MAX_BYTES,max_seconds=6)
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
        files=sorted((os.path.join(root,n) for n in os.listdir(root) if n.endswith('.img')),
                     key=os.path.getmtime,reverse=True)
        used=0
        for index,old in enumerate(files):
            try:
                size=os.path.getsize(old)
                if index>=64 or used+size>MAX_DISK_BYTES: os.unlink(old)
                else: used+=size
            except OSError: pass
        return filename


def sources(item):
    poster=next((item.get(k) for k in ('cover','stream_icon','movie_image') if isinstance(item.get(k),str) and item[k]),'')
    backdrop=item.get('backdrop_path')
    if isinstance(backdrop,list): backdrop=next((p for p in backdrop if isinstance(p,str) and p),'')
    if not isinstance(backdrop,str): backdrop=''
    return poster,backdrop or poster


def local_art(item):
    import xbmcaddon
    placeholder=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','tv.png' if item.get('kind')=='live' else 'series.png' if item.get('kind')=='series' else 'vod.png')
    poster,backdrop=sources(item)
    poster=cached(poster) or placeholder; backdrop=cached(backdrop)
    return dict(poster=poster,thumb=poster,icon=poster,fanart=backdrop,landscape=backdrop or poster)


def request(items):
    """Bounded service prefetch for widget covers, with retry backoff."""
    global _worker
    with _queue_lock:
        if _worker is None:
            _worker=threading.Thread(target=_prefetch,daemon=True,name='XCMate-widget-art');_worker.start()
        now=time.monotonic()
        for item in items[:12]:
            for url in dict.fromkeys(sources(item)):
                if not url or _requested.get(url,0)>now: continue
                try: _requests.put_nowait(url)
                except queue.Full: return
                _requested[url]=now+180
        if len(_requested)>128:
            for url in list(_requested)[:-128]: _requested.pop(url,None)


def _prefetch():
    import xbmc
    monitor=xbmc.Monitor()
    while not monitor.abortRequested():
        try: url=_requests.get(timeout=.5)
        except queue.Empty: continue
        try: fetch(url)
        except Exception: pass

"""Bounded background logo cache. Never give Kodi a remote texture URL."""
import hashlib
import os
from pathlib import Path
import queue
import tempfile
import threading
import time

_READY, _SEEN = {}, {}
_QUEUE = queue.Queue(maxsize=32)
_LOCK = threading.Lock()
_WORKER = None


def local_logo(uri):
    return _READY.get(str(uri or ''),'')


def request(channels):
    global _WORKER
    if not any(getattr(ch,'logo','') for ch in channels): return
    with _LOCK:
        if _WORKER is None:
            _WORKER = threading.Thread(target=_run,daemon=True,name='XCMateLogoCache')
            _WORKER.start()
        for ch in channels:
            uri = str(getattr(ch,'logo','') or '')
            if not uri or time.time()-_SEEN.get(uri,0)<300: continue
            try:
                _QUEUE.put_nowait(uri)
                _SEEN[uri]=time.time()
            except queue.Full: break
        if len(_SEEN)>256:
            for k in sorted(_SEEN,key=_SEEN.get)[:-256]: _SEEN.pop(k,None)


def _run():
    from utils import addon_data_dir, http_get
    folder = Path(addon_data_dir())/'tv_logos'
    while True:
        uri = _QUEUE.get()
        temp = None
        try:
            if uri.startswith('/') and os.path.isfile(uri):
                _READY[uri]=uri
                continue
            if not uri.startswith(('http://','https://')): continue
            folder.mkdir(parents=True,exist_ok=True)
            target=folder/(hashlib.sha256(uri.encode()).hexdigest()+'.img')
            if not target.is_file():
                raw,_=http_get(uri,timeout=3,max_bytes=512*1024,max_seconds=5)
                if not (raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\xff\xd8\xff')): continue
                fd,temp=tempfile.mkstemp(prefix='.logo-',dir=folder)
                with os.fdopen(fd,'wb') as f: f.write(raw)
                os.replace(temp,target)
            _READY[uri]=str(target)
            files=sorted(folder.glob('*.img'),key=lambda p:p.stat().st_mtime)
            for p in files[:-128]:
                p.unlink()
                for key,value in list(_READY.items()):
                    if value==str(p): _READY.pop(key,None)
            if len(_READY)>128:
                for key in list(_READY)[:-128]: _READY.pop(key,None)
        except Exception:
            pass  # fallback icon remains usable even offline
        finally:
            if temp and os.path.exists(temp): os.unlink(temp)
            _QUEUE.task_done()

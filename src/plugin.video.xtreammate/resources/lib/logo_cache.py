"""Bounded background logo cache. Never give Kodi a remote texture URL."""
import hashlib
import os
import queue
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
        if _WORKER is None or not _WORKER.is_alive():
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
    from utils import http_get
    from media_art import dimensions,MAX_PIXELS
    from art_storage import check,ArtworkFailure
    from art_diagnostics import publish
    from artwork_backend import active_backend
    storage=active_backend('logos')
    def valid(data):
        try:
            w,h=dimensions(data)
            return 0<w<=4096 and 0<h<=4096 and w*h<=MAX_PIXELS
        except (ValueError,TypeError):return False
    while True:
        uri = _QUEUE.get()
        try:
            if uri.startswith('/') and os.path.isfile(uri):
                _READY[uri]=uri
                continue
            if not uri.startswith(('http://','https://')): continue
            ident=hashlib.sha256(uri.encode()).hexdigest()
            existing=storage.exists(ident) and valid(storage.read(ident,65536))
            if not existing:
                publish('logo','FETCH_BEGIN',expected_bytes=512*1024)
                check(512*1024,limit=0,backend=storage)
                raw,_=http_get(uri,timeout=3,max_bytes=512*1024,max_seconds=5)
                if len(raw)>512*1024 or not valid(raw):
                    publish('logo','INVALID_IMAGE');continue
                check(len(raw),limit=0,backend=storage)
                storage.write_verified(ident,raw,valid)
            _READY[uri]=storage.make_display_uri(ident)
            publish('logo','READY',bytes=storage.stat(ident)['bytes'])
            # Bound only the RAM lookup. Previously downloaded logo files
            # remain persistent; loading a new logo never removes an old one.
            if len(_READY)>128:
                for key in list(_READY)[:-128]: _READY.pop(key,None)
        except Exception as error:
            from art_errors import classify
            code=error.code if isinstance(error,ArtworkFailure) else 'DISK_FULL' if isinstance(error,OSError) and error.errno==28 else 'CACHE_ERROR' if isinstance(error,OSError) and error.errno in (13,30) else classify(error)
            publish('logo',code,reason=getattr(error,'reason',''),**getattr(error,'storage',{}))
        finally:
            _QUEUE.task_done()

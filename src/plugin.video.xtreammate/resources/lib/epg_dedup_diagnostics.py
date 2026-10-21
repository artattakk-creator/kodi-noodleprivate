"""Small local short-guide report; no account, host, URL or raw payload saved."""
import hashlib
import json
import os
import threading
import time

_LOCK=threading.Lock()


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'epg_dedup_diagnostics_v1.json')


def read():
    try:
        with open(path(),encoding='utf-8') as stream: value=json.load(stream)
        return value if isinstance(value,list) else []
    except (OSError,ValueError): return []


def record(pid,sid,guide):
    try:
        digest=hashlib.sha256((str(pid)+'\0'+str(sid)).encode()).hexdigest()[:16]
        # Titles are deliberately excluded: even malicious provider text cannot
        # smuggle credentials/URLs into a diagnostic meant for sharing.
        decisions=[{k:d[k] for k in ('starts','stops','kept_start','source')} for d in guide.get('dedup_decisions',[])[:16]]
        value=dict(at=int(time.time()),stream=digest,source='XTREAM_SHORT',
                   raw=guide.get('raw_count',0),unique=guide.get('unique_count',0),
                   removed=guide.get('duplicates',0),decisions=decisions)
        with _LOCK:
            rows=(read()+[value])[-32:]
            temporary=path()+'.tmp'
            with open(temporary,'w',encoding='utf-8') as stream: json.dump(rows,stream,separators=(',',':'))
            os.replace(temporary,path())
    except (OSError,ValueError,TypeError,ImportError): pass

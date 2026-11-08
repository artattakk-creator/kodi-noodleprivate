"""Worker-only short read leases keyed by real guide/WAL/mapping generation.

No guide writes or long-term replacement database. Missing programmes back off
for at most 30 seconds; positive intervals expire at the real event boundary.
"""
import copy,hashlib,json,os,threading,time
_lock=threading.RLock();_values={}
def key(pid,channels,mappings,display):
    from guide_store import path
    from epg_status import revision
    from epg_handoff63 import profile_scope
    from local_epg import channel_keys
    filename=path()
    def stamp(name):
        try:v=os.stat(name);return [v.st_mtime_ns,v.st_size]
        except OSError:return [0,0]
    rows=[channel_keys(c,mappings) for c in channels[:16]]
    return hashlib.sha256(json.dumps([profile_scope(),str(pid),revision(pid),stamp(filename),stamp(filename+'-wal'),rows,mappings,getattr(mappings,'sources48',{}),bool(display)],sort_keys=True,default=str).encode()).hexdigest()
def read(cache_key,now):
    with _lock:record=_values.get(cache_key)
    if not record or time.monotonic()>record['until'] or abs(now-record['now'])>30:return None
    for info in record['value'].values():
        if info.get('now') and not info.get('start',0)<=now<info.get('stop',0):return None
        if not info.get('now') and 0<info.get('next_start',0)<=now:return None
    return copy.deepcopy(record['value'])
def remember(cache_key,value,now):
    ttl=15 if any(v.get('now') for v in value.values()) else 30
    with _lock:
        _values[cache_key]=dict(until=time.monotonic()+ttl,now=now,value=copy.deepcopy(value))
        while len(_values)>32:_values.pop(next(iter(_values)))

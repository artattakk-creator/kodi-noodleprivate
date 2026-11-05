"""Coalesced local-only Now/Next refresh. GUI requests contain only identities.

Uses the one existing guide/mapping reader. No provider/HTTP/import/migration.
A fresh metadata/configuration revision still invalidates mismatched snapshots.
"""
import threading,time
_lock=threading.Lock();_wanted={};_due={};_thread=None;_wake=threading.Event();_stop=threading.Event()

def request(pid,sid):
    global _thread
    if _stop.is_set():return
    from epg_handoff63 import profile_scope
    key=(profile_scope(),str(pid),str(sid));now=time.monotonic()
    with _lock:
        if now<_due.get(key,0):return
        _due[key]=now+15;_wanted[key]=now
        while len(_wanted)>64:_wanted.pop(next(iter(_wanted)))
        while len(_due)>256:_due.pop(next(iter(_due)))
        import xbmc
        factory=getattr(xbmc,'Monitor',None)
        if not callable(factory):return
        monitor=factory()
        if not all(callable(getattr(monitor,n,None)) for n in ('abortRequested','waitForAbort')):return
        if _thread is None or not _thread.is_alive():
            _thread=threading.Thread(target=_run,name='XCMate-local-EPG74',daemon=True);_thread.start()
        _wake.set()

def _run():
    import xbmc
    from epg_handoff63 import profile_scope
    monitor=xbmc.Monitor()
    while not _stop.is_set() and not monitor.abortRequested():
        _wake.wait(.5);_wake.clear()
        with _lock:jobs=list(_wanted);_wanted.clear()
        groups={}
        for scope,pid,sid in jobs:
            if scope==profile_scope():groups.setdefault(pid,[]).append(sid)
        for pid,sids in groups.items():
            if _stop.is_set() or monitor.abortRequested():return
            try:
                from library_index import Reader
                from epg_sources import configuration
                from local_epg import now_next
                from programme_read47 import session
                reader=Reader(pid,timeout=.03,query_seconds=.1)
                rows=[row for sid in sids if (row:=reader.get('live',sid))]
                mappings=configuration(pid)['mappings']
                with session():
                    for offset in range(0,len(rows),16):
                        if _stop.is_set() or monitor.abortRequested():return
                        now_next(pid,rows[offset:offset+16],mappings,display_only65=True)
            except Exception:
                # Existing reader emits bounded SQL error evidence. Do not
                # publish an empty frame or log private exception text here.
                pass
        with _lock:
            if not _wanted:return

def shutdown():
    _stop.set();_wake.set()
    with _lock:_wanted.clear();thread=_thread
    if thread is not None and thread is not threading.current_thread():thread.join(timeout=.15)

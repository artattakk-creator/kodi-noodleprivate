"""Coalesced local-only Now/Next refresh. GUI requests contain only identities.

Uses the one existing guide/mapping reader. No provider/HTTP/import/migration.
A fresh metadata/configuration revision still invalidates mismatched snapshots.
"""
import threading,time
_lock=threading.Lock();_wanted={};_due={};_failures86={};_thread=None;_wake=threading.Event();_stop=threading.Event()

def request(pid,sid):
    global _thread
    if _stop.is_set():return
    from epg_handoff63 import profile_scope
    key=(profile_scope(),str(pid),str(sid));now=time.monotonic()
    revision86=__import__('epg_status').revision(pid)
    with _lock:
        previous86=_failures86.get(key)
        if previous86 and previous86[0]!=revision86:_due.pop(key,None);_failures86.pop(key,None)
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
            reader=None;values86={}
            revision86=__import__('epg_status').revision(pid)
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
                        values86.update(now_next(pid,rows[offset:offset+16],mappings,display_only65=True) or {})
            except Exception:
                # Existing reader emits bounded SQL error evidence. Do not
                # publish an empty frame or log private exception text here.
                pass
            finally:
                # Reader is a stateless facade: every _query closes its own
                # connection in finally. There is no facade.close() lifecycle.
                if revision86==__import__('epg_status').revision(pid):
                    with _lock:
                        for sid86 in sids:
                            key86=(profile_scope(),str(pid),str(sid86));info86=values86.get(str(sid86),{})
                            if info86.get('now'):_failures86.pop(key86,None)
                            else:
                                old86=_failures86.get(key86);count86=min(4,(old86[1] if old86 and old86[0]==revision86 else 0)+1)
                                _failures86[key86]=(revision86,count86);_due[key86]=time.monotonic()+(30,60,180,300)[count86-1]
                        while len(_failures86)>256:_failures86.pop(next(iter(_failures86)))
        # Stay single-flight until shutdown; a request can arrive immediately
        # after the queue is drained. Do not lose that wake in a dying thread.

def shutdown():
    _stop.set();_wake.set()
    with _lock:_wanted.clear();thread=_thread
    if thread is not None and thread is not threading.current_thread():thread.join(timeout=.15)

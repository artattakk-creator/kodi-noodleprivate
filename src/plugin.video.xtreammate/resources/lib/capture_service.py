"""Service-owned single independent recording; no player/GUI modifications."""
import os
import threading
import time
import xbmc

_guard=threading.Lock();_thread=None;_stop=threading.Event()


def resolve(job):
    from portals import get_by_id
    from library_index import Reader
    from direct_ts import Failure
    portal=get_by_id(job['pid'])
    if not portal or not portal.get('enabled',True):raise Failure('PORTAL_UNAVAILABLE')
    channel=Reader(job['pid'],timeout=.15,query_seconds=1).get('live',job['sid'])
    if not channel:raise Failure('CHANNEL_UNAVAILABLE')
    if portal.get('type')=='xtream':
        from xtream import XtreamClient
        return XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass']).live_stream_url(channel['sid'],ext='ts')
    if portal.get('type')=='m3u':
        from source_adapters import for_portal
        url,headers=for_portal(portal).play_uri('live',channel['sid'])
        if headers:raise Failure('UNSUPPORTED_HEADERS')
        return url
    raise Failure('UNSUPPORTED_PORTAL')


def _run():
    try:import fcntl
    except ImportError:return
    from capture_store import path,rows,update,interrupted
    from direct_ts import Recorder,error_code
    from transfer_diagnostics import encode,mark
    lock=None;active=None;worker=None;job=None;last=0
    monitor=xbmc.Monitor()
    try:
        lock=os.open(path()+'.owner',os.O_CREAT|os.O_RDWR,0o600)
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:return
        interrupted()
        while not _stop.is_set() and not monitor.abortRequested():
            try:
                snapshot=rows()
                if active is not None:
                    current=next((r for r in snapshot if r['id']==job['id']),None)
                    if current and current['stop']:active.finish()
                    if not worker.is_alive():
                        state=dict(active.state);mark('CAPTURE','STATE',state)
                        update(job['id'],status=state['status'],bytes=state['bytes'],seconds=state['seconds'],code=encode(state),file=state.get('file',''))
                        active=None;worker=None;job=None
                    elif time.monotonic()-last>=1:
                        state=dict(active.state);last=time.monotonic();mark('CAPTURE','STATE',state)
                        update(job['id'],status=state['status'] if state['status']!='pending' else 'starting',bytes=state['bytes'],seconds=state['seconds'],code=encode(state))
                if active is None:
                    job=next((r for r in reversed(snapshot) if r['status']=='pending'),None)
                    if job:
                        if job['stop'] or time.time()-job['created']>120:
                            update(job['id'],status='failed',code='CANCELLED' if job['stop'] else 'STALE_REQUEST');job=None
                        else:
                            update(job['id'],status='starting')
                            try:
                                from capture_target import probe
                                probe(job['target'],create=True)
                                mark('CAPTURE','TARGET_READY')
                                mark('CAPTURE','SOURCE_RESOLVE')
                                source=resolve(job)
                                current=next((r for r in rows() if r['id']==job['id']),None)
                                if _stop.is_set() or monitor.abortRequested() or current is None or current['stop']:
                                    update(job['id'],status='failed',code='CANCELLED');job=None;continue
                                os.makedirs(job['target'],mode=0o700,exist_ok=True)
                                active=Recorder(source,job['target'],job['duration'],separate_connection=True)
                                # Stable own ID relates recovery artifacts to the job.
                                active.ident=job['id'];active.state['id']=job['id']
                                worker=threading.Thread(target=active.run,name='XCMate-capture',daemon=True);worker.start()
                            except Exception as exc:
                                mark('CAPTURE','FAILED',encode(exc,error_code(exc)))
                                update(job['id'],status='failed',code=encode(exc,error_code(exc)));active=None;worker=None;job=None
            except Exception:
                # A temporary DB failure never starts a second recorder.
                pass
            if monitor.waitForAbort(.2):break
    finally:
        if active is not None:
            active.stop();worker.join(2.5)
            try:
                state=dict(active.state)
                update(job['id'],status='partial',bytes=state['bytes'],seconds=state['seconds'],code='SERVICE_INTERRUPTED')
            except Exception:pass
            # Keep the cross-interpreter lease until outstanding IO has exited.
            if worker.is_alive():worker.join()
        if lock is not None:os.close(lock)


def poll():
    global _thread
    if _stop.is_set():return
    from capture_store import path
    if not os.path.exists(path()):return
    with _guard:
        if _thread is None or not _thread.is_alive():
            _thread=threading.Thread(target=_run,name='XCMate-capture-owner',daemon=True);_thread.start()


def shutdown():
    _stop.set()
    if _thread is not None:_thread.join(.25)

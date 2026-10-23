"""Explicit enqueue/actions; a separate bounded service worker owns transfers."""
import os,threading
from download_sources import DownloadFailure

_guard=threading.Lock();_worker=None;_stop=threading.Event()


def folder():
    from download_targets import configured
    return configured()


def enqueue(portal,kind,sid,series_id='',cancel=lambda:False):
    import download_store
    from download_sources import describe
    from media_files import probe
    if cancel():raise InterruptedError()
    target=folder();probe(target)
    media=describe(portal,kind,sid,series_id,target)
    if cancel():raise InterruptedError()
    ident=download_store.enqueue(media)
    if cancel():download_store.command(ident,'cancel')
    return ident


def _run():
    import xbmc,fcntl
    from download_store import path
    from download_worker import run_one
    lock=os.open(path()+'.owner',os.O_CREAT|os.O_RDWR,0o600)
    try:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:return
        monitor=xbmc.Monitor();cancel=lambda:_stop.is_set() or monitor.abortRequested()
        while not cancel():
            try:worked=run_one(cancel)
            except Exception:worked=False
            if monitor.waitForAbort(.1 if worked else 1):break
    finally:os.close(lock)


def shutdown():
    _stop.set()
    if _worker is not None:_worker.join(.25)


def poll():
    from download_store import path
    global _worker
    if _stop.is_set() or not os.path.isfile(path()):return
    with _guard:
        if _worker is None or not _worker.is_alive():
            _worker=threading.Thread(target=_run,name='XCMate-downloads',daemon=True);_worker.start()


def delete(ident):
    """Explicit confirmed action only; content identity guards foreign files."""
    import download_store as store
    import media_files as files
    from download_worker import _hash
    row=store.get(ident)
    if not row or row['state'] not in ('COMPLETE','FAILED','CANCELLED','PAUSED') or row['lease']>__import__('time').time():raise DownloadFailure('BUSY')
    uri=row['file'] if row['state']=='COMPLETE' else row['part']
    if not uri:return False
    root=row['media']['target'].rstrip('/')+'/'
    if not uri.startswith(root) or (row['state']!='COMPLETE' and not files.owned_part(uri,ident)):raise DownloadFailure('UNSAFE_TARGET')
    expected=row['total'] if row['state']=='COMPLETE' else row['bytes']
    if files.exists(uri):
        if files.size(uri)!=expected or _hash(uri,expected)!=row['digest']:raise DownloadFailure('FILE_CHANGED')
        files.remove(uri)
    connection=store.db()
    try:
        with connection:connection.execute("UPDATE jobs SET state='CANCELLED',code='FILE_DELETED',hidden=1 WHERE id=?",(ident,))
    finally:connection.close()
    return True


def playable(row):
    import media_files as files
    if not row or row['state']!='COMPLETE':raise DownloadFailure('NOT_COMPLETE')
    uri=row['file'];root=row['media']['target'].rstrip('/')+'/'
    if not uri.startswith(root) or uri.endswith('.part'):raise DownloadFailure('UNSAFE_TARGET')
    if not files.exists(uri) or files.size(uri)!=row['total']:raise DownloadFailure('TARGET_UNAVAILABLE')
    return uri

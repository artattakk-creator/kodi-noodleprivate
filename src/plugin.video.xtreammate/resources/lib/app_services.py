"""Optional additive work, isolated from the frozen live navigator loop."""
import threading
import time

_worker=None
_guard=threading.Lock()
_retry_after={}
_bootstrapped=set()
_stop=threading.Event()


def refresh_local(cancel=lambda:False):
    if cancel():return
    from portals import get_active
    from xtream import XtreamClient
    from library_index import refresh
    for portal in get_active():
        if cancel():return
        if portal.get('type') not in ('xtream','m3u','stb'): continue
        if time.monotonic()<_retry_after.get(portal['id'],0): continue
        try:
            if portal['type']=='xtream': client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
            else:
                from source_adapters import for_portal
                client=for_portal(portal)
            if portal['type']=='xtream' and not hasattr(client,'iter_catalog'):
                refresh(portal,client)
            elif portal['id'] not in _bootstrapped:
                from catalog_sync import request
                for kind in ('live','vod','series'):
                    if cancel():return
                    request(portal,kind,portal.get('start_group_id','') if kind=='live' else '',priority=20)
                _bootstrapped.add(portal['id'])
            from guide_store import refresh as refresh_guide
            if cancel():return
            refresh_guide(portal)
            if cancel():return
            from library_index import Reader,initial_group
            from media_art import request
            reader=Reader(portal['id'])
            for kind in ('vod','series'):
                rows,_=reader.rail(kind,limit=12)
                request(rows)
            start=reader.get('live',str(portal.get('start_stream_id') or ''))
            cid=initial_group(portal,reader.groups('live'),start)
            if cid:
                rows,_=reader.page('live',category=cid,limit=12,pin=start['sid'] if start else None)
                request(rows)
            _retry_after.pop(portal['id'],None)
        except Exception as exc:
            # A disk-full/over-budget/corrupt import must not reparse the same
            # large local snapshot every 15 seconds. Explicit UI requests are
            # independent; automatic retries wait five minutes.
            _retry_after[portal['id']]=time.monotonic()+300
            from utils import warn
            warn('Local library index: '+type(exc).__name__)


def _run():
    import xbmc
    monitor=xbmc.Monitor()
    cancelled=lambda:_stop.is_set() or monitor.abortRequested()
    while not cancelled():
        worked=False
        try:
            from artwork_db import maintain
            maintain(cancel=cancelled)
        except Exception: pass
        if cancelled():break
        # Optional guide/art preparation may fail independently. It must not
        # starve an otherwise valid movie/series sync request.
        try: refresh_local(cancelled)
        except Exception: pass
        if cancelled():break
        try:
            from art_store import prefetch_selected
            prefetch_selected()
        except Exception: pass
        if cancelled():break
        try:
            from startup_preload import prepare
            prepare(cancel=cancelled)
        except Exception: pass
        if cancelled():break
        try:
            from catalog_sync import run_next
            worked=run_next(cancelled)
        except Exception: pass
        if cancelled():break
        try:
            from guide_timers import poll as poll_timers
            poll_timers()
        except Exception: pass
        if monitor.waitForAbort(0.1 if worked else 5): break


def poll():
    global _worker
    from capture_service import poll as poll_captures
    poll_captures()
    from downloads import poll as poll_downloads
    poll_downloads()
    with _guard:
        if _stop.is_set():return
        if _worker is None or not _worker.is_alive():
            _worker=threading.Thread(target=_run,name='XCMate-library',daemon=True)
            _worker.start()
    from media_autoplay import poll as poll_autoplay
    poll_autoplay()
    from media_progress import poll as poll_media
    poll_media()

    from media_osd import poll as poll_osd
    poll_osd()


def shutdown():
    """Prevent new optional work; never block Kodi waiting on provider IO.

    Already running non-cancellable HTTP may outlive this bounded join. That
    limitation is reported explicitly, rather than claiming a forced stop.
    """
    from capture_service import shutdown as shutdown_captures
    shutdown_captures()
    from downloads import shutdown as shutdown_downloads
    shutdown_downloads()
    with _guard:
        _stop.set();worker=_worker
    if worker is not None and worker is not threading.current_thread():worker.join(timeout=.2)
    stopped=worker is None or not worker.is_alive()
    from boot_diagnostics import mark
    mark('APP_WORKER_STOPPED' if stopped else 'APP_WORKER_STOP_PENDING')
    return stopped

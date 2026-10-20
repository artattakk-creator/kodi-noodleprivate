"""Optional additive work, isolated from the frozen live navigator loop."""
import threading
import time

_worker=None
_guard=threading.Lock()
_retry_after={}
_bootstrapped=set()


def refresh_local():
    from portals import get_active
    from xtream import XtreamClient
    from library_index import refresh
    for portal in get_active():
        if portal.get('type')!='xtream': continue
        if time.monotonic()<_retry_after.get(portal['id'],0): continue
        try:
            client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
            if not hasattr(client,'iter_catalog'):
                refresh(portal,client)
            elif portal['id'] not in _bootstrapped:
                from catalog_sync import request
                for kind in ('live','vod','series'):
                    request(portal,kind,portal.get('start_group_id','') if kind=='live' else '',priority=20)
                _bootstrapped.add(portal['id'])
            from guide_store import refresh as refresh_guide
            refresh_guide(portal)
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
    while not monitor.abortRequested():
        worked=False
        # Optional guide/art preparation may fail independently. It must not
        # starve an otherwise valid movie/series sync request.
        try: refresh_local()
        except Exception: pass
        try:
            from art_store import prefetch_selected
            prefetch_selected()
        except Exception: pass
        try:
            from startup_preload import prepare
            prepare(cancel=monitor.abortRequested)
        except Exception: pass
        try:
            from catalog_sync import run_next
            worked=run_next(monitor.abortRequested)
        except Exception: pass
        try:
            from guide_timers import poll as poll_timers
            poll_timers()
        except Exception: pass
        if monitor.waitForAbort(0.1 if worked else 5): break


def poll():
    global _worker
    with _guard:
        if _worker is None or not _worker.is_alive():
            _worker=threading.Thread(target=_run,name='XCMate-library',daemon=True)
            _worker.start()
    from media_progress import poll as poll_media
    poll_media()


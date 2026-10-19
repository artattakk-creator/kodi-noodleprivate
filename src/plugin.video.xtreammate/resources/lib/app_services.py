"""Optional additive work, isolated from the frozen live navigator loop."""
import threading

_worker=None
_guard=threading.Lock()


def refresh_local():
    from portals import get_active
    from xtream import XtreamClient
    from library_index import refresh
    for portal in get_active():
        if portal.get('type')!='xtream': continue
        try:
            client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
            refresh(portal,client)
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
        except Exception as exc:
            from utils import warn
            warn('Local library index: '+type(exc).__name__)


def _run():
    import xbmc
    monitor=xbmc.Monitor()
    while not monitor.abortRequested():
        try: refresh_local()
        except Exception: pass
        try:
            from guide_timers import poll as poll_timers
            poll_timers()
        except Exception: pass
        if monitor.waitForAbort(15): break


def poll():
    global _worker
    with _guard:
        if _worker is None:
            _worker=threading.Thread(target=_run,name='XCMate-library',daemon=True)
            _worker.start()
    from media_progress import poll as poll_media
    poll_media()


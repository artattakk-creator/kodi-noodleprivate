"""Optional additive work, isolated from the frozen live navigator loop."""
import threading
import time
import service_runtime as runtime

_worker=None
_guard=threading.Lock()
_retry_after={}
_bootstrapped=set()
_local_once48=set()
_stop=threading.Event()


def refresh_local(cancel=lambda:False):
    from startup48 import suspended
    if suspended():return
    from widget_hooks45 import prepare as prepare_widget_bindings
    prepare_widget_bindings()
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
            from catalog_delta52 import reconcile_series
            reconcile_series(portal)
            if portal['type']=='xtream' and not hasattr(client,'iter_catalog'):
                refresh(portal,client)
            elif portal['id'] not in _bootstrapped:
                from catalog_sync import request
                from library_index import Reader
                existing=Reader(portal['id'])
                for kind in ('live','vod','series'):
                    if cancel():return
                    if portal.get('include_'+kind,True) and not existing.state(kind):
                        request(portal,kind,portal.get('start_group_id','') if kind=='live' else '',priority=20)
                _bootstrapped.add(portal['id'])
            from guide_store import refresh as refresh_guide
            if cancel():return
            from programme_index46 import prepare_local as prepare_programmes46
            prepare_programmes46(portal,cancel)
            try:
                if portal['id'] not in _local_once48:
                    refresh_guide(portal);_local_once48.add(portal['id'])
            except Exception:
                from utils import warn
                warn('GUIDE_PREWARM_UNAVAILABLE')
            if cancel():return
            # Bounded indexed widget pages replace full-catalogue rail COUNTs.
            # Prepare references in this long-lived data worker, not IR/render.
            from widget_data41 import snapshot
            from widget_art44 import prepare
            for kind in ('live','vod','series'):
                if cancel():return
                try:
                    rows,code=snapshot(portal,kind,background=True)
                    if kind=='live':
                        from widget_home50 import rows as start_group_rows56
                        previous_code56=code;rows,code=start_group_rows56(portal)
                        if previous_code56=='READ_ONLY' and code=='READY':code='READ_ONLY'
                    from widget_diagnostics47 import inspect_index
                    inspect_index(portal,kind,rows,code)
                    if kind=='live':
                        from programme_prefetch48 import prepare as prefetch_events48
                        prefetch_events48(portal,rows,cancel)
                    try:
                        prepare(portal['id'],rows)
                        from programme_assets47 import prepare as prepare_assets47
                        prepare_assets47(portal,kind,rows,cancel,provider_only=kind in ('vod','series'))
                    except Exception:
                        from widget_diagnostics47 import note
                        note(portal['id'],kind,'ASSETS','PREPARE_UNAVAILABLE')
                    if cancel():return
                    from widget_live47 import publish
                    publish(portal,kind,rows,code)
                except Exception:
                    # A failed Live/film preparation must not starve the
                    # successful series row or another independent widget.
                    from widget_diagnostics47 import note
                    note(portal['id'],kind,'SELECT','WORKER_UNAVAILABLE')
            _retry_after.pop(portal['id'],None)
        except Exception as exc:
            # A disk-full/over-budget/corrupt import must not reparse the same
            # large local snapshot every 15 seconds. Explicit UI requests are
            # independent; automatic retries wait five minutes.
            _retry_after[portal['id']]=time.monotonic()+300
            from utils import warn
            warn('Local library index: '+type(exc).__name__)


@runtime.background
def _run():
    import xbmc
    monitor=xbmc.Monitor()
    cancelled=lambda:_stop.is_set() or monitor.abortRequested()
    from startup48 import Phases,suspended,mark
    phases48=Phases()
    next_prepare=0
    while not cancelled():
        runtime.emit()
        if suspended():
            if runtime.wait_abort(monitor,.1,_stop):break
            continue
        if runtime.pressure():
            from art_diagnostics import publish
            publish('service','MEMORY_PRESSURE')
            if runtime.wait_abort(monitor,.5,_stop):break
            continue
        worked=False
        try:
            from widget_notice46 import focused
            focused()
        except Exception:pass
        prepare_now=time.monotonic()>=next_prepare
        if phases48.network() and phases48.due('maintenance',300):
            next_prepare=time.monotonic()+5
            try:
                from artwork_db import maintain
                maintain(cancel=cancelled)
            except MemoryError:runtime.note_pressure()
            except Exception:pass
        if cancelled():break
        # Persisted image jobs resume even when catalogue warming is disabled
        # or no fresh media window requests an enrolment. Data worker only.
        try:
            from media_art import ensure_worker
            if phases48.network():ensure_worker()
        except MemoryError:runtime.note_pressure()
        except Exception:pass
        if cancelled():break
        if prepare_now and phases48.network():
            next_prepare=time.monotonic()+5
            # Optional guide/art preparation may fail independently. It must not
            # starve an otherwise valid movie/series sync request.
            started48=time.monotonic()
            try:
                refresh_local(cancelled)
                mark('LOCAL',duration_ms=(time.monotonic()-started48)*1000)
            except MemoryError:runtime.note_pressure()
            except Exception: pass
            if cancelled():break
            try:
                from art_store import prefetch_selected
                if phases48.network() and phases48.due('prefetch',300):prefetch_selected()
            except MemoryError:runtime.note_pressure()
            except Exception: pass
            if cancelled():break
            try:
                from startup_preload import prepare
                if phases48.network():prepare(cancel=cancelled)
            except MemoryError:runtime.note_pressure()
            except Exception: pass
            if cancelled():break
        try:
            from catalog_delta import run_next as run_delta
            worked=run_delta(cancelled) or worked
        except MemoryError:runtime.note_pressure()
        except Exception:pass
        try:
            from catalog_sync import run_next
            worked=run_next(cancelled) or worked
        except MemoryError:runtime.note_pressure()
        except Exception: pass
        if cancelled():break
        try:
            from genre_search import run_next as index_genres
            worked=index_genres(cancelled) or worked
        except MemoryError:runtime.note_pressure()
        except Exception:pass
        if cancelled():break
        try:
            from guide_timers import poll as poll_timers
            poll_timers()
        except MemoryError:runtime.note_pressure()
        except Exception: pass
        if runtime.wait_abort(monitor,0.1 if worked else .5,_stop):break


def poll():
    if _stop.is_set():return
    from app_imports46 import ensure as imports_ready46
    if not imports_ready46():return
    from widget_notice46 import poll as poll_widget_lists
    poll_widget_lists()
    from guide_backup44 import poll as poll_guide_backup
    poll_guide_backup()
    from app_entry import observe
    observe()
    global _worker
    if _stop.is_set():return
    runtime.install()
    from stability_monitor import ensure
    ensure()
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
    _stop.set()
    from programme_art46 import shutdown as shutdown_programme46
    from programme_urls55 import shutdown as shutdown_urls55
    shutdown_urls55()
    shutdown_programme46()
    for name in ('downloads','capture_service','media_art'):
        event=getattr(__import__(name),'_stop',None)
        if event is not None:event.set()
    runtime.stop()
    from media_art import shutdown as shutdown_art
    shutdown_art(timeout=.05)
    from stability_monitor import shutdown as shutdown_monitor
    shutdown_monitor()
    from capture_service import shutdown as shutdown_captures
    shutdown_captures()
    from downloads import shutdown as shutdown_downloads
    shutdown_downloads()
    with _guard:
        _stop.set();worker=_worker
    if worker is not None and worker is not threading.current_thread():worker.join(timeout=.2)
    candidates=[worker]+[t for t in threading.enumerate() if t is not threading.current_thread() and (t.name.startswith('XCMate') or t.name.startswith('epg_warmup_') or t.name.startswith('ThreadPoolExecutor'))]
    stopped=all(t is None or not t.is_alive() for t in candidates)
    from boot_diagnostics import mark
    mark('APP_WORKER_STOPPED' if stopped else 'APP_WORKER_STOP_PENDING')
    return stopped

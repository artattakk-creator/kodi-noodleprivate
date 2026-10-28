"""Prime optional imports away from the service's input/window owner thread."""
import importlib,threading,time
_thread=None;_ready=threading.Event();_retry=0
MODULES=('widget_notice46','guide_backup44','app_entry','stability_monitor',
         'capture_service','downloads','media_autoplay','media_progress','media_osd')


def ensure():
    global _thread
    if _ready.is_set():return True
    if time.monotonic()<_retry:return False
    if _thread is None or not _thread.is_alive():
        _thread=threading.Thread(target=_prime,name='XCMate-import46',daemon=True)
        _thread.start()
    return _ready.is_set()


def _prime():
    global _retry
    try:
        for name in MODULES:importlib.import_module(name)
    except (ImportError,RuntimeError,MemoryError,AttributeError,OSError,ValueError):_retry=time.monotonic()+5
    else:_ready.set()

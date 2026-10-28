"""One discovery deadline, request budget and cancellation per wizard worker.

The native UI remains cancellable. A Python deadline cannot forcibly interrupt
platform DNS; no new discovery worker is spawned while that call still owns its
slot. No provider/PIN/profile settings are rewritten to shorten a request.
"""
import functools
import threading
import time
_local=threading.local()
_slot=threading.BoundedSemaphore(1)


def active():return getattr(_local,'deadline',None) is not None


def check():
    if not active():return
    if _local.cancel():raise InterruptedError('WIZARD_CANCELLED')
    # No aggregate discovery duration: each HTTP operation retains its own limit.


def policy(timeout,seconds,retries):
    if not active():return timeout,seconds,retries
    check()
    return min(timeout,15),min(seconds,60),min(retries,1)


def byte_limit(value):return min(value,2*1024*1024) if active() else value


def discovery(function):
    @functools.wraps(function)
    def run(self,cancel=lambda:False,status=lambda *a:None):
        if not _slot.acquire(blocking=False):raise OSError('WIZARD_DISCOVERY_BUSY')
        previous=(getattr(_local,'deadline',None),getattr(_local,'cancel',None))
        _local.deadline=float('inf');_local.cancel=cancel
        from setup_trace import mark
        mark('DISCOVER_BEGIN',getattr(self,'pid',''))
        try:
            check();value=function(self,cancel,status);check()
            mark('DISCOVER_DONE',getattr(self,'pid',''));return value
        except BaseException:
            mark('DISCOVER_FAILED',getattr(self,'pid',''));raise
        finally:
            _local.deadline,_local.cancel=previous;_slot.release()
    return run

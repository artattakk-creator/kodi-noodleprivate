"""Finite, reentrant cross-interpreter lock for local profile configuration.

Kodi Android/Linux uses flock. The lock file contains no user data; reads and
normal startup do not acquire this write lock.
"""
from contextlib import contextmanager
from functools import wraps
import os
import threading
import time

_guard=threading.RLock()
_local=threading.local()


@contextmanager
def writing(timeout=1):
    from utils import addon_data_dir
    if not _guard.acquire(timeout=timeout): raise TimeoutError('profile write busy')
    try:
        if getattr(_local,'depth',0):
            _local.depth+=1
            try: yield
            finally: _local.depth-=1
            return
        import fcntl
        descriptor=os.open(os.path.join(addon_data_dir(),'.xcmate-config.lock'),os.O_CREAT|os.O_RDWR,0o600)
        deadline=time.monotonic()+timeout
        try:
            while True:
                try: fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB);break
                except BlockingIOError:
                    if time.monotonic()>=deadline: raise TimeoutError('profile write busy')
                    time.sleep(.02)
            _local.depth=1
            try: yield
            finally: _local.depth=0;fcntl.flock(descriptor,fcntl.LOCK_UN)
        finally: os.close(descriptor)
    finally: _guard.release()


def serialized(function):
    @wraps(function)
    def wrapped(*args,**kwargs):
        with writing(): return function(*args,**kwargs)
    return wrapped

"""One nonblocking profile-local writer gate for downloads and user migration."""
from contextlib import contextmanager
import fcntl
import os
import threading

_local=threading.local()


class WriterBusy(OSError):pass


@contextmanager
def writer():
    if getattr(_local,'depth',0):
        _local.depth+=1
        try:yield
        finally:_local.depth-=1
        return
    from utils import addon_data_dir
    fd=os.open(os.path.join(addon_data_dir(),'.artwork-writer.lock'),os.O_CREAT|os.O_RDWR,0o600)
    try:
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise WriterBusy('ARTWORK_WRITER_BUSY') from None
        _local.depth=1
        try:yield
        finally:_local.depth=0
    finally:
        fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)


def guarded(function):
    from functools import wraps
    @wraps(function)
    def run(*args,**kwargs):
        with writer():return function(*args,**kwargs)
    return run

"""Thread-local, page-scoped RO connections, never a cross-thread SQLite handle.

Keep one committed read snapshot per database for a bounded viewport. Borrowers
cannot close it early. Writers always use their own connections. This removes
hundreds of reconnect/schema/DNS-policy reads from an 88-channel publication.
"""
from contextlib import contextmanager
from functools import wraps
import threading

_local=threading.local()


class Borrowed:
    def __init__(self,db):self._db=db
    def __getattr__(self,name):return getattr(self._db,name)
    def close(self):pass


@contextmanager
def session():
    if getattr(_local,'state',None) is not None:
        yield
        return
    state=dict(connections={},memo={})
    _local.state=state
    try:yield
    finally:
        _local.state=None
        for db in state['connections'].values():db.close()


def scoped(function):
    @wraps(function)
    def wrapped(*args,**kwargs):
        with session():return function(*args,**kwargs)
    return wrapped


def borrowed(filename):
    state=getattr(_local,'state',None)
    db=state['connections'].get(str(filename)) if state else None
    if db is not None:
        # A prior bounded cursor's deadline must not poison a later point read.
        db.set_progress_handler(None,0)
        return Borrowed(db)
    return None


def retain(filename,db):
    state=getattr(_local,'state',None)
    if state is None:return db
    try:db.execute('BEGIN')
    except Exception:
        db.close()
        raise
    state['connections'][str(filename)]=db
    return Borrowed(db)


def memo(key,load):
    state=getattr(_local,'state',None)
    if state is None:return load()
    if key not in state['memo']:state['memo'][key]=load()
    return state['memo'][key]

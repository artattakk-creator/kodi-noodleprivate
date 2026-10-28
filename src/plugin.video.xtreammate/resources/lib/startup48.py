"""Bounded startup phases and OS-held singleton, no settings/schema migration.

A Kodi heartbeat is telemetry, not mutual exclusion: importing/starting a
second service after five busy seconds must never spawn a second worker tree.
The flock lives until service termination, including across Python interpreters.
"""
import contextlib
import fcntl
import os
import time


def mark(phase, code='READY', duration_ms=0, rows=0, retry=0):
    phases={'SERVICE','DUPLICATE','LOCAL','NETWORK','WIDGET','EXIT','BACKGROUND','IMAGE','MAPPING'}
    codes={'READY','BUSY','DEFERRED','FAILED','NO_PORTAL','SETUP_ACTIVE','BUDGET','UNAVAILABLE','SKIPPED'}
    if phase not in phases:return
    code=code if code in codes else 'FAILED'
    try:
        import xbmc
        from service_runtime import memory
        values=memory()
        fields=' '.join(k+'='+str(max(0,int(values.get(k,0)))) for k in ('rss_kib','virtual_kib','os_threads'))
        xbmc.log('[XCMate][START48] phase='+phase+' code='+code+' duration_ms='+str(round(max(0,duration_ms),1))+' rows='+str(max(0,int(rows)))+' retry='+str(max(0,int(retry)))+' '+fields,xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError,ValueError,MemoryError):pass


@contextlib.contextmanager
def singleton(name='service'):
    from artwork_config import root
    if name not in ('service','library'):raise ValueError('UNKNOWN_SERVICE')
    filename=os.path.join(root(),'.'+name+'48.lock')
    fd=None;acquired=False
    try:
        fd=os.open(filename,os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0),0o600)
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);acquired=True
        except BlockingIOError:pass
        yield acquired
    finally:
        if fd is not None:
            if acquired:fcntl.flock(fd,fcntl.LOCK_UN)
            os.close(fd)


class Phases:
    """Local snapshots first; one optional network phase after quiet startup.

    Timers do not wait on the GUI. Explicit user requests use their own queues.
    During an own pending Stop, optional work yields to the existing watchdog.
    """
    def __init__(self,clock=None):
        self.clock=clock or time.monotonic;self.started=self.clock();self.next={}
    def due(self,name,interval):
        now=self.clock()
        if now<self.next.get(name,0):return False
        self.next[name]=now+interval;return True
    def network(self):
        if self.clock()-self.started<15:return False
        from setup_navigation import active
        if active():return False
        from exit_jobs import blocked
        if blocked():return False
        return True


def suspended():
    """Properties only: never query a potentially locked native Player."""
    try:
        from exit_jobs import blocked
        if blocked():return True
        from live_exit import state
        value=state()
        return bool(value and value['phase'] in ('requested','stopping','home'))
    except (ImportError,AttributeError,RuntimeError,ValueError):return True

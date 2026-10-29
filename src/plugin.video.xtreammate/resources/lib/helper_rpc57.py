"""Single-flight public Kodi RPC, never on the GUI/owner thread.

Kodi cannot cancel an executeJSONRPC call. A timed-out call stays the ONLY
in-flight RPC until it exits; no accumulating replacement threads, late writes
or native player/window commands. Callers cancel their own wait and discard it.
"""
import json
import threading
import time

_lock=threading.Lock()
_active=None
MAX_REPLY=512*1024
METHODS=frozenset(('Addons.GetAddonDetails','Files.GetDirectory','VideoLibrary.GetMovies',
                   'VideoLibrary.GetTVShows','VideoLibrary.GetEpisodes'))


class Error(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)


def call(method,params,cancel=lambda:False,timeout=10,execute=None):
    global _active
    if method not in METHODS:raise Error('HELPER_BACKGROUND_UNAVAILABLE')
    if threading.current_thread() is threading.main_thread():raise Error('HELPER_BACKGROUND_UNAVAILABLE')
    if cancel():raise Error('CANCELLED')
    task=dict(done=threading.Event(),reply=None,error=None)
    request=json.dumps(dict(jsonrpc='2.0',id=57,method=method,params=params))
    def run():
        try:
            import xbmc
            raw=(execute or xbmc.executeJSONRPC)(request)
            if not isinstance(raw,str) or len(raw)>MAX_REPLY or len(raw.encode())>MAX_REPLY:raise Error('HELPER_BACKGROUND_UNAVAILABLE')
            value=json.loads(raw)
            if not isinstance(value,dict) or value.get('id')!=57 or value.get('jsonrpc')!='2.0':raise Error('HELPER_BACKGROUND_UNAVAILABLE')
            if 'error' in value:raise Error('HELPER_BACKGROUND_UNAVAILABLE')
            if not isinstance(value.get('result'),dict):raise Error('HELPER_BACKGROUND_UNAVAILABLE')
            task['reply']=value['result']
        except Error as exc:task['error']=exc.code
        except Exception:task['error']='HELPER_BACKGROUND_UNAVAILABLE'
        finally:task['done'].set()
    with _lock:
        if _active is not None and not _active['done'].is_set():raise Error('HELPER_BACKGROUND_UNAVAILABLE')
        _active=task
        try:threading.Thread(target=run,name='XCMate-helper-rpc57',daemon=True).start()
        except (RuntimeError,MemoryError):task['done'].set();raise Error('HELPER_BACKGROUND_UNAVAILABLE') from None
    deadline=time.monotonic()+max(.01,min(20,float(timeout)))
    while not task['done'].wait(.025):
        if cancel():raise Error('CANCELLED')
        if time.monotonic()>=deadline:raise Error('HELPER_TIMEOUT')
    if cancel():raise Error('CANCELLED')
    if task['error']:raise Error(task['error'])
    return task['reply']

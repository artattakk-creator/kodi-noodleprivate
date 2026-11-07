"""A transient resolver error is not proof that a verified CDN became private."""
import time,threading
_lock=threading.Lock();_values={}
def record(key,temporary):
    with _lock:
        _values[key]=(time.monotonic()+5,bool(temporary))
        while len(_values)>128:_values.pop(next(iter(_values)))
def temporary(key):
    with _lock:value=_values.get(key)
    return bool(value and value[0]>time.monotonic() and value[1])

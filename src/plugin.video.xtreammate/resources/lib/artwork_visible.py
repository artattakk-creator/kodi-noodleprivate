"""Bounded visible-image approval/cache; no external filesystem/DNS on GUI.

Dynamic mode passes approved provider URLs to Kodi's texture loader. XCMate
never downloads/archives them; Kodi may cache textures itself. Public-address
DNS validation is background-only, cached briefly, with no provider URL logs.
"""
import collections
import ipaddress
import queue
import socket
import threading
import time
from urllib.parse import urlsplit

_lock=threading.Lock();_values=collections.OrderedDict();_pending=set();_revision=0
_queues={'dynamic':queue.Queue(maxsize=128),'external':queue.Queue(maxsize=128)}
_threads={}
_dns_cache=collections.OrderedDict()
KODI_OPTIONS='|redirect-limit=0&connection-timeout=3&failonerror=true'


def syntactic(url):
    from media_art import valid_source
    if not valid_source(url) or '\\' in url or '|' in url:return False
    try:
        p=urlsplit(url)
        if p.username is not None or p.password is not None:return False
        if p.hostname.lower()=='localhost' or p.hostname.lower().endswith(('.localhost','.local','.internal')):return False
        try:return ipaddress.ip_address(p.hostname).is_global
        except ValueError:return '.' in p.hostname
    except (ValueError,AttributeError):return False


def public_dns(url):
    if not syntactic(url):return False
    p=urlsplit(url);key=(p.hostname,p.port or (443 if p.scheme=='https' else 80))
    with _lock:
        prior=_dns_cache.get(key)
        if prior and prior[0]>time.monotonic():return prior[1]
    try:
        values=socket.getaddrinfo(key[0],key[1],type=socket.SOCK_STREAM)
        approved=bool(values) and all(ipaddress.ip_address(value[4][0]).is_global for value in values)
    except (OSError,ValueError):approved=False
    with _lock:
        _dns_cache[key]=(time.monotonic()+(30 if approved else 5),approved)
        _dns_cache.move_to_end(key)
        while len(_dns_cache)>128:_dns_cache.popitem(last=False)
    return approved


def _process(kind,key,payload):
    if kind=='dynamic':
        approved=public_dns(payload)
        from art_diagnostics import publish
        publish('transfer','DYNAMIC_URL_APPROVED' if approved else 'DYNAMIC_SOURCE_UNAVAILABLE')
        return payload+KODI_OPTIONS if approved else ''
    storage,ident=payload
    from artwork_vfs import image_valid
    data=storage.read(ident,65536)
    return storage.make_display_uri(ident) if image_valid(data) else ''


def _run(kind):
    global _revision
    work=_queues[kind]
    while True:
        try:key,payload=work.get(timeout=2)
        except queue.Empty:
            with _lock:
                if work.empty():_threads.pop(kind,None);return
            continue
        try:
            try:value=_process(kind,key,payload)
            except Exception:value=''
            with _lock:
                _values[key]=(time.monotonic()+(30 if value else 5),value)
                _values.move_to_end(key);_pending.discard(key);_revision+=1
                while len(_values)>512:_values.popitem(last=False)
        finally:work.task_done()


def lookup(kind,key,payload):
    with _lock:
        value=_values.get(key)
        if value and value[0]>time.monotonic():return value[1]
        if key not in _pending:
            try:_queues[kind].put_nowait((key,payload));_pending.add(key)
            except queue.Full:return ''
        thread=_threads.get(kind)
        if thread is None or not thread.is_alive():
            thread=threading.Thread(target=_run,args=(kind,),name='XCMate-visible-'+kind,daemon=True)
            _threads[kind]=thread;thread.start()
    return ''


def dynamic(url):
    if not syntactic(url):return ''
    return lookup('dynamic',('dynamic',url),url)


def external(storage,ident):
    return lookup('external',('external',storage.resolve_target(),ident),(storage,ident))


def revision():
    with _lock:return _revision

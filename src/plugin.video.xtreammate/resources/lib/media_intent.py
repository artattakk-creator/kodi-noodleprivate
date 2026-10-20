"""Bounded GUI→resolver cancellation. A request alone never authorizes stop.

Only a matching current InfoTag may be stopped by playback_exit. Requests and
cancellations contain opaque IDs, no URLs or credentials, and expire locally.
"""
import json
import time
import uuid

REQUEST='XCMate.MediaRequest'
CANCELLED='XCMate.MediaCancelled'
TTL=120


def _read(key):
    import xbmcgui
    raw=xbmcgui.Window(10000).getProperty(key)
    try: return json.loads(raw) if raw and len(raw)<=4096 else None
    except (ValueError,TypeError): return None


def _valid(value,ttl=TTL):
    try:
        return (isinstance(value,dict) and all(isinstance(value.get(k),str) and 0<len(value[k])<=256 for k in ('nonce','pid','sid'))
                and 0<=time.time()-float(value.get('at',0))<ttl)
    except (ValueError,TypeError,OverflowError): return False


def _cancel(value):
    import xbmcgui
    entries=_read(CANCELLED)
    entries=[e for e in entries if _valid(e,86400)] if isinstance(entries,list) else []
    entries=[e for e in entries if e['nonce']!=value['nonce']]
    entries.append({k:value[k] for k in ('nonce','pid','sid')});entries[-1]['at']=time.time()
    entries=entries[-8:]
    while entries and len(json.dumps(entries))>4096: entries.pop(0)
    xbmcgui.Window(10000).setProperty(CANCELLED,json.dumps(entries))


def begin(pid,kind,sid):
    import xbmcgui
    previous=_read(REQUEST)
    if _valid(previous): _cancel(previous)
    value=dict(pid=str(pid),kind=kind,sid=str(sid),nonce=uuid.uuid4().hex,at=time.time())
    xbmcgui.Window(10000).setProperty(REQUEST,json.dumps(value))
    return value['nonce']


def cancelled(session):
    entries=_read(CANCELLED)
    return bool(isinstance(entries,list) and any(_valid(e,86400) and all(e[k]==session.get(k) for k in ('nonce','pid','sid')) for e in entries))


def cancel(pid,nonce):
    """Cancel only the request initiated by this XML window, even after resolve."""
    if not nonce: return False
    from media_progress import PROPERTY
    for key in (REQUEST,PROPERTY):
        value=_read(key)
        if _valid(value,86400) and value['nonce']==nonce and value['pid']==str(pid):
            _cancel(value);return True
    return False


def allowed(nonce,pid,kind,sid):
    value=_read(REQUEST)
    return bool(_valid(value) and value.get('kind')==kind and all(value[k]==str(v) for k,v in (('nonce',nonce),('pid',pid),('sid',sid))) and not cancelled(value))


def complete(nonce):
    import xbmcgui
    value=_read(REQUEST)
    if _valid(value) and value['nonce']==nonce: xbmcgui.Window(10000).clearProperty(REQUEST)

"""Explicit artwork opt-in nudges only the existing bounded background lane."""
import json,time,uuid
KEY='XCMate.ProgrammeRefresh63'
_seen={}
_retries={}

def request():
    import xbmcgui
    from epg_handoff63 import profile_scope
    xbmcgui.Window(10000).setProperty(KEY,json.dumps(dict(id=uuid.uuid4().hex,at=time.time(),profile=profile_scope())))

def active(pid):
    try:
        import xbmcgui
        raw=xbmcgui.Window(10000).getProperty(KEY)
        if not raw or len(raw)>256:return False
        value=json.loads(raw);age=time.time()-float(value['at'])
        from epg_handoff63 import profile_scope
        if value.get('profile')!=profile_scope():return False
        if not isinstance(value.get('id'),str) or len(value['id'])!=32 or not 0<=age<90:return False
        _seen[str(pid)]=value['id']
        while len(_seen)>8:_seen.pop(next(iter(_seen)))
        return True
    except (ImportError,AttributeError,RuntimeError,TypeError,ValueError,KeyError):return False

def retry(event,previous):
    """Consume one explicit activation per event; positives are never invalidated."""
    try:
        if not active(event.get('pid','')):return False
        import xbmcgui
        value=json.loads(xbmcgui.Window(10000).getProperty(KEY))
        key=(value['profile'],value['id'],str(event.get('key','')))
        if not key[2] or key in _retries:return False
        _retries[key]=True
        while len(_retries)>256:_retries.pop(next(iter(_retries)))
        return bool(previous and previous.get('source')=='placeholder' and previous.get('code') not in ('HTTP_RATE_LIMIT','CANCELLED'))
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,KeyError):return False

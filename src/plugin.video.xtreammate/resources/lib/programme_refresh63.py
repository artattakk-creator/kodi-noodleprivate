"""Explicit artwork opt-in nudges only the existing bounded background lane."""
import json,time,uuid
KEY='XCMate.ProgrammeRefresh63'
_seen={}

def request():
    import xbmcgui
    xbmcgui.Window(10000).setProperty(KEY,json.dumps(dict(id=uuid.uuid4().hex,at=time.time())))

def active(pid):
    try:
        import xbmcgui
        raw=xbmcgui.Window(10000).getProperty(KEY)
        if not raw or len(raw)>256:return False
        value=json.loads(raw);age=time.time()-float(value['at'])
        if not isinstance(value.get('id'),str) or len(value['id'])!=32 or not 0<=age<90:return False
        _seen[str(pid)]=value['id']
        while len(_seen)>8:_seen.pop(next(iter(_seen)))
        return True
    except (ImportError,AttributeError,RuntimeError,TypeError,ValueError,KeyError):return False

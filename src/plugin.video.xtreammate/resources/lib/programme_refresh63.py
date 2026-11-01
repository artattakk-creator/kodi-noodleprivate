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

_retry67={}
def retry67(event,previous):
 """One bounded retry of affected negatives; positives/files are untouched."""
 from utils import setting_bool
 own=setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False)
 maze=setting_bool('programme_tvmaze67',False)
 if not previous or previous.get('source')!='placeholder' or not (own or maze):return False
 if not maze and previous.get('code') not in ('HELPER_TIMEOUT','HELPER_BACKGROUND_UNAVAILABLE','HELPER_NOT_AVAILABLE','NOT_CLASSIFIED_MOVIE'):return False
 from epg_handoff63 import profile_scope
 key=(profile_scope(),event.get('key',''),maze);now=time.monotonic()
 if not key[1] or now-_retry67.get(key,-1e9)<300:return False
 _retry67[key]=now
 while len(_retry67)>256:_retry67.pop(next(iter(_retry67)))
 return True

"""Opaque playback-intent correlation; no account, title, ID, URL or exception."""
import time
_seen={}

def note(intent,stage,code='OK'):
 if not isinstance(intent,str) or len(intent)!=32 or any(c not in '0123456789abcdef' for c in intent):return
 if stage not in ('PLAY_ACTION','RESOLVER_BEGIN','ITEM_RESOLVED','KODI_RESOLVED','PLAYING','FAILED','START_TIMEOUT'):return
 if code not in ('OK','REJECTED','TIMEOUT','CANCELLED'):code='REJECTED'
 key=(intent,stage);now=time.monotonic()
 if now-_seen.get(key,-1e9)<30:return
 _seen[key]=now
 while len(_seen)>128:_seen.pop(next(iter(_seen)))
 import xbmc
 try:xbmc.log('[XCMate][VOD80] intent='+intent+' stage='+stage+' code='+code,xbmc.LOGINFO)
 except (RuntimeError,AttributeError):pass

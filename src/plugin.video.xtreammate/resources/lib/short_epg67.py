"""Portal cooldown for short-guide failures; no waiting or playback dependence."""
import time,threading
_lock=threading.Lock();_state={}
def key(client):return client._cache_key('get_short_epg')
def permit(client):
 with _lock:prior=_state.get(key(client))
 return not prior or time.monotonic()>=prior[0]
def success(client):
 with _lock:_state.pop(key(client),None)
def failed(client,error):
 status=getattr(error,'code',None) or getattr(getattr(error,'response',None),'status_code',0)
 status=status if type(status) is int and 100<=status<=599 else 0
 with _lock:
  attempt=min(5,_state.get(key(client),(0,0))[1]+1);delay=min(900,30*2**(attempt-1))
  if status in (404,410):delay=21600  # Unsupported endpoint; local/XMLTV remains authoritative.
  if status==429:
   try:delay=max(delay,min(900,int(getattr(error,'headers',{}).get('Retry-After','300'))))
   except (TypeError,ValueError,AttributeError):delay=max(delay,300)
  _state[key(client)]=(time.monotonic()+delay,attempt)
  while len(_state)>16:_state.pop(next(iter(_state)))
 try:
  import xbmc
  xbmc.log('[XCMate][SHORT67] request=GET_SHORT_EPG portal='+key(client)[:12]+' status='+str(status)+' code='+('TIMEOUT' if isinstance(error,TimeoutError) else 'SHORT_EPG_UNSUPPORTED' if status in (404,410) else 'HTTP_FAILURE' if status else 'NETWORK_FAILURE')+' retry_seconds='+str(delay)+' attempts='+str(attempt),xbmc.LOGWARNING)
 except (ImportError,AttributeError,RuntimeError):pass

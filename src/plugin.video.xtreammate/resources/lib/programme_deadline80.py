"""UI-only finite wait, without cancelling a foreign/initializing player."""
import time

WAITING=frozenset(('REQUESTED','WAITING_SERVICE','PENDING','QUEUED','RUNNING','AWAITING_BACKGROUND_REFRESH'))

def code(event,current):
 if current not in WAITING:return current
 from programme_requests68 import identity,_read,SLOTS
 tag=identity(event);value=_read('request.'+str(int(tag[:8],16)%SLOTS))
 if value.get('tag')==tag and time.time()-value.get('since70',time.time())>=45:return 'IMAGE_LOOKUP_TIMEOUT'
 return current

def retry_window(record,previous):
 """One new wait budget per explicit existing Retry marker, never per tick."""
 import json,xbmcgui
 from programme_refresh63 import KEY
 from epg_handoff63 import profile_scope
 record['retry80']=previous.get('retry80','')
 try:
  raw=xbmcgui.Window(10000).getProperty(KEY)
  marker=json.loads(raw) if raw and len(raw)<512 else {}
  tag=marker.get('id','')
  if len(tag)==32 and marker.get('profile')==profile_scope() and 0<=time.time()-float(marker.get('at',0))<90 and tag!=record['retry80']:
   record['since70']=time.time();record['retry80']=tag
 except (ValueError,TypeError,RuntimeError,AttributeError):pass

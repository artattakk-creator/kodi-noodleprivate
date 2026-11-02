"""Pure bounded status admission and explicit-retry observation. No IO/network."""
import json,math,time
def policy():
 from programme_policy68 import negative_scope
 return negative_scope({})
def valid(record,now=None):
 now=time.time() if now is None else now
 try:
  at=record['at'];art=record.get('art') or {};age=now-float(at)
  if not math.isfinite(age) or not 0<=age<86400:return False
  if age<300:return True
  until=art.get('until',0)
  return type(until) in (int,float) and math.isfinite(until) and now<until<=now+86400 and art.get('policy69')==policy()
 except (ValueError,TypeError,KeyError,OverflowError):return False
def retry(event,previous):
 # Read-only at all queue/consumer gates. Consuming a refresh here would steal
 # it from the resolver. New outcomes carry resolved_at55 after this marker.
 if not previous or previous.get('source')!='placeholder' or previous.get('code') in ('HTTP_RATE_LIMIT','CANCELLED'):return False
 try:
  import xbmcgui
  from epg_handoff63 import profile_scope
  from programme_refresh63 import KEY
  raw=xbmcgui.Window(10000).getProperty(KEY)
  marker=json.loads(raw) if raw and len(raw)<=256 else {}
  return marker.get('profile')==profile_scope() and isinstance(marker.get('id'),str) and len(marker['id'])==32 and 0<=time.time()-float(marker['at'])<90 and float(previous.get('resolved_at55',0))<float(marker['at'])
 except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,KeyError):return False
def waiting(event,previous=None):
 from programme_requests68 import identity,_read,SLOTS
 value=_read('request.'+str(int(identity(event)[:8],16)%SLOTS))
 if value.get('tag')!=identity(event) or not 0<=time.time()-value.get('at',0)<20:return previous or {}
 code='WAITING_SERVICE' if time.time()-value.get('since70',value['at'])>=15 else 'REQUESTED'
 return dict(previous or {},code=code,status68=code)

def legacy_negative(value):
 # Lazy one-event upgrade of affected .69 negatives, never a global reset.
 return isinstance(value,dict) and value.get('source')=='placeholder' and value.get('code') in ('HELPER_TIMEOUT','HELPER_BACKGROUND_UNAVAILABLE','NOT_SCHEDULED') and 'sources70' not in value

def since(previous,tag):
 now=time.time()
 try:
  first=float(previous.get('since70',previous.get('at',now)))
  if previous.get('tag')==tag and previous.get('scope')==__import__('programme_requests68').scope() and 0<=now-float(previous.get('at',0))<20 and math.isfinite(first) and 0<=now-first<86400:return first
 except (ValueError,TypeError,OverflowError):pass
 return now

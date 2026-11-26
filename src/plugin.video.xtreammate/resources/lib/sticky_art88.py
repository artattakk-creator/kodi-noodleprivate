"""Exact event + account + mapping + consent binding for fully decoded bytes.

Remote DNS leases never get extended. A session capability serves the bytes
already verified by the pinned transport, avoiding a second remote request.
"""
import json,time
PREFIX='XCMate.Sticky88.'
def key(event,source=None):return __import__('programme_display84').key(event,source)
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def valid(art,event=None):
 from programme_requests68 import scope,identity
 from programme_image69 import fingerprint,policy
 if not __import__('event_art81').allowed(art):return False
 source=art.get('source')
 if art.get('profile69')!=scope() or art.get('policy69')!=policy(source):return False
 if art.get('until',0)<=time.time() or __import__('widget_refs74').revoked(art.get('source_url','')):return False
 if event is not None:
  from event_cache88 import asset_key,receipt
  try:expected=asset_key(key(event,source),str(art.get('sha256','')),receipt(art))
  except (ValueError,TypeError,AttributeError):return False
  if art.get('asset88')!=expected or art.get('scope69')!=identity(event) or art.get('fingerprint')!=fingerprint(event,source):return False
 return __import__('decoded_assets88').valid(art.get('asset88',''),art.get('image',''),art.get('sha256'))
def remember(event,value,body):
 if __import__('os').path.isabs(str(value.get('image',''))) and not value.get('temp85'):return value
 if not body or not value.get('decoded77') or not __import__('programme_image69').eligible(value,event):return value
 if value.get('provisional85'):return value
 result=publish89(event,value,body)
 if result.get('decoded88'):
  try:__import__('external_art89').archive_programme(event,value,body)
  except (OSError,ValueError,TypeError,RuntimeError):pass
 return result
def publish89(event,value,body,*,shared=True):
 """Internal producer: caller already proved source/event and decoded bytes."""
 from programme_requests68 import identity,scope
 from programme_image69 import fingerprint,policy
 try:
  # Selected future/past details get a bounded view session too; current event
  # expires on event end. Never extend a stale live event into its successor.
  now=time.time();until=min(now+86400,float(event['stop'])) if event.get('start',0)<=now<event.get('stop',0) else now+600
  from event_cache88 import asset_key,receipt
  source=value.get('source')
  proof=receipt(value)
  asset_key88=asset_key(key(event,source),__import__('hashlib').sha256(body).hexdigest(),proof)
  asset=__import__('decoded_assets88').put(asset_key88,body,until,receipt88=proof)
  result=dict(value,key=event.get('key') or __import__('programme_events46').key(event['pid'],event['sid'],event),fingerprint=fingerprint(event,source),image=asset['uri'],thumbnail=asset['uri'],sha256=asset['sha256'],until=asset['until'],asset88=asset_key88,decoded88=True,scope69=identity(event),profile69=scope(),policy69=policy(source),storage69='RAM_ONLY',persisted69=False)
  for field in ('display84','display_key84','url_version55','url_verified69','temp85'):result.pop(field,None)
  if shared:window().setProperty(PREFIX+key(event,source),json.dumps(result,separators=(',',':')))
  return result
 except (OSError,ValueError,TypeError):return value
def read(event):
 for source in ('agent_xmltv',None) if __import__('agent_programme100').typed(event) else (None,):
  try:
   raw=window().getProperty(PREFIX+key(event,source));art=json.loads(raw) if raw and len(raw)<8192 else {}
   if art.get('decoded88') and valid(art,event):return art
  except (ValueError,TypeError,KeyError):pass
 return None

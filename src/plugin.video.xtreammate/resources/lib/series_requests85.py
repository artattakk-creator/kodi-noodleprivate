"""Candidate-manager intents on the existing programme service worker."""
import json,time,uuid
from media_sources43 import SourceError
KEY='XCMate.SeriesManager85.Request';RESULT='XCMate.SeriesManager85.Result'
def request(event,thumbnail=None):
 from programme_requests68 import _FIELDS,scope
 import xbmcgui
 value=dict(event={k:event[k] for k in _FIELDS+('genre','year','country','external_ids','description','work_id','_work_ids_verified85','original_title') if k in event},binding=__import__('programme_mapping85').namespace(event),scope=scope(),nonce=uuid.uuid4().hex,at=time.time())
 if thumbnail:value['thumbnail']=[thumbnail.get('source'),thumbnail.get('id')]
 raw=json.dumps(value,separators=(',',':'))
 if len(raw.encode())>16384:return None
 xbmcgui.Window(10000).setProperty(KEY,raw);return value['nonce']
def result(nonce):
 import xbmcgui
 try:
  raw=xbmcgui.Window(10000).getProperty(RESULT);data=json.loads(raw) if raw and len(raw.encode())<=65536 else {}
  return data if data.get('nonce')==nonce else None
 except (TypeError,ValueError):return None
def cancelled(nonce):
 import xbmcgui
 try:return json.loads(xbmcgui.Window(10000).getProperty(KEY) or '{}').get('nonce')!=nonce
 except (TypeError,ValueError):return True
def cancel(nonce):
 import xbmcgui
 if not cancelled(nonce):xbmcgui.Window(10000).clearProperty(KEY)
_seen=''
def drain(cancelled_service=lambda:False):
 global _seen
 __import__('work_requests86').drain(cancelled_service)
 import xbmcgui
 from programme_requests68 import scope
 from programme_mapping85 import reload,refresh_sources,namespace
 reload()
 try:
  from portals import get_active
  for item in get_active()[:4]:refresh_sources(item['id'])
 except (OSError,ValueError,TypeError):pass
 window=xbmcgui.Window(10000)
 try:
  raw=window.getProperty(KEY)
  data=json.loads(raw) if raw and len(raw.encode())<=16384 else {}
  nonce=data.get('nonce');event=data.get('event')
  if not isinstance(event,dict) or not isinstance(nonce,str) or len(nonce)!=32 or nonce==_seen or data.get('scope')!=scope() or not 0<=time.time()-data.get('at',0)<35:return
  _seen=nonce;stop=lambda:cancelled_service() or cancelled(nonce)
  from portals import get_by_id
  from library_index import Reader
  from programme_events46 import load
  portal=get_by_id(str(event.get('pid')))
  if not portal:raise ValueError('PORTAL_MISSING')
  reader=Reader(portal['id'])
  try:channel=reader.get('live',str(event.get('sid')))
  finally:
   close=getattr(reader,'close',None)
   if close:close()
  if not channel:raise ValueError('CHANNEL_MISSING')
  actual=load(portal,channel,event)
  if actual.get('code')!='LOCAL_EVENT' or actual.get('start')!=event.get('start') or actual.get('stop')!=event.get('stop'):raise ValueError('NO_SOURCE_FACTS')
  refresh_sources(portal['id'])
  if namespace(actual)!=data.get('binding'):raise ValueError('SOURCE_CHANGED')
  from programme_candidates85 import search
  thumb=data.get('thumbnail')
  if thumb:
   from programme_candidates85 import read
   cached=read(dict(actual,_manager85=True));rows=[r for r in cached.get('rows',[]) if [r.get('source'),r.get('id')]==thumb];complete=cached.get('complete',False)
  else:rows,complete=search(dict(actual,_manager85=True),stop,include_tvmaze=True)
  from programme_urls55 import probe,OPTIONS,safe
  from artwork_visible import public_dns
  started=time.monotonic()
  for row in rows[:5]:
   if time.monotonic()-started>12:break
   if stop():return
   url=row.get('poster','').replace('/w500/','/w185/')
   if url and safe(url) and public_dns(url):
    try:
     checked=probe(url,cancel=stop)
     if checked.get('decoded77'):row['thumb85']=url+OPTIONS
    except (SourceError,OSError,ValueError,RuntimeError):pass
  if not stop():window.setProperty(RESULT,json.dumps(dict(nonce=nonce,code='THUMB' if thumb else 'READY',rows=rows,complete=complete,binding=namespace(actual)),separators=(',',':')))
 except Exception:
  if isinstance(locals().get('nonce'),str) and not cancelled(nonce):window.setProperty(RESULT,json.dumps(dict(nonce=nonce,code='UNAVAILABLE',rows=[])))

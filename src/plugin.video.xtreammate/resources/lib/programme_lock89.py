"""Canonical-event lock after a verified local texture reaches a native bank.

No GUI file/network/SQL access. Worker verifies bytes. A native control receipt
is still not a physical Android pixel PASS. No remote DNS lease is extended.
"""
import hashlib,json,os,time
PREFIX='XCMate.ProgrammeLock89.'
_checked={}
def key(event):
 from epg_handoff63 import profile_scope
 from programme_display84 import _account
 from programme_mapping85 import epoch
 from programme_policy68 import negative_scope
 from epg_events import title_key,integer
 facts=[profile_scope(),_account(event.get('pid')),str(event.get('pid')),str(event.get('sid')),str(event.get('canonical') or ''),str(event.get('source_key46') or ''),str(event.get('epg_source46') or ''),integer(event.get('start')),integer(event.get('stop')),title_key(event.get('title')),epoch(event),negative_scope({})]
 return hashlib.sha256(json.dumps(facts,sort_keys=True).encode()).hexdigest()
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def slot(tag):return PREFIX+str(int(tag[:8],16)%32)
def load(event):
 tag=key(event)
 try:
  raw=window().getProperty(slot(tag));record=json.loads(raw) if raw and len(raw)<16384 else {}
  return record if record.get('key')==tag else {}
 except (ValueError,TypeError):return {}
def put(record):
 raw=json.dumps(record,separators=(',',':'))
 if len(raw.encode())<=16384:
  window().setProperty(slot(record['key']),raw);window().setProperty(PREFIX+'Active','true')
def propose(event,value,texture):
 from event_art81 import allowed
 from programme_lastgood80 import file_valid
 if value.get('provisional85') or not allowed(value) or not event.get('start') or not event.get('stop'):return
 if current(event,worker=True):return
 file=texture.get('file','');digest=texture.get('sha256','')
 if not os.path.isabs(file) or not __import__('re').fullmatch('[a-f0-9]{64}',digest):return
 art=dict(value,image=file,thumbnail=file,sha256=digest,storage69='KODI_TEXTURE_CACHE',persisted69=False)
 for field in ('url_version55','url_verified69','display84','display_key84','temp85','decoded88','asset88'):art.pop(field,None)
 if not file_valid(art):return
 now=time.time();until=min(now+86400,float(event['stop'])) if event['start']<=now<event['stop'] else now+600
 prior=load(event);grace=prior.get('preferred_until89',time.monotonic()+.75) if prior.get('state')=='VERIFIED_DISPLAYABLE' else time.monotonic()+.75
 put(dict(key=key(event),state='VERIFIED_DISPLAYABLE',art=art,display_uri=value['image'],until=until,preferred_until89=grace,revision=hashlib.sha256(str(event.get('revision')).encode()).hexdigest()))
def current(event,worker=False):
 if window().getProperty(PREFIX+'Active')!='true':return None
 record=load(event)
 if record.get('state')!='LOCKED' or record.get('until',0)<=time.time():return None
 art=record.get('art',{})
 if not __import__('event_art81').allowed(art) or __import__('widget_refs74').revoked(art.get('source_url','')):return None
 if worker and time.monotonic()>=_checked.get(record['key'],0):
  if not __import__('programme_lastgood80').file_valid(art):window().clearProperty(slot(record['key']));return None
  _checked[record['key']]=time.monotonic()+5
  while len(_checked)>64:_checked.pop(next(iter(_checked)))
 from programme_requests68 import identity,scope
 from programme_art46 import fingerprint
 return dict(art,key=event['key'],fingerprint=fingerprint(event),scope69=identity(event),profile69=scope(),until=record['until'],lock89=True)
def acknowledge(event,win):
 import xbmc,xbmcgui
 if window().getProperty(PREFIX+'Active')!='true':return None
 record=load(event)
 if record.get('state')=='VERIFIED_DISPLAYABLE' and record.get('until',0)>time.time():
  bank=win.getProperty('XCMate.Hero63.Active');prefix='XCMate.Hero63.'+bank+'.'
  exact=win.getProperty(prefix+'Image') in (record.get('display_uri'),record.get('art',{}).get('image'))
  native=xbmcgui.getCurrentWindowId()==10000 and xbmc.getInfoLabel('ListItem.Property(XCMate.WidgetKind41)')=='live' and xbmc.getInfoLabel('ListItem.Property(XCMate.MediaId)')==str(event.get('sid'))
  preferred=record['art'].get('source','').startswith('tmdb') or record['art'].get('manual85') or time.monotonic()>=record.get('preferred_until89',0)
  if preferred and exact and native and any(xbmc.getCondVisibility('Control.IsVisible('+str(cid)+')') for cid in (296751,296783)):
   record['state']='LOCKED';record['evidence']='LOCAL_HASH_AND_NATIVE_BANK_CONTROL';put(record)
 return current(event)

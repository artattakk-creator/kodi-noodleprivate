"""Source hysteresis plus exact-edition durable artwork; worker file access only."""
import hashlib,json,time
_upgrade={}

def key(event):
 from epg_handoff63 import profile_scope
 from epg_events import title_key
 values=[profile_scope()]+[event.get(k) for k in ('pid','sid','canonical','source_key46','epg_source46','start','stop','year','season','episode','subtitle')]+[title_key(event.get('title',''))]
 return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()

def rank(value):
 source=value.get('source','')
 if source.startswith('tmdb_'):return 0 if value.get('role81')!='poster' else 3
 return {'xmltv_event':1,'provider_event':2,'tvmaze_episode':2,'tvmaze_series':3}.get(source,4)

def allowed(value):
 from utils import setting_bool
 source=value.get('source','')
 if source.startswith('tmdb_'):return setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False) and not setting_bool('programme_tmdb_optout77',False)
 if source.startswith('tvmaze'):return setting_bool('programme_tvmaze67',False) and not setting_bool('programme_tvmaze_optout77',False)
 if source in ('xcmate_catalog','kodi_library'):return setting_bool('programme_catalog57',True)
 return source in ('xmltv_event','provider_event')

def prior(event):
 from render_cache81 import read
 record=read(key(event))
 if not record:return None
 try:
  value=record.get('art81',{})
  if not value or not allowed(value):return None
  from programme_requests68 import identity,scope
  from programme_art46 import fingerprint
  return dict(value,image=record['file'],thumbnail=record['file'],key=event['key'],fingerprint=fingerprint(event),scope69=identity(event),profile69=scope(),until=min(record['at']+30*86400,max(time.time()+300,event['stop']+3600)))
 except (OSError,ValueError,KeyError,TypeError):return None

def commit(event,value,body=None):
 from render_cache81 import store
 from profile_transaction import writing
 if not __import__('artwork_display84').metadata_allowed() or __import__('home_schedule75').applicable():
  old=prior(event)
  return old if old and rank(old)<=rank(value) else value
 try:
  with writing(timeout=.1):
   old=prior(event)
   if old and rank(old)<=rank(value):return old
   if not body:return value
   def enrich81(record):
    saved=dict(value,image=record['file'],thumbnail=record['file'],sha256=record['sha256'])
    for field in ('url_version55','url_verified69','source_url'):saved.pop(field,None)
    return dict(art81=saved)
   record=store(key(event),body,enrich=enrich81)
   from art_trace81 import note
   note(event,'SOURCE_COMMITTED',str(value.get('source','UNKNOWN')).upper(),width=record['width'],height=record['height'])
   return record['art81']
 except (OSError,ValueError,TypeError,TimeoutError):return prior(event) or value

def upgrade(event,previous):
 if not previous or rank(previous)==0:return False
 from utils import setting_bool
 if not setting_bool('programme_tmdb46',False) or not setting_bool('tmdb_research43',False) or setting_bool('programme_tmdb_optout77',False):return False
 tag=key(event);now=time.monotonic()
 if now<_upgrade.get(tag,0):return False
 _upgrade[tag]=now+300
 while len(_upgrade)>256:_upgrade.pop(next(iter(_upgrade)))
 return True


def select(value,previous):
 if previous and value and rank(previous)<rank(value):return previous
 if previous and value and rank(previous)==rank(value) and previous.get('source')==value.get('source'):return previous
 return value

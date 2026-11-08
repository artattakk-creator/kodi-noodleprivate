"""Optional exact TMDB Hero supplement; provider rail posters always win."""
import hashlib,json,time
_due={}

def identity(portal,kind,row):
 from widget_assets69 import identity as key
 edition=json.dumps([row.get(k) for k in ('name','year','tmdb_id')],sort_keys=True)
 return key(portal,kind,row,'tmdb_hero81',edition)

def reference(portal,kind,row):
 from utils import setting_bool
 if not setting_bool('programme_tmdb46',False) or not setting_bool('tmdb_research43',False) or setting_bool('programme_tmdb_optout77',False):return ''
 from render_cache81 import read
 value=read(identity(portal,kind,row))
 return value['file'] if value else ''

def prepare(portal,kind,rows,cancel=lambda:False):
 if kind not in ('vod','series') or not rows:return
 from home_schedule75 import focused_rows
 selected=focused_rows(portal,kind,rows) or rows[:1]
 row=selected[0];key=identity(portal,kind,row)
 if reference(portal,kind,row) or time.monotonic()<_due.get(key,0):return
 _due[key]=time.monotonic()+300
 while len(_due)>128:_due.pop(next(iter(_due)))
 from programme_assets47 import sources
 if sources(row,provider_only=True).get('fanart'):return
 from art_trace81 import own,note
 from programme_match46 import candidate
 from programme_transport77 import verified
 from render_cache81 import store
 event=dict(pid=str(portal['id']),sid=str(row['sid']),key=key,title=row['name'],year=row.get('year'),genre='Series' if kind=='series' else 'Film')
 try:
  found=own(event,lambda:candidate(event,cancel))
  if not found or found.get('role81')=='poster' or cancel():return
  url81=found['url'].replace('https://image.tmdb.org/t/p/w500/','https://image.tmdb.org/t/p/w1280/',1)
  response=verified(url81,cancel=cancel,keep_data81=True)
  if cancel():return
  store(key,response['_body81']);note(event,'SOURCE_COMMITTED','TMDB_BACKDROP')
 except Exception as error:
  # Optional enrichment may never terminate the existing provider worker.
  note(event,'SKIPPED_REASON',getattr(error,'code','LOOKUP_FAILED'))

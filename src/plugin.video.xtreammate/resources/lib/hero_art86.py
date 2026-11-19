"""Typed Home Hero admission. Feed thumbnails are never main Hero pictures."""
import math
def classify(value):
 if not isinstance(value,dict):return None
 source=value.get('source','');role=value.get('role81','')
 width=value.get('image_width77',value.get('width',0));height=value.get('image_height77',value.get('height',0))
 if type(width) not in (int,float) or type(height) not in (int,float) or not math.isfinite(width+height) or height<=0:return None
 if value.get('provisional85'):return None
 manual=value.get('manual85') or value.get('match')=='MANUAL_CONFIRMED'
 if source in ('tmdb_movie','tmdb_series','tvmaze_series','user_local86','agent_tmdb','agent_tvmaze','agent_xmltv') and role=='poster':
  if width>=500 and height>=700 and .45<=width/height<=.85:return ('official_poster',-1 if manual else 2)
  return None
 if role=='thumb' or width<960 or height<540 or not 1.3<=width/height<=2.5:return None
 if source in ('tmdb_movie','tmdb_series','agent_tmdb') and role=='backdrop':return ('hero_backdrop',-1 if manual else 0)
 if source in ('agent_tmdb','agent_tvmaze','agent_xmltv') and role in ('backdrop','episode_still'):
  return ('hero_backdrop',1)
 if source in ('tmdb_episode','tvmaze_episode','xmltv_event','provider_event','user_local86') and role!='poster':
  return ('hero_backdrop',-1 if manual else 1)
 return None
def poster(candidate):
 if candidate.get('manual85') or candidate.get('match')=='MANUAL_CONFIRMED':return None
 url=candidate.get('official_poster86')
 if not url or candidate.get('source') not in ('tmdb_movie','tmdb_series'):return None
 return dict(candidate,url=url,role81='poster')
def ordered(primary,feeds):
 """TMDB wide -> large scene -> independently identified official poster."""
 wide=[v for v in primary if v.get('source') in ('tmdb_movie','tmdb_series') and v.get('role81')=='backdrop']
 scenes=[v for v in primary if v not in wide and v.get('role81')!='poster']+feeds
 posters=[v for v in primary if v.get('role81')=='poster']+[p for v in wide if (p:=poster(v))]
 return [v for work in wide for v in __import__('cinematic_images96').alternatives(work)]+scenes+posters


def expand(primary,event,cancel=lambda:False):
 """Explicit Home chooser: enrich proved works after visible-worker admission.

 Generic identity searches never start optional cinematic lookups. A proved
 episode ID still needs an independently verified parent work for the Hero.
 """
 result=[]
 for value in primary:
  if value.get('manual85') or value.get('match')=='MANUAL_CONFIRMED':
   result.append(value);continue
  if value.get('source')=='tmdb_episode' and type(value.get('remote_id')) is int:
   try:
    row=__import__('programme_candidates85').details(event,value['remote_id'],cancel,manual=False)
    if row and row.get('work_match85'):
     work=__import__('programme_candidates85').artifact(row,'EXACT_TV_TITLE_YEAR66' if event.get('year') else 'EXACT_UNIQUE_TV_TITLE66')
     work['image_scope57']='series_fallback'
     result.append(__import__('cinematic_images96').enrich(work,event,cancel))
   except __import__('media_sources43').SourceError:pass
  if value.get('source') in ('tmdb_movie','tmdb_series'):
   value=__import__('cinematic_images96').enrich(value,event,cancel)
  result.append(value)
 return result

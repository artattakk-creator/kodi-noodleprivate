"""Movie-part normalization preserves franchise and sequel number exactly."""
import re

def query(value):
 value=str(value or '')[:512]
 value=re.sub(r'\s*\(([1-9][0-9]?)\)\s*$',r' Teil \1',value)
 return re.sub(r'\bPart\s+([1-9][0-9]?)\s*$',r'Teil \1',value,flags=re.I)

def key(value):
 from epg_events import title_key
 return title_key(query(value))

def unclassified(event,cancel):
 """Unknown genre: require complete TV exclusion before exact movie proof."""
 genre=str(event.get('genre','')).casefold()
 if event.get('season') is not None or event.get('episode') is not None:return None
 if any(v in genre for v in ('serie','series','sitcom','news','nachricht','sport','talk')):return None
 try:duration=float(event['stop'])-float(event['start'])
 except (KeyError,TypeError,ValueError):return None
 if not 3600<=duration<=5*3600:return None
 from media_sources43 import TMDB,tmdb_token
 from tmdb_connection60 import request
 from urllib.parse import urlencode
 title=key(event.get('title'))
 if len(title)<12:return None
 result=request(TMDB+'/search/tv?'+urlencode(dict(query=query(event['title']),language='de-DE',include_adult='false')),token=tmdb_token(),cancel=cancel)
 rows=result.get('results')
 if not isinstance(rows,list) or type(result.get('total_pages')) is not int or result['total_pages'] not in (0,1) or type(result.get('total_results')) is not int or result.get('total_results')!=len(rows) or len(rows)>20 or (result['total_pages']==0 and rows):return None
 if any(title in (key(r.get('name')),key(r.get('original_name'))) for r in rows if isinstance(r,dict)):return None
 if event.get('year'):
  from tmdb_epg60 import candidate
  return candidate(dict(event,genre='Movie'),cancel)
 from programme_match46 import unique_movie56
 return unique_movie56(event,cancel)

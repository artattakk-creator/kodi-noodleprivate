"""Optional cinematic TMDB art after identity proof, in the existing image worker.

One bounded images request per confirmed work, no searching, threads, feed reads,
Helper dependency or independent scheduler. The visible-five queue owns admission.
API metadata ranks candidates; the existing image decoder still proves pixels.
"""
import hashlib
import math
import time
from urllib.parse import urlencode

MAX_BACKDROPS=5
MAX_ROWS=500
_cache={}
_PROOFS=('EXACT_TITLE_YEAR','EXACT_UNIQUE_FILM_TITLE','EXACT_TV_TITLE_YEAR66','EXACT_UNIQUE_TV_TITLE66','MANUAL_CONFIRMED')


def rank(data,ident):
 """Return at most five neutral/German, safe, >=720p wide backdrops."""
 from media_sources43 import _tmdb_image
 if not isinstance(data,dict) or type(data.get('id')) is not int or data['id']!=ident:return []
 rows=data.get('backdrops')
 if not isinstance(rows,list) or len(rows)>MAX_ROWS:return []
 selected={}
 for row in rows:
  if not isinstance(row,dict) or row.get('iso_639_1') not in (None,'','de'):continue
  width,height=row.get('width'),row.get('height')
  votes,rating=row.get('vote_count',0),row.get('vote_average',0)
  if type(width) is not int or type(height) is not int or not 1280<=width<=16384 or not 720<=height<=16384 or not 1.5<=width/height<=2.0:continue
  if type(votes) is not int or not 0<=votes<=10000000 or type(rating) not in (int,float) or not math.isfinite(rating) or not 0<=rating<=10:continue
  url=_tmdb_image(row.get('file_path'))
  if not url:continue
  url=url.replace('/t/p/w500/','/t/p/w1280/',1)
  # Aspect matters most; capped resolution and a Bayesian rating avoid a
  # single 10/10 vote overwhelming well-supported large work artwork.
  score=(1-abs(width/height-16/9))*4+min(width*height/(1920*1080),2)+((votes*rating+5*6)/(votes+5))/5+min(math.log1p(votes),8)/8
  if row.get('iso_639_1') in (None,''):score+=.15
  value=dict(url=url,width=width,height=height,vote_count88=votes,vote_average88=rating,language96=row.get('iso_639_1') or '',score96=round(score,6),role81='backdrop')
  if url not in selected or selected[url]['score96']<value['score96']:selected[url]=value
 return sorted(selected.values(),key=lambda row:(-row['score96'],row['url']))[:MAX_BACKDROPS]


def enrich(value,event,cancel=lambda:False):
 """Keep the verified existing candidate on every optional images failure.

 The caller must already have independently proved a unique work or obtained
 an explicit manual confirmation; search/detail suggestions never call here.
 No event/title/year/ID proof is inferred from an images response.
 """
 if not isinstance(value,dict) or value.get('source') not in ('tmdb_movie','tmdb_series') or value.get('match') not in _PROOFS or value.get('provisional85') or type(value.get('remote_id')) is not int or value['remote_id']<=0 or value.get('cinematic_backdrops96') or cancel():return value
 from programme_candidates85 import enabled
 if not enabled():return value
 from media_sources43 import TMDB,tmdb_token
 from tmdb_connection60 import request
 from programme_requests68 import scope
 kind='movie' if value['source']=='tmdb_movie' else 'tv'
 cache_key=None
 try:
  token=tmdb_token()
  cache_key=(scope(),hashlib.sha256(token.encode()).hexdigest(),kind,value['remote_id'])
  now=time.monotonic();cached=_cache.get(cache_key)
  if cached and 0<=now-cached[0]<cached[1]:ranked=cached[2]
  else:
   data=request(TMDB+'/'+kind+'/'+str(value['remote_id'])+'/images?'+urlencode(dict(include_image_language='null,de')),token=token,cancel=cancel)
   if cancel():return value
   ranked=rank(data,value['remote_id'])
   _cache[cache_key]=(now,600 if ranked else 60,ranked)
   while len(_cache)>64:_cache.pop(next(iter(_cache)))
 except Exception:
  # This enrichment is optional, including malformed endpoint responses.
  # Short negative backoff also prevents nested match adapters retrying it.
  if cache_key is not None:
   _cache[cache_key]=(time.monotonic(),60,[])
   while len(_cache)>64:_cache.pop(next(iter(_cache)))
  return value
 if not ranked:return value
 best=ranked[0]
 return dict(value,url=best['url'],role81='backdrop',vote_average88=best['vote_average88'],vote_count88=best['vote_count88'],cinematic_backdrops96=ranked,alternate_urls57=[r['url'] for r in ranked[1:]])


def alternatives(value):
 """Each ranked URL retains its work proof, source and typed backdrop role."""
 rows=value.get('cinematic_backdrops96')
 if not isinstance(rows,list) or not rows:return [value]
 return [dict(value,url=row['url'],role81='backdrop',vote_average88=row['vote_average88'],vote_count88=row['vote_count88']) for row in rows[:MAX_BACKDROPS]]

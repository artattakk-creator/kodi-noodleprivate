"""Conservative TV artwork without requiring invented season/episode numbers."""
import re
from urllib.parse import urlencode
def candidate(event,cancel=lambda:False):
 from utils import setting_bool
 from media_sources43 import TMDB,_tmdb_image,tmdb_token,SourceError
 from tmdb_connection60 import request,ATTRIBUTION
 from epg_events import title_key
 if not setting_bool('programme_tmdb46',False):return None
 genre=str(event.get('genre','')).casefold()
 if any(v in genre for v in ('nachricht','news','sport','fußball','talk')):return None
 if not any(v in genre for v in ('serie','series','sitcom','episode')):return None
 label=str(event.get('title',''))[:200];year=str(event.get('year') or '')
 suffix=re.fullmatch(r'(.+?)\s+\(((?:19|20)[0-9]{2})\)',label)
 if suffix:
  if year and year!=suffix[2]:raise SourceError('NO_MATCH')
  label,year=suffix[1],suffix[2]
 if year and (not year.isdigit() or not 1880<=int(year)<=2100):raise SourceError('NO_MATCH')
 title=title_key(label)
 if not title:return None
 token=tmdb_token();data=request(TMDB+'/search/tv?'+urlencode(dict(query=label,language='de-DE',include_adult='false')),token=token,cancel=cancel)
 rows=data.get('results',[])
 if not isinstance(rows,list) or data.get('total_pages')!=1 or type(data.get('total_results')) is not int or data['total_results']!=len(rows) or len(rows)>20:raise SourceError('NO_MATCH_AMBIGUOUS')
 matches={r['id']:r for r in rows if isinstance(r,dict) and type(r.get('id')) is int and r['id']>0 and not r.get('adult') and title in (title_key(r.get('name','')),title_key(r.get('original_name',''))) and (not year or str(r.get('first_air_date',''))[:4]==year)}
 if not matches:raise SourceError('NO_MATCH')
 if len(matches)!=1:raise SourceError('NO_MATCH_AMBIGUOUS')
 remote,row=next(iter(matches.items()))
 details=request(TMDB+'/tv/'+str(remote)+'?language=de-DE',token=token,cancel=cancel)
 if details.get('id')!=remote or details.get('adult') or title not in (title_key(details.get('name','')),title_key(details.get('original_name',''))):raise SourceError('NO_MATCH')
 actual=str(details.get('first_air_date',''))[:4]
 if not actual.isdigit() or actual!=str(row.get('first_air_date',''))[:4] or year and year!=actual:raise SourceError('NO_MATCH')
 from programme_flow48 import trace
 trace('MATCH',event,'READY')
 url=_tmdb_image(details.get('backdrop_path'))
 if not url:raise SourceError('NO_ARTWORK')
 return dict(url=url,source='tmdb_series',match='EXACT_TV_TITLE_YEAR66' if year else 'EXACT_UNIQUE_TV_TITLE66',remote_id=remote,matched_year56=int(actual),image_scope57='series_fallback',attribution='TMDB · https://www.themoviedb.org/tv/'+str(remote)+' · Serienbild (kein Episodenbild) · '+ATTRIBUTION)

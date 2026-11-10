"""Exact TV work proof, independent of optional genre/episode classification."""
import re
from urllib.parse import urlencode

def reject84(event,code):
 __import__('art_trace81').note(event,'MATCH_REJECTED',code)

def complete84(data,empty=False):
 rows=data.get('results');pages=data.get('total_pages')
 return isinstance(rows,list) and type(pages) is int and pages in ((0,1) if empty else (1,)) and type(data.get('total_results')) is int and data['total_results']==len(rows) and len(rows)<=20 and not(pages==0 and rows)

def candidate84(event,cancel=lambda:False):
 from utils import setting_bool
 from media_sources43 import TMDB,_tmdb_image,tmdb_token,SourceError
 from tmdb_connection60 import request,ATTRIBUTION
 from epg_events import title_key
 if not setting_bool('programme_tmdb46',False) or setting_bool('programme_tmdb_optout77',False):
  reject84(event,'SERIES_SOURCE_DISABLED');return None
 genre=str(event.get('genre','')).casefold()
 if any(v in genre for v in ('nachricht','news','sport','fußball','talk','spielfilm','movie','film')):return None
 classified=any(v in genre for v in ('serie','series','sitcom','episode'))
 if not classified:reject84(event,'SERIES_GENRE_UNKNOWN')
 label=str(event.get('title',''))[:200];year=str(event.get('year') or '')
 suffix=re.fullmatch(r'(.+?)\s+\(((?:19|20)[0-9]{2})\)',label)
 if suffix:
  if year and year!=suffix[2]:reject84(event,'SERIES_YEAR_CONFLICT');raise SourceError('NO_MATCH')
  label,year=suffix[1],suffix[2]
 if year and (not year.isdigit() or not 1880<=int(year)<=2100):reject84(event,'SERIES_YEAR_CONFLICT');raise SourceError('NO_MATCH')
 original=label;alias={'yuna stitch':'Stitch!'}.get(title_key(label))
 if alias:label=alias
 title=title_key(label)
 if not title:return None
 if len(title)<12 and not year:reject84(event,'SERIES_TITLE_SHORT_NEEDS_PROOF')
 token=tmdb_token();query=dict(query=label,language='de-DE',include_adult='false')
 data=request(TMDB+'/search/tv?'+urlencode(query),token=token,cancel=cancel)
 if not complete84(data,empty=True):reject84(event,'SERIES_MULTIPLE_MATCHES');raise SourceError('NO_MATCH_AMBIGUOUS')
 rows=data['results'];valid={r['id']:r for r in rows if isinstance(r,dict) and type(r.get('id')) is int and r['id']>0 and not r.get('adult')}
 exact={i:r for i,r in valid.items() if title in (title_key(r.get('name','')),title_key(r.get('original_name','')))}
 matches={i:r for i,r in exact.items() if not year or str(r.get('first_air_date',''))[:4]==year}
 if len(matches)>1:reject84(event,'SERIES_MULTIPLE_MATCHES');raise SourceError('NO_MATCH_AMBIGUOUS')
 discover_alias=False
 if not matches:
  if exact and year:reject84(event,'SERIES_YEAR_CONFLICT');raise SourceError('NO_MATCH')
  # One complete result may be an official translated/alternative title.
  # The search rank itself is never proof; an independent AKA response is.
  if len(valid)!=1:return None
  remote,row=next(iter(valid.items()));discover_alias=True
 else:remote,row=next(iter(matches.items()))
 details=request(TMDB+'/tv/'+str(remote)+'?language=de-DE',token=token,cancel=cancel)
 if details.get('id')!=remote or details.get('adult') or not any(title_key(n) and title_key(n) in (title_key(details.get('name','')),title_key(details.get('original_name',''))) for n in (row.get('name',''),row.get('original_name',''))):raise SourceError('NO_MATCH')
 if alias or discover_alias:
  alternatives=request(TMDB+'/tv/'+str(remote)+'/alternative_titles',token=token,cancel=cancel)
  if alternatives.get('id')!=remote or not any(title_key(r.get('title',''))==title_key(original) for r in alternatives.get('results',[]) if isinstance(r,dict)):
   reject84(event,'SERIES_ALIAS_UNVERIFIED')
   if not classified:return None
   raise SourceError('NO_MATCH')
 actual=str(details.get('first_air_date',''))[:4]
 if not actual.isdigit() or not 1880<=int(actual)<=2100 or actual!=str(row.get('first_air_date',''))[:4] or year and year!=actual:reject84(event,'SERIES_YEAR_CONFLICT');raise SourceError('NO_MATCH')
 if not classified:
  # Additional cross-media exclusion for an unknown/short EPG title. A
  # same-name film means there is insufficient evidence to select TV.
  films=request(TMDB+'/search/movie?'+urlencode(dict(query=original,language='de-DE',include_adult='false')),token=token,cancel=cancel)
  if not complete84(films,empty=True):reject84(event,'SERIES_MULTIPLE_MATCHES');raise SourceError('NO_MATCH_AMBIGUOUS')
  names={title_key(original),title_key(details.get('name','')),title_key(details.get('original_name',''))}
  if any(names.intersection((title_key(r.get('title','')),title_key(r.get('original_title','')))) and (not year or str(r.get('release_date',''))[:4]==year) for r in films['results'] if isinstance(r,dict) and not r.get('adult')):
   reject84(event,'SERIES_MULTIPLE_MATCHES');raise SourceError('NO_MATCH_AMBIGUOUS')
 from programme_flow48 import trace
 trace('MATCH',event,'READY')
 url=_tmdb_image(details.get('backdrop_path') or details.get('poster_path'))
 if not url:reject84(event,'SERIES_ART_MISSING');raise SourceError('NO_ARTWORK')
 return dict(url=url,source='tmdb_series',vote_average88=details.get('vote_average'),vote_count88=details.get('vote_count'),role81='backdrop' if details.get('backdrop_path') else 'poster',match='EXACT_TV_TITLE_YEAR66' if year else 'EXACT_UNIQUE_TV_TITLE66',remote_id=remote,matched_year56=int(actual),image_scope57='series_fallback',attribution='TMDB · https://www.themoviedb.org/tv/'+str(remote)+' · Serienbild (kein Episodenbild) · '+ATTRIBUTION)


def candidate(event,cancel=lambda:False):
 return __import__("programme_candidates85").candidate(event,cancel)

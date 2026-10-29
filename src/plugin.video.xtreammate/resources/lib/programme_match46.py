"""Conservative opt-in TMDb artwork only, never replaces authoritative EPG text."""
def candidate(event,cancel=lambda:False):
 from utils import setting_bool
 if not setting_bool('programme_tmdb46',False):return None
 from media_sources43 import tmdb,tmdb_token,get,TMDB,_tmdb_image,SourceError
 from epg_events import title_key
 # News/talk are never treated as movies by guessing their title.
 series=bool(event.get('season') and event.get('episode'))
 movie=any(v in str(event.get('genre','')).casefold() for v in ('spielfilm','film','movie'))
 if not (series or movie):return None
 if not series and not event.get('year'):
  return unique_movie56(event,cancel)
 rows=tmdb(event['title'],'series' if series else 'vod',cancel=cancel)
 matches=[r for r in rows if title_key(r.get('title'))==title_key(event['title']) and (not event.get('year') or str(r.get('year'))==str(event['year']))]
 ids={r.get('remote_id') for r in matches}
 if len(ids)!=1:return None
 chosen=next((r for r in matches if r.get('role')=='fanart'),matches[0])
 if series:
  season,episode=event['season'],event['episode'];remote=chosen['remote_id']
  data=get(TMDB+'/tv/'+str(remote)+'/season/'+str(season)+'/episode/'+str(episode)+'?language=de-DE',api=True,token=tmdb_token(),cancel=cancel)
  if data.get('season_number')!=season or data.get('episode_number')!=episode:return None
  if event.get('subtitle') and title_key(data.get('name'))!=title_key(event['subtitle']):return None
  url=_tmdb_image(data.get('still_path'))
  return dict(url=url,source='tmdb_episode',match='EXACT_SEASON_EPISODE',attribution=chosen['attribution']) if url else None
 if not chosen.get('url'):return None
 return dict(url=chosen['url'],source='tmdb_movie',match='EXACT_TITLE_YEAR',attribution=chosen['attribution'])


def diagnose(event):
 """Fixed reasons, no network, text disclosure or EPG modification."""
 from utils import setting_bool,setting
 if not setting_bool('programme_tmdb46',False) or not setting_bool('tmdb_research43',False):return 'TMDB_DISABLED'
 if not setting('tmdb_read_token43','').strip():return 'TMDB_TOKEN_MISSING'
 series=bool(event.get('season') and event.get('episode'))
 if not series and not any(v in str(event.get('genre','')).casefold() for v in ('spielfilm','film','movie')):return 'NOT_CLASSIFIED_MOVIE'
 if not series and not event.get('year'):return 'NO_YEAR'
 return 'NO_MATCH'


def unique_movie56(event,cancel=lambda:False):
 """Yearless explicit movie: complete unique search AND independent details.

 No partial first-page guessing, remakes, generic title aliases or sequel
 truncation. A supplied conflicting production year never enters this path.
 The inferred year is an artwork proof, never a replacement of local EPG text.
 """
 from utils import setting_bool,setting
 if not setting_bool('tmdb_research43',False) or not setting('tmdb_read_token43','').strip():return None
 from media_sources43 import get,TMDB,tmdb_token,_tmdb_image,SourceError
 from epg_events import title_key
 from urllib.parse import urlencode
 title=title_key(event.get('title',''))
 if not title or len(title)<8:return None
 token=tmdb_token()
 data=get(TMDB+'/search/movie?'+urlencode(dict(query=event['title'],language='de-DE',include_adult='false')),api=True,token=token,cancel=cancel)
 rows=data.get('results',[])
 if (not isinstance(rows,list) or data.get('total_pages')!=1 or
     not isinstance(data.get('total_results'),int) or data['total_results']!=len(rows) or len(rows)>20):return None
 matches={r['id']:r for r in rows if isinstance(r,dict) and isinstance(r.get('id'),int) and
          not r.get('adult') and title_key(r.get('title',''))==title}
 if len(matches)!=1:return None
 remote,row=next(iter(matches.items()))
 details=get(TMDB+'/movie/'+str(remote)+'?language=de-DE',api=True,token=token,cancel=cancel)
 if details.get('id')!=remote or details.get('adult') or title_key(details.get('title',''))!=title:return None
 year=str(details.get('release_date',''))[:4]
 if not year.isdigit() or not 1880<=int(year)<=2100 or str(row.get('release_date',''))[:4]!=year:return None
 url=_tmdb_image(details.get('backdrop_path'))
 if not url:raise SourceError('NO_VALID_URL')
 return dict(url=url,source='tmdb_movie',match='EXACT_UNIQUE_FILM_TITLE',matched_year56=int(year),
             remote_id=remote,attribution='TMDb · https://www.themoviedb.org/movie/'+str(remote)+' · nicht von TMDb zertifiziert; Bildnutzungsbedingungen beachten')

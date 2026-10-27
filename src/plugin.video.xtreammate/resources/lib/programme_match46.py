"""Conservative opt-in TMDb artwork only, never replaces authoritative EPG text."""
def candidate(event,cancel=lambda:False):
 from utils import setting_bool
 if not setting_bool('programme_tmdb46',False):return None
 from media_sources43 import tmdb,tmdb_token,get,TMDB,_tmdb_image,SourceError
 from epg_events import title_key
 # News/talk are never treated as movies by guessing their title.
 series=bool(event.get('season') and event.get('episode'))
 movie=any(v in str(event.get('genre','')).casefold() for v in ('spielfilm','film','movie'))
 if not (series or movie) or (not series and not event.get('year')):return None
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

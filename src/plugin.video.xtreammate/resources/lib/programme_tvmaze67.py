"""Optional TVmaze fallback; exact series identity, never guessed episodes."""
import re
from urllib.parse import urlencode,urlsplit
def candidate(event,cancel=lambda:False):
 from utils import setting_bool
 if not setting_bool('programme_tvmaze67',False) or setting_bool('programme_tvmaze_optout77',False):return None
 genre=str(event.get('genre','')).casefold()
 classified=any(v in genre for v in ('serie','series','sitcom','episode')) or type(event.get('season')) is int and type(event.get('episode')) is int or __import__('programme_series84').known(event)
 if any(v in genre for v in ('news','nachricht','sport','talk')) or not classified:return None
 from media_sources43 import get,SourceError
 from epg_events import title_key
 label=str(event.get('title',''))[:200];year=str(event.get('year') or '')
 if year and (not year.isdigit() or not 1880<=int(year)<=2100):raise SourceError('NO_MATCH')
 rows=get('https://api.tvmaze.com/search/shows?'+urlencode(dict(q=label)),api=True,cancel=cancel,json_list67=True)
 if not isinstance(rows,list) or len(rows)>=10:raise SourceError('NO_MATCH_AMBIGUOUS')
 values={}
 for result in rows:
  row=result.get('show',{}) if isinstance(result,dict) else {}
  if type(row.get('id')) is int and row['id']>0 and title_key(row.get('name',''))==title_key(label) and (not year or str(row.get('premiered',''))[:4]==year):values[row['id']]=row
 if len(values)!=1:raise SourceError('NO_MATCH_AMBIGUOUS' if values else 'NO_MATCH')
 identity,row=next(iter(values.items()))
 details=get('https://api.tvmaze.com/shows/'+str(identity),api=True,cancel=cancel)
 actual=str(details.get('premiered',''))[:4]
 if details.get('id')!=identity or title_key(details.get('name',''))!=title_key(label) or not actual.isdigit() or actual!=str(row.get('premiered',''))[:4] or year and year!=actual:raise SourceError('NO_MATCH')
 image=details.get('image') or {};scope='series_fallback'
 season,episode=event.get('season'),event.get('episode')
 if type(season) is int and type(episode) is int and 0<=season<=100 and 1<=episode<=2000:
  ep=get('https://api.tvmaze.com/shows/'+str(identity)+'/episodebynumber?'+urlencode(dict(season=season,number=episode)),api=True,cancel=cancel)
  if ep.get('season')!=season or ep.get('number')!=episode or event.get('subtitle') and title_key(ep.get('name',''))!=title_key(event['subtitle']):raise SourceError('NO_MATCH')
  if ep.get('image'):image=ep['image'];scope='episode'
 url=image.get('original','') if isinstance(image,dict) else ''
 if not re.fullmatch(r'https://static\.tvmaze\.com/uploads/images/(?:original_untouched|medium_portrait)/[0-9]+/[0-9]+\.(?:jpg|png)',url):raise SourceError('NO_ARTWORK')
 return dict(url=url,source='tvmaze_series' if scope=='series_fallback' else 'tvmaze_episode',match='EXACT_TVMAZE_ID67',image_scope57=scope,remote_id=identity,matched_year56=int(actual),attribution='TVmaze · https://www.tvmaze.com/shows/'+str(identity)+' · Daten CC BY-SA; Bildrechte beim Rechteinhaber'+(' · Serienbild (kein Episodenbild)' if scope=='series_fallback' else ''))

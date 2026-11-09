"""Independently verified TVmaze work alternatives; no implicit opt-in."""
import re
from urllib.parse import urlencode
from html import unescape

def details(event,ident,cancel=lambda:False,manual=False,row=None):
 from media_sources43 import get,SourceError
 from programme_mapping85 import name
 data=get('https://api.tvmaze.com/shows/'+str(ident),api=True,cancel=cancel)
 if data.get('id')!=ident:raise SourceError('NO_MATCH')
 title=str(data.get('name') or '');year=str(data.get('premiered',''))[:4]
 if not title or not year.isdigit() or not 1880<=int(year)<=2100:raise SourceError('NO_MATCH')
 if row and (name(row.get('name'))!=name(title) or str(row.get('premiered',''))[:4]!=year):raise SourceError('NO_MATCH')
 if not manual and name(event.get('title'))!=name(title):
  alternatives=get('https://api.tvmaze.com/shows/'+str(ident)+'/akas',api=True,cancel=cancel,json_list67=True)
  if not isinstance(alternatives,list) or len(alternatives)>64 or not any(name(r.get('name'))==name(event.get('title')) for r in alternatives if isinstance(r,dict)):raise SourceError('NO_MATCH')
 external=event.get('external_ids') or {};raw_external=data.get('externals') or {};actual={'imdb_id':raw_external.get('imdb'),'tvdb_id':raw_external.get('thetvdb'),'tvrage_id':raw_external.get('tvrage')}
 if not manual and any(v and (k not in actual or str(actual[k])!=str(v)) for k,v in external.items()):raise SourceError('NO_MATCH')
 image=data.get('image') or {};url=image.get('original','')
 if not re.fullmatch(r'https://static\.tvmaze\.com/uploads/images/(?:original_untouched|medium_portrait)/[0-9]+/[0-9]+\.(?:jpg|png)',url):raise SourceError('NO_ARTWORK')
 country=((data.get('network') or data.get('webChannel') or {}).get('country') or {}).get('code')
 return dict(id=ident,source='tvmaze',title=title[:200],original=title[:200],year=int(year),country=[country] if isinstance(country,str) and len(country)==2 else [],overview=unescape(re.sub('<[^>]*>','',str(data.get('summary') or '')))[:1000],poster=url,url=url,role='poster',verified85=True)
def search(event,cancel=lambda:False,strict=False):
 from programme_candidates85 import enabled
 from media_sources43 import get,SourceError
 from programme_mapping85 import name
 if not enabled('tvmaze'):return [],True
 genre=str(event.get('genre') or '').casefold()
 if not event.get('_manager85') and any(v in genre for v in ('film','movie','news','nachricht','sport','talk')):return [],True
 rows=get('https://api.tvmaze.com/search/shows?'+urlencode(dict(q=str(event.get('title') or '')[:200])),api=True,cancel=cancel,json_list67=True)
 if not isinstance(rows,list) or len(rows)>20:raise SourceError('NO_MATCH_AMBIGUOUS')
 raw=[r['show'] for r in rows if isinstance(r,dict) and isinstance(r.get('show'),dict) and type(r['show'].get('id')) is int and r['show']['id']>0]
 exact=[r for r in raw if name(r.get('name'))==name(event.get('title'))];selected=exact or raw[:4];result=[]
 if event.get('year') and not event.get('_manager85'):selected=[r for r in selected if str(r.get('premiered',''))[:4]==str(event['year'])]
 if strict and len(selected)>1 and not event.get('country') and not event.get('external_ids'):raise SourceError('NO_MATCH_AMBIGUOUS')
 for row in selected[:8]:
  if cancel():break
  if not event.get('_manager85') and event.get('year') and str(row.get('premiered',''))[:4]!=str(event['year']):continue
  try:value=details(event,row['id'],cancel,manual=bool(event.get('_manager85')),row=row)
  except SourceError:
   if strict and len(selected)==1:raise
   continue
  result.append(value)
 return result,len(selected)<=8 and not cancel()

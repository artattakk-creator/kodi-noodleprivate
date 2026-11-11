"""One bounded preview page; independent work verification only on selection.

Preview URLs are built from official image formats and DNS-approved through the
existing URL policy. They are never evidence of decoded pixels or a saved match.
"""
import re,time
from html import unescape
from urllib.parse import urlencode
from media_sources43 import SourceError

def search(query,kind,source,page,cancel):
 from media_sources43 import TMDB,tmdb_token,_tmdb_image,get
 from programme_urls55 import safe,OPTIONS
 if cancel():raise SourceError('CANCELLED')
 api_page=(page-1)//3+1;offset=((page-1)%3)*8
 if source=='tmdb':
  data=__import__('tmdb_connection60').request(TMDB+'/search/'+kind+'?'+urlencode(dict(query=query,language='de-DE',include_adult='false',page=api_page)),token=tmdb_token(),cancel=cancel)
  raw=data.get('results');total=data.get('total_pages')
  if not isinstance(raw,list) or len(raw)>20 or type(total) is not int or total<0 or data.get('page',api_page)!=api_page:raise SourceError('CANDIDATES_REJECTED')
  more=offset+8<len(raw) or api_page<min(3,total)
 else:
  if kind!='tv':raise SourceError('CANDIDATES_REJECTED')
  data=get('https://api.tvmaze.com/search/shows?'+urlencode(dict(q=query)),api=True,cancel=cancel,json_list67=True)
  if not isinstance(data,list) or len(data)>20:raise SourceError('CANDIDATES_REJECTED')
  raw=[r['show'] for r in data if isinstance(r,dict) and isinstance(r.get('show'),dict)];offset=(page-1)*8;more=offset+8<len(raw)
 rows=[]
 for row in raw[offset:offset+8]:
  if cancel():raise SourceError('CANCELLED')
  if not isinstance(row,dict) or type(row.get('id')) is not int or row['id']<=0 or row.get('adult'):continue
  if source=='tmdb':
   title=row.get('name' if kind=='tv' else 'title');year=str(row.get('first_air_date' if kind=='tv' else 'release_date') or '')[:4]
   poster=_tmdb_image(row.get('poster_path'));backdrop=_tmdb_image(row.get('backdrop_path'));country=row.get('origin_country') or []
  else:
   title=row.get('name');year=str(row.get('premiered') or '')[:4];poster=(row.get('image') or {}).get('original','');backdrop=''
   if not re.fullmatch(r'https://static\.tvmaze\.com/uploads/images/(?:original_untouched|medium_portrait)/[0-9]+/[0-9]+\.(?:jpg|png)',poster):poster=''
   code=((row.get('network') or row.get('webChannel') or {}).get('country') or {}).get('code');country=[code] if isinstance(code,str) else []
  if not isinstance(title,str) or not title.strip() or not year.isdigit() or not 1880<=int(year)<=2100 or not poster and not backdrop:continue
  value=dict(id=row['id'],source=source,media_type86=kind,title=title[:200],year=int(year),country=[str(c)[:3] for c in country[:4]],overview=unescape(re.sub('<[^>]*>','',str(row.get('overview') or row.get('summary') or '')))[:1000],poster=poster,url=backdrop or poster,role='backdrop' if backdrop else 'poster',verified85=False,preview89=True)
  if poster and safe(poster):value['thumb86']=poster+OPTIONS
  rows.append(value)
 return dict(rows=rows,more=more,code='READY' if rows else 'ZERO_RESULTS')

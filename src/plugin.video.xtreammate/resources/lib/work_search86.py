"""Bounded editable TV/movie research; search never mutates a work mapping."""
import re,time
from urllib.parse import urlencode
from media_sources43 import SourceError

def aliases(query):
 query=str(query or '').strip()[:200]
 variants=[query]
 if query.casefold() in ('charmed – zauberhafte hexen','charmed - zauberhafte hexen','zauberhafte hexen','charmed'):
  variants+=['Charmed','Charmed – Zauberhafte Hexen','Zauberhafte Hexen']
 return list(dict.fromkeys(variants))
def details(ident,kind,source='tmdb',cancel=lambda:False):
 if type(ident) is not int or ident<=0 or kind not in ('tv','movie'):raise SourceError('CANDIDATES_REJECTED')
 if source=='tvmaze':
  if kind!='tv':raise SourceError('CANDIDATES_REJECTED')
  row=__import__('programme_tvmaze85').details({},ident,cancel,manual=True)
 else:
  from tmdb_connection60 import request
  from media_sources43 import TMDB,tmdb_token,_tmdb_image
  data=request(TMDB+'/'+kind+'/'+str(ident)+'?language=de-DE',token=tmdb_token(),cancel=cancel)
  title=str(data.get('name' if kind=='tv' else 'title') or '')
  year=str(data.get('first_air_date' if kind=='tv' else 'release_date') or '')[:4]
  if data.get('id')!=ident or data.get('adult') or not title or not year.isdigit():raise SourceError('CANDIDATES_REJECTED')
  poster=_tmdb_image(data.get('poster_path'));backdrop=_tmdb_image(data.get('backdrop_path'))
  if not poster and not backdrop:raise SourceError('NO_ARTWORK')
  row=dict(id=ident,source='tmdb',title=title[:200],original=str(data.get('original_name' if kind=='tv' else 'original_title') or '')[:200],year=int(year),country=[str(c)[:3] for c in (data.get('origin_country') or [])[:4]],overview=str(data.get('overview') or '')[:1000],poster=poster,url=backdrop or poster,role='backdrop' if backdrop else 'poster',verified85=True)
 row['media_type86']=kind
 return row

def search(query,kind='tv',source='tmdb',page=1,cancel=lambda:False):
 from programme_candidates85 import enabled
 if not enabled(source):raise SourceError('SOURCE_DISABLED')
 if kind not in ('tv','movie') or source not in ('tmdb','tvmaze') or type(page) is not int or not 1<=page<=9:raise SourceError('CANDIDATES_REJECTED')
 query=str(query or '').strip()[:200]
 if not query:raise SourceError('QUERY_EMPTY')
 if source=='tvmaze':
  if kind!='tv':raise SourceError('CANDIDATES_REJECTED')
  rows,complete=__import__('programme_tvmaze85').search(dict(title=query,_manager85=True),cancel)
  for row in rows:row['media_type86']='tv'
  return dict(rows=rows,more=False,code='READY' if rows else 'ZERO_RESULTS')
 from tmdb_connection60 import request
 from media_sources43 import TMDB,tmdb_token
 rows=[];more=False;rejected=0;started=time.monotonic()
 original_cancel=cancel;cancel=lambda:original_cancel() or time.monotonic()-started>22
 api_page=(page-1)//3+1;start=((page-1)%3)*8
 for variant in aliases(query):
  if cancel() or time.monotonic()-started>20:break
  data=request(TMDB+'/search/'+kind+'?'+urlencode(dict(query=variant,language='de-DE',include_adult='false',page=api_page)),token=tmdb_token(),cancel=cancel)
  part=data.get('results');total=data.get('total_pages')
  if not isinstance(part,list) or len(part)>20 or type(total) is not int or total<0 or data.get('page',api_page)!=api_page:raise SourceError('CANDIDATES_REJECTED')
  more=more or start+8<len(part) or api_page<min(3,total)
  for row in part[start:start+8]:
   if cancel() or len(rows)>=8 or time.monotonic()-started>20:break
   if not isinstance(row,dict) or type(row.get('id')) is not int or row.get('adult'):rejected+=1;continue
   if any(v['id']==row['id'] for v in rows):continue
   try:verified=details(row['id'],kind,cancel=cancel)
   except SourceError as error:
    if error.code in ('CANDIDATES_REJECTED','NO_ARTWORK','NO_MATCH'):rejected+=1;continue
    raise
   rows.append(verified)
  if rows:break
 # Preflight at most five candidate posters; unverified paths never reach GUI.
 for row in rows[:5]:
  if cancel():break
  url=row.get('poster','')
  try:
   if not url or not __import__('programme_urls55').safe(url):continue
   checked=__import__('programme_urls55').probe(url,cancel=cancel)
   row.update(thumb86=url+__import__('programme_urls55').OPTIONS,width86=checked['width'],height86=checked['height'])
  except (SourceError,OSError,ValueError):continue
 return dict(rows=rows,more=more,code='READY' if rows else 'CANDIDATES_REJECTED' if rejected else 'ZERO_RESULTS')

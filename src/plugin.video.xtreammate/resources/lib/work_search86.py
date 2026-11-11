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
 from programme_candidates85 import enabled
 if source not in ('tmdb','tvmaze') or not enabled(source):raise SourceError('SOURCE_DISABLED')
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
  if data.get('id')!=ident or data.get('adult') or not title or not year.isdigit() or not 1880<=int(year)<=2100:raise SourceError('CANDIDATES_REJECTED')
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
 # A candidate page is a preview, not a verified assignment. Fetch only the
 # search response; the selected work alone is independently checked on Save.
 return __import__('work_candidates89').search(query,kind,source,page,cancel)

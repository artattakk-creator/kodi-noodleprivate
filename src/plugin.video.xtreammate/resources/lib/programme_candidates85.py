"""Bounded independently verified TV works; guesses never become episode facts."""
import hashlib,json,re,time
from urllib.parse import urlencode
MAX_PAGES=3;MAX_ROWS=60;MAX_DETAILS=8
PREFIX='XCMate.TVCandidates85.'
_cache={}

def note(event,code):__import__('art_trace81').note(event,'SKIPPED_REASON' if code in ('PROVISIONAL_SUGGESTION','MULTIPAGE_SEARCH','SEARCH_INCOMPLETE') else 'MATCH_REJECTED',code)
def enabled(source='tmdb'):
 from utils import setting_bool
 if source=='tmdb':return setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False) and not setting_bool('programme_tmdb_optout77',False)
 return setting_bool('programme_tvmaze67',False) and not setting_bool('programme_tvmaze_optout77',False)
def key(event):
 from programme_mapping85 import namespace
 from programme_policy68 import negative_scope
 return hashlib.sha256((namespace(event)+negative_scope({})+('manager85' if event.get('_manager85') else '')).encode()).hexdigest()
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def remember(event,rows,complete=True,tv_only=False):
 data=dict(at=time.time(),key=key(event),rows=rows[:MAX_DETAILS],complete=bool(complete),tv_only85=tv_only)
 raw=json.dumps(data,separators=(',',':'))
 if len(raw.encode())<=64*1024:window().setProperty(PREFIX+key(event),raw)
 _cache[key(event)]=data
 while len(_cache)>64:
  first=next(iter(_cache));_cache.pop(first);window().clearProperty(PREFIX+first)
def read(event):
 try:
  raw=window().getProperty(PREFIX+key(event));data=json.loads(raw) if raw and len(raw.encode())<=64*1024 else {}
  if data.get('key')==key(event) and 0<=time.time()-data.get('at',0)<600:return data
 except (ValueError,TypeError):pass
 return {}
def pages(event,kind,query,cancel):
 from tmdb_connection60 import request
 from media_sources43 import TMDB,tmdb_token,SourceError
 rows=[];total=None;pages_count=None;complete=False;started=time.monotonic()
 for page in range(1,MAX_PAGES+1):
  if cancel() or time.monotonic()-started>15:break
  data=request(TMDB+'/search/'+kind+'?'+urlencode(dict(query=query,language='de-DE',include_adult='false',page=page)),token=tmdb_token(),cancel=cancel)
  part=data.get('results');count=data.get('total_results');number=data.get('total_pages')
  if not isinstance(part,list) or len(part)>20 or type(count) is not int or count<0 or type(number) is not int or number<0 or any(not isinstance(r,dict) or type(r.get('id')) is not int or r['id']<=0 for r in part):raise SourceError('NO_MATCH_AMBIGUOUS')
  if total is None:total,pages_count=count,number
  if count!=total or number!=pages_count or data.get('page',page)!=page or (number>page and len(part)!=20):raise SourceError('NO_MATCH_AMBIGUOUS')
  rows.extend(part)
  if page==1 and number>1:note(event,'MULTIPAGE_SEARCH')
  if page>=number:
   complete=len(rows)==total;break
 if len({r['id'] for r in rows})!=len(rows):complete=False
 if not complete:note(event,'SEARCH_INCOMPLETE')
 return rows[:MAX_ROWS],complete

def details(event,ident,cancel=lambda:False,manual=False,row=None):
 from tmdb_connection60 import request
 from media_sources43 import TMDB,tmdb_token,_tmdb_image
 from programme_mapping85 import name
 data=request(TMDB+'/tv/'+str(ident)+'?language=de-DE',token=tmdb_token(),cancel=cancel)
 if data.get('id')!=ident or data.get('adult'):raise __import__('media_sources43').SourceError('NO_MATCH')
 year=str(data.get('first_air_date',''))[:4]
 if not year.isdigit() or not 1880<=int(year)<=2100:return None
 title=str(data.get('name') or '');original=str(data.get('original_name') or '')
 if not title and not original:return None
 if row is not None and not {name(row.get(k)) for k in ('name','original_name') if row.get(k)}.intersection({name(title),name(original)}):raise __import__('media_sources43').SourceError('NO_MATCH')
 expected=name(event.get('title'));alias=False;work_match85=expected in (name(title),name(original))
 if not manual and expected not in (name(title),name(original)):
  alternatives=request(TMDB+'/tv/'+str(ident)+'/alternative_titles',token=tmdb_token(),cancel=cancel)
  if alternatives.get('id')!=ident or not any(name(row.get('title'))==expected for row in alternatives.get('results',[]) if isinstance(row,dict)):
   note(event,'SERIES_ALIAS_UNVERIFIED')
  else:alias=True;work_match85=True
 external=event.get('external_ids') or {}
 actual=data.get('external_ids') or {}
 if not manual and isinstance(external,dict) and external and any(k not in actual for k in external):actual=request(TMDB+'/tv/'+str(ident)+'/external_ids',token=tmdb_token(),cancel=cancel)
 if not manual and isinstance(external,dict) and any(v and (k not in actual or str(v)!=str(actual[k])) for k,v in external.items()):note(event,'EXTERNAL_ID_CONFLICT');return None
 backdrop=_tmdb_image(data.get('backdrop_path'));poster=_tmdb_image(data.get('poster_path'))
 if not backdrop and not poster:
  note(event,'TV_IMAGE_MISSING');raise __import__('media_sources43').SourceError('NO_ARTWORK')
 countries=data.get('origin_country') or [];countries=[str(x)[:3].upper() for x in countries[:4] if isinstance(x,str)] if isinstance(countries,list) else []
 return dict(id=ident,source='tmdb',title=title[:200],original=original[:200],year=int(year),country=countries,overview=str(data.get('overview') or '')[:1000],poster=poster or '',url=backdrop or poster,role='backdrop' if backdrop else 'poster',verified85=True,alias85=alias,work_match85=work_match85 or manual)

def search_tmdb85(event,cancel=lambda:False):
 from media_sources43 import SourceError
 from programme_mapping85 import name
 if not enabled():remember(event,[]);return [],True
 genre=str(event.get('genre') or '').casefold()
 if not event.get('_manager85') and any(v in genre for v in ('film','movie','nachricht','news','sport','talk')):remember(event,[]);return [],True
 label=str(event.get('title') or '')[:200];year=str(event.get('year') or '')
 suffix=re.fullmatch(r'(.+?)\s+\(((?:19|20)[0-9]{2})\)',label)
 if suffix:
  if year and year!=suffix[2]:raise SourceError('NO_MATCH')
  label,year=suffix[1],suffix[2];event=dict(event,title=label,year=year)
 if not label:return [],True
 query={'yuna stitch':'Stitch!'}.get(name(label),label)
 rows,complete=pages(event,'tv',query,cancel)
 exact=[r for r in rows if name(label) in (name(r.get('name')),name(r.get('original_name')))]
 if year and not event.get('_manager85'):
  if not year.isdigit() or not 1880<=int(year)<=2100:raise SourceError('NO_MATCH')
  matches=[r for r in exact if str(r.get('first_air_date',''))[:4]==year]
  if exact and not matches:note(event,'SERIES_YEAR_CONFLICT');raise SourceError('NO_MATCH')
  exact=matches
 considered=exact if exact else rows[:4]
 verified=[];started=time.monotonic()
 for row in considered[:MAX_DETAILS]:
  if cancel() or time.monotonic()-started>15:complete=False;break
  if row.get('adult'):continue
  try:candidate=details(event,row['id'],cancel,manual=bool(event.get('_manager85')),row=row)
  except SourceError:
   if len(considered)==1:raise
   continue
  if not candidate:continue
  if str(row.get('first_air_date',''))[:4]!=str(candidate['year']):continue
  if not event.get('_manager85') and year and str(candidate['year'])!=year:continue
  verified.append(candidate)
 if len(considered)>MAX_DETAILS:complete=False
 country=str(event.get('country') or '').upper()
 def score(row):
  evidence=int(bool(year) and str(row['year'])==year)*8+int(bool(country) and country in row['country'])*4
  # Only explicit trusted facts affect confidence; server ranking breaks ties
  # for a provisional illustration, never for a confirmed identity.
  return evidence
 verified.sort(key=score,reverse=True)
 remember(event,verified,complete)
 if len(exact)>1 and not verified:raise SourceError('NO_MATCH_AMBIGUOUS')
 return verified,complete

def candidate(event,cancel=lambda:False):
 from media_sources43 import SourceError
 from programme_mapping85 import current
 mapping=current(event)
 if mapping and mapping.get('id') and not enabled(mapping.get('source')):return None
 if mapping and mapping.get('hidden'):return None
 if mapping and mapping.get('source') in ('tmdb','tvmaze') and enabled(mapping['source']):
  fetch85=(lambda e,i,cancel,manual=True:__import__('work_search86').details(i,'movie',mapping['source'],cancel)) if mapping.get('media_type86')=='movie' else details if mapping['source']=='tmdb' else __import__('programme_tvmaze85').details
  chosen=next((r for r in read(event).get('rows',[])+read(dict(event,_manager85=True)).get('rows',[]) if r.get('source')==mapping['source'] and r.get('id')==mapping['id'] and r.get('media_type86','tv')==mapping.get('media_type86','tv') and r.get('verified85')),None)
  if chosen is None and mapping.get('work87'):
   receipt87=mapping['work87']
   from programme_urls55 import safe
   if receipt87.get('role') in ('poster','backdrop') and safe(receipt87.get('url','')):
    chosen=dict(receipt87,id=mapping['id'],source=mapping['source'],year=mapping.get('year'),country=mapping.get('country') or [],media_type86=mapping.get('media_type86','tv'),verified85=True,work_match85=True)
  if chosen is None:chosen=fetch85(event,mapping['id'],cancel,manual=True)
  if chosen and (mapping.get('year') is None or mapping['year']==chosen['year']):return artifact(chosen,'MANUAL_CONFIRMED')
  note(event,'EXTERNAL_ID_CONFLICT');return None
 cached=read(event)
 if cached.get('tv_only85'):
  rows,complete=cached.get('rows',[]),cached.get('complete',False)
 else:rows,complete=search(event,cancel)
 if not rows:return None
 country=str(event.get('country') or '').upper()
 matching=[r for r in rows if r.get('work_match85',True) and (not country or country in r['country'])]
 if not matching:
  if any(v in str(event.get('genre') or '').casefold() for v in ('serie','series','sitcom','episode')):raise SourceError('NO_MATCH')
  return None
 chosen=matching[0] if matching else rows[0]
 genre=str(event.get('genre') or '').casefold()
 if not cached.get('tv_only85') and not any(v in genre for v in ('serie','series','sitcom','episode')):
  from programme_mapping85 import name
  if not enabled():raise SourceError('NO_MATCH_AMBIGUOUS')
  films,done=pages(event,'movie',str(event['title']),cancel)
  names={name(event['title'])}|{name(r[k]) for r in rows for k in ('title','original')}
  if not done or any(names.intersection((name(r.get('title')),name(r.get('original_title')))) and (not event.get('year') or str(r.get('release_date',''))[:4]==str(event['year'])) for r in films):raise SourceError('NO_MATCH_AMBIGUOUS')
 remember(event,rows,complete,tv_only=True)
 if not complete or len(matching)!=1:note(event,'TV_MULTIPLE_MATCHES');raise SourceError('NO_MATCH_AMBIGUOUS')
 __import__('programme_flow48').trace('MATCH',event,'READY')
 return artifact(chosen,'EXACT_TV_TITLE_YEAR66' if event.get('year') else 'EXACT_UNIQUE_TV_TITLE66')

def artifact(row,match):
 from tmdb_connection60 import ATTRIBUTION
 return dict(url=row['url'],source=('tmdb_movie' if row.get('media_type86')=='movie' else 'tmdb_series') if row['source']=='tmdb' else 'tvmaze_series',role81=row['role'],match=match,remote_id=row['id'],matched_year56=row['year'],image_scope57='series_fallback',attribution=('TMDB · https://www.themoviedb.org/'+('movie' if row.get('media_type86')=='movie' else 'tv')+'/'+str(row['id'])+' · '+ATTRIBUTION if row['source']=='tmdb' else 'TVmaze · https://www.tvmaze.com/shows/'+str(row['id'])+' · Daten CC BY-SA, Bildrechte beim Rechteinhaber')+' · Serienbild (kein Episodenbild)',manual85=match=='MANUAL_CONFIRMED',official_poster86=row.get('poster',''))

def suggestion(event):
 from utils import setting_bool
 from programme_mapping85 import current
 if not setting_bool('programme_suggestions85',True) or not (enabled() or enabled('tvmaze')) or (current(event) or {}).get('hidden'):return None
 data=read(event);rows=data.get('rows',[])
 if not rows:return None
 # Unclassified cross-media conflicts never permit even a provisional image.
 genre=str(event.get('genre') or '').casefold()
 if not data.get('tv_only85') and not any(v in genre for v in ('serie','series','sitcom','episode')):return None
 row=next((r for r in rows if r.get('poster')),None)
 if not row:return None
 value=artifact(row,'PROVISIONAL_TV85');value.update(url=row['poster'],role81='poster',provisional85=True,attribution='Bildvorschlag – Zuordnung nicht bestätigt · '+value['attribution'])
 note(event,'PROVISIONAL_SUGGESTION');return value


def search(event,cancel=lambda:False,include_tvmaze=False):
 from media_sources43 import SourceError
 rows=[];complete=True
 if enabled():
  try:rows,complete=search_tmdb85(event,cancel)
  except SourceError as error:
   if not include_tvmaze or error.code not in ('TIMEOUT','NETWORK_ERROR','TLS_ERROR','DNS_ERROR','HTTP_SERVER'):raise
 if include_tvmaze and not rows and enabled('tvmaze') and not cancel():
  rows,complete=__import__('programme_tvmaze85').search(event,cancel)
  remember(event,rows,complete)
 return rows,complete

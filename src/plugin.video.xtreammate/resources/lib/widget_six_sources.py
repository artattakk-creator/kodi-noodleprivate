"""Read-only six-row source discovery. Never edits saved BINGIE shortcuts.

Foreign routes stay in their own add-ons; XCMate credentials are never added.
Only browse-only TMDB lists and the installed audio add-on are admissible.
"""
import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit, parse_qs, parse_qsl, urlencode, urlunsplit

SPECS=(('vod','Filme',None,'videos'),('series','Serien',None,'videos'),
       ('cinema','Im Kino',29761,'videos'),('disney','Disney',29762,'videos'),
       ('trend','Diese Woche im Trend',29763,'videos'),('mp3','MP3s',29764,'music'))
EXTRAS=SPECS[2:]
CORE={'widget_live_start_group':'live','widget_recent_vod':'vod','widget_recent_series':'series'}
HELPER='plugin.video.themoviedb.helper'
AUDIO='plugin.audio.m3sr2019'
RELOAD=re.compile(r'\$INFO\[Window\((?:Home|10000)\)\.Property\((widgetreload(?:2|movies|tvshows)?|TMDbHelper\.Widgets\.Reload)\)\]')
HELPER_KEYS={'info','tmdb_type','reload','widget','with_id','with_watch_providers','watch_region','region',
 'with_watch_monetization_types','with_genres','with_networks','with_companies','sort_by','language','page',
 'limit','include_adult','with_original_language','year','primary_release_year','first_air_date_year'}

def uri(value,kind):
 if not isinstance(value,str) or not 0<len(value)<=4096 or any(ord(c)<32 for c in value):raise ValueError('SOURCE_URI_REJECTED')
 if any(c in value for c in ('"',"'",'\\')):raise ValueError('SOURCE_URI_REJECTED')
 checked=RELOAD.sub('reload',value)
 if '$' in checked or any(c in checked for c in ('(',')','[',']')):raise ValueError('SOURCE_URI_REJECTED')
 p=urlsplit(value);q=parse_qs(p.query,keep_blank_values=True)
 if any('$' in v and (k!='reload' or not RELOAD.fullmatch(v)) for k,values in q.items() for v in values):raise ValueError('SOURCE_URI_REJECTED')
 if any(any(ord(c)<32 for c in v) or any(c in v for c in ('\"',"'",'\\')) for values in q.values() for v in values):raise ValueError('SOURCE_URI_REJECTED')
 if p.scheme!='plugin' or p.fragment or p.netloc not in (HELPER,AUDIO) or any(len(v)!=1 for v in q.values()):raise ValueError('SOURCE_URI_REJECTED')
 if kind=='mp3':
  if p.netloc!=AUDIO or not re.fullmatch(r'/(?:|favourites/(?:song|album|artist)|musicmp3/(?:main_albums/[^/]+/[^/]+/(?:new|top)/[0-9]+/dir|album|artists_albums))',p.path):raise ValueError('AUDIO_BROWSE_REQUIRED')
  if any(k not in ('reload','link') for k in q):raise ValueError('AUDIO_BROWSE_REQUIRED')
 else:
  if p.netloc!=HELPER or p.path!='/' or set(q)-HELPER_KEYS:raise ValueError('SOURCE_URI_REJECTED')
  info=q.get('info',[''])[0];media=q.get('tmdb_type',[''])[0]
  if kind=='cinema' and (info,media)!=('now_playing','movie'):raise ValueError('CINEMA_SOURCE_REQUIRED')
  if kind=='trend' and (info,media)!=('trending_week','tv'):raise ValueError('TREND_SOURCE_REQUIRED')
  if q.get('with_id',['True'])[0] not in ('True','true','False','false'):raise ValueError('SOURCE_URI_REJECTED')
  if kind=='disney':
   providers=re.split(r'[|,]',q.get('with_watch_providers',[''])[0])
   if (info,media)!=('discover','movie') or '337' not in providers or not re.fullmatch('[A-Z]{2}',q.get('watch_region',[''])[0]):raise ValueError('DISNEY_SOURCE_REQUIRED')
  if kind not in ('cinema','trend','disney'):raise ValueError('SOURCE_KIND_REJECTED')
 return value

def runtime_uri(value,kind,reload_value=lambda name:'xcmate-six-static'):
 """Resolve only inert refresh labels; never pulse the shared reload hook."""
 value=uri(value,kind);p=urlsplit(value)
 def replace(match):
  value=reload_value(match.group(1))
  return value if isinstance(value,str) and len(value)<=128 else ''
 pairs=[(k,RELOAD.sub(replace,v)) for k,v in parse_qsl(p.query,keep_blank_values=True)]
 return urlunsplit((p.scheme,p.netloc,p.path,urlencode(pairs),''))

def menu_audio(profile):
 from widget_binding50 import xml
 from widget_transaction50 import read
 root=Path(profile)/'addon_data/script.skinshortcuts'
 for path in sorted(root.glob('*-mainmenu.DATA.xml')):
  tree=xml(read(path))
  for node in tree.findall('shortcut'):
   action=node.findtext('action') or ''
   match=re.fullmatch(r'ActivateWindow\((?:Music|10500),\s*("[^"]+"|[^,()]+),\s*return\)',action,re.I)
   if not match:continue
   value=match[1].strip('"')
   try:return uri(value,'mp3')
   except ValueError:continue
 return None

def discover(profile,pid,enabled=lambda addon:False,reload_value=lambda name:'xcmate-six-static'):
 from widget_inventory87 import widgets
 from widget_reload78 import directory_uri89
 rows=widgets(profile);groups={}
 for row in rows:
  try:
   p=urlsplit(directory_uri89(row['path']));q=parse_qs(p.query);kind=CORE.get(q.get('action',[''])[0])
  except ValueError:continue
  if not kind or q.get('pid',[str(pid)])[0]!=str(pid):continue
  key=(row['file'],row['menu'],row['identity']);groups.setdefault(key,{})[kind]=row
 roots=[(key,values) for key,values in groups.items() if set(values)=={'live','vod','series'}]
 result={'root':roots[0][0] if len(roots)==1 else None,'code':'READY' if len(roots)==1 else 'OWN_HOME_AMBIGUOUS' if roots else 'OWN_HOME_MISSING','sources':{}}
 for kind,title,cid,target in EXTRAS:
  choices=[]
  for record in rows:
   try:choices.append(uri(record['path'],kind))
   except ValueError:continue
  if kind=='mp3' and not choices:
   value=menu_audio(profile)
   if value:choices.append(value)
  choices=list(dict.fromkeys(choices));addon=AUDIO if kind=='mp3' else HELPER
  code='SOURCE_NOT_CONFIGURED' if not choices else 'SOURCE_AMBIGUOUS' if len(choices)>1 else 'SOURCE_UNAVAILABLE' if not enabled(addon) else 'WAITING'
  resolved=runtime_uri(choices[0],kind,reload_value) if len(choices)==1 else ''
  result['sources'][kind]={'kind':kind,'title':title,'cid':cid,'target':target,'code':code,'uri':resolved if code=='WAITING' else '',
   'source_hash':hashlib.sha256(resolved.encode()).hexdigest() if len(choices)==1 else '', 'addon':addon}
 return result

def public_summary(plan):
 """No raw paths, URLs, menu names, provider identifiers or auth material."""
 return {'code':plan['code'],'rows':[{'kind':r['kind'],'title':r['title'],'control':r['cid'],'target':r['target'],'code':r['code'],'addon':r['addon']} for r in plan['sources'].values()]}

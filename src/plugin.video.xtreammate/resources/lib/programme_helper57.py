"""Public Helper search/details directories; no private imports/settings/keys.

Only the existing programme worker calls this module. Exact identity is proved
before handing an image to the existing URL preflight/index. The device-specific
installed version and real pixels remain a separate Android acceptance gate.
"""
import re
from urllib.parse import parse_qs,urlsplit,urlencode,unquote
from helper_rpc57 import call,Error

ADDON='plugin.video.themoviedb.helper'
FIELDS=['title','originaltitle','year','art','uniqueid','season','episode','showtitle','premiered']


def number(value):
    if isinstance(value,bool):return None
    return int(str(value)) if re.fullmatch(r'[1-9][0-9]{0,11}',str(value)) else None


def kind(event):
    if number(event.get('season')) and number(event.get('episode')):return 'tv'
    genre=str(event.get('genre','')).casefold()
    if any(v in genre for v in ('spielfilm','movie','film')):return 'movie'
    if any(v in genre for v in ('nachricht','news','talk','sport','fußball')):return 'unsupported'
    return 'both'  # no fabricated movie classification; cross-type uniqueness


def available(cancel=lambda:False,rpc=call):
    try:value=rpc('Addons.GetAddonDetails',dict(addonid=ADDON,properties=['version','enabled','installed']),cancel=cancel)
    except Error as exc:
        if exc.code=='HELPER_BACKGROUND_UNAVAILABLE':raise Error('HELPER_NOT_AVAILABLE') from None
        raise
    addon=value.get('addon',{})
    if addon.get('addonid')!=ADDON or addon.get('enabled') is not True or addon.get('installed') is not True:
        raise Error('HELPER_NOT_AVAILABLE')
    version=addon.get('version','')
    if not isinstance(version,str) or not re.fullmatch(r'[56]\.[0-9]+\.[0-9]+(?:[~+.-][A-Za-z0-9.-]+)?',version):
        raise Error('HELPER_VERSION_UNSUPPORTED')
    return version


def directory(params,cancel=lambda:False,rpc=call):
    # Fully supplied query / exact IDs: never keyboard, playback, RunScript,
    # Container.Update or service-monitor skin/window-property commands.
    params=dict(params,widget='true',cacheonly='false',nextpage='true')
    available(cancel,rpc)  # disabled/missing add-ons must not trigger InstallModal
    uri='plugin://'+ADDON+'/?'+urlencode(params)
    result=rpc('Files.GetDirectory',dict(directory=uri,media='video',properties=FIELDS,
        limits=dict(start=0,end=25)),cancel=cancel)
    rows=result.get('files',[]);limits=result.get('limits',{})
    if not isinstance(rows,list) or len(rows)>24 or any(not isinstance(v,dict) for v in rows):raise Error('NO_UNIQUE_MATCH')
    total=limits.get('total',len(rows))
    if not isinstance(total,int) or total!=len(rows):raise Error('NO_UNIQUE_MATCH')
    for row in rows:
        if any(number(v)>1 for v in params_of(row).get('page',[]) if number(v)):raise Error('NO_UNIQUE_MATCH')
    return rows


def params_of(row):
    raw=row.get('file','')
    if not isinstance(raw,str) or len(raw)>4096:return {}
    try:parsed=urlsplit(raw)
    except ValueError:return {}
    return parse_qs(parsed.query) if parsed.scheme=='plugin' and parsed.netloc==ADDON else {}


def identity(row):
    params=params_of(row);unique=row.get('uniqueid',{})
    if not isinstance(unique,dict):unique={}
    one=lambda k:params.get(k,[''])[0] if len(params.get(k,[]))==1 else ''
    query_id=number(one('tmdb_id'));tag_id=number(unique.get('tmdb'))
    # Episode uniqueid.tmdb may identify the EPISODE; the documented plugin
    # path tmdb_id identifies its parent SERIES. Never equate those two IDs.
    episode=row.get('type')=='episode'
    if not episode and query_id and tag_id and query_id!=tag_id:raise Error('HELPER_NO_ID')
    remote=query_id if episode else tag_id or query_id
    if not remote:raise Error('HELPER_NO_ID')
    route_type=one('tmdb_type');tag_type=row.get('type','')
    inferred='movie' if tag_type=='movie' else 'tv' if tag_type in ('tvshow','episode','season') else ''
    if route_type and inferred and route_type!=inferred:raise Error('NO_UNIQUE_MATCH')
    media=route_type or inferred
    if media not in ('movie','tv'):raise Error('NO_UNIQUE_MATCH')
    return media,remote


def same_title(wanted,row,series=False):
    from epg_events import title_key
    fields=('showtitle',) if series else ('title','originaltitle')
    return any(title_key(wanted)==title_key(row.get(field,'')) for field in fields)


def images(row,episode=False,check=None):
    arts=row.get('art',{})
    if not isinstance(arts,dict):return []
    names=('thumb','landscape') if episode else ('fanart','landscape','poster')
    if check is None:
        from programme_urls55 import safe as check
    result=[]
    for name in names:
        value=arts.get(name,'')
        if isinstance(value,str) and value.startswith('image://') and value.endswith('/'):
            value=unquote(value[8:-1])  # exactly one documented Kodi image wrapper
        if check(value) and value not in result:result.append(value)
    return result


def image(row,episode=False,check=None):
    return next(iter(images(row,episode,check)),'')


def episode_images(item,parent,check=None):
    arts=parent.get('art',{})
    arts=arts if isinstance(arts,dict) else {}
    parent_images=[image(dict(art={role:value}),check=check) for role,value in arts.items() if role in ('poster','fanart','landscape')]
    asset=lambda value:(urlsplit(value).hostname,urlsplit(value).path.rsplit('/',1)[-1])
    return [url for url in images(item,episode=True,check=check) if not any(value and asset(value)==asset(url) for value in parent_images)]


def lookup(event,cancel=lambda:False,rpc=call,image_check=None):
    if kind(event)=='unsupported':raise Error('NO_UNIQUE_MATCH')
    version=available(cancel,rpc)
    from programme_sources57 import trace
    trace(event,'HELPER_AVAILABLE')
    from epg_events import title_key
    title=str(event.get('title','')).strip();media=kind(event)
    if not 3<=len(title)<=512 or not title_key(title):raise Error('NO_UNIQUE_MATCH')
    params=dict(info='search',tmdb_type=media,query=title,length=20)
    year=number(event.get('year'))
    if year and media=='movie':params['year']=year
    rows=directory(params,cancel,rpc);matches={}
    for row in rows:
        if not same_title(title,row):continue
        typed,remote=identity(row)
        if media!='both' and typed!=media:continue
        # EPG episode year is not the series' first-aired year.
        found_year=number(row.get('year'))
        if typed=='movie' and (not found_year or year and found_year!=year):continue
        matches[(typed,remote)]=row
    if len(matches)!=1:raise Error('NO_UNIQUE_MATCH')
    (typed,remote),found=next(iter(matches.items()))
    details=directory(dict(info='details',tmdb_type=typed,tmdb_id=remote),cancel,rpc)
    if len(details)!=1:raise Error('NO_UNIQUE_MATCH')
    detail=details[0]
    if identity(detail)!=(typed,remote) or not same_title(title,detail):raise Error('NO_UNIQUE_MATCH')
    confirmed=number(detail.get('year'))
    if not confirmed or confirmed!=number(found.get('year')):raise Error('NO_UNIQUE_MATCH')
    if typed=='movie':
        url=image(detail,check=image_check);scope='movie';proof='EXACT_HELPER_MOVIE57'
    elif number(event.get('season')) and number(event.get('episode')):
        season,episode=number(event['season']),number(event['episode'])
        details=directory(dict(info='details',tmdb_type='tv',tmdb_id=remote,season=season,episode=episode),cancel,rpc)
        if len(details)!=1:raise Error('NO_UNIQUE_MATCH')
        item=details[0]
        if identity(item)!=('tv',remote) or not same_title(title,item,series=True) or number(item.get('season'))!=season or number(item.get('episode'))!=episode:raise Error('NO_UNIQUE_MATCH')
        if event.get('subtitle') and not same_title(event['subtitle'],item):raise Error('NO_UNIQUE_MATCH')
        url=next(iter(episode_images(item,detail,image_check)),'');scope='episode';proof='EXACT_HELPER_EPISODE57'
        # Some Helper artwork policies put a parent poster into episode.thumb.
        # Same CDN asset, even at another width, is not evidence of a still.
        if not url:url=image(detail,check=image_check);scope='series_fallback';proof='EXACT_HELPER_SERIES57'
    else:
        # A TV result alone must never be called an episode still.
        url=image(detail,check=image_check);scope='series_fallback';proof='EXACT_HELPER_SERIES57'
    if not url:raise Error('HELPER_ART_MISSING')
    credit='TMDb Helper / TMDb · https://www.themoviedb.org/'+typed+'/'+str(remote)+' · nicht von TMDb zertifiziert; Bildnutzungsbedingungen beachten'
    if scope=='series_fallback':credit+=' · Serienbild (kein Episodenbild)'
    choices=episode_images(item,detail,image_check) if scope=='episode' else images(detail,check=image_check)
    result=dict(url=url,source='tmdb_helper',match=proof,remote_id=remote,matched_year56=confirmed,
                image_scope57=scope,helper_version57=version,attribution=credit,
                alternate_urls57=[v for v in choices if v!=url])
    if scope=='episode':
        parent=images(detail,check=image_check)
        if parent:result['series_fallback57']=dict(result,url=parent[0],match='EXACT_HELPER_SERIES57',image_scope57='series_fallback',
            alternate_urls57=parent[1:],attribution=credit+' · Serienbild (kein Episodenbild)')
    return result

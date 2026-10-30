"""Bounded existing XCMate/Kodi catalogue reads, never imports or scrapes.

Only exact title/year or identified parent/season/episode is eligible. This
source references already present validated HTTPS art; private local/SMB paths
are not exported as Internet URLs. The existing shared preflight remains final.
"""
import json
from programme_helper57 import number,kind,same_title,image,images,episode_images
from helper_rpc57 import call,Error


def choose(event,rows,source,allow_missing_series_art=False):
    wanted=kind(event);matches={}
    for row in rows:
        if not same_title(event.get('title',''),row):continue
        if row.get('type') not in ('movie','tvshow'):continue
        if wanted!='both' and row['type']!=('movie' if wanted=='movie' else 'tvshow'):continue
        year=number(event.get('year'));actual=number(row.get('year'))
        # A pre-existing arbitrary title alone cannot disambiguate a remake.
        if not year or year!=actual:continue
        identity=(row['type'],str(row.get('id','')),actual)
        matches[identity]=row
    if len(matches)!=1:return None
    row=next(iter(matches.values()));url=image(row)
    if not url and not (allow_missing_series_art and row['type']=='tvshow'):return None
    scope='movie' if row['type']=='movie' else 'series_fallback'
    credit=source+' · vorhandener Katalog; Bildnutzungsbedingungen beachten'
    if scope=='series_fallback':credit+=' · Serienbild (kein Episodenbild)'
    return dict(url=url,source=source,match='EXACT_CATALOG_MOVIE57' if scope=='movie' else 'EXACT_CATALOG_SERIES57',
                image_scope57=scope,matched_year56=number(row['year']),attribution=credit,
                alternate_urls57=[value for value in images(row) if value!=url])


def xcmate(event,cancel=lambda:False):
    from library_index import normalized,IndexReadError
    from widget_movie47 import MovieReader
    from programme_assets47 import sources
    from media_data import video_info
    rows=[];wanted=kind(event)
    if wanted=='unsupported':return None
    for group in (('vod',) if wanted=='movie' else ('series',) if wanted=='tv' else ('vod','series')):
        if cancel():raise Error('CANCELLED')
        reader=MovieReader(event['pid'],kind=group)
        try:
            reader.groups(group)
            found=reader._query('''/* direct44 */ SELECT payload FROM readable_titles
              WHERE pid=? AND kind=? AND search=? AND cid IN(SELECT cid FROM selected_categories) LIMIT 21''',
              (str(event['pid']),group,normalized(event['title'])),group)
            if len(found)>20:continue
            for raw in found:
                item=json.loads(raw['payload']);info=video_info(item);art=sources(item)
                rows.append(dict(id=str(item.get('sid','')),type='movie' if group=='vod' else 'tvshow',
                    title=info.get('title') or item.get('name',''),year=info.get('year'),art=art))
        except (IndexReadError,OSError,ValueError,TypeError):pass
        finally:reader.close()
    return choose(event,rows,'xcmate_catalog')


def kodi(event,cancel=lambda:False,rpc=call):
    wanted=kind(event);rows=[]
    if wanted=='unsupported':return None
    for group in (('movie',) if wanted=='movie' else ('tvshow',) if wanted=='tv' else ('movie','tvshow')):
        if cancel():raise Error('CANCELLED')
        method='VideoLibrary.GetMovies' if group=='movie' else 'VideoLibrary.GetTVShows'
        field='movies' if group=='movie' else 'tvshows'
        value=rpc(method,dict(properties=['title','originaltitle','year','art','uniqueid'],
            filter=dict(field='title',operator='is',value=event['title']),limits=dict(start=0,end=21)),cancel=cancel)
        found=value.get(field,[])
        if not isinstance(found,list) or len(found)>20 or value.get('limits',{}).get('total',len(found))!=len(found):continue
        for raw in found:
            if isinstance(raw,dict):rows.append(dict(raw,type=group,id=raw.get('movieid',raw.get('tvshowid'))))
    result=choose(event,rows,'kodi_library',allow_missing_series_art=True)
    if not result or result['image_scope57']=='movie':return result
    fallback=result if result['url'] else None
    if not number(event.get('season')) or not number(event.get('episode')):return fallback
    # Series launch year differs from the EPG episode year; no guessed parent.
    parent=next((v for v in rows if same_title(event['title'],v) and number(v.get('year'))==number(event.get('year'))),None)
    if not parent:return fallback
    value=rpc('VideoLibrary.GetEpisodes',dict(tvshowid=parent['id'],season=number(event['season']),
        properties=['title','showtitle','season','episode','art','uniqueid'],limits=dict(start=0,end=201)),cancel=cancel)
    found=value.get('episodes',[])
    if not isinstance(found,list) or len(found)>200 or value.get('limits',{}).get('total',len(found))!=len(found):return fallback
    matches=[v for v in found if isinstance(v,dict) and number(v.get('season'))==number(event['season']) and number(v.get('episode'))==number(event['episode']) and same_title(event['title'],v,series=True) and (not event.get('subtitle') or same_title(event['subtitle'],v))]
    if len(matches)!=1:return fallback
    choices=episode_images(matches[0],parent)
    if not choices:return fallback
    exact=dict(result,url=choices[0],match='EXACT_CATALOG_EPISODE57',image_scope57='episode',alternate_urls57=choices[1:],
                attribution='Kodi-Mediathek · exakte Serienepisode; Bildnutzungsbedingungen beachten')
    if fallback:exact['series_fallback57']=fallback
    return exact

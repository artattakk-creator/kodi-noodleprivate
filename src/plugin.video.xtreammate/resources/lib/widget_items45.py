"""One stable ListItem contract for old plugin URLs and live Home publication."""
import os
from urllib.parse import urlencode


def describe(portal,kind,row,approved,epg=None,assets47=None):
    from widget_art44 import art
    from theme_render import snapshot
    from theme_store import asset
    from media_data import recent_label
    from utils import setting_int
    import xbmcaddon
    image=art(dict(row,kind=kind),approved);theme=snapshot()
    if kind in ('live','vod','series') and assets47:
        poster=assets47.get('poster');fanart=assets47.get('fanart')
        if poster:image.update(poster=poster,thumb=poster,icon=poster)
        if fanart:image.update(fanart=fanart,landscape=fanart)
        elif poster:image['landscape']=poster
    provider80=__import__('home_publication80').capture(row,image)
    if assets47:
        from render_cache81 import record_for
        from programme_assets47 import sources,fingerprint
        for role,source in sources(row,provider_only=True).items():
            proof81=record_for(portal,kind,row,role,source)
            if proof81 and proof81.get('file')==image.get(role):
                provider80[role]=dict(source=proof81.get('source81') or fingerprint(source),uri=proof81['file'])
    supplement81=__import__('media_hero81').reference(portal,kind,row) if kind in ('vod','series') and not image.get('fanart') else ''
    if supplement81:image.update(fanart=supplement81,landscape=supplement81)
    placeholder=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media',{'live':'tv','series':'series'}.get(kind,'vod')+'.png')
    if theme:
        if image['landscape']==placeholder or image['landscape'].startswith(str(theme['folder'])+'/'):
            image['landscape']=asset('widget.live' if kind=='live' else 'widget.series' if kind=='series' else 'widget.movie',image['landscape'],snapshot=theme)
        image['banner']=asset('widget.header',snapshot=theme)
    props={'XCMate.WidgetKind41':kind,'XCMate.PortalId':str(portal['id']),'XCMate.MediaId':str(row['sid']),
           'XCMate.Account':str(portal.get('name','')),'IsPlayable':'true' if kind=='live' else 'false'}
    params=dict(action=('play_live' if portal.get('type')=='xtream' else 'source_play') if kind=='live' else 'media_detail',pid=portal['id'],sid=row['sid'])
    if kind=='live':
        from widget_focus41 import token
        params['name']=row['name'];props['XCMate.LogoScale41']='0.5';props['XCMate.WidgetToken41']=token(portal,row)
    else:params['kind']=kind
    url='plugin://plugin.video.xtreammate/?'+urlencode(params)
    props['XCMate.ClickTarget44']=url
    info=dict(title=str(row['name']),plot=str(row.get('plot') or '')[:8192],mediatype={'vod':'movie','series':'tvshow','live':'video'}[kind])
    for key in ('genre','year','rating','duration'):
        if row.get(key) is not None:info[key]=row[key]
    if kind in ('vod','series'):
        # Provider numeric strings/duration text are not Kodi InfoTag values.
        # Reuse the normal movie contract; leave the successful series path.
        from media_data import video_info
        normalized=video_info(row)
        for key in ('genre','year','rating','duration'):
            info.pop(key,None)
            if key in normalized:info[key]=normalized[key]
        cast75=normalized.get('cast')
        if isinstance(cast75,str):cast75=[v.strip() for v in cast75.split(',') if v.strip()]
        if isinstance(cast75,list):
            info['cast']=[(str(v.get('name','')) if isinstance(v,dict) else str(v))[:128] for v in cast75[:24] if isinstance(v,(str,dict))]
        director75=normalized.get('director')
        if isinstance(director75,str):info['director']=director75[:256]
        if isinstance(row.get('mpaa'),str):info['mpaa']=row['mpaa'][:64]
        genre=info.get('genre')
        if genre is not None and not (isinstance(genre,str) or isinstance(genre,list) and all(isinstance(g,str) for g in genre)):
            info.pop('genre',None)
    if epg:
        from app_routes import guide_plot
        info['plot']=epg.get('_plot45') or guide_plot(epg)
        values=dict(Now=epg['now'],Next=epg['next'],Start=epg['start'],Stop=epg['stop'],Progress=epg['progress'] if epg['progress'] is not None else '')
        props.update({'XtreamMate.'+k:str(v) for k,v in values.items()})
        props['XtreamMate.NowTime']=epg.get('now_time','');props['XtreamMate.NextTime']=epg.get('next_time','')
        props['XCMate.EpgPercent41']=str(round(epg['progress']*100)) if isinstance(epg['progress'],(int,float)) else ''
    if kind!='live':
        label=recent_label(row,setting_int('recent_days',10));props['XCMate.AddedStatus']=label
        info['plot']=label+'\n'+info['plot']
    props['XCMate.MediaHeroSource81']='TMDB' if supplement81 else 'Provider'
    if kind=='series':
        from series_art64 import inspect,note
        props['XCMate.SeriesArt64']=inspect(row,image);note(props['XCMate.SeriesArt64'])
    if kind in ('vod','series') and __import__('widget_assets69').home():
        from widget_assets69 import renderable
        image={k:(v if renderable(v) else '') for k,v in image.items()}
        props['XCMate.ArtPending69']='false' if image.get('poster') else 'true'
    value=dict(label=str(row['name']),url=url,art=image,info=info,props=props,_provider80=provider80)
    if kind=='live':
        from programme_widgets46 import decorate
        value=decorate(value,portal,row,epg or {})
        from artwork_display84 import logo_proof
        value['props']['XCMate.LogoProof84']=logo_proof(portal,row,value['props'].get('XCMate.ProgrammeLogo46',''))
    return value


def item(value):
    import xbmcgui
    li=xbmcgui.ListItem(value['label'],path=value['url'])
    li.setArt(value['art']);li.setInfo('video',value['info'])
    __import__('artwork_display84').note(value.get('props',{}).get('XCMate.WidgetKind41',''),'REFERENCE_HANDED',
        count=sum(__import__('widget_assets69').renderable(v) for v in value['art'].values()))
    for key,text in value['props'].items():li.setProperty(key,str(text))
    if value.get('menus46'):li.addContextMenuItems(value['menus46'])
    return li

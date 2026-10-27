"""One stable ListItem contract for old plugin URLs and live Home publication."""
import os
from urllib.parse import urlencode


def describe(portal,kind,row,approved,epg=None):
    from widget_art44 import art
    from theme_render import snapshot
    from theme_store import asset
    from media_data import recent_label
    from utils import setting_int
    import xbmcaddon
    image=art(row,approved);theme=snapshot()
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
    value=dict(label=str(row['name']),url=url,art=image,info=info,props=props)
    if kind=='live':
        from programme_widgets46 import decorate
        value=decorate(value,portal,row,epg or {})
    return value


def item(value):
    import xbmcgui
    li=xbmcgui.ListItem(value['label'],path=value['url'])
    li.setArt(value['art']);li.setInfo('video',value['info'])
    for key,text in value['props'].items():li.setProperty(key,str(text))
    if value.get('menus46'):li.addContextMenuItems(value['menus46'])
    return li

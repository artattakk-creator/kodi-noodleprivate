"""Station DTO exists before optional local programme/asset decoration."""
import os
import sqlite3
from urllib.parse import urlencode

def basic(portal,row,approved):
    import xbmcaddon
    from localization import tr
    from widget_focus41 import token
    from programme_assets47 import station_image
    root=xbmcaddon.Addon().getAddonInfo('path');logo=os.path.join(root,'resources','media','tv.png')
    try:
        from widget_art44 import art
        logo=art(dict(row,kind='live'),approved).get('thumb') or logo
    except (OSError,ValueError,TypeError,KeyError,RuntimeError,sqlite3.Error):
        from live_home62 import trace
        trace('RENDER','LOGO_UNAVAILABLE')
    real=logo if station_image(logo) else ''
    params=dict(action='play_live' if portal.get('type')=='xtream' else 'source_play',pid=portal['id'],sid=row['sid'],name=row['name'])
    url='plugin://plugin.video.xtreammate/?'+urlencode(params)
    props={'XCMate.WidgetKind41':'live','XCMate.PortalId':str(portal['id']),'XCMate.MediaId':row['sid'],'XCMate.Account':str(portal.get('name','')),'IsPlayable':'true','XCMate.Home50':'true','XCMate.WidgetToken41':token(portal,row),'XCMate.ClickTarget44':url,'XCMate.LogoScale41':'0.5','XCMate.ProgrammeChannel46':row['name'],'XCMate.ProgrammeLogo46':real,'XCMate.ProgrammeImage46':os.path.join(root,'resources','media','programme46','neutral.png'),'XCMate.ProgrammeTitle46':tr(36102),'XCMate.ProgrammePercent46':'0','XCMate.ProgrammeNext46':'','XCMate.ProgrammeTimes46':'','XCMate.ProgrammeDescription46':'','channellogo':real}
    return dict(label=row['name'],url=url,props=props,art=dict(icon=logo,thumb=logo,poster=logo,landscape=logo,fanart=props['XCMate.ProgrammeImage46']),info=dict(title=row['name'],plot='',mediatype='video'))

def values(portal,rows):
    from live_home62 import trace
    from widget_art44 import read
    try:approved=read(portal['id'])
    except (OSError,ValueError,TypeError):approved={}
    result=[]
    for offset in range(0,len(rows),16):
        batch=rows[offset:offset+16];base=[basic(portal,row,approved) for row in batch]
        try:
            from widget_render47 import values as decorate
            enriched=decorate(portal,'live',batch,approved)
            if len(enriched)!=len(base):raise ValueError()
            for item,value in zip(base,enriched):
                if value['props'].get('XCMate.MediaId')!=item['props']['XCMate.MediaId']:raise ValueError()
                item['props'].update({k:v for k,v in value['props'].items() if k.startswith(('XCMate.Programme','XtreamMate.'))})
                if isinstance(value.get('info',{}).get('plot'),str):item['info']['plot']=value['info']['plot'][:8192]
                if value.get('menus46'):item['menus46']=value['menus46']
        except (OSError,ValueError,TypeError,KeyError,RuntimeError,sqlite3.Error):trace('RENDER','ENRICHMENT_UNAVAILABLE',len(batch))
        result.extend(base)
    trace('RENDER','READY',len(result));return result

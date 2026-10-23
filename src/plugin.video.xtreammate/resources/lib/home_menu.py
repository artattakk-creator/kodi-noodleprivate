"""Additive 0.1.27 navigation. Existing playback/settings actions stay valid."""
from localization import tr
from boot_diagnostics import phase
import os
import uuid

HOME = ((32400,'home_start','tv.png'), (32401,'home_live','tv.png'),
        (32402,'guide_grid','epg.png'), (32403,'movies_home','vod.png'),
        (32404,'series_home','series.png'), (32405,'settings_home','settings.png'))
SETTINGS = ((32406,'accounts'), (32407,'startup'),
            (32402,'epg'), (32408,'groups'),
            (32409,'remote'), (32410,'player'),
            (32411,'storage'), (32412,'appearance'),
            (32413,'maintenance'), (32414,'about'))


def active_portal(portals, preferred=''):
    from utils import setting
    active=[p for p in portals if p.get('enabled',True)]
    chosen=preferred or setting('active_portal_id','')
    return next((p for p in active if str(p['id'])==chosen), active[0] if active else None)


@phase('HOME_MENU')
def show(router, portal):
    import xbmcplugin
    from boot_diagnostics import finish_directory
    import xbmcaddon
    path=xbmcaddon.Addon().getAddonInfo('path')
    xbmcplugin.setPluginCategory(router._handle,'XCMate · '+portal.get('name',''))
    xbmcplugin.setContent(router._handle,'files')
    from theme_render import snapshot
    from theme_store import asset
    theme=snapshot()
    for label_id,action,icon in HOME:
        label=tr(label_id)
        name={'home_start':'start','home_live':'live','guide_grid':'epg','movies_home':'movies','series_home':'series','settings_home':'settings'}[action]
        from window_navigation import WINDOW_ACTIONS,add_action
        add=add_action if action in WINDOW_ACTIONS or action=='home_start' else lambda router,*a,**kw:router._add_dir(*a,**kw)
        add(router,label,router.url(action=action,pid=portal['id']),
                        icon=__import__('branding').icon() if action=='home_start' else asset('icon.'+name,os.path.join(path,'resources','media',icon),snapshot=theme),
                        fanart=asset('background.home.'+name,os.path.join(path,'fanart.jpg'),snapshot=theme),
                        plot=(tr(32415) if action=='settings_home' else label))
    finish_directory(router,cacheToDisc=False)


def probe_directory(folder, vfs):
    """Never alter the setting until a unique temporary file round-trips."""
    if not folder or not vfs.exists(folder): return False
    token=uuid.uuid4().hex
    target=os.path.join(folder,'.xcmate-write-test-'+token)
    try:
        stream=vfs.File(target,'w')
        try:
            if not stream.write(token): return False
        finally: stream.close()
        stream=vfs.File(target)
        try: return stream.read()==token
        finally: stream.close()
    except (OSError,RuntimeError): return False
    finally:
        try: vfs.delete(target)
        except (OSError,RuntimeError): pass


def settings(router, portal, section=''):
    import xbmc, xbmcgui, xbmcplugin, xbmcaddon
    from boot_diagnostics import finish_directory
    pid=portal['id'] if portal else ''
    from theme_render import snapshot
    from theme_store import asset
    theme=snapshot()
    def add(label,action,**params):
        from window_navigation import WINDOW_ACTIONS,DIALOG_ACTIONS,add_action
        url=router.url(action=action,pid=pid,**params)
        key=section or params.get('section','')
        key={'storage':'recordings','startup':'start-channel','designs':'appearance'}.get(key,key)
        art=dict(icon=asset('icon.settings.'+key,os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources/media/settings.png'),snapshot=theme),fanart=asset('background.settings.'+key,asset('background.settings',os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'fanart.jpg'),snapshot=theme),snapshot=theme))
        if action in WINDOW_ACTIONS|DIALOG_ACTIONS or action=='global_search':
            add_action(router,label,url,**art)
        else:router._add_dir(label,url,**art)
    if not section:
        for label_id,key in SETTINGS: add(tr(label_id),'settings_section',section=key)
    elif section=='accounts':
        from portals import get_active
        add(tr(32416),'account_select')
        for p in get_active():
            add('{} · {}'.format(p.get('name',tr(32417)),p.get('type','')),'account_select',selected=p['id'])
            account_action={'xtream':'xtream_account','stb':'stb_account','m3u':'m3u_account'}.get(p.get('type'))
            if account_action:
                router._add_dir(tr(32418)+p.get('name',tr(32417)),
                                router.url(action=account_action,pid=p['id']))
        add(tr(32419),'portal_manager')
        add(tr(32420),'setup_wizard')
    elif section=='startup':
        add(tr(32421),'startup_settings')
        add(tr(32422),'autoplay_diagnostic_mode')
    elif section=='epg':
        add(tr(32423),'guide_browser')
        add(tr(32424),'epg_sources')
        add(tr(32425),'epg_status')
        add(tr(32426),'guide_status')
        add(tr(32427),'guide_timers')
        add(tr(32428),'refresh_epg')
        add(tr(32429),'settings')
    elif section=='groups':
        if portal and portal.get('type')=='m3u': add(tr(32746),'playlist_editor')
        add(tr(32430),'groups_manager')
        add(tr(32431),'favourites')
        add(tr(32432),'media_favourites',kind='vod')
        add(tr(32433),'media_favourites',kind='series')
        add(tr(32434),'global_search')
    elif section=='remote':
        add(tr(32435),'remote_learn')
        add(tr(32436),'remote_setup')
    elif section=='player':
        add(tr(32437),'settings')
    elif section=='storage':
        add(tr(32900),'art_db_health')
        add(tr(32661),'art_status')
        add(tr(32662),'art_retry')
        add(tr(32438),'recording_folder')
        add(tr(32439),'recording_folder',check='1')
        add(tr(32440),'settings')
        add(tr(32441),'recording_capabilities')
    elif section=='designs':
        add(tr(33813),'theme_manager')
    elif section=='appearance':
        add(tr(33800),'settings_section',section='designs')
        add(tr(32620),'ui_language')
        add(tr(32622),'appearance_settings')
        add(tr(32442),'settings')
        add(tr(32443),'widget_setup')
        add(tr(32444),'widget_live_start_group')
        add(tr(32445),'widget_recent_vod')
        add(tr(32446),'widget_recent_series')
    elif section=='maintenance':
        for label,action in ((tr(32447),'global_search'),(tr(32448),'refresh_portal'),
            (tr(32425),'epg_status'),(tr(32449),'remote_diagnostics'),
            (tr(32450),'service_recover'),(tr(32451),'popup_probe'),
            (tr(32452),'clear_cache'),(tr(32453),'settings')):
            add(label,action)
    elif section=='about':
        add(tr(33701),'branding_status')
        add(tr(32454),'about_xcmate')
        add(tr(33405),'xcmate_licenses')
    finish_directory(router,cacheToDisc=False)


def recording_folder(check_only=False):
    import xbmcgui, xbmcaddon, xbmcvfs
    from utils import setting
    old=setting('recordings_folder','special://profile/addon_data/plugin.video.xtreammate/recordings/')
    selected=old if check_only else xbmcgui.Dialog().browseSingle(0,tr(32455),'files',defaultt=old)
    if not selected: return
    if probe_directory(selected,xbmcvfs):
        if not check_only: xbmcaddon.Addon().setSetting('recordings_folder',selected)
        from urllib.parse import urlsplit,urlunsplit
        parts=urlsplit(selected)
        display=urlunsplit((parts.scheme,parts.hostname or '',parts.path,'','')) if parts.scheme and parts.netloc else selected
        try:
            status=os.statvfs(xbmcvfs.translatePath(selected))
            space=tr(32456).format(status.f_bavail*status.f_frsize//(1024*1024))
        except (AttributeError,OSError,RuntimeError): space=tr(32457)
        xbmcgui.Dialog().ok('XCMate',display+'\n'+space+tr(32458))
    else:
        xbmcgui.Dialog().ok('XCMate',tr(32459))

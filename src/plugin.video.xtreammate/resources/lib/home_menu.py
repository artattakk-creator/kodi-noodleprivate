"""Additive 0.1.27 navigation. Existing playback/settings actions stay valid."""
from localization import tr
from boot_diagnostics import phase
import os
import uuid

HOME = ((32400,'home_start','tv.png'), (32401,'home_live','tv.png'),
        (32402,'guide_grid','epg.png'), (32403,'movies_home','vod.png'),
        (32404,'series_home','series.png'), (32405,'settings_home','settings.png'))
from settings_sections45 import SECTIONS as SETTINGS


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
    from theme_render import snapshot,lightweight_background
    from theme_store import asset
    theme=snapshot()
    for label_id,action,icon in HOME:
        label=tr(label_id)
        name={'home_start':'start','home_live':'live','guide_grid':'epg','movies_home':'movies','series_home':'series','settings_home':'settings'}[action]
        from window_navigation import WINDOW_ACTIONS,add_action
        add=add_action if action in WINDOW_ACTIONS or action=='home_start' else lambda router,*a,**kw:router._add_dir(*a,**kw)
        add(router,label,router.url(action=action,pid=portal['id']),
                        icon=__import__('branding').icon() if action=='home_start' else asset('icon.'+name,os.path.join(path,'resources','media',icon),snapshot=theme),
                        fanart=asset('background.home.'+name,lightweight_background(),snapshot=theme),
                        plot=(tr(32415) if action=='settings_home' else label))
    # Passive native picker folder; selecting a source never writes a binding.
    router._add_dir(tr(32443),router.url(action='widget_sources49',pid=portal['id']),
                    icon=__import__('menu_icons45').icon('widget_setup'),plot=tr(36304),
                    fanart=lightweight_background())
    router._add_dir(tr(36611),router.url(action='widget_setup',pid=portal['id']),
                    icon=__import__('menu_icons45').icon('widget_setup'),plot=tr(36612),
                    fanart=lightweight_background())
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
    from settings_sections45 import render
    return render(router,portal,section)


def recording_folder(check_only=False):
    import xbmcgui, xbmcaddon, xbmcvfs
    from utils import setting
    old=setting('recordings_folder','special://profile/addon_data/plugin.video.xtreammate/recordings/')
    from storage_sources import choose as choose_source
    from storage_diagnostics import mark,kind
    selected=old if check_only else choose_source('RECORD')
    if not selected: return
    from capture_target import probe,compatible_default,TargetFailure
    from capture_ui import work
    selected=xbmcvfs.translatePath(selected)
    mark('RECORD','TARGET_PROBE',kind(selected),'NATIVE')
    try:
        result=work(lambda:probe(selected,create=True))
        if result is None:return
    except TargetFailure as exc:
        from transfer_diagnostics import describe
        mark('RECORD','FAILED',kind(selected),'NATIVE',exc)
        xbmcgui.Dialog().ok('XCMate',tr(34901)+'\n'+describe(exc)+'\n'+tr(34914));return
    if not check_only:
        xbmcaddon.Addon().setSetting('recordings_folder',selected)
        mark('RECORD','PERSIST_OK',kind(selected),'NATIVE')
    xbmcgui.Dialog().ok('XCMate',tr(34102))

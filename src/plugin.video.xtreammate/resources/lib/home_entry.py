"""Small installed-profile Home route, without importing the legacy router.

Same six items, assets, directory completion and explicit autoplay policy.
All other routes and empty profiles keep the full Router, including the wizard.
No catalogue/EPG/HTTP/hardware/migration scan on this menu path.
"""
from urllib.parse import parse_qsl,urlencode,quote
import os


class HomeRouter:
    def __init__(self,argv):
        self._handle=int(argv[1]);self._base=argv[0]
        self._params=dict(parse_qsl(argv[2].lstrip('?') if len(argv)>2 else '',keep_blank_values=True))
    def url(self,**kw):return self._base+'?'+urlencode({k:v for k,v in kw.items() if v is not None},quote_via=quote)
    def _add_dir(self,label,url,icon=None,is_folder=True,plot='',fanart=None):
        import xbmcaddon,xbmcgui,xbmcplugin
        from branding import icon as original_icon
        item=xbmcgui.ListItem(label);art=icon or original_icon()
        item.setArt(dict(icon=art,thumb=art,landscape=art,clearart=art,fanart=fanart or os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'fanart.jpg')))
        item.setInfo('video',dict(title=label,plot=plot or label))
        if not is_folder:item.setProperty('IsPlayable','true')
        xbmcplugin.addDirectoryItem(self._handle,url,item,isFolder=is_folder)


def dispatch(argv,router=None):
    router=router or HomeRouter(argv);action=router._params.get('action','root')
    if router._handle<0 or action not in ('root','portal_home','xcmate_home'):return False
    from setup_navigation import active
    if active():return False
    from boot_diagnostics import phase,mark
    mark('ROUTE',action=action)
    from window_lifecycle import route_phase
    route_phase(router,'ENTRY',action)
    try:
        with phase('HOME_PORTALS'):
            from portals import get_active
            rows=get_active()
        if not rows:return False
        from home_menu import active_portal,show
        preferred=router._params.get('pid','')
        if preferred and not any(str(row['id'])==preferred for row in rows):return False
        portal=active_portal(rows,preferred)
        with phase('ROOT_MENU'):show(router,portal)
        if action=='root':maybe_autoplay(router,portal)
        mark('HOME_SUBMITTED')  # Not a physical display/IR-readiness measurement.
        return True
    finally:route_phase(router,'RETURN',action)


def maybe_autoplay(router, portal):
    """Start the configured channel once on app entry, not on every refresh.

    The portal home is still built as the navigation fallback. A short
    cooldown protects against overlapping Kodi directory refreshes.
    """
    # Fail-safe for Android remote diagnosis: the existing per-portal
    # autoplay preference is preserved, but 0.1.16 pauses execution by
    # default. Otherwise entering a single-portal Kodi plugin always
    # starts Live TV before the modal popup can be opened.
    import xbmc,xbmcgui
    from utils import setting_bool
    from live_exit import state as live_exit_state
    if live_exit_state():return
    if setting_bool('autoplay_diagnostics_safe', True):
        xbmcgui.Window(10000).setProperty(
            'XtreamMate.AutoplayDiagnosticState',
            'PAUSIERT – XCMate Popup-Test ohne Live-TV erreichbar')
        return
    if (portal.get('type') != 'xtream' or not portal.get('autoplay_start')
            or not portal.get('start_stream_id') or xbmc.Player().isPlayingVideo()):
        return
    import time
    marker = xbmcgui.Window(10000)
    previous = marker.getProperty('XtreamMate.LastAutoplay')
    try:
        portal_id, timestamp = previous.rsplit(':', 1)
        if portal_id == str(portal['id']) and time.time()-float(timestamp) < 30:
            return
    except (ValueError, TypeError):
        pass
    marker.setProperty('XtreamMate.LastAutoplay',
                       '{}:{}'.format(portal['id'], time.time()))
    # A RunPlugin request is not a playable-item resolution. Its handler
    # must call xbmc.Player().play(), unlike the menu item's setResolvedUrl.
    xbmc.executebuiltin('RunPlugin({})'.format(
        router.url(action='play_start_direct', pid=portal['id'])))


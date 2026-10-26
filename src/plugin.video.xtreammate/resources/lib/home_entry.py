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
    if router._handle<0 or action not in ('root','portal_home','xcmate_home','app_open'):return False
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
        maybe_autoplay(router,portal)
        mark('HOME_SUBMITTED')  # Not a physical display/IR-readiness measurement.
        return True
    finally:route_phase(router,'RETURN',action)


def maybe_autoplay(router, portal):
    from app_entry import enter
    return enter(router,portal)

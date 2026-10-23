"""Action entry points retain Kodi's directory; one owner may open a window.

Kodi CGUIMediaWindow::OnClick runs a non-folder, non-playable plugin item via
RunScriptWithParams (handle -1). It does not replace the current directory.
Legacy directory URLs are anchored to Home before activation, never on Back.
"""
from contextlib import contextmanager
import os
import threading
import time
import uuid
from urllib.parse import urlsplit,parse_qs
import xbmc
import xbmcgui

DIALOG_ACTIONS=frozenset(('branding_status','theme_manager','art_status','art_retry','art_db_health','ui_language',
    'appearance_settings','settings','account_select','recording_folder','recording_capabilities','download_folder','download_capabilities',
    'xcmate_licenses','guide_timers','guide_status','about_xcmate','widget_setup','playlist_editor'))
WINDOW_ACTIONS=frozenset(('movies_home','series_home','media_detail','media_favourites','guide_browser','guide_grid'))
_local=threading.Lock()
DIALOG_ACTIONS=DIALOG_ACTIONS|frozenset(('record_now','recordings_manage'))


def trace(event,mode='',key=0,dispatch=''):
    """No route arguments, account IDs, filenames, URLs or exception messages."""
    if event not in ('ENTRY','BUSY','ANCHOR','HOME_READY','ANCHOR_TIMEOUT','OPEN','RETURN',
                     'BACK','TRANSITION','CLOSED_INPUT','FOCUS_FALLBACK','FOCUS_DEFER','FOCUS_READY','START_RECOVERED'):
        return
    values=['[XCMate][NAV] event='+event,'ms='+str(int(time.monotonic()*1000)),
            'thread='+str(threading.get_ident()),'key='+str(int(key))]
    if mode in ('landing','groups','grid','detail','seasons','episodes','guide'):values.append('mode='+mode)
    if dispatch and len(dispatch)==32 and all(c in '0123456789abcdef' for c in dispatch):values.append('dispatch='+dispatch)
    for name,fn in (('window',getattr(xbmcgui,'getCurrentWindowId',None)),
                    ('dialog',getattr(xbmcgui,'getCurrentWindowDialogId',None))):
        try: values.append(name+'='+str(int(fn())))
        except Exception: pass
    try: xbmc.log(' '.join(values),xbmc.LOGINFO)
    except Exception: pass


def add_action(router,label,url,icon=None,plot='',fanart=None):
    import xbmcplugin
    item=xbmcgui.ListItem(label)
    item.setProperty('IsPlayable','false')
    item.setInfo('video',{'title':label,'plot':plot or label})
    if icon:item.setArt({'icon':icon,'thumb':icon})
    if fanart:item.setArt({'fanart':fanart})
    xbmcplugin.addDirectoryItem(router._handle,url,item,isFolder=False)


@contextmanager
def ownership():
    """Nonblocking cross-interpreter lock; never queue another modal window."""
    locked=False;stream=None
    if _local.acquire(False):
        try:
            import fcntl
            from utils import addon_data_dir
            stream=open(os.path.join(addon_data_dir(),'.window-navigation.lock'),'a')
            fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
            locked=True
        except (ImportError,OSError):
            _local.release()
    try: yield locked
    finally:
        if stream:stream.close()
        if locked:_local.release()


def _anchor_home(router,portal,dispatch):
    """Compatibility for directory bookmarks/widgets from older installations."""
    path=xbmc.getInfoLabel('Container.FolderPath')
    current=urlsplit(path);query=parse_qs(current.query)
    if (router._handle<0 and current.netloc=='plugin.video.xtreammate' and
        query.get('action',['root'])[0] in ('root','xcmate_home','portal_home')):return True
    from home_menu import show
    if router._handle>=0:show(router,portal)  # Complete old directory once.
    destination=router.url(action='xcmate_home',pid=portal['id'],nav=dispatch)
    trace('ANCHOR',dispatch=dispatch)
    if router._handle>=0 or current.netloc=='plugin.video.xtreammate':
        xbmc.executebuiltin('Container.Update('+destination+',replace)')
    else:xbmc.executebuiltin('ActivateWindow(Videos,'+destination+',return)')
    monitor=xbmc.Monitor();deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        # FolderPath is used for equality only, never logged or persisted.
        path=xbmc.getInfoLabel('Container.FolderPath')
        query=parse_qs(urlsplit(path).query)
        if query.get('action')==['xcmate_home'] and query.get('nav')==[dispatch]:
            trace('HOME_READY',dispatch=dispatch);return True
        if monitor.waitForAbort(.05):return False
    trace('ANCHOR_TIMEOUT',dispatch=dispatch);return False


def open_route(router,portal,opener,after_close=None):
    dispatch=uuid.uuid4().hex
    trace('ENTRY',dispatch=dispatch)
    result=None
    with ownership() as acquired:
        if not acquired:
            # Existing WindowXML keeps owning input; do not replace its container.
            from boot_diagnostics import finish_directory
            finish_directory(router,succeeded=True,cacheToDisc=False)
            trace('BUSY',dispatch=dispatch);return
        if not _anchor_home(router,portal,dispatch):return
        router._navigation_dispatch=dispatch
        try:
            trace('OPEN',dispatch=dispatch)
            result=opener()
        except Exception as exc:
            from owner_dispatch import WindowStartError
            if not isinstance(exc,WindowStartError):raise
            # Home is already the underlying directory. Never recursively reload
            # the media route or close a foreign dialog to try another show().
            from localization import tr
            trace('START_RECOVERED',dispatch=dispatch)
            xbmcgui.Dialog().notification('XCMate',tr(32910))
        finally:trace('RETURN',dispatch=dispatch)

    # The native callback/pump and cross-interpreter navigation lock have ended.
    if after_close is not None and result is not None:after_close(router,portal,result)

"""Native search excursions after guide pump exit, under one navigation lease.

No search Container.Update, nested navigation lock or player dispatch in callbacks.
Only UI snapshots are retained between fresh guide instances; no profile writes.
"""
import time
import uuid
from urllib.parse import urlsplit,parse_qs
import xbmc,xbmcgui
from owner_dispatch import WindowStartError


def mark(stage,router=None,source='',session='',focus=0,owner=False):
    if stage not in ('ENTRY','DIRECTORY_READY','DIRECTORY_TIMEOUT','INTENT','CANCEL',
                     'GUIDE_CLOSED','SEARCH_OPEN','SEARCH_CLOSED','GUIDE_RESTORE','FOCUS_TIMEOUT','START_FAILED',
                     'WAIT_RELEASE','RELEASE_READY','RELEASE_TIMEOUT'):return
    if source not in ('guide','grid','route','media'):source='route'
    if len(session)!=32 or any(c not in '0123456789abcdef' for c in session):session=''
    values=['[XCMate][SEARCH_NAV] stage='+stage,'source='+source,'session='+session,
            'ms='+str(int(time.monotonic()*1000)),'focus='+str(int(focus)),'owner='+str(int(bool(owner)))]
    if router is not None:values.append('handle='+('directory' if router._handle>=0 else 'action'))
    for key,name in (('window','getCurrentWindowId'),('dialog','getCurrentWindowDialogId')):
        try:values.append(key+'='+str(int(getattr(xbmcgui,name)())))
        except (AttributeError,RuntimeError,TypeError,ValueError):pass
    try:xbmc.log(' '.join(values),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def anchor(router,portal,dispatch):
    mark('ENTRY',router,session=dispatch,owner=True)
    if router._handle<0:
        from window_navigation import _anchor_home
        return _anchor_home(router,portal,dispatch)
    # Fulfil the original directory with the complete branded Home exactly once.
    # Do not issue a second Home update while Kodi is completing this request.
    from home_menu import show
    show(router,portal)
    deadline=time.monotonic()+5;monitor=xbmc.Monitor()
    while time.monotonic()<deadline:
        path=urlsplit(xbmc.getInfoLabel('Container.FolderPath'))
        if (path.netloc=='plugin.video.xtreammate' and parse_qs(path.query).get('action')==['global_search']
                and not xbmc.getCondVisibility('Container.IsUpdating')):
            # Let the directory's GUI message finish before WindowXML.show().
            if monitor.waitForAbort(.05):return False
            if xbmc.getCondVisibility('Container.IsUpdating'):continue
            mark('DIRECTORY_READY',router,session=dispatch,owner=True);return True
        if monitor.waitForAbort(.05):return False
    mark('DIRECTORY_TIMEOUT',router,session=dispatch,owner=True);return False


def queue(window,source):
    if window._closed or window._leaving or window._search_prompt:return
    from localization import tr
    window._search_prompt=True
    try:query=xbmcgui.Dialog().input(tr(32534))
    finally:window._search_prompt=False
    query=str(query or '').strip()[:200]
    if not query:
        mark('CANCEL',window.router,source,focus=window.getFocusId(),owner=True);return
    fields=(('category','offset','row','cursor','origin','mode','groups','_focus_zone','_header','_views','_group_return')
            if source=='grid' else ('category','day','channel_offset','event_offset'))
    view={name:getattr(window,name) for name in fields}
    if source=='guide':
        view.update(channel_pos=window.getControl(210).getSelectedPosition(),
                    event_pos=window.getControl(220).getSelectedPosition(),focus=window.getFocusId())
    try:native_window=int(xbmcgui.getCurrentWindowId())
    except (AttributeError,RuntimeError,TypeError,ValueError):native_window=None
    window._search_request=dict(query=query,session=uuid.uuid4().hex,view=view,window=native_window)
    mark('INTENT',window.router,source,window._search_request['session'],window.getFocusId(),True)
    window._generation+=1
    if window._pending_future is not None:window._pending_future.cancel()
    window._pending_future=None;window._pending_apply=None
    window._leaving=True;window._leave_after=time.monotonic()+.15


def released(router,source,session,window_id):
    # Window.close() may still have an outstanding native GUI message. A Python
    # _closed flag alone is not proof that the old Kodi window has deactivated.
    mark('WAIT_RELEASE',router,source,session,owner=True)
    monitor=xbmc.Monitor();deadline=time.monotonic()+2
    while True:
        if monitor.waitForAbort(.05):return False
        try:active=window_id is not None and int(xbmcgui.getCurrentWindowId())==window_id
        except (AttributeError,RuntimeError,TypeError,ValueError):active=False
        if not active and not xbmc.getCondVisibility('System.HasActiveModalDialog'):
            mark('RELEASE_READY',router,source,session,owner=True);return True
        if time.monotonic()>=deadline:
            mark('RELEASE_TIMEOUT',router,source,session,owner=True);return False


def guide_flow(router,portal,open_window,window_class,xml,source):
    view=None
    while True:
        window=open_window(window_class,xml,router,portal,**({'return_view':view} if view is not None else {}))
        request=getattr(window,'_search_request',None)
        if request is None:return getattr(window,'_play_request',None)
        if not window._closed or getattr(window,'_running',False):return None
        view=request['view']
        session=request['session']
        mark('GUIDE_CLOSED',router,source,session,owner=True)
        del window
        if not released(router,source,session,request.get('window')):return None
        from media_window import open_search
        mark('SEARCH_OPEN',router,source,session,owner=True)
        try:search=open_search(router,portal,request['query'],session)
        except WindowStartError:
            mark('START_FAILED',router,source,session,owner=True)
            from localization import tr
            xbmcgui.Dialog().notification('XCMate',tr(32910))
            if xbmc.Monitor().waitForAbort(0):return None
            continue
        if not search._closed or getattr(search,'_running',False):return None
        intent=getattr(search,'_search_live',None)
        native_window=getattr(search,'_search_native_window',None)
        mark('SEARCH_CLOSED',router,source,session,owner=True)
        del search
        if intent:return intent  # Existing caller dispatches only AFTER unlocking.
        if not released(router,source,session,native_window):return None
        mark('GUIDE_RESTORE',router,source,session,owner=True)

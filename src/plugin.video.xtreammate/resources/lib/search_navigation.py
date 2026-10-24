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
                     'WAIT_RELEASE','RELEASE_READY','RELEASE_TIMEOUT','BUSY_DEFERRED','ASYNC_QUEUED',
                     'ASYNC_READY','BLOCK_FOREIGN','BLOCK_CONTEXT','BLOCK_OWNER','BLOCK_STALE','ASYNC_FAILED'):return
    if source not in ('guide','grid','route','media'):source='route'
    if len(session)!=32 or any(c not in '0123456789abcdef' for c in session):session=''
    values=['[XCMate][SEARCH_NAV] stage='+stage,'source='+source,'session='+session,
            'ms='+str(int(time.monotonic()*1000)),'focus='+str(int(focus)),'owner='+str(int(bool(owner)))]
    if router is not None:values.append('handle='+('directory' if router._handle>=0 else 'action'))
    for key,name in (('window','getCurrentWindowId'),('dialog','getCurrentWindowDialogId')):
        try:values.append(key+'='+str(int(getattr(xbmcgui,name)())))
        except (AttributeError,RuntimeError,TypeError,ValueError):pass
    from window_lifecycle import lease,state
    snapshot=state();values.extend(('lease='+lease(),'updating='+str(int(snapshot['updating']))))
    reason=getattr(router,'_search_block_reason','') if router else ''
    if reason in ('BUSY_REENTRANT','FOREIGN_MODAL','WINDOW_ACTIVE','SESSION_CHANGED','CONTAINER_CHANGED','ABORT'):values.append('reason='+reason)
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
    if busy_dialog():return True
    deadline=time.monotonic()+5;monitor=xbmc.Monitor()
    while time.monotonic()<deadline:
        path=urlsplit(xbmc.getInfoLabel('Container.FolderPath'))
        if (path.netloc=='plugin.video.xtreammate' and parse_qs(path.query).get('action')==['global_search']
                and not xbmc.getCondVisibility('Container.IsUpdating')):
            # Let the directory's GUI message finish before WindowXML.show().
            if monitor.waitForAbort(.05):return False
            if busy_dialog():return True
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
    from window_lifecycle import capture
    native_window=capture(window)
    window._search_request=dict(query=query,session=uuid.uuid4().hex,view=view,window=native_window)
    mark('INTENT',window.router,source,window._search_request['session'],window.getFocusId(),True)
    window._generation+=1
    if window._pending_future is not None:window._pending_future.cancel()
    window._pending_future=None;window._pending_apply=None
    window._leaving=True;window._leave_after=time.monotonic()+.15


def busy_dialog():
    try:return int(xbmcgui.getCurrentWindowDialogId())==10138 and xbmc.getCondVisibility('System.HasActiveModalDialog')
    except (AttributeError,RuntimeError,TypeError,ValueError):return False


def open_root(router,portal):
    session=getattr(router,'_navigation_dispatch','')
    if busy_dialog() and not getattr(router,'_search_async_owner',False):
        from search_handoff import SearchTransfer
        return SearchTransfer(router,portal,dict(query=router._params.get('q'),session=session,window=None,view=None),'route')
    from media_window import open_search
    return open_search(router,portal,router._params.get('q'),session)


def released(router,source,session,window_id):
    # Window.close() may still have an outstanding native GUI message. A Python
    # _closed flag alone is not proof that the old Kodi window has deactivated.
    mark('WAIT_RELEASE',router,source,session,owner=True)
    monitor=xbmc.Monitor();deadline=time.monotonic()+2
    while True:
        if monitor.waitForAbort(.05):
            router._search_block_reason='ABORT';return False
        from window_lifecycle import active as frame_active,state
        snapshot=state();active=frame_active(window_id,snapshot)
        router._search_block_reason=('WINDOW_ACTIVE' if active else 'BUSY_REENTRANT' if snapshot['dialog']==10138 else 'FOREIGN_MODAL' if snapshot['modal'] else 'CONTAINER_CHANGED' if snapshot['updating'] else '')
        if not active and busy_dialog() and not getattr(router,'_search_async_owner',False):
            mark('BUSY_DEFERRED',router,source,session,owner=True);return False
        if not active and not snapshot['modal'] and not snapshot['updating']:
            mark('RELEASE_READY',router,source,session,owner=True);return True
        if time.monotonic()>=deadline:
            mark('RELEASE_TIMEOUT',router,source,session,owner=True);return False


def guide_flow(router,portal,open_window,window_class,xml,source,initial=None):
    view=None;request=initial
    while True:
        if request is None:
            window=open_window(window_class,xml,router,portal,**({'return_view':view} if view is not None else {}))
            request=getattr(window,'_search_request',None)
            if request is None:return getattr(window,'_play_request',None)
            if not window._closed or getattr(window,'_running',False):return None
            mark('GUIDE_CLOSED',router,source,request['session'],owner=True)
            del window
        view=request['view'];session=request['session']
        if request.get('restore_only'):
            request=None;continue
        if not released(router,source,session,request.get('window')):
            if busy_dialog() and not getattr(router,'_search_async_owner',False):
                from search_handoff import SearchTransfer
                return SearchTransfer(router,portal,request,source)
            return None
        from media_window import open_search
        mark('ASYNC_READY',router,source,session,owner=True)
        mark('SEARCH_OPEN',router,source,session,owner=True)
        try:search=open_search(router,portal,request['query'],session)
        except WindowStartError:
            mark('START_FAILED',router,source,session,owner=True)
            from localization import tr
            xbmcgui.Dialog().notification('XCMate',tr(32910))
            if xbmc.Monitor().waitForAbort(0):return None
            request=None;continue
        if not search._closed or getattr(search,'_running',False):return None
        intent=getattr(search,'_search_live',None)
        native_window=getattr(search,'_search_native_window',None)
        mark('SEARCH_CLOSED',router,source,session,owner=True)
        del search
        if intent:return intent  # Existing caller dispatches only AFTER unlocking.
        if not released(router,source,session,native_window):
            if busy_dialog() and not getattr(router,'_search_async_owner',False):
                from search_handoff import SearchTransfer
                request=dict(request,restore_only=True,window=native_window)
                return SearchTransfer(router,portal,request,source)
            return None
        request=None
        mark('GUIDE_RESTORE',router,source,session,owner=True)


def focus_details(window,target,eligible,valid):
    """Changed fixed focus state only; no labels, queries or account metadata."""
    try:
        control=window.getControl(target)
        state=(int(target),target in eligible,bool(control.isVisible()),
               bool(xbmc.getCondVisibility('Control.IsEnabled({})'.format(target))),int(window.getFocusId()))
        if state==getattr(window,'_search_focus_trace',None):return
        window._search_focus_trace=state
        session=getattr(window,'_search_correlation','')
        if len(session)!=32 or any(c not in '0123456789abcdef' for c in session):session=''
        xbmc.log('[XCMate][FOCUS] mode=search target={} semantic={} visible={} enabled={} focus={} session={}'.format(
            state[0],int(state[1]),int(state[2]),int(state[3]),state[4],session),xbmc.LOGINFO)
    except (AttributeError,RuntimeError,TypeError,ValueError,KeyError):pass

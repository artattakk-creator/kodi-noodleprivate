"""Offer a reviewed Home adapter update and require explicit Kodi approval."""

import threading
import time
from xml.etree.ElementTree import ParseError

_lock=threading.Lock()
_pending=None
_done=False
_next=0


def prepare():
    global _pending,_next
    if _done or time.monotonic()<_next:return
    with _lock:
        if _pending is not None:return
    _next=time.monotonic()+60
    import xbmcgui
    from epg_handoff63 import profile_scope
    from skin_patch103 import log_error
    from utils import setting,setting_bool
    from widget_manager50 import runtime
    from widget_skin50 import applied,prepare as make
    from widget_skin75 import previously_applied
    from widget_skin77 import inspect
    from widget_skin78 import previous_owned,supported
    from widget_skin103 import installed,previous_owned as previous103

    try:profile,skin=runtime()
    except (OSError,ValueError,RuntimeError):return
    marker=xbmcgui.Window(10000)
    marker.clearProperty('XCMate.Home78.Apply')
    full_graph=supported(skin)
    if not full_graph and applied(skin):return
    if full_graph and installed(skin):
        from home_activation78 import KEY,request
        if not marker.getProperty(KEY):request('installed78')
        return
    if setting_bool('home78_repair_optout',False) or setting('bingie_hero63_notice','')=='0.1.29.103':
        return
    owned = (full_graph and (previous103(skin) or previous_owned(skin) or __import__('widget_skin88').previous_owned(skin)))
    if not owned and not previously_applied(skin) and inspect().get('code')!='ADAPTER_APPROVAL_REQUIRED':
        return

    scope=profile_scope()
    try:plan=make(skin)
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,ParseError) as exc:
        log_error(exc,'layout')
        return
    with _lock:
        _pending=dict(profile=profile,skin=skin,plan=plan,scope=scope)


def poll():
    global _pending,_done
    import xbmc,xbmcaddon,xbmcgui
    from epg_handoff63 import profile_scope
    from skin_patch103 import confirm,show_error
    from widget_manager50 import install_skin

    if _done or xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):
        return
    if xbmc.getCondVisibility('Player.HasMedia') or xbmc.getCondVisibility('System.HasActiveModalDialog'):
        return
    with _lock:
        pending=_pending
        _pending=None
    if pending is None or pending.get('scope')!=profile_scope():return

    _done=True
    dialog=xbmcgui.Dialog()
    try:
        approved=confirm(dialog,pending['plan'])
        if pending.get('scope')!=profile_scope():return
        if approved:
            install_skin(pending['plan'],pending['profile'],pending['skin'],dialog)
        xbmcaddon.Addon().setSetting('bingie_hero63_notice','0.1.29.103')
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,ParseError) as exc:
        show_error(dialog,exc,'preview')

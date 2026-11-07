"""One visible exact-adapter upgrade; installation/update never writes skin XML."""
import threading,time
_lock=threading.Lock();_pending=None;_done=False;_next=0

def prepare():
    global _pending,_next
    import xbmcgui
    marker=xbmcgui.Window(10000);requested78=marker.getProperty('XCMate.Home78.Apply')
    if requested78:
        marker.clearProperty('XCMate.Home78.Apply')
        try:
            from widget_manager50 import runtime,rebuild,trace
            from widget_skin50 import apply
            from widget_transaction50 import load
            profile,skin=runtime();plan78=load(requested78,'skin')
            from widget_skin78 import previous_owned
            if not previous_owned(skin):return
            apply(requested78,skin,confirmed=True);trace('SKIN_FILES_VERIFIED');rebuild()
        except (OSError,ValueError,RuntimeError,KeyError):pass
        return
    if _done or time.monotonic()<_next:return
    with _lock:
        if _pending is not None:return
    _next=time.monotonic()+60
    try:
        from utils import setting
        if setting('bingie_hero63_notice','')=='0.1.29.78':return
        from widget_manager50 import runtime
        from widget_skin50 import applied,prepare as make
        from widget_skin75 import previously_applied
        from widget_skin77 import inspect as inspect77
        profile,skin=runtime()
        if applied(skin):return
        from widget_skin78 import supported,installed,previous_owned
        if supported(skin) and installed(skin):
            # A restart can lose the RAM receipt after files were committed.
            # Recheck only own consumers; do not reapply the skin transaction.
            from home_activation78 import KEY,request
            if not marker.getProperty(KEY):request('installed78')
            return
        automatic78=supported(skin) and previous_owned(skin) and not __import__('utils').setting_bool('home78_repair_optout',False)
        if not automatic78 and not previously_applied(skin) and inspect77().get('code')!='ADAPTER_APPROVAL_REQUIRED':return
        plan=make(skin)
        from widget_skin60 import preview
        text=preview(plan).replace('(.60)','(.78)')
        from epg_handoff63 import profile_scope
        with _lock:_pending=dict(profile=profile,skin=skin,plan=plan,text=text,scope=profile_scope(),automatic78=automatic78)
    except (OSError,ValueError,KeyError,TypeError,RuntimeError):pass

def poll():
    global _pending,_done
    import xbmc,xbmcgui,xbmcaddon
    if _done or xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
    if xbmc.getCondVisibility('Player.HasMedia'):return
    # Offer new Home integration only while one of our native rows is focused.
    # Existing bindings/settings are preserved; no patch without confirmation.
    with _lock:automatic78=bool(_pending and _pending.get('automatic78'))
    if not automatic78 and xbmc.getInfoLabel('ListItem.Property(XCMate.WidgetKind41)') not in ('live','vod','series'):return
    with _lock:pending=_pending;_pending=None
    if pending is None:return
    from epg_handoff63 import profile_scope
    if pending.get('scope')!=profile_scope():return
    _done=True
    if pending.get('automatic78'):
        xbmcgui.Window(10000).setProperty('XCMate.Home78.Apply',pending['plan']['id']);return
    from localization import tr
    dialog=xbmcgui.Dialog()
    dialog.textviewer(tr(36669),tr(36670)+'\n\n'+pending['text'])
    confirmed=dialog.yesno(tr(36669),tr(36671),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10))
    if pending.get('scope')!=profile_scope():return
    xbmcaddon.Addon().setSetting('bingie_hero63_notice','0.1.29.78')
    if not confirmed:return
    from widget_manager50 import runtime,rebuild,trace,error
    try:
        from widget_skin50 import apply
        profile,skin=runtime()
        if profile!=pending['profile'] or skin!=pending['skin']:raise ValueError('PROFILE_CHANGED')
        apply(pending['plan']['id'],skin,confirmed=True)
        trace('SKIN_PATCH_VERIFIED');rebuild();dialog.notification('XCMate',tr(36415))
    except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:error(exc)

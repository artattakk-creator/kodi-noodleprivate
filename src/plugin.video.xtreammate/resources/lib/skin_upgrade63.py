"""One visible exact-adapter upgrade; installation/update never writes skin XML."""
import threading,time
_lock=threading.Lock();_pending=None;_done=False;_next=0

def prepare():
    global _pending,_next
    if _done or time.monotonic()<_next:return
    _next=time.monotonic()+60
    try:
        from utils import setting
        if setting('bingie_hero63_notice','')=='0.1.29.63':return
        from widget_manager50 import runtime
        from widget_skin50 import applied,prepare as make
        from widget_skin63 import previously_applied
        profile,skin=runtime()
        if applied(skin) or not previously_applied(skin):return
        plan=make(skin)
        from widget_skin60 import preview
        text=preview(plan).replace('(.60)','(.63)')
        with _lock:_pending=dict(profile=profile,skin=skin,plan=plan,text=text)
    except (OSError,ValueError,KeyError,TypeError,RuntimeError):pass

def poll():
    global _pending,_done
    import xbmc,xbmcgui,xbmcaddon
    if _done or xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
    if xbmc.getCondVisibility('Player.HasMedia'):return
    with _lock:pending=_pending;_pending=None
    if pending is None:return
    _done=True
    from localization import tr
    dialog=xbmcgui.Dialog()
    dialog.textviewer(tr(36669),tr(36670)+'\n\n'+pending['text'])
    confirmed=dialog.yesno(tr(36669),tr(36671),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10))
    xbmcaddon.Addon().setSetting('bingie_hero63_notice','0.1.29.63')
    if not confirmed:return
    from widget_manager50 import runtime,rebuild,trace,error
    try:
        from widget_skin50 import apply
        profile,skin=runtime()
        if profile!=pending['profile'] or skin!=pending['skin']:raise ValueError('PROFILE_CHANGED')
        apply(pending['plan']['id'],skin,confirmed=True)
        trace('SKIN_PATCH_VERIFIED');rebuild();dialog.notification('XCMate',tr(36415))
    except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:error(exc)

"""RAM-only GUI notification bridge; all skin/profile/frame IO stays in worker."""
import hashlib,json,threading,time
_lock=threading.Lock();_pending={};_hooks={};_seen={};_focus=None;_next=0


def prepare(portal,kind,signature,count):
    from widget_hooks45 import read
    state=read();hooks=[]
    for binding in state.get('bindings',[])[:96]:
        if binding.get('pid')==str(portal['id']) and binding.get('kind')==kind:
            hooks.extend(h for h in binding.get('hooks',[]) if h.startswith('XCMate.Widget45.Reload.') or h in ('widgetreload','widgetreload2','widgetreloadmovies','widgetreloadtvshows'))
    with _lock:
        _hooks[(str(portal['id']),kind)]=hooks
        _pending[(str(portal['id']),kind)]=(signature,count)


def poll():
    global _next,_focus
    from hero_epg63 import poll as hero63
    from skin_upgrade63 import poll as upgrade63
    hero63();upgrade63()
    import xbmc,xbmcgui
    if time.monotonic()<_next:return
    _next=time.monotonic()+1
    if xbmc.getSkinDir()!='skin.titan.bingie.mod' or xbmcgui.getCurrentWindowId()!=10000:return
    if xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
    from widget_home_probe59 import poll as observe_home59
    observe_home59()
    if xbmc.getCondVisibility('Player.HasMedia'):return
    # Kodi's selected ListItem is already a RAM object. Never perform a source,
    # DNS, SQLite or disk query when IR focus changes.
    url=xbmc.getInfoLabel('ListItem.Property(XCMate.ProgrammeDetails46)')
    if isinstance(url,str) and len(url)<2048 and url.startswith('plugin://plugin.video.xtreammate/'):
        with _lock:_focus=url
    from widget_refresh45 import trace
    with _lock:pending=dict(_pending);hooks={k:list(v) for k,v in _hooks.items()}
    changes={}
    for key,(signature,count) in pending.items():
        if not hooks.get(key):trace('BLOCKED_NO_RELOAD_HOOK',key[1],count)
        for hook in hooks.get(key,[]):changes.setdefault(hook,[]).append((key[0],key[1],signature,count))
    now=time.monotonic();window=xbmcgui.Window(10000)
    for hook,values in changes.items():
        signature=hashlib.sha256(json.dumps(sorted(values)).encode()).hexdigest();old=_seen.get(hook)
        if old and (old[0]==signature or now-old[1]<60):continue
        window.setProperty(hook,signature);_seen[hook]=(signature,now)
        for _,kind,_,count in values:trace('UPDATED',kind,count)


def focused():
    """Drain the legacy hint; focused ListItems already contain the final URL.

    Focus must not become a second metadata resolver, even on a worker. The
    rotating background prefetcher handles NOW/NEXT independently of input.
    """
    global _focus
    with _lock:_focus=None

"""RAM-only GUI notification bridge; all skin/profile/frame IO stays in worker."""
import hashlib,json,threading,time
_lock=threading.Lock();_pending={};_hooks={};_seen={};_focus=None;_next=0
_art_counts84={};_art_seen84={};_manual_seen86={}


def prepare(portal,kind,signature,count,art_count84=None):
    from widget_hooks45 import read
    state=read();hooks=[]
    for binding in state.get('bindings',[])[:96]:
        if binding.get('pid')==str(portal['id']) and binding.get('kind')==kind:
            hooks.extend(h for h in binding.get('hooks',[]) if h.startswith('XCMate.Widget45.Reload.') or h in ('widgetreload','widgetreload2','widgetreloadmovies','widgetreloadtvshows'))
    with _lock:
        _hooks[(str(portal['id']),kind)]=hooks
        _pending[(str(portal['id']),kind)]=(signature,count)
        if type(art_count84) is int:
            from widget_data41 import policy
            _art_counts84[(str(portal['id']),kind)]=(policy(portal,kind),max(0,art_count84))


def poll():
    from home_activation78 import poll as activation78
    activation78()
    global _next,_focus
    from hero_epg63 import poll as hero63
    from skin_upgrade63 import poll as upgrade63
    hero63();upgrade63()
    from home_schedule75 import observe
    observe()
    import xbmc,xbmcgui
    if time.monotonic()<_next:return
    _next=time.monotonic()+1
    if xbmc.getSkinDir()!='skin.titan.bingie.mod' or xbmcgui.getCurrentWindowId()!=10000:return
    if xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
    from widget_home_probe59 import poll as observe_home59
    observe_home59()
    __import__('widget_runtime79').poll()
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
        newly_visible84=[]
        if __import__('artwork_display84').enabled():
            for pid,kind,_,_ in values:
                scope84,images84=_art_counts84.get((pid,kind),('',0));key84=(hook,pid,kind,scope84)
                if scope84 and images84>0 and not _art_seen84.get(key84):newly_visible84.append(key84)
        if old and old[0]==signature:continue
        from work_requests86 import manual_slot
        manual86=[(str(pid),kind,window.getProperty(manual_slot(pid,kind))) for pid,kind,_,_ in values if kind in ('vod','series')]
        changed_manual86=any(token and _manual_seen86.get((hook,pid,kind))!=token for pid,kind,token in manual86)
        if __import__('widget_patch85').publication(hook,values):
            _seen[hook]=(signature,old[1] if old else now)
            for pid,kind,token in manual86:_manual_seen86[(hook,pid,kind)]=token
            for _,kind,_,count in values:trace('UPDATED',kind,count)
            continue
        if old and now-old[1]<60 and not newly_visible84 and not changed_manual86:continue
        window.setProperty(hook,signature);_seen[hook]=(signature,now)
        for pid,kind,token in manual86:_manual_seen86[(hook,pid,kind)]=token
        while len(_manual_seen86)>128:_manual_seen86.pop(next(iter(_manual_seen86)))
        __import__('widget_patch85').sent(hook,values)
        for key84 in newly_visible84:_art_seen84[key84]=True
        while len(_art_seen84)>96:_art_seen84.pop(next(iter(_art_seen84)))
        for _,kind,_,count in values:trace('UPDATED',kind,count)


def focused():
    """Drain the legacy hint; focused ListItems already contain the final URL.

    Focus must not become a second metadata resolver, even on a worker. The
    rotating background prefetcher handles NOW/NEXT independently of input.
    """
    global _focus
    with _lock:_focus=None

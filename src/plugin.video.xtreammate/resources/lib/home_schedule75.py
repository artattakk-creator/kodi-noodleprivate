"""Shared Home admission gates over existing workers, never another loader.

A verified published image/fallback page may admit the next background phase.
Only native receiver observations record VISIBLE_READY. A focused item bypasses automatic gates;
it never resets the Live -> Movies -> Series ordering or starts a bulk scan.
"""
import hashlib,json,time,threading
KEY='XCMate.Home75.Schedule'
FOCUS='XCMate.Home75.Focus'
_seen={}
_lock=threading.RLock()

def _window():
    import xbmcgui
    return xbmcgui.Window(10000)

def _read(key):
    try:
        raw=_window().getProperty(key)
        value=json.loads(raw) if raw and len(raw)<8192 else {}
        return value if isinstance(value,dict) else {}
    except (ValueError,TypeError,AttributeError,RuntimeError):return {}

def trace(stage,**facts):
    allowed={'START_GROUP_KNOWN','LIVE_HOME_READY','MOVIE_WARM_BEGIN','MOVIES_PREPARED',
             'MOVIES_VISIBLE_READY','SERIES_WARM_BEGIN','SERIES_PREPARED','SERIES_VISIBLE_READY',
             'REST_WARM_BEGIN','MOVIES_DISABLED','SERIES_DISABLED','FOCUS_OVERRIDE','VISIBLE5_QUEUED','RENDER_PENDING','RENDER_CONTROL_MISSING'}
    if stage not in allowed:return
    safe={k:v for k,v in facts.items() if k in ('elapsed_ms','count','phase','queue_depth') and type(v) in (int,float)}
    signature=(stage,tuple(safe.items()));now=time.monotonic()
    if now-_seen.get(signature,-1e9)<30:return
    _seen[signature]=now
    while len(_seen)>64:_seen.pop(next(iter(_seen)))
    import xbmc
    try:xbmc.log('[XCMate][HOME75] stage='+stage+' '+json.dumps(safe,separators=(',',':')),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass

def configure(portals):
    from live_warm68 import portal_key
    from epg_handoff63 import profile_scope,meta_key
    from epg_status import revision
    material=[76,profile_scope(),[(portal_key(p),revision(p['id']),_window().getProperty(meta_key(p['id'])),
              p.get('include_vod',True),p.get('include_series',True)) for p in portals]]
    context=hashlib.sha256(json.dumps(material,sort_keys=True).encode()).hexdigest()
    with _lock:
        current=_read(KEY)
        if current.get('context')!=context:
            current=dict(context=context,phase=0,at=time.monotonic(),profile=profile_scope(),prepared=[],visible=[],ready76={},
                         required76={kind:[str(p['id']) for p in portals if p.get('include_'+kind,True)] for kind in ('vod','series')})
            _window().setProperty(KEY,json.dumps(current));trace('START_GROUP_KNOWN',phase=0)
        return current

def _advance(current):
    for kind,target in (('vod',2),('series',3)):
        required=current.get('required76',{}).get(kind)
        if required is None or current.get('phase',0)!=target-1:continue
        receipts=current.get('ready76',{}).get(kind,{})
        if any(pid not in receipts for pid in required):continue
        current['phase']=target
        if required:
            if kind not in current['prepared']:
                current['prepared'].append(kind)
                trace('MOVIES_PREPARED' if kind=='vod' else 'SERIES_PREPARED',count=sum(receipts[p]['count'] for p in required))
        else:trace('MOVIES_DISABLED' if kind=='vod' else 'SERIES_DISABLED',count=0)
        if target==3:trace('REST_WARM_BEGIN',phase=3)


def applicable():
    # Automatic warming must also be gated during the splash/startup window,
    # not merely after Home has already become active.
    try:
        import xbmc
        return xbmc.getSkinDir()=='skin.titan.bingie.mod'
    except (AttributeError,RuntimeError):return False

def focus():
    from epg_handoff63 import profile_scope
    value=_read(FOCUS)
    return value if value.get('profile')==profile_scope() and 0<=time.monotonic()-value.get('at',0)<2 else {}

def visible_position(pid,default=0):
    value=focus()
    return value.get('left',default) if value.get('pid')==pid and value.get('kind')=='live' else default

def allowed(kind,portal=None):
    if kind=='live' or not applicable():return True
    value=_read(KEY)
    return value.get('phase',0)>=(1 if kind=='vod' else 2)

def rest_allowed():return not applicable() or _read(KEY).get('phase',0)>=3

def focused_rows(portal,kind,rows):
    value=focus()
    if value.get('kind')!=kind or value.get('pid')!=str(portal['id']):return []
    selected=[row for row in rows if str(row.get('sid'))==value.get('sid')]
    if selected:trace('FOCUS_OVERRIDE',count=1)
    return selected[:1]

def prepared(kind,count,portal=None,rows=None):
    """Admit only a verified published page, including an honest neutral fallback.

    The old count-only call remains insufficient. Image/file validation happens
    in the existing data worker, outside the short receipt lock.
    """
    from epg_handoff63 import profile_scope
    value=_read(KEY)
    if kind not in ('vod','series') or not portal or rows is None or value.get('profile')!=profile_scope():return False
    from home_prepared76 import proof
    checked=proof(portal,kind,rows)
    if checked is None or checked['count']!=count:return False
    with _lock:
        current=_read(KEY)
        if current.get('context')!=value.get('context') or current.get('profile')!=profile_scope():return False
        pid=str(portal['id'])
        if pid not in current.get('required76',{}).get(kind,[]):return False
        current.setdefault('ready76',{}).setdefault(kind,{})[pid]=checked
        _advance(current);_window().setProperty(KEY,json.dumps(current))
    return True


def observe():
    """UI-safe: read native selected item, geometry and rendered label controls.

    Visibility/labels are receiver evidence, not HTTP or pixel-decode claims.
    Final pixel/texture acceptance is recorded by native tests and Android gates.
    """
    import xbmc,xbmcgui
    from epg_handoff63 import profile_scope
    if not applicable() or xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
    window=_window();kind=xbmc.getInfoLabel('ListItem.Property(XCMate.WidgetKind41)')
    if kind not in ('live','vod','series'):return
    pid=xbmc.getInfoLabel('ListItem.Property(XCMate.PortalId)');sid=xbmc.getInfoLabel('ListItem.Property(XCMate.MediaId)')
    if not pid or not sid:return
    try:
        ident=window.getFocusId()
        pos=int(xbmc.getInfoLabel('Container('+str(ident)+').Position') or 0)
        absolute=int(xbmc.getInfoLabel('Container('+str(ident)+').CurrentItem') or 0)
    except (AttributeError,RuntimeError,ValueError):return
    value=dict(profile=profile_scope(),pid=pid,sid=sid,kind=kind,at=time.monotonic())
    if absolute>0:value['left']=max(0,absolute-1-pos)
    window.setProperty(FOCUS,json.dumps(value))
    try:
        from home_runtime77 import control
        image=control(window,296751);title=control(window,296752 if kind=='live' else 296754)
        x,y=image.getPosition();width=image.getWidth();height=image.getHeight()
        title_id=296752 if kind=='live' else 296754
        rendered=bool(xbmc.getInfoLabel('Control.GetLabel('+str(title_id)+')')) and xbmc.getCondVisibility('Control.IsVisible('+str(title_id)+')')
        geometry=100<=x<=300 and 0<=y<=100 and 1000<=width<=1250 and 450<=height<=610
    except (AttributeError,RuntimeError,ValueError):
        window.setProperty('XCMate.Home75.RenderProbe','CONTROL_UNAVAILABLE')
        trace('RENDER_CONTROL_MISSING');return
    window.setProperty('XCMate.Home75.RenderProbe',json.dumps(dict(geometry=geometry,rendered=rendered,x=x,y=y,width=width,height=height)))
    if not rendered or not geometry:return
    with _lock:
        current=_read(KEY)
        if not current or current.get('profile')!=profile_scope():return
        if kind=='live' and current.get('phase',0)==0:current['phase']=1
        stage={'live':'LIVE_HOME_READY','vod':'MOVIES_VISIBLE_READY','series':'SERIES_VISIBLE_READY'}[kind]
        if kind not in current.setdefault('visible',[]):
            current['visible'].append(kind)
            trace(stage,phase=current.get('phase',0),elapsed_ms=int((time.monotonic()-current.get('at',time.monotonic()))*1000))
        _advance(current);window.setProperty(KEY,json.dumps(current))

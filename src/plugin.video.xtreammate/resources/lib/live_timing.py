"""Numeric latency events. No URLs, titles, portal IDs or session nonces in logs.

Menu receipt is the plugin route boundary, not a physical IR timestamp. Player
video/time state is observable here; decoder output/first screen frame is not.
"""
import json
import time
import uuid

KEY='XCMate.LiveTiming'
PHASES=frozenset(('IR_MENU_CLICK','ROUTE_ACCEPTED','START_SID_RESOLVED',
    'PORTAL_REQUEST_BEGIN','PORTAL_REQUEST_END','PLAY_INVOKED','PLAYER_STARTED',
    'FIRST_VIDEO_DETECTED','REMOTE_ACTION_RECEIVED','LIVE_NAV_READY',
    'INFO_WINDOW_VISIBLE','MINI_CHANNELS_VISIBLE','PLAYER_STATE_UNAVAILABLE'))


def emit(value,phase,**fields):
    if phase not in PHASES or not value:return
    try:
        ident=value['id'];started=int(value['started'])
        if len(ident)!=32 or any(c not in '0123456789abcdef' for c in ident):return
        ms=(time.monotonic_ns()-started)//1000000
        if not 0<=ms<=300000:return
        import xbmc
        message='[XCMate][LIVE_TIMING] phase='+phase+' generation='+ident+' ms='+str(ms)
        for key in ('cold','ready','network','menu_route','duration_ms','rows'):
            v=fields.get(key)
            if isinstance(v,(int,float,bool)) and 0<=v<=10**9:message+=' '+key+'='+str(int(v))
        xbmc.log(message,xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,KeyError):pass


def begin(router,menu=False):
    value=getattr(router,'_live_timing',None)
    if value is None:
        value=dict(id=uuid.uuid4().hex,started=time.monotonic_ns())
        router._live_timing=value
        if menu:emit(value,'IR_MENU_CLICK',menu_route=1)
        emit(value,'ROUTE_ACCEPTED',menu_route=menu)
    return value


def bind(value,session):
    import xbmcgui
    xbmcgui.Window(10000).setProperty(KEY,json.dumps(dict(value,nonce=session['nonce'])))
    from flow46 import bind as bind_flow46
    bind_flow46('live',session)


def current():
    try:
        import xbmcgui
        raw=xbmcgui.Window(10000).getProperty(KEY)
        value=json.loads(raw) if raw and len(raw)<1024 else None
        if isinstance(value,dict) and 0<=time.monotonic_ns()-int(value['started'])<120*10**9:return value
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,KeyError):pass
    return None


def observe():
    """Service-only sampling; verify immutable item identity before attributing AV."""
    from flow46 import observe as observe_flow46
    observe_flow46()
    value=current()
    if not value or value.get('video'):return
    try:
        import xbmc,xbmcgui
        from playback_exit import identity
        player=xbmc.Player();owned=identity(player)
        if not owned or owned[0]!='live' or owned[1]['nonce']!=value.get('nonce'):return
        if not value.get('player'):
            value['player']=True;emit(value,'PLAYER_STARTED')
        player.getTime()
        value['video']=True;emit(value,'FIRST_VIDEO_DETECTED',ready=1)
        from epg_handoff63 import note as epg63_note
        epg63_note('FIRST_VIDEO',owned[1]['pid'],owned[1]['sid'])  # Native player-state proxy, not a decoded-frame proof.
        xbmcgui.Window(10000).setProperty(KEY,json.dumps(value))
    except (AttributeError,RuntimeError,TypeError,ValueError):
        # A stop can invalidate InfoTags after isPlayingVideo. Rate limit this
        # diagnostic rather than logging Kodi's private exception message.
        if not value.get('unavailable'):
            emit(value,'PLAYER_STATE_UNAVAILABLE');value['unavailable']=True
            import xbmcgui
            xbmcgui.Window(10000).setProperty(KEY,json.dumps(value))


def nav_ready(navigator):
    navigator._latency=current() or dict(id=uuid.uuid4().hex,started=time.monotonic_ns())
    navigator._latency_seen=set()
    emit(navigator._latency,'LIVE_NAV_READY',rows=len(navigator.channels))
    from flow46 import mark
    if navigator.channels and hasattr(navigator,'portal'):mark('GROUPS_READY',pid=navigator.portal['id'],sid=navigator.sid)


def remote(navigator,command):
    if command not in ('ok','left','long_left','info'):return
    navigator._latency=dict(id=uuid.uuid4().hex,started=time.monotonic_ns())
    emit(navigator._latency,'REMOTE_ACTION_RECEIVED',cold=not bool(getattr(navigator,'_latency_seen',set())))
    emit(navigator._latency,'LIVE_NAV_READY',ready=bool(getattr(navigator,'_drawn',False)))


def visible(navigator):
    phase={'info':'INFO_WINDOW_VISIBLE','channels':'MINI_CHANNELS_VISIBLE'}.get(navigator.mode)
    if phase:
        if phase=='INFO_WINDOW_VISIBLE':
            from epg_handoff63 import visible as epg63_visible
            epg63_visible(navigator)
        if navigator.mode=='channels' and getattr(navigator,'visible_channels',[]) and hasattr(navigator,'portal'):
            from flow46 import mark
            mark('MINI_EPG_VISIBLE',pid=navigator.portal['id'],sid=navigator.sid)
        seen=getattr(navigator,'_latency_seen',set())
        emit(getattr(navigator,'_latency',None),phase,cold=phase not in seen)
        seen.add(phase);navigator._latency_seen=seen

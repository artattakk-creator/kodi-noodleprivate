"""One explicit app-entry intent, shared by root and compatible skin shortcuts.

No DB/network on entry or IR. A consumed lease stays consumed through refresh,
Back, settings and playback. Only service-observed departure rearms it. Kodi
restart clears Window properties; it never starts playback without an entry.
"""
import json
import time
import uuid
from urllib.parse import urlsplit
KEY='XCMate.AppEntry38'
PAUSE='XCMate.AutoplayPause38'


def marker():
    import xbmcgui
    return xbmcgui.Window(10000)


def read():
    try:
        value=json.loads(marker().getProperty(KEY))
        if isinstance(value,dict) and len(value.get('nonce',''))==32:return value
    except (ValueError,TypeError):pass
    return None


def paused():
    try:return 0<float(marker().getProperty(PAUSE))-time.time()<=900
    except (ValueError,TypeError):return False


def toggle_pause():
    import xbmcgui
    from localization import tr
    window=marker()
    if paused():window.clearProperty(PAUSE)
    elif xbmcgui.Dialog().yesno('XCMate',tr(35500)):window.setProperty(PAUSE,str(time.time()+900))
    window.setProperty('XtreamMate.AutoplayDiagnosticState','PAUSED_15_MIN' if paused() else 'ENABLED_BY_PORTAL_PREFERENCE')
    xbmcgui.Dialog().notification('XCMate',tr(35501 if paused() else 35502))


def enter(router,portal):
    import xbmc
    params=router._params
    if params.get('action','root') not in ('root','portal_home','xcmate_home','app_open'):return False
    if any(params.get(k) for k in ('nav','widget','background')) or params.get('entry')=='return':return False
    from setup_navigation import active
    if active():return False
    # A skin background widget is not a deliberate foreground app opening.
    if router._handle<0 or not getattr(xbmc,'getCondVisibility',lambda c:False)('Window.IsActive(videos)'):return False
    if read():return False
    value=dict(nonce=uuid.uuid4().hex,phase='consumed',pid=str(portal['id']),seen=False,outside=0)
    player=xbmc.Player()
    from live_exit import state
    if (paused() or state() or portal.get('type')!='xtream' or not portal.get('enabled',True)
        or not portal.get('include_live',True) or not portal.get('autoplay_start') or not portal.get('start_stream_id')
        or getattr(player,'isPlaying',player.isPlayingVideo)()):
        marker().setProperty(KEY,json.dumps(value));return False
    from profile_transaction import writing
    try:
        with writing(timeout=.05):
            if read():return False
            value=dict(nonce=uuid.uuid4().hex,phase='consumed',pid=str(portal['id']),seen=False,outside=0)
            marker().setProperty(KEY,json.dumps(value))
            player=xbmc.Player()
            from live_exit import state
            if (paused() or state() or portal.get('type')!='xtream' or not portal.get('enabled',True)
                or not portal.get('include_live',True) or not portal.get('autoplay_start') or not portal.get('start_stream_id')
                or getattr(player,'isPlaying',player.isPlayingVideo)()):return False
            value['phase']='queued';marker().setProperty(KEY,json.dumps(value))
    except (OSError,RuntimeError):return False
    xbmc.executebuiltin('RunPlugin('+router.url(action='play_start_direct',pid=portal['id'],autoplay_entry=value['nonce'])+')')
    return True


def accept_play(params):
    nonce=params.get('autoplay_entry')
    if not nonce:return True  # Existing manual direct route.
    import xbmc
    from portals import get_by_id
    from profile_transaction import writing
    with writing(timeout=.05):
        value=read();portal=get_by_id(params.get('pid',''));player=xbmc.Player()
        if not value or value['nonce']!=nonce or value['phase']!='queued':return False
        value['phase']='consumed';marker().setProperty(KEY,json.dumps(value))
        return bool(portal and portal.get('enabled',True) and portal.get('include_live',True) and portal.get('autoplay_start') and not paused()
                    and not getattr(player,'isPlaying',player.isPlayingVideo)())


def _observe_locked():
    """Service-only: bounded native queries, no catalogue or playback action."""
    import xbmc
    value=read()
    if not value:return
    try:
        folder=urlsplit(xbmc.getInfoLabel('Container.FolderPath'))
        own=folder.scheme=='plugin' and folder.netloc=='plugin.video.xtreammate'
        playing=getattr(xbmc.Player(),'isPlaying',xbmc.Player().isPlayingVideo)()
        from window_lifecycle import lease,state
        native=state()
        own=own and native.get('window') in (None,10025)
        before=dict(value)
        if own or playing or lease() or native['modal']:
            if own:value['seen']=True
            value['outside']=0
        elif value['seen']:
            if not value['outside']:value['outside']=time.monotonic()
            elif time.monotonic()-value['outside']>=.5:
                marker().clearProperty(KEY)
                from live_exit import state as exit_state,KEY as exit_key
                prior=exit_state()
                if prior and prior['phase'] in ('complete','failed'):marker().clearProperty(exit_key)
                return
        if value!=before:marker().setProperty(KEY,json.dumps(value))
    except (AttributeError,RuntimeError,TypeError,ValueError):return


def observe():
    if not read():return
    from profile_transaction import writing
    try:
        with writing(timeout=0):_observe_locked()
    except (OSError,RuntimeError):return


def still_allowed(params):
    if not params.get('autoplay_entry'):return True
    import xbmc
    from portals import get_by_id
    try:
        value=read();portal=get_by_id(params.get('pid',''));player=xbmc.Player()
        return bool(value and value['nonce']==params['autoplay_entry'] and value['phase']=='consumed'
                    and portal and portal.get('enabled',True) and portal.get('include_live',True)
                    and portal.get('autoplay_start') and not paused() and not getattr(player,'isPlaying',player.isPlayingVideo)())
    except (OSError,RuntimeError):return False

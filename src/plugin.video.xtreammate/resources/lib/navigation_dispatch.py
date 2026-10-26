"""Whitelisted navigation destinations; invoked after native owner release."""
from urllib.parse import urlencode
ROUTES=frozenset(('global_search','favourites','home_live','movies_home','series_home','guide_grid','settings_home','xcmate_home','startup_settings'))
DIRECTORIES=frozenset(('favourites','home_live','settings_home','xcmate_home'))


class RouteTransfer:
    def __init__(self,action):
        if action not in ROUTES:raise ValueError('INVALID_ROUTE')
        self._nav_destination=action


KEY='XCMate.Navigation38'
ACTIVE='XCMate.NavigationActive38'


def _home():
    import xbmcgui
    return xbmcgui.Window(10000)


def _read(key):
    import json
    try:
        raw=_home().getProperty(key)
        value=json.loads(raw) if raw and len(raw)<4096 else None
        return value if isinstance(value,dict) else None
    except (ValueError,RuntimeError):return None


def dispatch(action,pid):
    if action not in ROUTES:return False
    import time,uuid,json,xbmc
    from playback_exit import identity
    if _read(KEY):return False
    current=identity(xbmc.Player());token=current if current and (current[0]=='live' or action=='xcmate_home') else None
    value=dict(action=action,pid=str(pid),token=token,nonce=uuid.uuid4().hex,deadline=time.monotonic()+12)
    _home().setProperty(KEY,json.dumps(value))
    trace('QUEUED')
    return True


def holding():
    import time,xbmc
    pending=_read(KEY)
    if pending and time.monotonic()<pending.get('deadline',0):return bool(pending.get('token'))
    value=_read(ACTIVE)
    if not value:return False
    from playback_exit import identity,_same
    if not value.get('token') or not _same(identity(xbmc.Player()),tuple(value['token'])):
        _home().clearProperty(ACTIVE);return False
    return True


def poll():
    import xbmc,time,json
    from window_lifecycle import state,lease
    pending=_read(KEY);value=_read(ACTIVE);native=state()
    if value:
        if not holding():value=None
        elif lease() or native['modal'] or native['window'] not in (12005,12901):
            value['away']=True;_home().setProperty(ACTIVE,json.dumps(value))
        elif value.get('away') or time.monotonic()>value.get('opening_until',0):
            _home().clearProperty(ACTIVE)
    if not pending:return
    if time.monotonic()>pending.get('deadline',0):
        _home().clearProperty(KEY);trace('TIMEOUT')
        from localization import tr
        import xbmcgui
        xbmcgui.Dialog().notification('XCMate',tr(35630));return
    if lease() or native['modal'] or native['updating']:return
    action=pending.get('action')
    if action not in ROUTES:_home().clearProperty(KEY);return
    if pending.get('token'):
        from playback_exit import identity,_same
        player=xbmc.Player();current=identity(player)
        if action=='xcmate_home' and pending.get('stopping'):
            if getattr(player,'isPlaying',player.isPlayingVideo)():
                if not _same(current,tuple(pending['token'])):_home().clearProperty(KEY);trace('FOREIGN_PLAYER')
                return
            pending['token']=None
        elif not _same(current,tuple(pending['token'])):
            _home().clearProperty(KEY);trace('FOREIGN_PLAYER');return
        elif action=='xcmate_home':
            from exit_jobs import request
            if not request(player,expected=current):_home().clearProperty(KEY);trace('STOP_REJECTED');return
            pending['stopping']=True;_home().setProperty(KEY,json.dumps(pending));return
    _home().clearProperty(KEY)
    if pending.get('token'):
        _home().setProperty(ACTIVE,json.dumps(dict(token=pending['token'],away=False,opening_until=time.monotonic()+8)))
    url='plugin://plugin.video.xtreammate/?'+urlencode(dict(action=action,pid=pending['pid'],entry='return'))
    trace('DISPATCHED')
    xbmc.executebuiltin(('ActivateWindow(Videos,'+url+',return)') if action in DIRECTORIES else 'RunPlugin('+url+')')


def current_start(portal,session):
    """Only a deliberate button+confirmation may persist the current SID."""
    from playback_exit import identity,_same
    import xbmc,xbmcgui
    if not _same(identity(xbmc.Player()),('live',session)):return False
    from portals import get_by_id
    current=get_by_id(portal['id'])
    if not current or not current.get('enabled',True):return False
    from library_index import Reader
    # Use the current tagged SID, never a highlighted but untuned mini row.
    sid=str(session['sid']);channel=Reader(portal['id']).get('live',sid)
    if channel is None:return False
    from group_selection import load
    cid=str(channel.get('category_id',''));selected=load(portal['id'],'live')
    if selected is not None and cid not in selected:return False
    from localization import tr
    if not xbmcgui.Dialog().yesno('XCMate',tr(35614,str(channel.get('name','')))):return False
    if not _same(identity(xbmc.Player()),('live',session)):return False
    from portals import update
    current=get_by_id(portal['id'])
    if not current or not current.get('enabled',True):return False
    result=update(portal['id'],dict(start_group_id=cid,start_stream_id=sid)) is not False
    if result:xbmcgui.Dialog().notification('XCMate',tr(35616))
    return result


def trace(stage):
    if stage not in ('QUEUED','DISPATCHED','TIMEOUT','FOREIGN_PLAYER','STOP_REJECTED'):return
    import xbmc
    try:xbmc.log('[XCMate][NAV38] stage='+stage,xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass

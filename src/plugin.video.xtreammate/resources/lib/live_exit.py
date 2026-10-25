"""Session-scoped explicit TV exit; callbacks request, service stops/returns."""
import hashlib,json,time
from urllib.parse import urlencode
import xbmc,xbmcgui
KEY='XCMate.LiveExit'
SESSION='XtreamMate.LiveSession'


def _marker():return xbmcgui.Window(10000)


def state():
    try:
        value=json.loads(_marker().getProperty(KEY))
        from playback_exit import _session
        if isinstance(value,dict) and _session(json.dumps(value.get('session'))) and value.get('phase') in ('requested','stopping','home','complete','failed') and 0<=time.time()-value['at']<86400:return value
    except (ValueError,TypeError,KeyError):pass
    return None


def _save(value):_marker().setProperty(KEY,json.dumps(value))


def _trace(stage,session=None):
    # Stable correlation without clear portal, sender, nonce or URL in the log.
    digest=hashlib.sha256(json.dumps({k:(session or {}).get(k) for k in ('pid','sid','nonce')},sort_keys=True).encode()).hexdigest()[:12]
    try:
        xbmc.log('[XCMate][LIVE_EXIT] stage='+stage+' session='+digest+
                 ' video='+str(int(xbmc.Player().isPlayingVideo()))+
                 ' window='+str(int(xbmcgui.getCurrentWindowId())),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def new_selection():
    # Called by an actual resolver/tune announcement; service URL-recovery is
    # suppressed while this intent exists and cannot create this selection.
    _marker().clearProperty(KEY)


def request(navigator):
    if getattr(navigator,'_exiting',False):return True
    from playback_exit import identity,_same
    player=xbmc.Player();token=identity(player)
    if token is None and not player.isPlayingVideo():token=getattr(navigator,'_owned_token',None)
    if not token or token[0]!='live' or token[1]['pid']!=str(navigator.portal['id']):return False
    from live_overlay import session_from_property
    announced=session_from_property(_marker().getProperty(SESSION))
    pending=None
    if announced and not _same(token,('live',announced)):
        previous=getattr(navigator,'_previous_session',None)
        if not (previous and _same(token,('live',previous)) and announced['pid']==str(navigator.portal['id']) and announced['sid']==navigator.sid):return False
        pending={k:announced[k] for k in ('pid','sid','nonce','at')}
    prior=state()
    if prior and _same(('live',prior['session']),token):
        # The latch belongs to the session, not one Python WindowDialog. A
        # reconstructed/reentrant navigator cannot replay Stop/Home or reset
        # an already committed phase/deadline.
        navigator._exiting=True;navigator._exit_nonce=token[1]['nonce']
        return True
    value=dict(session={k:token[1][k] for k in ('pid','sid','nonce','at')},phase='requested',at=time.time(),deadline=time.monotonic()+5,not_before=time.monotonic()+.15)
    value['pending']=pending
    _save(value);navigator._exiting=True;navigator._exit_nonce=token[1]['nonce']
    _marker().setProperty('XCMate.PrePlay.Cancel',(pending or token[1])['nonce'])
    _trace('STOP_REQUESTED',token[1]);return True


def _poll(navigator=None):
    value=state()
    if value is None:
        # A consciously selected new session replaces the old exiting dialog.
        if navigator is not None and getattr(navigator,'_exiting',False):navigator.close()
        return False
    session=value['session'];marker=_marker()
    from live_overlay import session_from_property
    current=session_from_property(marker.getProperty(SESSION))
    allowed=[session]+([value['pending']] if value.get('pending') else [])
    if current and not any(current['nonce']==item['nonce'] for item in allowed):
        if navigator is not None and getattr(navigator,'_exiting',False):navigator.close()
        marker.clearProperty(KEY);return False
    player=xbmc.Player()
    from playback_exit import identity,_same
    from exit_jobs import request as stop_owned
    if value['phase'] in ('complete','failed'):
        # A past live Exit must not disable media_progress/playback_exit for
        # a later movie or a foreign add-on. Keep the root-autoplay tombstone.
        return not player.isPlayingVideo() or any(_same(identity(player),('live',item)) for item in allowed)
    token=identity(player)
    playing=player.isPlaying() if hasattr(player,'isPlaying') else player.isPlayingVideo()
    if playing and not any(_same(token,('live',item)) for item in allowed):
        # Foreign playback must neither receive stop nor a GUI navigation.
        if navigator is not None and getattr(navigator,'_exiting',False):navigator.close()
        value['phase']='failed';_save(value);_trace('FOREIGN_PLAYER',session);return True
    if value['phase']=='requested':
        if time.monotonic()<value['not_before']:return True
        # Commit before invoking native Stop; reentrant ticks cannot stop twice.
        value['phase']='stopping';_save(value)
        # Release the native overlay BEFORE scheduling Stop on a later tick.
        # Never wait on Player.stop while owning the live dialog.
        if navigator is not None and not navigator._closed:navigator.close()
        if playing:
            if not stop_owned(player,expected=token):
                value['phase']='failed';_save(value)
                if navigator is not None and not navigator._closed:navigator.close()
                _trace('OWNERSHIP_CHANGED',session);return True
        _trace('STOP_QUEUED',session)
        return True
    if player.isPlayingVideo() or (hasattr(player,'isPlaying') and player.isPlaying()):
        if time.monotonic()>value['deadline']:
            value['phase']='failed';_save(value)
            if navigator is not None and not navigator._closed:navigator.close()
            _trace('STOP_TIMEOUT',session)
            xbmcgui.Dialog().notification('XCMate','Live-TV konnte nicht beendet werden.')
        return True
    if value['phase']=='stopping':
        if navigator is not None and not navigator._closed:navigator.close()
        for key in ('XCMate.PrePlay.Request','XCMate.PrePlay.Ack','XCMate.PrePlay.Ready',SESSION,'XtreamMate.RemoteCommand'):
            raw=marker.getProperty(key)
            if key=='XtreamMate.RemoteCommand' or raw in [item['nonce'] for item in allowed] or (session_from_property(raw) or {}).get('nonce') in [item['nonce'] for item in allowed]:marker.clearProperty(key)
        value['phase']='home';_save(value);_trace('STOP_DONE',session)
        return True  # Native close returns before navigation on a later tick.
    if xbmc.getCondVisibility('System.HasActiveModalDialog'):
        if time.monotonic()>value['deadline']:value['phase']='failed';_save(value);_trace('RETURN_BLOCKED',session)
        return True
    if getattr(xbmc.Monitor(),'abortRequested',lambda:False)():return True
    value['phase']='complete';_save(value)
    url='plugin://plugin.video.xtreammate/?'+urlencode(dict(action='xcmate_home',pid=session['pid']))
    from urllib.parse import urlsplit,parse_qs
    folder=urlsplit(xbmc.getInfoLabel('Container.FolderPath'))
    params=parse_qs(folder.query)
    same_home=(folder.scheme=='plugin' and folder.netloc=='plugin.video.xtreammate'
               and params.get('action')==['xcmate_home'] and params.get('pid')==[session['pid']])
    if same_home:
        # Reveal the existing Videos Home without issuing another GetDirectory.
        if not xbmc.getCondVisibility('Window.IsActive(videos)'):
            xbmc.executebuiltin('ActivateWindow(Videos)')
        _trace('HOME_REUSED',session)
    elif xbmc.getCondVisibility('Window.IsActive(videos)'):
        xbmc.executebuiltin('Container.Update('+url+',replace)')
    else:xbmc.executebuiltin('ActivateWindow(Videos,'+url+',return)')
    if not same_home:_trace('HOME_REQUESTED',session)
    return True


def poll(navigator=None):
    try:return _poll(navigator)
    except (AttributeError,RuntimeError,TypeError,ValueError,KeyError):
        # Kodi can invalidate InfoTags between isPlayingVideo and identity().
        # Hold this exit while pending; never terminate the background service.
        value=state()
        if not value:return False
        if time.monotonic()>value['deadline']:
            value['phase']='failed';_save(value)
            if navigator is not None and not navigator._closed:navigator.close()
        _trace('PLAYER_UNAVAILABLE',value['session']);return True

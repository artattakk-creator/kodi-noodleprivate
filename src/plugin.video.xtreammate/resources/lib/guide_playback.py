"""One-shot grid-to-existing-live-route handoff, outside every Window callback."""
import time
import xbmc,xbmcgui
from localization import tr


def _mark(stage):
    # Fixed stages only, no sender IDs, paths, stream URLs or exception text.
    try:xbmc.log('[XCMate][GUIDE_HANDOFF] stage='+stage,xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def player_state():
    try:
        player=xbmc.Player()
        playing=player.isPlaying() if hasattr(player,'isPlaying') else player.isPlayingVideo()
        return (True,player.getPlayingFile()) if playing else (False,'')
    except (AttributeError,RuntimeError):return None


def request(portal,channel,entry_player):
    _mark('QUEUED')
    return dict(pid=str(portal['id']),sid=str(channel['sid']),player=entry_player,
                session=xbmcgui.Window(10000).getProperty('XtreamMate.LiveSession'))


def _handoff(router,portal,intent):
    # Consume before any wait/foreign callback; a repeated call cannot replay.
    if intent.pop('consumed',False):return False
    intent['consumed']=True
    if intent.get('pid')!=str(portal['id']) or not intent.get('sid'):return False
    monitor=xbmc.Monitor();deadline=time.monotonic()+2
    while True:
        if getattr(monitor,'abortRequested',lambda:False)():return False
        try:active=int(xbmcgui.getCurrentWindowId())==intent.get('window')
        except (AttributeError,RuntimeError):active=False
        if not active and not xbmc.getCondVisibility('System.HasActiveModalDialog'):break
        if time.monotonic()>=deadline or monitor.waitForAbort(.05):return False
    # Never stop a player or override a different session that started meanwhile.
    if intent.get('player') is None or player_state()!=intent['player']:return False
    from library_index import Reader
    from portals import get_by_id
    current=get_by_id(intent['pid'])
    if not current or not current.get('enabled',True) or current.get('type')!=portal.get('type'):return False
    channel=Reader(intent['pid']).get('live',intent['sid'])
    if not channel:return False
    if portal.get('type') not in ('xtream','m3u','stb'):return False
    action='play_live' if portal.get('type')=='xtream' else 'source_play'
    # Exactly the playable URL used by the working Live-TV directory. Kodi
    # supplies the resolver handle in a new plugin invocation; no direct player.
    url=router.url(action=action,pid=intent['pid'],sid=channel['sid'],name=channel['name'])
    if player_state()!=intent['player']:return False
    if xbmcgui.Window(10000).getProperty('XtreamMate.LiveSession')!=intent['session']:return False
    _mark('RESOLVER_REQUEST')
    xbmc.executebuiltin('PlayMedia('+url+')')
    return True


def handoff(router,portal,intent):
    if intent.get('consumed'):return False
    try:started=_handoff(router,portal,intent)
    except Exception:
        # Bounded read failures must not escape into another playback attempt.
        started=False
    _mark('DISPATCHED' if started else 'SKIPPED')
    if not started:xbmcgui.Dialog().notification('XCMate',tr(33122))
    return started

"""One-shot guide -> existing live resolver, after native owner/lease release."""
import time
import uuid
import xbmc,xbmcgui
from localization import tr

REASONS=frozenset(('INVALID_INTENT','REPLAY','OWNER_ABORT','OWNER_UNAVAILABLE','WINDOW_STILL_ACTIVE',
    'BUSY_TIMEOUT','FOREIGN_MODAL','CONTAINER_UPDATING','PLAYER_UNAVAILABLE','PLAYER_STATE_CHANGED',
    'FOREIGN_PLAYER','LIVE_SESSION_CHANGED','PORTAL_UNAVAILABLE','PORTAL_CHANGED','CHANNEL_UNAVAILABLE',
    'UNSUPPORTED_PORTAL','EXCEPTION_CLASS'))


class Rejected(Exception):pass


def _mark(stage,intent=None,reason='',error=None):
    from window_lifecycle import state,token,lease
    intent=intent or {};snapshot=state()
    values=['[XCMate][GUIDE_HANDOFF] stage='+stage,'reason='+(reason if reason in REASONS else ''),
            'request='+token(intent.get('request','')),'origin_lease='+token(intent.get('lease','')),
            'lease='+lease(),'owner='+token(intent.get('owner','')),
            'surface='+('dialog' if intent.get('surface')=='dialog' else 'window'),
            'window='+str(snapshot['window']),'dialog='+str(snapshot['dialog']),
            'modal='+str(int(snapshot['modal'])),'updating='+str(int(snapshot['updating']))]
    if error is not None:
        name=type(error).__name__
        values.append('error='+(name if name in ('RuntimeError','ValueError','TypeError','OSError','IndexReadError','OperationalError','MemoryError') else 'OTHER'))
    try:xbmc.log(' '.join(values),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def player_state():
    try:
        player=xbmc.Player()
        playing=player.isPlaying() if hasattr(player,'isPlaying') else player.isPlayingVideo()
        return (True,player.getPlayingFile()) if playing else (False,'')
    except (AttributeError,RuntimeError):return None


def request(portal,channel,entry_player,reference=None):
    from window_lifecycle import lease
    intent=dict(pid=str(portal['id']),sid=str(channel['sid']),player=entry_player,
                session=xbmcgui.Window(10000).getProperty('XtreamMate.LiveSession'),request=uuid.uuid4().hex,lease=lease())
    if reference:intent.update(reference)
    _mark('QUEUED',intent);return intent


def _check_player(intent):
    state=player_state()
    if state is None or intent.get('player') is None:raise Rejected('PLAYER_UNAVAILABLE')
    if state!=intent['player']:raise Rejected('PLAYER_STATE_CHANGED')
    if state[0]:
        from playback_exit import identity
        owned=identity(xbmc.Player())
        if not owned or owned[0]!='live' or owned[1].get('pid')!=intent['pid']:raise Rejected('FOREIGN_PLAYER')
    if xbmcgui.Window(10000).getProperty('XtreamMate.LiveSession')!=intent.get('session',''):
        raise Rejected('LIVE_SESSION_CHANGED')


def _idle(intent):
    from window_lifecycle import active,state
    if intent.get('surface')=='dialog' and intent.get('window') is None:raise Rejected('OWNER_UNAVAILABLE')
    monitor=xbmc.Monitor();deadline=time.monotonic()+2;last=None
    while True:
        if getattr(monitor,'abortRequested',lambda:False)():raise Rejected('OWNER_ABORT')
        snapshot=state();own_active=active(intent,snapshot)
        reason=('WINDOW_STILL_ACTIVE' if own_active else 'BUSY_TIMEOUT' if snapshot['dialog']==10138 else
                'FOREIGN_MODAL' if snapshot['modal'] else 'CONTAINER_UPDATING' if snapshot['updating'] else '')
        if not reason:return
        if reason!=last:_mark('WAIT',intent,reason);last=reason
        if time.monotonic()>=deadline:raise Rejected(reason)
        if monitor.waitForAbort(.05):raise Rejected('OWNER_ABORT')


def _handoff(router,portal,intent):
    if intent.get('consumed',False):raise Rejected('REPLAY')
    intent['consumed']=True
    if intent.get('pid')!=str(portal['id']) or not intent.get('sid'):raise Rejected('INVALID_INTENT')
    _idle(intent);_check_player(intent)
    from library_index import Reader
    from portals import get_by_id
    current=get_by_id(intent['pid'])
    if not current or not current.get('enabled',True):raise Rejected('PORTAL_UNAVAILABLE')
    if current.get('type')!=portal.get('type'):raise Rejected('PORTAL_CHANGED')
    if portal.get('type') not in ('xtream','m3u','stb'):raise Rejected('UNSUPPORTED_PORTAL')
    channel=Reader(intent['pid'],timeout=.15,query_seconds=1).get('live',intent['sid'])
    if not channel:raise Rejected('CHANNEL_UNAVAILABLE')
    action='play_live' if portal.get('type')=='xtream' else 'source_play'
    # The resolver and player are the same as in the working Live-TV directory.
    url=router.url(action=action,pid=intent['pid'],sid=channel['sid'],name=channel['name'])
    _idle(intent);_check_player(intent)
    _mark('RESOLVER_REQUEST',intent)
    xbmc.executebuiltin('PlayMedia('+url+')')
    return True


def handoff(router,portal,intent):
    reason='';error=None
    try:started=_handoff(router,portal,intent)
    except Rejected as exc:started=False;reason=str(exc)
    except Exception as exc:started=False;reason='EXCEPTION_CLASS';error=exc
    _mark('DISPATCHED' if started else 'SKIPPED',intent,reason,error)
    if not started and reason!='REPLAY':xbmcgui.Dialog().notification('XCMate',tr(33122))
    return started

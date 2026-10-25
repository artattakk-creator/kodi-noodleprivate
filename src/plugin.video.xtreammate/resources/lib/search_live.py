"""Search-only direct handoff after WindowXML/owner release; no plugin resolver."""
import time
import uuid
import xbmc
import xbmcgui
from localization import tr


class Rejected(Exception):
    pass


def mark(stage,token,reason=''):
    # Values originate only in this module, never from a provider/exception.
    try:xbmc.log('[XCMate][SEARCH_LIVE] stage={} request={} reason={}'.format(stage,token,reason),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def _check_player(intent):
    from guide_playback import player_state
    state=player_state()
    if state is None:raise Rejected('PLAYER_UNAVAILABLE')
    if state!=intent.get('player'):raise Rejected('PLAYER_CHANGED')
    if xbmcgui.Window(10000).getProperty('XtreamMate.LiveSession')!=intent.get('session'):
        raise Rejected('SESSION_CHANGED')
    if state[0]:
        from playback_exit import identity
        owned=identity(xbmc.Player())
        if not owned or owned[0]!='live' or owned[1]['pid']!=intent.get('pid'):
            raise Rejected('FOREIGN_PLAYER')


def _idle(intent,monitor):
    deadline=time.monotonic()+5
    while True:
        if getattr(monitor,'abortRequested',lambda:False)():raise Rejected('SHUTDOWN')
        _check_player(intent)
        from window_lifecycle import active as frame_active
        active=frame_active(intent)
        busy=any(xbmc.getCondVisibility(c) for c in (
            'System.HasActiveModalDialog','Window.IsActive(busydialog)',
            'Window.IsActive(busydialognocancel)'))
        if not active and not busy:return
        if time.monotonic()>=deadline:raise Rejected('WINDOW_WAIT_TIMEOUT' if active else 'BUSY_TIMEOUT')
        if monitor.waitForAbort(.05):raise Rejected('SHUTDOWN')


def _prepare(portal,intent):
    from portals import get_by_id
    from library_index import Reader
    current=get_by_id(intent.get('pid',''))
    if not current or not current.get('enabled',True):raise Rejected('PORTAL_UNAVAILABLE')
    if str(portal['id'])!=str(current['id']) or portal.get('type')!=current.get('type'):
        raise Rejected('PORTAL_CHANGED')
    channel=Reader(current['id'],timeout=.15,query_seconds=1).get('live',intent.get('sid',''))
    if not channel:raise Rejected('CHANNEL_NOT_FOUND')
    if current.get('type')=='xtream':
        from xtream import XtreamClient
        client=XtreamClient(current['xc_host'],current['xc_user'],current['xc_pass'])
        url=client.live_stream_url(channel['sid']);headers={}
    elif current.get('type') in ('m3u','stb'):
        from source_adapters import for_portal
        url,headers=for_portal(current).play_uri('live',channel['sid'])
    else:raise Rejected('UNSUPPORTED_PORTAL')
    if not url:raise Rejected('SOURCE_UNAVAILABLE')
    return current,channel,url,headers


def handoff(router,portal,intent):
    if intent.get('consumed'):return False
    intent['consumed']=True;token=uuid.uuid4().hex
    mark('OWNER_RELEASED',token)
    previous=intent.get('session','');session=None
    try:
        monitor=xbmc.Monitor();_idle(intent,monitor)
        current,channel,url,headers=_prepare(portal,intent)
        # Provider resolution may yield to another invocation. Revalidate after it.
        _idle(intent,monitor)
        from player import build_playable_item
        from live_overlay import announce
        from live_recovery import tag_live_item
        item=build_playable_item(url,title=channel['name'],headers=headers)
        _check_player(intent)
        session=announce(current['id'],channel['sid'],channel['name'])
        if not tag_live_item(item,session):raise Rejected('ITEM_TAG_UNAVAILABLE')
        if getattr(monitor,'abortRequested',lambda:False)():raise Rejected('SHUTDOWN')
        # Same direct Player/ListItem contract as the working Startsender route.
        # Do not PlayMedia(plugin://...): that starts Kodi's GetDirectory/busy
        # resolver inside the returning directory invocation (#125).
        mark('PLAYER_REQUEST',token)
        xbmc.Player().play(item.getPath(),item)
        mark('PLAYER_DISPATCHED',token)
        return True
    except Exception as exc:
        if session is not None:
            marker=xbmcgui.Window(10000)
            from live_overlay import session_from_property
            actual=session_from_property(marker.getProperty('XtreamMate.LiveSession'))
            if actual and actual.get('nonce')==session['nonce']:
                marker.setProperty('XtreamMate.LiveSession',previous)
        reason=str(exc) if isinstance(exc,Rejected) else 'START_FAILED'
        mark('REJECTED',token,reason)
        xbmcgui.Dialog().notification('XCMate',tr(33122))
        return False

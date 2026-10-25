"""Service -> plugin one-shot guide excursion; original live item keeps playing.

Only the service closes its own navigator. The separate plugin owns its native
Guide/Search pump; service progress/autoplay/background polling keeps running.
"""
import json
import time
import uuid
from types import SimpleNamespace
from urllib.parse import urlencode
import xbmc,xbmcgui

KEY='XCMate.LiveGuideIntent'
RESUME='XCMate.LiveGuideResume'
PHASES=frozenset(('QUEUED','WAIT_RELEASE','DISPATCHED','ACTIVE','SWITCH','RETURN'))


def _home():return xbmcgui.Window(10000)


def _state():
    try:
        raw=_home().getProperty(KEY)
        if not raw or len(raw)>8192:return None
        value=json.loads(raw)
        from window_lifecycle import token
        if (not token(value.get('token')) or value.get('phase') not in PHASES or
                not isinstance(value.get('session'),dict)):return None
        return value
    except (ValueError,TypeError,RuntimeError):return None


def _save(value):_home().setProperty(KEY,json.dumps(value,separators=(',',':')))


def _mark(stage):
    if stage not in ('REQUESTED','SUSPENDED','DISPATCHED','OPEN','RETURN','SWITCH','REJECTED','TIMEOUT'):return
    from window_lifecycle import state
    snapshot=state()
    try:xbmc.log('[XCMate][LIVE_GUIDE] stage={} window={} dialog={}'.format(stage,snapshot['window'],snapshot['dialog']),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def _same_player(value):
    from playback_exit import identity,_same
    try:return _same(identity(xbmc.Player()),('live',value['session']))
    except (AttributeError,RuntimeError,ValueError,TypeError):return False


def _announced(value):
    from live_overlay import session_from_property,SESSION_KEY
    current=session_from_property(_home().getProperty(SESSION_KEY))
    return current and all(current.get(k)==value['session'].get(k) for k in ('pid','sid','nonce'))


def _finish(value,navigator=None,notify=False):
    current=_state()
    if current and current['token']==value['token']:_home().clearProperty(KEY)
    if navigator is not None:navigator._guide_handoff=False
    if _same_player(value) and _announced(value) and (navigator is None or navigator._closed):
        _home().setProperty(RESUME,json.dumps(dict(nonce=value['session']['nonce'],at=time.monotonic())))
    if notify:
        from localization import tr
        xbmcgui.Dialog().notification('XCMate',tr(32910))


def request(navigator):
    """Native callback only creates an intent; never closes/navigates/plays."""
    if _state() or navigator._closed or getattr(navigator,'_guide_handoff',False):return False
    from playback_exit import identity
    from window_lifecycle import state
    try:
        owned=identity(xbmc.Player());dialog=state()['dialog']
        if (not owned or owned[0]!='live' or owned[1]['pid']!=str(navigator.portal['id']) or
                not navigator.owns_playback() or dialog is None or dialog<13000 or
                xbmcgui.Window(dialog).getProperty('XtreamMate.NavigatorIdentity')!=navigator._window_nonce):return False
        session={k:owned[1][k] for k in ('pid','sid','nonce','at')}
        value=dict(token=uuid.uuid4().hex,phase='QUEUED',session=session,owner=navigator._window_nonce,
                   dialog=dialog,created=time.monotonic(),deadline=time.monotonic()+5)
        if not _announced(value):return False
        _save(value);navigator._guide_handoff=True;_mark('REQUESTED');return True
    except (AttributeError,RuntimeError,TypeError,KeyError):return False


def preserves_player():
    value=_state()
    return bool(value and _same_player(value))


def poll(navigator=None):
    """Service owner tick, with no native work on the callback stack."""
    value=_state()
    if value is None:return False
    from window_lifecycle import state,lease
    snapshot=state();now=time.monotonic();phase=value['phase']
    if getattr(xbmc.Monitor(),'abortRequested',lambda:False)():
        _finish(value,navigator);return False
    if phase in ('QUEUED','WAIT_RELEASE','DISPATCHED') and (not _same_player(value) or not _announced(value)):
        _mark('REJECTED');_finish(value,navigator);return False
    if phase=='QUEUED':
        if (navigator is None or navigator._closed or navigator._window_nonce!=value['owner']):
            _finish(value,navigator);return False
        if snapshot['dialog']!=value['dialog']:
            if now>value['deadline']:_mark('TIMEOUT');_finish(value,navigator,notify=True);return False
            return True  # Foreign modal owns focus; leave it and our dialog intact.
        navigator.suspend_for_guide()
        value['phase']='WAIT_RELEASE';_save(value);_mark('SUSPENDED');return True
    if phase=='WAIT_RELEASE':
        if snapshot['dialog']==value['dialog'] or snapshot['modal'] or snapshot['updating']:
            if now>value['deadline']:_mark('TIMEOUT');_finish(value,navigator,notify=True);return False
            return True
        if not xbmc.getCondVisibility('Window.IsActive(fullscreenvideo)'):
            _mark('REJECTED');_finish(value,navigator);return False
        value.update(phase='DISPATCHED',deadline=now+8);_save(value)
        xbmc.executebuiltin('RunPlugin(plugin://plugin.video.xtreammate/?action=live_guide&token='+value['token']+')')
        _mark('DISPATCHED');return True
    if phase=='DISPATCHED':
        if now>value['deadline']:_mark('TIMEOUT');_finish(value,navigator,notify=True);return False
        return True
    if phase=='ACTIVE':
        if value.get('lease')==lease():return True
        # Plugin failure/return released its lease. Never force any dialog shut.
        value.update(phase='RETURN',deadline=now+15);_save(value)
    elif phase=='SWITCH':
        if _same_player(value) and _announced(value) and now<value['deadline']:return True
        value.update(phase='RETURN',deadline=now+15);_save(value)
    if snapshot['modal'] or snapshot['updating']:
        if now>value['deadline']:_finish(value,navigator);return False
        return True
    _finish(value,navigator);return False


def consume_resume():
    try:
        raw=_home().getProperty(RESUME)
        value=json.loads(raw) if raw else {}
        if 0<=time.monotonic()-value.get('at',-100)<=30:
            from window_lifecycle import state
            snapshot=state()
            if snapshot['modal'] or snapshot['updating']:return ''
            if not xbmc.getCondVisibility('Window.IsActive(fullscreenvideo)'):return ''
            _home().clearProperty(RESUME);return value.get('nonce','')
        _home().clearProperty(RESUME)
    except (ValueError,RuntimeError,TypeError):pass
    return ''


def restore_info(candidate,nonce):
    from live_overlay import session_from_property,SESSION_KEY
    session=session_from_property(_home().getProperty(SESSION_KEY))
    if nonce and session and session['nonce']==nonce and candidate.owns_playback():
        candidate.mode='info';candidate._info_deadline=time.monotonic()+candidate._info_timeout


def run(token):
    """Dedicated action invocation: no Home anchor, no player stop on opening."""
    from window_navigation import ownership
    from window_lifecycle import state,lease
    value=_state()
    if not value or value['token']!=token or value['phase']!='DISPATCHED':return False
    if time.monotonic()>value['deadline'] or not _same_player(value) or not _announced(value):return False
    snapshot=state()
    if snapshot['modal'] or snapshot['updating'] or not xbmc.getCondVisibility('Window.IsActive(fullscreenvideo)'):return False
    intent=None;portal=None;router=None
    try:
        with ownership() as acquired:
            if not acquired:return False
            # Commit ACTIVE before native callbacks; a repeated token cannot run.
            value.update(phase='ACTIVE',lease=lease());_save(value)
            from portals import get_by_id
            portal=get_by_id(value['session']['pid'])
            if not portal or not portal.get('enabled',True):return False
            def client(p):
                if p.get('type')=='xtream':
                    from xtream import XtreamClient
                    return XtreamClient(p['xc_host'],p['xc_user'],p['xc_pass'])
                return None
            router=SimpleNamespace(_handle=-1,_params={'pid':portal['id']},_xc=client,
                _navigation_dispatch=value['token'],
                url=lambda **kw:'plugin://plugin.video.xtreammate/?'+urlencode({k:v for k,v in kw.items() if v is not None}))
            from guide_grid_window import open_grid
            _mark('OPEN');intent=open_grid(router,portal)
        if intent:
            # Existing .34 handoff only AFTER native pump and lease release.
            from guide_playback import handoff
            value.update(phase='SWITCH',deadline=time.monotonic()+3);_save(value)
            started=handoff(router,portal,intent)
            if started:_mark('SWITCH');return True
        value.update(phase='RETURN',deadline=time.monotonic()+15);_save(value);_mark('RETURN');return True
    except Exception:
        # Never publish private exception text or restart the player on failure.
        _mark('REJECTED');return False
    finally:
        current=_state()
        if current and current['token']==token and current['phase']=='ACTIVE':
            value.update(phase='RETURN',deadline=time.monotonic()+15);_save(value)

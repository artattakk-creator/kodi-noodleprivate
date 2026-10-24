"""One-shot, memory-only continuation in Kodi's asynchronous RunScript owner.

The originating plugin returns normally. The new invocation acquires its OWN
navigation lease and waits for real native release; no modal bypass/forced close.
"""
import json
import time
import uuid
from types import SimpleNamespace
from urllib.parse import urlencode,urlsplit,parse_qs
import xbmc,xbmcgui

PREFIX='XCMate.SearchContinuation.'
LATEST=PREFIX+'latest'
MAX_BYTES=2*1024*1024
TTL=15


def valid_token(value):
    return isinstance(value,str) and len(value)==32 and all(c in '0123456789abcdef' for c in value)


class SearchTransfer:
    deferred=True
    def __init__(self,router,portal,request,source):
        from guide_playback import player_state
        request=dict(request)
        if request.get('query') is not None:request['query']=str(request['query']).strip()[:200]
        self.payload=dict(pid=str(portal['id']),portal_type=portal.get('type',''),request=request,source=source,
                          directory=source=='route' and router._handle>=0,folder=xbmc.getInfoLabel('Container.FolderPath'),
                          player=player_state(),live_session=xbmcgui.Window(10000).getProperty('XtreamMate.LiveSession'))


def _mark(stage,payload):
    from search_navigation import mark
    mark(stage,source=payload.get('source','route'),session=payload.get('request',{}).get('session',''),owner=True)


def schedule(transfer):
    payload=dict(transfer.payload,created=time.monotonic())
    token=uuid.uuid4().hex;home=xbmcgui.Window(10000)
    try:
        previous=home.getProperty(LATEST)
        if valid_token(previous):home.clearProperty(PREFIX+previous)
        home.setProperty(LATEST,token)
        value=json.dumps(payload,ensure_ascii=True,separators=(',',':'))
        if len(value)>MAX_BYTES:raise ValueError('SEARCH_CONTINUATION_SIZE')
        home.setProperty(PREFIX+token,value)
        # Fixed installed script + random token only, never a query/account URL.
        xbmc.executebuiltin('RunScript("special://home/addons/plugin.video.xtreammate/search_handoff.py",'+token+')')
    except (ValueError,RuntimeError,TypeError):
        home.clearProperty(PREFIX+token)
        if home.getProperty(LATEST)==token:home.clearProperty(LATEST)
        _mark('ASYNC_FAILED',payload);return False
    _mark('ASYNC_QUEUED',payload);return True


def handoff(router,portal,result):
    if isinstance(result,SearchTransfer):return schedule(result)
    if not isinstance(result,dict):
        from media_search import handoff as selected
        return selected(router,portal,result)
    from guide_playback import handoff as selected
    return selected(router,portal,result)


def _consume(token):
    if not valid_token(token):return None
    home=xbmcgui.Window(10000);value=home.getProperty(PREFIX+token)
    home.clearProperty(PREFIX+token)
    if home.getProperty(LATEST)!=token:return None
    home.clearProperty(LATEST)
    if not value or len(value)>MAX_BYTES:return None
    try:
        payload=json.loads(value);age=time.monotonic()-float(payload['created'])
        request=payload['request']
        if not 0<=age<=TTL or payload['source'] not in ('route','guide','grid'):return None
        if not valid_token(request['session']):return None
        if request.get('query') is not None and (not isinstance(request['query'],str) or len(request['query'])>200):return None
        if payload['source']!='route' and not isinstance(request['view'],dict):return None
        return payload
    except (ValueError,TypeError,KeyError):return None


def _ready(payload):
    from guide_playback import player_state
    from search_navigation import released
    request=payload['request'];source=payload['source']
    router=SimpleNamespace(_handle=-1,_search_async_owner=True)
    if not released(router,source,request['session'],request.get('window')):
        _mark('BLOCK_FOREIGN',payload);return False
    # No late continuation can replace a different session or directory.
    home=xbmcgui.Window(10000)
    current=player_state();saved=payload.get('player')
    if current is None or list(current)!=saved or home.getProperty('XtreamMate.LiveSession')!=payload.get('live_session',''):
        _mark('BLOCK_CONTEXT',payload);return False
    folder=xbmc.getInfoLabel('Container.FolderPath')
    if payload['directory']:
        parsed=urlsplit(folder);params=parse_qs(parsed.query)
        if (parsed.netloc!='plugin.video.xtreammate' or params.get('action')!=['global_search']
                or params.get('pid')!=[payload['pid']] or xbmc.getCondVisibility('Container.IsUpdating')):
            _mark('BLOCK_CONTEXT',payload);return False
    elif folder!=payload['folder']:
        _mark('BLOCK_CONTEXT',payload);return False
    return True


def run(token):
    """Called by the separate Kodi script, never by a native Guide callback."""
    from window_navigation import ownership
    home=xbmcgui.Window(10000);result=None;portal=None;router=None
    with ownership() as acquired:
        if not acquired:
            if valid_token(token):
                home.clearProperty(PREFIX+token)
                if home.getProperty(LATEST)==token:home.clearProperty(LATEST)
            _mark('BLOCK_OWNER',{});return False
        payload=_consume(token)
        if payload is None:return False
        try:
            from portals import get_by_id
            portal=get_by_id(payload['pid'])
            if not portal or not portal.get('enabled',True) or portal.get('type')!=payload['portal_type']:
                _mark('BLOCK_CONTEXT',payload);return False
            if not _ready(payload):return False
            # Router-compatible action object; no top-level main/migration import.
            router=SimpleNamespace(_handle=-1,_params={'pid':payload['pid']},
                _navigation_dispatch=payload['request']['session'],_search_async_owner=True,
                url=lambda **kw:'plugin://plugin.video.xtreammate/?'+urlencode({k:v for k,v in kw.items() if v is not None}))
            def client(p):
                from xtream import XtreamClient
                if p.get('type')=='xtream':return XtreamClient(p['xc_host'],p['xc_user'],p['xc_pass'])
                return None
            router._xc=client
            _mark('ASYNC_READY',payload)
            from search_navigation import guide_flow
            from owner_dispatch import open_owned_window
            source=payload['source'];request=payload['request']
            if source=='grid':
                from guide_grid_window import GuideGridWindow
                result=guide_flow(router,portal,open_owned_window,GuideGridWindow,'XCMateGuideGrid.xml',source,initial=request)
            elif source=='guide':
                from guide_window import GuideWindow
                result=guide_flow(router,portal,open_owned_window,GuideWindow,'XCMateGuide.xml',source,initial=request)
            else:
                from media_window import open_search
                result=open_search(router,portal,request.get('query'),request['session'])
        except Exception:
            # Fixed code only, never private payloads or exception messages.
            _mark('ASYNC_FAILED',payload)
            from localization import tr
            xbmcgui.Dialog().notification('XCMate',tr(32910));return False
    if result is not None:return handoff(router,portal,result)
    return True

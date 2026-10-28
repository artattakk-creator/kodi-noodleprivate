"""Instant Now/Next guide data for the on-video channel list and Kodi widgets.

This module only reads existing normalized EPG cache: remote button presses and
skin-widget refreshes must never wait for an external Xtream server.
"""
import time


def _as_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def _find_events(data, ids):
    for ident in ids:
        if ident and isinstance(data.get(str(ident)), list):
            return data[str(ident)]
    return []


def guide_for_channel(cache, epg_id='', stream_id='', now=None):
    """Return now/next dict; empty strings mean the provider has no EPG data."""
    result = {'now': '', 'next': '', 'description': '', 'image': '',
              'now_time': '', 'now_end_time': '', 'next_time': '', 'next_end_time': '',
              'start': 0, 'stop': 0, 'next_start': 0, 'next_stop': 0,
              'progress': None, 'elapsed': None, 'remaining': None,
              'events': [], 'epg_id': '', 'source_index': None, 'reason': 'NO_DATA'}
    if not isinstance(cache, dict):
        return result
    ts = int(time.time() if now is None else now)
    # A manually mapped Xtream stream ID must override the provider's guide ID.
    ident = next((str(i) for i in (stream_id, epg_id)
                  if i and isinstance(cache.get(str(i)), list) and cache[str(i)]), '')
    events = cache.get(ident, [])
    result['epg_id'] = ident
    from epg_events import deduplicate
    clean=deduplicate(events,channel=ident)
    valid=[(e['start'],e['stop'],e['title'],e) for e in clean]
    result['events'] = [dict(e) for e in clean if e['stop']>ts][:48]
    current = next((item for item in valid if item[0] <= ts < item[1]), None)
    future = next((item for item in valid if item[0] > ts), None)
    if current:
        result['now'] = current[2]
        result['now_time'] = time.strftime('%H:%M', time.localtime(current[0]))
        result.update(start=current[0], stop=current[1], elapsed=ts-current[0],
                      remaining=current[1]-ts,
                      progress=max(0., min(1., (ts-current[0])/(current[1]-current[0]))),
                      now_end_time=time.strftime('%H:%M', time.localtime(current[1])),
                      source_index=current[3].get('_source_index'), reason='READY')
        result['description'] = str(current[3].get('descr') or current[3].get('description') or '')
        result['image'] = str(current[3].get('screenshot_uri') or '')
        # Following programme must begin after the current programme.
        future = next((item for item in valid if item[0] >= current[1]), None)
    if future:
        result['next'] = future[2]
        result['next_time'] = time.strftime('%H:%M', time.localtime(future[0]))
        result.update(next_start=future[0], next_stop=future[1],
                      next_end_time=time.strftime('%H:%M', time.localtime(future[1])))
        if not current: result['reason'] = 'FUTURE_ONLY'
        if not current: result['source_index'] = future[3].get('_source_index')
    return result


def resolve_guide(cache, epg_id='', stream_id='', now=None, client=None, mappings=None):
    """One local resolver for directory, TV snapshot and programme preview.

    Explicit mapping wins even if a stale stream alias remains in the cache.
    Cached short EPG is a fallback for missing *current* XMLTV data, never HTTP.
    """
    sid = str(stream_id or '')
    mapped = (mappings or {}).get(sid)
    if mapped:
        from epg_binding48 import qualified_cache
        result = guide_for_channel(qualified_cache(cache,mappings,sid), str(mapped), now=now)
        result['epg_id'] = str(mapped)
        result['mapping'] = 'MANUAL'
        if not result['events']: result['reason'] = 'MANUAL_ID_MISSING'
        return result
    result = guide_for_channel(cache, epg_id, sid, now)
    result['mapping'] = 'STREAM_ALIAS' if result['epg_id'] == sid and sid else 'PROVIDER_ID'
    if not result['now'] and client is not None and sid:
        short = cached_short_guide(client, sid, now)
        if short['now'] or (not result['next'] and short['next']):
            if short['now'] and not short['next'] and result['next_start']>=short['stop']:
                for key in ('next','next_time','next_end_time','next_start','next_stop'):
                    short[key]=result[key]
                short['events']+= [e for e in result['events'] if e['start']>=short['stop']]
                short['events']=short['events'][:48]
            short.update(epg_id=sid, mapping='SHORT_EPG', source_index=-1)
            return short
    return result


def programme_plot(info):
    parts = []
    if info.get('now'):
        parts.append('Jetzt {}: {}'.format(info.get('now_time', ''), info['now']).strip())
    if info.get('next'):
        parts.append('Danach {}: {}'.format(info.get('next_time', ''), info['next']).strip())
    if info.get('description'):
        parts.append(str(info['description']))
    return '\n'.join(parts) if parts else 'Zurzeit keine EPG-Daten vorhanden.'


def row_title(name, info):
    title = str(name)
    if info.get('now'):
        title += '  |  {}-{}  {}'.format(info.get('now_time',''),
                                        info.get('now_end_time',''), info['now'])
    if info.get('next'):
        title += '  |  Danach: ' + str(info['next'])
    return title

# Bounded asynchronous Xtream short-guide fallback for missing XMLTV data.
_SHORT_LOCK = None
_SHORT_INFLIGHT = set()
_SHORT_SEEN = {}
_SHORT_FAILED = {}

def _short_guide(raw, now=None):
    """Normalize cached get_short_epg events into XMLTV-compatible Now/Next."""
    import base64
    ts = int(time.time() if now is None else now)
    entries = raw.get('epg_listings', []) if isinstance(raw, dict) else []
    normalized = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        title = str(item.get('title') or '').strip()
        try:
            decoded = base64.b64decode(title, validate=True).decode('utf-8')
            if decoded.strip():
                title = decoded
        except (ValueError, TypeError, UnicodeError):
            pass
        start = _as_int(item.get('start_timestamp'))
        stop = _as_int(item.get('stop_timestamp') or item.get('end_timestamp'))
        if not stop:
            # Only an explicitly named seconds field is unambiguous. Generic
            # "duration" differs between providers; never invent its unit.
            duration = _as_int(item.get('duration_secs'))
            if 0 < duration <= 86400: stop = start + duration
        if start > 0 and stop > start and title:
            record=dict(item,name=title,start_timestamp=start,stop_timestamp=stop,_source_index=-1)
            description=str(item.get('description') or item.get('descr') or '')
            try: description=base64.b64decode(description,validate=True).decode('utf-8')
            except (ValueError,TypeError,UnicodeError): pass
            record['descr']=description
            normalized.append(record)
    from epg_events import deduplicate
    decisions=[];clean=deduplicate(normalized,channel='_short',decisions=decisions)
    result=guide_for_channel({'_short':clean},'_short',now=ts)
    result.update(raw_count=len(entries),unique_count=len(clean),duplicates=len(normalized)-len(clean),
                  dedup_decisions=decisions)
    return result

def cached_short_guide(client, stream_id, now=None):
    if not stream_id:
        return guide_for_channel({}, now=now)
    # Old four-event caches remain valid. Extended results use a separate key;
    # only the service may fill it, never remote navigation or local views.
    best=None
    for limit in (12,4):
        try:
            data=client._get_json('get_short_epg',
                extra={'stream_id':str(stream_id),'limit':limit},cached_only=True)
        except (OSError,TimeoutError,ValueError):
            # A failed extended cache must not hide a valid four-event cache.
            # Cache-only read: no new network retry or cache/config mutation.
            continue
        guide=_short_guide(data,now=now)
        if best is None or (bool(guide['now']),len(guide['events']))>(bool(best['now']),len(best['events'])):
            best=guide
    return best if best is not None else guide_for_channel({},now=now)

def _view_key(path):
    import hashlib,json,urllib.parse
    p=urllib.parse.urlsplit(path)
    q=dict(urllib.parse.parse_qsl(p.query))
    if p.scheme!='plugin' or p.netloc!='plugin.video.xtreammate' or q.get('action')!='live_channels':
        return ''
    data=[q.get('pid',''),q.get('group',''),q.get('page','0')]
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()


def prefetch_short_guides(portal, channels, limit=24, view_path=''):
    """Send a bounded page request to the long-lived service, not a GUI thread."""
    import json,uuid,xbmcgui
    if not isinstance(portal,dict) or portal.get('type') not in ('xtream','stb'): return
    sids=[str(sid) for ch in channels if (sid:=(ch.get('sid') if isinstance(ch,dict) else ch.extra.get('stream_id')))][:limit]
    if not sids: return
    request={'pid':str(portal['id']),'sids':sids,'at':time.time(),
             'nonce':uuid.uuid4().hex,'view':_view_key(view_path)}
    xbmcgui.Window(10000).setProperty('XtreamMate.ShortGuideRequest',json.dumps(request))


def refresh_visible_page(portal_id, view_key=''):
    """Refresh only our current sender page, never a player or another add-on."""
    import xbmc,urllib.parse
    try:
        path=xbmc.getInfoLabel('Container.FolderPath')
        key=_view_key(path)
        params=dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(path).query))
        if not key or params.get('pid')!=str(portal_id): return
        if view_key and key!=view_key: return
        if xbmc.getCondVisibility('Window.IsActive(fullscreenvideo)'): return
        xbmc.executebuiltin('Container.Refresh')
    except Exception:
        pass


_LAST_REQUEST=''


def poll_short_guides():
    import json,xbmcgui
    import portals
    global _LAST_REQUEST
    window=xbmcgui.Window(10000)
    raw=window.getProperty('XtreamMate.ShortGuideRequest')
    if not raw or len(raw)>8192: return
    try: request=json.loads(raw)
    except (ValueError,TypeError): return
    if not isinstance(request,dict) or request.get('nonce')==_LAST_REQUEST: return
    try:
        if not 0<=time.time()-float(request.get('at',0))<120: return
    except (ValueError,TypeError): return
    portal=portals.get_by_id(request.get('pid'))
    if not portal or not portal.get('enabled',True) or portal.get('type') not in ('xtream','stb'): return
    sids=request.get('sids')
    if not isinstance(sids,list): return
    sids=[sid for sid in sids[:24] if isinstance(sid,str) and 0<len(sid)<=256 and (portal.get('type')=='stb' or sid.isdecimal())]
    if _start_short_guides(portal,sids,str(request.get('view') or '')):
        _LAST_REQUEST=request['nonce']


def _start_short_guides(portal, sids, view_key=''):
    """Prefetch missing visible TV programmes without waiting in Kodi navigation."""
    import threading
    from concurrent.futures import ThreadPoolExecutor
    from xtream import XtreamClient
    global _SHORT_LOCK
    if _SHORT_LOCK is None:
        _SHORT_LOCK = threading.Lock()
    if not isinstance(portal, dict) or portal.get('type') not in ('xtream','stb'):
        return
    pid = str(portal['id'])
    current = time.time()
    with _SHORT_LOCK:
        if _SHORT_INFLIGHT:
            return False
        ids = [sid for sid in sids if current-_SHORT_SEEN.get((pid,sid),0)>1800
               and current-_SHORT_FAILED.get((pid,sid),0)>30]
        if not ids:
            return True
        _SHORT_INFLIGHT.add(pid)
    def worker():
        try:
            changed=[]
            if portal.get('type')=='stb':
                from source_adapters import for_portal
                xc=for_portal(portal)
            else: xc = XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
            def fetch(sid):
                cached=cached_short_guide(xc,sid)
                if (cached['now'] or cached['next']) and not (cached.get('duplicates') and cached.get('unique_count',0)<4):
                    _SHORT_SEEN[(pid,sid)]=time.time()
                    return
                try:
                    data=xc.get_short_epg(sid,limit=12,force_refresh=True)
                    guide=_short_guide(data)
                    # Optional diagnostics must never turn valid EPG into a
                    # failed fetch (e.g. inaccessible profile during shutdown).
                    try:
                        from epg_dedup_diagnostics import record
                        record(pid,sid,guide)
                    except Exception: pass
                    if guide['now'] or guide['next']:
                        _SHORT_SEEN[(pid,sid)]=time.time()
                        changed.append(sid)
                    else:
                        _SHORT_FAILED[(pid,sid)]=time.time()
                except Exception:
                    _SHORT_FAILED[(pid,sid)]=time.time()
            # Start/first visible channel is completed before lower priorities.
            if ids: fetch(ids[0])
            with ThreadPoolExecutor(max_workers=2) as executor:
                list(executor.map(fetch,ids[1:]))
            for history in (_SHORT_SEEN,_SHORT_FAILED):
                if len(history)>512:
                    for key in sorted(history,key=history.get)[:-512]:
                        history.pop(key,None)
            if changed:
                import xbmcgui,uuid
                xbmcgui.Window(10000).setProperty('XCMate.ShortGuideRevision.'+pid,uuid.uuid4().hex)
            if view_key and changed:
                # Never refresh an unrelated directory or steal fullscreen
                # focus when the user has left the requested sender page.
                refresh_visible_page(pid,view_key)
        finally:
            with _SHORT_LOCK:
                _SHORT_INFLIGHT.discard(pid)
    try:
        threading.Thread(target=worker,daemon=True,name='XCMateShortGuide').start()
    except RuntimeError:
        with _SHORT_LOCK: _SHORT_INFLIGHT.discard(pid)
        return False
    return True

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
              'now_time': '', 'next_time': ''}
    if not isinstance(cache, dict):
        return result
    ts = int(time.time() if now is None else now)
    # A manually mapped Xtream stream ID must override the provider's guide ID.
    events = _find_events(cache, (stream_id, epg_id))
    valid = []
    for e in events:
        if not isinstance(e, dict):
            continue
        start = _as_int(e.get('start_timestamp') or e.get('start'))
        end = _as_int(e.get('stop_timestamp') or e.get('end_timestamp') or e.get('stop'))
        title = str(e.get('name') or e.get('title') or '').strip()
        if start and end > start and title:
            valid.append((start, end, title, e))
    valid.sort(key=lambda x: x[0])
    current = next((item for item in valid if item[0] <= ts < item[1]), None)
    future = next((item for item in valid if item[0] > ts), None)
    if current:
        result['now'] = current[2]
        result['now_time'] = time.strftime('%H:%M', time.localtime(current[0]))
        result['description'] = str(current[3].get('descr') or current[3].get('description') or '')
        result['image'] = str(current[3].get('screenshot_uri') or '')
        # Following programme must begin after the current programme.
        future = next((item for item in valid if item[0] >= current[1]), future)
    if future:
        result['next'] = future[2]
        result['next_time'] = time.strftime('%H:%M', time.localtime(future[0]))
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
        title += '  |  Jetzt: ' + str(info['now'])
    if info.get('next'):
        title += '  |  Danach: ' + str(info['next'])
    return title

# Bounded asynchronous Xtream short-guide fallback for missing XMLTV data.
_SHORT_LOCK = None
_SHORT_INFLIGHT = set()
_SHORT_SEEN = {}

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
        if start and stop > start and title:
            normalized.append({'name': title, 'start_timestamp': start,
                               'stop_timestamp': stop})
    return guide_for_channel({'_short': normalized}, '_short', now=ts)

def cached_short_guide(client, stream_id, now=None):
    if not stream_id:
        return guide_for_channel({}, now=now)
    data = client._get_json('get_short_epg',
        extra={'stream_id': str(stream_id), 'limit': 4}, cached_only=True)
    return _short_guide(data, now=now)

def prefetch_short_guides(portal, channels, limit=24):
    """Prefetch missing visible TV programmes without waiting in Kodi navigation."""
    import threading
    from concurrent.futures import ThreadPoolExecutor
    from xtream import XtreamClient
    global _SHORT_LOCK
    if _SHORT_LOCK is None:
        _SHORT_LOCK = threading.Lock()
    if not isinstance(portal, dict) or portal.get('type') != 'xtream':
        return
    pid = str(portal['id'])
    sids = [str(ch.extra.get('stream_id')) for ch in channels
            if ch.extra.get('stream_id')][:limit]
    current = time.time()
    with _SHORT_LOCK:
        if pid in _SHORT_INFLIGHT:
            return
        ids = [sid for sid in sids if current-_SHORT_SEEN.get((pid,sid),0)>1800]
        if not ids:
            return
        _SHORT_INFLIGHT.add(pid)
        for sid in ids:
            _SHORT_SEEN[(pid,sid)] = current
    def worker():
        try:
            xc = XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
            def fetch(sid):
                if cached_short_guide(xc,sid)['now']:
                    return
                try:
                    xc.get_short_epg(sid,limit=4,force_refresh=True)
                except Exception:
                    pass
            with ThreadPoolExecutor(max_workers=3) as executor:
                list(executor.map(fetch,ids))
        finally:
            with _SHORT_LOCK:
                _SHORT_INFLIGHT.discard(pid)
    threading.Thread(target=worker,daemon=True,name='XCMateShortGuide').start()

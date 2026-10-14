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
    events = _find_events(cache, (epg_id, stream_id))
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

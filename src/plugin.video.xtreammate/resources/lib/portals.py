from profile_transaction import serialized
import json
import time
import uuid
import os
import stat
from typing import Optional

import xbmcvfs

from utils import addon_data_dir, error, info, debug


PORTAL_TYPES   = ['m3u', 'xtream', 'stb']
PORTAL_LABELS  = ['M3U Playlist', 'Xtream Codes', 'STB / Stalker Portal']

_DB_FILE = None

def _db_path():
    global _DB_FILE
    if not _DB_FILE:
        _DB_FILE = os.path.join(addon_data_dir(), 'portals.json')
    return _DB_FILE


from portal_snapshot import Snapshot,PortalReadError
_snapshot=Snapshot()


def _read(select=lambda rows:rows):
    try:return _snapshot.read(_db_path(),PORTAL_TYPES,select)
    except PortalReadError:raise
    except Exception as exc:
        raise PortalReadError('Portalliste kann nicht gelesen werden. Daten wurden nicht verändert.') from exc


def load_all() -> list:
    return _read()


@serialized
def save_all(portal_list: list):
    """Write atomically to Kodi's local profile, then verify it was persisted.

    v0.1.0 swallowed write errors and reported a successful installation even
    when portals.json did not exist. Never acknowledge an unverified save.
    """
    import tempfile
    path = _db_path()
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix='.xtreammate-portals-', dir=folder)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(portal_list, stream, indent=2, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    except Exception as exc:
        error('portals.save_all failed: {}'.format(type(exc).__name__))
        raise OSError('Portal konnte nicht gespeichert werden. Bitte Speicherplatz/Zugriff prüfen.') from exc
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    _snapshot.invalidate()
    actual = load_all()
    if actual != portal_list:
        raise OSError('Portal wurde geschrieben, konnte aber nicht verifiziert werden.')


def get_by_id(portal_id: str) -> Optional[dict]:
    return _read(lambda rows:next((p for p in rows if p.get('id')==portal_id),None))


def get_active() -> list:
    return _read(lambda rows:[p for p in rows if p.get('enabled',True)])


@serialized
def add(portal: dict, portal_id=None) -> dict:
    now = int(time.time())
    extra={k:portal[k] for k in ('source_schema','m3u_original','m3u_origin','provider_epg_enabled','stb_serial','stb_device_id') if k in portal}
    portal = {
        'id'      : str(portal_id or uuid.uuid4()),
        'name'    : portal.get('name', 'New Portal'),
        'type'    : portal.get('type', 'm3u'),
        'enabled' : portal.get('enabled', True),
        'm3u_url' : portal.get('m3u_url', ''),
        'xc_host' : portal.get('xc_host', ''),
        'xc_user' : portal.get('xc_user', ''),
        'xc_pass' : portal.get('xc_pass', ''),
        'stb_url' : portal.get('stb_url', ''),
        'stb_mac' : portal.get('stb_mac', '00:1A:79:00:00:00'),
        'epg_url'  : portal.get('epg_url', ''),
        'epg_show' : portal.get('epg_show', True),
        'include_live': portal.get('include_live', True),
        'include_vod': portal.get('include_vod', True),
        'include_series': portal.get('include_series', True),
        'start_group_id': portal.get('start_group_id', '*'),
        'start_stream_id': portal.get('start_stream_id', ''),
        'autoplay_start': portal.get('autoplay_start', False),
        'created' : now,
        'updated' : now,
    }
    portal.update(extra)
    portals = load_all()
    if any(p['id']==portal['id'] for p in portals): raise ValueError('portal ID already exists')
    portals.append(portal)
    save_all(portals)
    info('Portal added and verified')
    return portal


@serialized
def update(portal_id: str, changes: dict) -> bool:
    portals = load_all()
    for p in portals:
        if p.get('id') == portal_id:
            p.update(changes)
            p['updated'] = int(time.time())
            save_all(portals)
            info('Portal updated and verified')
            return True
    error(f'portals.update: id {portal_id} not found')
    return False


@serialized
def delete(portal_id: str) -> bool:
    portals = load_all()
    before  = len(portals)
    portals = [p for p in portals if p.get('id') != portal_id]
    if len(portals) < before:
        save_all(portals)
        _clear_cache_for(portal_id)
        info(f'Portal deleted: {portal_id}')
        return True
    return False


def toggle_enabled(portal_id: str) -> bool:
    p = get_by_id(portal_id)
    if not p:
        return False
    new_state = not p.get('enabled', True)
    update(portal_id, {'enabled': new_state})
    return new_state


@serialized
def move_up(portal_id: str):
    portals = load_all()
    idx = next((i for i, p in enumerate(portals) if p.get('id') == portal_id), -1)
    if idx > 0:
        portals[idx - 1], portals[idx] = portals[idx], portals[idx - 1]
        save_all(portals)


@serialized
def move_down(portal_id: str):
    portals = load_all()
    idx = next((i for i, p in enumerate(portals) if p.get('id') == portal_id), -1)
    if 0 <= idx < len(portals) - 1:
        portals[idx], portals[idx + 1] = portals[idx + 1], portals[idx]
        save_all(portals)


def _clear_cache_for(portal_id: str):
    from utils import cache_dir
    import xbmcvfs
    cd = cache_dir()
    _, files = xbmcvfs.listdir(cd)
    for fn in files:
        pass

    from utils import cache_clear
    cache_clear()


@serialized
def import_from_settings():
    from utils import setting, setting_bool, setting_int
    portals = load_all()
    if portals:
        return

    imported = 0
    for i in range(1, 4):
        if not setting_bool(f'playlist{i}_enabled', i == 1):
            continue
        ptype_i = setting_int(f'playlist{i}_type', 0)
        name    = setting(f'playlist{i}_name') or f'Playlist {i}'
        epg     = setting(f'playlist{i}_epg_url')

        if ptype_i == 0 or ptype_i == 1:
            url = setting(f'playlist{i}_url')
            if url:
                add({'name': name, 'type': 'm3u', 'm3u_url': url, 'epg_url': epg})
                imported += 1
        elif ptype_i == 2:
            host = setting(f'playlist{i}_xc_host')
            user = setting(f'playlist{i}_xc_user')
            pwd  = setting(f'playlist{i}_xc_pass')
            if host and user:
                add({'name': name, 'type': 'xtream',
                     'xc_host': host, 'xc_user': user, 'xc_pass': pwd,
                     'epg_url': epg})
                imported += 1
        elif ptype_i == 3:
            url = setting(f'playlist{i}_stb_url')
            mac = setting(f'playlist{i}_stb_mac')
            if url and mac:
                add({'name': name, 'type': 'stb',
                     'stb_url': url, 'stb_mac': mac, 'epg_url': epg})
                imported += 1

    if imported:
        info(f'Migrated {imported} playlist(s) from settings to portal DB')


def type_label(ptype: str) -> str:
    return {'m3u': 'M3U', 'xtream': 'Xtream Codes', 'stb': 'STB/Stalker'}.get(ptype, ptype)


def portal_summary(p: dict) -> str:
    t = type_label(p.get('type', ''))
    if p['type'] == 'm3u':
        detail = p.get('m3u_url', '')[:50]
    elif p['type'] == 'xtream':
        detail = p.get('xc_host', '')
    else:
        detail = f"{p.get('stb_url', '')}  [{p.get('stb_mac', '')}]"
    enabled = '' if p.get('enabled', True) else '  (disabled)'
    return f'[{t}]  {detail}{enabled}'


import re as _re
import urllib.parse as _up

_XC_GET_PHP = _re.compile(
    r'^(https?://[^/]+)/get\.php\?.*?username=([^&]+).*?password=([^&]+)',
    _re.IGNORECASE
)
_XC_SLASH = _re.compile(
    r'^(https?://[^/]+(?::\d+)?)/([^/\?]+)/([^/\?]+)(?:/|\?|$)',
    _re.IGNORECASE
)


def detect_xtream(url: str) -> Optional[dict]:
    """
    Try to extract Xtream Codes credentials from an M3U URL.

    Returns {'xc_host': ..., 'xc_user': ..., 'xc_pass': ...}
    or None if the URL doesn't look like an Xtream endpoint.

    Detection is done purely by URL pattern - no network request needed.
    Called when saving an M3U portal and optionally on first load.
    """
    if not url:
        return None

    url = url.strip()


    m = _XC_GET_PHP.match(url)
    if m:
        host = m.group(1)
        user = _up.unquote(m.group(2))
        pwd  = _up.unquote(m.group(3).split('&')[0])
        return {'xc_host': host, 'xc_user': user, 'xc_pass': pwd}

    _SKIP = {'live', 'movie', 'series', 'vod', 'stream', 'hls', 'ts', 'play',
             'get.php', 'player_api.php', 'panel_api.php', 'xmltv.php'}
    m2 = _XC_SLASH.match(url)
    if m2:
        host = m2.group(1)
        user = _up.unquote(m2.group(2))
        pwd  = _up.unquote(m2.group(3))
        if (user.lower() not in _SKIP and pwd.lower() not in _SKIP
                and len(user) >= 4 and '.' not in user
                and len(pwd) >= 4 and '.' not in pwd):
            return {'xc_host': host, 'xc_user': user, 'xc_pass': pwd}

    return None

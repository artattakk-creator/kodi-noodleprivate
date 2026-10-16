"""Per-portal XMLTV source and channel mapping manager for Kodi/Android.

Built-in programme IDs take precedence; external feeds fill missing IDs.
Saved sender mappings take precedence for individual Xtream streams.
Configuration is separate from Kodi caches and survives add-on upgrades.
"""
import gzip
import io
import json
import os
import re
import tempfile
import unicodedata
import uuid
from urllib.parse import urlsplit

from utils import addon_data_dir, cache_key, cache_get, cache_set, http_get, error

MAX_XML_BYTES = 80 * 1024 * 1024
INDEX_TTL = 30 * 86400

# Public third-party XMLTV links; availability and channel coverage can change.
# Presets are opt-in, never fetched merely because XCMate has been installed.
PRESET_FEEDS = (
    ('de_master', 'Deutschland · Kaimandura Master',
     'https://kaimandura.github.io/epg-de/DE-MASTER.xml.gz'),
    ('de_epgshare', 'Deutschland · EPGShare01',
     'https://epgshare01.online/epgshare01/epg_ripper_DE1.xml.gz'),
    ('at_epgshare', 'Österreich · EPGShare01',
     'https://epgshare01.online/epgshare01/epg_ripper_AT1.xml.gz'),
    ('ch_epgshare', 'Schweiz · EPGShare01',
     'https://epgshare01.online/epgshare01/epg_ripper_CH1.xml.gz'),
    ('nl_epgshare', 'Niederlande · EPGShare01 (optional)',
     'https://epgshare01.online/epgshare01/epg_ripper_NL1.xml.gz'),
)


def add_presets(portal_id, preset_keys):
    """Install selected XMLTV feeds idempotently, without touching existing ones."""
    wanted = set(preset_keys)
    known = {key for key, _, _ in PRESET_FEEDS}
    if wanted - known:
        raise ValueError('Unbekanntes EPG-Paket')
    state = configuration(portal_id)
    existing = {str(item.get('uri', '')) for item in state['sources']}
    added = []
    for key, title, uri in PRESET_FEEDS:
        if key not in wanted or uri in existing:
            continue
        state['sources'].append({
            'id': uuid.uuid4().hex, 'name': title, 'uri': uri,
            'local': False, 'enabled': True,
        })
        existing.add(uri)
        added.append(key)
    if added:
        _save(portal_id, state)
    return added


def _file_path():
    return os.path.join(addon_data_dir(), 'xtreammate_epg_sources.json')


def _load_all():
    path = _file_path()
    if not os.path.isfile(path):
        return {}
    with open(path, 'r', encoding='utf-8') as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError('Ungültige EPG-Konfiguration')
    return data


def _write_all(data):
    folder = os.path.dirname(_file_path())
    os.makedirs(folder, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.xtreammate-epg-', dir=folder)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, _file_path())
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def configuration(portal_id):
    entry = _load_all().get(str(portal_id), {})
    if not isinstance(entry, dict):
        raise ValueError('Ungültige Portal-EPG-Konfiguration')
    return {
        'sources': [dict(s) for s in entry.get('sources', []) if isinstance(s, dict)],
        'mappings': dict(entry.get('mappings', {})),
    }


def _save(portal_id, state):
    all_data = _load_all()
    all_data[str(portal_id)] = state
    _write_all(all_data)


def add_source(portal_id, title, uri, local=False):
    uri = str(uri).strip()
    if not uri:
        raise ValueError('Die EPG-Adresse fehlt')
    if local:
        if '://' in uri and not uri.startswith(('special://', 'smb://', 'nfs://',
                                                 'content://', 'file://')):
            raise ValueError('Nicht unterstützter Dateipfad')
    else:
        parsed = urlsplit(uri)
        if parsed.scheme.lower() not in ('http', 'https') or not parsed.netloc:
            raise ValueError('Bitte eine gültige HTTP- oder HTTPS-Adresse eingeben')
    state = configuration(portal_id)
    if any(s.get('uri') == uri for s in state['sources']):
        raise ValueError('Diese Quelle wurde bereits hinzugefügt')
    item = {'id': uuid.uuid4().hex, 'name': str(title).strip() or 'XMLTV',
            'uri': uri, 'local': bool(local), 'enabled': True}
    state['sources'].append(item)
    _save(portal_id, state)
    return item


def edit_source(portal_id, source_id, operation):
    state = configuration(portal_id)
    index = next((i for i, s in enumerate(state['sources'])
                  if s.get('id') == source_id), -1)
    if index < 0:
        return False
    if operation == 'toggle':
        s = state['sources'][index]
        s['enabled'] = not s.get('enabled', True)
    elif operation == 'delete':
        del state['sources'][index]
    elif operation in ('up', 'down'):
        dest = index + (-1 if operation == 'up' else 1)
        if dest < 0 or dest >= len(state['sources']):
            return False
        state['sources'][index], state['sources'][dest] = (
            state['sources'][dest], state['sources'][index])
    else:
        raise ValueError('Ungültige EPG-Aktion')
    _save(portal_id, state)
    return True


def set_mapping(portal_id, stream_id, epg_id):
    state = configuration(portal_id)
    sid = str(stream_id).strip()
    eid = str(epg_id).strip()
    if not sid:
        raise ValueError('Sender-ID fehlt')
    if eid:
        state['mappings'][sid] = eid
    else:
        state['mappings'].pop(sid, None)
    _save(portal_id, state)


def _read_source(source):
    uri = str(source.get('uri') or '')
    if source.get('local'):
        import xbmcvfs
        f = xbmcvfs.File(uri)
        try:
            raw = f.readBytes(MAX_XML_BYTES + 1)
        finally:
            f.close()
    else:
        if urlsplit(uri).scheme.lower() not in ('http', 'https'):
            raise ValueError('Nur HTTP(S)-EPG-Adressen sind erlaubt')
        raw, _ = http_get(uri, timeout=20)
    raw = bytes(raw) if not isinstance(raw, bytes) else raw
    if len(raw) > MAX_XML_BYTES:
        raise ValueError('XMLTV-Datei ist zu groß (max. 80 MB)')
    if raw[:2] == b'\x1f\x8b':
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as archive:
            raw = archive.read(MAX_XML_BYTES + 1)
        if len(raw) > MAX_XML_BYTES:
            raise ValueError('Entpackte XMLTV-Daten sind zu groß')
    if b'<!DOCTYPE' in raw[:4096].upper() or b'<!ENTITY' in raw[:4096].upper():
        raise ValueError('XML-Dokument mit DTD/Entities nicht erlaubt')
    return raw


def _channels_cache_key(portal_id):
    return cache_key('xtreammate_epg_channel_index_' + str(portal_id))


def available_channels(portal_id):
    result = cache_get(_channels_cache_key(portal_id), max_age=INDEX_TTL)
    return result if isinstance(result, dict) else {}


def _channel_name_key(value):
    """Conservative exact-name comparison; no uncertain title mapping."""
    value = unicodedata.normalize('NFKD', str(value or '')).casefold()
    value = re.sub(r'^\s*(?:de|ger|at|aut|ch|sui|nl)\s*[|:–-]\s*', '', value)
    value = re.sub(r'\s*(?:uhd|fhd|hd|sd|4k)\s*$', '', value)
    return re.sub(r'[^a-z0-9]+', '', value)


def _link_cached_xtream_channels(portal_id, programmes, channel_index):
    """Map unambiguous channel names only; preserve provider and manual IDs.

    This runs during EPG refresh, never on the remote control/UI thread.
    Ambiguous station names from several countries require manual mapping.
    """
    try:
        import portals
        from xtream import XtreamClient
        portal = portals.get_by_id(portal_id)
        if not portal or portal.get('type') != 'xtream':
            return 0
        client = XtreamClient(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
        streams = client.get_cached_catalog('get_live_streams') or []
    except Exception as exc:
        error('EPG auto-link unavailable: {}'.format(type(exc).__name__))
        return 0
    names = {}
    for channel_id, display_name in channel_index.items():
        if not programmes.get(channel_id):
            continue
        key = _channel_name_key(display_name)
        if not key:
            continue
        if key in names and names[key] != channel_id:
            names[key] = None  # ambiguous: refuse to guess
        elif key not in names:
            names[key] = channel_id
    count = 0
    for channel in streams:
        if not isinstance(channel, dict):
            continue
        stream_id = str(channel.get('stream_id') or '').strip()
        provider_id = str(channel.get('epg_channel_id') or '').strip()
        if not stream_id or programmes.get(stream_id) or (
                provider_id and programmes.get(provider_id)):
            continue
        source_id = names.get(_channel_name_key(channel.get('name')))
        if source_id and source_id in programmes:
            programmes[stream_id] = programmes[source_id]
            count += 1
    return count


def merge_sources(portal_id, builtin_programmes, parse_xmltv):
    """Fetch enabled XMLTV feeds; retain built-in data when any feed fails.

    Feed order is priority order: the last enabled feed wins for overlapping
    channel IDs. Explicit sender-to-XMLTV mapping is applied last and wins.
    """
    state = configuration(portal_id)
    merged = dict(builtin_programmes or {})
    index = {}
    successes, failures = 0, 0
    for source in state['sources']:
        if not source.get('enabled', True):
            continue
        try:
            raw = _read_source(source)
            channels, programmes = parse_xmltv(raw)
            if not programmes:
                raise ValueError('XMLTV enthält keine Sendungen')
            index.update(channels)
            for channel_id, entries in programmes.items():
                if entries and not merged.get(channel_id):
                    merged[channel_id] = entries
            successes += 1
        except Exception as exc:
            failures += 1
            error('EPG source failed ({}): {}'.format(
                source.get('id', '')[:8], type(exc).__name__))
    if index:
        cache_set(_channels_cache_key(portal_id), index)
        linked = _link_cached_xtream_channels(portal_id, merged, index)
    for stream_id, xmltv_id in state['mappings'].items():
        if xmltv_id in merged:
            merged[str(stream_id)] = merged[xmltv_id]
    return merged, successes, failures


def _choose_portal():
    import portals
    import xbmcgui
    active = portals.get_active()
    if not active:
        xbmcgui.Dialog().ok('XCMate EPG', 'Bitte zuerst einen TV-Zugang einrichten.')
        return None
    if len(active) == 1:
        return active[0]
    i = xbmcgui.Dialog().select('EPG: TV-Liste wählen', [p['name'] for p in active])
    return active[i] if 0 <= i < len(active) else None


def _choose_preset(portal):
    """Native Kodi picker, deliberately avoiding multiple automatic downloads."""
    import xbmcgui
    from epg import warmup_async
    dialog = xbmcgui.Dialog()
    existing = {s.get('uri') for s in configuration(portal['id'])['sources']}
    labels = [('✓ ' if uri in existing else '＋ ') + title
              for _, title, uri in PRESET_FEEDS]
    labels.append('＋ DACH-Paket: Deutschland (2), Österreich, Schweiz')
    selection = dialog.select('XCMate – EPG-Pakete auswählen', labels)
    if selection < 0:
        return False
    keys = ([PRESET_FEEDS[selection][0]] if selection < len(PRESET_FEEDS)
            else ['de_master', 'de_epgshare', 'at_epgshare', 'ch_epgshare'])
    added = add_presets(portal['id'], keys)
    if not added:
        dialog.notification('XCMate EPG', 'EPG-Paket bereits vorhanden')
        return False
    dialog.notification('XCMate EPG',
                        '{} Quelle(n) ergänzt – EPG wird aktualisiert'.format(len(added)))
    warmup_async(portal['id'], portal, force=True)
    return True


def _manage_source(portal, source):
    import xbmcgui
    d = xbmcgui.Dialog()
    choice = d.select(str(source.get('name') or 'XMLTV'), [
        'Quelle ' + ('deaktivieren' if source.get('enabled', True) else 'aktivieren'),
        'Priorität erhöhen', 'Priorität senken',
        'Quelle löschen', 'Zurück'])
    operations = ('toggle', 'up', 'down', 'delete')
    if choice < 0 or choice >= len(operations):
        return False
    if choice == 3 and not d.yesno('XCMate EPG', 'EPG-Quelle wirklich löschen?'):
        return False
    return edit_source(portal['id'], source['id'], operations[choice])


def _choose_mapping(portal):
    import xbmcgui
    d = xbmcgui.Dialog()
    if portal.get('type') != 'xtream':
        d.ok('XCMate EPG', 'Manuelle Zuordnung wird derzeit für Xtream Codes unterstützt.')
        return
    from xtream import XtreamClient
    xc = XtreamClient(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
    streams = xc.get_cached_catalog('get_live_streams') or []
    streams = sorted((x for x in streams if isinstance(x, dict) and x.get('stream_id')),
                     key=lambda x: str(x.get('name') or '').casefold())
    index = available_channels(portal['id'])
    if not streams:
        d.ok('XCMate EPG', 'Senderkatalog wird noch geladen. Bitte später erneut versuchen.')
        return
    if not index:
        d.ok('XCMate EPG', 'Zuerst eine XMLTV-Quelle hinzufügen und EPG aktualisieren.')
        return
    state = configuration(portal['id'])
    labels = []
    for s in streams:
        sid = str(s['stream_id'])
        eid = state['mappings'].get(sid, '')
        labels.append(str(s.get('name') or sid) + (('  →  ' + eid) if eid else ''))
    i = d.select('Xtream-Sender zuordnen', labels)
    if i < 0:
        return
    sid = str(streams[i]['stream_id'])
    channels = sorted(index.items(), key=lambda x: str(x[1]).casefold())
    options = ['Zuordnung entfernen'] + [
        '{}  [{}]'.format(name, cid) for cid, name in channels]
    selected = state['mappings'].get(sid, '')
    preselect = next((j + 1 for j, (cid, _) in enumerate(channels)
                      if cid == selected), 0)
    j = d.select('XMLTV-Kanal wählen', options, preselect=preselect)
    if j >= 0:
        set_mapping(portal['id'], sid, channels[j - 1][0] if j else '')
        d.notification('XCMate EPG', 'Zuordnung gespeichert – EPG bitte aktualisieren')


def manage(portal=None):
    """Kodi-native remote navigable EPG settings, including Android file picker."""
    import xbmcgui
    from epg import warmup_async
    portal = portal or _choose_portal()
    if not portal:
        return
    d = xbmcgui.Dialog()
    while True:
        state = configuration(portal['id'])
        source_labels = [('✓  ' if s.get('enabled', True) else '○  ') +
                         str(s.get('name') or 'XMLTV') for s in state['sources']]
        options = [
            '➕ EPG-Paket Deutschland / Österreich / Schweiz / NL',
            '➕ XMLTV-Adresse (HTTP/HTTPS) hinzufügen',
            '➕ XMLTV-Datei (.xml / .gz) auswählen',
            '↻ EPG-Quellen jetzt aktualisieren',
            '↔ Xtream-Sender einem XMLTV-Kanal zuordnen',
        ] + source_labels + ['Zurück']
        choice = d.select('XCMate – EPG-Verwaltung · ' + portal['name'], options)
        if choice < 0 or choice == len(options) - 1:
            return
        try:
            if choice == 0:
                _choose_preset(portal)
            elif choice == 1:
                url = d.input('XMLTV-URL eingeben', type=xbmcgui.INPUT_ALPHANUM)
                if url:
                    name = d.input('Name dieser EPG-Quelle', defaultt='XMLTV URL',
                                   type=xbmcgui.INPUT_ALPHANUM)
                    add_source(portal['id'], name, url)
            elif choice == 2:
                uri = d.browse(1, 'XMLTV-Datei auswählen', 'files',
                               '.xml|.gz|.xml.gz', False, False, '')
                if uri:
                    name = d.input('Name dieser EPG-Quelle', defaultt='Lokales XMLTV',
                                   type=xbmcgui.INPUT_ALPHANUM)
                    add_source(portal['id'], name, uri, local=True)
            elif choice == 3:
                warmup_async(portal['id'], portal, force=True)
                d.notification('XCMate EPG', 'Aktualisierung im Hintergrund gestartet')
            elif choice == 4:
                _choose_mapping(portal)
            else:
                _manage_source(portal, state['sources'][choice - 5])
        except Exception as exc:
            error('EPG manager action failed: {}'.format(type(exc).__name__))
            d.ok('XCMate EPG', 'Aktion fehlgeschlagen: ' + str(exc)[:160])

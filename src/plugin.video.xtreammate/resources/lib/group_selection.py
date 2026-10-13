"""Persistent per-portal Xtream live/VOD/series category controls.

Selections are keyed by provider category ID, so provider renames do not undo
choices. Supports the 0.1.0 JSON layout (portal ID -> list of live IDs).
"""
import json
import os
import tempfile
from utils import addon_data_dir

KINDS = ('live', 'vod', 'series')
LABELS = {'live': 'Sendergruppen', 'vod': 'Filmgruppen', 'series': 'Seriengruppen'}


def _path():
    return os.path.join(addon_data_dir(), 'xtreammate_groups.json')


def _read():
    path = _path()
    if not os.path.isfile(path):
        return {}
    with open(path, encoding='utf-8') as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError('Ungültige Datei mit gespeicherten Sendergruppen')
    return value


def _write(root):
    path = _path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.xm-groups-', dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(root, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _state(root, portal_id, kind):
    pid = str(portal_id)
    entries = root.get('_v2', {})
    state = entries.get(pid, {}).get(kind) if isinstance(entries, dict) else None
    if isinstance(state, dict) and isinstance(state.get('enabled'), list):
        return {'enabled': set(str(x) for x in state['enabled']),
                'known': set(str(x) for x in state.get('known', state['enabled'])),
                'auto_new': bool(state.get('auto_new', False))}
    if kind == 'live' and isinstance(root.get(pid), list):
        # v0.1.0 had only selected live IDs, never recorded known categories.
        legacy = set(str(x) for x in root[pid])
        return {'enabled': legacy, 'known': legacy, 'auto_new': False}
    return None  # First use: show all, no prior restriction.


def load(portal_id, kind='live'):
    state = _state(_read(), portal_id, kind)
    return None if state is None else state['enabled']


def save(portal_id, categories, kind='live', known=None, auto_new=False):
    if kind not in KINDS:
        raise ValueError('Ungültige Gruppenart')
    root = _read()
    ids = list(dict.fromkeys(str(x) for x in categories))
    known_ids = list(dict.fromkeys(str(x) for x in (known if known is not None else ids)))
    root.setdefault('_v2', {}).setdefault(str(portal_id), {})[kind] = {
        'enabled': ids, 'known': known_ids, 'auto_new': bool(auto_new)}
    _write(root)


def enabled_ids(portal_id, kind, categories):
    """Compute effective IDs, respecting opt-in auto-enable of newly found IDs."""
    ids = {str(c['category_id']) for c in categories if c.get('category_id') is not None}
    state = _state(_read(), portal_id, kind)
    if state is None:
        return ids
    enabled = state['enabled']
    if state['auto_new']:
        return (enabled | (ids - state['known'])) & ids
    return enabled & ids


def filter_channels(channels, portal_id):
    selected = load(portal_id, 'live')
    if selected is None:
        return list(channels)
    # Auto-new categories are applied at catalog refresh, not by silently
    # re-enabling categories the user explicitly switched off.
    state = _state(_read(), portal_id, 'live')
    new = set()
    if state['auto_new']:
        new = {str(ch.extra.get('category_id', '')) for ch in channels} - state['known']
    return [ch for ch in channels if str(ch.extra.get('category_id', '')) in selected | new]


def filter_entries(entries, portal_id, kind):
    """Filter movie/series dictionaries without restricting pagination."""
    state = _state(_read(), portal_id, kind)
    if state is None:
        return list(entries)
    chosen = state['enabled']
    if state['auto_new']:
        chosen = chosen | ({str(e.get('category_id', '')) for e in entries} - state['known'])
    return [e for e in entries if str(e.get('category_id', '')) in chosen]


def _categories(portal, kind, force=True):
    from xtream import XtreamClient
    xc = XtreamClient(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
    method = getattr(xc, {'live': 'get_live_categories', 'vod': 'get_vod_categories',
                          'series': 'get_series_categories'}[kind])
    return [c for c in method(force_refresh=force) if isinstance(c, dict)
            and c.get('category_id') is not None]


def choose_groups(portal, kind='live'):
    """Kodi remote-friendly one-at-a-time toggles with Save/Cancel and bulk ops."""
    import xbmcgui
    if kind not in KINDS or portal.get('type') != 'xtream':
        return False
    dlg = xbmcgui.Dialog()
    cats = _categories(portal, kind)
    if not cats:
        dlg.ok('XtreamMate', 'Keine {} vom Server erhalten.'.format(LABELS[kind]))
        return False
    ids = [str(c['category_id']) for c in cats]
    state = _state(_read(), portal['id'], kind)
    old_known = state['known'] if state else set(ids)
    current = (state['enabled'] | (set(ids) - old_known) if state and state['auto_new']
               else state['enabled']) if state else set(ids)
    current &= set(ids)
    auto_new = state['auto_new'] if state else False
    first_index = 5
    while True:
        newly_found = set(ids) - old_known
        options = [
            '[B]✔ Auswahl speichern  ({} / {})[/B]'.format(len(current), len(ids)),
            '[B]Alle aktivieren[/B]',
            '[B]Alle deaktivieren[/B]',
            '[B]Neue aktivieren ({})[/B]'.format(len(newly_found)),
            'Zukünftig neue automatisch aktivieren: [B]{}[/B]'.format('AN' if auto_new else 'AUS'),
        ]
        for cat, cid in zip(cats, ids):
            label = str(cat.get('category_name') or cid)
            marker = '[COLOR lime]● AN[/COLOR]' if cid in current else '[COLOR orange]○ AUS[/COLOR]'
            suffix = ' [NEU]' if cid in newly_found else ''
            options.append('{}  {}{}'.format(marker, label, suffix))
        options.append('[Abbrechen – ohne Änderungen]')
        choice = dlg.select('XtreamMate – {} (OK umschalten)'.format(LABELS[kind]), options)
        if choice in (-1, len(options) - 1):
            return False
        if choice == 0:
            save(portal['id'], [i for i in ids if i in current], kind=kind,
                 known=ids, auto_new=auto_new)
            dlg.notification('XtreamMate', '{}: {} von {} aktiv'.format(
                LABELS[kind], len(current), len(ids)))
            return True
        if choice == 1:
            current = set(ids)
        elif choice == 2:
            current.clear()
        elif choice == 3:
            current |= newly_found
        elif choice == 4:
            auto_new = not auto_new
        else:
            key = ids[choice - first_index]
            if key in current:
                current.remove(key)
            else:
                current.add(key)


def manage_groups(portal):
    """Persistent TV/VOD/Series manager, available from home and portal settings."""
    import xbmcgui
    if portal.get('type') != 'xtream':
        return
    dlg = xbmcgui.Dialog()
    while True:
        choice = dlg.select('XtreamMate – Gruppen verwalten', [
            'Live-TV: Sendergruppen', 'Filme: Filmgruppen', 'Serien: Seriengruppen',
            'Zurück'])
        if choice < 0 or choice == 3:
            return
        try:
            choose_groups(portal, KINDS[choice])
        except Exception as exc:
            from utils import error
            error('XtreamMate group manager failed: {}'.format(type(exc).__name__))
            dlg.ok('XtreamMate', 'Die Gruppen konnten nicht geladen oder gespeichert werden. '
                    'Bitte Internetverbindung und lokalen Speicher prüfen.')

from profile_transaction import serialized
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


@serialized
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


def _categories(portal, kind, force=False):
    """Keep the cached Xtream category catalog unless explicit refresh is requested."""
    if portal.get('type') in ('m3u','stb'):
        from source_adapters import for_portal
        from catalog_sync import request
        if force: request(portal,kind,priority=0,force=True)
        return for_portal(portal).categories(kind)
    from xtream import XtreamClient
    xc = XtreamClient(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
    method = getattr(xc, {'live': 'get_live_categories',
                          'vod': 'get_vod_categories',
                          'series': 'get_series_categories'}[kind])
    categories = method(force_refresh=force) or []
    if not isinstance(categories, list):
        return []
    return [c for c in categories if isinstance(c, dict)
            and c.get('category_id') is not None]


def _menu_items(kind, current, ids, old_known, auto_new):
    """Group management shortcuts; individual toggling uses Kodi native checkboxes."""
    newly_found = set(ids) - old_known
    return [
        '[B]☑ Gruppen mit Checkboxen auswählen ({} / {})[/B]'.format(len(current), len(ids)),
        'Alle aktivieren',
        'Alle deaktivieren',
        'Neue aktivieren ({})'.format(len(newly_found)),
        'Neue Gruppen künftig automatisch: [B]{}[/B]'.format('AN' if auto_new else 'AUS'),
        'Kategorien vom Anbieter neu laden',
        '[COLOR lime][B]✓ Auswahl speichern ({} / {})[/B][/COLOR]'.format(len(current), len(ids)),
        'Abbrechen – Änderungen verwerfen',
    ]


def _checkbox_selection(dialog, kind, categories, ids, current, new_ids):
    """The list never closes on checkbox toggles; Kodi itself retains cursor focus."""
    labels = []
    for category, cid in zip(categories, ids):
        name = str(category.get('category_name') or cid)
        suffix = ' [COLOR yellow](NEU)[/COLOR]' if cid in new_ids else ''
        labels.append(name + suffix)
    initial = [index for index, cid in enumerate(ids) if cid in current]
    selected = __import__('menu_icons45').multiselect(dialog,
        'XCMate – {} (Haken setzen, unten OK = speichern)'.format(LABELS[kind]),
        labels, preselect=initial,default='list')
    if selected is None:
        return None
    return {ids[index] for index in selected if isinstance(index, int)
            and 0 <= index < len(ids)}


def choose_groups(portal, kind='live',categories=None,allow_refresh=True):
    """Persist changes once on Save; Back discards temporary checkbox selections."""
    import xbmcgui
    if kind not in KINDS or portal.get('type') not in ('xtream','m3u','stb'):
        return False
    dlg = xbmcgui.Dialog()
    cats = _categories(portal, kind) if categories is None else list(categories)
    if not cats:
        dlg.ok('XCMate', 'Keine {} vom Server erhalten.'.format(LABELS[kind]))
        return False
    ids = [str(c['category_id']) for c in cats]
    state = _state(_read(), portal['id'], kind)
    old_known = state['known'] if state else set(ids)
    current = (state['enabled'] | (set(ids) - old_known) if state and state['auto_new']
               else state['enabled']) if state else set(ids)
    current &= set(ids)
    auto_new = state['auto_new'] if state else False

    def commit():
        save(portal['id'], [cid for cid in ids if cid in current],
             kind=kind, known=ids, auto_new=auto_new)
        if portal.get('type') in ('m3u','stb'):
            from portals import update
            update(portal['id'],{'include_'+kind:bool(current)})
            portal['include_'+kind]=bool(current)
            from catalog_sync import request
            request(portal,kind,priority=1)
        elif portal.get('type')=='xtream':
            from portals import update
            update(portal['id'],{'include_'+kind:bool(current)})
            portal['include_'+kind]=bool(current)
            # Existing sync_kind skips already complete groups. Only added
            # group heads are requested; no force/full-provider restart.
            from catalog_delta import request
            previous=state['enabled'] if state else set()
            added=current-set(previous)
            for cid in sorted(added):request(portal,kind,cid)
        dlg.notification('XCMate', '{}: {} von {} aktiv'.format(
            LABELS[kind], len(current), len(ids)))
        return True

    while True:
        options = _menu_items(kind, current, ids, old_known, auto_new)
        try:
            choice = __import__('menu_icons45').select(dlg,'XCMate – {}'.format(LABELS[kind]),
                                options, preselect=0,default='list')
        except TypeError:
            choice = __import__('menu_icons45').select(dlg,'XCMate – {}'.format(LABELS[kind]), options,default='list')
        if choice in (-1, 7):
            return False
        if choice == 0:
            checked = _checkbox_selection(dlg, kind, cats, ids, current,
                                          set(ids) - old_known)
            if checked is not None:
                current = checked
                return commit()
        elif choice == 1:
            current = set(ids)
        elif choice == 2:
            current.clear()
        elif choice == 3:
            current |= set(ids) - old_known
        elif choice == 4:
            auto_new = not auto_new
        elif choice == 5:
            if not allow_refresh:
                from catalog_sync import request
                request(portal,kind,priority=0,force=True)
                dlg.notification('XCMate','Kategorien-Aktualisierung im Hintergrund angefordert.')
                continue
            try:
                updated = _categories(portal, kind, force=True)
                if updated:
                    cats = updated
                    ids = [str(c['category_id']) for c in cats]
                    if auto_new:
                        current |= set(ids) - old_known
                    current &= set(ids)
                else:
                    dlg.notification('XCMate', 'Keine neuen Gruppen vom Server erhalten.')
            except Exception:
                dlg.ok('XCMate', 'Kategorien konnten nicht aktualisiert werden. '
                       'Die bisherige Auswahl bleibt erhalten.')
        elif choice == 6:
            return commit()
        else:
            return False


def manage_groups(portal):
    """Persistent TV/VOD/Series manager, available from home and portal settings."""
    import xbmcgui
    if portal.get('type') not in ('xtream','m3u','stb'):
        return
    dlg = xbmcgui.Dialog()
    while True:
        choice = __import__('menu_icons45').select(dlg,'XCMate – Gruppen verwalten', [
            'Live-TV: Sendergruppen', 'Filme: Filmgruppen', 'Serien: Seriengruppen',
            'Zurück'],default='list')
        if choice < 0 or choice == 3:
            return
        try:
            choose_groups(portal, KINDS[choice])
        except Exception as exc:
            from utils import error
            error('XCMate group manager failed: {}'.format(type(exc).__name__))
            dlg.ok('XCMate', 'Die Gruppen konnten nicht geladen oder gespeichert werden. '
                    'Bitte Internetverbindung und lokalen Speicher prüfen.')

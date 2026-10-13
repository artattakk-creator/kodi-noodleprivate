"""Per-portal multi-select Xtream live categories; IDs are stable across renames."""
import json
import os
import tempfile
from utils import addon_data_dir


def _path():
    return os.path.join(addon_data_dir(), 'xtreammate_groups.json')


def load(portal_id):
    try:
        with open(_path(), encoding='utf-8') as fd:
            root = json.load(fd)
        selection = root.get(str(portal_id))
        if isinstance(selection, list):
            return set(str(x) for x in selection)
    except (OSError, TypeError, ValueError, AttributeError):
        pass
    return None    # None = all groups, including for old imported portals


def save(portal_id, categories):
    path = _path()
    try:
        with open(path, encoding='utf-8') as fd:
            root = json.load(fd)
        if not isinstance(root, dict):
            root = {}
    except (OSError, TypeError, ValueError):
        root = {}
    root[str(portal_id)] = list(dict.fromkeys(str(x) for x in categories))
    dirname = os.path.dirname(path)
    os.makedirs(dirname, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.xm-groups-', dir=dirname)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(root, out, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def filter_channels(channels, portal_id):
    chosen = load(portal_id)
    if chosen is None:
        return list(channels)
    return [c for c in channels if str(c.extra.get('category_id', '')) in chosen]


def choose_groups(portal):
    import xbmcgui
    from xtream import XtreamClient
    xc = XtreamClient(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
    cats = xc.get_live_categories()
    cats = [c for c in cats if isinstance(c, dict) and c.get('category_id') is not None]
    if not cats:
        xbmcgui.Dialog().ok('XtreamMate', 'Der Server hat keine Sendergruppen geliefert.')
        return False
    current = load(portal['id'])
    ids = [str(c['category_id']) for c in cats]
    preselect = list(range(len(cats))) if current is None else [i for i, cid in enumerate(ids) if cid in current]
    chosen = xbmcgui.Dialog().multiselect('XtreamMate – Sendergruppen auswählen',
            [str(c.get('category_name', c['category_id'])) for c in cats], preselect=preselect)
    if chosen is None:
        return False
    save(portal['id'], [ids[i] for i in chosen])
    xbmcgui.Dialog().notification('XtreamMate', '{} von {} Gruppen aktiviert'.format(len(chosen), len(ids)))
    return True

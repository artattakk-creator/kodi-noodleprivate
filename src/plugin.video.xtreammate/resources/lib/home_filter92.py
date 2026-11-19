"""Home-only provider category selection, keyed to the existing profile/account."""
import hashlib
import json
import re

KEY = 'home_vod_groups92'
ADULT_LABEL = re.compile(r'\b(?:adult|erotik|erotic|xxx)\b|(?<!\d)18\s*\+(?!\d)', re.IGNORECASE)


def context(pid):
    from portals import get_by_id
    from epg_handoff63 import profile_scope
    from portal_snapshot import PortalReadError

    try:
        portal = get_by_id(str(pid)) or {}
    except PortalReadError as exc:
        raise OSError('HOME_FILTER_PORTAL_UNAVAILABLE') from exc
    identity = [profile_scope(), str(pid)] + [
        portal.get(key) for key in ('id', 'xc_host', 'xc_user', 'xc_pass', 'type')
    ]
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()


def validate(value):
    if not isinstance(value, dict) or len(value) > 32:
        raise ValueError('HOME_FILTER_INVALID')
    for key, ids in value.items():
        if len(key) != 64 or not isinstance(ids, list) or len(ids) > 2048:
            raise ValueError('HOME_FILTER_INVALID')
        if any(not isinstance(cid, str) or len(cid) > 160 for cid in ids):
            raise ValueError('HOME_FILTER_INVALID')
    return value


def read():
    import xbmcaddon
    from settings_guard96 import value

    raw = value(KEY, xbmcaddon.Addon('plugin.video.xtreammate'))
    if not raw:
        return {}
    if len(raw.encode()) > 65536:
        raise ValueError('HOME_FILTER_LIMIT')
    return validate(json.loads(raw))


def selected(pid):
    return read().get(context(pid))


def allowed(pid, ids):
    chosen = selected(pid)
    return set(ids) if chosen is None else set(ids).intersection(chosen)


def signature(pid):
    try:
        value = selected(pid)
    except (OSError, ValueError, TypeError):
        # Isolate cached rows from any readable policy while settings are
        # unavailable. The data query reports the error instead of showing all.
        return 'HOME_FILTER_UNAVAILABLE'
    return '' if value is None else hashlib.sha256(json.dumps(sorted(value)).encode()).hexdigest()


def save(pid, ids):
    import xbmcaddon

    value = read()
    value[context(pid)] = sorted(set(map(str, ids)))
    raw = json.dumps(validate(value), sort_keys=True, separators=(',', ':'))
    if len(raw.encode()) > 65536:
        raise ValueError('HOME_FILTER_LIMIT')
    addon = xbmcaddon.Addon('plugin.video.xtreammate')
    addon.setSetting(KEY, raw)
    if json.loads(addon.getSetting(KEY)) != value or read() != value:
        raise OSError('HOME_FILTER_READBACK')


def refresh_movies(pid):
    import xbmcgui
    from widget_hooks45 import read
    from widget_snapshot85 import invalidate89

    invalidate89({'id': pid}, 'vod')
    owned, shared = set(), set()
    for binding in read().get('bindings', []):
        hooks = {name for name in binding.get('hooks', []) if name.startswith('XCMate.Widget45.Reload.')}
        if binding.get('pid') == str(pid) and binding.get('kind') == 'vod':
            owned.update(hooks)
        else:
            shared.update(hooks)
    window = xbmcgui.Window(10000)
    token = 'home-filter.' + signature(pid)
    for hook in owned - shared:
        window.setProperty(hook, token)


def manage(portal):
    import xbmcgui
    from artwork_ui import job
    from library_index import IndexReadError
    from localization import tr
    from menu_icons45 import multiselect, select
    from widget_data41 import WidgetReader

    dialog = xbmcgui.Dialog()
    heading = tr(38729)
    if not portal:
        dialog.ok(heading, tr(32466))
        return

    pid = portal['id']

    def groups(cancel, progress):
        return WidgetReader(pid)._query(
            'SELECT cid,title FROM groups WHERE pid=? AND kind=? ORDER BY ordinal,cid',
            (str(pid), 'vod'),
        )

    try:
        chosen = selected(pid)
        rows = job(groups)
    except (IndexReadError, OSError, ValueError, TypeError):
        dialog.ok(heading, tr(38983))
        return
    if rows is None:
        return
    if not rows:
        dialog.ok(heading, tr(38984))
        return

    ids = [row['cid'] for row in rows]
    titles = [row['title'] or row['cid'] for row in rows]
    current = set(ids)
    original = current if chosen is None else set(chosen)
    draft = original.copy()
    commands = [tr(38980), tr(32704), tr(32705), tr(38981), tr(32709), tr(32708)]
    if chosen is None:
        commands.append(tr(38982))
    while True:
        choice = select(dialog, tr(38985, len(draft & current), len(current)), commands, default='grid')
        if choice == 0:
            choices = multiselect(dialog, heading, titles, preselect=[i for i, cid in enumerate(ids) if cid in draft])
            if choices is not None:
                # A partial provider refresh cannot revoke absent selections.
                draft = (draft - current) | {ids[i] for i in choices if type(i) is int and 0 <= i < len(ids)}
        elif choice == 1:
            draft.update(current)
        elif choice == 2:
            draft.clear()
        elif choice == 3:
            draft = original.copy()
        elif choice == 4:
            break
        elif choice == 6 and chosen is None:
            draft.difference_update(cid for cid, title in zip(ids, titles) if ADULT_LABEL.search(title))
        else:
            return

    if draft == original and chosen is not None:
        return
    try:
        save(pid, draft)
    except (OSError, RuntimeError, ValueError, TypeError):
        dialog.ok(heading, tr(38986))
        return
    refresh_movies(pid)
    dialog.notification(heading, tr(38987))

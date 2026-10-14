import xbmc
import xbmcgui
import xbmcaddon

import portals
from portals import (
    load_all, add, update, delete, toggle_enabled,
    move_up, move_down, type_label, portal_summary,
    PORTAL_TYPES, PORTAL_LABELS
)
from utils import notify, info, error, _L

ADDON = xbmcaddon.Addon()

def show():
    while True:
        all_portals = load_all()
        rows  = []
        items = []
        for p in all_portals:
            state = '[ON]' if p.get('enabled', True) else '[OFF]'
            rows.append(f'{state}  {p["name"]}  -  {portal_summary(p)}')
            items.append(p)
        add_idx    = len(rows)
        export_idx = len(rows) + 1
        rows.append(f'[+]  {_L(32060)}')
        rows.append(f'[\u21c5]  {_L(32290)}')
        choice = xbmcgui.Dialog().select(_L(32012), rows)
        if choice < 0:
            break
        elif choice == add_idx:
            from setup_wizard import setup
            created = setup()
            if created:
                return created
        elif choice == export_idx:
            import export_import
            export_import.show_menu()
        else:
            _portal_menu(items[choice])


def _portal_menu(p: dict):
    while True:
        enabled  = p.get('enabled', True)
        epg_show = p.get('epg_show', True)
        name     = p['name']
        options = [
            f'{_L(32074, name)}',
            _L(32078) if enabled else _L(32077),
            f'EPG: [B]{"EINGESCHALTET" if epg_show else "AUSGESCHALTET"}[/B]',
            'Inhaltsbereiche (TV / Filme / Serien) ändern',
            'Sender-/Film-/Seriengruppen verwalten',
            _L(32079),
            _L(32080),
            'Refresh cache',
            _L(32076),
        ]
        idx = xbmcgui.Dialog().select(f'{_L(32012)}: {name}', options)
        if idx < 0:
            break
        elif idx == 0:
            if _wizard_edit(p):
                p = portals.get_by_id(p['id']) or p
        elif idx == 1:
            new_state = toggle_enabled(p['id'])
            p = portals.get_by_id(p['id']) or p
            notify(_L(32012),
                   (_L(32088) if new_state else _L(32089)).format(name))
        elif idx == 2:
            new_epg = not epg_show
            update(p['id'], {'epg_show': new_epg})
            p = portals.get_by_id(p['id']) or p
            notify(_L(32012), f'EPG {"EINGESCHALTET" if new_epg else "AUSGESCHALTET"}: {name}', duration=1500)
        elif idx == 3:
            options = [('include_live', 'Live-TV'), ('include_vod', 'Filme / VOD'),
                       ('include_series', 'Serien')]
            current = [i for i, (key, label) in enumerate(options) if p.get(key, True)]
            choice = xbmcgui.Dialog().multiselect('XCMate – Inhaltsbereiche',
                        [label for key, label in options], preselect=current)
            if choice is not None and choice:
                update(p['id'], {key: i in choice for i, (key, _) in enumerate(options)})
                p = portals.get_by_id(p['id']) or p
        elif idx == 4:
            from group_selection import manage_groups
            manage_groups(p)
        elif idx == 5:
            move_up(p['id'])
            notify(_L(32012), _L(32086, name), duration=1500)
            break
        elif idx == 6:
            move_down(p['id'])
            notify(_L(32012), _L(32087, name), duration=1500)
            break
        elif idx == 7:
            _refresh_portal(p)
        elif idx == 8:
            if xbmcgui.Dialog().yesno(_L(32076),
                         f'Really delete "{name}"?\nAll cached data will be removed.'):
                delete(p['id'])
                notify(_L(32012), _L(32084, name))
                break
def _wizard_add():
    dlg  = xbmcgui.Dialog()
    data = {}

    name = dlg.input(_L(32061), defaultt=_L(32090),
                     type=xbmcgui.INPUT_ALPHANUM)
    if not name:
        return
    data['name'] = name

    type_idx = dlg.select(_L(32062), PORTAL_LABELS)
    if type_idx < 0:
        return
    data['type'] = PORTAL_TYPES[type_idx]

    if not _fill_type_fields(dlg, data):
        return

    epg = dlg.input(_L(32072),
                    type=xbmcgui.INPUT_ALPHANUM)
    data['epg_url'] = epg or ''

    data['epg_show'] = dlg.yesno(_L(32093), _L(32094))

    summary = _build_summary(data)
    if dlg.yesno(_L(32060), summary + f'\n\n{_L(32073)}'):
        portal = add(data)
        notify(_L(32012), _L(32083, portal['name']))
        xbmc.executebuiltin('Container.Refresh')

def _wizard_edit(p: dict) -> bool:
    dlg = xbmcgui.Dialog()
    fields = _get_editable_fields(p)

    while True:
        rows = [f'{label}:   {_mask(key, p.get(key, ""))}' for key, label in fields]
        rows.append('[Save & Close]')
        rows.append('[Cancel]')

        idx = dlg.select(_L(32074, p['name']), rows)
        if idx < 0 or idx == len(fields) + 1:
            return False
        if idx == len(fields):
            update(p['id'], {k: p[k] for k, _ in fields})
            notify(_L(32012), _L(32085, p['name']))
            xbmc.executebuiltin('Container.Refresh')
            return True

        key, label = fields[idx]
        if key == 'type':
            t_idx = dlg.select(_L(32062), PORTAL_LABELS)
            if t_idx >= 0:
                p['type'] = PORTAL_TYPES[t_idx]
                fields = _get_editable_fields(p)
        elif key == 'enabled':
            p['enabled'] = not p.get('enabled', True)
        elif key == 'epg_show':
            p['epg_show'] = not p.get('epg_show', True)
        else:
            current = p.get(key, '')
            new_val = dlg.input(label, defaultt=current,
                                type=xbmcgui.INPUT_ALPHANUM)
            if new_val is not None:
                p[key] = new_val
                if key == 'm3u_url' and new_val:
                    xc = portals.detect_xtream(new_val)
                    if xc and dlg.yesno(
                        _L(32100),
                        _L(32101, xc['xc_host'], xc['xc_user']),
                        nolabel=_L(32102),
                        yeslabel=_L(32103)
                    ):
                        p['type'] = 'xtream'
                        p.update(xc)
                        p['m3u_url'] = ''
                        fields = _get_editable_fields(p)

def _get_editable_fields(p: dict) -> list:
    base = [('name', _L(32061)), ('type', _L(32092)),
            ('epg_url', _L(32072)), ('enabled', _L(32091))]
    if p.get('type') == 'm3u':
        return [('name', _L(32061)), ('type', _L(32092)),
                ('m3u_url', _L(32066)),
                ('epg_url', _L(32072)), ('epg_show', _L(32093)), ('enabled', _L(32091))]
    elif p.get('type') == 'xtream':
        return [('name', _L(32061)), ('type', _L(32092)),
                ('xc_host', _L(32067)),
                ('xc_user', _L(32068)),
                ('xc_pass', _L(32069)),
                ('epg_url', _L(32072)), ('epg_show', _L(32093)), ('enabled', _L(32091))]
    elif p.get('type') == 'stb':
        return [('name', _L(32061)), ('type', _L(32092)),
                ('stb_url', _L(32070)),
                ('stb_mac', _L(32071)),
                ('epg_url', _L(32072)), ('epg_show', _L(32093)), ('enabled', _L(32091))]
    return base

def _mask(key: str, val: str) -> str:
    if 'pass' in key.lower():
        return '*' * min(len(val), 10) if val else ''
    if key == 'enabled':
        return _L(32091) if val else _L(32078)
    if key == 'epg_show':
        return _L(32095) if val else _L(32096)
    if len(val) > 60:
        return val[:57] + '...'
    return val or '–'

def _fill_type_fields(dlg, data: dict) -> bool:
    ptype = data['type']
    if ptype == 'm3u':
        url = dlg.input(_L(32066), type=xbmcgui.INPUT_ALPHANUM)
        if not url:
            return False
        data['m3u_url'] = url
        xc = portals.detect_xtream(url)
        if xc:
            if dlg.yesno(
                _L(32100),
                _L(32101, xc['xc_host'], xc['xc_user']),
                nolabel=_L(32102),
                yeslabel=_L(32103)
            ):
                data['type'] = 'xtream'
                data.update(xc)
                data['m3u_url'] = ''
    elif ptype == 'xtream':
        host = dlg.input(_L(32067),
                         type=xbmcgui.INPUT_ALPHANUM)
        if not host:
            return False
        user = dlg.input(_L(32068), type=xbmcgui.INPUT_ALPHANUM)
        if user is None:
            return False
        pwd = dlg.input(_L(32069), type=xbmcgui.INPUT_ALPHANUM)
        data.update({'xc_host': host, 'xc_user': user, 'xc_pass': pwd or ''})
    elif ptype == 'stb':
        url = dlg.input(_L(32070),
                        type=xbmcgui.INPUT_ALPHANUM)
        if not url:
            return False
        mac = dlg.input(_L(32071), defaultt='00:1A:79:00:00:00',
                        type=xbmcgui.INPUT_ALPHANUM)
        if not mac:
            return False
        data.update({'stb_url': url, 'stb_mac': mac})
    return True


def _refresh_portal(p: dict):
    notify(_L(32012), _L(32053, p['name']), duration=1500)
    try:
        ptype = p.get('type', 'm3u')
        if ptype == 'm3u':
            from iptv import load_m3u
            load_m3u(p.get('m3u_url', ''), force_refresh=True)
        elif ptype == 'xtream':
            from xtream import XtreamClient
            xc = XtreamClient(p['xc_host'], p['xc_user'], p['xc_pass'])
            xc.get_live_streams(force_refresh=True)
        elif ptype == 'stb':
            from stalker import client_for_portal
            sc = client_for_portal(p)
            if sc:
                sc.authenticate(force=True)
                sc.get_live_channels(force=True)
        notify(_L(32012), _L(32041))
    except Exception as e:
        error(f'_refresh_portal: {e}')
        notify(_L(32012), _L(32054, e), duration=4000)


def _build_summary(data: dict) -> str:
    lines = [
        f'Name: {data.get("name")}',
        f'Type: {type_label(data.get("type", ""))}',
    ]
    if data.get('type') == 'm3u':
        lines.append(f'URL:  {data.get("m3u_url", "")}')
    elif data.get('type') == 'xtream':
        lines.append(f'Host: {data.get("xc_host", "")}')
        lines.append(f'User: {data.get("xc_user", "")}')
    elif data.get('type') == 'stb':
        lines.append(f'URL:  {data.get("stb_url", "")}')
        lines.append(f'MAC:  {data.get("stb_mac", "")}')
    if data.get('epg_url'):
        lines.append(f'EPG:  {data.get("epg_url")}')
    epg_show = data.get('epg_show', True)
    lines.append(f'Show EPG: {"Yes" if epg_show else "No"}')
    return '\n'.join(lines)

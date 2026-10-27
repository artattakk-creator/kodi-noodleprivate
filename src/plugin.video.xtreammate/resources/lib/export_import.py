import json
import os
import urllib.request

import xbmc
import xbmcgui
import xbmcvfs

from utils import notify, info, error, _L, addon_data_dir
import portals

_ADDON = None


def _addon():
    global _ADDON
    if not _ADDON:
        import xbmcaddon
        _ADDON = xbmcaddon.Addon()
    return _ADDON


def _dropbox_token():
    return _addon().getSetting('dropbox_token').strip()


def _dropbox_remote_path():
    p = _addon().getSetting('dropbox_backup_path').strip()
    if not p:
        p = '/portals_backup.json'
    if not p.startswith('/'):
        p = '/' + p
    return p


def show_menu():
    dlg = xbmcgui.Dialog()
    options = [_L(32291), _L(32292), _L(32295), _L(32296)]
    idx = __import__('menu_icons45').select(dlg,_L(32290), options,default='shield')
    if idx == 0:
        export_local()
    elif idx == 1:
        import_local()
    elif idx == 2:
        export_dropbox()
    elif idx == 3:
        import_dropbox()


def _pick_path(title, default='', is_save=True):
    dlg = xbmcgui.Dialog()
    method = __import__('menu_icons45').select(dlg,title, [_L(32314), _L(32315)],default='shield')
    if method < 0:
        return None
    if method == 0:
        label = _L(32302) if is_save else _L(32303)
        path = dlg.input(label, defaultt=default, type=xbmcgui.INPUT_ALPHANUM)
        return path.strip() if path else None
    if is_save:
        folder = dlg.browse(3, title, 'files', '', False, False, '')
        if not folder:
            return None
        fname = dlg.input('Dateiname', defaultt='portals_backup.json',
                          type=xbmcgui.INPUT_ALPHANUM)
        if not fname:
            return None
        if not fname.endswith('.json'):
            fname += '.json'
        return os.path.join(folder, fname)
    path = dlg.browse(1, title, 'files', '.json', False, False, '')
    return path if path else None


def export_local():
    all_portals = portals.load_all()
    if not all_portals:
        notify('XtreamMate', _L(32301))
        return
    default = os.path.join(addon_data_dir(), 'portals_backup.json')
    path = _pick_path(_L(32291), default=default, is_save=True)
    if not path:
        return
    try:
        data = json.dumps(all_portals, indent=2, ensure_ascii=False)
        with xbmcvfs.File(path, 'w') as f:
            f.write(data)
        notify('XtreamMate', _L(32317).format(len(all_portals)))
        info(f'Portals exported to: {path}')
    except Exception as e:
        error(f'export_local: {e}')
        notify('XtreamMate', _L(32305), duration=4000)


def import_local():
    path = _pick_path(_L(32292), is_save=False)
    if not path:
        return
    _do_import(path)


def _do_import(path):
    if not xbmcvfs.exists(path):
        notify('XtreamMate', _L(32304), duration=4000)
        return
    try:
        with xbmcvfs.File(path) as f:
            raw = f.read()
        data = json.loads(raw)
    except Exception as e:
        error(f'import parse: {e}')
        notify('XtreamMate', _L(32307), duration=4000)
        return
    if not isinstance(data, list):
        notify('XtreamMate', _L(32307), duration=4000)
        return
    _apply_import(data)


def _apply_import(data):
    dlg = xbmcgui.Dialog()
    mode = __import__('menu_icons45').select(dlg,_L(32308), [_L(32309), _L(32310)],default='shield')
    if mode < 0:
        return
    if mode == 1:
        portals.save_all([])
    existing_ids = {p['id'] for p in portals.load_all()}
    added = 0
    for p in data:
        if not isinstance(p, dict) or 'name' not in p:
            continue
        if p.get('id') in existing_ids:
            continue
        portals.add(p)
        added += 1
    notify('XtreamMate', _L(32316).format(added))
    info(f'Portals imported: {added}')
    xbmc.executebuiltin('Container.Refresh')


def _dropbox_upload(token, remote_path, content):
    url = 'https://content.dropboxapi.com/2/files/upload'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/octet-stream',
        'Dropbox-API-Arg': json.dumps({
            'path': remote_path,
            'mode': 'overwrite',
            'autorename': False,
            'mute': False,
        }),
    }
    body = content.encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception as e:
        error(f'dropbox_upload: {e}')
        return False


def _dropbox_download(token, remote_path):
    url = 'https://content.dropboxapi.com/2/files/download'
    headers = {
        'Authorization': f'Bearer {token}',
        'Dropbox-API-Arg': json.dumps({'path': remote_path}),
    }
    req = urllib.request.Request(url, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8')
    except Exception as e:
        error(f'dropbox_download: {e}')
        return None


def _check_dropbox_token():
    token = _dropbox_token()
    if not token:
        xbmcgui.Dialog().ok('IPTV Master – Dropbox', _L(32311))
        _addon().openSettings()
        return None
    return token


def export_dropbox():
    token = _check_dropbox_token()
    if not token:
        return
    all_portals = portals.load_all()
    if not all_portals:
        notify('XtreamMate', _L(32301))
        return
    remote_path = _dropbox_remote_path()
    content = json.dumps(all_portals, indent=2, ensure_ascii=False)
    notify('XtreamMate', 'Uploading to Dropbox…', duration=1500)
    if _dropbox_upload(token, remote_path, content):
        notify('XtreamMate', _L(32317).format(len(all_portals)))
        info(f'Portals exported to Dropbox: {remote_path}')
    else:
        notify('XtreamMate', _L(32312), duration=4000)


def import_dropbox():
    token = _check_dropbox_token()
    if not token:
        return
    remote_path = _dropbox_remote_path()
    notify('XtreamMate', 'Downloading from Dropbox…', duration=1500)
    raw = _dropbox_download(token, remote_path)
    if raw is None:
        notify('XtreamMate', _L(32313), duration=4000)
        return
    try:
        data = json.loads(raw)
    except Exception as e:
        error(f'import_dropbox parse: {e}')
        notify('XtreamMate', _L(32307), duration=4000)
        return
    if not isinstance(data, list):
        notify('XtreamMate', _L(32307), duration=4000)
        return
    _apply_import(data)

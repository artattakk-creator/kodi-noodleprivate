"""Opt-in, Kodi-fullscreen-only XCMate keymap and remote command bridge.

No global Kodi settings or third-party keymaps are overwritten. Only the
namespaced keymap file that this addon created can be removed again.
"""
import json
import os
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET

import xbmc
import xbmcgui
import xbmcvfs

COMMAND_KEY = 'XtreamMate.RemoteCommand'
SESSION_KEY = 'XtreamMate.LiveSession'
OWN_KEYMAP = 'xtreammate.xml'
MAGIC = 'xtreammate-managed-keymap-v1'
BRIDGE = 'special://home/addons/plugin.video.xtreammate/resources/lib/remote_bridge.py'


def keymap_path():
    return os.path.join(xbmcvfs.translatePath('special://profile/keymaps/'), OWN_KEYMAP)


def build_keymap():
    cmd = lambda action: 'RunScript({},{})'.format(BRIDGE, action)
    root = ET.Element('keymap')
    full = ET.SubElement(root, 'FullscreenVideo')
    for device, entries in (
        ('keyboard', [('left','left',None),('up','up',None),('down','down',None),('return','ok',None),
                      ('enter','ok',None),('return','more','longpress'),
                      ('enter','more','longpress'),('e','epg',None)]),
        ('remote', [('left','left',None),('up','up',None),('down','down',None),('select','ok',None),
                    ('select','more','longpress'),('guide','epg',None)]),
    ):
        dev = ET.SubElement(full, device)
        for key, action, modifier in entries:
            item = ET.SubElement(dev, key)
            if modifier:
                item.set('mod', modifier)
            item.text = cmd(action)
    return '<!-- {} -->\n'.format(MAGIC) + ET.tostring(root, encoding='unicode') + '\n'


def is_enabled():
    path = keymap_path()
    try:
        with open(path, encoding='utf-8') as stream:
            return MAGIC in stream.read(300)
    except (OSError, UnicodeError):
        return False


def enable():
    path = keymap_path()
    if os.path.exists(path) and not is_enabled():
        raise OSError('Eine fremde xtreammate.xml existiert bereits; nichts überschrieben.')
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.xm-map-', dir=folder)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(build_keymap())
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    xbmc.executebuiltin('Action(reloadkeymaps)')
    return is_enabled()


def disable():
    if not is_enabled():
        return False
    os.unlink(keymap_path())
    xbmc.executebuiltin('Action(reloadkeymaps)')
    return True


def configure():
    dlg = xbmcgui.Dialog()
    active = is_enabled()
    title = 'XCMate – TV-Fernbedienung'
    choices = (['Fernbedienung deaktivieren', 'Funktionsweise anzeigen'] if active
               else ['Fernbedienung aktivieren (Links / Hoch / Runter / OK)', 'Funktionsweise anzeigen'])
    selection = dlg.select(title, choices)
    if selection == 1:
        dlg.ok(title, 'Nur bei XCMate-Vollbildvideo: Links öffnet Senderliste, nochmal Links Gruppen. '
               'Hoch/Runter schaltet jeweils einen Sender in der aktiven Gruppe. '
               'OK öffnet die Player-Leiste, nochmal OK die Zusatzleiste. '
               'Langes OK öffnet direkt Zusatzfunktionen, soweit die Fernbedienung '
               'Langes Drücken an Kodi übermittelt. Guide oder E: EPG öffnen.\n\n'
               'Bei fremden Videos werden Standardbefehle weitergegeben. '
               'Kodi gegebenenfalls neu starten.')
        return
    if selection != 0:
        return
    try:
        if active:
            disable()
        else:
            if not dlg.yesno(title, 'Die Tasten Links, Hoch/Runter und OK werden ausschließlich während '
                             'der Vollbildwiedergabe von XCMate abgefangen. '
                             'Eine eigene Keymap wird angelegt. Jetzt aktivieren?'):
                return
            enable()
        dlg.ok(title, 'Die Fernbedienungssteuerung ist {}. '\
                'Bitte Kodi neu starten, falls die Tastenbelegung nicht sofort wirkt.'.format(
                'deaktiviert' if active else 'aktiviert'))
    except Exception as exc:
        dlg.ok(title, 'Keymap konnte nicht geändert werden: {}'.format(type(exc).__name__))


def emit(action):
    xbmcgui.Window(10000).setProperty(COMMAND_KEY,
        json.dumps({'action': action, 'at': time.time(), 'nonce': uuid.uuid4().hex}))


def parse_command(raw, now=None):
    try:
        data = json.loads(raw)
        if not isinstance(data, dict) or data.get('action') not in ('left','ok','more','up','down','epg'):
            return None
        if not data.get('nonce') or abs((time.time() if now is None else now) - float(data['at'])) > 15:
            return None
        return data
    except (ValueError, TypeError, KeyError):
        return None

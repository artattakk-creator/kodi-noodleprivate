"""XCMate-owned Kodi fullscreen keymap, activated only during XCMate Live-TV.

Kodi loads keymaps globally, so all remapped buttons *must* forward their
ordinary Kodi actions when no valid XCMate playback marker exists. Never edit
other keymap files. A user's explicit disable decision is preserved.
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
DISABLED_FLAG = 'xtreammate_remote_autostart.disabled'

# Kodi keyboard devices and Android remotes can produce different tags.
# Leave volume keys to the host. A WindowDialog.onAction is also active when
# the FullscreenVideo keymap cannot receive an event from the current skin.
BUTTONS = (
    ('keyboard', (
        ('left','left'), ('right','right'), ('up','up'), ('down','down'),
        ('return','ok'), ('enter','ok'), ('escape','back'),
        ('backspace','back'), ('menu','menu'), ('c','menu'),
        ('i','info'), ('e','epg'), ('play_pause','play_pause'),
    )),
    ('remote', (
        ('left','left'), ('right','right'), ('up','up'), ('down','down'),
        ('select','ok'), ('back','back'), ('menu','menu'),
        ('guide','epg'), ('info','info'), ('play','play_pause'),
        ('pause','play_pause'),
    )),
)


def keymap_path():
    return os.path.join(xbmcvfs.translatePath('special://profile/keymaps/'), OWN_KEYMAP)


def _opt_out_path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(), DISABLED_FLAG)


def opted_out():
    return os.path.isfile(_opt_out_path())


def keymap_opted_in():
    """Native WindowDialog navigation is the safe default.

    Kodi's FullscreenVideo keymaps affect other addons too, so the RunScript
    bridge must never be installed automatically without an explicit opt-in.
    """
    from utils import setting_bool
    return setting_bool('xc_remote_keymap_fallback', False)


def release_unrequested_keymap():
    """Remove only our own legacy managed keymap, never a foreign keymap.

    Called at XCMate service startup so a stale fullscreen keymap cannot
    intercept remote keys in BINGIE MOD or other Kodi video addons.
    """
    if keymap_opted_in() or not is_enabled():
        return False
    try:
        os.unlink(keymap_path())
        xbmc.executebuiltin('Action(reloadkeymaps)')
        return True
    except OSError:
        return False


def build_keymap():
    root = ET.Element('keymap')
    full = ET.SubElement(root, 'FullscreenVideo')
    for device, bindings in BUTTONS:
        dev = ET.SubElement(full, device)
        for button, action in bindings:
            item = ET.SubElement(dev, button)
            item.text = 'RunScript({},{})'.format(BRIDGE, action)
            if action in ('left', 'right', 'up', 'down', 'ok', 'back', 'menu',
                          'play_pause'):
                held = ET.SubElement(dev, button)
                held.set('mod', 'longpress')
                held.text = 'RunScript({},long_{})'.format(BRIDGE, action)
    return '<!-- {} -->\n'.format(MAGIC) + ET.tostring(root, encoding='unicode') + '\n'


def is_enabled():
    try:
        with open(keymap_path(), encoding='utf-8') as stream:
            return MAGIC in stream.read(300)
    except (OSError, UnicodeError):
        return False


def enable():
    path = keymap_path()
    if os.path.exists(path) and not is_enabled():
        raise OSError('Fremde xtreammate.xml vorhanden; nicht überschrieben.')
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.xm-map-', dir=folder)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(build_keymap())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    xbmc.executebuiltin('Action(reloadkeymaps)')
    return is_enabled()


def disable():
    # Prevent the service from silently reinstalling after manual disable.
    flag = _opt_out_path()
    os.makedirs(os.path.dirname(flag), exist_ok=True)
    with open(flag, 'w', encoding='utf-8') as stream:
        stream.write('disabled by user\n')
    if not is_enabled():
        return False
    os.unlink(keymap_path())
    xbmc.executebuiltin('Action(reloadkeymaps)')
    return True


def ensure_for_live_tv():
    """Best-effort managed keymap installation after a real XCMate session.

    Never overrides an unrelated file, never ignores a manual opt-out and
    never modifies the learned Android action-code JSON.
    """
    if opted_out():
        return 'vom Nutzer deaktiviert'
    if not keymap_opted_in():
        return 'native Kodi-Steuerung (globale Keymap ausgeschaltet)'
    path = keymap_path()
    if os.path.isfile(path) and not is_enabled():
        return 'Konflikt: fremde xtreammate.xml'
    try:
        with open(path, 'r', encoding='utf-8') as stream:
            if stream.read() == build_keymap():
                return 'aktiv'
    except OSError:
        pass
    try:
        return 'aktiviert' if enable() else 'Einrichtung fehlgeschlagen'
    except (OSError, PermissionError):
        return 'Einrichtung fehlgeschlagen'


def configure():
    dialog = xbmcgui.Dialog()
    active = is_enabled()
    choice = dialog.select('XCMate – TV-Fernbedienung', [
        'Alternative globale Vollbild-Keymap ' + ('deaktivieren' if active else 'aktivieren'),
        'Bedienung und Diagnose anzeigen',
    ])
    if choice == 1:
        dialog.ok('XCMate', 'Bei XCMate-Live-TV: Links Senderliste, nochmal Links Gruppen. '
                  'Hoch nächster Sender, Runter vorheriger. OK XCMate-Bedienleiste, '
                  'Rechts letzter Sender, Menü Zusatzfunktionen, Zurück EPG. '
                  'Fernbedienungstasten lassen sich anlernen.\n\n'
                  'Die Keymap wird nur in XCMate genutzt und außerhalb an Kodi '
                  'weitergegeben. Lange Tastendrücke benötigen Geräteunterstützung. '
                  'Zur Kontrolle: TV-Fernbedienung → Diagnose.')
        return
    if choice != 0:
        return
    if active:
        disable()
        import xbmcaddon
        xbmcaddon.Addon().setSetting('xc_remote_keymap_fallback', 'false')
        dialog.notification('XCMate', 'Globale Keymap deaktiviert')
    else:
        if not dialog.yesno('XCMate',
            'XCMate steuert während eigenem Live-TV Links/Rechts/Hoch/Runter, '
            'OK, Zurück und Menü. Außerhalb von XCMate bleiben Kodi-Aktionen '
            'erhalten. Jetzt aktivieren?'):
            return
        try:
            flag = _opt_out_path()
            if os.path.exists(flag):
                os.unlink(flag)
            if not enable():
                raise OSError('keymap not available')
            import xbmcaddon
            xbmcaddon.Addon().setSetting('xc_remote_keymap_fallback', 'true')
            dialog.ok('XCMate', 'Alternative Vollbild-Keymap aktiviert. Kodi bei Bedarf neu starten.')
        except OSError as exc:
            dialog.ok('XCMate', 'Aktivierung fehlgeschlagen: {}'.format(type(exc).__name__))


def emit(action):
    xbmcgui.Window(10000).setProperty(COMMAND_KEY, json.dumps({
        'action': action, 'at': time.time(), 'nonce': uuid.uuid4().hex,
    }))


ALLOWED_ACTIONS = frozenset((
    'left','right','up','down','ok','back','menu','epg','info',
    'play_pause','long_left','long_right','long_up','long_down','long_ok',
    'long_back','long_menu','long_play_pause','more',
))


def parse_command(raw, now=None):
    try:
        data = json.loads(raw)
        if (not isinstance(data, dict) or data.get('action') not in ALLOWED_ACTIONS
                or not data.get('nonce')
                or abs((time.time() if now is None else now)
                       - float(data['at'])) > 15):
            return None
        return data
    except (ValueError, TypeError, KeyError):
        return None

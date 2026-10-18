"""Kodi/Android remote learning for XCMate's on-video WindowDialog.

Only numeric Kodi *action IDs* are mapped; no Android system permissions,
third-party skin keymaps, or global keymaps are modified.
"""
import json
import os
import tempfile

from utils import addon_data_dir

COMMANDS = ('left', 'up', 'down', 'ok', 'epg', 'more')
NAMES = {
    'left': 'Senderliste / Sendergruppen',
    'up': 'Vorheriger Sender',
    'down': 'Nächster Sender',
    'ok': 'Player-Leiste / Zusatzleiste',
    'epg': 'EPG direkt öffnen',
    'more': 'Zusatzleiste direkt öffnen',
}
DEFAULT = {'left': 1, 'up': 3, 'down': 4, 'ok': 7,
           'epg': 117, 'more': 122}

def path():
    return os.path.join(addon_data_dir(), 'xtreammate_remote_actions.json')

def load():
    try:
        with open(path(), 'r', encoding='utf-8') as f:
            stored = json.load(f)
    except FileNotFoundError:
        stored = {}
    if not isinstance(stored, dict):
        raise ValueError('Ungültige Fernbedienungseinstellungen')
    result = dict(DEFAULT)
    for key, value in stored.items():
        if key in COMMANDS and isinstance(value, int) and 0 < value < 100000:
            result[key] = value
    return result

def save(bindings):
    values = {name: int(bindings[name]) for name in COMMANDS}
    if len(set(values.values())) != len(values):
        raise ValueError('Eine Fernbedienungstaste wurde doppelt zugewiesen')
    if any(n < 1 or n >= 100000 or n == 13 for n in values.values()):
        raise ValueError('Ungültige oder reservierte Taste')
    target = path()
    folder = os.path.dirname(target)
    os.makedirs(folder, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.xtreammate-remote-', dir=folder)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(values, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
    finally:
        if os.path.isfile(temp):
            os.unlink(temp)
    return True

def mapped_action(kodi_action):
    code = int(kodi_action)
    for name, bound in load().items():
        if bound == code:
            return name
    # Android's Back key has several Kodi equivalents. Unless specifically
    # assigned to another action, use it to display XCMate channels.
    if code in (9, 10, 92):
        return 'left'
    return None

def _capture():
    import xbmcgui
    class Capture(xbmcgui.WindowDialog):
        def __init__(self):
            super().__init__()
            self.result = None
            # Programmatic Omega WindowDialog never dispatches onInit.
            # Build before doModal and learn the raw action in onAction.
            width = max(720, self.getWidth())
            height = max(480, self.getHeight())
            self.title = xbmcgui.ControlLabel(
                64, height // 2 - 90, width - 128, 70,
                'XCMate: Gewünschte Fernbedienungstaste jetzt drücken',
                'font16', '0xFFFFFFFF')
            self.focus_button = xbmcgui.ControlButton(
                width // 2 - 140, height // 2 + 5, 280, 56,
                'Warte auf Tastendruck…')
            self.addControls([self.title, self.focus_button])
            self.setFocus(self.focus_button)
        def onAction(self, action):
            try:
                code = int(action.getId())
                raw = int(action.getButtonCode())
            except Exception:
                code, raw = 0, 0
            if code:
                self.result = (code, raw)
                self.close()
    dialog = Capture()
    dialog.doModal()
    result = dialog.result
    del dialog
    return result

def configure():
    import xbmcgui
    d = xbmcgui.Dialog()
    while True:
        bindings = load()
        labels = ['{}  [Kodi-Aktion {}]'.format(NAMES[k], bindings[k])
                  for k in COMMANDS]
        items = labels + ['Alle Tasten zurücksetzen', 'Zurück']
        choice = d.select('XCMate – Android-Fernbedienung anlernen', items)
        if choice < 0 or choice == len(items)-1:
            return
        if choice == len(COMMANDS):
            if d.yesno('XCMate', 'Alle gelernten Tastencodes zurücksetzen?'):
                save(DEFAULT)
                d.notification('XCMate', 'Standardbelegung wiederhergestellt')
            continue
        command = COMMANDS[choice]
        if not d.yesno('XCMate', NAMES[command] + '\n'
                       'Im nächsten Fenster genau die gewünschte Taste drücken.'):
            continue
        result = _capture()
        if not result:
            continue
        code, raw = result
        if code == 13:
            d.ok('XCMate', 'Stop kann nicht als Navigationstaste verwendet werden.')
            continue
        other = next((k for k,v in bindings.items()
                      if v == code and k != command), None)
        if other:
            d.ok('XCMate',
                 'Kodi-Aktion {} ist bereits für {} belegt. '
                 'Diese Taste kann nicht doppelt zugewiesen werden.'.format(
                    code, NAMES[other]))
            continue
        if d.yesno('XCMate – Taste erkannt',
                   '{}\nKodi-Aktion: {}\nAndroid-Tastencode: {}\n'
                   'Diese Belegung speichern?'.format(NAMES[command], code, raw)):
            bindings[command] = code
            save(bindings)
            d.notification('XCMate', 'Fernbedienung gespeichert')

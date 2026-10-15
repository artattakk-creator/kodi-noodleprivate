"""Kodi-visible remote debugging, using a native dialog then an XML modal.

Evidence from real Android 0.1.16: WindowDialog received 16 native actions
and closed on Back, but its dynamically added controls were invisible under
the user's active Kodi skin. Route now starts with a Kodi-native select dialog
(which is already known to render), then opens a skin-independent XML dialog.

No IPTV stream, service, credentials or autoplay needed.
"""
import os
import time

import xbmcaddon
import xbmcgui

PREFIX = 'XtreamMate.PopupProbe.'
STATUS = PREFIX + 'Status'
LAST_KEY = PREFIX + 'LastKey'
KEY_COUNT = PREFIX + 'KeyCount'
FOCUS = PREFIX + 'Focus'
LAST_OPENED = PREFIX + 'LastOpened'
RENDERER = PREFIX + 'Renderer'
BACK = frozenset((9, 10, 92))
MOVE = frozenset((1, 2, 3, 4))
SELECT = 7
BUTTON_TEST = 100
BUTTON_CLOSE = 101


def describe_action(key):
    return {
        1: 'Links', 2: 'Rechts', 3: 'Hoch', 4: 'Runter',
        7: 'OK', 9: 'Zurück (Parent)', 10: 'Zurück (Menü)',
        92: 'Zurück (Navigation)', 117: 'Menü',
    }.get(int(key), 'Kodi-Aktion {}'.format(int(key)))


def _home():
    return xbmcgui.Window(10000)


class PopupXMLProbe(xbmcgui.WindowXMLDialog):
    """XML-declared controls have their own explicit Kodi rendering layout."""

    def onInit(self):
        self.count = 0
        self.last_key = 'noch keine'
        self.focus_index = 0
        self.last_ok = 0.0
        self.getControl(52).setLabel('Empfangene Tasten: 0')
        self.getControl(53).setLabel('Letzte Taste: noch keine')
        self.setFocusId(BUTTON_TEST)
        _home().setProperty(RENDERER, 'WindowXMLDialog – Default/720p')
        _home().setProperty(LAST_OPENED, str(time.time()))
        self._write('XML-FENSTER INITIALISIERT')

    def _write(self, status=None):
        home = _home()
        if status is not None:
            home.setProperty(STATUS, status)
        home.setProperty(KEY_COUNT, str(self.count))
        home.setProperty(LAST_KEY, self.last_key)
        home.setProperty(FOCUS, 'Testfeld' if self.focus_index == 0 else 'Schließen')

    def _render(self):
        self.getControl(52).setLabel('Empfangene Tasten: {}'.format(self.count))
        self.getControl(53).setLabel('Letzte Taste: {}'.format(self.last_key))
        self._write('XML-TASTEN EMPFANGEN' if self.count else 'XML-FENSTER INITIALISIERT')

    def _record(self, name, key, raw=0):
        self.count += 1
        self.last_key = '{} (Kodi-ID {}, Code {})'.format(name, key, raw)
        self._render()

    def onAction(self, action):
        try:
            key = int(action.getId())
            raw = int(action.getButtonCode())
        except (TypeError, ValueError, AttributeError):
            return
        self._record(describe_action(key), key, raw)
        if key in BACK:
            self._write('XML: PER ZURÜCK GESCHLOSSEN')
            self.close()
        elif key in MOVE:
            self.focus_index = 1 - self.focus_index
            self.setFocusId(BUTTON_CLOSE if self.focus_index else BUTTON_TEST)
            self._render()
        elif key == SELECT:
            self.last_ok = time.monotonic()
            if self.focus_index == 1:
                self._write('XML: PER OK GESCHLOSSEN')
                self.close()

    def onFocus(self, control_id):
        if control_id in (BUTTON_TEST, BUTTON_CLOSE):
            self.focus_index = 0 if control_id == BUTTON_TEST else 1
            self._write()

    def onClick(self, control_id):
        if control_id not in (BUTTON_TEST, BUTTON_CLOSE):
            return
        if time.monotonic() - getattr(self, 'last_ok', 0.0) >= 0.3:
            self._record('OK / onClick', SELECT, 0)
        if control_id == BUTTON_CLOSE:
            self._write('XML: PER KLICK GESCHLOSSEN')
            self.close()


def run_popup_test():
    """Always show a known-visible native Kodi chooser before custom XML."""
    home = _home()
    home.setProperty(RENDERER, 'Kodi Dialog.select – Vortest')
    home.setProperty(STATUS, 'NATIVER KODI-DIALOG AUFGERUFEN')
    home.setProperty(LAST_OPENED, str(time.time()))
    home.setProperty(KEY_COUNT, '0')
    home.setProperty(LAST_KEY, 'noch keine')
    home.setProperty(FOCUS, 'Kodi-Auswahlfenster')
    selection = xbmcgui.Dialog().select(
        'XCMate – SICHTBARER POPUP-TEST',
        ['Eigenes XCMate-XML-Fenster jetzt öffnen',
         'Nur Kodi-Popup bestätigen und zurück zum Menü'])
    if selection < 0:
        home.setProperty(STATUS, 'KODI-DIALOG MIT ZURÜCK GESCHLOSSEN')
        return
    if selection == 1:
        home.setProperty(STATUS, 'KODI-DIALOG SICHTBAR – BESTÄTIGT')
        home.setProperty(LAST_KEY, 'Kodi-Dialog: Auswahl bestätigt')
        return
    if selection != 0:
        home.setProperty(STATUS, 'KODI-DIALOG OHNE XML BEENDET')
        return
    home.setProperty(STATUS, 'XML-LADEVERSUCH')
    addon_path = xbmcaddon.Addon().getAddonInfo('path')
    dialog = None
    try:
        dialog = PopupXMLProbe(
            'XCMatePopupTest.xml', addon_path, 'Default', '720p')
        dialog.doModal()
    except Exception as exc:
        # Do not log a path, a provider URL, stacktrace or credentials.
        kind = type(exc).__name__
        home.setProperty(STATUS, 'XML-FEHLER: ' + kind)
        xbmcgui.Dialog().ok(
            'XCMate – XML-Popup konnte nicht geladen werden',
            'Fehlerklasse: {}. Die normale Kodi-Diagnose bleibt verfügbar.'.format(kind))
    finally:
        if dialog is not None:
            del dialog

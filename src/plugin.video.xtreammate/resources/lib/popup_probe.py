"""Standalone Kodi modal UI diagnostic for XCMate on Android.

This dialog can be opened from the XCMate portal menu while NO video plays.
Unlike the video overlay, it runs in the add-on's foreground plug-in invocation
using WindowDialog.doModal(), and tests Kodi's native action delivery/focus.
Only harmless action IDs and counts are stored in Kodi's home-window properties.
"""
import os
import time

import xbmcgui

PREFIX = 'XtreamMate.PopupProbe.'
STATUS = PREFIX + 'Status'
LAST_KEY = PREFIX + 'LastKey'
KEY_COUNT = PREFIX + 'KeyCount'
FOCUS = PREFIX + 'Focus'
LAST_OPENED = PREFIX + 'LastOpened'
BACK = frozenset((9, 10, 92))
MOVE = {1: -1, 2: 1, 3: -1, 4: 1}
SELECT = 7


def describe_action(key):
    return {
        1: 'Links', 2: 'Rechts', 3: 'Hoch', 4: 'Runter',
        7: 'OK', 9: 'Zurück (Parent)', 10: 'Zurück (Menü)',
        92: 'Zurück (Navigation)', 117: 'Menü',
    }.get(int(key), 'Kodi-Aktion {}'.format(int(key)))


class PopupInputProbe(xbmcgui.WindowDialog):
    """Real focusable XCMate popup – no IPTV player, service or credentials."""

    def __init__(self):
        super().__init__()
        self.count = 0
        self.last_key = 'noch keine'
        self.focus_index = 0
        self._initialized = False
        self._last_select_time = 0

    def _write(self, status=None):
        window = xbmcgui.Window(10000)
        if status is not None:
            window.setProperty(STATUS, status)
        window.setProperty(KEY_COUNT, str(self.count))
        window.setProperty(LAST_KEY, self.last_key)
        window.setProperty(FOCUS, 'Testfeld' if self.focus_index == 0 else 'Schließen')

    def onInit(self):
        import xbmcaddon
        try:
            w = max(960, self.getWidth())
            h = max(540, self.getHeight())
        except Exception:
            w, h = 1280, 720
        addon_path = xbmcaddon.Addon().getAddonInfo('path')
        bg_image = os.path.join(addon_path, 'resources', 'media', 'tv_overlay_bg.png')
        pad = max(36, w // 22)
        panel_width = min(w-2*pad, 1080)
        panel_left = (w-panel_width)//2
        panel_top = max(48, (h-500)//2)
        self.bg = xbmcgui.ControlImage(panel_left, panel_top, panel_width, 490, bg_image)
        self.title = xbmcgui.ControlLabel(
            panel_left+35, panel_top+25, panel_width-70, 58,
            'XCMate · POPUP- UND FERNBEDIENUNGSTEST',
            'font16', '0xFFFFFFFF')
        self.description = xbmcgui.ControlLabel(
            panel_left+35, panel_top+99, panel_width-70, 40,
            'Eigener Kodi-Dialog – OHNE gestarteten TV-Stream',
            'font13', '0xFFD3DAE1')
        self.instructions = xbmcgui.ControlLabel(
            panel_left+35, panel_top+158, panel_width-70, 37,
            'Hoch / Runter / Links / Rechts / OK drücken. Zurück schließt.',
            'font13', '0xFFFFFFFF')
        self.count_label = xbmcgui.ControlLabel(
            panel_left+35, panel_top+213, panel_width-70, 45,
            'Empfangene Tasten: 0',
            'font13', '0xFFFFFFFF')
        self.last_label = xbmcgui.ControlLabel(
            panel_left+35, panel_top+267, panel_width-70, 40,
            'Letzte Taste: noch keine',
            'font13', '0xFFD3DAE1')
        self.test_button = xbmcgui.ControlButton(
            panel_left+35, panel_top+355, (panel_width-115)//2, 60,
            'OK / Fokus testen')
        self.close_button = xbmcgui.ControlButton(
            panel_left+80+(panel_width-115)//2, panel_top+355,
            (panel_width-115)//2, 60, 'Schließen')
        for ctl in (self.bg, self.title, self.description, self.instructions,
                    self.count_label, self.last_label, self.test_button, self.close_button):
            self.addControl(ctl)
        self._initialized = True
        self.setFocus(self.test_button)
        xbmcgui.Window(10000).setProperty(LAST_OPENED, str(time.time()))
        self._write('FENSTER SICHTBAR – warte auf Tastendruck')

    def _render(self):
        if not self._initialized:
            return
        self.count_label.setLabel('Empfangene Tasten: {}'.format(self.count))
        self.last_label.setLabel('Letzte Taste: {}'.format(self.last_key))
        self.setFocus(self.test_button if self.focus_index == 0 else self.close_button)
        self._write('TASTEN ANGEKOMMEN' if self.count else 'FENSTER SICHTBAR')

    def _record(self, key, raw=0):
        self.count += 1
        self.last_key = '{} (Kodi-ID {}, Code {})'.format(describe_action(key), key, raw)
        self._render()

    def onAction(self, action):
        try:
            key = int(action.getId())
            raw = int(action.getButtonCode())
        except (TypeError, ValueError, AttributeError):
            return
        self._record(key, raw)
        if key in BACK:
            self._write('PER ZURÜCK GESCHLOSSEN')
            self.close()
        elif key in MOVE:
            self.focus_index = 1 if (self.focus_index + MOVE[key]) % 2 else 0
            self._render()
        elif key == SELECT:
            self._last_select_time = time.monotonic()
            if self.focus_index == 1:
                self._write('PER OK GESCHLOSSEN')
                self.close()

    def onClick(self, control_id):
        # Some Android remotes report OK to onClick instead of onAction.
        if not self._initialized:
            return
        if control_id == self.close_button.getId():
            self.count += 1
            self.last_key = 'OK – Schließen (Kodi onClick)'
            self._write('PER KLICK GESCHLOSSEN')
            self.close()
        elif control_id == self.test_button.getId():
            if time.monotonic() - self._last_select_time > 0.25:
                self.count += 1
                self.last_key = 'OK – Testfeld (Kodi onClick)'
                self._render()


def run_popup_test():
    """Public entry point for Kodi's normal menu navigation."""
    dialog = PopupInputProbe()
    try:
        dialog.doModal()
    finally:
        del dialog

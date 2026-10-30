"""Safe, read-only Live-TV view for Box B evaluation.

One local catalogue read, then one local EPG/artwork refresh for the focused
channel after debounce. Never tunes or stops a player, modifies a skin,
calls the IPTV provider, or changes profile/widget bindings.
"""
from concurrent.futures import Future
import threading
import time

import xbmc
import xbmcaddon
import xbmcgui

SAMPLE_DELAY = .35
PREVIEW_TTL = 25.0
ROW_LIMIT = 2000


def load_rows(portal):
    """Index-only, bounded, in start-group order; no network or EPG reads."""
    from widget_home50 import rows
    values, code = rows(portal)
    if len(values) > ROW_LIMIT:
        return [], 'TOO_MANY_CHANNELS'
    return values, code


def logo_for(row):
    """Provider logo if present, otherwise the bundled neutral TV icon."""
    import os
    value = row.get('stream_icon') or row.get('logo') or row.get('icon') or ''
    if isinstance(value, str) and value and len(value) <= 2048 and not any(ord(c) < 32 for c in value):
        return value
    return os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'media', 'tv.png')


def preview(portal, row):
    """Hydrate only the focused programme from the existing local EPG cache."""
    from widget_render47 import values
    from widget_art44 import read
    item = values(portal, 'live', [row], read(portal['id']))[0]
    return item['props'], item['art']


def _worker(future, fn):
    if not future.set_running_or_notify_cancel():
        return
    try:
        future.set_result(fn())
    except Exception:
        future.set_exception(RuntimeError('LOCAL_PREVIEW_UNAVAILABLE'))


class SafeLiveView60(xbmcgui.WindowXMLDialog):
    def configure(self, portal):
        self.portal = portal
        self.owner = threading.get_ident()
        self._closed = False
        self._ready = False
        self.rows = []
        self._rows_future = None
        self._focus_future = None
        self._focus_index = -1
        self._focus_requested = 0.0
        self._focus_key = None
        self._focus_refresh = 0.0
        self._shown = None

    def _on_owner(self):
        if threading.get_ident() != self.owner:
            raise RuntimeError('LIVE_VIEW_OWNER_THREAD')

    def _background(self, fn):
        future = Future()
        thread = threading.Thread(target=_worker, args=(future, fn),
                                  name='XCMate-safe-live-view60', daemon=True)
        try:
            thread.start()
            return future
        except (MemoryError, RuntimeError):
            return None

    def onInit(self):
        self._on_owner()
        self._ready = True
        self.getControl(101).setLabel('Live-TV · sichere Vorschau · nur lesen')
        self.getControl(117).setLabel('Startgruppe wird lokal geladen …')
        self.setFocusId(200)
        self._rows_future = self._background(lambda: load_rows(self.portal))

    def _render_preview(self, data):
        props, art = data
        def prop(key):
            return str(props.get('XCMate.' + key, ''))
        logo = prop('ProgrammeLogo46')
        image = prop('ProgrammeImage46')
        self.getControl(110).setImage(image or logo)
        self.getControl(111).setImage(logo or '')
        self.getControl(112).setLabel(prop('ProgrammeTitle46') or 'Keine EPG-Daten')
        self.getControl(113).setLabel(prop('ProgrammeNext46'))
        self.getControl(114).setLabel(prop('ProgrammeChannel46'))
        self.getControl(115).setText(prop('ProgrammeDescription46'))
        self.getControl(118).setLabel(prop('ProgrammeTimes46'))
        self.getControl(119).setLabel(prop('ProgrammeNextTimes48'))
        try:
            self.getControl(116).setPercent(max(0, min(100, float(prop('ProgrammePercent46') or 0))))
        except (ValueError, TypeError, AttributeError):
            pass
        self.getControl(117).setLabel('Fokus: Vorschau · OK: keine Wiedergabe · Zurück: Schließen')

    def pump(self):
        self._on_owner()
        if self._rows_future and self._rows_future.done():
            f = self._rows_future
            self._rows_future = None
            try:
                rows, code = f.result()
            except Exception:
                rows, code = [], 'LOCAL_UNAVAILABLE'
            self.rows = rows
            control = self.getControl(200)
            control.reset()
            items = []
            for row in rows:
                item = xbmcgui.ListItem(str(row.get('name') or 'Sender'))
                item.setProperty('XCMate.LiveLogo60', logo_for(row))
                items.append(item)
            if items:
                control.addItems(items)
                control.selectItem(0)
                self._focus_requested = time.monotonic() + SAMPLE_DELAY
            self.getControl(101).setLabel('Live-TV · ' + str(len(rows)) + ' Sender · rein lokale Vorschau')
            self.getControl(117).setLabel('Nur Lesen · ' + str(code) if rows else
                                           'Startgruppe nicht verfügbar · ' + str(code))
        if not self.rows:
            return
        index = self.getControl(200).getSelectedPosition()
        if not isinstance(index, int) or index < 0 or index >= len(self.rows):
            return
        now = time.monotonic()
        if index != self._focus_index:
            self._focus_index = index
            self._focus_key = (index, str(self.rows[index].get('sid')))
            self._focus_requested = now + SAMPLE_DELAY
            self.getControl(114).setLabel(str(self.rows[index].get('name', '')))
            self.getControl(117).setLabel('EPG-Vorschau wird geladen …')
        if self._focus_future and self._focus_future.done():
            f, wanted = self._focus_future
            self._focus_future = None
            try:
                data = f.result()
            except Exception:
                if wanted == self._focus_key:
                    self.getControl(117).setLabel('Lokale EPG-Vorschau nicht verfügbar · Sender bleibt sichtbar')
            else:
                if wanted == self._focus_key:
                    self._render_preview(data)
                    self._shown = wanted
                    self._focus_refresh = now + PREVIEW_TTL
        if (self._focus_future is None and now >= self._focus_requested and
                (self._shown != self._focus_key or now >= self._focus_refresh)):
            wanted = self._focus_key
            row = dict(self.rows[index])
            self._focus_future = (self._background(lambda: preview(self.portal, row)), wanted)
            if self._focus_future[0] is None:
                self._focus_future = None
                self._focus_requested = now + PREVIEW_TTL
            else:
                self._focus_requested = now + PREVIEW_TTL

    def onClick(self, control_id):
        # Strictly no tune, no PlayerControl, no window transition on OK.
        if control_id == 200:
            self.getControl(117).setLabel('Sicherer Testmodus: Wiedergabe absichtlich deaktiviert')

    def onAction(self, action):
        if action.getId() in (9, 10, 92):
            self.close()

    def run(self):
        monitor = xbmc.Monitor()
        started = time.monotonic()
        try:
            self.show()
            while not self._closed:
                if self._ready:
                    self.pump()
                elif time.monotonic() - started > 10:
                    break
                if monitor.waitForAbort(.08):
                    break
        finally:
            self.close()

    def close(self):
        self._on_owner()
        if self._closed:
            return
        self._closed = True
        for future in (self._rows_future, self._focus_future[0] if self._focus_future else None):
            if future:
                future.cancel()
        super().close()


def launch(portal):
    if not portal:
        return
    from programme_window46 import permitted
    from window_navigation import ownership
    with ownership() as acquired:
        if not acquired or not permitted():
            return
        dialog = SafeLiveView60('XCMateLiveView60.xml',
                                xbmcaddon.Addon().getAddonInfo('path'), 'Default', '720p')
        dialog.configure(portal)
        dialog.run()

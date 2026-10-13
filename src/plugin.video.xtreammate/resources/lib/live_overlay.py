"""XtreamMate remote-control TV navigation, displayed over active Xtream live TV.

Back/Left: closed -> channels -> category groups; Right: return to channels.
Up/Down: highlight items; OK: tune channel or open highlighted group.
Context/Menu (or 0): toggle a group in the saved multi-selection.
Back on groups: close overlay. Stop: stop playback and close overlay.

All Kodi controls are owned by the GUI thread; no network requests are made in
onAction. Reloading is only done during session initialization or group toggles.
"""
import json
import os
import time
import uuid

import xbmc
import xbmcgui

from utils import info, warn

SESSION_KEY = 'XtreamMate.LiveSession'
ACTION_LEFT = 1
ACTION_RIGHT = 2
ACTION_UP = 3
ACTION_DOWN = 4
ACTION_PAGE_UP = 5
ACTION_PAGE_DOWN = 6
ACTION_SELECT = 7
ACTION_PREVIOUS_MENU = 10
ACTION_STOP = 13
ACTION_PAUSE = 12
ACTION_NAV_BACK = 92
ACTION_CONTEXT_MENU = 117
ACTION_PARENT_DIR = 9
BACK_ACTIONS = (ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_PARENT_DIR)


def announce(portal_id, stream_id, channel_name=''):
    """Set a small, short-lived playback marker; never store provider passwords."""
    value = {'pid': str(portal_id), 'sid': str(stream_id),
             'name': str(channel_name)[:160], 'at': time.time(),
             'nonce': uuid.uuid4().hex}
    xbmcgui.Window(10000).setProperty(SESSION_KEY, json.dumps(value))


def session_from_property(raw, now=None):
    try:
        obj = json.loads(raw)
        if (not isinstance(obj, dict) or not obj.get('pid') or not obj.get('sid')
                or not obj.get('nonce')):
            return None
        if abs((time.time() if now is None else now) - float(obj.get('at', 0))) > 120:
            return None
        return obj
    except (TypeError, ValueError, KeyError):
        return None


def category_rows(categories, enabled):
    """Pure helper: all categories including disabled are shown, sorted by source."""
    selected = None if enabled is None else set(str(x) for x in enabled)
    rows = [('*', 'Alle aktivierten Gruppen', True)]
    for c in categories:
        cid = str(c.get('category_id', ''))
        if not cid:
            continue
        rows.append((cid, str(c.get('category_name', cid)),
                     selected is None or cid in selected))
    return rows


def channels_for_category(channels, category_id, enabled):
    active = None if enabled is None else {str(x) for x in enabled}
    return [ch for ch in channels
            if (active is None or str(ch.extra.get('category_id', '')) in active)
            and (category_id == '*' or str(ch.extra.get('category_id', '')) == category_id)]


class LiveNavigator(xbmcgui.WindowDialog):
    """Nonblocking WindowDialog; service.py owns and closes its lifecycle."""

    def __init__(self, portal, initial_sid=''):
        super().__init__()
        from xtream import XtreamClient
        from iptv import Channel
        from group_selection import load
        self.portal = portal
        self.xc = XtreamClient(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
        self.sid = str(initial_sid)
        self.groups = [c for c in self.xc.get_live_categories() if isinstance(c, dict)]
        self.enabled = load(portal['id'])
        names = {str(c.get('category_id')): c.get('category_name', '') for c in self.groups}
        self.channels = []
        for s in self.xc.get_live_streams():
            if not isinstance(s, dict) or not s.get('stream_id'):
                continue
            cid = str(s.get('category_id', ''))
            self.channels.append(Channel(name=s.get('name', ''),
                url=self.xc.live_stream_url(s['stream_id'], 'ts'),
                logo=s.get('stream_icon', ''), group=str(names.get(cid, cid)),
                extra={'category_id': cid, 'stream_id': str(s['stream_id'])}))
        self.mode = 'hidden'
        self.category_id = '*'
        self.visible_channels = []
        self.rows = category_rows(self.groups, self.enabled)
        self._drawn = False
        self._closed = False
        self._highlight = {'channels': 0, 'groups': 0}

    def onInit(self):
        # Transparent native Kodi dialog; background video stays visible.
        import xbmcaddon
        image = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'media', 'tv_overlay_bg.png')
        self.bg = xbmcgui.ControlImage(0, 0, 820, 1080, image)
        self.heading = xbmcgui.ControlLabel(38, 42, 750, 60, 'XtreamMate', 'font16', '0xFFFFFFFF')
        self.sub = xbmcgui.ControlLabel(38, 111, 750, 45, '', 'font13', '0xFFE3C5FF')
        self.control = xbmcgui.ControlList(36, 176, 736, 755, font='font13',
                                         textColor='0xFFFFFFFF',
                                         selectedColor='0xFFFFC46E',
                                         _itemHeight=48, _space=4)
        self.footer = xbmcgui.ControlLabel(38, 958, 745, 72, '', 'font12', '0xFFD3D7E2')
        for c in (self.bg, self.heading, self.sub, self.control, self.footer):
            self.addControl(c)
        self._drawn = True
        self._render()

    def _render(self):
        if not self._drawn:
            return
        visible = self.mode != 'hidden'
        for c in (self.bg, self.heading, self.sub, self.control, self.footer):
            c.setVisible(visible)
        if not visible:
            return
        self.control.reset()
        if self.mode == 'groups':
            self.rows = category_rows(self.groups, self.enabled)
            labels = [('✔  ' if enabled else '○  ') + label for _, label, enabled in self.rows]
            self.heading.setLabel('XtreamMate  ·  SENDERGRUPPEN')
            self.sub.setLabel('OK: Gruppe öffnen  ·  Menü: An/Aus')
            self.footer.setLabel('◀/Zurück: schließen   ▶: Senderliste   ▲▼: navigieren')
        else:
            self.visible_channels = channels_for_category(self.channels, self.category_id, self.enabled)
            labels = [c.name for c in self.visible_channels]
            self.heading.setLabel('XtreamMate  ·  LIVE-TV')
            self.sub.setLabel('{} Sender  ·  {}'.format(len(labels),
                               next((x[1] for x in self.rows if x[0] == self.category_id), 'Aktivierte Gruppen')))
            self.footer.setLabel('◀/Zurück: Sendergruppen   OK: Sender starten   ▲▼: navigieren')
        if not labels:
            labels = ['Keine Sender in dieser Auswahl']
        self.control.addItems(labels)
        pos = self._highlight[self.mode]
        if self.mode == 'channels' and self.sid:
            found = next((i for i,c in enumerate(self.visible_channels)
                          if c.extra.get('stream_id') == self.sid), None)
            if found is not None:
                pos = found
                self.sid = ''
        self.control.selectItem(min(pos, len(labels)-1))
        self.setFocus(self.control)

    def _position(self, step):
        count = self.control.size()
        if count > 0:
            i = min(max(self.control.getSelectedPosition() + step, 0), count - 1)
            self.control.selectItem(i)
            self._highlight[self.mode] = i

    def _switch(self, mode):
        self.mode = mode
        self._render()

    def _toggle(self):
        from group_selection import save
        if self.mode != 'groups':
            return
        pos = self.control.getSelectedPosition()
        if pos < 1 or pos >= len(self.rows):
            return
        cid = self.rows[pos][0]
        all_ids = {str(c.get('category_id')) for c in self.groups}
        if self.enabled is None:
            self.enabled = all_ids
        else:
            self.enabled = set(self.enabled)
        if cid in self.enabled:
            self.enabled.remove(cid)
        else:
            self.enabled.add(cid)
        save(self.portal['id'], self.enabled)
        self._highlight['groups'] = pos
        if self.category_id != '*' and self.category_id not in self.enabled:
            self.category_id = '*'
        self._render()

    def _select(self):
        if self.mode == 'groups':
            i = self.control.getSelectedPosition()
            if 0 <= i < len(self.rows):
                cid, _, active = self.rows[i]
                if cid != '*' and not active:
                    self._toggle()
                self.category_id = cid
                self._highlight['channels'] = 0
                self._switch('channels')
        elif self.mode == 'channels':
            i = self.control.getSelectedPosition()
            if 0 <= i < len(self.visible_channels):
                c = self.visible_channels[i]
                from player import build_playable_item
                self._highlight['channels'] = i
                # Keep this dialog open while the player changes channels.
                sid = c.extra.get('stream_id', '')
                self.sid = str(sid)
                announce(self.portal['id'], sid, c.name)
                xbmc.Player().play(c.url, build_playable_item(c.url, title=c.name, logo=c.logo))
                self._switch('hidden')

    def onAction(self, action):
        key = action.getId()
        if key == ACTION_STOP:
            xbmc.Player().stop()
            self.close()
            return
        if key == ACTION_PAUSE and self.mode == 'hidden':
            xbmc.Player().pause()
            return
        if key in BACK_ACTIONS or key == ACTION_LEFT:
            if self.mode == 'hidden':
                self._switch('channels')
            elif self.mode == 'channels':
                self._switch('groups')
            else:
                self._switch('hidden')
        elif key == ACTION_RIGHT:
            if self.mode == 'groups':
                self._switch('channels')
            elif self.mode == 'hidden':
                self._switch('channels')
            else:
                self._switch('hidden')
        elif key in (ACTION_UP, ACTION_DOWN, ACTION_PAGE_UP, ACTION_PAGE_DOWN):
            if self.mode == 'hidden':
                self._switch('channels')
            else:
                self._position({ACTION_UP:-1,ACTION_DOWN:1,ACTION_PAGE_UP:-10,ACTION_PAGE_DOWN:10}[key])
        elif key == ACTION_SELECT:
            if self.mode == 'hidden':
                self._switch('channels')
            else:
                self._select()
        elif key == ACTION_CONTEXT_MENU and self.mode == 'groups':
            self._toggle()
        elif key in (ACTION_PREVIOUS_MENU, ACTION_NAV_BACK):
            self._switch('hidden')

    def onClick(self, control_id):
        if self._drawn and control_id == self.control.getId() and self.mode != 'hidden':
            self._select()


def start_if_eligible(last_nonce):
    """Return overlay instance or None. Called in the service's main thread."""
    if not xbmc.Player().isPlayingVideo():
        return None
    session = session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
    if not session or session['nonce'] == last_nonce:
        return None
    from portals import get_by_id
    portal = get_by_id(session['pid'])
    if not portal or portal.get('type') != 'xtream':
        return None
    try:
        return LiveNavigator(portal, session['sid'])
    except Exception as exc:
        warn('XtreamMate navigator cannot start: {}'.format(type(exc).__name__))
        return None

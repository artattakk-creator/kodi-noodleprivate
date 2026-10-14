"""XtreamMate remote-control TV navigation, displayed over active Xtream live TV.

Back/Left: closed -> channels -> category groups; Right: return to channels.
Up/Down: zap one station in the active group when hidden, otherwise highlight items.
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
        if abs((time.time() if now is None else now) - float(obj.get('at', 0))) > 86400:
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


def adjacent_channel(channels, category_id, enabled, current_sid, step):
    """Next/previous channel in provider order; wrap at group boundaries.

    Categories are identified by provider IDs, never translated display names.
    Disabled categories are excluded. Unknown station: select first/last.
    """
    choices = channels_for_category(channels, category_id, enabled)
    if not choices:
        return None
    current = str(current_sid)
    idx = next((i for i, channel in enumerate(choices)
                if str(channel.extra.get('stream_id', '')) == current), None)
    if idx is None:
        return choices[0 if step > 0 else -1]
    return choices[(idx + (1 if step > 0 else -1)) % len(choices)]


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
        self.groups = []
        self.enabled = load(portal['id'])
        self.channels = []
        self._catalog_ready = False
        # Cache-only, no network. The background service warms missing data;
        # list presentation is fast even when the provider stalls.
        self._load_catalog_from_disk()
        self.mode = 'hidden'
        self._focus_main = 0
        self._focus_extra = 0
        self._last_select = 0
        selected_stream = next((c for c in self.channels
                                if str(c.extra.get('stream_id')) == self.sid), None)
        # Normally zap within the playing station's own category. Selecting
        # "all enabled" explicitly allows zapping across all active groups.
        self.category_id = (str(selected_stream.extra.get('category_id'))
                            if selected_stream else str(portal.get('start_group_id') or '*'))
        self._scroll_to_current = True
        self.visible_channels = []
        self.rows = category_rows(self.groups, self.enabled)
        self._drawn = False
        self._closed = False
        self._epg_fetching = False
        self._highlight = {'channels': 0, 'groups': 0}

    def _load_catalog_from_disk(self):
        from iptv import Channel
        categories = self.xc.get_cached_catalog('get_live_categories')
        streams = self.xc.get_cached_catalog('get_live_streams')
        if categories is None or streams is None:
            return False
        groups = [c for c in categories if isinstance(c, dict)]
        names = {str(c.get('category_id')): c.get('category_name', '')
                 for c in groups}
        channels = []
        for stream in streams:
            if not isinstance(stream, dict) or not stream.get('stream_id'):
                continue
            cid = str(stream.get('category_id', ''))
            channels.append(Channel(
                name=stream.get('name', ''),
                url=self.xc.live_stream_url(stream['stream_id'], 'ts'),
                logo=stream.get('stream_icon', ''),
                group=str(names.get(cid, cid)),
                tvg_id=str(stream.get('epg_channel_id') or ''),
                extra={'category_id': cid,
                       'stream_id': str(stream['stream_id'])}))
        self.groups, self.channels = groups, channels
        self._catalog_ready = True
        return True

    def refresh_from_cache(self):
        """Service polls only until initial background warming has completed."""
        if self._catalog_ready or not self._load_catalog_from_disk():
            return False
        self.rows = category_rows(self.groups, self.enabled)
        selected_stream = next((c for c in self.channels
                                if str(c.extra.get('stream_id')) == self.sid), None)
        if selected_stream:
            self.category_id = str(selected_stream.extra.get('category_id'))
        if self.mode in ('channels', 'groups'):
            self._render()
        return True

    def onInit(self):
        import xbmcaddon
        try:
            width = max(840, self.getWidth())
            height = max(560, self.getHeight())
        except Exception:
            width, height = 1280, 720
        image = os.path.join(xbmcaddon.Addon().getAddonInfo('path'),
                             'resources', 'media', 'tv_overlay_bg.png')
        sidebar = min(600, max(440, int(width * 0.47)))
        self.bg = xbmcgui.ControlImage(0, 0, sidebar, height, image)
        self.heading = xbmcgui.ControlLabel(32, 25, sidebar-48, 55, 'XtreamMate', 'font16', '0xFFFFFFFF')
        self.sub = xbmcgui.ControlLabel(32, 82, sidebar-48, 40, '', 'font13', '0xFFE3C5FF')
        self.control = xbmcgui.ControlList(32, 135, sidebar-58, height-205,
            font='font13', textColor='0xFFFFFFFF', selectedColor='0xFFFFC46E')
        self.control.setItemHeight(46)
        self.control.setSpace(3)
        self.footer = xbmcgui.ControlLabel(32, height-65, sidebar-40, 48, '', 'font12', '0xFFD3D7E2')
        self.osd_bg = xbmcgui.ControlImage(0, height-165, width, 165, image)
        self.osd_title = xbmcgui.ControlLabel(26, height-155, width-50, 38, '', 'font13', '0xFFFFFFFF')
        self.main_buttons = []
        self.extra_buttons = []
        main = ['⏯ Pause / Weiter', '◀◀ −10 s', '▶▶ +30 s', '■ Stop']
        extra = ['Ton', 'Bild', 'EPG', 'Einstellungen', 'Sendergruppen']
        space = max(125, int((width-40)/len(main)))
        for idx, label in enumerate(main):
            self.main_buttons.append(xbmcgui.ControlButton(
                20+idx*space, height-111, space-8, 40, label))
        space2 = max(110, int((width-40)/len(extra)))
        for idx, label in enumerate(extra):
            self.extra_buttons.append(xbmcgui.ControlButton(
                20+idx*space2, height-59, space2-8, 40, label))
        for control in (self.bg, self.heading, self.sub, self.control, self.footer,
                        self.osd_bg, self.osd_title, *self.main_buttons, *self.extra_buttons):
            self.addControl(control)
        self._drawn = True
        xbmcgui.Window(10000).setProperty('XtreamMate.OverlayStatus', 'bereit')
        self._render()

    def _render(self):
        if not self._drawn:
            return
        listing = self.mode in ('groups','channels')
        osd = self.mode in ('controls','extras')
        for c in (self.bg, self.heading, self.sub, self.control, self.footer):
            c.setVisible(listing)
        for c in (self.osd_bg, self.osd_title, *self.main_buttons):
            c.setVisible(osd)
        for c in self.extra_buttons:
            c.setVisible(self.mode == 'extras')
        if osd:
            self.osd_title.setLabel('XtreamMate  ·  {}  |  {}'.format(
                self.portal.get('name','Live TV'),
                'OK: Weitere Funktionen' if self.mode == 'controls' else 'OK: Ausführen'))
            focus = (self.main_buttons[self._focus_main] if self.mode == 'controls'
                     else self.extra_buttons[self._focus_extra])
            self.setFocus(focus)
            return
        if not listing:
            return
        self.control.reset()
        if self.mode == 'groups':
            self.rows = category_rows(self.groups, self.enabled)
            labels = [('✔  ' if enabled else '○  ') + label for _, label, enabled in self.rows]
            self.heading.setLabel('XtreamMate · SENDERGRUPPEN')
            self.sub.setLabel('OK: Gruppe öffnen · Menü: Ein/Aus')
            self.footer.setLabel('◀/Zurück: schließen   ▶: Senderliste   ▲▼: navigieren')
        else:
            self.visible_channels = channels_for_category(self.channels, self.category_id, self.enabled)
            from epg import load_cache
            from epg_views import guide_for_channel, row_title
            guide = load_cache(self.portal['id'])
            now_ts = time.time()
            labels = [row_title(c.name, guide_for_channel(
                guide, c.tvg_id, c.extra.get('stream_id', ''), now_ts))
                for c in self.visible_channels]
            self.heading.setLabel('XtreamMate · LIVE-TV')
            self.sub.setLabel('{} Sender · {}'.format(len(labels),
                next((x[1] for x in self.rows if x[0] == self.category_id), 'Aktivierte Gruppen')))
            self.footer.setLabel('◀/Zurück: Sendergruppen   OK: Umschalten')
        if not labels:
            labels = ['Senderliste wird im Hintergrund geladen …' if not self._catalog_ready
                      else 'Keine Sender in dieser Auswahl']
        self.control.addItems(labels)
        pos = self._highlight[self.mode]
        if self.mode == 'channels' and self._scroll_to_current and self.sid:
            found = next((i for i,c in enumerate(self.visible_channels)
                          if c.extra.get('stream_id') == self.sid), None)
            if found is not None:
                pos = found
            self._scroll_to_current = False
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
                self._scroll_to_current = False
                self._highlight['channels'] = 0
                self._switch('channels')
        elif self.mode == 'channels':
            i = self.control.getSelectedPosition()
            if 0 <= i < len(self.visible_channels):
                c = self.visible_channels[i]
                self._highlight['channels'] = i
                self._tune(c)

    def _tune(self, channel):
        from player import build_playable_item
        sid = str(channel.extra.get('stream_id', ''))
        if not sid:
            return
        self.sid = sid
        self._scroll_to_current = True
        announce(self.portal['id'], sid, channel.name)
        self._switch('hidden')
        xbmc.Player().play(channel.url, build_playable_item(
            channel.url, title=channel.name, logo=channel.logo))

    def _zap(self, step):
        channel = adjacent_channel(self.channels, self.category_id,
                                   self.enabled, self.sid, step)
        if channel is None:
            xbmcgui.Dialog().notification('XtreamMate',
                'Keine aktiven Sender in dieser Gruppe.')
            return
        self._tune(channel)

    def _seek(self, seconds):
        player = xbmc.Player()
        try:
            duration = float(player.getTotalTime())
            position = float(player.getTime())
            if duration < 5:
                raise ValueError('live stream without timeshift')
            player.seekTime(min(max(position+seconds, 0), duration))
        except Exception:
            xbmcgui.Dialog().notification('XtreamMate',
                'Spulen ist bei diesem Live-Sender nicht verfügbar (kein Timeshift).')

    def _epg(self):
        """Show cached EPG instantly. Missing short guide refreshes asynchronously.

        Never block a Kodi GUI action on the remote Xtream server.
        """
        import base64
        import threading
        from epg import load_cache
        import xbmcgui
        data = self.xc._get_json('get_short_epg',
                        extra={'stream_id': self.sid, 'limit': 6},
                        cached_only=True) or {}
        rows = data.get('epg_listings', []) if isinstance(data, dict) else []
        lines = []
        for item in rows:
            if not isinstance(item, dict):
                continue
            title = str(item.get('title', ''))
            try:
                decoded = base64.b64decode(title, validate=True).decode('utf-8')
                if decoded.strip(): title = decoded
            except (ValueError, TypeError, UnicodeError):
                pass
            lines.append('{}  {}'.format(item.get('start', ''), title))
        if not lines:
            channel = next((c for c in self.channels
                            if str(c.extra.get('stream_id')) == self.sid), None)
            guide = load_cache(self.portal['id'])
            tvg_id = channel.tvg_id if channel else ''
            cached = guide.get(tvg_id, []) if isinstance(guide, dict) else []
            for item in cached[:10]:
                if isinstance(item, dict):
                    lines.append('{}  {}'.format(item.get('start',
                        item.get('start_timestamp', '')), item.get('name',
                        item.get('title', ''))))
        if lines:
            xbmcgui.Dialog().textviewer('XtreamMate – EPG', '\n'.join(lines))
            return
        if not self._epg_fetching and self.sid:
            self._epg_fetching = True
            sid = str(self.sid)
            def warm():
                try:
                    self.xc.get_short_epg(sid, limit=6, force_refresh=True)
                except Exception as exc:
                    warn('XtreamMate short EPG: {}'.format(type(exc).__name__))
                finally:
                    self._epg_fetching = False
            threading.Thread(target=warm, daemon=True,
                             name='XtreamMateShortEPG').start()
        xbmcgui.Dialog().notification('XtreamMate – EPG',
            'EPG wird im Hintergrund geladen. Gleich erneut öffnen.')

    def _execute(self, section, index):
        if section == 'controls':
            if index == 0:
                try: xbmc.Player().pause()
                except Exception: pass
            elif index == 1: self._seek(-10)
            elif index == 2: self._seek(30)
            elif index == 3:
                xbmc.Player().stop()
                self.close()
        else:
            if index == 0:
                xbmc.executebuiltin('ActivateWindow(osdaudiosettings)')
            elif index == 1:
                xbmc.executebuiltin('ActivateWindow(osdvideosettings)')
            elif index == 2: self._epg()
            elif index == 3:
                import xbmcaddon
                xbmcaddon.Addon().openSettings()
            elif index == 4:
                from group_selection import manage_groups
                manage_groups(self.portal)
                from group_selection import load
                self.enabled = load(self.portal['id'])
                self._switch('groups')
                return
        self._switch('hidden')

    def handle_command(self, command):
        """Commands arrive from remote keymap or native WindowDialog.onAction."""
        if command == 'left':
            if self.mode == 'channels': self._switch('groups')
            elif self.mode == 'groups': self._switch('hidden')
            else: self._switch('channels')
        elif command == 'more':
            self._switch('extras')
        elif command == 'epg':
            self._epg()
        elif command == 'up':
            if self.mode == 'hidden': self._zap(-1)
            elif self.mode in ('groups','channels'): self._position(-1)
        elif command == 'down':
            if self.mode == 'hidden': self._zap(1)
            elif self.mode in ('groups','channels'): self._position(1)
        elif command == 'ok':
            if self.mode == 'hidden': self._switch('controls')
            elif self.mode == 'controls': self._switch('extras')
            elif self.mode == 'extras': self._execute('extras', self._focus_extra)
            else: self._select()

    def onAction(self, action):
        key = action.getId()
        if key == ACTION_STOP:
            xbmc.Player().stop()
            self.close()
            return
        if key == ACTION_PAUSE and self.mode == 'hidden':
            xbmc.Player().pause()
            return
        if key == ACTION_LEFT or key in BACK_ACTIONS:
            self.handle_command('left')
        elif key == ACTION_SELECT:
            self._last_select = time.time()
            self.handle_command('ok')
        elif key == ACTION_CONTEXT_MENU and self.mode == 'groups':
            self._toggle()
        elif key in (ACTION_UP, ACTION_DOWN, ACTION_PAGE_UP, ACTION_PAGE_DOWN):
            step = {ACTION_UP:-1,ACTION_DOWN:1,ACTION_PAGE_UP:-10,ACTION_PAGE_DOWN:10}[key]
            if self.mode == 'hidden': self._zap(step)
            elif self.mode in ('groups','channels'): self._position(step)
            elif self.mode == 'controls':
                self._focus_main = (self._focus_main + step) % len(self.main_buttons)
                self._render()
            elif self.mode == 'extras':
                self._focus_extra = (self._focus_extra + step) % len(self.extra_buttons)
                self._render()
        elif key == ACTION_RIGHT:
            if self.mode == 'groups': self._switch('channels')
            elif self.mode == 'channels': self._switch('hidden')
            elif self.mode == 'controls':
                self._focus_main = (self._focus_main+1)%len(self.main_buttons)
                self._render()
            elif self.mode == 'extras':
                self._focus_extra = (self._focus_extra+1)%len(self.extra_buttons)
                self._render()
        elif key == ACTION_PAUSE:
            xbmc.Player().pause()

    def onClick(self, control_id):
        # Kodi may invoke onAction(SELECT) and onClick for one press.
        if time.time()-self._last_select < 0.3:
            return
        if self._drawn and control_id == self.control.getId() and self.mode in ('groups','channels'):
            self._select()
            return
        if self.mode == 'controls':
            for i,button in enumerate(self.main_buttons):
                if button.getId() == control_id: self._execute('controls',i);return
        elif self.mode == 'extras':
            for i,button in enumerate(self.extra_buttons):
                if button.getId() == control_id: self._execute('extras',i);return


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

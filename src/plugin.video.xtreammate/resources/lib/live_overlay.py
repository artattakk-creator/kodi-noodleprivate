"""XCMate remote-control TV navigation, displayed over active Xtream live TV.

First OK: compact programme info. Second OK/Down: player controls.
Left opens indexed channels; Left again opens groups. Back returns one level.
Up/Down zap only in full-screen mode. Stop releases playback and dialog.

Kodi handles native list movement before Python callbacks. Bridge commands move
the list explicitly; native events must not move it a second time. No network
requests are made in input callbacks.
"""
import json
import math
import os
import time
import uuid

import xbmc
import xbmcgui

from utils import info, warn


def trace(stage, code, **fields):
    try:
        from live_diagnostics import record
        record(stage,code,**fields)
    except Exception:
        pass

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
CHANNEL_PAGE_SIZE = 100


def announce(portal_id, stream_id, channel_name=''):
    """Set a small, short-lived playback marker; never store provider passwords."""
    from live_exit import new_selection
    new_selection()
    value = {'pid': str(portal_id), 'sid': str(stream_id),
             'name': str(channel_name)[:160], 'at': time.time(),
             'nonce': uuid.uuid4().hex}
    xbmcgui.Window(10000).setProperty(SESSION_KEY, json.dumps(value))
    trace('session','ANNOUNCED',marker=True)
    return value


def session_from_property(raw, now=None):
    try:
        obj = json.loads(raw)
        if (not isinstance(obj, dict) or not obj.get('pid') or not obj.get('sid')
                or not obj.get('nonce')):
            if raw: trace('session','MARKER_INVALID',marker=True)
            return None
        at=float(obj.get('at',0))
        if not math.isfinite(at):
            trace('session','MARKER_INVALID',marker=True)
            return None
        if abs((time.time() if now is None else now) - at) > 86400:
            trace('session','MARKER_EXPIRED',marker=True)
            return None
        return obj
    except (TypeError, ValueError, KeyError):
        if raw: trace('session','MARKER_INVALID',marker=True)
        return None


def category_rows(categories, enabled):
    """Normal navigation contains active groups only; management keeps all."""
    selected=None if enabled is None else set(map(str,enabled))
    rows=[(str(c['category_id']),str(c.get('category_name') or c['category_id']),True)
          for c in categories if c.get('category_id') not in (None,'') and (selected is None or str(c['category_id']) in selected)]
    return [('*','Alle aktivierten Gruppen',True)]+rows if rows else [
        ('','Keine aktiven Gruppen – Menü: Gruppen verwalten',False)]


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

    def __init__(self, portal, initial_sid='', client=None):
        super().__init__()
        from xtream import XtreamClient
        from iptv import Channel
        from group_selection import load
        from tv_data import CatalogIndex, GuideSnapshot
        from types import SimpleNamespace
        self._theme=__import__('theme_render').snapshot()
        self.portal = portal
        self._left_counts = dict(left_received=0,left_channels=0,left_groups=0)
        from remote_profiles import load as load_bindings, DEFAULT
        try:
            self._bindings = load_bindings()
        except (OSError, ValueError, TypeError):
            self._bindings = dict(DEFAULT)
            trace('input','PROFILE_FALLBACK')
        self.xc = client if client is not None else XtreamClient(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
        self.sid = str(initial_sid)
        self._recent_sid = ''
        self._tune_deadline = 0
        self._previous_session = None
        self._window_nonce = uuid.uuid4().hex
        self.groups = []
        self.enabled = load(portal['id'])
        self.channels = []
        self.index = CatalogIndex(())
        self._identity_client = SimpleNamespace(live_stream_url=self.xc.live_stream_url,
            is_cached_live_id=lambda sid: sid in self.index.by_sid)
        self._catalog_ready = False
        # Cache-only, no network. The background service warms missing data;
        # list presentation is fast even when the provider stalls.
        self._load_catalog_from_disk()
        # 0.1.25 starts with the video unobscured; first OK is information only.
        self.mode = 'hidden'
        self._intro_deadline = None
        self._focus_main = 0
        self._focus_extra = 0
        selected_stream = next((c for c in self.channels
                                if str(c.extra.get('stream_id')) == self.sid), None)
        # Normally zap within the playing station's own category. Selecting
        # "all enabled" explicitly allows zapping across all active groups.
        self.category_id = (str(selected_stream.extra.get('category_id'))
                            if selected_stream else str(portal.get('start_group_id') or '*'))
        self._scroll_to_current = True
        self.visible_channels = []
        self._page_start = self._row_offset = 0
        self.rows = category_rows(self.groups, self.enabled)
        self._drawn = False
        self._closed = False
        self._epg_fetching = False
        self._highlight = {'channels': 0, 'groups': 0, 'guide': 0}
        self._list_key = None
        self._info_deadline = None
        self._guide_generation = -1
        self._last_tick = 0
        try:
            from utils import setting_int
            self._info_timeout = min(30,max(3,setting_int('tv_infobar_seconds',8)))
        except Exception: self._info_timeout = 8
        self._guide = GuideSnapshot(portal,self.xc)
        self._guide.request([selected_stream] if selected_stream else [])
        self._guide.start()

    def _load_catalog_from_disk(self):
        from iptv import Channel
        started=time.perf_counter()
        categories = self.xc.get_cached_catalog('get_live_categories')
        streams = self.xc.get_cached_catalog('get_live_streams')
        loaded=time.perf_counter()
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
        from group_selection import enabled_ids
        self.enabled=enabled_ids(self.portal['id'],'live',groups)
        from tv_data import CatalogIndex
        self.index = CatalogIndex(channels)
        self.index.selection('*',self.enabled)
        trace('catalog_performance','CATALOG_READY',cache_ms=(loaded-started)*1000,
              index_ms=(time.perf_counter()-loaded)*1000,channels=len(channels))
        self._catalog_ready = True
        return True

    def refresh_from_cache(self):
        """Service polls only until initial background warming has completed."""
        if self._catalog_ready or not self._load_catalog_from_disk():
            self.tick()
            return False
        self.rows = category_rows(self.groups, self.enabled)
        selected_stream = next((c for c in self.channels
                                if str(c.extra.get('stream_id')) == self.sid), None)
        if selected_stream:
            self.category_id = str(selected_stream.extra.get('category_id'))
        if self.mode in ('channels', 'groups'):
            self._render()
        return True

    def show(self):
        """Plain Omega WindowDialog does not dispatch Python onInit()."""
        if self._closed:
            return
        self._startup_stage = 'BUILD_CONTROLS'
        try:
            if not self._drawn:
                self._build_controls()
                xbmcgui.Window(10000).setProperty('XtreamMate.NativeActionCount','0')
                trace('input','WAITING_FOR_ACTION',count=0,
                      learned_left_action=self._bindings.get('left',ACTION_LEFT))
            try: self.setProperty('XtreamMate.NavigatorIdentity',self._window_nonce)
            except Exception: pass
            trace('dialog','SHOW_REQUESTED',channels=len(self.channels),catalog=self._catalog_ready)
            self._startup_stage = 'WINDOW_SHOW'
            super().show()
            self._startup_stage = 'RENDER'
            self._render()
            self._startup_stage = 'FOCUS'
            self.observe_focus()
        except Exception as exc:
            trace('dialog','SHOW_FAILED',failure_stage=self._startup_stage,
                  exception_class=type(exc).__name__)
            self.close()
            raise

    def observe_focus(self):
        focus_id=dialog_id=-1
        try: focus_id=self.getFocusId()
        except Exception: pass
        try: dialog_id=xbmcgui.getCurrentWindowDialogId()
        except Exception: pass
        controls=([self.control,self.capture,*self.main_buttons,*self.extra_buttons]
                  if self._drawn else [])
        trace('focus','OBSERVED',focus_id=focus_id,dialog_id=dialog_id,
              focused=any(c.getId()==focus_id for c in controls))
        if dialog_id>0:
            try:
                active=xbmcgui.Window(dialog_id).getProperty('XtreamMate.NavigatorIdentity')==self._window_nonce
                trace('focus','ACTIVE_DIALOG' if active else 'OTHER_DIALOG',
                      focus_id=focus_id,dialog_id=dialog_id,focused=active)
            except Exception: pass

    def close(self):
        if self._closed:
            return
        self._closed = True
        if hasattr(self, '_guide'): self._guide.close()
        self._intro_deadline = None
        super().close()
        marker = xbmcgui.Window(10000)
        marker.clearProperty('XtreamMate.RemoteCommand')
        session = session_from_property(marker.getProperty(SESSION_KEY))
        if session and (session['pid'], session['sid']) == (str(self.portal['id']), self.sid) and (not getattr(self,'_exit_nonce','') or session['nonce']==self._exit_nonce):
            marker.clearProperty(SESSION_KEY)
        marker.setProperty('XtreamMate.OverlayStatus', 'geschlossen')
        trace('dialog','CLOSED',video=xbmc.Player().isPlayingVideo())
        try:
            from live_diagnostics import checkpoint
            checkpoint()
        except Exception: pass

    def owns_playback(self):
        """Release input immediately if playback belongs to another add-on."""
        try:
            player = xbmc.Player()
            if not player.isPlayingVideo():
                return False
            from live_recovery import playback_match
            session=session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
            match,reason = playback_match(player,[self.portal],lambda *args:self._identity_client,session)
            if not match and self._previous_session and time.monotonic()<self._tune_deadline:
                match,reason=playback_match(player,[self.portal],lambda *args:self._identity_client,self._previous_session)
                if match: reason='PREVIOUS_'+reason
            trace('ownership',reason,video=True,marker=bool(session),catalog=self._catalog_ready)
            if not match or match[0] != str(self.portal['id']):
                return False
            # Player.play is asynchronous; the old verified live URL may remain
            # visible briefly while Kodi resolves the newly selected channel.
            return (match[1] == self.sid or
                    (match[1] == self._recent_sid and
                     time.monotonic() < self._tune_deadline))
        except Exception:
            trace('ownership','CHECK_FAILED')
            return False

    def _accept_input(self):
        if self._closed or getattr(self,'_exiting',False):
            return False
        if not self.owns_playback():
            self.close()
            return False
        from playback_exit import identity
        try:self._owned_token=identity(xbmc.Player())
        except (AttributeError,RuntimeError):self._owned_token=None
        return True

    def _request_exit(self):
        from live_exit import request,_trace
        try:accepted=request(self)
        except (AttributeError,RuntimeError):accepted=False
        if not accepted:_trace('STOP_REJECTED')
        return accepted

    def _build_controls(self):
        import xbmcaddon
        width, height = max(960,self.getWidth()), max(640,self.getHeight())
        self._width, self._height = width,height
        self._media = os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media')
        media = self._media
        normal,focused,clear = [__import__('theme_render').texture(self,os.path.join(media,s+'.png'),'') for s in ('tv_normal','tv_focus','remote_clear')]
        panel = os.path.join(media,'tv_panel.png')
        sidebar = min(800,int(width*.65))
        self._sidebar = sidebar
        self.bg = xbmcgui.ControlImage(24,24,sidebar,height-48,__import__('theme_render').texture(self,panel,'panel.sidebar'))
        self.heading = xbmcgui.ControlLabel(48,38,sidebar-48,36,'XCMate','font16','0xFFF0F2F5')
        self.sub = xbmcgui.ControlLabel(48,78,sidebar-48,28,'','font12','0xFFB6BCC6')
        self._startup_stage = 'CONTROL_LIST'
        # Native list owns focus and movement. Its labels are drawn below as a
        # bounded eight-row viewport, avoiding skin-specific label layouts.
        self.control = xbmcgui.ControlList(44,116,sidebar-40,height-198,
            font='font13',textColor='0x00000000',selectedColor='0x00000000',
            buttonTexture=clear,buttonFocusTexture=clear,_itemHeight=46,_space=3)
        self._startup_stage = 'BUILD_CONTROLS'
        self.capture = xbmcgui.ControlButton(24,24,8,8,'',focusTexture=clear,noFocusTexture=clear)
        self.footer = xbmcgui.ControlLabel(48,height-73,sidebar-48,30,'','font12','0xFFB6BCC6')
        self._row_controls = []
        row_height = (height-210)//8
        for i in range(8):
            y = 116+i*row_height
            self._row_controls.append((
                xbmcgui.ControlImage(44,y,sidebar-40,row_height-3,focused),
                xbmcgui.ControlImage(52,y+7,42,42,__import__('theme_render').texture(self,os.path.join(media,'tv.png'),'icon.live'),aspectRatio=2),
                xbmcgui.ControlLabel(106,y+1,sidebar-128,27,'','font13','0xFFF0F2F5'),
                xbmcgui.ControlLabel(106,y+28,sidebar-128,25,'','font12','0xFFB6BCC6')))
        self.info_bg = xbmcgui.ControlImage(32,height-248,width-64,216,__import__('theme_render').texture(self,panel,'panel.player.infobar'))
        self.info_logo = xbmcgui.ControlImage(54,height-214,96,96,__import__('theme_render').texture(self,os.path.join(media,'tv.png'),'icon.live'),aspectRatio=2)
        self.info_name = xbmcgui.ControlLabel(174,height-234,width-220,32,'','font16','0xFFF0F2F5')
        self.info_now = xbmcgui.ControlLabel(174,height-193,width-465,29,'','font13','0xFFF0F2F5')
        self.info_times = xbmcgui.ControlLabel(width-280,height-193,230,29,'','font13','0xFFD2D8E0')
        self._progress_width = width-460
        self.info_track = xbmcgui.ControlImage(174,height-153,self._progress_width,8,__import__('theme_render').texture(self,normal,'panel.player.progress-track'))
        self.info_progress = xbmcgui.ControlImage(174,height-153,self._progress_width,8,os.path.join(media,'tv_progress.png'))
        self.info_duration = xbmcgui.ControlLabel(174,height-131,width-220,27,'','font12','0xFFB6BCC6')
        self.info_next = xbmcgui.ControlLabel(174,height-99,width-220,29,'','font13','0xFFF0F2F5')
        self.info_hint = xbmcgui.ControlLabel(174,height-61,width-220,24,'OK / Runter: Bedienung    Links: Sender    Zurück: TV','font12','0xFFB6BCC6')
        self._info_controls = [self.info_bg,self.info_logo,self.info_name,self.info_now,self.info_times,
                              self.info_track,self.info_progress,self.info_duration,self.info_next,self.info_hint]
        self.osd_bg = xbmcgui.ControlImage(32,height-204,width-64,172,__import__('theme_render').texture(self,panel,'panel.player.controls'))
        self.osd_title = xbmcgui.ControlLabel(52,height-194,width-104,30,'XCMate','font13','0xFFF0F2F5')
        self.main_buttons,self.extra_buttons,self._button_icons = [],[],[]
        # Stable action indices; visual tape-deck order is defined in _render.
        main = [('Pause','pause'),('-10 s','back'),('+30 s','forward'),('Stop','stop'),('Weitere','more'),('Live-Ende','live')]
        extra = [('Ton','audio'),('Bild','video'),('Untertitel','subtitle'),('EPG','epg'),('Einstellungen','settings'),('Gruppen','tv')]
        for entries,buttons,y in ((main,self.main_buttons,height-150),(extra,self.extra_buttons,height-150)):
            space = (width-104)//len(entries)
            for i,(label,icon) in enumerate(entries):
                buttons.append(xbmcgui.ControlButton(52+i*space,y,space-8,46,label,
                    focusTexture=focused,noFocusTexture=normal,textOffsetX=36,font='font13',disabledColor='0xFF6F7780'))
                self._button_icons.append((buttons[-1],xbmcgui.ControlImage(60+i*space,y+12,22,22,
                    __import__('theme_render').texture(self,os.path.join(media,'tv_'+icon+'.png'),''))))
        all_controls = [self.bg,self.heading,self.sub,self.control,self.footer,self.capture,
            *[c for row in self._row_controls for c in row],*self._info_controls,
            self.osd_bg,self.osd_title,*self.main_buttons,*self.extra_buttons,
            *[image for _,image in self._button_icons]]
        for control in all_controls: self.addControl(control)
        for control in (self.capture,*self.main_buttons,*self.extra_buttons):
            control.setNavigation(control,control,control,control)
        self.control.controlLeft(self.control)
        self.control.controlRight(self.control)
        self._drawn = True
        marker = xbmcgui.Window(10000)
        marker.setProperty('XtreamMate.OverlayStatus','bereit')
        marker.setProperty('XtreamMate.InputMode','native WindowDialog / onControl')
        marker.setProperty('XtreamMate.AutoPopupStatus','LIVE_FULL - OK: Senderinformation')

    def _can_seek(self):
        try:
            duration=float(xbmc.Player().getTotalTime())
            return bool(xbmc.getCondVisibility('Player.SeekEnabled') and math.isfinite(duration) and duration>5)
        except Exception: return False

    def _render_transport(self):
        self.osd_bg.setImage(__import__('theme_render').texture(self,os.path.join(self._media,'tv_panel.png'),'panel.player.options' if self.mode=='extras' else 'panel.player.controls'))
        paused=bool(xbmc.getCondVisibility('Player.Paused'))
        self.main_buttons[0].setLabel('Weiter' if paused else 'Pause')
        self._button_icons[0][1].setImage(__import__('theme_render').texture(self,os.path.join(self._media,'tv_play.png' if paused else 'tv_pause.png'),''))

    def _local_logo(self, channel):
        from logo_cache import local_logo
        return local_logo(getattr(channel,'logo','')) or __import__('theme_render').texture(self,os.path.join(self._media,'tv.png'),'icon.settings.groups' if self.mode=='groups' else 'icon.epg.clock' if self.mode=='guide' else 'icon.live')

    def _render_info(self):
        channel = self.index.by_sid.get(self.sid)
        self._guide.request([channel] if channel else [])
        before=time.perf_counter()
        info = self._guide.get(self.sid)
        self._snapshot_ms=getattr(self,'_snapshot_ms',0)+(time.perf_counter()-before)*1000
        self.info_logo.setImage(self._local_logo(channel))
        self.info_name.setLabel(channel.name if channel else 'Live-TV')
        self.info_now.setLabel('JETZT: '+info['now'] if info['now'] else 'Für diesen Sender keine EPG-Daten verfügbar')
        self.info_times.setLabel('{} - {} Uhr'.format(info['now_time'],info['now_end_time']) if info['now'] else '')
        for control in (self.info_track,self.info_progress,self.info_duration): control.setVisible(bool(info['now']))
        if info['now']:
            self.info_progress.setWidth(max(1,int(self._progress_width*info['progress'])))
            self.info_progress.setVisible(info['progress']>0)
            self.info_duration.setLabel('{} / {} Min. vergangen    Noch {} Minuten'.format(
                int(info['elapsed']//60),max(1,int((info['stop']-info['start']+59)//60)),
                max(1,int((info['remaining']+59)//60))))
        self.info_next.setLabel('DANACH: {}    ab {} Uhr'.format(info['next'],info['next_time'])
                                if info['next'] else 'DANACH: Keine Programmdaten verfügbar')

    def _list_content(self):
        if self.mode == 'groups':
            self.rows = category_rows(self.groups,self.enabled)
            return [name for _,name,_ in self.rows]
        if self.mode == 'guide':
            info = self._guide.get(self._guide_sid)
            self._programme_events = info['events']
            return ['{} - {}  {}'.format(time.strftime('%H:%M',time.localtime(e['start'])),
                    time.strftime('%H:%M',time.localtime(e['stop'])),e['title']) for e in self._programme_events] or [
                    'Keine EPG-Daten - Quellenstatus im XCMate-Hauptmenü prüfen']
        self.visible_channels, positions = self.index.selection(self.category_id,self.enabled)
        pos = self._highlight['channels']
        if self._scroll_to_current:
            pos = positions.get(self.sid,pos)
            self._scroll_to_current = False
        pos = min(max(pos,0),max(len(self.visible_channels)-1,0))
        self._highlight['channels'] = pos
        self._page_start = pos//CHANNEL_PAGE_SIZE*CHANNEL_PAGE_SIZE
        self._row_offset = 0
        page = self.visible_channels[self._page_start:self._page_start+CHANNEL_PAGE_SIZE]
        labels = [c.name for c in page]
        return labels or ['Senderkatalog wird vorbereitet' if not self._catalog_ready else 'Keine aktivierten Sender']

    def _render_rows(self):
        selected = max(0,self.control.getSelectedPosition())
        first = selected//8*8
        self.footer.setLabel('OK: auswählen    Links: Gruppen    Zurück: TV')
        wanted = []
        playing = self.index.by_sid.get(self.sid)
        if playing: wanted.append(playing)
        for row,(background,logo,title,detail) in enumerate(self._row_controls):
            i = first+row
            available = i<len(self._labels)
            for c in (logo,title,detail): c.setVisible(available)
            background.setVisible(available and i==selected)
            if not available: continue
            label,subtitle,channel = self._labels[i],'',None
            if self.mode == 'channels':
                absolute = self._page_start+i-self._row_offset
                if self._row_offset<=i<self._row_offset+min(CHANNEL_PAGE_SIZE,len(self.visible_channels)-self._page_start):
                    channel = self.visible_channels[absolute]
                    wanted.append(channel)
                    sid = str(channel.extra.get('stream_id',''))
                    before=time.perf_counter()
                    info = self._guide.get(sid)
                    self._snapshot_ms=getattr(self,'_snapshot_ms',0)+(time.perf_counter()-before)*1000
                    label = ('LIVE  ' if sid==self.sid else '')+channel.name
                    subtitle = '{}-{}  {}'.format(info['now_time'],info['now_end_time'],info['now']) if info['now'] else 'Keine aktuellen EPG-Daten'
                    if i==selected and info['next']:
                        self.footer.setLabel('Danach {}: {}'.format(info['next_time'],info['next']))
            elif self.mode == 'guide' and i<len(self._programme_events):
                subtitle = self._programme_events[i].get('description','')[:100]
            title.setLabel(label)
            detail.setLabel(subtitle)
            logo.setImage(self._local_logo(channel))
        if self.mode == 'guide':
            channel = self.index.by_sid.get(self._guide_sid)
            if channel: wanted.append(channel)
        self._guide.request(wanted)

    def _render(self, focus=True):
        if not self._drawn: return
        begin = time.perf_counter()
        self._snapshot_ms=0
        index_ms=0
        listing = self.mode in ('groups','channels','guide')
        osd = self.mode in ('controls','extras')
        for c in (self.bg,self.heading,self.sub,self.control,self.footer): c.setVisible(listing)
        for row in self._row_controls:
            for c in row: c.setVisible(False)
        for c in self._info_controls: c.setVisible(self.mode=='info')
        for c in (self.osd_bg,self.osd_title): c.setVisible(osd)
        seek = self._can_seek() if osd else False
        transport = [1,0,2,5,3,4]
        self._main_indices = transport if seek else [0,3,4]
        for i,c in enumerate(self.main_buttons):
            c.setVisible(self.mode=='controls')
            c.setEnabled(i in self._main_indices)
        for slot,i in enumerate(transport):
            space=(self._width-104)//len(transport)
            self.main_buttons[i].setPosition(52+slot*space,self._height-150)
            self.main_buttons[i].setWidth(space-8)
            self._button_icons[i][1].setPosition(60+slot*space,self._height-138)
        for c in self.extra_buttons: c.setVisible(self.mode=='extras')
        for button,image in self._button_icons:
            image.setVisible(button in self.main_buttons and self.mode=='controls' or
                             button in self.extra_buttons and self.mode=='extras')
        target = self.capture
        if self.mode=='info': self._render_info()
        elif osd:
            self._render_transport()
            if self._focus_main not in self._main_indices:
                previous=self.main_buttons[self._focus_main]
                self._focus_main=0
                if self.mode=='controls' and not focus:
                    try:
                        dialog=xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
                        # Repair a newly disabled seek focus only while this
                        # dialog is topmost; never steal Audio/Video's focus.
                        focus=(self.getFocusId()==previous.getId() and
                               dialog.getProperty('XtreamMate.NavigatorIdentity')==self._window_nonce)
                    except (AttributeError,RuntimeError): pass
            title = ('Player - Runter: Einstellungen' if seek else
                     'Player - Kein Spulen/Live-Ende verfügbar - Runter: Einstellungen')
            self.osd_title.setLabel('XCMate - '+(title if self.mode=='controls' else 'Einstellungen - Hoch: Player'))
            target = self.main_buttons[self._focus_main] if self.mode=='controls' else self.extra_buttons[self._focus_extra]
        elif listing:
            index_begin=time.perf_counter()
            labels = self._list_content()
            index_ms=(time.perf_counter()-index_begin)*1000
            key = (self.mode,self.category_id,self._page_start,tuple(labels))
            if key != self._list_key:
                self.control.reset()
                self.control.addItems(labels)
                self._labels,self._list_key = labels,key
                pos = self._highlight[self.mode]
                if self.mode=='channels': pos = pos-self._page_start+self._row_offset
                self.control.selectItem(min(max(pos,0),len(labels)-1))
            self.heading.setLabel('XCMate - '+{'channels':'LIVE-TV','groups':'SENDERGRUPPEN','guide':'PROGRAMM'}[self.mode])
            if self.mode=='channels':
                self.sub.setLabel('{} Sender'.format(len(self.visible_channels)))
            elif self.mode=='guide':
                ch=self.index.by_sid.get(self._guide_sid)
                self.sub.setLabel(ch.name if ch else 'Programmübersicht')
            else: self.sub.setLabel('OK: öffnen    Menü: Gruppen verwalten')
            self.footer.setLabel('OK: auswählen    Links: Gruppen    Zurück: TV')
            self._render_rows()
            target = self.control
        render_end = time.perf_counter()
        if focus: self.setFocus(target)
        trace('performance',self.mode.upper(),index_ms=index_ms,snapshot_ms=self._snapshot_ms,
              render_ms=max(0,(render_end-begin)*1000-index_ms-self._snapshot_ms),focus_ms=(time.perf_counter()-render_end)*1000,
              items=len(getattr(self,'_labels',[])) if listing else 0)

    def tick(self):
        if self._closed or not self._drawn: return
        now=time.monotonic()
        if self.mode=='info' and self._info_deadline is not None and now>=self._info_deadline:
            self._switch('hidden')
            return
        if now-self._last_tick<1: return
        self._last_tick=now
        if self.mode=='info': self._render_info()
        elif self.mode in ('controls','extras'):
            self._render(focus=False)
        elif self.mode in ('channels','groups','guide') and self._guide.generation!=self._guide_generation:
            self._guide_generation=self._guide.generation
            self._render(focus=False)

    def expire_intro(self):
        """Service timer: refresh local info and expire only the INFO_BAR."""
        self.tick()

    def _position(self, step):
        if self.mode=='channels':
            self._move_channels(step)
            return
        count = self.control.size()
        if count > 0:
            i = min(max(self.control.getSelectedPosition() + step, 0), count - 1)
            self.control.selectItem(i)
            self._remember_position()
            self._render_rows()

    def _remember_position(self):
        i = self.control.getSelectedPosition()
        if self.mode == 'channels':
            i = self._page_start + i - self._row_offset
            # Page links are not channels and must never become tune targets.
            if not self._page_start <= i < min(self._page_start+CHANNEL_PAGE_SIZE,
                                                len(self.visible_channels)):
                return
        self._highlight[self.mode] = i

    def _move_channels(self,step):
        """Absolute position; Kodi's native list movement is never applied twice."""
        if not self.visible_channels: return False
        previous=self._highlight['channels']
        target=min(max(previous+step,0),len(self.visible_channels)-1)
        self._highlight['channels']=target
        self._scroll_to_current=False
        if not self._page_start<=target<self._page_start+CHANNEL_PAGE_SIZE:
            self._render()
        else:
            self.control.selectItem(target-self._page_start)
            self._render_rows()
        return target!=previous

    def _page_channels(self, step):
        if len(self.visible_channels)<=CHANNEL_PAGE_SIZE: return False
        return self._move_channels(step*CHANNEL_PAGE_SIZE)

    def _switch(self, mode):
        self.mode = mode
        self._info_deadline = time.monotonic()+self._info_timeout if mode=='info' else None
        self._render()

    def _toggle(self):
        """Menu opens explicit checkbox management, never toggles a nav row."""
        if self.mode!='groups': return
        from group_selection import choose_groups,enabled_ids
        if not choose_groups(self.portal,'live',categories=self.groups,allow_refresh=False): return
        self.enabled=enabled_ids(self.portal['id'],'live',self.groups)
        self._load_catalog_from_disk()
        if self.category_id!='*' and self.category_id not in self.enabled: self.category_id='*'
        self._highlight['groups']=0
        self._highlight['channels']=0
        self._scroll_to_current=False
        self._list_key=None
        self._render()

    def _select(self):
        if self.mode == 'groups':
            i = self.control.getSelectedPosition()
            if 0 <= i < len(self.rows):
                cid, _, active = self.rows[i]
                if not active: return
                self.category_id = cid
                self._scroll_to_current = False
                self._highlight['channels'] = 0
                self._switch('channels')
        elif self.mode == 'guide':
            i = self.control.getSelectedPosition()
            if 0<=i<len(self._programme_events):
                event=self._programme_events[i]
                xbmcgui.Dialog().textviewer('XCMate - '+event['title'],event.get('description') or 'Keine Beschreibung vorhanden.')
        elif self.mode == 'channels':
            row = self.control.getSelectedPosition()
            i = self._page_start + row - self._row_offset
            if 0 <= i < len(self.visible_channels):
                c = self.visible_channels[i]
                self._highlight[self.mode] = i
                self._tune(c)

    def _tune(self, channel):
        from player import build_playable_item
        sid = str(channel.extra.get('stream_id', ''))
        if not sid:
            return
        if self.sid != sid:
            self._recent_sid = self.sid
            self._tune_deadline = time.monotonic() + 8
        self.sid = sid
        current = self.index.by_sid.get(sid)
        self._guide.request([current] if current else [])
        self._scroll_to_current = True
        self._previous_session=session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
        session=announce(self.portal['id'], sid, channel.name)
        self._switch('hidden')
        item = build_playable_item(channel.url, title=channel.name, logo=channel.logo)
        from live_recovery import tag_live_item
        trace('session','ITEM_TAGGED' if tag_live_item(item,session) else 'ITEM_TAG_UNAVAILABLE',marker=True)
        xbmc.Player().play(item.getPath(), item)

    def _zap(self, step):
        rows,positions = self.index.selection(self.category_id,self.enabled)
        pos = (positions[self.sid]+step)%len(rows) if self.sid in positions else (0 if step>0 else -1)
        channel = rows[pos] if rows else None
        if channel is None:
            xbmcgui.Dialog().notification('XCMate',
                'Keine aktiven Sender in dieser Gruppe.')
            return
        self._tune(channel)

    def _seek(self, seconds):
        if not self._can_seek(): return
        player = xbmc.Player()
        try:
            duration = float(player.getTotalTime())
            position = float(player.getTime())
            if not math.isfinite(position):
                raise ValueError('live stream without timeshift')
            player.seekTime(duration if seconds is None else min(max(position+seconds, 0), duration))
        except Exception:
            xbmcgui.Dialog().notification('XCMate',
                'Spulen ist bei diesem Live-Sender nicht verfügbar (kein Timeshift).')

    def _epg(self):
        self._guide_return = self.mode if self.mode != 'guide' else getattr(self,'_guide_return','extras')
        self._guide_sid = self.sid
        self._highlight['guide'] = 0
        self._switch('guide')

    def _execute(self, section, index):
        if section == 'controls':
            if index in (1,2,5) and not self._can_seek(): return
            if index == 4:
                self._switch('extras')
                return
            if index == 0: xbmc.Player().pause()
            elif index == 1: self._seek(-10)
            elif index == 2: self._seek(30)
            elif index == 5: self._seek(None)
            elif index == 3:
                self._request_exit()
                return
            self._render()
        else:
            if index == 3:
                self._epg()
                return
            if index == 5:
                self._switch('groups')
                return
            self._switch('hidden')
            if index in (0,1,2):
                window=('osdaudiosettings','osdvideosettings','osdsubtitlesettings')[index]
                xbmc.executebuiltin('ActivateWindow('+window+')')
            elif index == 4:
                import xbmcaddon
                xbmcaddon.Addon().openSettings()

    def _recent(self):
        channel = self.index.by_sid.get(self._recent_sid)
        if channel is not None:
            self._tune(channel)
        else:
            xbmcgui.Dialog().notification('XCMate', 'Noch kein vorheriger Sender.')

    def _search_channels(self):
        """Only cached channel names; no portal access or network requests."""
        query = xbmcgui.Dialog().input('XCMate – Sender suchen')
        if not query:
            return
        choices = channels_for_category(self.channels, '*', self.enabled)
        result = next((ch for ch in choices if query.casefold() in ch.name.casefold()), None)
        if result is None:
            xbmcgui.Dialog().notification('XCMate', 'Kein passender Sender gefunden.')
            return
        self.category_id = str(result.extra.get('category_id') or '*')
        self._scroll_to_current = False
        self._highlight['channels'] = next((i for i,c in enumerate(
            channels_for_category(self.channels, self.category_id, self.enabled))
            if str(c.extra.get('stream_id')) == str(result.extra.get('stream_id'))), 0)
        self._switch('channels')

    def _input_trace(self, code, source, command='', before=None, **fields):
        try: focus_id=self.getFocusId()
        except (RuntimeError, AttributeError): focus_id=-1
        counts=getattr(self,'_left_counts',{})
        if code=='COMMAND_HANDLED' and source=='native' and fields.get('action_id')==ACTION_LEFT:
            counts['left_received']=counts.get('left_received',0)+1
            if before in ('hidden','info') and self.mode=='channels':
                counts['left_channels']=counts.get('left_channels',0)+1
            elif before=='channels' and self.mode=='groups':
                counts['left_groups']=counts.get('left_groups',0)+1
        trace('input',code,input_source=source,command=command,
              mode_before=before or self.mode,mode_after=self.mode,focus_id=focus_id,
              learned_left_action=getattr(self,'_bindings',{}).get('left',ACTION_LEFT),**counts,**fields)

    def handle_command(self, command, source='bridge', **fields):
        before=self.mode
        try: fields['focus_before']=self.getFocusId()
        except (RuntimeError,AttributeError): pass
        if not self._accept_input():
            self._input_trace('COMMAND_REJECTED',source,command,before,**fields)
            return
        self._handle_command(command)
        self._input_trace('COMMAND_HANDLED',source,command,before,**fields)

    def _handle_command(self, command):
        """XCMate-local TV commands; never open Kodi's own player OSD."""
        self._intro_deadline = None
        if self.mode=='info': self._info_deadline=time.monotonic()+self._info_timeout
        if command in ('left', 'long_left'):
            if self.mode in ('controls', 'extras'):
                if self.mode == 'controls':
                    self._focus_main = self._main_indices[(self._main_indices.index(self._focus_main)-1)%len(self._main_indices)]
                else:
                    self._focus_extra = (self._focus_extra - 1) % len(self.extra_buttons)
                self._render()
            elif self.mode == 'channels':
                self._switch('groups')
            elif self.mode == 'groups':
                self._switch('hidden')
            else:
                self._switch('channels')
        elif command == 'right':
            if self.mode == 'hidden':
                self._recent()
            elif self.mode == 'groups':
                self._switch('channels')
            elif self.mode in ('channels','guide'):
                self._switch('hidden')
            elif self.mode in ('controls','extras'):
                if self.mode == 'controls':
                    self._focus_main = self._main_indices[(self._main_indices.index(self._focus_main)+1)%len(self._main_indices)]
                else:
                    self._focus_extra = (self._focus_extra + 1) % len(self.extra_buttons)
                self._render()
        elif command in ('more', 'long_ok', 'menu', 'long_menu'):
            if command == 'menu' and self.mode == 'groups':
                self._toggle()
            elif command == 'long_menu':
                self._epg()
            else:
                self._switch('extras')
        elif command in ('epg', 'guide'):
            self._epg()
        elif command in ('info', 'long_right'):
            self._switch('info')
        elif command in ('back',):
            if self.mode == 'hidden':
                self._request_exit()
            elif self.mode == 'channels':
                self._switch('hidden')
            elif self.mode == 'guide':
                self._switch(self._guide_return)
            elif self.mode == 'groups':
                self._switch('channels')
            elif self.mode == 'extras':
                self._switch('controls')
            elif self.mode == 'controls':
                self._switch('info')
            else:
                self._switch('hidden')
        elif command == 'long_back':
            self._request_exit()
        elif command == 'long_up':
            self._recent()
        elif command == 'long_down':
            self._search_channels()
        elif command == 'long_play_pause':
            self._seek(None)
        elif command == 'play_pause':
            xbmc.Player().pause()
        elif command in ('up', 'down'):
            if self.mode == 'hidden':
                self._zap(1 if command == 'up' else -1)
            elif self.mode=='info':
                if command=='down': self._switch('controls')
                else: self._switch('hidden')
            elif self.mode in ('channels', 'groups', 'guide'):
                self._position(-1 if command == 'up' else 1)
            elif self.mode in ('controls','extras'):
                if self.mode=='controls': self._switch('info' if command=='up' else 'extras')
                elif command=='up': self._switch('controls')
        elif command == 'ok':
            if self.mode == 'hidden':
                self._switch('info')
            elif self.mode=='info':
                self._focus_main=0
                self._switch('controls')
            elif self.mode == 'controls':
                self._execute('controls', self._focus_main)
            elif self.mode == 'extras':
                self._execute('extras', self._focus_extra)
            else:
                self._select()

    def onAction(self, action):
        """Native Kodi Android actions take priority while our dialog owns focus.

        Log numeric action/buttoncode only; never include stream URLs.
        The keymap bridge is a fallback, not the sole remote input path.
        """
        key = int(action.getId())
        try:
            raw = int(action.getButtonCode())
        except Exception:
            raw = 0
        if key==ACTION_STOP and not self._closed and not getattr(self,'_exiting',False):
            self._request_exit();return
        was_closed=getattr(self,'_closed',False)
        if not self._accept_input():
            trace('input','ACTION_IGNORED_CLOSED' if was_closed else 'ACTION_REJECTED',
                  action_id=key,button_code=raw)
            return
        self._intro_deadline = None
        marker = xbmcgui.Window(10000)
        marker.setProperty('XtreamMate.LastRemoteKey', '{} / {} (native)'.format(key, raw))
        marker.setProperty('XtreamMate.AutoPopupStatus',
                           'natives Action-Event empfangen')
        try:
            count = int(marker.getProperty('XtreamMate.NativeActionCount') or '0')
        except (ValueError, TypeError):
            count = 0
        marker.setProperty('XtreamMate.NativeActionCount', str(count+1))
        self._input_trace('NATIVE_ACTION','native',action_id=key,button_code=raw,count=count+1)
        # Back and Context are *not* Kodi player OSD commands in XCMate.
        # Must override learned Back->left and default Menu->epg from old profiles.
        if key in BACK_ACTIONS:
            mapped = 'back'
        elif key == ACTION_CONTEXT_MENU:
            mapped = 'menu'
        elif key == ACTION_PAUSE:
            mapped = 'play_pause'
        elif key == ACTION_RIGHT:
            mapped = 'right'
        elif key == ACTION_LEFT:
            mapped = 'left'
        elif key in (ACTION_UP, ACTION_DOWN, ACTION_PAGE_UP, ACTION_PAGE_DOWN) and self.mode in ('channels', 'guide', 'groups'):
            # CGUIControlList already applied this action before onAction.
            if key in (ACTION_UP,ACTION_DOWN) and self.mode=='channels':
                self._move_channels(-1 if key==ACTION_UP else 1)
                self._input_trace('NATIVE_LIST_MOVED','native',action_id=key,button_code=raw)
                return
            elif key in (ACTION_PAGE_UP, ACTION_PAGE_DOWN) and self.mode == 'channels':
                if not self._page_channels(-1 if key == ACTION_PAGE_UP else 1):
                    self._remember_position()
            else:
                self._remember_position()
            self._render_rows()
            self._input_trace('NATIVE_LIST_MOVED','native',action_id=key,button_code=raw)
            return
        elif key == ACTION_SELECT:
            # Omega dispatches onControl BEFORE onAction(SELECT). Handling
            # SELECT here too would execute a second action in the new mode.
            marker.setProperty('XtreamMate.LastHandledKey', 'ok')
            self._input_trace('SELECT_ALREADY_CLICKED','native',action_id=key,button_code=raw)
            return
        elif key in (ACTION_UP, ACTION_DOWN):
            mapped = 'up' if key==ACTION_UP else 'down'
        else:
            from remote_profiles import mapped_action
            mapped = mapped_action(key, self._bindings)
        if mapped:
            marker.setProperty('XtreamMate.LastHandledKey', mapped)
            self.handle_command(mapped,source='native',action_id=key,button_code=raw)
        else:
            self._input_trace('ACTION_UNMAPPED','native',action_id=key,button_code=raw)

    def onControl(self, control):
        """Omega's click callback for programmatically created controls."""
        if not self._accept_input() or not self._drawn:
            return
        control_id = control.getId()
        if control_id == self.capture.getId():
            self.handle_command('ok',source='control',control_id=control_id)
            return
        if control_id == self.control.getId() and self.mode in ('groups','channels','guide'):
            self.handle_command('ok',source='control',control_id=control_id)
            return
        if self.mode == 'controls':
            for i,button in enumerate(self.main_buttons):
                if button.getId() == control_id:
                    if i not in self._main_indices: return
                    self._focus_main=i
                    self.handle_command('ok',source='control',control_id=control_id)
                    return
        elif self.mode == 'extras':
            for i,button in enumerate(self.extra_buttons):
                if button.getId() == control_id:
                    self._focus_extra=i
                    self.handle_command('ok',source='control',control_id=control_id)
                    return


def start_if_eligible(last_nonce):
    """Return overlay instance or None. Called in the service's main thread."""
    if not xbmc.Player().isPlayingVideo():
        return None
    session = session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
    if not session or session['nonce'] == last_nonce:
        trace('dialog','NO_SESSION' if not session else 'SESSION_ALREADY_HANDLED',marker=bool(session))
        return None
    from portals import get_by_id
    portal = get_by_id(session['pid'])
    if not portal or portal.get('type') != 'xtream' or not portal.get('enabled',True):
        trace('dialog','PORTAL_UNAVAILABLE',marker=True)
        return None
    try:
        candidate = LiveNavigator(portal, session['sid'])
        trace('dialog','CANDIDATE_CREATED',channels=len(candidate.channels),catalog=candidate._catalog_ready)
        if candidate.owns_playback(): return candidate
        candidate.close()
        return None
    except Exception as exc:
        trace('dialog','CONSTRUCTION_FAILED')
        warn('XCMate navigator cannot start: {}'.format(type(exc).__name__))
        return None

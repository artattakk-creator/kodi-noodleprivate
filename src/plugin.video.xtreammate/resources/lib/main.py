import sys
import time
import urllib.parse
import json
import threading
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

from utils import (
    setting, setting_bool, setting_int,
    load_favourites, toggle_favourite, is_favourite,
    cache_clear, notify, debug, info, warn, error,
    apply_lang_sort, _L
)

ADDON      = xbmcaddon.Addon()
ADDON_ID   = ADDON.getAddonInfo('id')
ADDON_PATH = ADDON.getAddonInfo('path').rstrip('/')
ADDON_ICON   = ADDON_PATH + '/icon.png'
ADDON_FANART = ADDON_PATH + '/fanart.jpg'

def _media(name):
    return ADDON_PATH + '/resources/media/' + name


_ICON_TV       = _media('tv.png')
_ICON_EPG      = _media('epg.png')
_ICON_VOD      = _media('vod.png')
_ICON_SERIES   = _media('series.png')
_ICON_FAV      = _media('favorites.png')
_ICON_SEARCH   = _media('search.png')
_ICON_SETTINGS = _media('settings.png')
_ICON_REC      = _media('recordings.png')
_ICON_CATCHUP  = _media('catchup.png')


class Router:
    def __init__(self, argv):
        self._handle = int(argv[1])
        self._base   = argv[0]
        args = argv[2][1:] if len(argv) > 2 else ''
        self._params = dict(urllib.parse.parse_qsl(args, keep_blank_values=True))

    def url(self, **kw):
        return self._base + '?' + urllib.parse.urlencode(
            {k: v for k, v in kw.items() if v is not None},
            quote_via=urllib.parse.quote
        )

    def dispatch(self):
        import portals as _portals_mod
        _portals_mod.import_from_settings()

        action = self._params.get('action', 'root')
        debug('dispatch: {}'.format(action))

        R = {
            'root'               : self._root,
            'portal_manager'     : self._portal_manager,
            'portal_home'        : self._portal_home,
            'live_groups'        : self._live_groups,
            'm3u_movies'         : self._m3u_movies,
            'm3u_series'         : self._m3u_series,
            'm3u_movie_list'     : self._m3u_movie_list,
            'm3u_series_list'    : self._m3u_series_list,
            'live_channels'      : self._live_channels,
            'recent_vod'         : self._recent_vod,
            'recent_series'      : self._recent_series,
            'widget_groups'      : self._widget_groups,
            'widget_channels'    : self._widget_channels,
            'media_details'      : self._media_details,
            'trailer'            : self._trailer,
            'vod_categories'     : self._vod_categories,
            'vod_list'           : self._vod_list,
            'series_categories'  : self._series_categories,
            'series_list'        : self._series_list,
            'series_seasons'     : self._series_seasons,
            'series_episodes'    : self._series_episodes,
            'stb_live_groups'    : self._stb_live_groups,
            'stb_channels'       : self._stb_channels,
            'stb_vod_cats'       : self._stb_vod_cats,
            'stb_vod_list'       : self._stb_vod_list,
            'stb_series_cats'    : self._stb_series_cats,
            'stb_series_list'    : self._stb_series_list,
            'stb_seasons'        : self._stb_seasons,
            'stb_episodes'       : self._stb_episodes,
            'stb_catchup_list'   : self._stb_catchup_list,
            'stb_account'        : self._stb_account,
            'xtream_account'     : self._xtream_account,
            'm3u_account'        : self._m3u_account,
            'play_live'          : self._play_live,
            'play_vod'           : self._play_vod,
            'play_episode'       : self._play_episode,
            'play_catchup'       : self._play_catchup,
            'play_stb_live'      : self._play_stb_live,
            'play_stb_vod'       : self._play_stb_vod,
            'play_stb_episode'   : self._play_stb_vod,
            'play_stb_catchup'   : self._play_stb_catchup,
            'favourites'         : self._favourites,
            'search'             : self._search,
            'search_results'     : self._search_results,
            'epg_now'            : self._epg_now,
            'epg_status'         : self._epg_status,
            'epg_channel'        : self._epg_channel,
            'epg_sources'        : self._epg_sources,
            'catchup_list'       : self._catchup_list,
            'toggle_favourite'   : self._toggle_favourite,
            'refresh_portal'     : self._refresh_portal,
            'refresh_epg'        : self._refresh_epg,
            'clear_cache'        : self._do_clear_cache,
            'settings'           : self._open_settings,
            'add_portal_from_settings': self._add_portal_from_settings,
            'setup_wizard': self._setup_wizard,
            'group_settings': self._group_settings,
            'groups_manager': self._groups_manager,
            'startup_settings': self._startup_settings,
            'play_start': self._play_start,
            'play_start_direct': self._play_start_direct,
            'remote_setup': self._remote_setup,
            'remote_learn': self._remote_learn,
            'remote_diagnostics': self._remote_diagnostics,
            'service_recover': self._service_recover,
            'popup_probe': self._popup_probe,
            'autoplay_diagnostic_mode': self._autoplay_diagnostic_mode,
        }
        from app_routes import ACTIONS
        R.update({name:self._app_route for name in ACTIONS})
        if action == 'root' and not _portals_mod.load_all():
            from setup_wizard import setup
            created = setup()
            if created:
                # The same request renders the new portal home directly.
                self._params['pid'] = created['id']
                self._portal_home()
                return
        R.get(action, self._root)()


    def _portal_plot(self, p: dict, extra: str = '', cached_only=False) -> str:
        import datetime as _dt2
        ptype = p.get('type', 'm3u')
        type_map = {'m3u': 'M3U Playlist', 'xtream': 'Xtream Codes', 'stb': 'STB / Stalker Portal'}
        lines = [f'[B]{p.get("name", "?")}[/B]  [{type_map.get(ptype, ptype.upper())}]', '']

        if ptype == 'm3u':
            if p.get('m3u_url'):
                lines.append('[B]URL:[/B]  [gespeichert]')
            if p.get('epg_url'):
                lines.append(f'[B]EPG:[/B]  {p["epg_url"]}')
            from portals import detect_xtream
            _xc_creds = detect_xtream(p.get('m3u_url', ''))
            if _xc_creds and not cached_only:
                try:
                    from xtream import XtreamClient
                    _xc = XtreamClient(_xc_creds['xc_host'], _xc_creds['xc_user'], _xc_creds['xc_pass'])
                    _ui = _xc.get_user_info()
                    _si = _xc.get_server_info()
                    if _ui:
                        lines.append('')
                        lines.append('[B]── Account-Info ──[/B]')
                        _status = _ui.get('status', '?')
                        _auth   = _ui.get('auth', 0)
                        lines.append(f'[B]Status:[/B]  {_status}  |  Auth: {"✔" if _auth else "✘"}')
                        if _ui.get('exp_date'):
                            try:
                                _exp = _dt2.datetime.fromtimestamp(int(_ui['exp_date']))
                                _days_left = (_exp - _dt2.datetime.now()).days
                                lines.append(f'[B]Läuft ab:[/B]  {_exp.strftime("%d.%m.%Y")}  ({_days_left} Tage)')
                            except Exception:
                                lines.append(f'[B]Läuft ab:[/B]  {_ui["exp_date"]}')
                        if _ui.get('max_connections'):
                            lines.append(f'[B]Max. Verbindungen:[/B]  {_ui["max_connections"]}')
                        if _ui.get('active_cons') is not None:
                            lines.append(f'[B]Aktive Verbindungen:[/B]  {_ui["active_cons"]}')
                        if _ui.get('is_trial') in ('1', 1, True):
                            lines.append('[B]Trial-Account[/B]')
                        if _ui.get('allowed_output_formats'):
                            lines.append(f'[B]Formate:[/B]  {", ".join(_ui["allowed_output_formats"])}')
                    if _si:
                        lines.append('')
                        lines.append('[B]── Server-Info ──[/B]')
                        if _si.get('timezone'):
                            lines.append(f'[B]Zeitzone:[/B]  {_si["timezone"]}')
                        if _si.get('server_protocol'):
                            lines.append(f'[B]Protokoll:[/B]  {_si["server_protocol"]}')
                        if _si.get('https_port'):
                            lines.append(f'[B]HTTPS-Port:[/B]  {_si["https_port"]}')
                        if _si.get('rtmp_port'):
                            lines.append(f'[B]RTMP-Port:[/B]  {_si["rtmp_port"]}')
                except Exception as e:
                    lines.append(f'[I](Account-Info nicht verfügbar: {e})[/I]')

        elif ptype == 'xtream':
            host = p.get('xc_host', '')
            user = p.get('xc_user', '')
            pwd  = p.get('xc_pass', '')
            if host:
                lines.append(f'[B]Server:[/B]  {host}')
            if user:
                lines.append(f'[B]Benutzer:[/B]  {user}')
            if pwd:
                lines.append('[B]Passwort:[/B]  ••••••••')
            if p.get('epg_url'):
                lines.append(f'[B]EPG:[/B]  {p["epg_url"]}')
            if host and user and not cached_only:
                try:
                    from xtream import XtreamClient
                    xc = XtreamClient(host, user, pwd)
                    ui = xc.get_user_info()
                    si = xc.get_server_info()
                    if ui:
                        lines.append('')
                        lines.append('[B]── Account-Info ──[/B]')
                        status = ui.get('status', '?')
                        auth   = ui.get('auth', 0)
                        lines.append(f'[B]Status:[/B]  {status}  |  Auth: {"✔" if auth else "✘"}')
                        if ui.get('exp_date'):
                            try:
                                exp = _dt2.datetime.fromtimestamp(int(ui['exp_date']))
                                days_left = (exp - _dt2.datetime.now()).days
                                lines.append(f'[B]Läuft ab:[/B]  {exp.strftime("%d.%m.%Y")}  ({days_left} Tage)')
                            except Exception:
                                lines.append(f'[B]Läuft ab:[/B]  {ui["exp_date"]}')
                        if ui.get('max_connections'):
                            lines.append(f'[B]Max. Verbindungen:[/B]  {ui["max_connections"]}')
                        if ui.get('active_cons') is not None:
                            lines.append(f'[B]Aktive Verbindungen:[/B]  {ui["active_cons"]}')
                        if ui.get('is_trial') in ('1', 1, True):
                            lines.append('[B]Trial-Account[/B]')
                        if ui.get('allowed_output_formats'):
                            fmts = ', '.join(ui['allowed_output_formats'])
                            lines.append(f'[B]Formate:[/B]  {fmts}')
                    if si:
                        lines.append('')
                        lines.append('[B]── Server-Info ──[/B]')
                        if si.get('timezone'):
                            lines.append(f'[B]Zeitzone:[/B]  {si["timezone"]}')
                        if si.get('server_protocol'):
                            lines.append(f'[B]Protokoll:[/B]  {si["server_protocol"]}')
                        if si.get('https_port'):
                            lines.append(f'[B]HTTPS-Port:[/B]  {si["https_port"]}')
                        if si.get('rtmp_port'):
                            lines.append(f'[B]RTMP-Port:[/B]  {si["rtmp_port"]}')
                except Exception as e:
                    lines.append(f'[I](Account-Info nicht verfügbar: {e})[/I]')

        elif ptype == 'stb':
            if p.get('stb_url'):
                lines.append(f'[B]URL:[/B]  {p["stb_url"]}')
            if p.get('stb_mac'):
                lines.append(f'[B]MAC:[/B]  {p["stb_mac"]}')
            if p.get('epg_url'):
                lines.append(f'[B]EPG:[/B]  {p["epg_url"]}')
            if p.get('stb_url') and p.get('stb_mac') and not cached_only:
                try:
                    from stalker import client_for_portal
                    stb = client_for_portal(p)
                    info_d = stb.get_account_info() if stb else {}
                    if info_d:
                        lines.append('')
                        lines.append('[B]── Account-Info ──[/B]')
                        if info_d.get('status'):
                            lines.append(f'[B]Status:[/B]  {info_d["status"]}')
                        if info_d.get('tariff_plan_name'):
                            lines.append(f'[B]Paket:[/B]  {info_d["tariff_plan_name"]}')
                        if info_d.get('end_date'):
                            try:
                                exp = _dt2.datetime.strptime(info_d['end_date'], '%Y-%m-%d')
                                days_left = (exp - _dt2.datetime.now()).days
                                lines.append(f'[B]Läuft ab:[/B]  {exp.strftime("%d.%m.%Y")}  ({days_left} Tage)')
                            except Exception:
                                lines.append(f'[B]Läuft ab:[/B]  {info_d["end_date"]}')
                        if info_d.get('max_connections'):
                            lines.append(f'[B]Max. Verbindungen:[/B]  {info_d["max_connections"]}')
                        if info_d.get('active_con') is not None:
                            lines.append(f'[B]Aktive Verbindungen:[/B]  {info_d["active_con"]}')
                        _pv = info_d.get('phone', '')
                        if _pv:
                            import re as _rep
                            _pv_norm = _rep.sub(r'\b(am|pm)\b', lambda m: m.group().upper(), _pv.strip(), flags=_rep.IGNORECASE)
                            _matched = False
                            for _fmt in ('%B %d, %Y, %I:%M %p', '%B %d, %Y, %-I:%M %p', '%B %d, %Y',
                                         '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d.%m.%Y'):
                                try:
                                    import datetime as _dtp
                                    _exp = _dtp.datetime.strptime(_pv_norm, _fmt)
                                    _days = (_exp - _dtp.datetime.now()).days
                                    lines.append(f'[B]Läuft ab:[/B]  {_exp.strftime("%d.%m.%Y %H:%M")}  ({_days} Tage)')
                                    _matched = True
                                    break
                                except Exception:
                                    pass
                            if not _matched:
                                lines.append(f'[B]Läuft ab:[/B]  {_pv}')
                except Exception as e:
                    lines.append(f'[I](Account-Info nicht verfügbar: {e})[/I]')

        lines.append('')
        if p.get('created'):
            try:
                c = _dt2.datetime.fromtimestamp(int(p['created'])).strftime('%d.%m.%Y %H:%M')
                lines.append(f'[B]Erstellt:[/B]  {c}')
            except Exception:
                pass
        if p.get('updated'):
            try:
                u = _dt2.datetime.fromtimestamp(int(p['updated'])).strftime('%d.%m.%Y %H:%M')
                lines.append(f'[B]Zuletzt aktualisiert:[/B]  {u}')
            except Exception:
                pass

        if extra:
            lines += ['', extra]
        return '\n'.join(lines)

    def _root(self):
        import portals as P
        active = P.get_active()
        xbmcplugin.setPluginCategory(self._handle, _L(32000))
        xbmcplugin.setContent(self._handle, '')

        if not active:
            self._add_dir('[+] Einrichtungsassistent starten',
                          self.url(action='setup_wizard'),
                          icon=_ICON_SETTINGS)
            self._add_dir(_L(32060),
                          self.url(action='portal_manager'),
                          icon=_ICON_SETTINGS,
                          plot='Kein Portal konfiguriert. Hier ein neues Portal hinzufügen.')
            self._add_dir(_L(32007), self.url(action='settings'),
                          icon=_ICON_SETTINGS,
                          plot='Addon-Einstellungen öffnen.')
            xbmcplugin.endOfDirectory(self._handle)
            return

        from home_menu import active_portal
        portal = active_portal(active, self._params.get('pid',''))
        self._show_portal_home(portal)
        self._maybe_autoplay_start(portal)

    def _maybe_autoplay_start(self, portal):
        """Start the configured channel once on app entry, not on every refresh.

        The portal home is still built as the navigation fallback. A short
        cooldown protects against overlapping Kodi directory refreshes.
        """
        # Fail-safe for Android remote diagnosis: the existing per-portal
        # autoplay preference is preserved, but 0.1.16 pauses execution by
        # default. Otherwise entering a single-portal Kodi plugin always
        # starts Live TV before the modal popup can be opened.
        if setting_bool('autoplay_diagnostics_safe', True):
            xbmcgui.Window(10000).setProperty(
                'XtreamMate.AutoplayDiagnosticState',
                'PAUSIERT – XCMate Popup-Test ohne Live-TV erreichbar')
            return
        if (portal.get('type') != 'xtream' or not portal.get('autoplay_start')
                or not portal.get('start_stream_id') or xbmc.Player().isPlayingVideo()):
            return
        import time
        marker = xbmcgui.Window(10000)
        previous = marker.getProperty('XtreamMate.LastAutoplay')
        try:
            portal_id, timestamp = previous.rsplit(':', 1)
            if portal_id == str(portal['id']) and time.time()-float(timestamp) < 30:
                return
        except (ValueError, TypeError):
            pass
        marker.setProperty('XtreamMate.LastAutoplay',
                           '{}:{}'.format(portal['id'], time.time()))
        # A RunPlugin request is not a playable-item resolution. Its handler
        # must call xbmc.Player().play(), unlike the menu item's setResolvedUrl.
        xbmc.executebuiltin('RunPlugin({})'.format(
            self.url(action='play_start_direct', pid=portal['id'])))

    def _portal_home(self):
        import portals as P
        pid = self._params.get('pid', '')
        p   = P.get_by_id(pid)
        if not p:
            notify(_L(32000), _L(32050))
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        self._show_portal_home(p)

    def _show_portal_home(self, p: dict):
        from home_menu import show
        show(self,p)

    def _app_route(self):
        from app_routes import dispatch
        dispatch(self)

    def _legacy_portal_home(self, p: dict):
        ptype = p.get('type', 'm3u')
        xbmcplugin.setPluginCategory(self._handle, p['name'])
        xbmcplugin.setContent(self._handle, '')
        pid = p['id']

        _base_plot = self._portal_plot(p, cached_only=True)

        def _pp(extra=''):
            return (_base_plot + '\n' + extra) if extra else _base_plot

        if ptype == 'xtream':
            # First entry must be available BEFORE any manually launched
            # channel and independently of the Kodi Player/LiveSession.
            self._add_dir('▶ XCMate Popup- und Fernbedienungstest (OHNE TV)',
                          self.url(action='popup_probe'), icon=_ICON_SETTINGS,
                          plot='Öffnet ein fokussierbares Kodi-Testfenster '
                               'ohne den Startsender zu laden.')
            paused = setting_bool('autoplay_diagnostics_safe', True)
            self._add_dir(
                ('Startsender-Autostart PAUSIERT – wieder freigeben'
                 if paused else
                 'Startsender-Autostart AKTIV – für Diagnose pausieren'),
                self.url(action='autoplay_diagnostic_mode'),
                icon=_ICON_SETTINGS,
                plot='Betrifft nur den automatischen Start beim Öffnen '
                     'von XCMate. Startsender, Portale und EPG bleiben '
                     'gespeichert. Manuelles Fernsehen funktioniert weiter.')
        if p.get('include_live', True):
            self._add_dir(_L(32001),
                          self.url(action='live_groups', pid=pid),
                          icon=_ICON_TV,
                          plot=_pp('Live-TV Sendergruppen anzeigen.'))
        if ptype == 'xtream':
            self._add_dir('Startsender und Start-Sendergruppe einstellen',
                          self.url(action='startup_settings', pid=pid),
                          icon=_ICON_SETTINGS)
            if p.get('start_stream_id'):
                self._add_dir('▶ Startsender abspielen',
                              self.url(action='play_start', pid=pid), icon=_ICON_TV, is_folder=False)
            self._add_dir('TV-Fernbedienung aktivieren / deaktivieren',
                          self.url(action='remote_setup'), icon=_ICON_SETTINGS)
            self._add_dir('Fernbedienungstasten anlernen (Android)',
                          self.url(action='remote_learn'), icon=_ICON_SETTINGS,
                          plot='Tasten direkt auf der Android-Fernbedienung erfassen '
                               'und einzelnen XCMate-Funktionen zuweisen.')
            self._add_dir('TV-Fernbedienung: Diagnose',
                          self.url(action='remote_diagnostics'), icon=_ICON_SETTINGS)
            self._add_dir('XCMate-Hintergrunddienst prüfen / manuell starten',
                          self.url(action='service_recover'), icon=_ICON_SETTINGS,
                          plot='Auch ohne laufenden Stream: Dienst-Lebenszeichen prüfen '
                               'und bei Bedarf einen einmaligen Start anfordern.')
            self._add_dir('BINGIE MOD Widgets – aktive Sendergruppen',
                          self.url(action='widget_groups', pid=pid),
                          icon=_ICON_TV,
                          plot='Sendergruppen als Widget auf die BINGIE-MOD-Startseite legen. '
                               'Senderlogos sowie Jetzt/Danach-Daten aus dem lokalen EPG.')
            self._add_dir('Gruppen verwalten: Live-TV, Filme und Serien',
                          self.url(action='groups_manager', pid=pid),
                          icon=_ICON_SETTINGS,
                          plot='Gruppen einzeln aktivieren/deaktivieren; alle oder neue Gruppen auswählen.')
        if ptype == 'xtream':
            if p.get('include_vod', True):
                self._add_dir('Neueste Filme',
                              self.url(action='recent_vod', pid=pid),
                              icon=_ICON_VOD,
                              plot=_pp('Zuletzt zum Xtream-Katalog hinzugefügte Filme.'))
            if p.get('include_series', True):
                self._add_dir('Neueste Serien',
                              self.url(action='recent_series', pid=pid),
                              icon=_ICON_SERIES,
                              plot=_pp('Zuletzt zum Xtream-Katalog hinzugefügte Serien.'))
        if ptype in ('xtream', 'stb'):
            if p.get('include_vod', True):
                self._add_dir(_L(32002),
                              self.url(action='vod_categories', pid=pid),
                              icon=_ICON_VOD,
                              plot=_pp('Filme und VOD-Inhalte durchsuchen.'))
            if p.get('include_series', True):
                self._add_dir(_L(32003),
                              self.url(action='series_categories', pid=pid),
                              icon=_ICON_SERIES,
                              plot=_pp('Serien und Staffeln durchsuchen.'))
        elif ptype == 'm3u':
            self._add_dir(_L(32002),
                          self.url(action='m3u_movies', pid=pid),
                          icon=_ICON_VOD,
                          plot=_pp('Filme aus der M3U-Playlist anzeigen.'))
            self._add_dir(_L(32003),
                          self.url(action='m3u_series', pid=pid),
                          icon=_ICON_SERIES,
                          plot=_pp('Serien aus der M3U-Playlist anzeigen.'))
        if ptype == 'stb':
            self._add_dir(_L(32013),
                          self.url(action='stb_account', pid=pid),
                          icon=_ICON_SETTINGS,
                          plot=_pp('STB-Kontoinformationen anzeigen.'))
        elif ptype == 'xtream':
            self._add_dir(_L(32013),
                          self.url(action='xtream_account', pid=pid),
                          icon=_ICON_SETTINGS,
                          plot=_pp('Xtream-Kontoinformationen anzeigen.'))
        elif ptype == 'm3u':
            self._add_dir(_L(32013),
                          self.url(action='m3u_account', pid=pid),
                          icon=_ICON_SETTINGS,
                          plot=_pp('M3U-Kontoinformationen anzeigen.'))
        self._add_dir(_L(32004),
                      self.url(action='favourites', pid=pid),
                      icon=_ICON_FAV,
                      plot=_pp('Gespeicherte Favoriten dieses Portals anzeigen.'))
        self._add_dir(_L(32005),
                      self.url(action='search', pid=pid),
                      icon=_ICON_SEARCH,
                      plot=_pp('Sender, Filme und Serien in diesem Portal suchen.'))
        self._add_dir(_L(32006),
                      self.url(action='epg_now', pid=pid),
                      icon=_ICON_EPG,
                      plot=_pp('Aktuelle Sendungen im Programmführer anzeigen.'))
        self._add_dir('EPG verwalten – XMLTV-Quellen & Senderzuordnung',
                      self.url(action='epg_sources', pid=pid),
                      icon=_ICON_EPG,
                      plot='Eigene oder externe XMLTV-Dateien, mehrere URLs, '
                           'Prioritäten und Sender-Zuordnungen verwalten.')
        self._add_dir('EPG-Status & Vorschau', self.url(action='epg_status',pid=pid),
                      icon=_ICON_EPG, plot='Quellen, Importfehler, Zuordnung und echte Programme aus dem lokalen Cache.')
        self._add_dir(_L(32008),
                      self.url(action='refresh_portal', pid=pid),
                      icon=_ICON_SETTINGS,
                      plot=_pp('Playlist und EPG-Daten neu laden.'))
        self._add_dir('[+] Weitere TV-Liste einrichten',
                      self.url(action='setup_wizard'),
                      icon=_ICON_SETTINGS,
                      plot='Neuen Xtream-, M3U- oder Stalker-Zugang hinzufügen.')
        self._add_dir(_L(32012),
                      self.url(action='portal_manager'),
                      icon=_ICON_SETTINGS,
                      plot='Portale verwalten, hinzufügen oder bearbeiten.')
        xbmcplugin.endOfDirectory(self._handle)


    def _setup_wizard(self):
        from setup_wizard import setup
        portal = setup()
        xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
        if portal:
            # Replace the setup container with the newly created portal home.
            xbmc.executebuiltin('Container.Update({},replace)'.format(
                self.url(action='portal_home', pid=portal['id'])))
        else:
            xbmc.executebuiltin('Container.Refresh')

    def _popup_probe(self):
        """Safe direct action: never resolve, play or launch the start channel."""
        marker = xbmcgui.Window(10000)
        marker.setProperty('XtreamMate.AutoplayDiagnosticState',
                           'Popup-Test angefordert – Startsender nicht starten')
        from popup_probe import run_popup_test
        run_popup_test()

    def _autoplay_diagnostic_mode(self):
        """Toggle only the add-on-wide safety switch, not portal settings."""
        paused = setting_bool('autoplay_diagnostics_safe', True)
        next_state = not paused
        if paused:
            if not xbmcgui.Dialog().yesno(
                    'XCMate – Startsender',
                    'Automatischen Senderstart wieder erlauben?\n'
                    'Wenn die Fernbedienung noch blockiert, kann das '
                    'den Popup-Test erneut verhindern.'):
                return
        ADDON.setSetting('autoplay_diagnostics_safe',
                         'true' if next_state else 'false')
        xbmcgui.Window(10000).setProperty(
            'XtreamMate.AutoplayDiagnosticState',
            'PAUSIERT' if next_state else 'FREIGEGEBEN')
        xbmcgui.Dialog().ok(
            'XCMate – Startsender',
            ('Automatischer Start ist für den Popup-Test pausiert.\n'
             'Manuelles Abspielen bleibt möglich.'
             if next_state else
             'Autostart freigegeben. Beim nächsten Öffnen von XCMate '
             'wird die gespeicherte Startsender-Einstellung verwendet.'))

    def _remote_diagnostics(self):
        from service_health import inspect
        from remote_control import is_enabled, SESSION_KEY
        from live_overlay import session_from_property
        marker = xbmcgui.Window(10000)
        session = session_from_property(marker.getProperty(SESSION_KEY))
        health = inspect(marker)
        last_seen = ('kein Lebenszeichen' if health['age'] is None
                     else '{:.1f} Sekunden'.format(health['age']))
        rows = [
            'Installierte XCMate-Version: '+ADDON.getAddonInfo('version'),
            '=== Hintergrunddienst (OHNE Stream prüfbar) ===',
            'Dienststatus: ' + health['state'],
            'Letztes Lebenszeichen: ' + last_seen,
            'Dienstschleifen: ' + health['loops'],
            'Dienstphase: ' + health['phase'],
            'Letzter Dienstfehler: ' + health['error'],
            'Letzte Live-Beobachtung: ' + health['live'],
            'Live-Sitzungswiederherstellung: ' +
            (marker.getProperty('XtreamMate.SessionRecovery') or 'noch keine Prüfung'),
            'Letzte TV-Einblendung: ' + health['overlay'],
            'Letzte Diensteingabe: ' + health['input'],
            '',
            'Autostart-Diagnosemodus: ' +
            ('PAUSIERT' if setting_bool('autoplay_diagnostics_safe', True)
             else 'FREIGEGEBEN'),
            '=== Eigener XCMate-Popup-Test ===',
            'Popup-Darstellungsweg: ' +
            (marker.getProperty('XtreamMate.PopupProbe.Renderer') or 'nicht geprüft'),
            'Popup-Status: ' +
            (marker.getProperty('XtreamMate.PopupProbe.Status') or 'noch nicht geöffnet'),
            'Popup-Ereignisse: ' +
            (marker.getProperty('XtreamMate.PopupProbe.KeyCount') or '0'),
            'Popup-Letzte Taste: ' +
            (marker.getProperty('XtreamMate.PopupProbe.LastKey') or 'noch keine'),
            'Popup-Fokus: ' +
            (marker.getProperty('XtreamMate.PopupProbe.Focus') or 'noch nicht geprüft'),
            'Auto-TV-Popup: ' +
            (marker.getProperty('XtreamMate.AutoPopupStatus') or 'nicht gestartet'),
            '',
            '=== Aktuelle Player-/Tastenlage ===',
            'Kodi-Tastenbelegung: ' + ('AKTIV' if is_enabled() else 'INAKTIV'),
            'XCMate-Stream erkannt: ' + ('JA' if session else 'NEIN'),
            'Video läuft: ' + ('JA' if xbmc.Player().isPlayingVideo() else 'NEIN'),
            'TV-Einblendung: ' + (marker.getProperty('XtreamMate.OverlayStatus') or 'nicht gestartet'),
            'Tastenübernahme: ' + (marker.getProperty('XtreamMate.KeymapStatus') or 'nicht überprüft'),
            'Eingabepfad: ' + (marker.getProperty('XtreamMate.InputMode') or 'nicht aktiv'),
            'Native Tastenereignisse: ' + (marker.getProperty('XtreamMate.NativeActionCount') or '0'),
            'Startsender: ' + (marker.getProperty('XtreamMate.StartupStatus') or 'noch nicht gestartet'),
            'Letzte Kodi-Taste: ' + (marker.getProperty('XtreamMate.LastRemoteKey') or 'noch keine'),
            'Zuletzt verarbeitet: ' + (marker.getProperty('XtreamMate.LastHandledKey') or 'noch keine'),
        ]
        from live_diagnostics import report
        rows.extend(['']+report())
        if not is_enabled():
            rows.append('')
            rows.append('Globale Keymap bleibt aus, sofern nicht ausdrücklich aktiviert.')
        else:
            rows.append('')
            rows.append('Test: Nach dem Stream diese Diagnose erneut öffnen;')
            rows.append('die letzte Live-Beobachtung bleibt erhalten.')
        rows.append('')
        rows.append('Bei NICHT BESTÄTIGT / KEIN AKTUELLES LEBENSZEICHEN:')
        rows.append('XCMate-Hintergrunddienst prüfen / manuell starten wählen.')
        xbmcgui.Dialog().textviewer('XCMate – Fernbedienungsdiagnose', '\n'.join(rows))

    def _service_recover(self):
        """Test/start the existing add-on service without needing live TV."""
        from service_health import inspect, request_manual_start
        marker = xbmcgui.Window(10000)
        health = inspect(marker)
        if health['alive']:
            xbmcgui.Dialog().ok('XCMate – Hintergrunddienst',
                                'Dienststatus: LÄUFT.\n'
                                'Dienstschleifen: {}\n'
                                'Letzte Live-Beobachtung: {}\n'
                                'Letzter Dienstfehler: {}'.format(
                                    health['loops'], health['live'], health['error']))
            return
        if not xbmcgui.Dialog().yesno(
                'XCMate – Hintergrunddienst',
                'Dienststatus: {}.\n'
                'Einmaligen manuellen Start anfordern?\n'
                'Das ändert keine Portale, Tasten oder EPG-Daten.'.format(health['state'])):
            return
        outcome = request_manual_start(marker)
        xbmcgui.Dialog().ok('XCMate – Hintergrunddienst',
                            outcome + '\n\n'
                            'Danach TV-Fernbedienung: Diagnose erneut öffnen.')

    def _remote_learn(self):
        from remote_profiles import configure
        configure()

    def _remote_setup(self):
        from remote_control import configure
        configure()
        xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)

    def _startup_settings(self):
        import portals
        from startup_preferences import configure_startup
        p=self._portal()
        if not p:
            candidates=[x for x in portals.get_active() if x.get('type')=='xtream']
            if not candidates:
                xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
                return
            idx=xbmcgui.Dialog().select('XCMate – Portal', [x['name'] for x in candidates])
            if idx<0:
                xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
                return
            p=candidates[idx]
        configure_startup(p)
        xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
        xbmc.executebuiltin('Container.Refresh')

    def _startup_playable(self):
        """Resolve only the configured stream, never refresh portal catalogs here.

        Return a Kodi ListItem with the provider URL in its path. The caller
        decides whether Kodi expects a resolved playable item or a direct play.
        """
        from portals import get_by_id
        p = get_by_id(self._params.get('pid', ''))
        if not p or p.get('type') != 'xtream' or not p.get('start_stream_id'):
            notify('XCMate', 'Bitte zuerst eine Startgruppe und einen Startsender wählen.')
            return None
        from xtream import XtreamClient
        from player import build_playable_item
        sid = str(p['start_stream_id'])
        xc = XtreamClient(p['xc_host'], p['xc_user'], p['xc_pass'])
        cached = xc.get_cached_catalog('get_live_streams') or []
        channel = next((c for c in cached if str(c.get('stream_id')) == sid), {})
        url = xc.live_stream_url(sid, 'ts')
        if not url:
            notify('XCMate', 'Die Startsender-Adresse konnte nicht ermittelt werden.')
            return None
        title = channel.get('name') or 'Startsender'
        item = build_playable_item(url, title=title,
                                   logo=channel.get('stream_icon', ''))
        return p, sid, title, item

    def _play_start(self):
        """Kodi playable menu entry: resolve, never open an empty directory.

        A ListItem with IsPlayable=true invokes Kodi's playback handshake.
        Calling Player.play() here leaves the pending plugin URL unresolved.
        """
        prepared = self._startup_playable()
        if prepared is None:
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return
        p, sid, title, item = prepared
        from live_overlay import announce
        try:
            session=announce(p['id'], sid, title)
            from live_recovery import tag_live_item
            tag_live_item(item,session)
            xbmcgui.Window(10000).setProperty(
                'XtreamMate.StartupStatus', 'Kodi-Auflösung: ' + title[:64])
            xbmcplugin.setResolvedUrl(self._handle, True, item)
        except Exception as exc:
            error('XCMate startup resolver failed: {}'.format(type(exc).__name__))
            notify('XCMate', 'Startsender konnte nicht gestartet werden.')
            xbmcgui.Window(10000).setProperty(
                'XtreamMate.StartupStatus', 'Fehler: ' + type(exc).__name__)
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())

    def _play_start_direct(self):
        """RunPlugin-only autoplay: direct playback without setResolvedUrl."""
        prepared = self._startup_playable()
        if prepared is None:
            return
        p, sid, title, item = prepared
        from live_overlay import announce
        try:
            session=announce(p['id'], sid, title)
            from live_recovery import tag_live_item
            tag_live_item(item,session)
            xbmcgui.Window(10000).setProperty(
                'XtreamMate.StartupStatus', 'Autoplay-Direktstart: ' + title[:64])
            xbmc.Player().play(item.getPath(), item)
        except Exception as exc:
            error('XCMate direct startup failed: {}'.format(type(exc).__name__))
            notify('XCMate', 'Startsender konnte nicht gestartet werden.')
            xbmcgui.Window(10000).setProperty(
                'XtreamMate.StartupStatus', 'Fehler: ' + type(exc).__name__)

    def _groups_manager(self):
        import portals
        pid = self._params.get('pid', '')
        p = portals.get_by_id(pid) if pid else None
        if not p:
            options = [item for item in portals.load_all() if item.get('type') == 'xtream']
            if not options:
                xbmcgui.Dialog().ok('XCMate', 'Zuerst einen Xtream-Codes-Zugang einrichten.')
                xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
                return
            idx = xbmcgui.Dialog().select('XCMate – Portal auswählen',
                                         [item['name'] for item in options])
            if idx < 0:
                xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
                return
            p = options[idx]
        from group_selection import manage_groups
        manage_groups(p)
        xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
        xbmc.executebuiltin('Container.Refresh')

    def _group_settings(self):
        p = self._portal()
        if not p or p.get('type') != 'xtream':
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        from group_selection import choose_groups
        choose_groups(p, self._params.get('kind', 'live'))
        xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
        xbmc.executebuiltin('Container.Refresh')

    def _portal_manager(self):
        import portal_manager
        created = portal_manager.show()
        xbmcplugin.endOfDirectory(self._handle, updateListing=True, cacheToDisc=False)
        if created:
            xbmc.executebuiltin('Container.Update({},replace)'.format(
                self.url(action='portal_home', pid=created['id'])))
        else:
            xbmc.executebuiltin('Container.Refresh')



    def _m3u_section_groups(self, section: str):
        from iptv import load_m3u, group_channels, split_m3u_sections
        p = self._portal()
        if not p:
            return
        pid      = p['id']
        m3u_url  = p.get('m3u_url', '').strip()
        if not m3u_url:
            notify(_L(32000), _L(32049))
            xbmcplugin.endOfDirectory(self._handle, False)
            return

        all_ch   = load_m3u(m3u_url, portal_id=pid)
        sections = split_m3u_sections(all_ch)
        channels = sections.get(section, [])

        if not channels:
            notify(_L(32000), _L(32055, section.title()))
            xbmcplugin.endOfDirectory(self._handle, False)
            return

        label   = _L(32002) if section == 'movies' else _L(32003)
        content = 'movies' if section == 'movies' else 'tvshows'
        xbmcplugin.setPluginCategory(self._handle, f'{p["name"]} – {label}')
        xbmcplugin.setContent(self._handle, content)

        groups  = group_channels(channels)
        g_list  = sorted(groups) if setting_int('sort_groups') == 1 else list(groups)
        g_list  = apply_lang_sort(g_list, name_fn=lambda g: g, group_fn=lambda g: g)

        action = 'm3u_movie_list' if section == 'movies' else 'm3u_series_list'
        for gname in g_list:
            count = len(groups[gname])
            self._add_dir(f'{gname}  [{count}]',
                          self.url(action=action, pid=pid, group=gname),
                          icon=_ICON_VOD if section == 'movies'
                               else _ICON_SERIES)

        xbmcplugin.endOfDirectory(self._handle, succeeded=True, updateListing=False, cacheToDisc=False)

    def _m3u_movies(self):
        self._m3u_section_groups('movies')

    def _m3u_series(self):
        self._m3u_section_groups('series')

    def _m3u_movie_list(self):
        from iptv import load_m3u, split_m3u_sections
        from player import vod_list_item
        p = self._portal()
        if not p:
            return
        pid     = p['id']
        group   = self._params.get('group', '')
        all_ch  = load_m3u(p.get('m3u_url', ''), portal_id=pid)
        movies  = split_m3u_sections(all_ch).get('movies', [])
        items   = [c for c in movies if c.group == group] if group else movies
        items   = apply_lang_sort(items)

        xbmcplugin.setPluginCategory(self._handle, group or _L(32002))
        xbmcplugin.setContent(self._handle, 'movies')

        for ch in items:
            li = xbmcgui.ListItem(ch.name)
            li.setArt({'thumb': ch.logo, 'icon': ch.logo})
            li.setInfo('video', {'title': ch.name, 'mediatype': 'movie'})
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self._handle, ch.url, li, False)

        xbmcplugin.endOfDirectory(self._handle)

    def _m3u_series_list(self):
        from iptv import load_m3u, split_m3u_sections
        p = self._portal()
        if not p:
            return
        pid    = p['id']
        group  = self._params.get('group', '')
        all_ch = load_m3u(p.get('m3u_url', ''), portal_id=pid)
        series = split_m3u_sections(all_ch).get('series', [])
        items  = [c for c in series if c.group == group] if group else series
        items  = apply_lang_sort(items)

        xbmcplugin.setPluginCategory(self._handle, group or _L(32003))
        xbmcplugin.setContent(self._handle, 'tvshows')

        for ch in items:
            li = xbmcgui.ListItem(ch.name)
            li.setArt({'thumb': ch.logo, 'icon': ch.logo})
            li.setInfo('video', {'title': ch.name, 'mediatype': 'episode'})
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self._handle, ch.url, li, False)

        xbmcplugin.endOfDirectory(self._handle)


    def _live_groups(self):
        p = self._portal()
        if not p:
            return
        if p['type'] == 'stb':
            self._stb_live_groups()
            return
        channels = self._load_channels(p)
        if p.get('type') == 'xtream':
            from group_selection import filter_channels
            channels = filter_channels(channels, p['id'])
        if not channels:
            ptype = p.get('type', 'm3u')
            from xtream import XtreamClient
            xc = self._xc(p) if ptype == 'xtream' else None
            if (xc and (xc.get_cached_catalog('get_live_categories') is None
                        or xc.get_cached_catalog('get_live_streams') is None)):
                self._add_dir('Senderliste wird im Hintergrund geladen – erneut öffnen',
                              self.url(action='live_groups', pid=p['id']),
                              icon=_ICON_TV)
                xbmcplugin.endOfDirectory(self._handle)
                return
            if ptype == 'm3u' and not p.get('m3u_url', '').strip():
                msg = 'M3U URL is empty. Open Portal Manager and set the URL.'
            elif ptype == 'xtream' and not p.get('xc_host', '').strip():
                msg = 'Xtream host not set. Open Portal Manager.'
            else:
                msg = f'No channels found for "{p["name"]}". Check URL/credentials.'
            if ptype == 'xtream':
                from group_selection import load
                if load(p['id'], 'live') == set():
                    msg = 'Alle Sendergruppen sind deaktiviert. Bitte Gruppen verwalten.'
            notify(_L(32000), msg, duration=5000)
            xbmcplugin.endOfDirectory(self._handle, False)
            return

        from iptv import group_channels
        groups = group_channels(channels)
        g_list = sorted(groups) if setting_int('sort_groups') == 1 else list(groups)
        g_list = apply_lang_sort(g_list,
                                 name_fn=lambda g: g,
                                 group_fn=lambda g: g)

        if len(g_list) == 1:
            self._params['group'] = g_list[0]
            self._live_channels()
            return

        xbmcplugin.setContent(self._handle, 'videos')
        if p.get('type') == 'xtream':
            self._add_dir('[B]Alle Sender aktivierter Gruppen[/B]',
                          self.url(action='live_channels', pid=p['id']),
                          icon=_ICON_TV)
        for gname in g_list:
            count = len(groups[gname])
            self._add_dir(f'{gname}  ({count})',
                          self.url(action='live_channels',
                                   pid=p['id'], group=gname),
                          icon=_ICON_TV)
        xbmcplugin.endOfDirectory(self._handle, succeeded=True, updateListing=False, cacheToDisc=False)

    def _live_channels(self):
        p = self._portal()
        if not p:
            return
        group   = self._params.get('group', '')
        page    = int(self._params.get('page', 0))
        psize   = setting_int('items_per_page', 50)
        all_ch  = self._load_channels(p)
        if p.get('type') == 'xtream':
            from group_selection import filter_channels
            all_ch = filter_channels(all_ch, p['id'])
        ch_list = [c for c in all_ch if c.group == group] if group else all_ch

        s = setting_int('sort_channels')
        if s == 1:
            ch_list.sort(key=lambda c: c.name.lower())
        elif s == 2:
            ch_list.sort(key=lambda c: c.name.lower(), reverse=True)
        ch_list = apply_lang_sort(ch_list)

        total   = len(ch_list)
        chunk   = ch_list[page * psize:(page + 1) * psize]

        xbmcplugin.setContent(self._handle, 'videos')
        label = group or _L(32015)
        if total > psize:
            label = f'{label}  ({page * psize + 1}-{min((page + 1) * psize, total)} / {total})'
        xbmcplugin.setPluginCategory(self._handle, label)

        ptype   = p.get('type', 'm3u')
        from player import channel_list_item
        from epg import load_cache
        from epg_views import resolve_guide, prefetch_short_guides
        guide = load_cache(p['id'])
        xc_epg = self._xc(p) if ptype == 'xtream' else None
        manual_epg = {}
        if xc_epg:
            from epg_sources import configuration
            manual_epg = configuration(p['id'])['mappings']
            prefetch_short_guides(p, chunk,view_path=self.url(action='live_channels',
                                  pid=p['id'],group=group,page=page))
        now = time.time()
        matched=now_count=next_count=0
        for ch in chunk:
            li = channel_list_item(ch)
            epg = resolve_guide(guide, ch.tvg_id, ch.extra.get('stream_id',''),
                                now, xc_epg, manual_epg)
            now_count+=bool(epg['now'])
            next_count+=bool(epg['next'])
            matched+=bool(epg['now'] or epg['next'])
            from epg_views import programme_plot
            li.setInfo('video', {'title':ch.name, 'plot':programme_plot(epg),
                                 'mediatype':'video'})
            if epg['now'] or epg['next']:
                li.setLabel('{}  |  Jetzt: {}  |  Danach: {}'.format(
                    ch.name, '{}-{} {}'.format(epg['now_time'],epg['now_end_time'],epg['now'])
                    if epg['now'] else 'Keine EPG-Daten',epg['next'] or '–'))

            if ptype == 'stb':
                play_url  = self.url(action='play_stb_live', pid=p['id'],
                                     cmd=ch.url, name=ch.name, logo=ch.logo)
                cu_action = 'stb_catchup_list'
            else:
                play_url  = self.url(action='play_live', pid=p['id'],
                                     sid=ch.extra.get('stream_id', ''),
                                     url=ch.url, name=ch.name, logo=ch.logo)
                cu_action = 'catchup_list'

            sid = str(ch.extra.get('stream_id', ''))
            epg_link_id = manual_epg.get(sid) or ch.tvg_id or sid
            cm = [
                (('Remove from Favourites' if is_favourite(ch.url)
                  else 'Add to Favourites'),
                 f'RunPlugin({self.url(action="toggle_favourite", url=ch.url, name=ch.name, logo=ch.logo, group=ch.group)})'),
                ('EPG',
                 f'Container.Update({self.url(action="epg_channel", pid=p["id"], sid=sid, tvg_id=epg_link_id, name=ch.name)})'),
                ('EPG-/Live-Diagnose',f'RunPlugin({self.url(action="remote_diagnostics")})'),
            ]
            if ch.catchup or ch.catchup_days:
                cm.append((_L(32009),
                            f'Container.Update({self.url(action=cu_action, pid=p["id"], url=ch.url, name=ch.name, tvg_id=ch.tvg_id)})'))
            li.addContextMenuItems(cm)
            xbmcplugin.addDirectoryItem(self._handle, play_url, li, False)

    
        if page > 0:
            self._add_dir(_L(32019, page),
                          self.url(action='live_channels', pid=p['id'],
                                   group=group, page=page - 1),
                          icon=_ICON_SETTINGS)
        if (page + 1) * psize < total:
            remaining = total - (page + 1) * psize
            self._add_dir(_L(32018, remaining),
                          self.url(action='live_channels', pid=p['id'],
                                   group=group, page=page + 1),
                          icon=_ICON_SETTINGS)

        from live_diagnostics import record
        record('epg_list','RENDERED',visible=len(chunk),matched=matched,
               now_count=now_count,next_count=next_count,channels=len(guide),
               programmes=sum(len(v) for v in guide.values() if isinstance(v,list)))
        xbmcplugin.addSortMethod(self._handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self._handle, succeeded=True, updateListing=False, cacheToDisc=False)


    def _add_media_context(self, li, item, kind, sid, pid):
        from metadata_views import trailer_id
        menu = [('Beschreibung und Details',
                 'RunPlugin({})'.format(self.url(action='media_details',pid=pid,
                                                 kind=kind,sid=sid)))]
        vid = trailer_id(item)
        if vid:
            menu.append(('YouTube-Trailer abspielen',
                         'RunPlugin({})'.format(self.url(action='trailer',vid=vid))))
        li.addContextMenuItems(menu)

    def _widget_groups(self):
        """Kodi skin-widget destinations; each folder path yields playable cards."""
        p = self._portal()
        if not p:
            return
        if p.get('type') != 'xtream':
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        from group_selection import enabled_ids
        xc = self._xc(p)
        groups = xc.get_cached_catalog('get_live_categories') if xc else None
        if not isinstance(groups, list):
            self._add_dir('Senderkatalog lädt im Hintergrund',
                          self.url(action='widget_groups', pid=p['id']), icon=_ICON_TV)
        else:
            allowed = enabled_ids(p['id'], 'live', groups)
            xbmcplugin.setContent(self._handle, 'files')
            for group in groups:
                cid = str(group.get('category_id') or '')
                if cid and cid in allowed:
                    self._add_dir(str(group.get('category_name') or cid),
                        self.url(action='widget_channels', pid=p['id'], cat_id=cid),
                        icon=_ICON_TV,
                        plot='Kodi/BINGIE-MOD-Widget: aktiver Sender dieser Gruppe')
        xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)

    def _widget_channels(self):
        """Widget-friendly static directory. No network calls during Kodi hover."""
        p = self._portal()
        if not p:
            return
        if p.get('type') != 'xtream' or not p.get('include_live', True):
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        from group_selection import enabled_ids
        from epg import load_cache
        from epg_views import guide_for_channel, programme_plot
        xc = self._xc(p)
        groups = xc.get_cached_catalog('get_live_categories') if xc else None
        streams = xc.get_cached_catalog('get_live_streams') if xc else None
        if not isinstance(groups, list) or not isinstance(streams, list):
            self._add_dir('Senderkatalog lädt im Hintergrund',
                          self.url(action='widget_channels', pid=p['id'],
                                   cat_id=self._params.get('cat_id','')), icon=_ICON_TV)
            xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
            return
        allowed = enabled_ids(p['id'], 'live', groups)
        cid = str(self._params.get('cat_id') or '')
        if cid not in allowed:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        names = {str(g.get('category_id')):str(g.get('category_name') or '')
                 for g in groups if isinstance(g,dict)}
        guide = load_cache(p['id'])
        now_ts = time.time()
        xbmcplugin.setContent(self._handle, 'videos')
        xbmcplugin.setPluginCategory(self._handle, 'XCMate – ' + names.get(cid,'TV'))
        for item in streams:
            if not isinstance(item, dict) or str(item.get('category_id','')) != cid:
                continue
            sid = str(item.get('stream_id') or '')
            if not sid:
                continue
            name = str(item.get('name') or 'Sender')
            logo = str(item.get('stream_icon') or '')
            epg = guide_for_channel(guide, item.get('epg_channel_id',''), sid, now_ts)
            li = xbmcgui.ListItem(name)
            img = epg.get('image') or logo
            li.setArt({'icon':logo, 'thumb':logo, 'poster':img, 'landscape':img,
                       'fanart':img or ADDON_FANART})
            li.setInfo('video', {'title':name, 'plot':programme_plot(epg),
                                 'mediatype':'video'})
            li.setProperty('IsPlayable','true')
            li.setProperty('XtreamMate.Now',epg.get('now',''))
            li.setProperty('XtreamMate.Next',epg.get('next',''))
            xbmcplugin.addDirectoryItem(self._handle,
                self.url(action='play_live', pid=p['id'],sid=sid,name=name,logo=logo),
                li,False)
        xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)

    def _media_details(self):
        """Fetch full description on user click, never while scrolling lists."""
        p = self._portal()
        if not p or p.get('type') != 'xtream':
            return
        kind = self._params.get('kind','vod')
        sid = self._params.get('sid','')
        xc = self._xc(p)
        if not sid or kind not in ('vod','series'):
            return
        from metadata_views import enrich, provider_plot, trailer_id
        details = (xc.get_vod_info(sid) if kind == 'vod' else xc.get_series_info(sid))
        item = enrich({}, details)
        plot = provider_plot(item) or 'Der Anbieter liefert keine Beschreibung.'
        vid = trailer_id(item)
        if vid:
            plot += '\n\nYouTube-Trailer-ID: ' + vid
        xbmcgui.Dialog().textviewer('XCMate – Filminfo', plot)
        if vid and xbmcgui.Dialog().yesno('XCMate', 'YouTube-Trailer abspielen?'):
            self._play_youtube_id(vid)

    @staticmethod
    def _play_youtube_id(vid):
        from metadata_views import trailer_id
        from urllib.parse import quote
        if trailer_id({'youtube_trailer':vid}) != vid:
            return
        try:
            xbmcaddon.Addon('plugin.video.youtube')
        except RuntimeError:
            xbmcgui.Dialog().ok('XCMate',
                'Bitte das offizielle Kodi-YouTube-Add-on installieren, '
                'um Trailer direkt wiederzugeben.')
            return
        xbmc.executebuiltin('PlayMedia(plugin://plugin.video.youtube/play/?video_id={})'.format(quote(vid)))

    def _trailer(self):
        self._play_youtube_id(self._params.get('vid',''))

    def _recent_vod(self):
        self._recent_media('get_vod_streams', 'vod')

    def _recent_series(self):
        self._recent_media('get_series', 'series')

    def _recent_media(self, action, kind):
        """Widget-ready Kodi directory populated from the cached Xtream index.

        Neither the home screen nor the latest view blocks on Xtream requests.
        The Kodi service warms the catalog in the background; refresh from
        the portal home is available if the IPTV provider has added new titles.
        """
        p = self._portal()
        if not p:
            return
        wanted = 'include_vod' if kind == 'vod' else 'include_series'
        if p.get('type') != 'xtream' or not p.get(wanted, True):
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        from group_selection import filter_entries
        from latest_media import first_seen, recent_entries
        from player import vod_list_item, series_list_item
        xc = self._xc(p)
        title = 'Neueste Filme' if kind == 'vod' else 'Neueste Serien'
        xbmcplugin.setPluginCategory(self._handle, '{} – {}'.format(p['name'], title))
        xbmcplugin.setContent(self._handle, 'movies' if kind == 'vod' else 'tvshows')
        all_items = xc.get_cached_catalog(action) if xc else None
        if not isinstance(all_items, list):
            self._add_dir('Katalog wird im Hintergrund geladen – später erneut öffnen',
                          self.url(action='portal_home', pid=p['id']),
                          icon=_ICON_SETTINGS,
                          plot='Beim ersten Scan muss XCMate Daten vom Anbieter laden.')
        else:
            # Cache was present before 0.1.5: initialize its discovery baseline
            # without falsely flagging all previously known items as 'new'.
            seen = first_seen(xc._cache_key(action), action, all_items)
            items = filter_entries(all_items, p['id'], kind)
            recent = recent_entries(items, action, seen, limit=50)
            for item in recent:
                if kind == 'vod':
                    sid = item.get('stream_id', '')
                    li = vod_list_item(item)
                    self._add_media_context(li, item, 'vod', sid, p['id'])
                    url = self.url(action='play_vod', pid=p['id'],
                                   stream_id=sid,
                                   ext=item.get('container_extension', 'mkv'),
                                   title=item.get('name', ''),
                                   logo=item.get('stream_icon', ''))
                    is_folder = False
                else:
                    sid = item.get('series_id', '')
                    li = series_list_item(item)
                    self._add_media_context(li, item, 'series', sid, p['id'])
                    url = self.url(action='series_seasons', pid=p['id'],
                                   series_id=sid, title=item.get('name', ''))
                    is_folder = True
                xbmcplugin.addDirectoryItem(self._handle, url, li, is_folder)
            if not recent:
                self._add_dir('Noch keine neu hinzugefügten Titel erkennbar',
                              self.url(action='portal_home', pid=p['id']),
                              icon=_ICON_SETTINGS,
                              plot='Der Anbieter liefert eventuell kein Hinzufügedatum. '
                                   'XCMate erkennt künftig beim Aktualisieren neue IDs.')
        xbmcplugin.addSortMethod(self._handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)

    def _vod_categories(self):
        p = self._portal()
        if not p:
            return
        if p['type'] == 'stb':
            self._stb_vod_cats()
            return
        xc = self._xc(p)
        if not xc:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        cats = xc.get_vod_categories()
        from group_selection import enabled_ids
        selected = enabled_ids(p['id'], 'vod', cats)
        cats = [c for c in cats if str(c.get('category_id', '')) in selected]
        cats = apply_lang_sort(cats,
                               name_fn=lambda c: c.get('category_name', ''),
                               group_fn=lambda c: c.get('category_name', ''))
        xbmcplugin.setContent(self._handle, 'files')
        self._add_dir(_L(32016),
                      self.url(action='vod_list', pid=p['id'], cat_id='all'))
        for cat in cats:
            self._add_dir(cat.get('category_name', ''),
                          self.url(action='vod_list', pid=p['id'],
                                   cat_id=cat.get('category_id', '')))
        xbmcplugin.endOfDirectory(self._handle)

    def _vod_list(self):
        p = self._portal()
        if not p:
            return
        cat_id = self._params.get('cat_id')
        page   = int(self._params.get('page', 0))
        psize  = setting_int('items_per_page', 50)
        xc = self._xc(p)
        if not xc:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        from player import vod_list_item
        from group_selection import enabled_ids, filter_entries
        allowed = enabled_ids(p['id'], 'vod', xc.get_vod_categories())
        if cat_id not in (None, 'all') and str(cat_id) not in allowed:
            all_v = []
        else:
            all_v = xc.get_vod_streams(None if cat_id in (None, 'all') else cat_id)
            all_v = filter_entries(all_v, p['id'], 'vod')
        all_v = apply_lang_sort(all_v, name_fn=lambda v: v.get('name', ''), group_fn=lambda v: v.get('category_name', ''))
        chunk = all_v[page * psize:(page + 1) * psize]
        xbmcplugin.setContent(self._handle, 'movies')
        for v in chunk:
            li  = vod_list_item(v)
            sid = v.get('stream_id', '')
            self._add_media_context(li, v, 'vod', sid, p['id'])
            ext = v.get('container_extension', 'mkv')
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='play_vod', pid=p['id'],
                         stream_id=sid, ext=ext,
                         title=v.get('name', ''), logo=v.get('stream_icon', '')),
                li, False
            )
        if (page + 1) * psize < len(all_v):
            self._add_dir(_L(32018, '…'),
                          self.url(action='vod_list', pid=p['id'],
                                   cat_id=cat_id, page=page + 1))
        xbmcplugin.addSortMethod(self._handle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
        xbmcplugin.addSortMethod(self._handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.endOfDirectory(self._handle)


    def _series_categories(self):
        p = self._portal()
        if not p:
            return
        if p['type'] == 'stb':
            self._stb_series_cats()
            return
        xc = self._xc(p)
        if not xc:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        cats = xc.get_series_categories()
        from group_selection import enabled_ids
        selected = enabled_ids(p['id'], 'series', cats)
        cats = [c for c in cats if str(c.get('category_id', '')) in selected]
        cats = apply_lang_sort(cats,
                               name_fn=lambda c: c.get('category_name', ''),
                               group_fn=lambda c: c.get('category_name', ''))
        xbmcplugin.setContent(self._handle, 'files')
        self._add_dir(_L(32017),
                      self.url(action='series_list', pid=p['id'], cat_id='all'))
        for cat in cats:
            self._add_dir(cat.get('category_name', ''),
                          self.url(action='series_list', pid=p['id'],
                                   cat_id=cat.get('category_id', '')))
        xbmcplugin.endOfDirectory(self._handle)

    def _series_list(self):
        p = self._portal()
        if not p:
            return
        cat_id = self._params.get('cat_id')
        page   = int(self._params.get('page', 0))
        psize  = setting_int('items_per_page', 50)
        xc = self._xc(p)
        if not xc:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        from player import series_list_item
        from group_selection import enabled_ids, filter_entries
        allowed = enabled_ids(p['id'], 'series', xc.get_series_categories())
        if cat_id not in (None, 'all') and str(cat_id) not in allowed:
            all_s = []
        else:
            all_s = xc.get_series(None if cat_id in (None, 'all') else cat_id)
            all_s = filter_entries(all_s, p['id'], 'series')
        all_s = apply_lang_sort(all_s, name_fn=lambda s: s.get('name', ''), group_fn=lambda s: s.get('category_name', ''))
        chunk = all_s[page * psize:(page + 1) * psize]
        xbmcplugin.setContent(self._handle, 'tvshows')
        for s in chunk:
            li  = series_list_item(s)
            sid = s.get('series_id', '')
            self._add_media_context(li, s, 'series', sid, p['id'])
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='series_seasons', pid=p['id'],
                         series_id=sid, title=s.get('name', '')),
                li, True
            )
        if (page + 1) * psize < len(all_s):
            self._add_dir(f'Next page ({page + 2})',
                          self.url(action='series_list', pid=p['id'],
                                   cat_id=cat_id, page=page + 1))
        xbmcplugin.endOfDirectory(self._handle)

    def _series_seasons(self):
        p = self._portal()
        if not p:
            return
        series_id = self._params.get('series_id', '')
        show_name = self._params.get('title', '')
        xc = self._xc(p)
        data = xc.get_series_info(series_id) if xc else {}
        episodes_by_season = data.get('episodes', {})
        xbmcplugin.setContent(self._handle, 'seasons')
        xbmcplugin.setPluginCategory(self._handle, show_name)
        for sn, eps in sorted(episodes_by_season.items(),
                               key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else 0):
            li = xbmcgui.ListItem(f'Season {sn}  ({len(eps)} episodes)')
            li.setInfo('video', {'season': int(sn), 'mediatype': 'season'})
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='series_episodes', pid=p['id'],
                         series_id=series_id, season=sn, title=show_name),
                li, True
            )
        xbmcplugin.endOfDirectory(self._handle)

    def _series_episodes(self):
        p = self._portal()
        if not p:
            return
        series_id = self._params.get('series_id', '')
        season    = self._params.get('season', '1')
        show_name = self._params.get('title', '')
        xc = self._xc(p)
        data = xc.get_series_info(series_id) if xc else {}
        episodes = data.get('episodes', {}).get(season, [])
        from player import episode_list_item
        xbmcplugin.setContent(self._handle, 'episodes')
        for ep in episodes:
            li  = episode_list_item(ep, show_name)
            sid = ep.get('id', '')
            ext = ep.get('container_extension', 'mkv')
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='play_episode', pid=p['id'],
                         stream_id=sid, ext=ext,
                         title=ep.get('title', ''),
                         logo=(ep.get('info') or {}).get('movie_image', '')),
                li, False
            )
        xbmcplugin.endOfDirectory(self._handle)


    def _stb_live_groups(self):
        p = self._portal()
        if not p:
            return
        stb = self._stb(p)
        if not stb:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        cats = stb.get_live_categories()
        cats = apply_lang_sort(cats, name_fn=lambda c: c.get('title', ''), group_fn=lambda c: c.get('title', ''))
        xbmcplugin.setPluginCategory(self._handle, p.get('name', ''))
        xbmcplugin.setContent(self._handle, 'videos')
        self._add_dir(_L(32015),
                      self.url(action='stb_channels', pid=p['id'], genre_id='*'),
                      icon=_ICON_TV)
        for cat in cats:
            gid   = str(cat.get('id', '*'))
            gname = cat.get('title', gid)
            self._add_dir(gname,
                          self.url(action='stb_channels',
                                   pid=p['id'], genre_id=gid),
                          icon=_ICON_TV)
        xbmcplugin.endOfDirectory(self._handle, succeeded=True, updateListing=False, cacheToDisc=False)

    def _stb_channels(self):
        p = self._portal()
        if not p:
            return
        genre_id = self._params.get('genre_id', '*')
        stb = self._stb(p)
        if not stb:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        channels_box = [None]
        epg_box      = [None]

        def _load_channels():
            channels_box[0] = stb.get_live_channels(genre_id)

        def _load_epg():
            epg_box[0] = self._epg_cache(p)

        t1 = threading.Thread(target=_load_channels, daemon=True)
        t2 = threading.Thread(target=_load_epg,      daemon=True)
        t1.start(); t2.start()
        t1.join();  t2.join()

        channels = apply_lang_sort(channels_box[0] or [], name_fn=lambda c: c.get('name', ''), group_fn=lambda c: c.get('tv_genre_id', '') or c.get('genre_id', ''))
        xbmcplugin.setContent(self._handle, 'videos')
        from epg import build_epg_ui, build_now_inline, resolve_epg_key
        epg_cache   = epg_box[0] or {}
        portal_id   = p.get('id', 'unknown')
        epg_enabled = setting_bool('epg_enabled', True) and p.get('epg_show', True)
        upcoming    = setting_int('epg_lines', 3)
        now = time.time()
        for ch in channels:
            ch_name = ch.get('name', '')
            logo    = ch.get('logo', '')
            cmd     = ch.get('cmd', '')
            tvg_id  = ch.get('epg_channel_id') or str(ch.get('id', ''))
            epg_key = resolve_epg_key(portal_id, ch) if epg_enabled else None
            label2  = ''
            epg_plot = ''
            display_name = ch_name
            if epg_enabled and epg_key:
                label2, epg_plot = build_epg_ui(portal_id, epg_key, upcoming_count=upcoming)
                now_inline = build_now_inline(portal_id, epg_key)
                if now_inline:
                    display_name = f'{ch_name}  •  {now_inline}'
                if not label2:
                    label2 = 'keine Daten'
            li = xbmcgui.ListItem(label=display_name, label2=label2)
            li.setArt({'icon': logo, 'thumb': logo})
            info_d = {'title': ch_name, 'mediatype': 'video'}
            if epg_plot:
                info_d['plot'] = epg_plot
            li.setInfo('video', info_d)
            li.setProperty('IsPlayable', 'true')
            cm = [
                (('Remove from Favourites' if is_favourite(cmd) else 'Add to Favourites'),
                 f'RunPlugin({self.url(action="toggle_favourite", url=cmd, name=ch_name, logo=logo)})'),
                ('EPG',
                 f'Container.Update({self.url(action="epg_channel", pid=p["id"], tvg_id=tvg_id, name=ch_name)})'),
                (_L(32009),
                 f'Container.Update({self.url(action="stb_catchup_list", pid=p["id"], cmd=cmd, name=ch_name, tvg_id=tvg_id)})'),
            ]
            li.addContextMenuItems(cm)
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='play_stb_live', pid=p['id'],
                         cmd=cmd, name=ch_name, logo=logo),
                li, False
            )
        xbmcplugin.addSortMethod(self._handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self._handle, succeeded=True, updateListing=False, cacheToDisc=False)

    def _stb_vod_cats(self):
        p = self._portal()
        if not p:
            return
        stb = self._stb(p)
        if not stb:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        cats = stb.get_vod_categories()
        cats = apply_lang_sort(cats, name_fn=lambda c: c.get('title', ''), group_fn=lambda c: c.get('title', ''))
        xbmcplugin.setPluginCategory(self._handle, p.get('name', ''))
        xbmcplugin.setContent(self._handle, 'videos')
        self._add_dir(_L(32016),
                      self.url(action='stb_vod_list', pid=p['id'], cat_id='*'),
                      icon=_ICON_VOD)
        for cat in cats:
            cid = str(cat.get('id', '*'))
            self._add_dir(cat.get('title', cid),
                          self.url(action='stb_vod_list', pid=p['id'], cat_id=cid))
        xbmcplugin.endOfDirectory(self._handle, succeeded=True, updateListing=False, cacheToDisc=False)

    def _stb_vod_list(self):
        p = self._portal()
        if not p:
            return
        cat_id = self._params.get('cat_id', '*')
        page   = int(self._params.get('page', 0))
        psize  = setting_int('items_per_page', 50)
        stb = self._stb(p)
        if not stb:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        all_v = stb.get_vod(cat_id)
        all_v = apply_lang_sort(all_v, name_fn=lambda v: v.get('name', ''), group_fn=lambda v: v.get('genres_str', ''))
        chunk = all_v[page * psize:(page + 1) * psize]
        xbmcplugin.setContent(self._handle, 'movies')
        from utils import safe_int, safe_float, safe_year
        for v in chunk:
            name = v.get('name', '')
            logo = v.get('screenshot_uri', '')
            cmd  = v.get('cmd', '')
            li   = xbmcgui.ListItem(name)
            li.setArt({'icon': logo, 'thumb': logo, 'poster': logo})
            li.setInfo('video', {
                'title'    : name,
                'plot'     : v.get('description', ''),
                'year'     : safe_year(v.get('year')),
                'genre'    : v.get('genres_str', ''),
                'director' : v.get('director', ''),
                'rating'   : safe_float(v.get('rating_imdb')),
                'duration' : safe_int(v.get('time')),
                'mediatype': 'movie',
            })
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='play_stb_vod', pid=p['id'],
                         cmd=cmd, name=name, logo=logo),
                li, False
            )
        if (page + 1) * psize < len(all_v):
            self._add_dir(f'Next page ({page + 2})',
                          self.url(action='stb_vod_list', pid=p['id'],
                                   cat_id=cat_id, page=page + 1))
        xbmcplugin.endOfDirectory(self._handle)

    def _stb_series_cats(self):
        p = self._portal()
        if not p:
            return
        stb = self._stb(p)
        if not stb:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        cats = stb.get_series_categories()
        cats = apply_lang_sort(cats, name_fn=lambda c: c.get('title', ''), group_fn=lambda c: c.get('title', ''))
        xbmcplugin.setPluginCategory(self._handle, p.get('name', ''))
        xbmcplugin.setContent(self._handle, 'videos')
        self._add_dir(_L(32017),
                      self.url(action='stb_series_list', pid=p['id'], cat_id='*'))
        for cat in cats:
            cid = str(cat.get('id', '*'))
            self._add_dir(cat.get('title', cid),
                          self.url(action='stb_series_list', pid=p['id'], cat_id=cid))
        xbmcplugin.endOfDirectory(self._handle, succeeded=True, updateListing=False, cacheToDisc=False)

    def _stb_series_list(self):
        p = self._portal()
        if not p:
            return
        cat_id = self._params.get('cat_id', '*')
        page   = int(self._params.get('page', 0))
        psize  = setting_int('items_per_page', 50)
        stb = self._stb(p)
        if not stb:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        all_s = stb.get_series(cat_id)
        all_s = apply_lang_sort(all_s, name_fn=lambda s: s.get('name', ''), group_fn=lambda s: s.get('category_name', '') or s.get('category', ''))
        chunk = all_s[page * psize:(page + 1) * psize]
        xbmcplugin.setContent(self._handle, 'tvshows')
        for s in chunk:
            sid  = str(s.get('id', ''))
            name = s.get('name', '')
            logo = s.get('screenshot_uri', '')
            li   = xbmcgui.ListItem(name)
            li.setArt({'icon': logo, 'thumb': logo, 'poster': logo})
            li.setInfo('video', {'title': name, 'mediatype': 'tvshow'})
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='stb_seasons', pid=p['id'],
                         movie_id=sid, title=name),
                li, True
            )
        if (page + 1) * psize < len(all_s):
            self._add_dir(f'Next page ({page + 2})',
                          self.url(action='stb_series_list', pid=p['id'],
                                   cat_id=cat_id, page=page + 1))
        xbmcplugin.endOfDirectory(self._handle)

    def _stb_seasons(self):
        p = self._portal()
        if not p:
            return
        movie_id = self._params.get('movie_id', '')
        title    = self._params.get('title', '')
        stb = self._stb(p)
        if not stb:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        seasons = stb.get_series_seasons(movie_id)
        xbmcplugin.setContent(self._handle, 'seasons')
        xbmcplugin.setPluginCategory(self._handle, title)
        for s in seasons:
            sid   = str(s.get('id', ''))
            sname = s.get('name', f'Season {sid}')
            li    = xbmcgui.ListItem(sname)
            li.setInfo('video', {'mediatype': 'season'})
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='stb_episodes', pid=p['id'],
                         movie_id=movie_id, season_id=sid, title=title),
                li, True
            )
        xbmcplugin.endOfDirectory(self._handle)

    def _stb_episodes(self):
        p = self._portal()
        if not p:
            return
        movie_id  = self._params.get('movie_id', '')
        season_id = self._params.get('season_id', '')
        show_name = self._params.get('title', '')
        stb = self._stb(p)
        if not stb:
            xbmcplugin.endOfDirectory(self._handle, False)
            return
        eps = stb.get_series_episodes(movie_id, season_id)
        xbmcplugin.setContent(self._handle, 'episodes')
        from utils import safe_int
        for ep in eps:
            name = ep.get('name', '')
            cmd  = ep.get('cmd', '')
            logo = ep.get('screenshot_uri', '')
            ep_n = safe_int(ep.get('series_num', ep.get('episode_num', 0)))
            li   = xbmcgui.ListItem(f'{ep_n:02d}. {name}' if ep_n else name)
            li.setArt({'icon': logo, 'thumb': logo})
            li.setInfo('video', {
                'title'    : name,
                'episode'  : ep_n,
                'plot'     : ep.get('description', ''),
                'duration' : safe_int(ep.get('time')),
                'mediatype': 'episode',
            })
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='play_stb_episode', pid=p['id'],
                         cmd=cmd, name=name, logo=logo),
                li, False
            )
        xbmcplugin.endOfDirectory(self._handle)

    def _stb_catchup_list(self):
        p = self._portal()
        if not p:
            return
        cmd    = self._params.get('cmd', '')
        name   = self._params.get('name', '')
        tvg_id = self._params.get('tvg_id', '')
        xbmcplugin.setContent(self._handle, 'videos')
        xbmcplugin.setPluginCategory(self._handle, f'{_L(32009)} – {name}')
        now     = time.time()
        days    = max(1, setting_int('epg_hours_back', 72) // 24)
        from_ts = now - days * 86400
        prgs    = []
        mgr = self._epg_mgr(p)
        if mgr:
            prgs = mgr.get_range(tvg_id, from_ts, now)
        if not prgs and tvg_id:
            stb = self._stb(p)
            if stb:
                for e in stb.get_short_epg(tvg_id, count=50):
                    try:
                        s = int(e.get('start_timestamp', e.get('time', 0)))
                        q = int(e.get('stop_timestamp',  e.get('time_to', 0)))
                        if s and q and q < now:
                            from epg import Programme
                            prgs.append(Programme(
                                channel=tvg_id, start=s, stop=q,
                                title=e.get('name', ''), desc=e.get('descr', '')
                            ))
                    except Exception:
                        pass
        if not prgs:
            notify(_L(32009), _L(32047))
            xbmcplugin.endOfDirectory(self._handle)
            return
        import datetime as _dt
        for pr in sorted(prgs, key=lambda x: x.start, reverse=True):
            dt_s = _dt.datetime.fromtimestamp(pr.start).strftime('%d/%m  %H:%M')
            li   = xbmcgui.ListItem(f'{dt_s}   {pr.title}')
            li.setInfo('video', {
                'title': pr.title, 'plot': pr.desc,
                'duration': max(0, pr.stop - pr.start), 'mediatype': 'video',
            })
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='play_stb_catchup', pid=p['id'],
                         cmd=cmd, name=pr.title,
                         start=int(pr.start), stop=int(pr.stop)),
                li, False
            )
        xbmcplugin.endOfDirectory(self._handle)

    def _stb_account(self):
        p = self._portal()
        if not p:
            return
        stb    = self._stb(p)
        info_d = stb.get_account_info() if stb else {}
        lines = [
            f'Portal:  {p["name"]}',
            f'MAC:     {p.get("stb_mac", "")}',
        ]
        _status = info_d.get('status', '')
        if _status:
            lines.append(f'Status:  {_status}')
        _pv2 = info_d.get('phone', '')
        _end = info_d.get('end_date', '')
        if _pv2:
            import re as _re2
            _pv2_norm = _re2.sub(r'\b(am|pm)\b', lambda m: m.group().upper(), _pv2.strip(), flags=_re2.IGNORECASE)
            _matched2 = False
            for _fmt2 in ('%B %d, %Y, %I:%M %p', '%B %d, %Y, %-I:%M %p', '%B %d, %Y',
                          '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d.%m.%Y'):
                try:
                    import datetime as _dtp3
                    _exp2 = _dtp3.datetime.strptime(_pv2_norm, _fmt2)
                    _days2 = (_exp2 - _dtp3.datetime.now()).days
                    lines.append(f'Läuft ab: {_exp2.strftime("%d.%m.%Y %H:%M")}  ({_days2} Tage)')
                    _matched2 = True
                    break
                except Exception:
                    pass
            if not _matched2:
                lines.append(f'Läuft ab: {_pv2}')
        elif _end:
            try:
                import datetime as _dtp4
                _exp3 = _dtp4.datetime.strptime(_end[:10], '%Y-%m-%d')
                _days3 = (_exp3 - _dtp4.datetime.now()).days
                lines.append(f'Läuft ab: {_exp3.strftime("%d.%m.%Y")}  ({_days3} Tage)')
            except Exception:
                lines.append(f'Läuft ab: {_end}')
        _pkg = info_d.get('tariff_plan_name', '')
        if _pkg:
            lines.append(f'Paket:    {_pkg}')
        _mc = info_d.get('max_connections', '')
        if _mc:
            lines.append(f'Max conn: {_mc}')
        xbmcgui.Dialog().ok(_L(32013), '\n'.join(lines))
        xbmcplugin.endOfDirectory(self._handle)


    def _xtream_account(self):
        import datetime as _dt
        p = self._portal()
        if not p:
            return
        host = p.get('xc_host', '')
        user = p.get('xc_user', '')
        pwd  = p.get('xc_pass', '')
        lines = [
            f'Portal:  {p["name"]}',
            f'Server:  {host}',
            f'Benutzer: {user}',
            f'Passwort: {pwd}',
        ]
        if host and user:
            try:
                from xtream import XtreamClient
                xc = XtreamClient(host, user, pwd)
                ui = xc.get_user_info()
                si = xc.get_server_info()
                if ui:
                    lines.append('')
                    lines.append('── Account-Info ──')
                    status = ui.get('status', '?')
                    auth   = ui.get('auth', 0)
                    lines.append(f'Status:  {status}  |  Auth: {"✔" if auth else "✘"}')
                    if ui.get('exp_date'):
                        try:
                            exp = _dt.datetime.fromtimestamp(int(ui['exp_date']))
                            days_left = (exp - _dt.datetime.now()).days
                            lines.append(f'Läuft ab: {exp.strftime("%d.%m.%Y")}  ({days_left} Tage)')
                        except Exception:
                            lines.append(f'Läuft ab: {ui["exp_date"]}')
                    if ui.get('max_connections'):
                        lines.append(f'Max. Verbindungen: {ui["max_connections"]}')
                    if ui.get('active_cons') is not None:
                        lines.append(f'Aktive Verbindungen: {ui["active_cons"]}')
                    if ui.get('is_trial') in ('1', 1, True):
                        lines.append('Trial-Account')
                if si:
                    lines.append('')
                    lines.append('── Server-Info ──')
                    if si.get('timezone'):
                        lines.append(f'Zeitzone: {si["timezone"]}')
                    if si.get('server_protocol'):
                        lines.append(f'Protokoll: {si["server_protocol"]}')
            except Exception as e:
                lines.append(f'(Account-Info nicht verfügbar: {e})')
        xbmcgui.Dialog().ok(_L(32013), '\n'.join(lines))
        xbmcplugin.endOfDirectory(self._handle)


    def _m3u_account(self):
        import datetime as _dt
        p = self._portal()
        if not p:
            return
        url = p.get('m3u_url', '')
        lines = [
            f'Portal:  {p["name"]}',
            f'URL:     {url}',
        ]
        if p.get('epg_url'):
            lines.append(f'EPG:     {p["epg_url"]}')
        from portals import detect_xtream
        xc_creds = detect_xtream(url)
        if xc_creds:
            lines.append('')
            lines.append('── Xtream Codes erkannt ──')
            lines.append(f'Server:   {xc_creds["xc_host"]}')
            lines.append(f'Benutzer: {xc_creds["xc_user"]}')
            lines.append(f'Passwort: {xc_creds["xc_pass"]}')
            try:
                from xtream import XtreamClient
                xc = XtreamClient(xc_creds['xc_host'], xc_creds['xc_user'], xc_creds['xc_pass'])
                ui = xc.get_user_info()
                if ui:
                    lines.append('')
                    lines.append('── Account-Info ──')
                    status = ui.get('status', '?')
                    auth   = ui.get('auth', 0)
                    lines.append(f'Status:  {status}  |  Auth: {"✔" if auth else "✘"}')
                    if ui.get('exp_date'):
                        try:
                            exp = _dt.datetime.fromtimestamp(int(ui['exp_date']))
                            days_left = (exp - _dt.datetime.now()).days
                            lines.append(f'Läuft ab: {exp.strftime("%d.%m.%Y")}  ({days_left} Tage)')
                        except Exception:
                            lines.append(f'Läuft ab: {ui["exp_date"]}')
                    if ui.get('max_connections'):
                        lines.append(f'Max. Verbindungen: {ui["max_connections"]}')
                    if ui.get('active_cons') is not None:
                        lines.append(f'Aktive Verbindungen: {ui["active_cons"]}')
            except Exception as e:
                lines.append(f'(Account-Info nicht verfügbar: {e})')
        xbmcgui.Dialog().ok(_L(32013), '\n'.join(lines))
        xbmcplugin.endOfDirectory(self._handle)


    def _favourites(self):
        xbmcplugin.setContent(self._handle, 'videos')
        xbmcplugin.setPluginCategory(self._handle, _L(32004))
        favs = load_favourites()
        if not favs:
            notify(_L(32004), _L(32045))
            xbmcplugin.endOfDirectory(self._handle)
            return
        from player import channel_list_item
        from iptv import Channel
        for fav in favs:
            ch = Channel(name=fav['name'], url=fav['url'],
                         logo=fav.get('logo', ''), group=_L(32004))
            li = channel_list_item(ch)
            li.addContextMenuItems([
                ('Remove from Favourites',
                 f'RunPlugin({self.url(action="toggle_favourite", url=ch.url, name=ch.name, logo=ch.logo)})'),
            ])
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='play_live', url=ch.url, name=ch.name, logo=ch.logo),
                li, False
            )
        xbmcplugin.endOfDirectory(self._handle)


    def _search(self):
        query = xbmcgui.Dialog().input(_L(32005), type=xbmcgui.INPUT_ALPHANUM)
        pid = self._params.get('pid', '')
        if not query:
            xbmcplugin.endOfDirectory(self._handle, succeeded=False)
            return
        self._params['q']   = query
        self._params['pid'] = pid
        self._search_results()
        return 
    def _search_results(self):
        query = self._params.get('q', '')
        pid   = self._params.get('pid', '')
        if not query:
            xbmcplugin.endOfDirectory(self._handle)
            return
        xbmcplugin.setContent(self._handle, 'videos')
        xbmcplugin.setPluginCategory(self._handle, f'{_L(32005)}: {query}')
        import portals as P
        from concurrent.futures import ThreadPoolExecutor, as_completed
        search_list = [P.get_by_id(pid)] if pid else P.get_active()
        search_list = [x for x in search_list if x]

        all_items = []
        workers   = min(len(search_list), 6)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(self._search_in_portal_collect, p, query): p
                       for p in search_list}
            for fut in as_completed(futures):
                try:
                    all_items.extend(fut.result())
                except Exception as e:
                    error(f'search thread error: {e}')

        all_items = apply_lang_sort(
            all_items,
            name_fn=lambda x: x[1].getLabel(),
            group_fn=lambda x: ''
        )
        for url, li, is_folder in all_items:
            xbmcplugin.addDirectoryItem(self._handle, url, li, is_folder)

        if not all_items:
            notify(_L(32005), _L(32046, query))
        xbmcplugin.endOfDirectory(self._handle)

    def _search_in_portal(self, p: dict, query: str) -> int:
        items = self._search_in_portal_collect(p, query)
        for url, li, is_folder in items:
            xbmcplugin.addDirectoryItem(self._handle, url, li, is_folder)
        return len(items)

    def _search_in_portal_collect(self, p: dict, query: str) -> list:
        ptype  = p.get('type', 'm3u')
        items  = []

        if ptype == 'stb':
            stb = self._stb(p)
            if stb:
                from iptv import Channel
                from player import channel_list_item
                for s in stb.search_live(query)[:50]:
                    ch = Channel(name=s.get('name', ''), url=s.get('cmd', ''),
                                 logo=s.get('logo', ''), group='Live')
                    items.append((
                        self.url(action='play_stb_live', pid=p['id'],
                                 cmd=s.get('cmd', ''), name=ch.name, logo=ch.logo),
                        channel_list_item(ch), False))
                for v in stb.search_vod(query)[:50]:
                    li = xbmcgui.ListItem(v.get('name', ''))
                    li.setInfo('video', {'title': v.get('name', ''), 'mediatype': 'movie'})
                    li.setProperty('IsPlayable', 'true')
                    items.append((
                        self.url(action='play_stb_vod', pid=p['id'],
                                 cmd=v.get('cmd', ''), name=v.get('name', '')),
                        li, False))

        elif ptype == 'xtream':
            xc = self._xc(p)
            if xc:
                from iptv import Channel
                from player import channel_list_item, vod_list_item
                for s in xc.search_live(query)[:50]:
                    ch = Channel(name=s.get('name', ''),
                                 url=xc.live_stream_url(s['stream_id']),
                                 logo=s.get('stream_icon', ''), group='Live')
                    items.append((
                        self.url(action='play_live', url=ch.url,
                                 name=ch.name, logo=ch.logo),
                        channel_list_item(ch), False))
                for v in xc.search_vod(query)[:50]:
                    li = vod_list_item(v)
                    items.append((
                        self.url(action='play_vod', pid=p['id'],
                                 stream_id=v.get('stream_id'),
                                 ext=v.get('container_extension', 'mkv'),
                                 title=v.get('name'), logo=v.get('stream_icon', '')),
                        li, False))
                for s in xc.search_series(query)[:50]:
                    li = xbmcgui.ListItem(s.get('name', ''))
                    li.setArt({'thumb': s.get('cover', ''), 'icon': s.get('cover', '')})
                    li.setInfo('video', {'title': s.get('name', ''),
                                         'mediatype': 'tvshow', 'plot': s.get('plot', '')})
                    items.append((
                        self.url(action='series_seasons', pid=p['id'],
                                 series_id=s.get('series_id')),
                        li, True))

        else:
            from iptv import load_m3u, split_m3u_sections
            all_ch   = load_m3u(p.get('m3u_url', ''), portal_id=p['id'])
            sections = split_m3u_sections(all_ch)
            q = query.lower()
            for section, mediatype in (
                ('live',   'video'),
                ('movies', 'movie'),
                ('series', 'episode'),
            ):
                for ch in sections.get(section, []):
                    if q in ch.name.lower() or q in (ch.group or '').lower():
                        li = xbmcgui.ListItem(ch.name)
                        li.setArt({'thumb': ch.logo, 'icon': ch.logo})
                        li.setInfo('video', {'title': ch.name, 'mediatype': mediatype})
                        li.setProperty('IsPlayable', 'true')
                        items.append((
                            self.url(action='play_live', url=ch.url,
                                     name=ch.name, logo=ch.logo),
                            li, False))
                        if len(items) >= 200:
                            return apply_lang_sort(items, name_fn=lambda x: x[1].getLabel(), group_fn=lambda x: '')
        return apply_lang_sort(items, name_fn=lambda x: x[1].getLabel(), group_fn=lambda x: '')


    def _epg_now(self):
        # The old manager iterated raw XMLTV IDs, bypassing sender mappings and
        # short-EPG. Use the same actual-channel preview as the TV overlay.
        self._epg_status(preview_first=True)

    def _epg_status(self, preview_first=False):
        if self._handle >= 0:
            xbmcplugin.endOfDirectory(self._handle,succeeded=False,cacheToDisc=False)
        p = self._portal()
        if p:
            from epg_preview import show
            show(p,preview_first=preview_first)

    def _epg_channel(self):
        p = self._portal()
        if not p:
            return
        tvg_id = self._params.get('tvg_id', '')
        name   = self._params.get('name', tvg_id)
        sid = self._params.get('sid','')
        if sid:
            # A freshly edited mapping must not depend on a stale stream alias
            # left by an earlier XMLTV import. Share TV/preview resolution.
            xbmcplugin.endOfDirectory(self._handle,succeeded=False,cacheToDisc=False)
            from epg import load_cache
            from epg_sources import configuration
            from epg_views import resolve_guide
            from epg_preview import programme_lines
            info=resolve_guide(load_cache(p['id']),tvg_id,sid,
                client=self._xc(p) if p.get('type')=='xtream' else None,
                mappings=configuration(p['id'])['mappings'])
            xbmcgui.Dialog().textviewer('XCMate - '+name,'\n'.join(programme_lines(info)))
            return
        xbmcplugin.setContent(self._handle, 'videos')
        xbmcplugin.setPluginCategory(self._handle, f'EPG – {name}')
        mgr = self._epg_mgr(p)
        now  = time.time()
        back = setting_int('epg_hours_back', 3) * 3600
        ahead= setting_int('epg_hours_ahead', 12) * 3600
        prgs = mgr.get_range(tvg_id, now - back, now + ahead) if mgr else []
        import datetime as _dt
        for pr in prgs:
            dt_s  = _dt.datetime.fromtimestamp(pr.start).strftime('%H:%M')
            label = f'{dt_s}  {pr.title}'
            if pr.episode:
                label += f'  [{pr.episode}]'
            li = xbmcgui.ListItem(label)
            li.setInfo('video', {
                'title': pr.title, 'plot': pr.desc,
                'genre': pr.category, 'episode': pr.episode,
                'duration': max(0, pr.stop - pr.start),
            })
            if pr.stop < now:
                xbmcplugin.addDirectoryItem(
                    self._handle,
                    self.url(action='play_catchup', pid=p['id'],
                             start=int(pr.start), stop=int(pr.stop),
                             tvg_id=tvg_id, name=pr.title),
                    li, False)
            else:
                xbmcplugin.addDirectoryItem(self._handle, '', li, False)
        xbmcplugin.endOfDirectory(self._handle)

    def _catchup_list(self):
        p = self._portal()
        if not p:
            return
        url    = self._params.get('url', '')
        name   = self._params.get('name', '')
        tvg_id = self._params.get('tvg_id', '')
        xbmcplugin.setContent(self._handle, 'videos')
        mgr     = self._epg_mgr(p)
        now     = time.time()
        from_ts = now - setting_int('epg_hours_back', 72) * 3600
        prgs    = mgr.get_range(tvg_id, from_ts, now) if mgr else []
        import datetime as _dt
        for pr in sorted(prgs, key=lambda x: x.start, reverse=True):
            dt_s = _dt.datetime.fromtimestamp(pr.start).strftime('%d/%m %H:%M')
            li   = xbmcgui.ListItem(f'{dt_s}  {pr.title}')
            li.setInfo('video', {'title': pr.title, 'plot': pr.desc,
                                 'duration': max(0, pr.stop - pr.start)})
            xbmcplugin.addDirectoryItem(
                self._handle,
                self.url(action='play_catchup', pid=p['id'],
                         start=int(pr.start), stop=int(pr.stop),
                         tvg_id=tvg_id, name=pr.title, base_url=url),
                li, False)
        xbmcplugin.endOfDirectory(self._handle)


    def _play_live(self):
        import urllib.parse
        url  = self._params.get('url', '')
        name = self._params.get('name', '')
        logo = self._params.get('logo', '')
        if url and '%25' in url:
            url = urllib.parse.unquote(url)
        if not url and self._params.get('sid'):
            # Widgets only store non-secret portal IDs and Xtream stream IDs.
            import portals as _portal_store
            p = _portal_store.get_by_id(self._params.get('pid',''))
            if p and p.get('type') == 'xtream':
                xc = self._xc(p)
                url = xc.live_stream_url(self._params['sid'])
        if not url:
            error('play_live: no URL in params')
            notify('XCMate', 'Stream URL fehlt')
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return
        # The service displays a transparent on-video TV remote panel. Never
        # put the stream URL or Xtream credentials in the session marker.
        session=None
        import portals as _portals
        from live_recovery import recover_from_player_path
        from xtream import XtreamClient
        active=_portals.get_active()
        requested_pid=self._params.get('pid')
        if requested_pid:
            active=[p for p in active if str(p.get('id'))==str(requested_pid)]
        match=recover_from_player_path(url,active,XtreamClient)
        if match:
            from live_overlay import announce
            session=announce(match[0],match[1],name)
        else:
            from live_diagnostics import record
            record('session','SOURCE_NOT_VERIFIED',marker=False)
        from player import play_stream
        play_stream(self._handle, url, title=name, logo=logo,live_session=session)

    def _play_vod(self):
        p   = self._portal()
        sid = self._params.get('stream_id', '')
        ext = self._params.get('ext', 'mkv')
        title = self._params.get('title', '')
        logo  = self._params.get('logo', '')
        xc = self._xc(p) if p else None
        if not xc or not sid:
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return
        from player import play_stream
        play_stream(self._handle, xc.vod_stream_url(sid, ext), title=title, logo=logo)

    def _play_episode(self):
        p   = self._portal()
        sid = self._params.get('stream_id', '')
        ext = self._params.get('ext', 'mkv')
        title = self._params.get('title', '')
        logo  = self._params.get('logo', '')
        xc = self._xc(p) if p else None
        if not xc or not sid:
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return
        from player import play_stream
        play_stream(self._handle, xc.series_episode_url(sid, ext), title=title, logo=logo)

    def _play_catchup(self):
        p      = self._portal()
        start  = int(self._params.get('start', 0))
        stop   = int(self._params.get('stop', 0))
        tvg_id = self._params.get('tvg_id', '')
        name   = self._params.get('name', '')
        burl   = self._params.get('base_url', '')
        from player import play_catchup
        xc = self._xc(p) if (p and p.get('type') == 'xtream') else None
        if xc and tvg_id:
            streams = xc.get_live_streams()
            sid_map = {s.get('epg_channel_id', ''): s.get('stream_id') for s in streams}
            stream_id = sid_map.get(tvg_id)
            if stream_id:
                play_catchup(self._handle, xc.catchup_url(stream_id, start, stop), start, stop, name)
                return
        if burl:
            tpl = setting('catchup_format', '{url}?utc={utc}&lutc={lutc}')
            cu  = (tpl.replace('{url}', burl)
                      .replace('{utc}', str(start))
                      .replace('{lutc}', str(stop))
                      .replace('{duration}', str(max(1, (stop - start) // 60))))
            play_catchup(self._handle, cu, start, stop, name)
        else:
            notify(_L(32009), _L(32048))
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())

    def _play_stb_live(self):
        p    = self._portal()
        cmd  = self._params.get('cmd', '')
        name = self._params.get('name', '')
        logo = self._params.get('logo', '')
        stb  = self._stb(p) if p else None
        if not stb or not cmd:
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        if not stb.authenticate():
            notify('STB', 'Authentication failed – check Portal URL and MAC')
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        url = stb.get_channel_stream_url(cmd)
        if not url:
            warn('STB: create_link returned empty, re-authenticating…')
            if stb.authenticate(force=True):
                url = stb.get_channel_stream_url(cmd)
        if not url:
            notify('STB', 'Stream URL konnte nicht aufgelöst werden.\nCmd: ' + cmd[:60])
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        from player import play_stream
        play_stream(self._handle, url, title=name, logo=logo,
                    headers=stb.stream_headers())

    def _play_stb_vod(self):
        p    = self._portal()
        cmd  = self._params.get('cmd', '')
        name = self._params.get('name', '')
        logo = self._params.get('logo', '')
        stb  = self._stb(p) if p else None
        if not stb or not cmd:
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        if not stb.authenticate():
            notify('STB', 'Authentication failed')
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        action = self._params.get('action', 'play_stb_vod')
        if action == 'play_stb_episode':
            url = stb.get_episode_stream_url(cmd)
        else:
            url = stb.get_vod_stream_url(cmd)

        if not url:
            if stb.authenticate(force=True):
                url = stb.get_vod_stream_url(cmd)
        if not url:
            notify('STB', 'VOD-URL konnte nicht aufgelöst werden')
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        from player import play_stream
        play_stream(self._handle, url, title=name, logo=logo,
                    headers=stb.stream_headers())

    def _play_stb_catchup(self):
        p     = self._portal()
        cmd   = self._params.get('cmd', '')
        start = int(self._params.get('start', 0))
        stop  = int(self._params.get('stop', 0))
        name  = self._params.get('name', '')
        stb   = self._stb(p) if p else None
        if not stb or not cmd:
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        if not stb.authenticate():
            notify('STB', 'Authentication failed')
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        url = stb.get_catchup_url(cmd, start, stop)
        if not url:
            if stb.authenticate(force=True):
                url = stb.get_catchup_url(cmd, start, stop)
        if not url:
            notify('STB Catch-up', 'Catch-up URL nicht verfügbar')
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        from player import play_catchup
        play_catchup(self._handle, url, start, stop, name,
                     headers=stb.stream_headers())


    def _toggle_favourite(self):
        url   = self._params.get('url', '')
        name  = self._params.get('name', '')
        logo  = self._params.get('logo', '')
        group = self._params.get('group', '')
        if url:
            toggle_favourite(url, name, logo, group)
        xbmc.executebuiltin('Container.Refresh')

    def _refresh_portal(self):
        import portals as P
        pid = self._params.get('pid', '')
        p   = P.get_by_id(pid)
        if not p:
            return
        notify('XCMate', f'Refreshing {p["name"]}…', duration=1500)
        self._load_channels(p, force=True)
        if p.get('type') == 'xtream':
            from xtream import XtreamClient
            xc = XtreamClient(p['xc_host'], p['xc_user'], p['xc_pass'])
            xc.get_vod_categories(force_refresh=True)
            xc.get_series_categories(force_refresh=True)
        notify('XCMate', f'{p["name"]} refreshed')
        xbmc.executebuiltin('Container.Refresh')

    def _epg_sources(self):
        # Close Kodi's directory request BEFORE opening a modal EPG manager.
        # Otherwise clicking this folder action can leave a persistent spinner.
        if self._handle >= 0:
            xbmcplugin.endOfDirectory(self._handle, succeeded=False,
                                      cacheToDisc=False)
        import portals as P
        from epg_sources import manage
        portal = P.get_by_id(self._params.get('pid', ''))
        manage(portal)

    def _refresh_epg(self):
        import portals as P
        pid = self._params.get('pid', '')
        p   = P.get_by_id(pid)
        if not p:
            return
        # End the plugin directory request before scheduling any network work.
        if self._handle >= 0:
            xbmcplugin.endOfDirectory(self._handle, succeeded=False, cacheToDisc=False)
        from epg import request_refresh
        request_refresh(p['id'], p, force=True)
        notify('XCMate', 'EPG-Aktualisierung im Hintergrund gestartet')

    def _do_clear_cache(self):
        cache_clear()
        notify('XCMate', 'Cache cleared')

    def _open_settings(self):
        ADDON.openSettings()

    def _add_portal_from_settings(self):
        from utils import setting, setting_bool, setting_int, _L
        import portals

        DEFAULTS = {
            'new_portal_name'   : 'My IPTV',
            'new_portal_m3u_url': '',
            'new_portal_xc_host': '',
            'new_portal_xc_user': '',
            'new_portal_xc_pass': '',
            'new_portal_stb_url': '',
            'new_portal_stb_mac': '00:1A:79:00:00:00',
            'new_portal_epg_url': '',
        }

        name     = setting('new_portal_name', 'My IPTV').strip()
        type_idx = setting_int('new_portal_type', 0)
        epg_url  = setting('new_portal_epg_url', '').strip()
        epg_show = setting_bool('new_portal_epg_show', True)
        enabled  = setting_bool('new_portal_enabled', True)

        if type_idx in (0, 1):
            url = setting('new_portal_m3u_url', '').strip()
            if not url:
                notify('XCMate', _L(32283))
                return
            xc = portals.detect_xtream(url)
            if xc:
                data = dict(name=name, type='xtream', epg_url=epg_url,
                            epg_show=epg_show, enabled=enabled, **xc)
            else:
                data = dict(name=name, type='m3u', m3u_url=url,
                            epg_url=epg_url, epg_show=epg_show, enabled=enabled)
        elif type_idx == 2:
            host = setting('new_portal_xc_host', '').strip()
            user = setting('new_portal_xc_user', '').strip()
            pwd  = setting('new_portal_xc_pass', '').strip()
            if not host or not user:
                notify('XCMate', _L(32284))
                return
            data = dict(name=name, type='xtream', xc_host=host,
                        xc_user=user, xc_pass=pwd,
                        epg_url=epg_url, epg_show=epg_show, enabled=enabled)
        elif type_idx == 3:
            url = setting('new_portal_stb_url', '').strip()
            mac = setting('new_portal_stb_mac', '00:1A:79:00:00:00').strip()
            if not url or not mac:
                notify('XCMate', _L(32285))
                return
            data = dict(name=name, type='stb', stb_url=url, stb_mac=mac,
                        epg_url=epg_url, epg_show=epg_show, enabled=enabled)
        else:
            return

        portals.add(data)
        notify('XCMate', _L(32083, name))
        for key, val in DEFAULTS.items():
            ADDON.setSetting(key, val)
        ADDON.setSetting('new_portal_type',    '0')
        ADDON.setSetting('new_portal_epg_show','true')
        ADDON.setSetting('new_portal_enabled', 'true')

        xbmc.executebuiltin('Container.Refresh')


    def _portal(self) -> Optional[dict]:
        import portals as P
        pid = self._params.get('pid', '')
        p   = P.get_by_id(pid) if pid else None
        if not p:
            notify('XCMate', 'Portal not found. Open Portal Manager.')
            xbmcplugin.endOfDirectory(self._handle, False)
        return p

    def _xc(self, p: dict):
        if not p or p.get('type') != 'xtream':
            return None
        from xtream import XtreamClient
        return XtreamClient(p['xc_host'], p['xc_user'], p['xc_pass'])

    def _stb(self, p: dict):
        if not p or p.get('type') != 'stb':
            return None
        from stalker import client_for_portal
        return client_for_portal(p)

    def _epg_cache(self, p: dict):
        try:
            from epg import load_cache
            portal_id = p.get('id', 'unknown')
            return load_cache(portal_id)
        except Exception:
            return {}

    def _epg_mgr(self, p: dict):
        from epg import EPGManager
        data = self._epg_cache(p)
        if not data:
            return None
        return EPGManager(data)

    def _load_channels(self, p: dict, force: bool = False):
        ptype = p.get('type', 'm3u')
        if ptype == 'stb':
            from stalker import client_for_portal
            from iptv import Channel
            stb = client_for_portal(p)
            if not stb or not stb.authenticate():
                return []
            cats = {str(c['id']): c.get('title', '')
                    for c in stb.get_live_categories(force=force)}
            return [
                Channel(
                    name    = s.get('name', ''),
                    url     = s.get('cmd', ''),
                    logo    = s.get('logo', ''),
                    group   = cats.get(str(s.get('genre_id',
                                               s.get('tv_genre_id', ''))),
                                       'Uncategorised'),
                    tvg_id  = s.get('epg_channel_id') or str(s.get('id', '')),
                    tvg_name= s.get('name', ''),
                )
                for s in stb.get_live_channels(force=force)
            ]
        elif ptype == 'xtream':
            from xtream import XtreamClient
            from iptv import Channel
            xc   = XtreamClient(p['xc_host'], p['xc_user'], p['xc_pass'])
            # Never block back navigation with server requests. Kodi service
            # preloads these two indexes independently of the interface.
            cats_raw = (xc.get_live_categories(force_refresh=True) if force else
                        xc.get_cached_catalog('get_live_categories'))
            channels_raw = (xc.get_live_streams(force_refresh=True) if force else
                            xc.get_cached_catalog('get_live_streams'))
            if cats_raw is None or channels_raw is None:
                return []
            cats = {str(c['category_id']): c.get('category_name', '')
                    for c in cats_raw if isinstance(c, dict) and 'category_id' in c}
            return [
                Channel(
                    name    = s.get('name', ''),
                    url     = xc.live_stream_url(s.get('stream_id', ''), 'ts'),
                    logo    = s.get('stream_icon', ''),
                    group   = cats.get(str(s.get('category_id', '')), 'Uncategorised'),
                    extra   = {'category_id': str(s.get('category_id', '')),
                               'stream_id': str(s.get('stream_id', ''))},
                    tvg_id  = s.get('epg_channel_id', ''),
                    tvg_name= s.get('name', ''),
                )
                for s in channels_raw if isinstance(s, dict)
            ]
        else:
            from iptv import load_m3u
            url = p.get('m3u_url', '').strip()
            if not url:
                error(f'load_channels: portal "{p.get("name")}" has no m3u_url')
                return []
            return load_m3u(url,
                            portal_id=p.get('id', ''),
                            force_refresh=force)

    def _add_dir(self, label, url, icon=None, is_folder=True, plot=''):
        li = xbmcgui.ListItem(label)
        _icon = icon if icon else ADDON_ICON
        li.setArt({
            'icon':      _icon,
            'thumb':     _icon,
            'landscape': _icon,
            'clearart':  _icon,
            'fanart':    ADDON_FANART,
        })
        li.setInfo('video', {'title': label, 'plot': plot or label})
        if not is_folder:
            li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self._handle, url, li, isFolder=is_folder)

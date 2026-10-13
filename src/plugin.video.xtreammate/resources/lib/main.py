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
            'epg_channel'        : self._epg_channel,
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
        }
        if action == 'root' and not _portals_mod.load_all():
            from setup_wizard import setup
            created = setup()
            if created:
                # The same request renders the new portal home directly.
                self._params['pid'] = created['id']
                self._portal_home()
                return
        R.get(action, self._root)()


    def _portal_plot(self, p: dict, extra: str = '') -> str:
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
            if _xc_creds:
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
            if host and user:
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
            if p.get('stb_url') and p.get('stb_mac'):
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

        if len(active) == 1:
            self._show_portal_home(active[0])
            return

        from concurrent.futures import ThreadPoolExecutor, as_completed as _asc
        plots = {}
        with ThreadPoolExecutor(max_workers=min(len(active), 4)) as _ex:
            _futs = {_ex.submit(self._portal_plot, p): p['id'] for p in active}
            for _fut in _asc(_futs):
                try:
                    plots[_futs[_fut]] = _fut.result()
                except Exception:
                    plots[_futs[_fut]] = ''
        for p in active:
            self._add_dir(p['name'],
                          self.url(action='portal_home', pid=p['id']),
                          icon=_ICON_TV,
                          plot=plots.get(p['id'], ''))

        self._add_dir(_L(32011), self.url(action='favourites'),
                      icon=_ICON_FAV,
                      plot='Alle Favoriten aus allen Portalen anzeigen.')
        self._add_dir(_L(32010), self.url(action='search'),
                      icon=_ICON_SEARCH,
                      plot='Portalübergreifend nach Sendern, Filmen und Serien suchen.')
        self._add_dir(_L(32012), self.url(action='portal_manager'),
                      icon=_ICON_SETTINGS,
                      plot='Portale hinzufügen, bearbeiten oder entfernen.')
        self._add_dir(_L(32007), self.url(action='settings'),
                      icon=_ICON_SETTINGS,
                      plot='Addon-Einstellungen öffnen.')
        xbmcplugin.endOfDirectory(self._handle)

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
        ptype = p.get('type', 'm3u')
        xbmcplugin.setPluginCategory(self._handle, p['name'])
        xbmcplugin.setContent(self._handle, '')
        pid = p['id']

        _base_plot = self._portal_plot(p)

        def _pp(extra=''):
            return (_base_plot + '\n' + extra) if extra else _base_plot

        if p.get('include_live', True):
            self._add_dir(_L(32001),
                          self.url(action='live_groups', pid=pid),
                          icon=_ICON_TV,
                          plot=_pp('Live-TV Sendergruppen anzeigen.'))
        if ptype == 'xtream':
            self._add_dir('Gruppen verwalten: Live-TV, Filme und Serien',
                          self.url(action='groups_manager', pid=pid),
                          icon=_ICON_SETTINGS,
                          plot='Gruppen einzeln aktivieren/deaktivieren; alle oder neue Gruppen auswählen.')
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

    def _groups_manager(self):
        import portals
        pid = self._params.get('pid', '')
        p = portals.get_by_id(pid) if pid else None
        if not p:
            options = [item for item in portals.load_all() if item.get('type') == 'xtream']
            if not options:
                xbmcgui.Dialog().ok('XtreamMate', 'Zuerst einen Xtream-Codes-Zugang einrichten.')
                xbmcplugin.endOfDirectory(self._handle, cacheToDisc=False)
                return
            idx = xbmcgui.Dialog().select('XtreamMate – Portal auswählen',
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
        epg_mgr = self._epg_mgr(p)
        from player import channel_list_item
        now = time.time()
        for ch in chunk:
            prog = epg_mgr.get_current(ch.tvg_id) if epg_mgr else None
            prg  = prog.progress() if prog else 0.0
            li   = channel_list_item(ch, prog, prg)

            if ptype == 'stb':
                play_url  = self.url(action='play_stb_live', pid=p['id'],
                                     cmd=ch.url, name=ch.name, logo=ch.logo)
                cu_action = 'stb_catchup_list'
            else:
                play_url  = self.url(action='play_live', pid=p['id'],
                                     sid=ch.extra.get('stream_id', ''),
                                     url=ch.url, name=ch.name, logo=ch.logo)
                cu_action = 'catchup_list'

            cm = [
                (('Remove from Favourites' if is_favourite(ch.url)
                  else 'Add to Favourites'),
                 f'RunPlugin({self.url(action="toggle_favourite", url=ch.url, name=ch.name, logo=ch.logo, group=ch.group)})'),
                ('EPG',
                 f'Container.Update({self.url(action="epg_channel", pid=p["id"], tvg_id=ch.tvg_id, name=ch.name)})'),
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

        xbmcplugin.addSortMethod(self._handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self._handle, succeeded=True, updateListing=False, cacheToDisc=False)


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
        p = self._portal()
        if not p:
            return
        xbmcplugin.setContent(self._handle, 'videos')
        xbmcplugin.setPluginCategory(self._handle, _L(32014))
        mgr = self._epg_mgr(p)
        if not mgr or not mgr.has_data():
            notify(_L(32006), _L(32044))
            xbmcplugin.endOfDirectory(self._handle)
            return
        now = time.time()
        for cid in list(mgr._programmes.keys())[:200]:
            prog = mgr.get_current(cid, now)
            if prog:
                self._add_dir(
                    f'{mgr.get_channel_name(cid)} – {prog.title}',
                    self.url(action='epg_channel', pid=p['id'],
                             tvg_id=cid, name=mgr.get_channel_name(cid))
                )
        xbmcplugin.endOfDirectory(self._handle)

    def _epg_channel(self):
        p = self._portal()
        if not p:
            return
        tvg_id = self._params.get('tvg_id', '')
        name   = self._params.get('name', tvg_id)
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
        if not url:
            error('play_live: no URL in params')
            notify('XtreamMate', 'Stream URL fehlt')
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return
        # The service displays a transparent on-video TV remote panel. Never
        # put the stream URL or Xtream credentials in the session marker.
        pid = self._params.get('pid', '')
        sid = self._params.get('sid', '')
        if pid and sid:
            import portals as _portals
            p = _portals.get_by_id(pid)
            if p and p.get('type') == 'xtream':
                from live_overlay import announce
                announce(pid, sid, name)
        from player import play_stream
        play_stream(self._handle, url, title=name, logo=logo)

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
        notify('XtreamMate', f'Refreshing {p["name"]}…', duration=1500)
        self._load_channels(p, force=True)
        if p.get('type') == 'xtream':
            from xtream import XtreamClient
            xc = XtreamClient(p['xc_host'], p['xc_user'], p['xc_pass'])
            xc.get_vod_categories(force_refresh=True)
            xc.get_series_categories(force_refresh=True)
        notify('XtreamMate', f'{p["name"]} refreshed')
        xbmc.executebuiltin('Container.Refresh')

    def _refresh_epg(self):
        import portals as P
        pid = self._params.get('pid', '')
        p   = P.get_by_id(pid)
        if not p:
            return
        notify('XtreamMate', 'Refreshing EPG…', duration=1500)
        from epg import ensure_epg_loaded_for_portal
        ensure_epg_loaded_for_portal(p, force=True)
        notify('XtreamMate', 'EPG refreshed')

    def _do_clear_cache(self):
        cache_clear()
        notify('XtreamMate', 'Cache cleared')

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
                notify('XtreamMate', _L(32283))
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
                notify('XtreamMate', _L(32284))
                return
            data = dict(name=name, type='xtream', xc_host=host,
                        xc_user=user, xc_pass=pwd,
                        epg_url=epg_url, epg_show=epg_show, enabled=enabled)
        elif type_idx == 3:
            url = setting('new_portal_stb_url', '').strip()
            mac = setting('new_portal_stb_mac', '00:1A:79:00:00:00').strip()
            if not url or not mac:
                notify('XtreamMate', _L(32285))
                return
            data = dict(name=name, type='stb', stb_url=url, stb_mac=mac,
                        epg_url=epg_url, epg_show=epg_show, enabled=enabled)
        else:
            return

        portals.add(data)
        notify('XtreamMate', _L(32083, name))
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
            notify('XtreamMate', 'Portal not found. Open Portal Manager.')
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
            from epg import load_cache, cache_has_data, warmup_async, _refresh_portal_epg
            portal_id = p.get('id', 'unknown')
            warmup_async(portal_id, p)
            if not cache_has_data(portal_id):
                _refresh_portal_epg(portal_id, p)
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
            cats = {str(c['category_id']): c['category_name']
                    for c in xc.get_live_categories(force_refresh=force)}
            return [
                Channel(
                    name    = s.get('name', ''),
                    url     = xc.live_stream_url(s.get('stream_id', ''), 'ts'),
                    logo    = s.get('stream_icon', ''),
                    group   = cats.get(str(s.get('category_id', '')), 'Uncategorised'),
                    extra   = {'category_id': str(s.get('category_id', ''))},
                    tvg_id  = s.get('epg_channel_id', ''),
                    tvg_name= s.get('name', ''),
                )
                for s in xc.get_live_streams(force_refresh=force)
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
        xbmcplugin.addDirectoryItem(self._handle, url, li, isFolder=is_folder)

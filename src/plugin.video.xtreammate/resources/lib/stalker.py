import json
import time
import re
import hashlib
import random
import string
import urllib.parse
import threading
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from utils import (
    http_get, cache_get, cache_set, cache_key,
    setting, setting_int, setting_bool,
    debug, info, warn, error
)


def _random_serial(length=13):
    return ''.join(random.choices(string.digits, k=length))

def _device_id(mac: str) -> str:
    return hashlib.md5(mac.encode()).hexdigest().upper()

def _device_id2(mac: str) -> str:
    return hashlib.md5((mac + 'extra').encode()).hexdigest().upper()

def _normalise_host(host: str) -> str:
    if not host.startswith(('http://', 'https://')):
        host = 'http://' + host
    return host.rstrip('/')

def _strip_portal_suffix(host: str) -> str:
    for sfx in ('/stalker_portal/c/', '/stalker_portal/c',
                '/stalker_portal/', '/stalker_portal',
                '/c/', '/c'):
        if host.endswith(sfx):
            return host[:-len(sfx)]
    return host

def _clean_stream_url(raw: str) -> str:
    if not raw:
        return ''
    raw = raw.strip()
    for pfx in ('ffmpeg ', 'shell ', 'vlc ', 'FFMPEG ', 'VLC '):
        if raw.startswith(pfx):
            raw = raw[len(pfx):].strip()
    if raw.startswith('http%3A') or raw.startswith('rtmp%3A'):
        raw = urllib.parse.unquote(raw)
    return raw


def _normalize_itv_cmd(cmd: str) -> str:
    clean = _clean_stream_url(cmd)
    if urllib.parse.urlsplit(clean).hostname == 'localhost':
        return cmd
    m = re.search(r'(\d+)[^\d/]*$', clean)
    if not m:
        return cmd
    return 'ffmpeg http://localhost/ch/' + m.group(1)


def _token_cache_key(mac: str, portal: str) -> str:
    return 'stb_token_' + hashlib.md5(f'{mac}|{portal}'.encode()).hexdigest()

def _mode_cache_key(mac: str, portal: str) -> str:
    return 'stb_mode_' + hashlib.md5(f'{mac}|{portal}'.encode()).hexdigest()

def _load_cached_token(mac: str, portal: str):
    data = cache_get(_token_cache_key(mac, portal), max_age=6 * 3600)
    if data and data.get('token'):
        return data['token'], data.get('serial', _random_serial())
    return None, None

def _save_token(mac: str, portal: str, token: str, serial: str):
    cache_set(_token_cache_key(mac, portal), {'token': token, 'serial': serial})

def _save_mode(mac: str, portal: str, compat: bool):
    cache_set(_mode_cache_key(mac, portal), {'compat': compat})

def _load_mode(mac: str, portal: str):
    data = cache_get(_mode_cache_key(mac, portal), max_age=24 * 3600)
    if data is not None:
        return data.get('compat', False)
    return None


class StalkerClient:

    PORTAL_PATH = '/portal.php'

    CACHE_TTL = {
        'get_genres'        : 3600 * 24,
        'get_ordered_list'  : 3600 * 6,
        'get_categories'    : 3600 * 24,
        'vod_list'          : 3600 * 6,
        'series_categories' : 3600 * 24,
        'series_list'       : 3600 * 6,
        'series_seasons'    : 3600 * 6,
        'series_episodes'   : 3600 * 6,
        'epg_info'          : 900,
        'short_epg'         : 900,
    }

    STB_UA = ('Mozilla/5.0 (QtEmbedded; U; Linux; C) '
              'AppleWebKit/533.3 (KHTML, like Gecko) '
              'MAG200 stbapp ver: 2 rev: 250 Safari/533.3')

    def __init__(self, portal_url: str, mac: str):
        host          = _strip_portal_suffix(_normalise_host(portal_url))
        self._base    = host
        self._portal  = host + self.PORTAL_PATH
        self._mac     = mac.upper().strip()
        self._token   = None
        self._serial  = _random_serial()
        self._dev_id  = _device_id(self._mac)
        self._dev_id2 = _device_id2(self._mac)
        self._authed  = False
        tok, ser = _load_cached_token(self._mac, self._portal)
        if tok:
            self._token  = tok
            self._serial = ser
            self._authed = True
            debug(f'STB: restored token from cache for {self._mac}')

    def _headers(self, with_auth: bool = True) -> dict:
        ua = setting('user_agent', self.STB_UA)
        h  = {
            'User-Agent'     : ua,
            'Accept'         : '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'X-User-Agent'   : 'Model: MAG250; Link: WiFi',
            'Cookie'         : (f'mac={self._mac}; stb_lang=en; '
                                f'timezone=UTC; token={self._token or ""}'),
        }
        if with_auth and self._token:
            h['Authorization'] = f'Bearer {self._token}'
        return h

    def stream_headers(self) -> dict:
        return {
            'User-Agent' : self.STB_UA,
            'Cookie'     : f'mac={self._mac}',
            'Referer'    : self._base + '/',
        }

    def _get(self, params: dict, ck: str = None,
             ttl: int = 3600, force: bool = False,
             skip_cache: bool = False):
        if ck and not force and not skip_cache:
            cached = cache_get(cache_key(ck), max_age=ttl)
            if cached is not None:
                return cached
        try:
            raw, _ = http_get(self._portal, params=params,
                              headers=self._headers())
            if isinstance(raw, (bytes, bytearray)):
                if raw[:2] == b'\x1f\x8b':
                    import gzip as _gzip
                    raw = _gzip.decompress(raw)
                raw = raw.decode('utf-8', errors='replace')
            data = json.loads(raw)
        except Exception as e:
            error(f'STB _get({params.get("action","?")}): {e}')
            return {}
        if ck and not skip_cache:
            cache_set(cache_key(ck), data)
        return data

    def authenticate(self, force: bool = False) -> bool:
        if self._authed and not force:
            return True

        info(f'STB auth: MAC={self._mac}  portal={self._portal}')

        try:
            raw, _ = http_get(self._portal, headers=self._headers(with_auth=False),
                              params={
                                  'type'         : 'stb',
                                  'action'       : 'handshake',
                                  'prehash'      : '0',
                                  'token'        : '',
                                  'JsHttpRequest': '1-xml',
                              })
            data = json.loads(raw)
        except Exception as e:
            error(f'STB handshake failed: {e}')
            return False

        js    = data.get('js', {}) if isinstance(data, dict) else {}
        token = js.get('token', '')
        if not token:
            error(f'STB handshake: no token. Response: {str(data)[:200]}')
            return False

        self._token = token
        debug(f'STB: token={token[:20]}…')
        try:
            raw2, _ = http_get(self._portal, headers=self._headers(),
                               params={
                                   'type'            : 'stb',
                                   'action'          : 'get_profile',
                                   'hd'              : '1',
                                   'ver'             : ('ImageDescription: 0.2.18-r23-pub-250; '
                                                        'ImageDate: Wed Mar 9 17:28:54 EET 2022; '
                                                        'PORTAL version: 6.2.0; '
                                                        'API Version: JS API version: 343'),
                                   'num_banks'       : '2',
                                   'sn'              : self._serial,
                                   'stb_type'        : 'MAG250',
                                   'image_version'   : '218',
                                   'device_id'       : self._dev_id,
                                   'device_id2'      : self._dev_id2,
                                   'signature'       : '',
                                   'auth_second_step': '1',
                                   'hw_version'      : '1.7-BD-00',
                                   'JsHttpRequest'   : '1-xml',
                               })
        except Exception as e:
            warn(f'STB get_profile failed (non-fatal): {e}')

        self._authed = True
        _save_token(self._mac, self._portal, token, self._serial)
        info('STB: authenticated')
        return True

    def _create_link(self, cmd: str, content_type: str = 'itv',
                     ch_start: int = 0, ch_stop: int = 0) -> str:
        if not self.authenticate():
            return ''

        clean = _clean_stream_url(cmd)
        if clean.startswith(('http://', 'https://', 'rtmp://', 'rtsp://')):
            fallback = clean
        else:
            fallback = ''

        send_cmd = _normalize_itv_cmd(cmd) if content_type == 'itv' else cmd

        params = {
            'type'               : content_type,
            'action'             : 'create_link',
            'cmd'                : send_cmd,
            'series'             : '0',
            'forced_storage'     : 'undefined',
            'disable_ad'         : '0',
            'download'           : '0',
            'force_ch_link_check': '0',
            'JsHttpRequest'      : '1-xml',
        }
        if ch_start and ch_stop:
            params['ch_start'] = str(ch_start)
            params['ch_stop']  = str(ch_stop)

        try:
            raw, _ = http_get(self._portal, params=params,
                              headers=self._headers(),
                              timeout=15)
            data = json.loads(raw)
        except Exception as e:
            error(f'STB create_link: {e}')
            return fallback

        js  = data.get('js', {}) if isinstance(data, dict) else {}
        lnk = js.get('cmd', '') if isinstance(js, dict) else ''
        url = _clean_stream_url(lnk)

        if not url:
            warn(f'STB create_link returned empty url, fallback={fallback}')
            return fallback

        debug(f'STB create_link resolved: {url[:80]}')
        return url

    def get_channel_stream_url(self, cmd: str) -> str:
        return self._create_link(cmd, content_type='itv')

    def get_vod_stream_url(self, cmd: str) -> str:
        return self._create_link(cmd, content_type='vod')

    def get_episode_stream_url(self, cmd: str) -> str:
        return self._create_link(cmd, content_type='series')

    def get_catchup_url(self, cmd: str, start_ts: int, stop_ts: int) -> str:
        return self._create_link(cmd, content_type='itv',
                                 ch_start=start_ts, ch_stop=stop_ts)

    def get_live_categories(self, force: bool = False) -> list:
        if not self.authenticate():
            return []
        data = self._get({'type': 'itv', 'action': 'get_genres',
                          'JsHttpRequest': '1-xml'},
                         ck=f'stb_genres_{self._mac}',
                         ttl=self.CACHE_TTL['get_genres'], force=force)
        js = data.get('js', []) if isinstance(data, dict) else []
        return js if isinstance(js, list) else []

    def get_all_channels(self, force: bool = False) -> list:
        if not self.authenticate():
            return []
        data = self._get(
            {'type': 'itv', 'action': 'get_all_channels', 'JsHttpRequest': '1-xml'},
            ck=f'stb_allch_{self._mac}', ttl=self.CACHE_TTL['get_ordered_list'], force=force
        )
        if not isinstance(data, dict):
            return []
        js = data.get('js', data)
        if isinstance(js, dict) and 'data' in js:
            return js['data'] if isinstance(js['data'], list) else []
        return js if isinstance(js, list) else []

    def get_live_channels(self, genre_id: str = '*',
                          force: bool = False) -> list:
        if not self.authenticate():
            return []
        if genre_id == '*':
            channels = self.get_all_channels(force=force)
            if channels:
                return channels
        return self._get_all_pages(
            {'type': 'itv', 'action': 'get_ordered_list',
             'genre': genre_id, 'force_ch_link_check': '0',
             'fav': '0', 'sortby': 'name', 'hd': '0'},
            ck_prefix=f'stb_ch_{self._mac}_{genre_id}',
            ttl=self.CACHE_TTL['get_ordered_list'], force=force
        )

    def get_vod_categories(self, force: bool = False) -> list:
        if not self.authenticate():
            return []
        data = self._get({'type': 'vod', 'action': 'get_categories',
                          'JsHttpRequest': '1-xml'},
                         ck=f'stb_vodcats_{self._mac}',
                         ttl=self.CACHE_TTL['get_categories'], force=force)
        js = data.get('js', []) if isinstance(data, dict) else []
        return js if isinstance(js, list) else []

    def get_vod(self, category_id: str = '*',
                force: bool = False) -> list:
        if not self.authenticate():
            return []
        return self._get_all_pages(
            {'type': 'vod', 'action': 'get_ordered_list',
             'category': category_id, 'sortby': 'name', 'fav': '0'},
            ck_prefix=f'stb_vod_{self._mac}_{category_id}',
            ttl=self.CACHE_TTL['vod_list'], force=force
        )

    def get_series_categories(self, force: bool = False) -> list:
        if not self.authenticate():
            return []
        data = self._get({'type': 'series', 'action': 'get_categories',
                          'JsHttpRequest': '1-xml'},
                         ck=f'stb_seriescats_{self._mac}',
                         ttl=self.CACHE_TTL['series_categories'], force=force)
        js = data.get('js', []) if isinstance(data, dict) else []
        return js if isinstance(js, list) else []

    def get_series(self, category_id: str = '*',
                   force: bool = False) -> list:
        if not self.authenticate():
            return []
        return self._get_all_pages(
            {'type': 'series', 'action': 'get_ordered_list',
             'category': category_id, 'sortby': 'name', 'fav': '0'},
            ck_prefix=f'stb_series_{self._mac}_{category_id}',
            ttl=self.CACHE_TTL['series_list'], force=force
        )

    def get_series_seasons(self, movie_id: str,
                           force: bool = False) -> list:
        if not self.authenticate():
            return []
        data = self._get(
            {'type': 'series', 'action': 'get_ordered_list',
             'movie_id': movie_id, 'season_id': '0', 'episode_id': '0',
             'JsHttpRequest': '1-xml'},
            ck=f'stb_seasons_{self._mac}_{movie_id}',
            ttl=self.CACHE_TTL['series_seasons'], force=force
        )
        js = data.get('js', {}) if isinstance(data, dict) else {}
        return js.get('data', []) if isinstance(js, dict) else []

    def get_series_episodes(self, movie_id: str, season_id: str,
                            force: bool = False) -> list:
        if not self.authenticate():
            return []
        data = self._get(
            {'type': 'series', 'action': 'get_ordered_list',
             'movie_id': movie_id, 'season_id': season_id,
             'episode_id': '0', 'JsHttpRequest': '1-xml'},
            ck=f'stb_eps_{self._mac}_{movie_id}_{season_id}',
            ttl=self.CACHE_TTL['series_episodes'], force=force
        )
        js = data.get('js', {}) if isinstance(data, dict) else {}
        return js.get('data', []) if isinstance(js, dict) else []

    def get_short_epg(self, ch_id: str, count: int = 5,
                      force: bool = False) -> list:
        if not self.authenticate():
            return []
        data = self._get(
            {'type': 'itv', 'action': 'get_short_epg',
             'ch_id': ch_id, 'count': count, 'JsHttpRequest': '1-xml'},
            ck=f'stb_shepg_{self._mac}_{ch_id}',
            ttl=self.CACHE_TTL['short_epg'], force=force
        )
        js = data.get('js', {}) if isinstance(data, dict) else {}
        return js.get('data', []) if isinstance(js, dict) else []

    def get_account_info(self) -> dict:
        if not self.authenticate():
            return {}
        data = self._get(
            {'type': 'account_info', 'action': 'get_main_info',
             'JsHttpRequest': '1-xml'},
            ck=f'stb_acct_{self._mac}', ttl=300
        )
        return data.get('js', {}) if isinstance(data, dict) else {}

    def search_live(self, query: str) -> list:
        q = query.lower()
        return [c for c in self.get_live_channels()
                if q in c.get('name', '').lower()]

    def search_vod(self, query: str) -> list:
        if not self.authenticate():
            return []
        return self._get_all_pages(
            {'type': 'vod', 'action': 'get_ordered_list',
             'category': '*', 'sortby': 'name',
             'fav': '0', 'search': query},
            ck_prefix=f'stb_vsrch_{self._mac}_{query}',
            ttl=300, force=True
        )

    def search_series(self, query: str) -> list:
        q = query.lower()
        return [s for s in self.get_series()
                if q in s.get('name', '').lower()]

    def _parse_page(self, data: dict):
        js = data.get('js', {}) if isinstance(data, dict) else {}
        if isinstance(js, dict):
            items = js.get('data', [])
            total = int(js.get('total_items', js.get('total', len(items))) or 0)
        elif isinstance(js, list):
            items = js
            total = len(items)
        else:
            items = []
            total = 0
        return items, total

    def _get_all_pages(self, params: dict, ck_prefix: str,
                       ttl: int = 3600, force: bool = False) -> list:
        pp0   = {**params, 'p': 0, 'JsHttpRequest': '1-xml'}
        data0 = self._get(pp0, ck=f'{ck_prefix}_p0', ttl=ttl, force=force)
        items0, total = self._parse_page(data0)
        if not items0:
            return []

        items_per_page = len(items0)
        if total <= items_per_page:
            return items0

        remaining_pages = []
        collected = items_per_page
        page = 1
        while collected < total and page <= 50:
            remaining_pages.append(page)
            collected += items_per_page
            page += 1

        if not remaining_pages:
            return items0

        lock    = threading.Lock()
        results = {0: items0}

        def _fetch_page(pg):
            pp   = {**params, 'p': pg, 'JsHttpRequest': '1-xml'}
            data = self._get(pp, ck=f'{ck_prefix}_p{pg}', ttl=ttl, force=force)
            items, _ = self._parse_page(data)
            with lock:
                results[pg] = items

        workers = min(10, len(remaining_pages))
        with ThreadPoolExecutor(max_workers=workers) as ex:
            list(ex.map(_fetch_page, remaining_pages))

        all_items = []
        for pg in sorted(results):
            all_items.extend(results[pg])
        return all_items


class StalkerClientCompat(StalkerClient):
    """
    Fallback für STB-Portale die keinen MAG-Handshake erwarten:
    - Chrome/147 UA
    - MAC als URL-Query-Parameter (kein Cookie / Authorization)
    - Kein Handshake / get_profile
    - create_link: minimale Parameter (kein series/forced_storage/etc.)
    - get_short_epg: periode= statt count=, js ist direkt eine Liste
    """

    CHROME_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/147.0.0.0 Safari/537.36')

    def _host(self) -> str:
        return self._base.replace('http://', '').replace('https://', '').split('/')[0]

    def _headers(self, with_auth: bool = True) -> dict:
        return {
            'Host'                     : self._host(),
            'Connection'               : 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent'               : self.CHROME_UA,
            'Accept'                   : ('text/html,application/xhtml+xml,'
                                          'application/xml;q=0.9,image/avif,'
                                          'image/webp,image/apng,*/*;q=0.8,'
                                          'application/signed-exchange;v=b3;q=0.7'),
            'Accept-Language'          : 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding'          : 'gzip, deflate',
        }

    def stream_headers(self) -> dict:
        return {
            'User-Agent': self.CHROME_UA,
            'Referer'   : self._base + '/',
            'Connection': 'keep-alive',
        }

    def _get(self, params: dict, ck: str = None,
             ttl: int = 3600, force: bool = False,
             skip_cache: bool = False):
        return super()._get(
            {**params, 'mac': self._mac},
            ck=ck, ttl=ttl, force=force, skip_cache=skip_cache
        )

    def authenticate(self, force: bool = False) -> bool:
        self._authed = True
        return True

    def _create_link(self, cmd: str, content_type: str = 'itv',
                     ch_start: int = 0, ch_stop: int = 0) -> str:
        send_cmd = _normalize_itv_cmd(cmd) if content_type == 'itv' else cmd
        params = {
            'type'         : content_type,
            'action'       : 'create_link',
            'cmd'          : send_cmd,
            'JsHttpRequest': '1-xml',
        }
        if ch_start and ch_stop:
            params['ch_start'] = str(ch_start)
            params['ch_stop']  = str(ch_stop)
        try:
            raw, _ = http_get(self._portal, params={**params, 'mac': self._mac},
                              headers=self._headers(), timeout=15)
            if isinstance(raw, (bytes, bytearray)):
                if raw[:2] == b'\x1f\x8b':
                    import gzip as _gzip
                    raw = _gzip.decompress(raw)
                raw = raw.decode('utf-8', errors='replace')
            data = json.loads(raw)
        except Exception as e:
            error(f'STB compat create_link: {e}')
            return ''
        js  = data.get('js', {}) if isinstance(data, dict) else {}
        lnk = js.get('cmd', '') if isinstance(js, dict) else ''
        url = _clean_stream_url(lnk)
        if not url:
            warn('STB compat create_link: empty url')
        else:
            debug(f'STB compat create_link resolved: {url[:80]}')
        return url

    def get_short_epg(self, ch_id: str, count: int = 5,
                      force: bool = False) -> list:
        data = self._get(
            {'type': 'itv', 'action': 'get_short_epg',
             'ch_id': ch_id, 'periode': count, 'JsHttpRequest': '1-xml'},
            ck=f'stb_shepg_c_{self._mac}_{ch_id}',
            ttl=self.CACHE_TTL['short_epg'], force=force
        )
        js = data.get('js', []) if isinstance(data, dict) else []
        if isinstance(js, list):
            return js
        if isinstance(js, dict):
            return js.get('data', [])
        return []


def client_for_portal(p: dict) -> Optional['StalkerClient']:
    url = p.get('stb_url', '')
    mac = p.get('stb_mac', '')
    if not url or not mac:
        return None

    portal_url = _strip_portal_suffix(_normalise_host(url)) + StalkerClient.PORTAL_PATH
    cached_mode = _load_mode(mac.upper(), portal_url)

    if cached_mode is True:
        info(f'STB: using cached compat mode for {url}')
        return StalkerClientCompat(url, mac)

    if cached_mode is False:
        return StalkerClient(url, mac)

    client = StalkerClient(url, mac)
    if client._authed:
        _save_mode(mac.upper(), portal_url, False)
        return client

    if client.authenticate():
        _save_mode(mac.upper(), portal_url, False)
        return client

    warn(f'STB: standard auth failed for {url}, switching to compat mode')
    _save_mode(mac.upper(), portal_url, True)
    return StalkerClientCompat(url, mac)

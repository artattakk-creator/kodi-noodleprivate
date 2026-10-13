import json
import time
from urllib.parse import urljoin

from utils import (
    http_get, cache_get, cache_set, cache_key,
    setting_int, debug, error, info, warn
)


class XtreamClient:
    CACHE_TTL = {
        'live_streams'       : 3600 * 12,
        'live_categories'    : 3600 * 24,
        'vod_streams'        : 3600 * 12,
        'vod_categories'     : 3600 * 24,
        'series'             : 3600 * 12,
        'series_categories'  : 3600 * 24,
        'series_info'        : 3600 * 6,
        'vod_info'           : 3600 * 6,
        'epg'                : 3600 * 2,
        'short_epg'          : 900,
    }

    def __init__(self, host: str, username: str, password: str):
        if not host.startswith(('http://', 'https://')):
            host = 'http://' + host
        if not host.endswith('/'):
            host += '/'
        self.host     = host
        self.username = username
        self.password = password
        self._info    = None

    def _api_url(self):
        return urljoin(self.host, 'player_api.php')

    def _base_params(self):
        return {'username': self.username, 'password': self.password}

    def _get_json(self, action, extra=None, force_refresh=False, ttl=None):
        params = {**self._base_params(), 'action': action, **(extra or {})}
        ck     = cache_key(json.dumps(params, sort_keys=True))
        age    = ttl or self.CACHE_TTL.get(action, 3600)

        if not force_refresh:
            cached = cache_get(ck, max_age=age)
            if cached is not None:
                return cached

        try:
            raw, _ = http_get(self._api_url(), params=params)
            data   = json.loads(raw)
            cache_set(ck, data)
            return data
        except Exception as e:
            error('Xtream API {} request failed: {}'.format(action, type(e).__name__))
            return None

    def authenticate(self):
        if self._info:
            return self._info
        data = self._get_json('', extra={})
        try:
            params = self._base_params()
            raw, _ = http_get(self._api_url(), params=params)
            self._info = json.loads(raw)
            return self._info
        except Exception as e:
            error('Xtream authentication request failed: {}'.format(type(e).__name__))
            return None

    def get_server_info(self):
        info_data = self.authenticate()
        return (info_data or {}).get('server_info', {})

    def get_user_info(self):
        info_data = self.authenticate()
        return (info_data or {}).get('user_info', {})

    def is_valid(self):
        ui = self.get_user_info()
        return ui.get('auth') == 1

    def get_live_categories(self, force_refresh=False):
        return self._get_json('get_live_categories', force_refresh=force_refresh) or []

    def get_live_streams(self, category_id=None, force_refresh=False):
        extra = {}
        if category_id:
            extra['category_id'] = category_id
        return self._get_json('get_live_streams', extra=extra,
                              force_refresh=force_refresh) or []

    def live_stream_url(self, stream_id, ext='ts'):
        return f'{self.host}live/{self.username}/{self.password}/{stream_id}.{ext}'

    def get_vod_categories(self, force_refresh=False):
        return self._get_json('get_vod_categories', force_refresh=force_refresh) or []

    def get_vod_streams(self, category_id=None, force_refresh=False):
        extra = {}
        if category_id:
            extra['category_id'] = category_id
        return self._get_json('get_vod_streams', extra=extra,
                              force_refresh=force_refresh) or []

    def get_vod_info(self, vod_id, force_refresh=False):
        return self._get_json('get_vod_info', extra={'vod_id': vod_id},
                              force_refresh=force_refresh) or {}

    def vod_stream_url(self, stream_id, ext='mkv'):
        return f'{self.host}movie/{self.username}/{self.password}/{stream_id}.{ext}'

    def get_series_categories(self, force_refresh=False):
        return self._get_json('get_series_categories', force_refresh=force_refresh) or []

    def get_series(self, category_id=None, force_refresh=False):
        extra = {}
        if category_id:
            extra['category_id'] = category_id
        return self._get_json('get_series', extra=extra,
                              force_refresh=force_refresh) or []

    def get_series_info(self, series_id, force_refresh=False):
        return self._get_json('get_series_info', extra={'series_id': series_id},
                              force_refresh=force_refresh) or {}

    def series_episode_url(self, stream_id, ext='mkv'):
        return f'{self.host}series/{self.username}/{self.password}/{stream_id}.{ext}'

    def get_epg(self, stream_id=None, limit=None, force_refresh=False):
        """Full EPG (XML) – expensive; use short_epg for per-channel."""
        extra = {}
        if stream_id:
            extra['stream_id'] = stream_id
        if limit:
            extra['limit'] = limit
        return self._get_json('get_short_epg', extra=extra,
                              force_refresh=force_refresh) or {}

    def get_short_epg(self, stream_id, limit=4, force_refresh=False):
        return self._get_json('get_short_epg',
                              extra={'stream_id': stream_id, 'limit': limit},
                              force_refresh=force_refresh) or {}

    def get_xmltv_epg_url(self):
        return f'{self.host}xmltv.php?username={self.username}&password={self.password}'

    def catchup_url(self, stream_id, start_ts, stop_ts, ext='ts'):
        duration = max(1, (stop_ts - start_ts) // 60)
        import datetime
        dt = datetime.datetime.utcfromtimestamp(start_ts)
        ts_str = dt.strftime('%Y-%m-%d_%H-%M-%S')
        return (f'{self.host}timeshift/{self.username}/{self.password}/'
                f'{duration}/{ts_str}/{stream_id}.{ext}')

    def search_live(self, query):
        q = query.lower()
        return [s for s in self.get_live_streams()
                if q in s.get('name', '').lower()]

    def search_vod(self, query):
        q = query.lower()
        return [s for s in self.get_vod_streams()
                if q in s.get('name', '').lower()]

    def search_series(self, query):
        q = query.lower()
        return [s for s in self.get_series()
                if q in s.get('name', '').lower()]


def client_for_playlist(idx: int):
    from utils import setting
    pfx  = f'playlist{idx}_'
    host = setting(pfx + 'xc_host')
    user = setting(pfx + 'xc_user')
    pwd  = setting(pfx + 'xc_pass')
    if not host or not user:
        return None
    return XtreamClient(host, user, pwd)


def client_is_configured(idx: int):
    from utils import setting
    return bool(setting(f'playlist{idx}_xc_host') and
                setting(f'playlist{idx}_xc_user'))

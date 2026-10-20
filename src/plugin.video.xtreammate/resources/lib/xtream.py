import json
import time
from urllib.parse import urljoin

from utils import (
    http_get, cache_get, cache_set, cache_key,
    setting_int, debug, error, info, warn
)


class XtreamClient:
    CACHE_TTL = {
        'get_live_streams': 3600 * 12,
        'get_live_categories': 3600 * 24,
        'get_vod_streams': 3600 * 12,
        'get_vod_categories': 3600 * 24,
        'get_series': 3600 * 12,
        'get_series_categories': 3600 * 24,
        'get_series_info': 3600 * 6,
        'get_vod_info': 3600 * 6,
        'get_epg': 3600 * 2,
        'get_short_epg': 900,
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

    # A slightly stale local index is preferable to a 30-second server roundtrip
    # whenever the user opens a TV channel list. Forced refreshes ignore it.
    STALE_GRACE_SECONDS = 30 * 86400

    def _cache_key(self, action, extra=None):
        # Include origin and credentials; two unrelated portals can share the
        # same username/password. Only a digest becomes a filename.
        params = {**self._base_params(), 'action': action, **(extra or {})}
        return cache_key(json.dumps({'origin': self._api_url(), 'query': params},
                                    sort_keys=True, separators=(',', ':')))

    def _get_json(self, action, extra=None, force_refresh=False, ttl=None,
                  cached_only=False):
        params = {**self._base_params(), 'action': action, **(extra or {})}
        ck = self._cache_key(action, extra)
        age = self.CACHE_TTL.get(action, 3600) if ttl is None else ttl
        if not force_refresh:
            cached = cache_get(ck, max_age=age)
            if cached is not None:
                return cached
            # Never hold up the Kodi GUI waiting for a catalog refresh when a
            # previous scan has already downloaded the same provider index.
            stale = cache_get(ck, max_age=self.STALE_GRACE_SECONDS)
            if stale is not None:
                return stale
        if cached_only:
            return None
        try:
            limits=dict(timeout=3,max_bytes=2*1024*1024,max_seconds=8) if action=='get_short_epg' else {}
            raw, _ = http_get(self._api_url(), params=params,**limits)
            data = json.loads(raw)
            if data is not None:
                cache_set(ck, data)
                if action in ('get_vod_streams', 'get_series') and not extra and isinstance(data, list):
                    try:
                        from latest_media import observe
                        observe(ck, action, data)
                    except Exception as exc:
                        warn('Xtream recent catalog update: {}'.format(type(exc).__name__))
            return data
        except Exception as exc:
            error('Xtream API {} request failed: {}'.format(action, type(exc).__name__))
            return None

    def iter_catalog(self, action, category_id=None, cached_only=False, cancel=lambda:False):
        """Stream a category response. Never deserialize the global cache to filter.

        Providers ignoring category_id are tolerated: every row is locally checked
        by the transactional index writer. The discarded count diagnoses support.
        Existing global JSON files are streamed as an offline migration fallback.
        """
        import os
        from utils import cache_dir, _private_cache_dir
        from streaming_json import iter_array
        extra = {'category_id':str(category_id)} if category_id is not None else {}
        if cached_only:
            for root in dict.fromkeys((cache_dir(),_private_cache_dir())):
                filename = os.path.join(root,self._cache_key(action,extra)+'.json')
                if not os.path.isfile(filename) and extra:
                    filename = os.path.join(root,self._cache_key(action)+'.json')
                if os.path.isfile(filename):
                    # cache_set stores {ts,data}, inspect without loading the array.
                    with open(filename,'rb') as stream:
                        from streaming_json import cached_array
                        yield from cached_array(stream,cancel)
                    return
            raise FileNotFoundError('No local catalogue snapshot')
        from utils import http_stream
        params = {**self._base_params(),'action':action,**extra}
        with http_stream(self._api_url(),params=params,cancel=cancel) as stream:
            yield from iter_array(stream,cancel)

    def _local_portal(self):
        try:
            from portals import get_active
            return next((p for p in get_active() if p.get('type')=='xtream'
                and p.get('xc_user')==self.username and p.get('xc_pass')==self.password
                and (str(p.get('xc_host','')) if str(p.get('xc_host','')).startswith(('http://','https://')) else 'http://'+str(p.get('xc_host',''))).rstrip('/')==self.host.rstrip('/')),None)
        except (ImportError,AttributeError): return None

    def _indexed_live(self,category_id=None):
        portal=self._local_portal()
        if not portal: return None
        from library_index import Reader
        reader=Reader(portal['id'])
        if not reader.state('live'): return None
        result=[];offset=0
        while True:
            rows,total=reader.page('live',category=category_id,offset=offset,limit=100)
            result.extend(dict(row,stream_id=row['sid']) for row in rows)
            offset+=len(rows)
            if not rows or offset>=total: return result

    def is_cached_live_id(self,sid):
        portal=self._local_portal()
        if portal:
            from library_index import Reader
            reader=Reader(portal['id'])
            if reader.state('live'): return reader.get('live',sid) is not None
        streams=self.get_cached_catalog('get_live_streams') or []
        return any(str(r.get('stream_id'))==str(sid) for r in streams if isinstance(r,dict))

    def get_cached_catalog(self, action):
        """Never use the network (especially from Kodi's UI/service loop)."""
        if action=='get_live_streams':
            indexed=self._indexed_live()
            if indexed is not None: return indexed
        if action not in ('get_live_categories', 'get_live_streams',
                          'get_vod_categories', 'get_vod_streams',
                          'get_series_categories', 'get_series'):
            raise ValueError('Not a supported catalog: ' + str(action))
        return self._get_json(action, cached_only=True)

    def warm_catalogs(self, include_live=True, include_vod=True,
                      include_series=True, force=False):
        """Called only in a background worker; preloads index files on disk."""
        portal=self._local_portal()
        if portal:
            from catalog_sync import request
            for kind,enabled in (('live',include_live),('vod',include_vod),('series',include_series)):
                if enabled: request(portal,kind,portal.get('start_group_id','') if kind=='live' else '',priority=20,force=force)
            return
        actions = []
        if include_live:
            actions += ['get_live_categories', 'get_live_streams']
        if include_vod:
            actions += ['get_vod_categories', 'get_vod_streams']
        if include_series:
            actions += ['get_series_categories', 'get_series']
        for action in actions:
            if force or cache_get(self._cache_key(action),
                                  max_age=self.CACHE_TTL.get(action, 3600)) is None:
                # Do not invalidate existing good data when refresh fails.
                self._get_json(action, force_refresh=True)


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
        if not force_refresh:
            indexed=self._indexed_live(category_id)
            if indexed is not None: return indexed
        if category_id is not None and not force_refresh:
            all_streams = self.get_cached_catalog('get_live_streams')
            if isinstance(all_streams, list):
                return [s for s in all_streams if
                        str(s.get('category_id', '')) == str(category_id)]
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
        if category_id is not None and not force_refresh:
            all_movies = self.get_cached_catalog('get_vod_streams')
            if isinstance(all_movies, list):
                return [v for v in all_movies if
                        str(v.get('category_id', '')) == str(category_id)]
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
        if category_id is not None and not force_refresh:
            all_series = self.get_cached_catalog('get_series')
            if isinstance(all_series, list):
                return [v for v in all_series if
                        str(v.get('category_id', '')) == str(category_id)]
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

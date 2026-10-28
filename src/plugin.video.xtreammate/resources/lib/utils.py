import os
import sys
import json
import time
import hashlib
import logging
import uuid
from network_io import read_http_chunks, MAX_HTTP_BYTES

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

# Transport imports belong to the first network request, never menu startup.
# None means unresolved; tests/older callers can still select either backend.
HAVE_HTTPX = None
httpx = None


def _httpx_available():
    global HAVE_HTTPX, httpx
    if HAVE_HTTPX is not False and httpx is None:
        try:
            import httpx as transport
            httpx = transport
            HAVE_HTTPX = True
        except ImportError:
            HAVE_HTTPX = False
    return bool(HAVE_HTTPX)

ADDON    = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_VER= ADDON.getAddonInfo('version')


def log(msg, level=xbmc.LOGDEBUG):
    xbmc.log(f'[{ADDON_ID}] {msg}', level=level)

def debug(msg):  log(msg, xbmc.LOGDEBUG)
def info(msg):   log(msg, xbmc.LOGINFO)
def warn(msg):   log(msg, xbmc.LOGWARNING)
def error(msg):  log(msg, xbmc.LOGERROR)

def setting(key, default=''):
    try:
        return ADDON.getSetting(key) or default
    except Exception:
        return default

def setting_bool(key, default=False):
    try:
        v = ADDON.getSetting(key)
        return v.lower() == 'true' if v else default
    except Exception:
        return default

def setting_int(key, default=0):
    try:
        return int(ADDON.getSetting(key) or default)
    except Exception:
        return default

_CACHE_WRITABLE = {}


def _private_cache_dir():
    path = xbmcvfs.translatePath(f'special://userdata/addon_data/{ADDON_ID}/cache/')
    xbmcvfs.mkdirs(path)
    return path


def _cache_is_writable(path):
    if time.monotonic() - _CACHE_WRITABLE.get(path, float('-inf')) < 30:
        return True
    probe = os.path.join(path, '.xcmate-probe-' + uuid.uuid4().hex)
    created = False
    try:
        if not (xbmcvfs.exists(path) or xbmcvfs.mkdirs(path)):
            return False
        with xbmcvfs.File(probe, 'w') as stream:
            created = True
            if not stream.write('XCMate cache probe'):
                return False
        _CACHE_WRITABLE[path] = time.monotonic()
        return True
    except Exception:
        return False
    finally:
        if created:
            xbmcvfs.delete(probe)


def cache_dir():
    """Use the selected Kodi folder, falling back to the add-on-owned cache.

    The folder picker persists cache_dir in Kodi. Never erase other user files.
    Missing or inaccessible custom locations must not stop XCMate from starting.
    """
    selected = (setting('cache_dir') or '').strip()
    if selected:
        try:
            path = (xbmcvfs.translatePath(selected)
                    if selected.startswith('special://') else selected)
            if _cache_is_writable(path):
                return path
        except Exception:
            pass
        warn('Configured XCMate cache directory unavailable; using private default')
    return _private_cache_dir()

def addon_data_dir():
    path = xbmcvfs.translatePath(f'special://userdata/addon_data/{ADDON_ID}/')
    # This is a local, translated Kodi profile. Avoid redundant VFS mutations
    # during every read and every concurrent plugin invocation.
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    return path

def _build_proxy():
    proxy_url = setting('proxy_url')
    if not proxy_url:
        return None
    user = setting('proxy_user')
    pwd  = setting('proxy_pass')
    if user and pwd:
        from urllib.parse import urlparse, urlunparse
        p = urlparse(proxy_url)
        proxy_url = urlunparse(p._replace(netloc=f'{user}:{pwd}@{p.netloc}'))
    return proxy_url

def _default_headers():
    return {
        'User-Agent': setting('user_agent',
            'Mozilla/5.0 (Linux; Android 11; TV) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'),
        'Accept-Encoding': 'gzip, deflate',
    }

def http_get(url, params=None, headers=None, timeout=None, stream=False,
             max_bytes=MAX_HTTP_BYTES, max_seconds=60, retry_limit=None):
    from network_io import service_cancelled,service_timeout
    to=service_timeout(timeout or setting_int('http_timeout',15))
    retries = setting_int('max_retries', 3) if retry_limit is None else max(0,min(3,int(retry_limit)))
    wizard48=sys.modules.get('wizard_deadline48')
    if wizard48 is not None:
        to,max_seconds,retries=wizard48.policy(to,max_seconds,retries)
        max_bytes=wizard48.byte_limit(max_bytes)
    verify  = setting_bool('ssl_verify', True)
    hdrs    = {**_default_headers(), **(headers or {})}

    last_exc = None
    deadline = time.monotonic() + max_seconds
    for attempt in range(retries + 1):
        if service_cancelled():raise InterruptedError('SERVICE_STOP')
        try:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('HTTP response time budget exceeded')
            if _httpx_available():
                proxy = _build_proxy()
                client_kwargs = dict(
                    headers=hdrs,
                    timeout=min(to, remaining),
                    verify=verify,
                    follow_redirects=True,
                )
                if proxy:
                    client_kwargs['proxy'] = proxy
                with httpx.Client(**client_kwargs) as client:
                    with client.stream('GET', url, params=params) as r:
                        r.raise_for_status()
                        # No chunk_size buffering: enforce the deadline after
                        # each transport read, including slow/dripping servers.
                        body = read_http_chunks(r.iter_raw(),
                                                r.headers, max_bytes, deadline)
                        return body, dict(r.headers)
            else:
                import urllib.request, urllib.parse
                request_url = url
                if params:
                    request_url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
                req = urllib.request.Request(request_url, headers=hdrs)
                with urllib.request.urlopen(req, timeout=min(to, remaining)) as resp:
                    chunks = iter(lambda: resp.read1(min(65536, max_bytes+1)), b'')
                    body = read_http_chunks(chunks, resp.headers, max_bytes, deadline)
                    return body, dict(resp.headers)
        except MemoryError:
            runtime=sys.modules.get('service_runtime')
            if runtime:runtime.note_pressure()
            raise
        except InterruptedError:
            raise
        except ValueError:
            # Size/encoding rejection cannot be repaired by downloading again.
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                delay = min(1.5 ** attempt, max(0, deadline-time.monotonic()))
                runtime=sys.modules.get('service_runtime')
                if runtime:
                    if runtime.wait(delay):raise InterruptedError('SERVICE_STOP')
                else:time.sleep(delay)
    raise last_exc

def http_post(url, data=None, json_data=None, headers=None, timeout=None):
    to   = timeout or setting_int('http_timeout', 15)
    hdrs = {**_default_headers(), **(headers or {})}
    verify = setting_bool('ssl_verify', True)
    if _httpx_available():
        proxy = _build_proxy()
        kw = dict(headers=hdrs, timeout=to, verify=verify, follow_redirects=True)
        if proxy:
            kw['proxies'] = proxy
        with httpx.Client(**kw) as client:
            if json_data is not None:
                r = client.post(url, json=json_data)
            else:
                r = client.post(url, data=data)
            r.raise_for_status()
            return r.content, dict(r.headers)
    else:
        import urllib.request
        body = json.dumps(json_data).encode() if json_data else (data or b'')
        if json_data:
            hdrs['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, data=body, headers=hdrs, method='POST')
        with urllib.request.urlopen(req, timeout=to) as resp:
            return resp.read(), dict(resp.headers)

def cache_key(s):
    return hashlib.md5(s.encode()).hexdigest()

def cache_get(key, max_age=3600):
    newest = None
    for directory in dict.fromkeys((cache_dir(), _private_cache_dir())):
        path = os.path.join(directory, key + '.json')
        if not xbmcvfs.exists(path): continue
        try:
            with xbmcvfs.File(path) as f: obj = json.loads(f.read())
            if time.time()-obj.get('ts',0)<=max_age and 'data' in obj:
                if newest is None or obj['ts']>newest['ts']: newest=obj
        except Exception: pass
    return newest['data'] if newest else None

def cache_set(key, data):
    obj = json.dumps({'ts': time.time(), 'data': data})
    directory = cache_dir()
    for attempt in range(2):
        temp = os.path.join(directory,'.xcmate-cache-'+uuid.uuid4().hex)
        try:
            with xbmcvfs.File(temp, 'w') as f:
                if not f.write(obj):
                    raise OSError('Cache write refused')
            target = os.path.join(directory,key+'.json')
            if '://' not in directory:
                os.replace(temp,target)
            elif not xbmcvfs.rename(temp,target):
                raise OSError('Atomic cache rename refused')
            return True
        except Exception:
            _CACHE_WRITABLE.pop(directory, None)
            fallback = _private_cache_dir()
            if attempt or directory == fallback:
                error('XCMate cache write failed (path redacted)')
                return False
            warn('XCMate cache permissions changed; retrying in private cache')
            directory = fallback
        finally:
            try:
                if xbmcvfs.exists(temp): xbmcvfs.delete(temp)
            except Exception: pass

def cache_clear():
    for cd in dict.fromkeys((cache_dir(),_private_cache_dir())):
        dirs, files = xbmcvfs.listdir(cd)
        for fn in files:
            # Only XCMate hashed cache keys, never sources/mappings/accounts.
            base, ext = os.path.splitext(fn)
            if ext == '.json' and len(base) == 32 and all(
                    ch in '0123456789abcdef' for ch in base):
                xbmcvfs.delete(os.path.join(cd, fn))
    info('Cache cleared')

def _favs_path():
    p = setting('favourites_file')
    if not p:
        p = os.path.join(addon_data_dir(), 'favourites.json')
    return p

def load_favourites():
    path = _favs_path()
    if not xbmcvfs.exists(path):
        return []
    try:
        with xbmcvfs.File(path) as f:
            return json.loads(f.read())
    except Exception:
        return []

def save_favourites(favs):
    with xbmcvfs.File(_favs_path(), 'w') as f:
        f.write(json.dumps(favs, indent=2))

def toggle_favourite(stream_url, name, logo='', group=''):
    favs = load_favourites()
    match = [i for i, x in enumerate(favs) if x.get('url') == stream_url]
    if match:
        favs.pop(match[0])
        msg = f'{name} removed from favourites'
    else:
        favs.append({'url': stream_url, 'name': name, 'logo': logo, 'group': group})
        msg = f'{name} added to favourites'
    save_favourites(favs)
    xbmcgui.Dialog().notification('Favourites', msg, xbmcgui.NOTIFICATION_INFO, 2000)

def is_favourite(stream_url):
    return any(f.get('url') == stream_url for f in load_favourites())

def notify(title, msg, icon=xbmcgui.NOTIFICATION_INFO, duration=3000):
    xbmcgui.Dialog().notification(title, msg, icon, duration)

def busy_start():
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')

def busy_stop():
    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')

def build_url(base, **kwargs):
    import urllib.parse
    return base + '?' + urllib.parse.urlencode({k: v for k, v in kwargs.items() if v is not None})

def url_params(url):
    import urllib.parse
    qs = url.split('?', 1)[1] if '?' in url else ''
    return {k: v[0] for k, v in urllib.parse.parse_qs(qs).items()}


def safe_int(val, default: int = 0) -> int:
    if val is None:
        return default
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    s = str(val).strip()
    if not s or s.lower() in ('n/a', 'none', '-', '?', 'null'):
        return default
    import re
    m = re.match(r'^-?\d+', s)
    return int(m.group()) if m else default

def safe_float(val, default: float = 0.0) -> float:
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s.lower() in ('n/a', 'none', '-', '?', 'null'):
        return default
    import re
    m = re.match(r'^-?\d+(\.\d+)?', s.replace(',', '.'))
    return float(m.group()) if m else default

def safe_year(val, default: int = 0) -> int:

    if val is None:
        return default
    if isinstance(val, int):
        return val if 1900 <= val <= 2100 else default
    s = str(val).strip()
    import re
    m = re.search(r'\b(19|20)\d{2}\b', s)
    return int(m.group()) if m else default


_LANG_ALIASES = {
    'de': ['de', 'deutsch', 'german', 'germany', 'deutschland', 'ger', 'deu'],
    'at': ['at', 'austria', 'österreich', 'oesterreich', 'aut'],
    'ch': ['ch', 'schweiz', 'switzerland', 'swiss', 'sui', 'che'],
    'en': ['en', 'english', 'eng', 'uk', 'gb', 'us', 'usa', 'britain', 'american'],
    'nl': ['nl', 'netherlands', 'nederland', 'dutch', 'nld', 'hollands', 'holland'],
    'fr': ['fr', 'french', 'france', 'français', 'francais', 'fra'],
    'es': ['es', 'spanish', 'spain', 'español', 'espanol', 'espana', 'españa', 'esp'],
    'it': ['it', 'italian', 'italy', 'italia', 'italiano', 'ita'],
    'tr': ['tr', 'turkish', 'turkey', 'türkei', 'turkei', 'türk', 'turk', 'tur'],
    'pl': ['pl', 'polish', 'poland', 'polska', 'pol'],
    'ru': ['ru', 'russian', 'russia', 'russland', 'rus'],
    'ar': ['ar', 'arabic', 'arab', 'ara'],
    'pt': ['pt', 'portuguese', 'portugal', 'português', 'portugues', 'por'],
    'ro': ['ro', 'romanian', 'romania', 'român', 'roman', 'rou'],
    'hr': ['hr', 'croatian', 'croatia', 'kroatien', 'hrvatski', 'hrv'],
    'sr': ['sr', 'serbian', 'serbia', 'srbija', 'srb'],
    'hu': ['hu', 'hungarian', 'hungary', 'ungarn', 'magyar', 'hun'],
    'cs': ['cs', 'czech', 'czechia', 'tschechien', 'česky', 'cesky', 'cze'],
    'sk': ['sk', 'slovak', 'slovakia', 'slowakei', 'slovensko', 'svk'],
    'el': ['el', 'greek', 'greece', 'griechenland', 'ελλάδα', 'ellada', 'grc'],
    'sv': ['sv', 'swedish', 'sweden', 'schweden', 'sverige', 'swe'],
    'no': ['no', 'norwegian', 'norway', 'norwegen', 'norge', 'nor'],
    'da': ['da', 'danish', 'denmark', 'dänemark', 'danemark', 'danmark', 'den'],
    'fi': ['fi', 'finnish', 'finland', 'finnland', 'suomi', 'fin'],
    'be': ['be', 'belgium', 'belgien', 'belgie', 'belgique', 'bel'],
}


def _get_tokens_for_code(code: str) -> list:
    return _LANG_ALIASES.get(code.lower(), [code.lower()])


def get_lang_priorities() -> list:
    raw = setting('lang_priority', '').strip()
    if not raw:
        return []
    return [t.strip().lower() for t in raw.replace(';', ',').split(',') if t.strip()]


def lang_sort_key(name: str, group: str = '', langs: list = None) -> tuple:
    if langs is None:
        langs = get_lang_priorities()
    return _lang_rank(langs, name, group)


def _lang_rank(langs: list, name: str, group: str) -> tuple:
    if not langs:
        return (0, 0)
    match_name  = setting_bool('lang_match_name',  True)
    match_group = setting_bool('lang_match_group', True)
    haystack = ''
    if match_name:
        haystack += ' ' + name.lower()
    if match_group:
        haystack += ' ' + (group or '').lower()
    for i, code in enumerate(langs):
        for token in _get_tokens_for_code(code):
            if token in haystack:
                return (i, 0)
    return (len(langs), 0)


def apply_lang_sort(items: list,
                    name_fn=None,
                    group_fn=None,
                    stable: bool = True) -> list:
    langs = get_lang_priorities()
    if not langs:
        return items

    name_fn  = name_fn  or (lambda x: getattr(x, 'name',  '') or '')
    group_fn = group_fn or (lambda x: getattr(x, 'group', '') or '')

    match_name  = setting_bool('lang_match_name',  True)
    match_group = setting_bool('lang_match_group', True)
    n = len(langs)

    def rank(item):
        haystack = ''
        if match_name:
            haystack += ' ' + name_fn(item).lower()
        if match_group:
            haystack += ' ' + group_fn(item).lower()
        for i, code in enumerate(langs):
            for token in _get_tokens_for_code(code):
                if token in haystack:
                    return i
        return n

    return sorted(items, key=lambda x: (rank(x),), reverse=False) if not stable \
           else [x for _, x in sorted(enumerate(items),
                                      key=lambda ix: (rank(ix[1]), ix[0]))]


import xbmc as _xbmc

_ADDON_INSTANCE = xbmcaddon.Addon()

_FALLBACK: dict = {
    32000: 'XCMate',     32001: 'Live TV',          32002: 'Movies',
    32003: 'Series',          32004: 'Favourites',        32005: 'Search',
    32006: 'EPG / Guide',     32007: 'Settings',          32008: 'Refresh Playlist',
    32009: 'Catch-up',        32010: 'Search All',        32011: 'All Favourites',
    32012: 'Portal Manager',  32013: 'Account Info',      32014: 'Now on TV',
    32015: 'All Channels',    32016: 'All Movies',        32017: 'All Series',
    32018: 'Next page ({0} more)', 32019: 'Previous page ({0})',
    32030: 'Add to Favourites',    32031: 'Remove from Favourites',
    32032: 'Now Playing',          32033: 'Refresh cache',
    32040: 'No channels found',    32041: 'Playlist refreshed',
    32042: 'EPG refreshed',        32043: 'Cache cleared',
    32044: 'No EPG data available',32045: 'No favourites saved yet',
    32046: 'No results for "{0}"', 32047: 'No catch-up data available',
    32048: 'No catch-up URL available',
    32049: 'No M3U URL configured for this portal',
    32050: 'Portal not found. Open Portal Manager.',
    32051: 'Xtream host not set. Open Portal Manager.',
    32052: 'Authentication failed – check Portal URL and MAC',
    32053: 'Refreshing {0}…',      32054: 'Refresh failed: {0}',
    32055: 'No {0} found in this M3U playlist',
    32056: 'Searching for "{0}"…', 32057: 'No channels found for "{0}". Check URL / credentials.',
    32060: 'Add new Portal',       32061: 'Portal name',
    32062: 'Portal type',          32063: 'M3U Playlist',
    32064: 'Xtream Codes',         32065: 'STB / Stalker Portal',
    32066: 'M3U URL or local path',32067: 'Xtream Codes host (e.g. http://provider.tv:8080)',
    32068: 'Username',             32069: 'Password',
    32070: 'Portal URL',           32071: 'MAC Address',
    32072: 'EPG URL (XMLTV) – optional',
    32073: 'Add this portal?',     32074: 'Edit "{0}"',
    32075: 'Really delete "{0}"? All cached data will be removed.',
    32076: 'Delete Portal',        32077: 'Enable',       32078: 'Disable',
    32079: 'Move up',              32080: 'Move down',
    32081: 'Save & Close',         32082: 'Cancel',
    32083: 'Added: {0}',           32084: 'Deleted: {0}', 32085: 'Saved: {0}',
    32086: 'Moved up: {0}',        32087: 'Moved down: {0}',
    32088: 'Enabled: {0}',         32089: 'Disabled: {0}',
    32090: 'My IPTV',              32091: 'Enabled',      32092: 'Type',
    32100: 'Xtream Codes detected',
    32101: 'This URL looks like an Xtream Codes server.\nSwitch to Xtream mode?\n\nHost: {0}\nUser: {1}',
    32102: 'Keep as M3U',          32103: 'Use Xtream',
    32210: 'Language Filter',      32211: 'Language priority (e.g. de,at,ch,en)',
    32212: 'Comma-separated codes. Leave blank to disable.',
    32213: 'Match against channel name', 32214: 'Match against group name',
    32200: 'Portals',           32201: 'Open Portal Manager',
    32220: 'Player',            32221: 'Default player',
    32222: 'Auto|InputStream Adaptive|Kodi built-in',
    32223: 'User-Agent',        32224: 'HTTP timeout (s)',
    32225: 'Retry attempts',    32226: 'Use ISA for HLS',
    32227: 'Use ISA for DASH',  32228: 'Preferred quality',
    32229: 'Best|1080p|720p|480p|360p|Worst',
    32230: 'EPG / Guide',       32231: 'Auto-refresh EPG',
    32232: 'Refresh interval (h)', 32233: 'Hours ahead',
    32234: 'Hours back (catch-up)', 32235: 'Show programme images',
    32240: 'Appearance',        32241: 'Show channel logos',
    32242: 'Items per page',    32243: 'Sort channels',
    32244: 'Playlist order|Name A-Z|Name Z-A',
    32245: 'Sort groups',       32246: 'Playlist order|Name A-Z',
    32247: 'View mode',         32248: 'List|Wide list|Thumbnails',
    32250: 'Cache & Data',      32251: 'Cache playlists',
    32252: 'Cache EPG',         32253: 'Cache directory',
    32254: 'Clear cache now',   32255: 'Favourites backup file',
    32256: 'Recordings folder',
    32260: 'Advanced',          32261: 'HTTP Proxy URL',
    32262: 'Proxy Username',    32263: 'Proxy Password',
    32264: 'Verify SSL certs',  32265: 'Debug logging',
    32266: 'Catch-up URL template',
}


def _L(string_id: int, *fmt_args) -> str:
    """
    Return the localized string for string_id.
    Optional positional args are formatted via str.format().
    Falls back to _FALLBACK dict if Kodi returns an empty string.
    """
    s = _ADDON_INSTANCE.getLocalizedString(string_id)
    if not s:
        s = _FALLBACK.get(string_id, f'#{string_id}')
    if fmt_args:
        try:
            s = s.format(*fmt_args)
        except Exception:
            pass
    return s


from contextlib import contextmanager


@contextmanager
def http_stream(url, params=None, headers=None, timeout=15, max_seconds=None,
                cancel=lambda: False):
    """One response, worker only. Failed imports retry from a fresh generation.

    No full body allocation and no 80-MiB collection limit. Existing http_get
    remains bounded for authentication, metadata and short guide requests.
    """
    from network_io import decoded_chunks, ChunkReader,service_timeout
    timeout=service_timeout(timeout)
    deadline = None if max_seconds is None else time.monotonic()+max_seconds
    hdrs = {**_default_headers(), **(headers or {})}
    if _httpx_available():
        options = dict(headers=hdrs, timeout=timeout, verify=setting_bool('ssl_verify',True), follow_redirects=True)
        proxy = _build_proxy()
        if proxy: options['proxy'] = proxy
        with httpx.Client(**options) as client:
            with client.stream('GET',url,params=params) as response:
                response.raise_for_status()
                yield ChunkReader(decoded_chunks(response.iter_raw(chunk_size=65536),response.headers,deadline,cancel))
    else:
        import urllib.request, urllib.parse
        if params: url += ('&' if '?' in url else '?')+urllib.parse.urlencode(params)
        context = None
        if not setting_bool('ssl_verify',True):
            import ssl
            context = ssl._create_unverified_context()
        request = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(request,timeout=timeout,context=context) as response:
            chunks = iter(lambda: response.read1(65536), b'')
            yield ChunkReader(decoded_chunks(chunks,response.headers,deadline,cancel))

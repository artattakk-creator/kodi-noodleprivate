"""Read selected Cumination provider directories through Kodi JSON-RPC.

No copied provider scrapers and no attempt to defeat site access controls.
The installed Cumination add-on owns parsing and stream resolution.
"""
import json
import re
import urllib.parse

CUMINATION_ID = 'plugin.video.cumination'
PROVIDERS = {
    'eporner': {'name': 'EPorner', 'search': 'https://www.eporner.com/search/'},
    'xhamster': {'name': 'xHamster', 'search': 'https://xhamster.com/search/'},
    'pornhub': {'name': 'Pornhub', 'search': 'https://www.pornhub.com/video/search?search='},
    'xnxx': {'name': 'XNXX', 'search': 'https://www.xnxx.com/search/'},
    'spankbang': {'name': 'SpankBang', 'search': 'https://spankbang.party/s/'},
    'tnaflix': {'name': 'Tnaflix', 'search': 'https://www.tnaflix.com/search.php?what='},
}
ORDER = ['eporner', 'xhamster', 'pornhub', 'xnxx', 'spankbang', 'tnaflix']
LEGACY = frozenset(ORDER)
SITE_ID = re.compile(r'^[A-Za-z0-9_]{1,64}$')
MODE = re.compile(r'^[A-Za-z0-9_]{1,64}\.[A-Za-z0-9_]{1,64}$')


def register_catalog(catalog):
    """Extend the original six with validated sites exposed by installed Cumination."""
    for key, data in (catalog or {}).items():
        if not SITE_ID.fullmatch(key) or not isinstance(data, dict):
            continue
        label = str(data.get('name') or key)[:110]
        uri = data.get('uri') or ''
        try:
            parsed = urllib.parse.urlsplit(uri)
            mode = urllib.parse.parse_qs(parsed.query).get('mode', [''])[0]
            if parsed.scheme != 'plugin' or parsed.netloc != CUMINATION_ID or not MODE.fullmatch(mode) or mode.split('.')[0] != key:
                continue
        except (ValueError, TypeError):
            continue
        if key not in PROVIDERS:
            PROVIDERS[key] = {'name': label, 'uri': uri, 'image': str(data.get('image') or '')}
            ORDER.append(key)
        else:
            PROVIDERS[key]['uri'] = uri
            PROVIDERS[key]['image'] = str(data.get('image') or '')





class BridgeError(Exception):
    pass


def enabled_sources(prefs):
    configured = prefs.get('provider_enabled', {})
    if not isinstance(configured, dict):
        configured = {}
    return ['noodlemagazine'] * (configured.get('noodlemagazine', True) is not False) + [
        key for key in ORDER if configured.get(key, key in LEGACY) is not False]


def source_name(source):
    return 'NoodleMagazine' if source == 'noodlemagazine' else PROVIDERS.get(source, {}).get('name', source)


def cumination_uri(provider, route='Main', keyword=None):
    if provider not in PROVIDERS or route not in ('Main', 'Search'):
        raise BridgeError('Nicht unterstützter Anbieter')
    params = {'mode': '{}.{}'.format(provider, route)}
    if route == 'Main' and PROVIDERS[provider].get('uri'):
        return validated_cumination_url(PROVIDERS[provider]['uri'], provider)
    if route == 'Search':
        if not PROVIDERS[provider].get('search'):
            raise BridgeError('Für diesen Anbieter ist kein Suchpfad bekannt')
        params['url'] = PROVIDERS[provider]['search']
        params['keyword'] = (keyword or '').strip()
    return 'plugin://{}/?{}'.format(CUMINATION_ID, urllib.parse.urlencode(params))


def validated_cumination_url(path, provider=None):
    """Only accept Cumination subroutes belonging to one of the chosen modules."""
    parsed = urllib.parse.urlsplit(path or '')
    if parsed.scheme != 'plugin' or parsed.netloc != CUMINATION_ID:
        raise BridgeError('Unerwarteter Kodi-Pluginpfad')
    mode = urllib.parse.parse_qs(parsed.query).get('mode', [''])[0]
    token = mode.split('.', 1)[0]
    if token not in PROVIDERS or not MODE.fullmatch(mode) or (provider and token != provider):
        raise BridgeError('Nicht freigegebener Cumination-Aufruf')
    return path


def source_for_url(url):
    parsed = urllib.parse.urlsplit(url or '')
    if parsed.scheme == 'plugin' and parsed.netloc == CUMINATION_ID:
        try:
            validated_cumination_url(url)
            mode = urllib.parse.parse_qs(parsed.query).get('mode', [''])[0]
            return mode.split('.', 1)[0]
        except BridgeError:
            return ''
    if parsed.scheme == 'https' and parsed.netloc in (
            'noodlemagazine.com', 'www.noodlemagazine.com', 'adult.noodlemagazine.com'):
        return 'noodlemagazine'
    return ''


def kodi_directory(execute_json_rpc, path, provider):
    """Request a directory via Kodi JSON-RPC (no direct scraping of other sites).

    Kodi may reject a source or block on a slow provider. Caller handles errors
    independently so one unavailable source cannot erase other search results.
    """
    validated_cumination_url(path, provider)
    request = {'jsonrpc': '2.0', 'id': 72, 'method': 'Files.GetDirectory', 'params': {
        'directory': path, 'media': 'video',
        'properties': ['title', 'thumbnail', 'art', 'duration', 'plot']}}
    try:
        raw = execute_json_rpc(json.dumps(request, ensure_ascii=False))
        result = json.loads(raw)
    except (ValueError, TypeError, RuntimeError) as exc:
        raise BridgeError('Kodi konnte den Anbieter nicht auslesen: {}'.format(exc)) from exc
    if 'error' in result:
        raise BridgeError('{}: {}'.format(source_name(provider), result['error'].get('message', 'Kodi-Fehler')))
    files = result.get('result', {}).get('files', [])
    if not isinstance(files, list):
        raise BridgeError('Kodi hat keine gültige Videoliste geliefert')
    rows = []
    for item in files[:120]:
        path = item.get('file', '')
        try:
            validated_cumination_url(path, provider)
        except BridgeError:
            continue
        art = item.get('art') or {}
        if not isinstance(art, dict):
            art = {}
        folder = item.get('filetype') == 'directory'
        title = str(item.get('label') or item.get('title') or 'Video')
        img = item.get('thumbnail') or art.get('thumb') or art.get('poster') or ''
        rows.append({'url': path, 'title': title, 'image': img,
                     'duration': max(0, int(item.get('duration') or 0)),
                     'provider': provider, 'is_folder': folder,
                     'description': str(item.get('plot') or '')})
    return rows

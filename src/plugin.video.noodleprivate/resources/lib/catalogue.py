"""Discover actual Cumination sites via Kodi. Never execute copied scraper files.

This cache is separate from state.json: playlists, favorites and user settings
are not reset when the Cumination catalog changes.
"""
import json
import os
import re
import time
import urllib.parse

CATALOG_NAME = 'cumination_catalog.json'
MODE_RE = re.compile(r'^[A-Za-z0-9_]{1,64}\.[A-Za-z0-9_]{1,64}$')
MARKUP_RE = re.compile(r'\[(?:/?COLOR[^\]]*|/?B|/?I)\]', re.I)
SITE_LIST = 'plugin://plugin.video.cumination/?mode=main.site_list'
CACHE_SECONDS = 6 * 3600


def _read_directory(execute, uri):
    payload = {'jsonrpc': '2.0', 'id': 144, 'method': 'Files.GetDirectory', 'params': {
        'directory': uri, 'media': 'video',
        'properties': ['title', 'thumbnail', 'art', 'plot']}}
    try:
        data = json.loads(execute(json.dumps(payload)))
    except (TypeError, ValueError, RuntimeError) as exc:
        raise ValueError('Kodi konnte den Cumination-Katalog nicht lesen: {}'.format(exc))
    if data.get('error'):
        raise ValueError('Kodi JSON-RPC: {}'.format(data['error'].get('message', 'unbekannt')))
    rows = data.get('result', {}).get('files', [])
    if not isinstance(rows, list):
        raise ValueError('Ungültiges Katalogformat')
    return rows


def parse_sites(rows):
    catalog = {}
    for item in rows:
        uri = item.get('file', '')
        try:
            url = urllib.parse.urlsplit(uri)
            mode = urllib.parse.parse_qs(url.query).get('mode', [''])[0]
            key = mode.split('.', 1)[0]
            if url.scheme != 'plugin' or url.netloc != 'plugin.video.cumination' or not MODE_RE.fullmatch(mode) or key == 'main':
                continue
            if item.get('filetype') not in (None, 'directory'):
                continue
            if key in catalog:
                continue
            label = MARKUP_RE.sub('', str(item.get('label') or key)).strip()
            art = item.get('art') or {}
            if not isinstance(art, dict):
                art = {}
            catalog[key] = {'name': label[:110] or key, 'uri': uri,
                            'image': item.get('thumbnail') or art.get('thumb') or ''}
        except (TypeError, ValueError, AttributeError):
            continue
    return catalog


def cache_file(profile):
    return os.path.join(profile, CATALOG_NAME)


def read_cache(profile):
    try:
        with open(cache_file(profile), 'r', encoding='utf8') as handle:
            cache = json.load(handle)
        if not isinstance(cache.get('sites'), dict):
            return {'sites': {}, 'updated': 0, 'health': {}}
        return cache
    except (OSError, ValueError, TypeError):
        return {'sites': {}, 'updated': 0, 'health': {}}


def write_cache(profile, catalog):
    os.makedirs(profile, exist_ok=True)
    path = cache_file(profile)
    temporary = path + '.tmp'
    with open(temporary, 'w', encoding='utf8') as f:
        json.dump(catalog, f, ensure_ascii=False)
    os.replace(temporary, path)


def load_catalog(profile, execute, refresh=False):
    cache = read_cache(profile)
    if not refresh and cache.get('sites') and time.time()-float(cache.get('updated') or 0)<CACHE_SECONDS:
        return cache
    try:
        sites = parse_sites(_read_directory(execute, SITE_LIST))
        if not sites:
            raise ValueError('Cumination lieferte keine registrierten Anbieter')
        cache['sites'] = sites
        cache['updated'] = time.time()
        write_cache(profile, cache)
    except (OSError, ValueError) as error:
        if not cache.get('sites'):
            raise
        cache['error'] = str(error)
    return cache


def search_link(rows, provider):
    """Read real native search route rather than guessing provider URLs."""
    for entry in rows:
        url = str(entry.get('file') or '')
        parsed = urllib.parse.urlsplit(url)
        mode = urllib.parse.parse_qs(parsed.query).get('mode', [''])[0]
        if mode == '{}.Search'.format(provider):
            return url
    return ''


def search_with_keyword(url, keyword):
    parsed = urllib.parse.urlsplit(url)
    pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    values = [(k, v) for k, v in pairs if k not in ('keyword', 'widget')]
    values.append(('keyword', (keyword or '').strip()[:120]))
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path,
                                    urllib.parse.urlencode(values), parsed.fragment))

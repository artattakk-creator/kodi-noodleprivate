"""Optional TVmaze artwork for verified live EPG titles, regardless of genre.

TVmaze's public API is CC BY-SA; keep source attribution attached to the
individual result. No account, token, VOD lookup, scraping or new EPG DB.
Runs only in the existing background programme URL worker after explicit opt-in.
https://www.tvmaze.com/api
"""
import json
import re
import threading
import time
from collections import deque
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE = 'https://api.tvmaze.com/'
USER_AGENT = 'XCMate-TVmaze-experimental/1.0 (https://github.com/artattakk-creator/kodi-noodleprivate)'
_lock = threading.Lock()
_requests = deque()
_retry_after = 0.0


def enabled():
    from utils import setting_bool
    return setting_bool('programme_tvmaze59', False)


def _error(code):
    from media_sources43 import SourceError
    return SourceError(code)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def _get(path, params=None, *, cancel=lambda: False, transport=None):
    """Only fixed TVmaze paths; bounded JSON, strict HTTPS, no redirects."""
    global _retry_after
    if cancel():
        raise _error('CANCELLED')
    if not (path == 'search/shows' or re.fullmatch(r'shows/[1-9][0-9]{0,7}/episodebynumber', path)):
        raise _error('TVMAZE_PATH_BLOCKED')
    url = BASE + path + ('?' + urlencode(params) if params else '')
    if transport is not None:
        return transport(url)
    now = time.monotonic()
    with _lock:
        while _requests and now - _requests[0] > 10:
            _requests.popleft()
        if now < _retry_after or len(_requests) >= 10:
            raise _error('TVMAZE_RATE_LIMIT')
        _requests.append(now)
    try:
        req = Request(url, headers={'Accept': 'application/json', 'User-Agent': USER_AGENT})
        with build_opener(_NoRedirect()).open(req, timeout=4) as response:
            if response.getcode() != 200 or 'application/json' not in response.headers.get('Content-Type', ''):
                raise _error('TVMAZE_INVALID_RESPONSE')
            data = response.read(524289)
            if len(data) > 524288:
                raise _error('TVMAZE_RESPONSE_LIMIT')
            if cancel():
                raise _error('CANCELLED')
            return json.loads(data.decode('utf-8'))
    except HTTPError as exc:
        if exc.code == 429:
            with _lock:
                _retry_after = time.monotonic() + 60
            raise _error('TVMAZE_RATE_LIMIT') from None
        raise _error('TVMAZE_NOT_FOUND' if exc.code == 404 else 'TVMAZE_HTTP_ERROR') from None
    except (URLError, TimeoutError, OSError, ValueError, UnicodeError, TypeError):
        raise _error('TVMAZE_NETWORK_ERROR') from None


def _title(value):
    from epg_events import title_key
    return title_key(str(value or '').strip())


def _art(value):
    image = value.get('image') if isinstance(value, dict) else None
    url = image.get('original') if isinstance(image, dict) else None
    if not isinstance(url, str):
        return None
    # No untrusted image URL reaches the shared EPG image resolver.
    from programme_urls55 import safe
    return url if safe(url) else None


def _movie(event):
    genre = ' '.join(str(event.get(k) or '') for k in ('genre', 'category', 'kind', 'type')).casefold()
    return any(word in genre for word in ('film', 'movie'))


def _compatible(event, show):
    """Never confuse a theatrical movie or classified broadcast with a TV series."""
    name = str(show.get('type') or '').casefold().strip()
    genre = str(event.get('genre') or '').casefold()
    if _movie(event):
        # TVmaze is a TV-show API, not a feature-film catalog. TV movies
        # count only with explicit movie classification AND matching year.
        if name not in ('movie', 'tv movie', 'television movie'):
            return False
        year = str(event.get('year') or '')
        premiered = str(show.get('premiered') or '')[:4]
        return len(year) == 4 and year.isdigit() and premiered == year
    for needle, allowed in (
        (('nachricht', 'news'), ('news',)),
        (('dokumentation', 'documentary'), ('documentary',)),
        (('sport',), ('sports', 'sport')),
        (('talkshow', 'talk show'), ('talk show',)),
    ):
        if any(part in genre for part in needle) and name and not any(part in name for part in allowed):
            return False
    return True


def search_title(title, *, cancel=lambda: False, transport=None):
    """Read-only experimental test; never publishes a match or an image."""
    if not isinstance(title, str) or not 2 <= len(title.strip()) <= 120:
        return []
    rows = _get('search/shows', {'q': title.strip()}, cancel=cancel, transport=transport)
    return [x.get('show') for x in rows[:50] if isinstance(x, dict) and isinstance(x.get('show'), dict)] if isinstance(rows, list) else []


def candidate(event, cancel=lambda: False, transport=None):
    """All live EPG genres are eligible; only uniquely proven TVmaze art is used."""
    if not enabled() or cancel() or not event.get('title'):
        return None
    raw = str(event.get('title', '')).strip()
    if not 2 <= len(raw) <= 120:
        return None
    matches = [row for row in search_title(raw, cancel=cancel, transport=transport)
               if _title(row.get('name')) == _title(raw) and isinstance(row.get('id'), int)]
    if not matches:
        raise _error('TVMAZE_NO_MATCH')
    compatible = [row for row in matches if _compatible(event, row)]
    if not compatible:
        raise _error('TVMAZE_MOVIE_UNAVAILABLE' if _movie(event) else 'TVMAZE_TYPE_MISMATCH')
    # Multiple show IDs require manual association, never take the first search hit.
    if len({row['id'] for row in compatible}) != 1:
        raise _error('TVMAZE_AMBIGUOUS')
    show = compatible[0]
    showid = show['id']
    if not 0 < showid < 100000000:
        return None
    # Derive attribution from the validated numeric ID, never arbitrary API text.
    source_page = 'https://www.tvmaze.com/shows/' + str(showid)
    credit = 'TVmaze (CC BY-SA) · ' + source_page
    season, episode = event.get('season'), event.get('episode')
    if bool(season) != bool(episode):
        raise _error('TVMAZE_EPISODE_UNCERTAIN')
    if season and episode:
        try:
            season, episode = int(season), int(episode)
        except (ValueError, TypeError):
            raise _error('TVMAZE_EPISODE_UNCERTAIN') from None
        if not 0 < season <= 250 or not 0 < episode <= 2000:
            raise _error('TVMAZE_EPISODE_UNCERTAIN')
        data = _get('shows/%d/episodebynumber' % showid,
                    {'season': season, 'number': episode}, cancel=cancel, transport=transport)
        if not isinstance(data, dict) or data.get('season') != season or data.get('number') != episode:
            raise _error('TVMAZE_EPISODE_UNCERTAIN')
        subtitle = str(event.get('subtitle') or '').strip()
        if subtitle and _title(subtitle) != _title(data.get('name')):
            raise _error('TVMAZE_EPISODE_UNCERTAIN')
        url = _art(data)
        if url:
            return dict(url=url, source='tvmaze_episode', match='EXACT_TVMAZE_EPISODE59',
                        image_scope57='episode', remote_id=showid, attribution=credit)
    # A TVmaze programme image is distinct from an episode image.
    url = _art(show)
    if not url:
        raise _error('TVMAZE_NO_IMAGE')
    if season and episode:
        return dict(url=url, source='tvmaze_series', match='EXACT_TVMAZE_SERIES59',
                    image_scope57='series_fallback', remote_id=showid, attribution=credit)
    return dict(url=url, source='tvmaze_programme', match='EXACT_TVMAZE_PROGRAMME59',
                image_scope57='programme', remote_id=showid, attribution=credit)

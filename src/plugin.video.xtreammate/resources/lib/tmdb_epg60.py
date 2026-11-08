"""Complete exact-identity EPG searches, independent of provider VOD widgets."""
from urllib.parse import urlencode


def candidate(event, cancel=lambda: False):
    from utils import setting_bool
    if not setting_bool('programme_tmdb46', False) or not setting_bool('tmdb_research43', False):
        return None
    from media_sources43 import tmdb_token, TMDB, _tmdb_image
    from tmdb_connection60 import request
    from epg_events import title_key
    title_key=__import__('programme_title80').key if not event.get('season') else title_key
    title = title_key(event.get('title', ''))
    if not title:
        return None
    season, episode = event.get('season'), event.get('episode')
    series = type(season) is int and type(episode) is int and 0 <= season <= 100 and 1 <= episode <= 2000
    movie = any(v in str(event.get('genre', '')).casefold() for v in ('spielfilm', 'film', 'movie'))
    if not series and not movie:
        from programme_tv66 import candidate as television66
        television80=television66(event,cancel)
        return television80 or __import__('programme_title80').unclassified(event,cancel)
    year = str(event.get('year') or '')
    if year and (not year.isdigit() or not 1880 <= int(year) <= 2100):
        return None
    if not series and not year:
        from programme_match46 import unique_movie56
        return unique_movie56(event, cancel)
    token = tmdb_token()
    kind = 'tv' if series else 'movie'
    data = request(TMDB + '/search/' + kind + '?' + urlencode(dict(query=__import__('programme_title80').query(event['title'])[:200] if not series else event['title'][:200], language='de-DE', include_adult='false')), token=token, cancel=cancel)
    rows = data.get('results')
    # A truncated first page cannot establish uniqueness.
    if not isinstance(rows, list) or data.get('total_pages') != 1 or type(data.get('total_results')) is not int or data['total_results'] != len(rows) or len(rows) > 20:
        return None
    matches = {r['id']: r for r in rows if isinstance(r, dict) and type(r.get('id')) is int and r['id'] > 0 and not r.get('adult') and title in (title_key(r.get('name' if series else 'title', '')),title_key(r.get('original_name' if series else 'original_title',''))) and
               (not year or str(r.get('first_air_date' if series else 'release_date', ''))[:4] == year)}
    if len(matches) != 1:
        return None
    remote, row = next(iter(matches.items()))
    credit = 'TMDB · https://www.themoviedb.org/' + kind + '/' + str(remote) + ' · ' + __import__('tmdb_connection60').ATTRIBUTION
    if series:
        details = request(TMDB + '/tv/' + str(remote) + '/season/' + str(season) + '/episode/' + str(episode) + '?language=de-DE', token=token, cancel=cancel)
        if details.get('season_number') != season or details.get('episode_number') != episode or type(details.get('id')) is not int:
            return None
        if event.get('subtitle') and title_key(details.get('name', '')) != title_key(event['subtitle']):
            return None
        url = _tmdb_image(details.get('still_path'))
        return dict(url=url, source='tmdb_episode', match='EXACT_SEASON_EPISODE', attribution=credit, remote_id=remote) if url else None
    details = request(TMDB + '/movie/' + str(remote) + '?language=de-DE', token=token, cancel=cancel)
    if details.get('id') != remote or details.get('adult') or title not in (title_key(details.get('title', '')),title_key(details.get('original_title',''))) or str(details.get('release_date', ''))[:4] != year:
        return None
    url = _tmdb_image(details.get('backdrop_path'))
    return dict(url=url, source='tmdb_movie', match='EXACT_TITLE_YEAR', attribution=credit, remote_id=remote) if url else None

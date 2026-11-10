"""Complete exact-identity EPG searches, independent of provider VOD widgets."""
from urllib.parse import urlencode


def reject84(event,code):
    from art_trace81 import note
    note(event,'MATCH_REJECTED',code)
    return None


def candidate(event, cancel=lambda: False):
    from utils import setting_bool
    if not setting_bool('programme_tmdb46', False) or not setting_bool('tmdb_research43', False):
        return reject84(event,'DISABLED')
    from media_sources43 import tmdb_token, TMDB, _tmdb_image
    from tmdb_connection60 import request
    from epg_events import title_key
    title_key=__import__('programme_title80').key if not event.get('season') else title_key
    title = title_key(event.get('title', ''))
    if not title:
        return reject84(event,'TITLE_EMPTY')
    season, episode = event.get('season'), event.get('episode')
    series = type(season) is int and type(episode) is int and 0 <= season <= 100 and 1 <= episode <= 2000
    movie = any(v in str(event.get('genre', '')).casefold() for v in ('spielfilm', 'film', 'movie'))
    if not series and not movie:
        from programme_tv66 import candidate as television66
        television80=television66(event,cancel)
        return television80 or __import__('programme_title80').unclassified(event,cancel)
    year = str(event.get('year') or '')
    if year and (not year.isdigit() or not 1880 <= int(year) <= 2100):
        return reject84(event,'YEAR_INVALID')
    if not series and not year:
        from programme_match46 import unique_movie56
        return unique_movie56(event, cancel)
    token = tmdb_token()
    kind = 'tv' if series else 'movie'
    data = request(TMDB + '/search/' + kind + '?' + urlencode(dict(query=__import__('programme_title80').query(event['title'])[:200] if not series else event['title'][:200], language='de-DE', include_adult='false')), token=token, cancel=cancel)
    rows = data.get('results')
    # A truncated first page cannot establish uniqueness.
    if not isinstance(rows, list) or data.get('total_pages') != 1 or type(data.get('total_results')) is not int or data['total_results'] != len(rows) or len(rows) > 20:
        return reject84(event,'SEARCH_INCOMPLETE')
    matches = {r['id']: r for r in rows if isinstance(r, dict) and type(r.get('id')) is int and r['id'] > 0 and not r.get('adult') and title in (title_key(r.get('name' if series else 'title', '')),title_key(r.get('original_name' if series else 'original_title',''))) and
               (not year or str(r.get('first_air_date' if series else 'release_date', ''))[:4] == year)}
    if len(matches) != 1:
        return reject84(event,'MATCH_AMBIGUOUS' if matches else 'TITLE_YEAR_MISMATCH')
    remote, row = next(iter(matches.items()))
    credit = 'TMDB · https://www.themoviedb.org/' + kind + '/' + str(remote) + ' · ' + __import__('tmdb_connection60').ATTRIBUTION
    if series:
        details = request(TMDB + '/tv/' + str(remote) + '/season/' + str(season) + '/episode/' + str(episode) + '?language=de-DE', token=token, cancel=cancel)
        if details.get('season_number') != season or details.get('episode_number') != episode or type(details.get('id')) is not int:
            return reject84(event,'EPISODE_MISMATCH')
        if event.get('subtitle') and title_key(details.get('name', '')) != title_key(event['subtitle']):
            return reject84(event,'EPISODE_TITLE_MISMATCH')
        url = _tmdb_image(details.get('still_path'))
        if url:return dict(url=url, source='tmdb_episode', match='EXACT_SEASON_EPISODE', attribution=credit, remote_id=remote)
        if details.get('still_path'):
            # A malformed supplied path is not an absent episode still.
            # Preserve the safety rejection without additional lookup work.
            return reject84(event,'IMAGE_PATH_INVALID')
        # Episode identity was proved; absence of a still permits only an
        # independently verified series work illustration, explicitly labelled.
        work=request(TMDB+'/tv/'+str(remote)+'?language=de-DE',token=token,cancel=cancel)
        actual=str(work.get('first_air_date',''))[:4]
        if work.get('id')!=remote or work.get('adult') or title not in (title_key(work.get('name','')),title_key(work.get('original_name',''))) or not actual.isdigit() or actual!=str(row.get('first_air_date',''))[:4]:return reject84(event,'DETAIL_IDENTITY_MISMATCH')
        fallback=_tmdb_image(work.get('backdrop_path') or work.get('poster_path'))
        if not fallback:return reject84(event,'IMAGE_PATH_MISSING')
        return dict(url=fallback,source='tmdb_series',match='EXACT_TV_TITLE_YEAR66' if year else 'EXACT_UNIQUE_TV_TITLE66',remote_id=remote,official_poster86=_tmdb_image(work.get('poster_path')),matched_year56=int(actual),role81='backdrop' if work.get('backdrop_path') else 'poster',image_scope57='series_fallback',attribution=credit+' · Serienbild (kein Episodenbild)')
    details = request(TMDB + '/movie/' + str(remote) + '?language=de-DE', token=token, cancel=cancel)
    if details.get('id') != remote or details.get('adult') or title not in (title_key(details.get('title', '')),title_key(details.get('original_title',''))) or str(details.get('release_date', ''))[:4] != year:
        return reject84(event,'DETAIL_IDENTITY_MISMATCH')
    url = _tmdb_image(details.get('backdrop_path') or details.get('poster_path'))
    return dict(url=url, source='tmdb_movie', match='EXACT_TITLE_YEAR',official_poster86=_tmdb_image(details.get('poster_path')),role81='backdrop' if details.get('backdrop_path') else 'poster', attribution=credit, remote_id=remote) if url else reject84(event,'IMAGE_PATH_MISSING')

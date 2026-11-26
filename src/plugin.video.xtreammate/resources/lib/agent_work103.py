"""Worker-side search and confirmed role assignments from the verified Agent index."""
import hashlib
import json
import time

from agent_programme100 import SOURCES, candidates, image_shape, pictures_enabled, validate_url
from media_sources43 import SourceError
from xmltv_stream import TMDB_WORK_ID


SOURCE = 'agent_event103'
ROLES = ('backdrop', 'episode_still', 'poster')
LABELS = {'backdrop': 'Hintergrundbild', 'episode_still': 'Episodenbild', 'poster': 'Poster'}
PAGE_SIZE = 16


def valid(values):
    return (isinstance(values, dict) and bool(values) and set(values) <= set(ROLES)
            and all(type(value) is int and 0 < value <= 16 ** 13 for value in values.values()))


def valid_locator(value):
    return (isinstance(value, dict) and set(value) == {'source', 'channel', 'start', 'stop'}
            and isinstance(value['source'], str) and value['source'] in SOURCES
            and isinstance(value['channel'], str) and 0 < len(value['channel']) <= 512
            and type(value['start']) is int and type(value['stop']) is int
            and 0 < value['start'] < value['stop'] < 2 ** 63)


def _id(row):
    fields = [row['source'], row['role81'], row['url']]
    return int(hashlib.sha256(json.dumps(fields).encode()).hexdigest()[:13], 16) + 1


def _folder(event):
    from epg_agent100 import local_candidate
    folder = local_candidate(event['pid'])
    generation = event.get('_agent_generation103')
    if folder and generation and folder.name != 'candidate-' + generation:
        return None
    return folder


def _work(value):
    value = str(value or '')
    return value if TMDB_WORK_ID.fullmatch(value) else ''


def work_id(event):
    return _work(event.get('xmltv_tmdb_id')) if event.get('_agent_event104') else ''


def _same_episode(event, row):
    work = work_id(event)
    return bool(work and work == row.get('work_id') and event.get('season') and event.get('episode')
                and (event['season'], event['episode']) == (row.get('season'), row.get('episode_number')))


def _indexed(event, row):
    from agent_programme100 import allowed
    from programme_urls55 import _contains_credentials, safe

    role = row['role']
    reference = row['reference']
    source, url = reference['source'], reference['url']
    if role not in ROLES or role == 'episode_still' and not _same_episode(event, row):
        return None
    if not allowed(source) or not validate_url(url, source) or not safe(url) or _contains_credentials(event, url):
        return None
    locator = dict(source=source, channel=row['channel'], start=row['start_timestamp'], stop=row['stop_timestamp'])
    if not valid_locator(locator):
        return None
    return dict(reference, role81=role, locator104=locator, title=row['title'], year=row.get('year') or 0,
                season=row.get('season'), episode=row.get('episode_number'), work_id=row.get('work_id') or '')


def _index_call(method, *args, **kwargs):
    import epg_agent_catalog103 as index
    try:
        return getattr(index, method)(*args, **kwargs)
    except index.IndexReadError as error:
        raise SourceError(error.code) from None


def _entry(event, value):
    result = dict(id=_id(value), source=SOURCE, role=value['role81'], title=event['title'],
                  year=event.get('year') or 0, media_type86='event',
                  overview=event.get('subtitle') or '', attribution=value['attribution'])
    if locator := value.get('locator104'):
        result.update(locator104=locator, channel=locator['channel'], title=value['title'],
                      year=value['year'], season=value['season'], episode=value['episode'],
                      work_id=value['work_id'], overview='')
    return result


def search(event, *, query='', page=1, role='', source='', year=None, season=None, episode=None,
           cancel=lambda:False):
    """Return exact-event choices and a bounded page from the whole active feed."""
    if not pictures_enabled():
        raise SourceError('SOURCE_DISABLED')
    if role and role not in ROLES or source and source not in SOURCES:
        raise SourceError('CANDIDATES_REJECTED')
    from epg_events import title_key

    query = str(query or event['title'])[:200].strip()
    page = max(1, min(1000, int(page)))
    rows = []
    if page == 1 and title_key(query) == title_key(event['title']):
        for value in candidates(event):
            if (value['role81'] in ROLES and (not role or role == value['role81'])
                    and (not source or source == value['source'])
                    and all(wanted is None or wanted == event.get(field) for field, wanted
                            in (('year', year), ('season', season), ('episode', episode)))):
                rows.append(_entry(event, value))
    seen = {(row['role'], row['id']) for row in rows}
    more = False
    folder = _folder(event)
    if folder is not None and query:
        work = _work(query)
        try:
            found, more = _index_call('search_art', folder, '' if work else query, work_id=work,
                                      year=year, season=season, episode=episode, role=role,
                                      source=source, offset=(page - 1) * PAGE_SIZE, limit=PAGE_SIZE,
                                      cancel=cancel)
        except SourceError as error:
            if not rows or error.code == 'CANCELLED':
                raise
            return dict(code='READY', rows=rows, more=False)
        for indexed in found:
            if cancel():
                raise SourceError('CANCELLED')
            value = _indexed(event, indexed)
            if value is None:
                continue
            key = (value['role81'], _id(value))
            if key not in seen:
                rows.append(_entry(event, value))
                seen.add(key)
    return dict(code='READY' if rows else 'ZERO_RESULTS', rows=rows, more=more)


def find(event, role, ident, locator=None, cancel=lambda:False):
    if not isinstance(role, str) or not valid({role: ident}):
        return None
    if locator is None:
        return next((row for row in candidates(event) if row['role81'] == role and _id(row) == ident), None)
    if not valid_locator(locator):
        return None
    folder = _folder(event)
    if folder is None:
        return None
    rows = _index_call('art_references', folder, locator['channel'], locator['start'],
                       locator['stop'], role, locator['source'], cancel=cancel)
    for raw in rows:
        row = _indexed(event, raw)
        if row and row['locator104'] == locator and _id(row) == ident:
            return row
    return None


def choices(event, mapping, requested, cancel=lambda:False):
    from agent_programme100 import VIEW_ROLES
    assigned = mapping.get('agent103', {})
    if not valid(assigned):
        return
    origins = mapping.get('agent_origins104', {})
    for role in VIEW_ROLES[requested]:
        try:
            row = find(event, role, assigned.get(role), origins.get(role), cancel)
        except SourceError as error:
            if error.code == 'CANCELLED':
                return
            continue
        if row:
            yield dict(row, manual85=True, match='MANUAL_CONFIRMED') if row.get('locator104') else dict(row, manual85=True)


def related(event, requested, cancel):
    """Reuse a verified work image, with exact episode coordinates for stills."""
    from agent_programme100 import VIEW_ROLES
    work = work_id(event)
    if not work or not pictures_enabled() or cancel():
        return
    folder = _folder(event)
    if folder is None:
        return
    for role in VIEW_ROLES[requested]:
        if role not in ROLES or cancel():
            continue
        filters = {}
        if role == 'episode_still':
            if not event.get('season') or not event.get('episode'):
                continue
            filters.update(season=event['season'], episode=event['episode'])
        try:
            rows, _ = _index_call('search_art', folder, work_id=work, role=role,
                                  limit=4, cancel=cancel, **filters)
        except SourceError:
            return
        for raw in rows:
            value = _indexed(event, raw)
            if value and value['work_id'] == work:
                yield dict(value, match='EXACT_AGENT_EPISODE' if role == 'episode_still' else 'EXACT_AGENT_WORK')


def _check(event, selected, cancel):
    from programme_origin75 import candidate as qualified_origin
    from programme_urls55 import _contains_credentials, probe, safe

    if not pictures_enabled():
        raise SourceError('SOURCE_DISABLED')
    role, ident, locator = selected.get('role'), selected.get('id'), selected.get('locator104')
    row = find(event, role, ident, locator, cancel)
    if not row or selected.get('title') != row.get('title', event['title']) or (
            locator and selected.get('year') != row.get('year')):
        raise SourceError('EPG_REVISION_CHANGED')
    url = row['url']
    qualified = row['source'] == 'agent_xmltv' and qualified_origin(event, url, row['source'])
    if (not qualified and not safe(url)) or _contains_credentials(event, url):
        raise SourceError('BLOCKED_IMAGE_HOST_OR_URL')
    checked = probe(url, cancel=cancel, qualified_origin=True) if row['source'] == 'agent_xmltv' else probe(url, cancel=cancel)
    final = checked.get('url', url) if isinstance(checked, dict) else url
    if not validate_url(final, row['source'], qualified=qualified) or _contains_credentials(event, final):
        raise SourceError('BLOCKED_IMAGE_HOST_OR_URL')
    if not image_shape(role, checked) or not checked.get('_body81'):
        raise SourceError('NO_ARTWORK')
    if cancel():
        raise SourceError('CANCELLED')
    return row, checked


def preview(event, selected, cancel):
    """Publish an on-demand preview from already validated bytes."""
    from decoded_assets88 import put
    from programme_requests68 import identity
    row, checked = _check(event, selected, cancel)
    key = 'agent-preview104.' + identity(event) + '.' + str(_id(row))
    try:
        return put(key, checked['_body81'], time.time() + 120)['uri']
    except (OSError, ValueError):
        raise SourceError('AGENT_CACHE_UNAVAILABLE') from None


def verify(event, selected, cancel):
    row, _ = _check(event, selected, cancel)
    result = dict(id=_id(row), source=SOURCE, media_type86='event', role=row['role81'], verified85=True)
    if row.get('locator104'):
        result['locator104'] = row['locator104']
    return result

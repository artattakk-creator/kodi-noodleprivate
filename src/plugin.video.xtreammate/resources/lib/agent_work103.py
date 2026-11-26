"""Manual choices from exact event image references in the imported Agent feed."""
import hashlib
import json

from agent_programme100 import candidates, image_shape, pictures_enabled, validate_url
from media_sources43 import SourceError


SOURCE = 'agent_event103'
ROLES = ('backdrop', 'episode_still', 'poster')
LABELS = {'backdrop': 'Hintergrundbild', 'episode_still': 'Episodenbild', 'poster': 'Poster'}


def valid(values):
    return (isinstance(values, dict) and bool(values) and set(values) <= set(ROLES)
            and all(type(value) is int and 0 < value <= 16 ** 13 for value in values.values()))


def _id(row):
    fields = [row['source'], row['role81'], row['url']]
    return int(hashlib.sha256(json.dumps(fields).encode()).hexdigest()[:13], 16) + 1


def search(event):
    if not pictures_enabled():
        raise SourceError('SOURCE_DISABLED')
    rows = []
    for value in candidates(event):
        role = value['role81']
        if role not in ROLES:
            continue
        rows.append(dict(id=_id(value), source=SOURCE, role=role,
                         title=event['title'], year=event.get('year') or 0,
                         media_type86='event', overview=event.get('subtitle') or '',
                         attribution=value['attribution']))
    return dict(code='READY' if rows else 'ZERO_RESULTS', rows=rows, more=False)


def find(event, role, ident):
    if not isinstance(role, str) or not valid({role: ident}):
        return None
    return next((row for row in candidates(event) if row['role81'] == role and _id(row) == ident), None)


def choices(event, mapping, requested):
    from agent_programme100 import VIEW_ROLES
    assigned = mapping.get('agent103', {})
    if not valid(assigned):
        return
    for role in VIEW_ROLES[requested]:
        row = find(event, role, assigned.get(role))
        if row:
            yield dict(row, manual85=True)


def verify(event, selected, cancel):
    from programme_origin75 import candidate as qualified_origin
    from programme_urls55 import _contains_credentials, probe, safe

    if not pictures_enabled():
        raise SourceError('SOURCE_DISABLED')
    role, ident = selected.get('role'), selected.get('id')
    row = find(event, role, ident)
    if not row or selected.get('title') != event['title']:
        raise SourceError('EPG_REVISION_CHANGED')
    url = row['url']
    qualified = not safe(url) and qualified_origin(event, url, row['source'])
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
    return dict(id=ident, source=SOURCE, media_type86='event', role=role, verified85=True)

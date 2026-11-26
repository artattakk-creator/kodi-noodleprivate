"""Typed image candidates from locally verified EPG Agent event facts."""

SOURCES = {'agent_tmdb': 'tmdb', 'agent_tvmaze': 'tvmaze', 'agent_xmltv': 'xmltv'}
VIEW_ROLE = {'hero': 'backdrop', 'details': 'episode_still', 'card': 'poster'}
VIEW_ROLES = {
    'hero': ('backdrop', 'legacy_icon'),
    'details': ('episode_still', 'backdrop', 'poster', 'legacy_icon'),
    'card': ('poster', 'legacy_icon'),
}
ROLE_ORDER = ('backdrop', 'episode_still', 'poster', 'legacy_icon')
PERSON_ROLES = ('person', 'character')
PERSON_VIEWS = ('person1', 'person2')
INDEX_FIELDS = ('_agent_generation103', '_agent_event104')
REFERENCE_CODES = frozenset(('AGENT_REFERENCE_MISSING', 'AGENT_REFERENCE_REJECTED',
                             'AGENT_REFERENCE_UNAVAILABLE', 'AGENT_ROLE_MISSING', 'AGENT_ART_DISABLED'))


def pictures_enabled():
    from utils import setting_bool
    from epg_handoff63 import profile_scope
    import xbmcgui

    return (setting_bool('epg_agent_enabled', False) and
            xbmcgui.Window(10000).getProperty('XCMate.Agent103.Variant.' + profile_scope()) in ('', 'artwork'))


def allowed(source):
    from epg_handoff63 import profile_scope
    import xbmcgui

    return (source in SOURCES and pictures_enabled() and
            xbmcgui.Window(10000).getProperty('XCMate.Storage92.Disabled.' + profile_scope()) != 'true')


def policy():
    """Receipt policy for imported programme images only."""
    import hashlib
    import json
    from epg_handoff63 import profile_scope
    from utils import setting

    fields = (profile_scope(), pictures_enabled(), setting('programme_image_hosts55', ''))
    return hashlib.sha256(json.dumps(fields, separators=(',', ':')).encode()).hexdigest()


def view(event):
    requested = event.get('_art_view499')
    if isinstance(requested, str) and (requested in VIEW_ROLE or requested in PERSON_VIEWS):
        return requested
    return 'details' if event.get('_detail93') else 'hero'


def typed(event):
    images = event.get('agent_art')
    return isinstance(images, dict) and any(role in images for role in ROLE_ORDER)


def source_status(event, requested=None, admitted=None):
    """Describe the exact feed stage before an optional lookup is considered."""
    images = event.get('agent_art')
    agent = bool(images or event.get('_agent_event104') or event.get('epg_source46') == 'agent')
    if not agent:
        return 'READY' if event.get('xmltv_image') or event.get('provider_image') else 'NO_SOURCE_FACTS'
    if not images:
        state=event.get('_agent_images104')
        return {'REJECTED':'AGENT_REFERENCE_REJECTED','ADMITTED':'AGENT_REFERENCE_UNAVAILABLE'}.get(state,'AGENT_REFERENCE_MISSING')
    if requested is None:
        return 'READY'
    if not any(allowed(source) for source in SOURCES):
        return 'AGENT_ART_DISABLED'
    roles = PERSON_ROLES if requested in PERSON_VIEWS else VIEW_ROLES.get(requested, ())
    if not any(role in images for role in roles):
        return 'AGENT_ROLE_MISSING'
    if admitted is None:
        admitted=candidates(event, requested)
    return 'READY' if admitted else 'AGENT_REFERENCE_REJECTED'


def manual(value):
    return bool(value.get('manual85') or value.get('match') == 'MANUAL_CONFIRMED'
                or value.get('source') == 'user_local86')


def fits(value, requested):
    if requested in PERSON_VIEWS:
        return (not value or value.get('source') in (None, '', 'placeholder')
                or (value.get('source') in SOURCES and value.get('match') == 'EXACT_EVENT'
                    and value.get('role81') in PERSON_ROLES and value.get('decoded88') is True))
    if value and value.get('role81') in PERSON_ROLES:
        return False
    if not value or value.get('source') in (None, '', 'placeholder'):
        return True
    role = value.get('role81')
    if manual(value):
        return role not in ('poster', 'episode_still') if requested == 'hero' else (
            role == 'poster' if requested == 'card' else True)
    if value.get('source') not in SOURCES:
        return True
    if role not in VIEW_ROLES[requested]:
        return False
    if role == 'legacy_icon' and requested == 'hero':
        return image_shape('backdrop', {'decoded77': value.get('decoded77'),
                           'width': value.get('image_width77'), 'height': value.get('image_height77')})
    return True


def selected(value, requested):
    return requested in VIEW_ROLE and value.get('role81') == VIEW_ROLE[requested]


def role_priority(value, requested):
    roles = VIEW_ROLES.get(requested, ())
    role = value.get('role81')
    return (not manual(value), roles.index(role)) if role in roles else None


def image_shape(role, checked):
    """Actual decoded dimensions are authoritative over a feed's attributes."""
    if not isinstance(checked, dict) or not checked.get('decoded77'):
        return False
    width, height = checked.get('width', 0), checked.get('height', 0)
    if type(width) is not int or type(height) is not int or min(width, height) < 64:
        return False
    if role == 'poster':
        return .4 <= width / height <= .89
    if role in PERSON_ROLES:
        return .4 <= width / height <= 1
    if role in ('episode_still', 'backdrop'):
        return 1.3 <= width / height <= 2.5
    return True


def _receipt(event, requested):
    import hashlib
    from programme_requests68 import identity
    from programme_image69 import fingerprint
    tag = hashlib.sha256((identity(event) + policy() + fingerprint(event, 'agent_xmltv') + '|' + requested).encode()).hexdigest()
    bucket = int(tag[:8], 16)
    slot = 192 + 8 * PERSON_VIEWS.index(requested) + bucket % 8 if requested in PERSON_VIEWS else bucket % 192
    return tag, 'XCMate.TypedArt499.' + str(slot)


def remember(event, requested, value):
    import json
    import xbmcgui
    from programme_image69 import proof

    if value.get('source') == 'placeholder' or not fits(value, requested):
        return
    payload = proof(value)
    if not payload:
        return
    tag, slot = _receipt(event, requested)
    xbmcgui.Window(10000).setProperty(slot, json.dumps({
        'key': tag, 'proof': payload, 'attribution': str(value.get('attribution', ''))[:500],
    }, separators=(',', ':')))


def read(event, requested):
    import json
    import xbmcgui
    from programme_image69 import unpack

    try:
        tag, slot = _receipt(event, requested)
        raw = xbmcgui.Window(10000).getProperty(slot)
        item = json.loads(raw) if raw and len(raw) <= 12288 else {}
        if item.get('key') != tag:
            return None
        value = unpack(item.get('proof'), event)
        if value and fits(value, requested):
            return dict(value, attribution=item.get('attribution', ''))
    except (TypeError, ValueError, AttributeError, RuntimeError):
        pass
    return None


def candidates(event, requested=None):
    if requested in PERSON_VIEWS:
        index = PERSON_VIEWS.index(requested)
        return person_candidates(event)[index:index + 1]
    roles = VIEW_ROLES[requested] if requested else ROLE_ORDER
    return _candidates(event, roles)


def person_candidates(event):
    from epg_agent100_art import validator

    admit = validator()
    result = []
    seen = set()
    for row in _candidates(event, PERSON_ROLES):
        uri = row['url']
        verified = admit(uri)
        if uri in seen or not verified or verified['source'] != row['source']:
            continue
        seen.add(uri)
        result.append(dict(row, attribution=verified['attribution']))
        if len(result) == len(PERSON_VIEWS):
            break
    return result


def _candidates(event, roles):
    raw = event.get('agent_art')
    if not isinstance(raw, dict):
        return []
    result = []
    for role in roles:
        primary = raw.get(role)
        if not isinstance(primary, dict):
            continue
        alternatives = primary.get('alternatives', [])
        rows = [primary, *alternatives[:4]] if isinstance(alternatives, list) else [primary]
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            source = row.get('source')
            uri = row.get('url')
            if (not isinstance(source, str) or source not in SOURCES or SOURCES[source] != row.get('provider')
                    or not allowed(source) or row.get('match') != 'EXACT_EVENT'
                    or not isinstance(uri, str) or len(uri) > 2048 or uri in seen):
                continue
            verified = validate_url(uri, source, qualified=bool(event.get('canonical')))
            if not verified or verified['source'] != source:
                continue
            seen.add(uri)
            result.append(dict(source=source, match='EXACT_EVENT', role81=role, url=uri,
                               attribution=row.get('attribution', verified['attribution'])[:500]
                               if isinstance(row.get('attribution'), str) else verified['attribution']))
    return result



def validate_url(uri, source, *, qualified=False):
    from urllib.parse import urlsplit
    from epg_agent100_art import validator

    provider = SOURCES.get(source)
    if not provider or not isinstance(uri, str) or '?' in uri or '#' in uri:
        return None
    checked = validator()(uri, provider)
    if not checked and qualified and provider == 'xmltv':
        # For an exact stored programme origin the worker still requires
        # programme_origin75's credential checks, pinned DNS and decode.
        try:
            host = urlsplit(uri).hostname
            if host and '.' in host and not host.endswith('.test'):
                checked = validator({host})(uri, provider)
        except (TypeError, ValueError):
            pass
    return checked

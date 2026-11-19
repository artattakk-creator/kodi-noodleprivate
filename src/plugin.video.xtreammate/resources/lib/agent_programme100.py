"""Typed image candidates from locally verified EPG Agent event facts."""

SOURCES = {'agent_tmdb': 'tmdb', 'agent_tvmaze': 'tvmaze', 'agent_xmltv': 'xmltv'}
VIEW_ROLE = {'hero': 'backdrop', 'details': 'episode_still', 'card': 'poster'}
ROLE_ORDER = (*VIEW_ROLE.values(), 'legacy_icon', 'thumb')


def allowed(source):
    from utils import setting_bool
    from epg_handoff63 import profile_scope
    import xbmcgui

    if not setting_bool('epg_agent_enabled', False):
        return False
    if xbmcgui.Window(10000).getProperty('XCMate.Storage92.Disabled.' + profile_scope()) == 'true':
        return False
    if source == 'agent_tmdb':
        return (setting_bool('programme_tmdb46', False) and setting_bool('tmdb_research43', False)
                and not setting_bool('programme_tmdb_optout77', False))
    if source == 'agent_tvmaze':
        return setting_bool('programme_tvmaze67', False) and not setting_bool('programme_tvmaze_optout77', False)
    return source == 'agent_xmltv' and setting_bool('programme_xmltv96', True)


def view(event):
    requested = event.get('_art_view499')
    if isinstance(requested, str) and requested in VIEW_ROLE:
        return requested
    return 'details' if event.get('_detail93') else 'hero'


def typed(event):
    images = event.get('agent_art')
    return isinstance(images, dict) and any(role in images for role in ROLE_ORDER)


def manual(value):
    return bool(value.get('manual85') or value.get('match') == 'MANUAL_CONFIRMED'
                or value.get('source') == 'user_local86')


def fits(value, requested):
    if not value or manual(value) or value.get('source') not in SOURCES:
        return True
    return value.get('role81') in (VIEW_ROLE[requested], 'legacy_icon')


def selected(value, requested):
    return value.get('role81') == VIEW_ROLE[requested]


def image_shape(role, checked):
    """Actual decoded dimensions are authoritative over a feed's attributes."""
    if not isinstance(checked, dict) or not checked.get('decoded77'):
        return False
    width, height = checked.get('width', 0), checked.get('height', 0)
    if type(width) is not int or type(height) is not int or min(width, height) < 64:
        return False
    if role == 'poster':
        return .4 <= width / height <= .89
    if role in ('episode_still', 'backdrop'):
        return 1.3 <= width / height <= 2.5
    return True


def _receipt(event, requested):
    import hashlib
    from programme_requests68 import identity
    from programme_policy68 import negative_scope
    tag = hashlib.sha256((identity(event) + negative_scope(event) + '|' + requested).encode()).hexdigest()
    return tag, 'XCMate.TypedArt499.' + str(int(tag[:8], 16) % 192)


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
    from urllib.parse import urlsplit

    raw = event.get('agent_art')
    if not isinstance(raw, dict):
        return []
    result = []
    roles = (VIEW_ROLE[requested], 'legacy_icon') if requested else ROLE_ORDER
    for role in roles:
        row = raw.get(role)
        if not isinstance(row, dict):
            continue
        source = row.get('source')
        uri = row.get('url')
        if (not isinstance(source, str) or source not in SOURCES or SOURCES[source] != row.get('provider')
                or not allowed(source) or row.get('match') != 'EXACT_EVENT'
                or not isinstance(uri, str) or len(uri) > 2048):
            continue
        try:
            parsed = urlsplit(uri)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.port not in (None, 443) or (
                    parsed.username is not None or parsed.password is not None or '?' in uri or '#' in uri):
                continue
        except ValueError:
            continue
        credit = row.get('attribution')
        result.append(dict(source=source, match='EXACT_EVENT', role81=role, url=uri,
                           attribution=credit[:500] if isinstance(credit, str) else 'XCMate EPG Agent'))
    return result

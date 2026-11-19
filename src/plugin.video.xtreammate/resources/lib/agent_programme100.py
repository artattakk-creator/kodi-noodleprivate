"""Typed image candidates from locally verified EPG Agent event facts."""

SOURCES = {'agent_tmdb': 'tmdb', 'agent_tvmaze': 'tvmaze', 'agent_xmltv': 'xmltv'}
ROLE_ORDER = ('backdrop', 'episode_still', 'poster', 'thumb')


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


def candidates(event, home=False):
    from urllib.parse import urlsplit

    raw = event.get('agent_art')
    if not isinstance(raw, dict):
        return []
    result = []
    for role in ROLE_ORDER:
        if home and role == 'thumb':
            continue
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

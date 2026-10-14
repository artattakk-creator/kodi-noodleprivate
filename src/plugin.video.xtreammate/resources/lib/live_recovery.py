"""Fail-closed XCMate ownership check for an already playing Kodi stream.

Kodi's video player can outlive the short-lived add-on invocation that called
setResolvedUrl / Player.play. On some Android hosts the home-window marker is
missing even though the Xtream stream is playing. Recover only by exact local
matching against an active configured portal and an allowed live stream ID.

URLs with credentials stay in memory. Never log, persist, display or return
the video URL. Never match VOD/series, external player streams, or other addons.
No server/network API request is allowed in this service-loop function.
"""
import re
import urllib.parse

_ID_WITH_EXTENSION = re.compile(r'^([0-9]+)\.(ts|m3u8)$', re.IGNORECASE)
_LIVE_ACTIONS = frozenset(('play_live', 'play_start', 'play_start_direct'))


def _eligible_stream_id(client, portal, sid):
    if sid == str(portal.get('start_stream_id') or ''):
        return True
    streams = client.get_cached_catalog('get_live_streams')
    if not isinstance(streams, list):
        return False
    return any(isinstance(c, dict) and str(c.get('stream_id', '')) == sid
               for c in streams)


def recover_from_player_path(playing_file, portals, client_factory):
    """Return (portal_id, stream_id) on verified Xtream live match; else None.

    This is a conservative recognition hint, not an authorization decision
    for portal access. Portals should already be the enabled portal subset.
    """
    if not isinstance(playing_file, str) or not playing_file:
        return None
    # Kodi may append request headers after a pipe. Strip headers, don't log.
    playback = playing_file.partition('|')[0]
    parsed = urllib.parse.urlsplit(playback)
    valid_portals = [p for p in portals if isinstance(p, dict)
                     and p.get('type') == 'xtream' and p.get('id')]
    if parsed.scheme == 'plugin':
        if parsed.netloc != 'plugin.video.xtreammate':
            return None
        args = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        if args.get('action') not in _LIVE_ACTIONS:
            return None
        pid = args.get('pid', '')
        for portal in valid_portals:
            if str(portal['id']) != pid:
                continue
            sid = str(args.get('sid') or portal.get('start_stream_id') or '')
            if not sid.isdecimal():
                return None
            client = client_factory(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
            return (pid, sid) if _eligible_stream_id(client, portal, sid) else None
        return None
    if parsed.scheme not in ('http', 'https'):
        return None
    match = _ID_WITH_EXTENSION.fullmatch(parsed.path.rsplit('/', 1)[-1])
    if match is None:
        return None
    sid, ext = match.group(1), match.group(2).lower()
    for portal in valid_portals:
        try:
            client = client_factory(portal['xc_host'], portal['xc_user'],
                                    portal['xc_pass'])
            # Equality includes configured server, username, password, path,
            # query and port: matching just the hostname is NOT sufficient.
            if playback != client.live_stream_url(sid, ext):
                continue
            if _eligible_stream_id(client, portal, sid):
                return str(portal['id']), sid
        except (TypeError, ValueError, KeyError):
            continue
    return None

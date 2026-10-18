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
import json
import time

_ID_WITH_EXTENSION = re.compile(r'^([0-9]+)\.(ts|m3u8)$', re.IGNORECASE)
_LIVE_ACTIONS = frozenset(('play_live', 'play_start', 'play_start_direct'))
ITEM_ID = 'xcmate_live'


def _url_identity(value):
    """Normalize equivalent URI spellings, never different origins or tokens."""
    p=urllib.parse.urlsplit(value.partition('|')[0])
    port=p.port or {'http':80,'https':443}.get(p.scheme.lower())
    path=tuple(urllib.parse.unquote(s, errors='strict') for s in p.path.split('/'))
    query=urllib.parse.parse_qsl(p.query,keep_blank_values=True,errors='strict')
    return (p.scheme.lower(),p.hostname,port,p.username,p.password,path,tuple(query),p.fragment)


def tag_live_item(item, session):
    if not isinstance(session, dict): return False
    try:
        # Kodi 21 InfoTagVideo is transferred by setResolvedUrl / Player.play.
        # The tag contains only the opaque session ID and local stream IDs.
        identity={k:session[k] for k in ('pid','sid','nonce','at')}
        item.getVideoInfoTag().setUniqueIDs({ITEM_ID:json.dumps(identity,separators=(',',':'))})
        return True
    except (AttributeError, RuntimeError, TypeError, KeyError):
        return False


def playback_match(player, portals, client_factory, session=None):
    """Return verified (portal, stream), evidence code; never return the URL."""
    if not player.isPlayingVideo(): return None,'NO_VIDEO'
    try:
        raw=player.getVideoInfoTag().getUniqueID(ITEM_ID)
        tag=json.loads(raw)
    except Exception:
        tag=None
    try:
        if isinstance(tag,dict) and session and str(tag.get('sid','')).isdecimal():
            if all(tag.get(k)==session.get(k) for k in ('pid','sid','nonce','at')) and tag.get('nonce'):
                if 0<=time.time()-float(tag.get('at',0))<86400:
                    if any(str(p.get('id'))==str(tag['pid']) and p.get('type')=='xtream'
                           and p.get('enabled',True) for p in portals):
                        return (str(tag['pid']),str(tag['sid'])),'ITEM_IDENTITY'
    except (ValueError,TypeError,KeyError):
        pass
    try:
        path=player.getPlayingFile()
        match=recover_from_player_path(path,portals,client_factory)
        if match: return match,'URL_IDENTITY'
        if not path: return None,'PLAYER_PATH_EMPTY'
        parsed=urllib.parse.urlsplit(path.partition('|')[0])
        if parsed.scheme not in ('http','https','plugin'): return None,'UNSUPPORTED_PROTOCOL'
        if parsed.scheme=='plugin' and parsed.netloc!='plugin.video.xtreammate':
            return None,'FOREIGN_PLUGIN'
        return None,'URL_NOT_VERIFIED'
    except Exception:
        return None,'PLAYER_PATH_ERROR'


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
                     and p.get('type') == 'xtream' and p.get('id') and p.get('enabled',True)]
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
    match = _ID_WITH_EXTENSION.fullmatch(urllib.parse.unquote(parsed.path.rsplit('/', 1)[-1]))
    if match is None:
        return None
    sid, ext = match.group(1), match.group(2).lower()
    matches=[]
    for portal in valid_portals:
        try:
            client = client_factory(portal['xc_host'], portal['xc_user'],
                                    portal['xc_pass'])
            # Equality includes configured server, username, password, path,
            # query and port: matching just the hostname is NOT sufficient.
            if _url_identity(playback) != _url_identity(client.live_stream_url(sid, ext)):
                continue
            if _eligible_stream_id(client, portal, sid):
                matches.append((str(portal['id']),sid))
        except (TypeError, ValueError, KeyError):
            continue
    return matches[0] if len(matches)==1 else None

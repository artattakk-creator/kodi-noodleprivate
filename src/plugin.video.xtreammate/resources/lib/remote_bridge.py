"""Fullscreen keymap bridge, active only for an XCMate live TV session.

Kodi loads window-specific keymaps globally. When no XCMate session is
active, forward the original Kodi command; do not hijack other add-ons.
"""
import sys
import json
import time
import uuid
import xbmc
import xbmcgui

ACTIONS = frozenset((
    'left','right','up','down','ok','back','menu','epg','info','play_pause',
    'long_left','long_right','long_up','long_down','long_ok','long_back',
    'long_menu','long_play_pause',
))

BASE_ACTIONS = {
    'left': 'left', 'right': 'right', 'up': 'up', 'down': 'down',
    'ok': 'select', 'back': 'back', 'menu': 'contextmenu',
    'epg': 'osd', 'info': 'info', 'play_pause': 'pause',
}


def route(action, window=None, player=None, now=None):
    """Side-effectful but credential-free dispatch, testable with stub APIs."""
    if action not in ACTIONS:
        return False
    if window is None:
        window = xbmcgui.Window(10000)
    if player is None:
        player = xbmc.Player()
    if now is None:
        now = time.time()
    try:
        session = json.loads(window.getProperty('XtreamMate.LiveSession') or '{}')
        active = (player.isPlayingVideo()
                  and session.get('pid') and session.get('sid')
                  and session.get('nonce')
                  and 0 <= now-float(session.get('at', 0)) < 86400)
    except (ValueError, TypeError, KeyError):
        active = False
    window.setProperty('XtreamMate.LastRemoteKey',
                       '{} ({})'.format(action, 'XCMate' if active else 'Kodi'))
    if active:
        window.setProperty('XtreamMate.RemoteCommand', json.dumps({
            'action': action, 'at': now, 'nonce': uuid.uuid4().hex,
        }))
    else:
        base = action[5:] if action.startswith('long_') else action
        xbmc.executebuiltin('Action({})'.format(BASE_ACTIONS[base]))
    return bool(active)


if __name__ == '__main__':
    route(sys.argv[1] if len(sys.argv) > 1 else '')

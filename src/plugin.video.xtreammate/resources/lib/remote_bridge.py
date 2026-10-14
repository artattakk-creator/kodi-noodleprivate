"""Kodi fullscreen keymap entrypoint. Runs briefly and never fetches credentials."""
import sys
import json
import time
import uuid
import xbmc
import xbmcgui

# A legacy keymap can remain even when the IPTV add-on's playback has ended.
# In that case, forward the key to the ordinary Kodi player controls.
ACTION = sys.argv[1] if len(sys.argv) > 1 else 'left'
FALLBACK = {'left':'left', 'ok':'select', 'more':'select', 'up':'up', 'down':'down', 'epg':'osd'}
window = xbmcgui.Window(10000)
try:
    session = json.loads(window.getProperty('XtreamMate.LiveSession') or '{}')
    active = (xbmc.Player().isPlayingVideo() and session.get('pid') and
              session.get('sid') and session.get('nonce') and
              0 <= time.time()-float(session.get('at', 0)) < 86400)
except (TypeError, ValueError, KeyError):
    active = False
window.setProperty('XtreamMate.LastRemoteKey', '{} ({})'.format(ACTION, 'XtreamMate' if active else 'Kodi'))
if active and ACTION in FALLBACK:
    window.setProperty('XtreamMate.RemoteCommand', json.dumps({
        'action': ACTION, 'at': time.time(), 'nonce': uuid.uuid4().hex}))
else:
    xbmc.executebuiltin('Action({})'.format(FALLBACK.get(ACTION, 'select')))

"""Stop only a verified XCMate item when fullscreen playback is left.

Overlay Back stays in fullscreen and does not call this stop path. Never infer
ownership from a stale property alone, a title, a window, or a provider URL.
"""
import json
import time

_armed=None


def _session(raw):
    try:
        value=json.loads(raw) if raw and len(raw)<=4096 else None
        if (isinstance(value,dict) and all(isinstance(value.get(k),str) and value[k]
                for k in ('pid','sid','nonce')) and 0<=time.time()-float(value.get('at',0))<86400):
            return value
    except (ValueError,TypeError,OverflowError): pass
    return None


def identity(player):
    import xbmcgui
    if not player.isPlayingVideo(): return None
    tag=player.getVideoInfoTag()
    from media_progress import PROPERTY,UNIQUE_ID
    value=_session(xbmcgui.Window(10000).getProperty(PROPERTY))
    if value and value.get('kind') in ('vod','episode','series_item') and tag.getUniqueID(UNIQUE_ID)==value['nonce']:
        return 'media',value
    # Live dialog Back can clear the announcement while the item remains live.
    # Its immutable item identity is still the ownership evidence.
    from live_recovery import ITEM_ID
    value=_session(tag.getUniqueID(ITEM_ID))
    if value: return 'live',value
    return None


def _same(a,b):
    return bool(a and b and a[0]==b[0] and all(
        a[1].get(k)==b[1].get(k) for k in ('nonce','pid','sid','at')))


def stop_owned(player=None,pid=None,expected=None):
    """Explicit UI return/exit. Snapshot current progress BEFORE stopping audio.

    A final identity check protects against a foreign item taking over while
    SQLite persists the bookmark. Missing ownership always fails closed.
    """
    global _armed
    import xbmc,xbmcgui
    player=player or xbmc.Player()
    try:
        token=identity(player)
        if not token or (pid is not None and token[1]['pid']!=str(pid)) or (expected and not _same(token,expected)):
            return False
        if token[0]=='media':
            from media_state import save_progress
            from media_progress import _current,_last
            try:
                sample=(float(player.getTime()),float(player.getTotalTime()))
            except (RuntimeError,TypeError,ValueError):
                sample=_last if _current and _current.get('nonce')==token[1]['nonce'] else None
            if sample:
                try: save_progress(token[1],*sample)
                except Exception:
                    # A failed disk must not leave unwanted audio playing.
                    from utils import warn
                    warn('XCMate exit checkpoint: WRITE_FAILED')
        if not _same(token,identity(player)): return False
        player.stop()
        marker=xbmcgui.Window(10000)
        from media_progress import PROPERTY
        SESSION_KEY='XtreamMate.LiveSession'
        key=PROPERTY if token[0]=='media' else SESSION_KEY
        value=_session(marker.getProperty(key))
        if value and value['nonce']==token[1]['nonce']: marker.clearProperty(key)
        if _same(_armed,token): _armed=None
        # Prevent periodic tracking from replacing the final checkpoint with an
        # older 15-second sample on its next stop notification.
        if token[0]=='media':
            import media_progress
            if media_progress._current and media_progress._current.get('nonce')==token[1]['nonce']:
                media_progress._current=media_progress._last=None
        return True
    except (AttributeError,RuntimeError,TypeError,ValueError): return False


def poll(player=None,fullscreen=None):
    global _armed
    import xbmc
    player=player or xbmc.Player()
    try:
        token=identity(player)
        if not token: _armed=None;return False
        if fullscreen is None:
            if not hasattr(xbmc,'getCondVisibility'): return False
            fullscreen=xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)')
        if fullscreen:
            _armed=token
            return False
        if not _same(_armed,token):
            _armed=None
            return False  # Pending startup must never be mistaken for exit.
        return stop_owned(player,expected=_armed)
    except (AttributeError,RuntimeError,TypeError,ValueError): return False

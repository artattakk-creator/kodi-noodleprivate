"""Stop only a verified XCMate item when fullscreen playback is left.

Overlay Back stays in fullscreen and does not call this stop path. Never infer
ownership from a stale property alone, a title, a window, or a provider URL.
"""
import json
import time
import hashlib

_armed=None
STOP_KEY='XCMate.PlaybackStopping'
_observed=None


def _trace(code, **fields):
    # Queue only: no profile/SQLite/network writes on the GUI exit callback.
    try:
        from live_diagnostics import record
        record('exit',code,**fields)
    except Exception: pass
    try:
        import xbmc
        xbmc.log('[XCMate][EXIT] '+code+' '+json.dumps(fields,sort_keys=True),xbmc.LOGINFO)
    except Exception: pass


def _fingerprint(token):
    return hashlib.sha256(json.dumps([token[0]]+[token[1].get(k) for k in ('pid','sid','nonce','at','kind','series_id','season','episode')]).encode()).hexdigest()


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
        marker=xbmcgui.Window(10000)
        try:
            pending=json.loads(marker.getProperty(STOP_KEY)[:256] or '{}')
            if pending.get('item')==_fingerprint(token) and 0<=time.monotonic()-float(pending.get('at',0))<2:
                _trace('STOP_PENDING',pending=True)
                return False
        except (ValueError,TypeError,AttributeError): pass
        began=time.monotonic();_trace('EXIT_REQUESTED',video=True)
        if token[0]=='media':
            from media_state import save_progress
            from media_progress import _current,_last
            try:
                sample=(float(player.getTime()),float(player.getTotalTime()))
            except (RuntimeError,TypeError,ValueError):
                sample=_last if _current and _current.get('nonce')==token[1]['nonce'] else None
            if sample:
                try:
                    saved=save_progress(token[1],*sample)
                    _trace('RESUME_CHECKPOINT',resume_saved=bool(saved),duration_ms=(time.monotonic()-began)*1000)
                except Exception:
                    # A failed disk must not leave unwanted audio playing.
                    from utils import warn
                    warn('XCMate exit checkpoint: WRITE_FAILED')
        if not _same(token,identity(player)): return False
        marker.setProperty(STOP_KEY,json.dumps({'item':_fingerprint(token),'at':time.monotonic()}))
        try: player.stop()
        except (RuntimeError,TypeError,ValueError):
            marker.clearProperty(STOP_KEY)
            _trace('STOP_FAILED',video=True)
            return False
        _trace('STOP_SENT',duration_ms=(time.monotonic()-began)*1000,video=True)
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
    global _armed,_observed
    import xbmc
    player=player or xbmc.Player()
    try:
        token=identity(player)
        if not token:
            if _observed is not None: _trace('NO_OWNED_VIDEO',video=bool(player.isPlayingVideo()))
            _observed=None;_armed=None;return False
        if token[0]=='media':
            from media_intent import cancelled
            if cancelled(token[1]): return stop_owned(player,expected=token)
        if fullscreen is None:
            if not hasattr(xbmc,'getCondVisibility'): return False
            fullscreen=xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)')
        state=(_fingerprint(token),bool(fullscreen))
        if state!=_observed:
            try:
                import xbmcgui
                _trace('FULLSCREEN' if fullscreen else 'NAVIGATION',video=True,fullscreen=bool(fullscreen),
                    window_id=xbmcgui.getCurrentWindowId() if hasattr(xbmcgui,'getCurrentWindowId') else 0,
                    dialog_id=xbmcgui.getCurrentWindowDialogId() if hasattr(xbmcgui,'getCurrentWindowDialogId') else 0,
                    busy=bool(xbmc.getCondVisibility('Window.IsActive(busydialog)') or xbmc.getCondVisibility('Window.IsActive(busydialognocancel)')))
            except Exception: _trace('WINDOW_STATE_UNAVAILABLE')
            _observed=state
        if fullscreen:
            _armed=token
            return False
        if not _same(_armed,token):
            _armed=None
            return False  # Pending startup must never be mistaken for exit.
        return stop_owned(player,expected=_armed)
    except (AttributeError,RuntimeError,TypeError,ValueError): return False

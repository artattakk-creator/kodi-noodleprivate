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
    try:
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
    except (AttributeError,RuntimeError,TypeError,ValueError):return None


def _same(a,b):
    return bool(a and b and a[0]==b[0] and all(
        a[1].get(k)==b[1].get(k) for k in ('nonce','pid','sid','at')) and
        (a[0]!='media' or a[1].get('kind')==b[1].get('kind')))


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
        checkpoint_ok=True;sample=None
        if token[0]=='media':
            if token[1].get('autoplay_chain'):
                from media_autoplay import request_cancel
                request_cancel(token[1]['autoplay_chain'],token[1]['pid'])
            from exit_jobs import trace
            trace('PROGRESS_SNAPSHOT_START',token)
            from media_state import save_progress
            from media_progress import _current,_last
            try:
                sample=(float(player.getTime()),float(player.getTotalTime()))
            except (RuntimeError,TypeError,ValueError):
                sample=_last if _current and _current.get('nonce')==token[1]['nonce'] else None
            if sample:
                try: save_progress(token[1],*sample,timeout=.05)
                except Exception:
                    checkpoint_ok=False
                    trace('PROGRESS_SNAPSHOT_FAIL',token)
                    # A failed disk must not leave unwanted audio playing.
                    from utils import warn
                    warn('XCMate exit checkpoint: WRITE_FAILED')
                if checkpoint_ok:trace('PROGRESS_SNAPSHOT_DONE',token)
        if not _same(token,identity(player)): return False
        from exit_jobs import trace
        trace('PLAYER_STOP_START',token)
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
            if not checkpoint_ok and sample:
                media_progress.queue_exit_checkpoint(token[1],sample)
                media_progress._current=media_progress._last=None
            elif media_progress._current and media_progress._current.get('nonce')==token[1]['nonce']:
                media_progress._current=media_progress._last=None
        return True
    except (AttributeError,RuntimeError,TypeError,ValueError): return False


def poll(player=None,fullscreen=None):
    """Window visibility is observation, NEVER evidence of a user's exit.

    Kodi can toggle fullscreen while starting/initializing a decoder or opening
    an audio/OSD dialog. Only an explicitly cancelled resolver/chain may stop
    here. Back/Stop are emitted by the owning input handlers with a reason.
    """
    global _armed
    _armed=None
    from exit_jobs import blocked,request
    if blocked():return False
    import xbmc
    player=player or xbmc.Player()
    try:
        token=identity(player)
        if token and token[0]=='media':
            from media_intent import cancelled
            if cancelled(token[1]):
                return request(player,expected=token,reason='AUTOPLAY_CANCEL' if token[1].get('autoplay_chain') else 'STARTUP_ABORT')
        return False
    except (AttributeError,RuntimeError,TypeError,ValueError):return False

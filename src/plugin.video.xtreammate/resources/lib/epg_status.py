"""Bounded, atomic, per-portal/source import outcomes without source addresses."""
import hashlib
import json
import os
import tempfile
import threading
import time

_LOCK = threading.RLock()


def _path(pid):
    from utils import addon_data_dir
    key = hashlib.sha256(str(pid).encode()).hexdigest()[:24]
    return os.path.join(addon_data_dir(), 'xcmate_epg_status_'+key+'.json')


def source_key(source):
    return hashlib.sha256(str(source.get('id', '')).encode()).hexdigest()[:24]


def read(pid):
    try:
        with open(_path(pid), encoding='utf-8') as f: raw = f.read(262145)
        data = json.loads(raw) if len(raw) <= 262144 else {}
        if not isinstance(data, dict): return {}
        from live_diagnostics import _clean
        return {k:safe for k,v in data.items() if isinstance(k,str)
                and (safe := _clean(v)) is not None}
    except (OSError, ValueError):
        return {}


def update(pid, key, code, **fields):
    """Import telemetry is best effort; never turn an import into a failure."""
    temp = None
    try:
        from live_diagnostics import _clean
        safe = _clean(dict(fields, stage='epg_source', code=code, at=time.time()))
        if safe is None: return
        with _LOCK:
            state = read(pid)
            previous = state.get(key, {})
            if previous.get('last_success'):
                safe.setdefault('last_success', previous['last_success'])
            for field in ('last_channels','last_programmes'):
                if field in previous: safe[field]=previous[field]
            if code == 'READY':
                safe['last_success'] = safe['at']
                for field in ('channels','programmes'):
                    if field in safe: safe['last_'+field]=safe[field]
            state[key] = safe
            # Bound obsolete source records after repeated configuration edits.
            if len(state) > 128:
                state = dict(sorted(state.items(), key=lambda item:item[1].get('at',0))[-128:])
            path = _path(pid)
            fd, temp = tempfile.mkstemp(prefix='.xcmate-source-', dir=os.path.dirname(path))
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(state, f, separators=(',', ':'))
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp, path)
    except Exception:
        pass
    finally:
        if temp and os.path.exists(temp): os.unlink(temp)


def revision(pid):
    """Cross-process, cheap revision token. No private identifiers in value."""
    try:
        import xbmcgui
        return xbmcgui.Window(10000).getProperty('XtreamMate.EPGRevision.'+
            hashlib.sha256(str(pid).encode()).hexdigest()[:24])
    except Exception: return ''


def changed(pid):
    try:
        import xbmcgui
        xbmcgui.Window(10000).setProperty('XtreamMate.EPGRevision.'+
            hashlib.sha256(str(pid).encode()).hexdigest()[:24], str(time.time_ns()))
    except Exception: pass

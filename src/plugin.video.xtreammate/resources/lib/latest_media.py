"""Recently added Xtream movies and series, safely backed by Kodi's local cache.

Use the provider's ``added`` upload date when available. If the provider omits
upload dates, only flag IDs first observed in a SUBSEQUENT successful full
catalog scan; the first scan is a baseline, not evidence of new content.
State keys are hashes of the full catalog cache key (including service origin),
so credentials, playlist URLs, and titles are never written to the marker path.
"""
import datetime
import hashlib
import json
import os
import tempfile
import time
from threading import Lock

_LOCK = Lock()
_TYPES = {"get_vod_streams": "stream_id", "get_series": "series_id"}


def _file(catalog_key, data_dir=None):
    if data_dir is None:
        from utils import addon_data_dir
        data_dir = addon_data_dir()
    digest = hashlib.sha256(str(catalog_key).encode("utf-8")).hexdigest()
    return os.path.join(data_dir, "recent-media-{}.json".format(digest))


def _ids(entries, id_field):
    return {str(item[id_field]) for item in entries if isinstance(item, dict)
            and item.get(id_field) not in (None, "")}


def _read(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            state = json.load(fh)
        if isinstance(state, dict) and state.get("version") == 1:
            return state
    except (OSError, ValueError, TypeError):
        pass
    # Never erase a corrupt state: if it is unreadable, no 'new' claims can
    # safely be made. A subsequent scan may re-baseline after a valid backup.
    return None


def observe(catalog_key, action, entries, data_dir=None, now=None):
    """Update first-seen records only after a successful, full catalog fetch.

    Returns first-seen timestamps for verified *newly appearing* IDs. Empty
    catalogs are ignored to avoid marking everything new after provider errors.
    """
    if action not in _TYPES or not isinstance(entries, list) or not entries:
        return {}
    ids = _ids(entries, _TYPES[action])
    if not ids:
        return {}
    now = int(now if now is not None else time.time())
    path = _file(catalog_key, data_dir)
    with _LOCK:
        previous = _read(path)
        known = set(previous.get("known", [])) if previous else set()
        discovered = dict(previous.get("new", {})) if previous else {}
        # First snapshot is a baseline, never a false 'all new' list.
        if previous:
            for item_id in ids - known:
                discovered[item_id] = now
        known.update(ids)
        # Limit the incidental local snapshot size, not the provider catalog.
        discovered = {key: value for key, value in discovered.items()
                      if key in ids and isinstance(value, (int, float))
                      and now - int(value) <= 180 * 86400}
        data = {"version": 1, "known": sorted(known), "new": discovered}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".recent-media-", dir=os.path.dirname(path))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
        finally:
            if os.path.isfile(tmp):
                os.unlink(tmp)
        return discovered


def first_seen(catalog_key, action, entries, data_dir=None):
    """Read existing history, or set the baseline for a previously cached index."""
    if action not in _TYPES or not isinstance(entries, list):
        return {}
    path = _file(catalog_key, data_dir)
    state = _read(path)
    if state is None and entries:
        return observe(catalog_key, action, entries, data_dir)
    return (state or {}).get("new", {})


def added_timestamp(value, now=None):
    """Xtream 'added' timestamps: Unix seconds, milliseconds or ISO dates."""
    if value is None or isinstance(value, bool):
        return None
    now = int(now if now is not None else time.time())
    ts = None
    try:
        if isinstance(value, (int, float)) or str(value).strip().isdigit():
            ts = float(value)
            if ts > 10**11:
                ts /= 1000
        else:
            s = str(value).strip()
            dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            ts = dt.timestamp()
    except (ValueError, TypeError, OverflowError):
        return None
    if ts is None or not 946684800 <= ts <= now + 2*86400:
        return None
    return int(ts)


def recent_entries(entries, action, seen=None, limit=50, now=None):
    """Return newest recognized titles, stable on equal dates, not alphabetical."""
    if action not in _TYPES or not isinstance(entries, list):
        return []
    key = _TYPES[action]
    found = []
    for i, item in enumerate(entries):
        if not isinstance(item, dict) or item.get(key) in (None, ""):
            continue
        t = added_timestamp(item.get("added"), now=now)
        if t is None:
            t = added_timestamp(item.get("date_added"), now=now)
        if t is None:
            t = (seen or {}).get(str(item[key]))
        if t is None:
            continue
        found.append((int(t), i, item))
    found.sort(key=lambda x: (-x[0], x[1]))
    return [entry for _, _, entry in found[:max(0, int(limit))]]

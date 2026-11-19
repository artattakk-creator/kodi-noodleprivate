"""Use verified persisted Agent logos as a fallback to provider and manual logos."""
import json
import os
import time
from urllib.parse import urlsplit

_PREFIX = 'XCMate.AgentLogo100.'
_due = {}


def _enabled():
    from utils import setting_bool
    return setting_bool('epg_agent_enabled', False)


def _window():
    import xbmcgui
    return xbmcgui.Window(10000)


def _slot(tag):
    return _PREFIX + str(int(tag[:8], 16) % 1024)


def reference(tag):
    """Focus-time RAM only; downloader and source lookup run in the worker."""
    if not tag or not _enabled():
        return ''
    try:
        raw = _window().getProperty(_slot(tag))
        value = json.loads(raw) if raw and len(raw)<8192 else {}
        image = value.get('image', '')
        if value.get('key') == tag and value.get('until', 0) > time.time() and os.path.isabs(image):
            return image
    except (AttributeError, ValueError, TypeError, KeyError, RuntimeError):
        pass
    return ''


def read(portal, rows):
    if not _enabled():
        return {}
    from logo_overrides96 import identity

    result = {}
    for row in rows:
        try:
            image = reference(identity(portal, row))
            if image and os.path.isabs(image) and not os.path.islink(image) and os.path.isfile(image):
                result[str(row['sid'])] = image
        except (OSError, ValueError):
            continue
    return result


def _batch(portal, rows):
    if not _enabled():
        return {}
    try:
        from epg_agent100_art import logos
        return logos(str(portal['id']), [str(row['sid']) for row in rows[:256]])
    except (ImportError, OSError, ValueError, KeyError, TypeError):
        return {}


def _selected(rows, candidates):
    for row in rows[:256]:
        sid = str(row['sid'])
        url = candidates.get(sid, '')
        if not url:
            continue
        try:
            parsed = urlsplit(url)
            if (parsed.scheme != 'https' or parsed.port not in (None, 443)
                    or parsed.username is not None or parsed.password is not None
                    or not parsed.hostname or '?' in url or '#' in url):
                continue
        except ValueError:
            continue
        yield row, dict(sid=sid, stream_icon=url)


def prepare(portal, rows, cancel):
    if not rows:
        return
    from logo_manifest86 import read as local, key
    from logo_overrides96 import identity
    from logo_store89 import persist
    from media_sources43 import SourceError
    from programme_transport77 import verified

    candidates = _batch(portal, rows)
    selected = list(_selected(rows, candidates))
    existing = local(portal, [logo for _, logo in selected], with_fallback=False,
                     with_overrides=False, with_agent=False) if selected else {}
    # The shared slots contain only verified local paths and scoped IDs.
    attempts = 0
    for station, logo in selected:
        if cancel() or not _enabled():
            return
        tag = identity(portal, station)
        sid = logo['sid']
        image = existing.get(sid, '')
        if not image:
            job = key(portal, logo)
            if attempts >= 2 or _due.get(job, 0) > time.monotonic():
                continue
            attempts += 1
            _due[job] = time.monotonic() + 120
            while len(_due) > 256:
                _due.pop(next(iter(_due)))
            try:
                body = verified(logo['stream_icon'], cancel=cancel, keep_data81=True)['_body81']
                image, _ = persist(portal, logo, body, cancel)
            except (OSError, KeyError, ValueError, TypeError, SourceError, TimeoutError):
                continue
        if os.path.isabs(image) and os.path.isfile(image):
            _window().setProperty(_slot(tag), json.dumps(dict(key=tag, image=image, until=time.time()+900)))
    for station in rows[:256]:
        if str(station['sid']) not in candidates:
            tag = identity(portal, station)
            if reference(tag):
                _window().clearProperty(_slot(tag))


def next_delay(portal, rows):
    if not _enabled():
        return None
    from logo_manifest86 import key
    hits = read(portal, rows)
    now = time.monotonic()
    return min((max(.25, _due.get(key(portal, logo), 0) - now)
                for _, logo in _selected(rows, _batch(portal, rows)) if logo['sid'] not in hits), default=None)

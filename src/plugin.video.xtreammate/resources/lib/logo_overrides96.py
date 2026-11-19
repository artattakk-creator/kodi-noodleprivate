"""Explicit station choices, separate from every disposable artwork namespace.

Only profile/account/SID hashes and owned bytes are persisted. Provider rows,
private source paths and credentials are never rewritten or logged.
"""
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

MAX_IMAGE = 3 * 1024 * 1024
MAX_MANIFEST = 512 * 1024
_verified = {}
PREFIX = 'XCMate.LogoChoice96.'


def _publish(tag, uri):
    """Publish only after worker verification or an atomic explicit commit."""
    import xbmcgui
    window=xbmcgui.Window(10000);key=PREFIX+tag;old=window.getProperty(key)
    raw=json.dumps(dict(key=tag, uri=uri), separators=(',', ':'))
    if raw==old or not uri and not old:return
    window.setProperty(key,raw)


def reference(tag):
    """GUI-only shared RAM receipt; no hashing, paths, files or SQL reads."""
    if not isinstance(tag, str) or len(tag) != 64:return ''
    try:
        import xbmcgui
        raw = xbmcgui.Window(10000).getProperty(PREFIX+tag)
        value = json.loads(raw) if raw and len(raw) <= 16384 else {}
        return value['uri'] if isinstance(value, dict) and value.get('key') == tag and isinstance(value.get('uri'), str) else ''
    except (ValueError, TypeError, AttributeError, RuntimeError):return ''


def binding(portal, row, fallback='', *, scope96=None, persistent96=None):
    """Worker-prepared identity and provider fallback, independent of EPG."""
    return dict(logo_key96=identity(portal, row), logo_portal96=str(portal['id']),
                logo_sid96=str(row.get('sid') or row.get('stream_id') or ''),
                logo_provider96=row.get('stream_icon', ''), logo_base96=fallback,
                logo_scope96=scope96 if scope96 is not None else scope(portal),
                logo_persistent96=__import__('artwork_config').persistent() if persistent96 is None else persistent96)


class _Scope:
    """Opaque private RAM comparison; Channel repr never discloses secrets."""
    __slots__ = ('__profile', '__account')
    def __init__(self, portal):
        import xbmcvfs
        self.__profile = xbmcvfs.translatePath('special://profile/')
        self.__account = tuple(portal.get(k) for k in ('id', 'type', 'xc_host', 'xc_user', 'xc_pass'))
    def __repr__(self):return '<LogoScope96>'
    def matches(self, portal):
        import xbmcvfs
        return self.__profile == xbmcvfs.translatePath('special://profile/') and self.__account == tuple(portal.get(k) for k in ('id', 'type', 'xc_host', 'xc_user', 'xc_pass'))


def scope(portal):return _Scope(portal)


def root():
    from utils import addon_data_dir
    return Path(addon_data_dir()) / 'station_logo_overrides96'


def identity(portal, row):
    from epg_handoff63 import profile_scope
    sid = str(row.get('sid') or row.get('stream_id') or '')
    if not sid or len(sid) > 256 or not portal.get('id'):
        raise ValueError('LOGO_IDENTITY_REQUIRED')
    values = [profile_scope(), [portal.get(k) for k in ('id', 'type', 'xc_host', 'xc_user', 'xc_pass')], sid]
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


def _safe_root():
    folder = root()
    if folder.is_symlink() or any(p.is_symlink() for p in folder.parents):
        raise OSError('LOGO_UNSAFE_ROOT')
    return folder


def _load():
    filename = _safe_root() / 'overrides96.json'
    if filename.is_symlink():raise OSError('LOGO_UNSAFE_MANIFEST')
    if not filename.exists():return {}
    if filename.stat().st_size > MAX_MANIFEST:raise OSError('LOGO_MANIFEST_LIMIT')
    value = json.loads(filename.read_bytes())
    if not isinstance(value, dict) or value.get('format') != 1 or not isinstance(value.get('records'), dict):
        raise OSError('LOGO_MANIFEST_INVALID')
    if len(value['records']) > 512:raise OSError('LOGO_MANIFEST_LIMIT')
    return value['records']


def validated(body):
    from media_sources43 import validate_image, SourceError
    if not isinstance(body, bytes) or not 0 < len(body) <= MAX_IMAGE:
        raise ValueError('LOGO_IMAGE_LIMIT')
    if not body.startswith((b'\x89PNG\r\n\x1a\n', b'\xff\xd8\xff')):
        raise ValueError('LOGO_PNG_JPEG_REQUIRED')
    try:width, height = validate_image(body)
    except SourceError:raise ValueError('LOGO_IMAGE_INVALID') from None
    if width > 4096 or height > 4096 or width * height > 8 * 1024 * 1024:
        raise ValueError('LOGO_PIXEL_LIMIT')
    return width, height


def selection(uri, *, smb_selected=False):
    """Read only the explicitly selected local/SMB object through Kodi VFS."""
    if not isinstance(uri, str) or not uri or len(uri) > 8192 or any(ord(c) < 32 for c in uri) or '|' in uri or '\\' in uri:
        raise ValueError('LOGO_UNSAFE_SELECTION')
    parsed = urlsplit(uri)
    decoded = unquote(parsed.path)
    if any(p in ('.', '..') for p in decoded.split('/')) or parsed.query or parsed.fragment or Path(decoded).suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        raise ValueError('LOGO_UNSAFE_SELECTION')
    if parsed.scheme == 'smb':
        if smb_selected is not True or not parsed.hostname:raise ValueError('LOGO_SMB_SELECTION_REQUIRED')
    elif parsed.scheme not in ('', 'special') or parsed.scheme == '' and not os.path.isabs(uri):
        raise ValueError('LOGO_LOCAL_SELECTION_REQUIRED')
    import xbmcvfs
    if parsed.scheme != 'smb':
        path = Path(xbmcvfs.translatePath(uri))
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):raise ValueError('LOGO_UNSAFE_SELECTION')
    stream = xbmcvfs.File(uri)
    try:body = bytes(stream.readBytes(MAX_IMAGE + 1))
    finally:stream.close()
    validated(body)
    return body


def _commit(records):
    from logo_store89 import atomic, capacity
    from artwork_backend import LocalArtworkStorage
    raw = json.dumps(dict(format=1, records=records), sort_keys=True, separators=(',', ':')).encode()
    if len(records) > 512 or len(raw) > MAX_MANIFEST:raise OSError('LOGO_MANIFEST_LIMIT')
    capacity(LocalArtworkStorage(str(_safe_root())), len(raw) + 65536)
    atomic(root() / 'overrides96.json', raw)
    if _load() != records:raise OSError('LOGO_OVERRIDE_READBACK')


def save(portal, row, body, *, confirmed=False):
    if confirmed is not True:raise ValueError('LOGO_CONFIRMATION_REQUIRED')
    width, height = validated(body)
    from profile_transaction import writing
    from logo_store89 import atomic, capacity, thumbnail, MAX_ASSET
    from artwork_backend import LocalArtworkStorage
    if len(body)>MAX_ASSET or width>512 or height>256:
        body, width, height = thumbnail(body)
    tag = identity(portal, row);digest = hashlib.sha256(body).hexdigest()
    name = digest + ('.png' if body.startswith(b'\x89PNG') else '.jpg')
    with writing(timeout=.2):
        folder = _safe_root();records = _load()
        # Measure the actual persistent target, never borrow archive capacity.
        capacity(LocalArtworkStorage(str(folder)), len(body) + MAX_MANIFEST)
        atomic(folder / name, body)
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != digest:raise OSError('LOGO_OVERRIDE_READBACK')
        records[tag] = dict(file=name, sha256=digest, width=width, height=height)
        _commit(records)
        _publish(tag, str(folder / name))
    return str(folder / name)


def reset(portal, row, *, confirmed=False):
    if confirmed is not True:raise ValueError('LOGO_CONFIRMATION_REQUIRED')
    from profile_transaction import writing
    with writing(timeout=.2):
        tag = identity(portal, row)
        records = _load();records.pop(tag, None);_commit(records)
        _publish(tag, '')
    # Shared bytes are preserved. Only this exact mapping is reset.
    return True


def read(portal, rows):
    from profile_transaction import reading
    try:
        # Prevent an old worker snapshot publishing over a concurrent Save/Reset.
        with reading(timeout=.15):return _read(portal, rows)
    except (OSError, TimeoutError):return {}


def _read(portal, rows):
    try:records = _load();folder = _safe_root()
    except (OSError, ValueError, TypeError):return {}
    result = {}
    for row in rows:
        try:
            tag = identity(portal, row)
            value = records.get(tag, {})
            if not isinstance(value, dict):continue
            digest = value.get('sha256', '')
            name = value.get('file', '')
            if not re.fullmatch('[a-f0-9]{64}', digest) or not re.fullmatch(digest + r'\.(png|jpg)', name):continue
            filename = folder / name
            if filename.is_symlink():continue
            stat = filename.stat()
            if not 0 < stat.st_size <= MAX_IMAGE:continue
            stamp = (stat.st_dev, stat.st_ino, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, digest)
            if _verified.get(str(filename)) != stamp:
                if hashlib.sha256(filename.read_bytes()).hexdigest() != digest:continue
                _verified[str(filename)] = stamp
                while len(_verified) > 512:_verified.pop(next(iter(_verified)))
            result[str(row.get('sid') or row.get('stream_id'))] = str(filename)
        except (OSError, ValueError, TypeError):continue
    for row in rows:
        try:_publish(identity(portal, row), result.get(str(row.get('sid') or row.get('stream_id')), ''))
        except (ValueError, TypeError):continue
    return result

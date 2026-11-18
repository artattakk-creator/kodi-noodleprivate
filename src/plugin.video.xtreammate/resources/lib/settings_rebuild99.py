"""One user-confirmed Kodi settings rebuild, completed across process starts."""
from contextlib import contextmanager
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time
from uuid import uuid4
from xml.etree import ElementTree

SETTINGS = 'settings.xml'
STATE = '.settings99.rebuild.json'
BACKUP_PREFIX = 'settings99.before-reset.'
RECEIPT = 'settings_rebuild_receipt99'
FILE_LIMIT = 8 * 1024 * 1024
STATE_LIMIT = 4096
PENDING = {'BACKUP_SAVED', 'APPLYING', 'READBACK_OK'}

# Other values come from Kodi's installed definitions. External image sources
# stay off even if a previous token or a storage opt-in is still on disk.
DEFAULTS = {
    'epg_enabled': True,
    'programme_xmltv96': False,
    'programme_tmdb46': False,
    'tmdb_research43': False,
    'programme_tvmaze67': False,
    'programme_helper57': False,
    'programme_catalog57': False,
    'programme_tmdb_optout77': True,
    'programme_tvmaze_optout77': True,
}


class RebuildError(OSError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _process_start(pid):
    with open(f'/proc/{pid}/stat', encoding='utf-8') as stream:
        # The command name is in parentheses and may contain spaces.
        start = stream.read(4096).rsplit(')', 1)[1].split()[19]
    if not start.isdecimal():
        raise ValueError()
    return start


def process_identity():
    """A Python interpreter restart is not a Kodi process restart."""
    try:
        return f'{os.getpid()}:{_process_start("self")}'
    except (OSError, IndexError, ValueError):
        raise RebuildError('KODI_PROCESS_UNKNOWN') from None


def _process_alive(identity):
    if not identity or not re.fullmatch(r'[0-9]+:[0-9]+', identity):
        return False
    pid, start = identity.split(':')
    try:
        return _process_start(pid) == start
    except FileNotFoundError:
        return False
    except (OSError, IndexError, ValueError):
        raise RebuildError('KODI_PROCESS_UNKNOWN') from None


def _sha(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def _default_xml(receipt):
    root = ElementTree.Element('settings', version='2')
    for name, value in DEFAULTS.items():
        ElementTree.SubElement(root, 'setting', id=name).text = str(value).lower()
    ElementTree.SubElement(root, 'setting', id=RECEIPT).text = receipt
    return ElementTree.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'


def _identity(info):
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise OSError(errno.EINVAL, 'unsafe file')
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _at(directory, name):
    try:
        return _identity(os.stat(name, dir_fd=directory, follow_symlinks=False))
    except FileNotFoundError:
        return None


def _read(directory, name, limit=FILE_LIMIT):
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    except FileNotFoundError:
        return None, None
    with os.fdopen(fd, 'rb') as stream:
        identity = _identity(os.fstat(stream.fileno()))
        raw = stream.read(limit + 1)
        if len(raw) > limit or _at(directory, name) != identity:
            raise OSError(errno.EINVAL, 'read failed')
    return raw, identity


def _atomic(directory, name, data, expected, error):
    temporary = '.settings99.' + uuid4().hex + '.tmp'
    try:
        handle = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=directory)
        with os.fdopen(handle, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if _read(directory, temporary)[0] != data:
            raise RebuildError(error)
        if _at(directory, name) != expected:
            raise RebuildError('KODI_CACHE_CONFLICT')
        os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)
        if _read(directory, name)[0] != data:
            raise RebuildError(error)
    finally:
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass


@contextmanager
def _directory(profile):
    descriptor = os.open(profile, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        yield descriptor
    finally:
        os.close(descriptor)


@contextmanager
def _locked(directory):
    import fcntl
    fd = os.open('.settings99.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,
                 0o600, dir_fd=directory)
    try:
        _identity(os.fstat(fd))
        deadline = time.monotonic() + 0.5
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise RebuildError('REPAIR_BUSY') from None
                time.sleep(0.01)
        yield
    finally:
        os.close(fd)


def _state(directory):
    try:
        raw, _ = _read(directory, STATE, STATE_LIMIT)
        if raw is None:
            return None
        value = json.loads(raw)
        phase = value['phase']
        origin = value['origin']
        backup, digest = value['backup'], value['original_sha256']
        if (value.get('version') != 1 or not re.fullmatch(r'[0-9a-f]{32}', value['receipt'])
                or phase not in PENDING | {'POST_RESTART_OK', 'KODI_CACHE_CONFLICT'}
                or not isinstance(origin, str) or not origin
                or (backup is None) != (digest is None)
                or (backup is not None and not re.fullmatch(r'settings99\.before-reset\.\d+\.[0-9a-f]{32}\.xml', backup))
                or (digest is not None and not re.fullmatch(r'[0-9a-f]{64}', digest))
                or (phase in {'APPLYING', 'READBACK_OK', 'POST_RESTART_OK'} and
                    (not isinstance(value.get('applied_by'), str) or not value['applied_by']))):
            raise ValueError()
        return value
    except (OSError, ValueError, KeyError, TypeError):
        raise RebuildError('REPAIR_STATE_INVALID') from None


def _save(directory, state, phase):
    data = dict(state, phase=phase)
    _atomic(directory, STATE, json.dumps(data, sort_keys=True).encode('ascii'),
            _at(directory, STATE), 'REPAIR_STATE_INVALID')
    return data


def pending(profile):
    """Use this before creating Kodi workers or opening settings."""
    if not os.path.lexists(Path(profile) / STATE):
        return False
    try:
        with _directory(profile) as directory:
            state = _state(directory)
            return bool(state and state['phase'] in PENDING)
    except OSError:
        # Inconclusive state is handled by the startup/repair UI.
        return True


def _disk_error(error, otherwise):
    if isinstance(error, RebuildError):
        return error.code
    if error.errno in (errno.ENOSPC, errno.EDQUOT):
        return 'NO_SPACE'
    return otherwise


def stage(profile, process, report=lambda code: None):
    """Called only after the user confirms. Leave the running Kodi file alone."""
    try:
        Path(profile).mkdir(parents=True, exist_ok=True)
        with _directory(profile) as directory, _locked(directory):
            state = _state(directory)
            if state and state['phase'] == 'POST_RESTART_OK':
                return 'POST_RESTART_OK'
            if state and state['phase'] in PENDING:
                return 'RESTART_REQUIRED'
            original, identity = _read(directory, SETTINGS)
            backup = None
            digest = _sha(original)
            if original is not None:
                backup = f'{BACKUP_PREFIX}{time.time_ns()}.{uuid4().hex}.xml'
                _atomic(directory, backup, original, None, 'BACKUP_FAILED')
            if _at(directory, SETTINGS) != identity:
                raise RebuildError('KODI_CACHE_CONFLICT')
            _save(directory, dict(version=1, origin=process, backup=backup,
                                  original_sha256=digest, receipt=uuid4().hex), 'BACKUP_SAVED')
            if backup is not None:
                report('BACKUP_SAVED')
            return 'RESTART_REQUIRED'
    except OSError as error:
        raise RebuildError(_disk_error(error, 'BACKUP_FAILED')) from None


def _conflict(directory, state):
    _save(directory, state, 'KODI_CACHE_CONFLICT')
    raise RebuildError('KODI_CACHE_CONFLICT')


def _resume(directory, process, native_check, report):
    state = _state(directory)
    if not state or state['phase'] not in PENDING:
        return None
    previous = (state['origin'], state.get('applied_by'))
    if process in previous or any(_process_alive(identity) for identity in previous):
        return 'RESTART_REQUIRED'
    if state['backup'] is not None:
        try:
            backup, _ = _read(directory, state['backup'])
        except OSError:
            raise RebuildError('BACKUP_FAILED') from None
        if _sha(backup) != state['original_sha256']:
            raise RebuildError('BACKUP_FAILED')

    receipt = state['receipt']
    fresh = _default_xml(receipt)
    current, identity = _read(directory, SETTINGS)
    if state['phase'] == 'BACKUP_SAVED' or (state['phase'] == 'APPLYING' and current != fresh):
        if _sha(current) != state['original_sha256']:
            _conflict(directory, state)
        state = _save(directory, dict(state, applied_by=process), 'APPLYING')
        _atomic(directory, SETTINGS, fresh, identity, 'READBACK_FAILED')
        report('RESET_WRITTEN')
        _save(directory, state, 'READBACK_OK')
        report('READBACK_OK')
        return 'RESTART_REQUIRED'

    # After an interrupted rename, the expected file may already be on disk.
    # The applying process has gone away, so this boot can verify that result.
    if current != fresh or not native_check(receipt) or _read(directory, SETTINGS)[1] != identity:
        _conflict(directory, state)
    os.fsync(directory)
    _save(directory, state, 'POST_RESTART_OK')
    return 'POST_RESTART_OK'


def resume(profile, process, native_check, report=lambda code: None):
    """Run before any addon settings consumer on each Kodi process start."""
    if not pending(profile):
        return None
    try:
        with _directory(profile) as directory, _locked(directory):
            return _resume(directory, process, native_check, report)
    except OSError as error:
        raise RebuildError(_disk_error(error, 'READBACK_FAILED')) from None

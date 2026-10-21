"""Private, immutable theme revisions and atomic activation.

Only themes_v1 is written. Running Kodi controls keep their original textures;
playback defers a selection until the next XCMate view opened after playback.
"""
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import tempfile
import zipfile
import zlib

from theme_package import (ThemeError, MAX_ZIP, MAX_IMAGE, MAX_METADATA,
                           check_archive, check_container, digest_file, fail, image, json_object,
                           manifest, version)

_verified = {}
_asset_valid = {}


def root(create=True):
    from utils import addon_data_dir
    path = Path(addon_data_dir()) / 'themes_v1'
    if path.is_symlink(): fail('PATH')
    if create: path.mkdir(mode=0o700, exist_ok=True)
    return path


def core_version():
    import xbmcaddon
    return xbmcaddon.Addon().getAddonInfo('version')


def playing():
    import xbmc
    return bool(xbmc.Player().isPlaying())


def check_space(additional):
    if shutil.disk_usage(root()).free < additional + 32*1024*1024: fail('SPACE')


def _read(path, limit=MAX_METADATA):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit: fail('PATH')
    with path.open('rb') as stream:
        data = stream.read(limit+1)
    if len(data) > limit: fail('LIMIT')
    return data


def _atomic(path, value):
    fd, temp = tempfile.mkstemp(prefix='.selection-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, sort_keys=True); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def _state():
    try:
        data = json_object(_read(root(create=False)/'selection.json', 8192))
        if not isinstance(data, dict) or set(data)-{'active','pending'}: return {'active': ''}
        for value in data.values():
            if not isinstance(value, str) or (value and not re.fullmatch(r'[a-z][a-z0-9-]{0,47}/[0-9.]+-[a-f0-9]{64}', value)):
                return {'active': ''}
        return data
    except (OSError, ThemeError): return {'active': ''}


def _revision(name):
    # A state file is untrusted too; no arbitrary absolute paths or symlinks.
    if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,47}/[0-9.]+-[a-f0-9]{64}', name): fail('PATH')
    folder = root()/'packages'/name
    if folder.is_symlink() or folder.parent.is_symlink() or folder.parent.parent.is_symlink(): fail('PATH')
    raw = _read(folder/'theme.json')
    spec = manifest(json_object(raw), core_version())
    if folder.parent.name != spec['id'] or not folder.name.startswith(spec['version']+'-'): fail('PATH')
    paths = [folder/'theme.json'] + [folder/p for p in spec['required_files']]
    signature = []
    for path in paths:
        # Reject a replaced directory symlink, including intermediate assets/.
        for parent in (path, *path.relative_to(folder).parents):
            candidate = parent if parent.is_absolute() else folder/parent
            if candidate.is_symlink(): fail('PATH')
        stat = path.stat()
        if not path.is_file() or stat.st_size > (MAX_METADATA if path.name == 'theme.json' else MAX_IMAGE): fail('LIMIT')
        signature.append((str(path), stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino))
    signature = tuple(signature)
    if _verified.get(str(folder)) != signature:
        for relative in spec['required_files']:
            if digest_file(folder/relative, MAX_IMAGE) != spec['sha256'][relative]: fail('CHECKSUM')
        for item in signature[1:]: _asset_valid[item[0]]=item[1:]
        _verified[str(folder)] = signature
    return dict(spec=spec, folder=folder, revision=name)


def current():
    """Local-only snapshot; corrupt/missing/incompatible content -> core."""
    state = _state()
    if 'pending' in state and not playing():
        from profile_transaction import writing
        try:
            with writing():
                state = _state()
                if 'pending' in state:
                    pending = state.pop('pending')
                    try:
                        if pending: _revision(pending)
                    except (OSError, ThemeError): pending = ''
                    state['active'] = pending
                    _atomic(root()/'selection.json', state)
        except (OSError, TimeoutError): return None
    if not state.get('active'): return None
    try: return _revision(state['active'])
    except (OSError, ThemeError, ValueError): return None


def installed():
    rows = []
    packages = root()/'packages'
    if not packages.exists(): return rows
    for folder in sorted(packages.glob('*/*')):
        if len(rows) >= 64: break
        try: rows.append(_revision(str(folder.relative_to(packages))))
        except (OSError, ThemeError, ValueError): continue
    return rows


def select(revision=''):
    from profile_transaction import writing
    with writing():
        if revision: _revision(revision)
        state = _state()
        deferred = playing()
        if deferred: state['pending'] = revision
        else: state = {'active': revision}
        _atomic(root()/'selection.json', state)
    return deferred


def install(filename, expected_sha='', cancel=lambda: False):
    """Worker-only; complete validation before publishing an immutable folder."""
    check_container(filename)
    digest = digest_file(filename)
    if expected_sha and digest != expected_sha: fail('CHECKSUM')
    stage = Path(tempfile.mkdtemp(prefix='.install-', dir=root()))
    try:
        with zipfile.ZipFile(filename) as archive:
            spec, total = check_archive(archive, core_version())
            # Keep a reserve for profile/SQLite writes; never evict existing art.
            check_space(total)
            for entry in archive.infolist():
                if cancel(): fail('CANCELLED')
                target = stage/entry.filename
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                limit = MAX_IMAGE if entry.filename.startswith('assets/') else MAX_METADATA
                with archive.open(entry) as source, target.open('xb') as output:
                    size = 0
                    while True:
                        if cancel(): fail('CANCELLED')
                        chunk = source.read(65536)
                        if not chunk: break
                        size += len(chunk)
                        if size > limit or size > entry.file_size: fail('LIMIT')
                        check_space(len(chunk))
                        output.write(chunk)
                    output.flush(); os.fsync(output.fileno())
                if entry.filename in spec['sha256']:
                    if digest_file(target, MAX_IMAGE) != spec['sha256'][entry.filename]: fail('CHECKSUM')
                    image(_read(target, MAX_IMAGE), target.suffix)
        from profile_transaction import writing
        with writing():
            if cancel(): fail('CANCELLED')
            existing = installed()
            previous = [r for r in existing if r['spec']['id'] == spec['id']]
            if any(version(row['spec']['version']) > version(spec['version']) for row in previous): fail('DOWNGRADE')
            for row in previous:
                if version(row['spec']['version']) == version(spec['version']):
                    if row['revision'].endswith('-'+digest): return row['revision']
                    fail('SAME_VERSION')
            # Bound accumulated immutable revisions. Removal is explicit.
            if len(existing) >= 32: fail('LIMIT')
            used = sum((row['folder']/p).stat().st_size for row in existing for p in row['spec']['required_files'])
            if used + total > 512*1024*1024: fail('SPACE')
            revision = spec['id']+'/'+spec['version']+'-'+digest
            parent = root()/'packages'/spec['id']
            parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            if parent.is_symlink() or parent.parent.is_symlink(): fail('PATH')
            destination = root()/'packages'/revision
            if destination.exists(): fail('PATH')
            os.replace(stage, destination)
            # Existing revisions are retained, so current player controls never
            # point at removed files. An update of the active ID is atomic too.
            state = _state()
            chosen = state.get('pending', state.get('active', ''))
            if chosen.startswith(spec['id']+'/'):
                if playing(): state['pending'] = revision
                else: state = {'active': revision}
                _atomic(root()/'selection.json', state)
            return revision
    except ThemeError: raise
    except (zipfile.BadZipFile, EOFError, RuntimeError, NotImplementedError, zlib.error): fail('ARCHIVE')
    finally:
        if stage.exists(): shutil.rmtree(stage)


def remove(theme_id):
    import re
    if not isinstance(theme_id, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', theme_id): fail('PATH')
    from profile_transaction import writing
    with writing():
        # No file deletion while old native controls may still display it.
        if playing(): fail('BUSY')
        state = _state()
        if any(value.startswith(theme_id+'/') for value in state.values()):
            _atomic(root()/'selection.json', {'active': ''})
        folder = root()/'packages'/theme_id
        if folder.is_symlink(): fail('PATH')
        if folder.exists(): shutil.rmtree(folder)


_UNSET = object()


def asset(key, fallback='', snapshot=_UNSET):
    theme = current() if snapshot is _UNSET else snapshot
    if theme and key in theme['spec']['assets']:
        path = theme['folder']/theme['spec']['assets'][key]
        try:
            theme_root=root();relative=path.relative_to(theme_root)
            if any((theme_root/parent).is_symlink() for parent in (relative,*relative.parents)): return fallback
            info=path.stat();signature=(info.st_size,info.st_mtime_ns,info.st_ctime_ns,info.st_ino)
            if _asset_valid.get(str(path)) != signature:
                if digest_file(path,MAX_IMAGE) != theme['spec']['sha256'][theme['spec']['assets'][key]]: return fallback
                _asset_valid[str(path)]=signature
            if path.is_file(): return str(path)
        except (OSError,ThemeError,ValueError): pass
    return fallback

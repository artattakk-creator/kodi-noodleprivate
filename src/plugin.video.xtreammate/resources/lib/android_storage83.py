"""Explicit Android shared-storage preflight. No grant, relocation or deletion.

Paths and mount sources stay local; public receipts contain only role, byte
counts and opaque correlation keys. Different FUSE devices are NOT evidence
of separate allocation pools. Kodi's folder browser is not an Android SAF API.
"""
import errno
import hashlib
import os
import re
import stat
import tempfile
from artwork_vfs import StorageFailure, target_root

BLOCK_FS = frozenset(('ext4', 'f2fs', 'vfat', 'exfat', 'xfs', 'btrfs'))
FUSE_FS = frozenset(('fuse', 'fuseblk', 'sdcardfs', 'esdfs'))


def key(value):
    return hashlib.sha256(str(value).encode()).hexdigest()[:16]


def android():
    import xbmc
    return bool(xbmc.getCondVisibility('System.Platform.Android'))


def failure(error, listing=False):
    number = getattr(error, 'errno', None)
    if number in (errno.EACCES, errno.EPERM):
        return 'TARGET_SAF_REQUIRED' if android() else 'TARGET_NOT_BROWSABLE' if listing else 'TARGET_NOT_WRITABLE'
    if number == errno.EROFS: return 'TARGET_NOT_WRITABLE'
    if number in (errno.ENOSPC, errno.EDQUOT): return 'TARGET_RESERVE_BLOCKED'
    return 'TARGET_OFFLINE'


def local_path(value):
    value = target_root(value)
    if '://' in value: raise StorageFailure('UNSUPPORTED_TARGET')
    # Resolve only after refusing every symlink component. A picker must not
    # silently follow a link from a shared folder into private app data.
    current = value
    while current and current != '/':
        if os.path.islink(current): raise StorageFailure('TARGET_SYMLINK')
        current = os.path.dirname(current)
    return os.path.realpath(value)


def mounts():
    result = []
    try:
        with open('/proc/self/mountinfo', encoding='utf-8') as stream:
            for line in stream:
                left, separator, right = line.partition(' - ')
                a, b = left.split(), right.split()
                if not separator or len(a) < 6 or len(b) < 2: continue
                def decode(text):
                    return re.sub(r'\\([0-7]{3})', lambda m: chr(int(m[1], 8)), text)
                result.append(dict(device=a[2], root=decode(a[3]), point=decode(a[4]),
                                   fs=b[0], source=decode(b[1]), readonly='ro' in a[5].split(',')))
    except OSError: pass
    return result


def measure(path, role, *, require=False, table=None):
    """Read-only observation. Missing cache folders use their existing parent.

    Selected destinations must themselves exist and be enumerable; no fallback
    to another filesystem and no fabricated Android StorageManager/SAF grant.
    """
    path = local_path(path)
    actual = path
    try:
        if require:
            if not stat.S_ISDIR(os.stat(actual).st_mode): raise StorageFailure('TARGET_NOT_BROWSABLE')
            with os.scandir(actual) as entries: next(entries, None)
        else:
            while not os.path.exists(actual):
                parent = os.path.dirname(actual)
                if parent == actual: raise StorageFailure('TARGET_OFFLINE')
                actual = parent
        before = os.stat(actual); vfs = os.statvfs(actual); after = os.stat(actual)
        if before.st_dev != after.st_dev: raise StorageFailure('TARGET_VOLUME_UNVERIFIED')
        unit = vfs.f_frsize or vfs.f_bsize
        total, available, free = vfs.f_blocks * unit, vfs.f_bavail * unit, vfs.f_bfree * unit
        if not 0 <= available <= free <= total or total <= 0: raise StorageFailure('TARGET_VOLUME_UNVERIFIED')
        table = mounts() if table is None else table
        matches = [m for m in table if actual == m['point'] or actual.startswith(m['point'].rstrip('/') + '/')]
        # Later overmounts at the same mountpoint supersede hidden mounts.
        mount = max(enumerate(matches), key=lambda pair: (len(pair[1]['point']), pair[0]))[1] if matches else {}
        from art_storage import reserve, MIN_RESERVE, MIB
        from artwork_config import read
        protected = reserve()
        if read().get('reserve_policy') == 'adaptive': protected = max(64*MIB, min(protected, int(total*.02)))
        return dict(path=path, role=role, device=before.st_dev, mount=mount,
                    identity_verified=mount.get('device') == '{}:{}'.format(os.major(before.st_dev),os.minor(before.st_dev)),
                    volume=key(before.st_dev), mount_key=key((mount.get('device'), mount.get('root'), mount.get('fs'))),
                    fs=mount.get('fs', 'UNKNOWN'), total=total, available=available, free=free,
                    reserve=protected, separate_reserve=max(MIN_RESERVE, min(256*MIB, int(total*.02))))
    except StorageFailure: raise
    except OSError as error: raise StorageFailure(failure(error, listing=require)) from None


def relation(source, target):
    a, b = source['mount'], target['mount']
    if source['device'] == target['device']: return 'TARGET_SAME_CAPACITY_POOL'
    # Bind mounts / aliases retain the backing major:minor even when observed
    # through different namespace wrappers. Quotas do not create another pool.
    if a.get('device') and a.get('device') == b.get('device'): return 'TARGET_SAME_CAPACITY_POOL'
    if a.get('source', '').startswith('/dev/') and a.get('source') == b.get('source'):
        return 'TARGET_SAME_CAPACITY_POOL'
    if (source.get('identity_verified') and target.get('identity_verified') and
            a.get('fs') in BLOCK_FS and b.get('fs') in BLOCK_FS and a.get('device') and b.get('device')):
        return 'SEPARATE_POOL_VERIFIED'
    # On Android, a FUSE mount may hide /data/media, quotas or a bind alias.
    # Equal totals/free alone cannot prove identity; different totals cannot
    # prove separation. No readable backing mapping => fail closed.
    return 'TARGET_VOLUME_UNVERIFIED'


def inventory(target=None, source_config=None):
    from artwork_config import root, read
    import xbmcvfs
    profile = root(); config = source_config if source_config is not None else read()
    paths = [('PROGRAMME_IMAGES', os.path.join(profile, 'programme_images46')),
             ('INTERNAL_MEDIA', os.path.join(profile, 'media_art_v1')),
             ('INTERNAL_LOGOS', os.path.join(profile, 'tv_logos')), ('PROFILE', profile)]
    for role, uri in (('KODI_HOME','special://home/'),('KODI_TEXTURES','special://thumbnails/')):
        try: paths.append((role,xbmcvfs.translatePath(uri)))
        except (AttributeError,RuntimeError):paths.append((role,''))
    if config.get('archive_mode', config['mode']) == 'external':
        from artwork_vfs import backend_for
        for kind in ('media', 'logos'):
            paths.append(('ACTIVE_' + kind.upper(), backend_for(config['target'], config['profile'], kind).root))
    rows = []
    for role, path in paths:
        try: rows.append(measure(path, role))
        except (StorageFailure, ValueError): rows.append(dict(role=role, error='TARGET_VOLUME_UNVERIFIED'))
    if target is not None: rows.append(measure(target, 'TARGET', require=True))
    return rows


def public(rows):
    fields = ('role', 'volume', 'mount_key', 'fs', 'total', 'available', 'free', 'reserve', 'error')
    return [{k: row[k] for k in fields if k in row} for row in rows]


def preflight(target, upcoming=4096, source_config=None):
    rows = inventory(target, source_config); destination = rows[-1]
    from artwork_config import read
    config = source_config if source_config is not None else read()
    external = config.get('archive_mode', config['mode']) == 'external'
    roles = ('ACTIVE_MEDIA', 'ACTIVE_LOGOS') if external else ('INTERNAL_MEDIA', 'INTERNAL_LOGOS', 'PROGRAMME_IMAGES')
    sources = [r for r in rows[:-1] if r['role'] in roles]
    results = [relation(r, destination) if 'error' not in r else 'TARGET_VOLUME_UNVERIFIED' for r in sources]
    code = ('TARGET_SAME_CAPACITY_POOL' if 'TARGET_SAME_CAPACITY_POOL' in results else
            'TARGET_VOLUME_UNVERIFIED' if len(sources) != len(roles) or 'TARGET_VOLUME_UNVERIFIED' in results else 'SEPARATE_POOL_VERIFIED')
    if destination['mount'].get('readonly'): raise StorageFailure('TARGET_NOT_WRITABLE')
    if code != 'SEPARATE_POOL_VERIFIED':
        error = StorageFailure(code); error.receipt = public(rows); raise error
    destination['reserve'] = destination['separate_reserve']
    from art_storage import WRITE_HEADROOM
    if destination['available'] < destination['reserve'] + max(0, upcoming) + WRITE_HEADROOM:
        error = StorageFailure('TARGET_RESERVE_BLOCKED'); error.receipt = public(rows); raise error
    return dict(target=destination['path'], volume=destination['volume'], mount_key=destination['mount_key'],
                code=code, rows=public(rows))


def probe(target, profile, *, confirmed=False):
    if confirmed is not True: raise StorageFailure('TARGET_PROBE_CONFIRMATION_REQUIRED')
    receipt = preflight(target)
    from artwork_vfs import prepare_target
    filename = None
    try:
        storage = prepare_target(receipt['target'], profile)
        payload = os.urandom(4096)
        fd, filename = tempfile.mkstemp(prefix='.probe83-', dir=storage.root)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        with open(filename, 'rb') as stream: result = stream.read(4097)
        if len(result) != 4096 or hashlib.sha256(result).digest() != hashlib.sha256(payload).digest():
            raise StorageFailure('TARGET_PROBE_VERIFY_FAILED')
        after = preflight(target)
        if (receipt['volume'], receipt['mount_key']) != (after['volume'], after['mount_key']):
            raise StorageFailure('TARGET_VOLUME_UNVERIFIED')
        return receipt
    except StorageFailure: raise
    except OSError as error: raise StorageFailure(failure(error)) from None
    finally:
        if filename is not None:
            try: os.unlink(filename)  # Only this invocation's exclusive probe.
            except OSError: raise StorageFailure('TARGET_PROBE_CLEANUP_FAILED') from None


def candidates():
    """Only known Android roots which can actually be listed. Never /storage/."""
    from storage_sources import kodi_sources
    roots = [os.environ.get('EXTERNAL_STORAGE', ''), '/storage/emulated/0/Movies',
             '/storage/emulated/0', '/sdcard/Movies', '/sdcard']
    roots += [r['path'] for r in kodi_sources() if r['path'].startswith(('/storage/emulated/', '/sdcard/'))]
    roots += [m['point'] for m in mounts() if m['point'].startswith(('/storage/emulated/', '/mnt/user/', '/mnt/runtime/default/'))]
    rows = []; seen = set()
    for path in roots:
        if not path or path == '/storage': continue
        # Android's /sdcard symlink is useful for discovery only; the picker
        # receives its real existing canonical root, never follows target links.
        path = os.path.realpath(path)
        if path in seen: continue
        seen.add(path)
        try: measure(path, 'CANDIDATE', require=True)
        except (StorageFailure, ValueError): continue
        rows.append(dict(label=os.path.basename(path) or 'Android', path=path))
    return rows

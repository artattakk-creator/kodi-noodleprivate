"""Wizard storage capabilities: POSIX privacy or owned Android app storage.

Android's emulated app-data filesystem may reject chmod or report synthetic
mode bits. Only Kodi's own configured app/profile subtree can use that backend;
arbitrary shared storage, foreign ownership and symlinks remain rejected.
"""
import os
import re
import stat
import errno


class StorageError(OSError):
    code = 'XM-SETUP-STORAGE'


def android_scoped(path):
    try:
        import xbmc, xbmcvfs
        if not xbmc.getCondVisibility('System.Platform.Android'):
            return False
        home = os.path.abspath(xbmcvfs.translatePath('special://home/'))
        profile = os.path.abspath(xbmcvfs.translatePath('special://profile/'))
        from utils import addon_data_dir
        root = os.path.abspath(addon_data_dir())
        target = os.path.abspath(path)
        if not re.search(r'/Android/data/org\.xbmc\.kodi/files/\.kodi$', home):
            return False
        if os.path.commonpath((home, profile)) != home:
            return False
        if root != os.path.join(profile, 'addon_data', 'plugin.video.xtreammate'):
            return False
        if os.path.commonpath((root, target)) != root:
            return False
        # Reject redirection anywhere in the app-controlled home/profile path.
        current = target
        while True:
            if os.path.islink(current):
                return False
            if os.path.exists(current) and os.stat(current).st_uid != os.getuid():
                return False
            if current == home:
                break
            parent = os.path.dirname(current)
            if parent == current:
                return False
            current = parent
        return True
    except (ImportError, AttributeError, OSError, ValueError, TypeError):
        return False


def protect(path, directory=False, fd=None):
    if os.path.islink(path):
        raise StorageError('WIZARD_SYMLINK')
    expected = 0o700 if directory else 0o600
    scoped = android_scoped(path)
    try:
        if fd is None:
            os.chmod(path, expected)
        else:
            os.fchmod(fd, expected)
    except OSError as exc:
        unsupported={errno.EPERM,errno.EACCES,errno.ENOSYS,errno.ENOTSUP,errno.EINVAL}
        if not scoped or exc.errno not in unsupported:
            raise
    value = os.fstat(fd) if fd is not None else os.stat(path)
    if not (stat.S_ISDIR(value.st_mode) if directory else stat.S_ISREG(value.st_mode)):
        raise StorageError('WIZARD_STORAGE_TYPE')
    if stat.S_IMODE(value.st_mode) & 0o077 and not scoped:
        raise StorageError('WIZARD_STORAGE_PRIVACY')
    return 'ANDROID_APP_STORAGE' if scoped else 'POSIX_PRIVATE'


def readable(path):
    return not os.path.islink(path) and (
        not stat.S_IMODE(os.stat(path).st_mode) & 0o077 or android_scoped(path))


class CheckpointError(OSError):
    code = 'XM-SETUP-CHECKPOINT'


def checkpoint(session, draft, stage='groups', categories=False):
    if session and not session.checkpoint(draft, stage, categories=categories):
        error = CheckpointError('WIZARD_CHECKPOINT_FAILED')
        error.errno = getattr(session, 'errno71', None)
        raise error

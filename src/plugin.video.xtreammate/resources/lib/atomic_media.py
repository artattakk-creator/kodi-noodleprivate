"""Native media publication: atomic no-replace rename or exclusive hardlink.

No architecture-specific syscall numbers, plain rename fallback, Kodi or HTTP.
File and directory fsync remain mandatory for both supported backends.
"""
import errno
import os
from pathlib import Path
import stat
import uuid

RESERVE=64*1024*1024


class StorageFailure(OSError):
    def __init__(self,code,step,number=0):
        self.code=code;self.step=step;self.number=number if isinstance(number,int) else 0
        super().__init__(code)


def failure(exc,step):
    number=getattr(exc,'errno',0) or 0
    code='TARGET_PERMISSION' if number in (errno.EACCES,errno.EPERM) else 'TARGET_READ_ONLY' if number==errno.EROFS else 'DISK_FULL' if number==errno.ENOSPC else 'TARGET_EXISTS' if number==errno.EEXIST else 'TARGET_SYMLINK' if number==errno.ELOOP else 'TARGET_SYNC_UNSUPPORTED' if step.startswith('FSYNC') else 'TARGET_UNAVAILABLE'
    return StorageFailure(code,step,number)


def _basename(name):
    if not isinstance(name,str) or not name or name in ('.','..') or any(c in name for c in ('/','\\','\0')):
        raise StorageFailure('TARGET_UNSAFE_NAME','PATH')
    return name


def _rename_noreplace(directory,source,target):
    try:
        import ctypes
        library=ctypes.CDLL(None,use_errno=True);rename=library.renameat2
    except (ImportError,AttributeError,OSError):raise OSError(errno.ENOSYS,'renameat2 unavailable') from None
    rename.argtypes=(ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint)
    rename.restype=ctypes.c_int
    if rename(directory,os.fsencode(source),directory,os.fsencode(target),1)!=0:
        number=ctypes.get_errno();raise OSError(number,os.strerror(number))


def publish(directory,source,target):
    """Publish a regular owned file without ever replacing any destination."""
    source=_basename(source);target=_basename(target)
    step='OPEN_FILE';fd=None
    try:
        fd=os.open(source,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
        if not stat.S_ISREG(os.fstat(fd).st_mode):raise StorageFailure('TARGET_NOT_REGULAR','READ')
        step='FSYNC_FILE';os.fsync(fd);step='FSYNC_DIRECTORY';os.fsync(directory)
        step='RENAME_NOREPLACE'
        try:_rename_noreplace(directory,source,target);backend='RENAME_NOREPLACE'
        except OSError as exc:
            if exc.errno not in (errno.ENOSYS,errno.EINVAL,errno.EOPNOTSUPP,errno.ENOTSUP):raise
            step='LINK'
            try:os.link(source,target,src_dir_fd=directory,dst_dir_fd=directory,follow_symlinks=False)
            except (OSError,NotImplementedError) as link_error:
                if getattr(link_error,'errno',0) not in (None,0,errno.ENOSYS,errno.EINVAL,errno.EOPNOTSUPP,errno.ENOTSUP):raise
                raise StorageFailure('TARGET_ATOMIC_PUBLISH_UNAVAILABLE',step,getattr(link_error,'errno',0) or 0) from None
            backend='HARDLINK';step='FSYNC_DIRECTORY';os.fsync(directory)
            step='UNLINK_OWN_PART';os.unlink(source,dir_fd=directory)
        step='FSYNC_DIRECTORY';os.fsync(directory)
        return backend
    except StorageFailure:raise
    except (OSError,NotImplementedError) as exc:raise failure(exc,step) from None
    finally:
        if fd is not None:os.close(fd)


def probe_fd(directory):
    token=uuid.uuid4().hex;source=token+'.probe';target=source+'.published';own=None;step='OPEN_FILE'
    try:
        fd=os.open(source,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600,dir_fd=directory)
        own=os.fstat(fd)
        with os.fdopen(fd,'wb') as stream:
            step='WRITE';stream.write(b'XCMate');stream.flush();step='FSYNC_FILE';os.fsync(stream.fileno())
        backend=publish(directory,source,target)
        step='READ';fd=os.open(target,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
        with os.fdopen(fd,'rb') as stream:
            if stream.read()!=b'XCMate':raise StorageFailure('TARGET_READ_FAILED',step)
        return backend
    except StorageFailure:raise
    except (OSError,NotImplementedError) as exc:raise failure(exc,step) from None
    finally:
        if own is not None:
            for name in (source,target):
                try:
                    actual=os.stat(name,dir_fd=directory,follow_symlinks=False)
                    if (actual.st_dev,actual.st_ino)==(own.st_dev,own.st_ino):os.unlink(name,dir_fd=directory)
                except OSError:pass


def probe(target,create=False):
    fd=None;step='PATH'
    try:
        if not isinstance(target,str) or '://' in target or not os.path.isabs(target):raise StorageFailure('UNSUPPORTED_TARGET',step)
        if Path(target).is_symlink():raise StorageFailure('TARGET_SYMLINK',step)
        if create:step='MKDIR';os.makedirs(target,mode=0o700,exist_ok=True)
        step='OPEN_DIRECTORY';fd=os.open(target,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        step='SPACE';space=os.fstatvfs(fd);free=space.f_bavail*space.f_frsize
        if free<RESERVE:raise StorageFailure('DISK_FULL',step)
        backend=probe_fd(fd)
        return dict(target=target,free=free,publish=backend)
    except StorageFailure:raise
    except (OSError,AttributeError,NotImplementedError) as exc:raise failure(exc,step) from None
    finally:
        if fd is not None:os.close(fd)

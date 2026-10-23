"""One POSIX target contract for picker, enqueue, service and recorder."""
import errno
import os
from pathlib import Path
import uuid
from direct_ts import Failure,RESERVE


class TargetFailure(Failure):
    def __init__(self,code,step,number=0):
        self.step=step;self.number=number if isinstance(number,int) else 0
        super().__init__(code)


def mark(code,step='DONE',number=0):
    try:
        import xbmc
        xbmc.log('[XCMate][CAPTURE_TARGET] code={} syscall={} errno={}'.format(code,step,number),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def _failure(exc,step):
    number=getattr(exc,'errno',0) or 0
    code='TARGET_PERMISSION' if number in (errno.EACCES,errno.EPERM) else 'TARGET_READ_ONLY' if number==errno.EROFS else 'DISK_FULL' if number==errno.ENOSPC else 'TARGET_HARDLINK_UNSUPPORTED' if step=='LINK' else 'TARGET_UNAVAILABLE'
    return TargetFailure(code,step,number)


def probe_fd(directory):
    token=uuid.uuid4().hex;name=token+'.probe';link=name+'.link';created=linked=False;step='OPEN_FILE'
    try:
        out=os.open(name,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600,dir_fd=directory);created=True
        with os.fdopen(out,'wb') as stream:
            step='WRITE';stream.write(b'XCMate');stream.flush();step='FSYNC_FILE';os.fsync(stream.fileno())
        step='LINK';os.link(name,link,src_dir_fd=directory,dst_dir_fd=directory,follow_symlinks=False);linked=True
        step='READ';inp=os.open(link,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
        with os.fdopen(inp,'rb') as stream:
            if stream.read()!=b'XCMate':raise TargetFailure('TARGET_READ_FAILED',step)
        step='FSYNC_DIRECTORY';os.fsync(directory)
    except TargetFailure:raise
    except (OSError,NotImplementedError) as exc:raise _failure(exc,step) from None
    finally:
        for own,exists in ((link,linked),(name,created)):
            if exists:
                try:os.unlink(own,dir_fd=directory)
                except OSError:pass


def probe(target,create=False):
    fd=None;step='PATH'
    try:
        if not isinstance(target,str) or '://' in target or not os.path.isabs(target):
            raise TargetFailure('UNSUPPORTED_TARGET',step)
        directory=Path(target)
        if directory.is_symlink():raise TargetFailure('TARGET_SYMLINK',step)
        if create:
            step='MKDIR';os.makedirs(target,mode=0o700,exist_ok=True)
        step='OPEN_DIRECTORY';fd=os.open(target,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        step='SPACE';capacity=os.fstatvfs(fd);free=capacity.f_bavail*capacity.f_frsize
        if free<RESERVE:raise TargetFailure('DISK_FULL',step)
        probe_fd(fd);mark('READY');return dict(target=target,free=free)
    except TargetFailure as exc:
        mark(exc.code,exc.step,exc.number);raise
    except (OSError,AttributeError,NotImplementedError) as exc:
        failure=_failure(exc,step);mark(failure.code,step,failure.number);raise failure from None
    finally:
        if fd is not None:os.close(fd)


def configured():
    import xbmcvfs
    from utils import setting,addon_data_dir
    return xbmcvfs.translatePath(setting('recordings_folder',os.path.join(addon_data_dir(),'recordings')))


def compatible_default():
    """Return a successfully probed persistent target, never Android's cache."""
    from utils import addon_data_dir
    candidates=[os.path.join(addon_data_dir(),'recordings')]
    try:
        import xbmc
        if xbmc.getCondVisibility('System.Platform.Android'):
            private=os.environ.get('ANDROID_PRIVATE','')
            if private and os.path.isdir(private):candidates.insert(0,os.path.join(private,'XCMate','recordings'))
            for base in ('/data/user/0/org.xbmc.kodi/files','/data/data/org.xbmc.kodi/files'):
                if os.path.isdir(base):candidates.append(os.path.join(base,'XCMate','recordings'))
    except (AttributeError,RuntimeError):pass
    for target in dict.fromkeys(candidates):
        try:probe(target,create=True);return target
        except Failure:continue
    return None

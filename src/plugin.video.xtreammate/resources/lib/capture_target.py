"""One POSIX target contract for picker, enqueue, service and recorder."""
import os
from direct_ts import Failure


class TargetFailure(Failure):
    def __init__(self,code,step,number=0):
        self.step=step;self.number=number if isinstance(number,int) else 0
        super().__init__(code,step=step,number=self.number)


def mark(code,step='DONE',number=0):
    try:
        import xbmc
        xbmc.log('[XCMate][CAPTURE_TARGET] code={} syscall={} errno={}'.format(code,step,number),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError):pass


def probe_fd(directory):
    from atomic_media import probe_fd as native_probe,StorageFailure
    try:return native_probe(directory)
    except StorageFailure as exc:raise TargetFailure(exc.code,exc.step,exc.number) from None


def probe(target,create=False):
    from atomic_media import probe as native_probe,StorageFailure
    try:
        result=native_probe(target,create=create);mark('READY',result['publish']);return result
    except StorageFailure as exc:
        mark(exc.code,exc.step,exc.number)
        raise TargetFailure(exc.code,exc.step,exc.number) from None


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
    except (ImportError,AttributeError,RuntimeError):pass
    for target in dict.fromkeys(candidates):
        try:probe(target,create=True);return target
        except Failure:continue
    return None

"""Hold the worker slot across GUI close until its non-GUI cleanup completes."""
import fcntl
import os


class Busy(OSError):
    code = 'XM-SETUP-WORKER-BUSY'


def acquire():
    from utils import addon_data_dir
    filename = os.path.join(addon_data_dir(), '.wizard-worker51.lock')
    fd = os.open(filename, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        raise Busy('wizard worker still closing') from None
    except BaseException:
        os.close(fd)
        raise
    def release():
        nonlocal fd
        if fd is not None:
            os.close(fd)
            fd = None
    return release

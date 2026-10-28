"""A stale two-hour Window property cannot own the wizard after script exit."""
import fcntl
import os


def owner_alive():
    from utils import addon_data_dir
    filename=os.path.join(addon_data_dir(),'.window-navigation.lock')
    fd=None
    try:
        fd=os.open(filename,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return True
        fcntl.flock(fd,fcntl.LOCK_UN);return False
    except FileNotFoundError:return False
    except OSError:return True  # Unknown ownership never authorizes a takeover.
    finally:
        if fd is not None:os.close(fd)

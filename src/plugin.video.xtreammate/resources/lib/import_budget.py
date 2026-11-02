"""Actual disk capacity, not a fixed total-collection size. No user-data reset."""
import os
import shutil

RESERVE = 32 * 1024 * 1024


class ReserveBlocked(OSError):
    code69='SAFE_RESERVE_BLOCKED'
    def __init__(self,free,reserve,upcoming):
        self.free_bytes69=free;self.reserve_bytes69=reserve;self.upcoming_bytes69=upcoming
        super().__init__(28,'Insufficient free space for safe import')

def check_space(filename, upcoming=0):
    folder = os.path.dirname(os.path.abspath(filename))
    if shutil.disk_usage(folder).free < RESERVE + max(0, upcoming):
        raise ReserveBlocked(shutil.disk_usage(folder).free, RESERVE, max(0, upcoming))


def safe_failure(exc):
    """Only Python basenames and line numbers; no exception text/locals/URLs."""
    import traceback
    return dict(exception_class=type(exc).__name__, frames=[
        (os.path.basename(frame.filename),frame.lineno)
        for frame in traceback.extract_tb(exc.__traceback__)[-5:]])

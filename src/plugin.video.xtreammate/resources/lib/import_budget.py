"""Actual disk capacity, not a fixed total-collection size. No user-data reset."""
import os
import shutil

RESERVE = 32 * 1024 * 1024


def check_space(filename, upcoming=0):
    folder = os.path.dirname(os.path.abspath(filename))
    if shutil.disk_usage(folder).free < RESERVE + max(0, upcoming):
        raise OSError(28, 'Insufficient free space for safe import')


def safe_failure(exc):
    """Only Python basenames and line numbers; no exception text/locals/URLs."""
    import traceback
    return dict(exception_class=type(exc).__name__, frames=[
        (os.path.basename(frame.filename),frame.lineno)
        for frame in traceback.extract_tb(exc.__traceback__)[-5:]])

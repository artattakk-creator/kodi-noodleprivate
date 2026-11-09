"""Actionable artwork errors; never display/log private exception strings."""
import sqlite3
from localization import tr

MESSAGES = {
    'TARGET_NOT_BROWSABLE':38310, 'TARGET_NOT_WRITABLE':38311, 'TARGET_SAF_REQUIRED':38312,
    'TARGET_OFFLINE':38313, 'STORAGE_OFFLINE':38313, 'TARGET_RESERVE_BLOCKED':38314,
    'DISK_FULL':38314, 'TARGET_SAME_CAPACITY_POOL':38315, 'TARGET_VOLUME_UNVERIFIED':38316,
    'ARTWORK_DB_BUSY':38317, 'ARTWORK_WRITER_BUSY':38317, 'RENDER_NOT_VERIFIED':38318,
    'METADATA_TARGET_REQUIRED':38319, 'TARGET_PROBE_CONFIRMATION_REQUIRED':38320,
    'TARGET_COLLISION':38321, 'TARGET_SYMLINK':38322, 'INVALID_TARGET':38322,
    'IMAGE_VERIFY_FAILED':38323, 'TARGET_PROBE_VERIFY_FAILED':38323,
    'TARGET_PROBE_CLEANUP_FAILED':38324, 'COPY_INCOMPLETE':38325,
    'NO_TRANSFER':38325, 'SOURCE_CHANGED':38326, 'SOURCE_IMAGE_INVALID':38326,
    'TARGET_WRITE_FAILED':38311,
    'ARTWORK_JOURNAL_RESERVE_BLOCKED':38328,
    'ARTWORK_DB_UNAVAILABLE':38329,
}


def show(error, dialog, phase):
    import xbmc
    code=getattr(error,'code','')
    if isinstance(error,sqlite3.OperationalError) and (getattr(error,'sqlite_errorcode',0)&255) in (5,6):code='ARTWORK_DB_BUSY'
    elif isinstance(error,sqlite3.Error):code='ARTWORK_DB_UNAVAILABLE'
    if isinstance(error,BlockingIOError) or type(error).__name__=='WriterBusy':code='ARTWORK_WRITER_BUSY'
    if isinstance(error,OSError) and not code and getattr(error,'errno',None):
        from android_storage83 import failure
        code=failure(error)
    if code not in MESSAGES:code='ARTWORK_OPERATION_FAILED'
    number=phase if isinstance(phase,int) and 0<=phase<18 else -1
    try:xbmc.log('[XCMate][ART_STORAGE83] phase={} code={}'.format(number,code),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass
    rows=getattr(error,'receipt',None)
    if rows:
        from artwork_ui import _storage_text
        dialog.textviewer(tr(38301),_storage_text(rows))
    dialog.ok(tr(35200),tr(MESSAGES.get(code,38327))+'\n'+code)

"""Bounded setup facts. No exception text, source lines, addresses or secrets."""
import errno
import hashlib
import os
import time
import traceback

STAGES = frozenset(('AUTH_BEGIN','AUTH_DONE','GROUPS_BEGIN','GROUPS_DONE',
    'CHECKPOINT_DONE','CHECKPOINT_FAILED','SELECTED','COMMIT_BEGIN','COMMIT_DONE',
    'READBACK_DONE','FAILED','LEGACY_DONE','LEGACY_SKIPPED','PROBE'))
_started={}


def emit(stage, session='', error=None, **fields):
    if stage not in STAGES:
        return
    stamp=time.monotonic();token=hashlib.sha256(str(session).encode()).hexdigest()[:12]
    prefix=stage.removesuffix('_BEGIN').removesuffix('_DONE')
    if stage.endswith('_BEGIN'):
        _started[(token,prefix)]=stamp
        while len(_started)>256:_started.pop(next(iter(_started)))
    if stage.endswith('_DONE'):
        before=_started.pop((token,prefix),None)
        if before is not None:fields.setdefault('duration_ms',int((stamp-before)*1000))
    values = ['[XCMate][SETUP71]', 'stage='+stage,'session='+token,'mono_ms='+str(int(stamp*1000))]
    for key in ('total','live','vod','series','duration_ms','free','available','block_size'):
        v = fields.get(key)
        if type(v) is int:
            values.append(key+'='+str(max(0, min(v, 2**63-1))))
    if fields.get('path') in ('PROFILE','HOME','ADDON_DATA','LIBRARY'):
        values.append('path='+fields['path'])
    if fields.get('backend') in ('ANDROID_APP_STORAGE','POSIX_PRIVATE','UNCONFIRMED'):
        values.append('backend='+fields['backend'])
    if fields.get('code') in ('READY','ANDROID_APP_STORAGE','POSIX_PRIVATE',
        'WRITE_FAILED','READ_ONLY','QUICK_CHECK_OK','QUICK_CHECK_FAILED','BUSY','NO_INPUT'):
        values.append('code='+fields['code'])
    if error is not None:
        names={'OSError','PermissionError','FileNotFoundError','TimeoutError',
               'CheckpointError','StorageError','ValueError','SaveError',
               'OperationalError','DatabaseError','Busy','DiscoveryBusy'}
        name=type(error).__name__
        values.append('type='+(name if name in names else 'OTHER'))
        number=getattr(error,'errno',None)
        if type(number) is int:
            values.append('errno='+str(number))
        # Hash the traceback's code positions; never emit source text/paths.
        frames=traceback.extract_tb(error.__traceback__)[-8:]
        signature='|'.join(os.path.basename(f.filename)+':'+str(f.lineno) for f in frames)
        values.append('stack='+hashlib.sha256(signature.encode()).hexdigest()[:12])
        allowed={'wizard_resume53.py','wizard_storage71.py','wizard_catalog54.py','wizard_ui54.py',
                 'setup_draft.py','legacy_setup71.py','portals.py','group_selection.py',
                 'profile_transaction.py','stream_http.py','setup_commit71.py','xtream.py','wizard_deadline48.py'}
        safe=[os.path.basename(f.filename)+':'+str(f.lineno) for f in frames if os.path.basename(f.filename) in allowed]
        if safe:values.append('frames='+'>'.join(safe))
    try:
        import xbmc
        xbmc.log(' '.join(values), xbmc.LOGINFO)
    except (ImportError, AttributeError, RuntimeError):
        pass


def probe(session=''):
    """Explicit worker-side probe; remove only our newly created probe file."""
    import tempfile
    import sqlite3
    from urllib.parse import quote
    import xbmcvfs
    from utils import addon_data_dir
    from library_index import path as library_path
    result={}
    for label, folder in (('HOME',xbmcvfs.translatePath('special://home/')),
                          ('PROFILE',xbmcvfs.translatePath('special://profile/')),
                          ('ADDON_DATA',addon_data_dir())):
        record={};tmp=None;fd=None
        try:
            fs=os.statvfs(folder)
            record.update(free=fs.f_bfree*fs.f_frsize,available=fs.f_bavail*fs.f_frsize,block_size=fs.f_frsize)
            fd,tmp=tempfile.mkstemp(prefix='.xcmate-probe71-',dir=folder)
            os.write(fd,b'XCMate storage probe\n');os.fsync(fd);os.close(fd);fd=None
            with open(tmp,'rb') as check:
                if check.read()!=b'XCMate storage probe\n':raise OSError('PROBE_READBACK')
            record['code']='READY'
            from wizard_storage71 import android_scoped,readable
            record['backend']='ANDROID_APP_STORAGE' if android_scoped(folder) else 'POSIX_PRIVATE' if readable(folder) else 'UNCONFIRMED'
        except OSError as exc:
            record['code']='WRITE_FAILED';emit('PROBE',session,error=exc,path=label,**record)
        else:
            emit('PROBE',session,path=label,**record)
        finally:
            if fd is not None:os.close(fd)
            if tmp is not None:
                try:os.unlink(tmp)
                except OSError as exc:
                    record['code']='WRITE_FAILED';emit('PROBE',session,error=exc,path=label,code='WRITE_FAILED')
        result[label]=record
    name=library_path()
    if os.path.isfile(name):
        db=None
        try:
            db=sqlite3.connect('file:'+quote(name,safe='/')+'?mode=ro',uri=True,timeout=.1)
            db.execute('PRAGMA query_only=ON')
            code='QUICK_CHECK_OK' if db.execute('PRAGMA quick_check').fetchone()[0]=='ok' else 'QUICK_CHECK_FAILED'
            result['LIBRARY']=dict(code=code);emit('PROBE',session,path='LIBRARY',code=code)
        except sqlite3.Error as exc:
            code='BUSY' if getattr(exc,'sqlite_errorcode',None) in (sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED) else 'QUICK_CHECK_FAILED'
            result['LIBRARY']=dict(code=code);emit('PROBE',session,error=exc,path='LIBRARY',code=code)
        finally:
            if db is not None:db.close()
    return result

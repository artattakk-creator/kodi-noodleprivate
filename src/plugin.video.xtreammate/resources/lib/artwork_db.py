"""Private artwork-job database maintenance; never repairs other databases.

All XCMate connections hold a shared process-independent file lock. Maintenance
needs the exclusive lock AND a SQLite writer barrier. Backups use SQLite's
online backup API, including committed WAL data, never a bare copy of the DB.
Only a proved art_pending index defect is repaired automatically. Queue rebuild
is a separate, explicitly confirmed operation; original image files survive.
"""
import errno
import hashlib
import json
import os
import re
import shutil
import sqlite3
import threading
import time
import uuid

try:
    import fcntl
except ImportError:
    fcntl=None

_gate=threading.RLock()
_initialized=set()
_failures={}
_SCHEMA=(
    '''CREATE TABLE IF NOT EXISTS jobs(ident TEXT PRIMARY KEY,url TEXT,status TEXT,
       priority INTEGER,attempts INTEGER,next_at REAL,updated REAL,bytes INTEGER)''',
    'CREATE INDEX IF NOT EXISTS art_pending ON jobs(status,next_at,priority)',
    'CREATE TABLE IF NOT EXISTS scan(pid TEXT,kind TEXT,revision TEXT,offset INTEGER,PRIMARY KEY(pid,kind))',
    "CREATE TABLE IF NOT EXISTS worker(id INTEGER PRIMARY KEY,until REAL,owner TEXT DEFAULT '')")


class ArtworkDBUnavailable(sqlite3.OperationalError):
    pass


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'media_art_jobs_v1.sqlite')


def _identity(filename):
    try:
        st=os.stat(filename)
        return [st.st_dev,st.st_ino]
    except OSError:
        return []


def _state_path():
    return os.path.join(os.path.dirname(path()),'media_art_db_health_v1.json')


def diagnostic():
    try:
        with open(_state_path(),encoding='utf-8') as stream:
            value=json.loads(stream.read(8192))
        if isinstance(value,dict):return value
    except (OSError,ValueError):pass
    return dict(code='NOT_CHECKED')


def _save(value):
    filename=_state_path();tmp=filename+'.'+uuid.uuid4().hex+'.tmp'
    try:
        fd=os.open(tmp,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(value,stream);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,filename)
    except OSError:pass
    finally:
        try:os.unlink(tmp)
        except FileNotFoundError:pass
        except OSError:pass


def classify(exc):
    number=getattr(exc,'sqlite_errorcode',0)&255
    if number in (sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED):return 'BUSY'
    if number==sqlite3.SQLITE_READONLY:return 'READONLY'
    if number==sqlite3.SQLITE_FULL or getattr(exc,'errno',None)==errno.ENOSPC:return 'SPACE_FULL'
    if number in (sqlite3.SQLITE_CORRUPT,sqlite3.SQLITE_NOTADB):return 'CORRUPT'
    if number==sqlite3.SQLITE_IOERR:return 'IO_ERROR'
    if getattr(exc,'errno',None) in (errno.EROFS,errno.EACCES,errno.EPERM):return 'READONLY'
    # Older Android sqlite wrappers may not expose errorcode. Inspect known
    # phrases internally, but never put the exception text into a log or state.
    message=str(exc).lower()
    if 'lock-unsupported' in message:return 'LOCK_UNSUPPORTED'
    for text,code in (('locked','BUSY'),('readonly','READONLY'),('disk is full','SPACE_FULL'),
                      ('malformed','CORRUPT'),('not a database','CORRUPT'),
                      ('no such column','SCHEMA_ERROR'),('no such table','SCHEMA_ERROR')):
        if text in message:return code
    return 'SQL_ERROR'


def _failure(exc,phase):
    filename=path();code=classify(exc);now=time.time()
    prior=_failures.get(filename) or diagnostic()
    delay=5 if code=='BUSY' else 300
    value=dict(code=code,phase=phase,error=type(exc).__name__ if type(exc).__name__ in
               ('OperationalError','DatabaseError','IntegrityError','OSError','PermissionError') else 'OTHER',
               sqlite_code=getattr(exc,'sqlite_errorcode',0)&255,
               retry_after=now+delay,identity=_identity(filename))
    _failures[filename]=value
    _save(value)
    if prior.get('code')!=code or prior.get('retry_after',0)<=now:
        from utils import warn
        warn('XCMate artwork db: code={} phase={} sqlite={}'.format(code,phase,value['sqlite_code']))
    return value


def reset_retry():
    """Explicit retry only; does not remove or reset a database or any image."""
    _failures.pop(path(),None)
    value=diagnostic();value['retry_after']=0;value['background_paused']=False;_save(value)


def _lock(exclusive=False):
    if fcntl is None:
        if exclusive:raise ArtworkDBUnavailable('XM-ARTWORK-LOCK-UNSUPPORTED')
        return None
    fd=os.open(path()+'.maintenance.lock',os.O_CREAT|os.O_RDWR,0o600)
    try:fcntl.flock(fd,(fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)|fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        raise sqlite3.OperationalError('database is locked') from None
    return fd


def _unlock(fd):
    if fd is not None:
        try:fcntl.flock(fd,fcntl.LOCK_UN)
        finally:os.close(fd)


class _Connection(sqlite3.Connection):
    _art_lock=None
    _art_phase='QUERY'

    def execute(self,sql,parameters=()):
        try:return super().execute(sql,parameters)
        except sqlite3.Error as exc:
            _failure(exc,self._art_phase)
            raise

    def commit(self):
        try:return super().commit()
        except sqlite3.Error as exc:
            _failure(exc,'COMMIT')
            raise

    def __exit__(self,*args):
        try:return super().__exit__(*args)
        except sqlite3.Error as exc:
            _failure(exc,'TRANSACTION');raise

    def close(self):
        try:super().close()
        finally:
            fd=self._art_lock;self._art_lock=None;_unlock(fd)


def _schema(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        for statement in _SCHEMA:db.execute(statement)
        if 'owner' not in {r[1] for r in db.execute('PRAGMA table_info(worker)')}:
            db.execute("ALTER TABLE worker ADD COLUMN owner TEXT DEFAULT ''")
        db.execute('INSERT OR IGNORE INTO worker(id,until) VALUES(1,0)')
        db.commit()
    except BaseException:
        db.rollback();raise


def connect():
    filename=path();prior=_failures.get(filename) or diagnostic()
    if prior.get('identity')==_identity(filename) and prior.get('retry_after',0)>time.time():
        raise ArtworkDBUnavailable('XM-ARTWORK-DB-PAUSED')
    if not _gate.acquire(timeout=.05):raise ArtworkDBUnavailable('XM-ARTWORK-DB-BUSY')
    fd=None;db=None
    try:
        fd=_lock()
        db=sqlite3.connect(filename,timeout=.05,factory=_Connection)
        db._art_lock=fd;fd=None;db.row_factory=sqlite3.Row
        ident=(filename,tuple(_identity(filename)))
        if ident not in _initialized:
            db._art_phase='SCHEMA';_schema(db);_initialized.add(ident)
            _failures.pop(filename,None)
        db._art_phase='QUERY'
        return db
    except (sqlite3.Error,OSError) as exc:
        if db is not None:db.close()
        else:_unlock(fd)
        # execute() already reported schema errors; report opening/lock errors.
        if filename not in _failures:_failure(exc,'OPEN')
        raise
    finally:_gate.release()


def _bounded(db,cancel):
    deadline=time.monotonic()+10
    db.set_progress_handler(lambda:int(cancel() or time.monotonic()>deadline),1000)


def _sync_directory(folder):
    fd=os.open(folder,os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
    try:os.fsync(fd)
    finally:os.close(fd)


def _backup(source,cancel):
    """Caller holds application exclusive lock and SQLite BEGIN IMMEDIATE."""
    from import_budget import check_space
    root=os.path.join(os.path.dirname(path()),'artwork_db_backups')
    os.makedirs(root,exist_ok=True)
    _sync_directory(os.path.dirname(root))
    size=sum(os.path.getsize(p) for p in (path(),path()+'-wal') if os.path.exists(p))
    check_space(os.path.join(root,'snapshot'),max(4096,size)*2)
    name='artwork-'+time.strftime('%Y%m%dT%H%M%S',time.gmtime())+'-'+uuid.uuid4().hex+'.sqlite'
    filename=os.path.join(root,name);partial=filename+'.partial'
    reader=sqlite3.connect(path(),timeout=.05);target=sqlite3.connect(partial,timeout=.05)
    os.chmod(partial,0o600);deadline=time.monotonic()+10
    def progress(status,remaining,total):
        if cancel() or time.monotonic()>deadline:raise InterruptedError('XM-ARTWORK-BACKUP-CANCELLED')
    try:
        reader.backup(target,pages=128,progress=progress,sleep=.01)
        target.close();target=None
        with open(partial,'rb') as stream:os.fsync(stream.fileno())
        os.replace(partial,filename)
        _sync_directory(root)  # backup name is durable before any live repair
    finally:
        reader.close()
        if target is not None:target.close()
        # An interrupted partial backup is retained, never mistaken for a
        # complete recovery snapshot, and never used to authorize a mutation.
    return filename


def _integrity(db,cancel):
    _bounded(db,cancel)
    try:return [row[0] for row in db.execute('PRAGMA integrity_check(100)')]
    except sqlite3.OperationalError:
        if cancel():raise InterruptedError('XM-ARTWORK-CANCELLED') from None
        raise
    finally:db.set_progress_handler(None,0)


def _table_hashes(db,cancel):
    result={};_bounded(db,cancel)
    try:
        for name in ('jobs','scan','worker'):
            if not db.execute('SELECT 1 FROM sqlite_master WHERE type=? AND name=?',('table',name)).fetchone():continue
            digest=hashlib.sha256()
            for row in db.execute('SELECT * FROM '+name+' NOT INDEXED ORDER BY rowid'):
                digest.update(repr(tuple(row)).encode('utf-8'))
            result[name]=digest.hexdigest()
    finally:db.set_progress_handler(None,0)
    return result


def _index_only(errors,db):
    if not errors or errors==['ok']:return False
    columns=[r[2] for r in db.execute('PRAGMA index_info(art_pending)')]
    allowed=r'(?:row \d+ missing from index art_pending|wrong # of entries in index art_pending)'
    return columns==['status','next_at','priority'] and all(re.fullmatch(allowed,e) for e in errors)


def _valid_tables(db):
    required={'jobs':{'ident','url','status','priority','attempts','next_at','updated','bytes'},
              'scan':{'pid','kind','revision','offset'},'worker':{'id','until'}}
    for name,columns in required.items():
        rows=list(db.execute('PRAGMA table_info('+name+')'))
        # Missing auxiliary tables and the legacy worker.owner column can be
        # created additively by connect; incompatible existing columns cannot.
        if rows and not columns.issubset({row[1] for row in rows}):return False
    return True


def _healthy(code,backup=''):
    value=dict(code=code,checked_at=time.time(),retry_after=0,identity=_identity(path()))
    if code=='QUEUE_REBUILT' or diagnostic().get('background_paused'):
        value['background_paused']=True
    if backup:value['backup']=os.path.basename(backup)
    _failures.pop(path(),None);_save(value)
    return value


def maintain(force=False,cancel=lambda:False):
    """Worker-only check; auto repair exclusively a confirmed art_pending defect."""
    if fcntl is None:return dict(code='LOCK_UNSUPPORTED')
    if not os.path.exists(path()):return dict(code='NOT_CREATED')
    prior=diagnostic();now=time.time()
    if not force and prior.get('identity')==_identity(path()):
        if prior.get('retry_after',0)>now:return prior
        if prior.get('code') in ('OK','INDEX_REPAIRED','QUEUE_REBUILT') and now-prior.get('checked_at',0)<86400:return prior
    fd=None;db=None;backup='';working='';phase='LOCK'
    try:
        fd=_lock(True);db=sqlite3.connect(path(),timeout=.05)
        db.execute('BEGIN IMMEDIATE')
        phase='BACKUP';backup=_backup(db,cancel)
        phase='CHECK';working=backup+'.verify'
        shutil.copyfile(backup,working);os.chmod(working,0o600)
        copy=sqlite3.connect(working,timeout=.05)
        try:
            errors=_integrity(copy,cancel)
            if errors==['ok']:
                if not _valid_tables(copy):
                    value=dict(code='SCHEMA_ERROR',phase='CHECK',checked_at=now,retry_after=now+86400,
                               identity=_identity(path()),backup=os.path.basename(backup))
                    _save(value);_failures[path()]=value;return value
                db.rollback();return _healthy('OK',backup)
            if not _index_only(errors,copy):
                value=dict(code='RECOVERY_REQUIRED',phase='CHECK',checked_at=now,retry_after=now+86400,
                           identity=_identity(path()),backup=os.path.basename(backup))
                _save(value);_failures[path()]=value;return value
            before=_table_hashes(copy,cancel)
            copy.execute('REINDEX art_pending')
            if _integrity(copy,cancel)!=['ok'] or _table_hashes(copy,cancel)!=before:
                raise sqlite3.DatabaseError('XM-ARTWORK-INDEX-REPAIR-UNVERIFIED')
        finally:copy.close()
        phase='REINDEX';db.execute('REINDEX art_pending')
        if _integrity(db,cancel)!=['ok'] or _table_hashes(db,cancel)!=before:
            raise sqlite3.DatabaseError('XM-ARTWORK-INDEX-REPAIR-UNVERIFIED')
        if cancel():raise InterruptedError('XM-ARTWORK-CANCELLED')
        db.commit();return _healthy('INDEX_REPAIRED',backup)
    except InterruptedError:
        return dict(code='CANCELLED')
    except (sqlite3.Error,OSError) as exc:
        if phase=='CHECK' and backup and classify(exc)=='CORRUPT':
            value=dict(code='RECOVERY_REQUIRED',phase='CHECK',checked_at=now,retry_after=now+86400,
                       identity=_identity(path()),backup=os.path.basename(backup))
            _save(value);_failures[path()]=value;return value
        return _failure(exc,phase)
    finally:
        if db is not None:db.close()  # uncommitted repairs roll back
        _unlock(fd)
        if working:
            try:os.unlink(working)
            except OSError:pass


def rebuild(confirmed=False,cancel=lambda:False):
    """Explicit queue-only recovery. Cannot replace active/uncheckpointed WAL."""
    if not confirmed:return dict(code='CONFIRMATION_REQUIRED')
    if fcntl is None:return dict(code='LOCK_UNSUPPORTED')
    fd=None;db=None;new='';phase='LOCK'
    try:
        fd=_lock(True)
        if not os.path.exists(path()):return dict(code='NOT_CREATED')
        db=sqlite3.connect(path(),timeout=.05);db.execute('BEGIN IMMEDIATE')
        phase='BACKUP';backup=_backup(db,cancel)
        check=sqlite3.connect(backup,timeout=.05)
        try:
            try:healthy=_integrity(check,cancel)==['ok'] and _valid_tables(check)
            except sqlite3.DatabaseError as exc:
                if classify(exc)!='CORRUPT':raise
                healthy=False
            if healthy:
                db.rollback();return _healthy('OK',backup)
        finally:check.close()
        from media_art import folder,dimensions,MAX_PIXELS
        phase='REBUILD';new=path()+'.rebuild-'+uuid.uuid4().hex
        target=sqlite3.connect(new,timeout=.05);os.chmod(new,0o600)
        try:
            _schema(target)
            with target:
                if os.path.isdir(folder()):
                    with os.scandir(folder()) as entries:
                        for entry in entries:
                            if cancel():raise InterruptedError('XM-ARTWORK-CANCELLED')
                            if not re.fullmatch(r'[0-9a-f]{64}\.img',entry.name) or not entry.is_file(follow_symlinks=False):continue
                            try:
                                with open(entry.path,'rb') as stream:w,h=dimensions(stream.read(65536))
                                if not 0<w<=4096 or not 0<h<=4096 or w*h>MAX_PIXELS:continue
                            except (OSError,ValueError):continue
                            target.execute("INSERT INTO jobs VALUES(?,'','READY',0,0,0,?,?)",
                                           (entry.name[:-4],time.time(),entry.stat().st_size))
            if _integrity(target,cancel)!=['ok']:raise sqlite3.DatabaseError('XM-ARTWORK-REBUILD-FAILED')
        finally:target.close()
        if cancel():raise InterruptedError('XM-ARTWORK-CANCELLED')
        # No own connections can enter under the exclusive application lock.
        # A legacy/external active writer/reader or corrupt WAL blocks recovery.
        phase='CHECKPOINT';db.commit()
        checkpoint=db.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
        if checkpoint and checkpoint[0]:raise sqlite3.OperationalError('database is locked')
        db.close();db=None
        if any(os.path.exists(path()+suffix) for suffix in ('-wal','-shm')):
            raise sqlite3.OperationalError('database is locked')
        phase='REPLACE';os.replace(new,path());new=''
        _sync_directory(os.path.dirname(path()))
        _initialized.clear()
        from art_store import _ADOPTED
        _ADOPTED.discard(folder())
        return _healthy('QUEUE_REBUILT',backup)
    except InterruptedError:return dict(code='CANCELLED')
    except (sqlite3.Error,OSError,ValueError) as exc:
        return _failure(exc,phase)
    finally:
        if db is not None:db.close()
        _unlock(fd)
        # Only our uninstalled candidate is removable; source DB, backups,
        # sidecars and artwork are never deleted by a failed recovery.
        if new:
            try:os.unlink(new)
            except OSError:pass

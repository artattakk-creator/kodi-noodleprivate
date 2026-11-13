"""Bounded upgrade maintenance, exact owned temp files and expired EPG only.

Never deletes artwork objects, Kodi files, backups, active journals or WALs.
Every run journals intent before deletion and records measured free bytes.
"""
import hashlib
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from urllib.parse import quote

VERSION = '0.1.29.92'
_due = 0

def root():
    from utils import addon_data_dir
    return Path(addon_data_dir())

def receipt_path():return root()/'storage_maintenance92.json'

def read():
    file = receipt_path()
    if not file.exists():return {}
    if file.is_symlink() or file.stat().st_size > 128*1024:raise OSError('MAINTENANCE_JOURNAL_UNSAFE')
    return json.loads(file.read_bytes())

def journal(value):
    from storage_metadata92 import check
    from logo_store89 import atomic
    raw = json.dumps(value,sort_keys=True,separators=(',',':')).encode()
    check(receipt_path(),len(raw),kind='maintenance');atomic(receipt_path(),raw)
    if read()!=value:raise OSError('MAINTENANCE_READBACK_FAILED')

def free():
    v = os.statvfs(root());return v.f_bavail*(v.f_frsize or v.f_bsize)

def reference_intervals():
    """Keep timer/reminder intervals even outside normal retention. RO only."""
    result = set()
    filename = root()/'guide_timers_v1.sqlite'
    if filename.exists():
        if filename.is_symlink():raise OSError('REFERENCE_SCAN_BLOCKED')
        db = sqlite3.connect('file:'+quote(str(filename),safe='/')+'?mode=ro',uri=True,timeout=.03)
        try:
            rows = db.execute('SELECT start,stop FROM timers LIMIT 4097').fetchall()
            if len(rows)>4096:raise OSError('REFERENCE_SCAN_BUDGET')
            result.update((int(a),int(b)) for a,b in rows)
        finally:db.close()
    file = root()/'reminders.json'
    if file.exists():
        if file.is_symlink() or file.stat().st_size>1024*1024:raise OSError('REFERENCE_SCAN_BUDGET')
        value = json.loads(file.read_bytes())
        def walk(value,depth=0):
            if depth>12:raise OSError('REFERENCE_SCAN_BUDGET')
            if isinstance(value,dict):
                if 'start' in value and 'stop' in value:result.add((int(value['start']),int(value['stop'])))
                for item in value.values():walk(item,depth+1)
            elif isinstance(value,list):
                for item in value:walk(item,depth+1)
        walk(value)
    return result

def expire_epg(filename, tables, cutoff, protected, *, limit=512, seconds=.2):
    """Small indexed/interruptible deletes; keep 7 local calendar days.

    Active import staging, aliases, mapping, artwork and future rows untouched.
    No VACUUM conversion and no manual unlink of SQLite companions.
    """
    file = Path(filename)
    if not file.exists():return dict(code='NOT_CREATED',rows=0)
    if file.is_symlink() or file.parent.resolve()!=root().resolve():raise OSError('EPG_PATH_UNSAFE')
    deadline=time.monotonic()+seconds
    before=sum(p.stat().st_size for p in (file,Path(str(file)+'-wal')) if p.exists())
    try:db=sqlite3.connect(str(file),timeout=.03)
    except sqlite3.Error:return dict(code='SQLITE_BUSY_OR_BUDGET',rows=0)
    removed=0;more=False
    try:
        db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        existing={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table in tables:
            if table not in existing:continue
            columns={r[1] for r in db.execute('PRAGMA table_info('+table+')')}
            required={'start','stop','pid'}
            if not required.issubset(columns):raise OSError('EPG_SCHEMA_UNVERIFIED')
            db.execute('BEGIN IMMEDIATE')
            try:
                rows=db.execute('SELECT rowid,start,stop FROM '+table+' WHERE stop<=? LIMIT ?',
                                (cutoff,limit+1)).fetchall()
                more=more or len(rows)>limit
                selected=[(r[0],) for r in rows[:limit] if (r[1],r[2]) not in protected]
                db.executemany('DELETE FROM '+table+' WHERE rowid=?',selected)
                if any(db.execute('SELECT 1 FROM '+table+' WHERE rowid=?',r).fetchone() for r in selected):
                    raise OSError('RETENTION_READBACK_FAILED')
                db.commit();removed+=len(selected)
            except Exception:db.rollback();raise
        db.set_progress_handler(None,0)
        check=db.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
        # Incremental mode is enabled only on newly created .92 guides.
        # Existing DBs are NOT converted using a space-hungry full VACUUM.
        if removed and db.execute('PRAGMA auto_vacuum').fetchone()[0]==2:
            from import_budget import check_space
            check_space(str(file),65536)
            db.execute('PRAGMA incremental_vacuum(128)')
        code='MORE' if more else 'VERIFIED_RETENTION'
        if check and check[0]:code='WAL_BUSY'
    except (sqlite3.Error,OSError) as error:
        db.rollback();code='SQLITE_BUSY_OR_BUDGET' if isinstance(error,sqlite3.Error) else 'RESERVE_BLOCKED'
    finally:db.close()
    after=sum(p.stat().st_size for p in (file,Path(str(file)+'-wal')) if p.exists())
    return dict(code=code,rows=removed,physical_bytes_before=before,physical_bytes_after=after,
                observed_file_delta=before-after,full_vacuum='NOT_RUN')

def expire_temp(cancel,now,maximum=128):
    """Only the exact private cache temp pattern emitted by utils.cache_set.

    A week-old, closed partial cache is disposable, never a committed cache.
    No general glob/rmtree and no image/metadata/reference heuristics.
    """
    folder=root()/'cache'
    if not folder.exists():return dict(files=0,bytes=0)
    if folder.is_symlink() or any(p.is_symlink() for p in folder.parents):raise OSError('UNSAFE_CACHE_ROOT')
    active=set()
    try:
        for entry in Path('/proc/self/fd').iterdir():
            try:active.add(os.readlink(entry))
            except OSError:pass
    except OSError:return dict(files=0,bytes=0,code='OPEN_FILE_SCAN_UNAVAILABLE')
    fd=os.open(folder,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    count=size=scanned=0;deadline=time.monotonic()+.15;limited=False
    try:
        with os.scandir(fd) as entries:
         for entry in entries:
            name=entry.name;scanned+=1
            if count>=maximum or scanned>4096 or time.monotonic()>deadline or cancel():limited=True;break
            if not re.fullmatch(r'\.xcmate-cache-[a-f0-9]{32}',name):continue
            if str(folder/name) in active:continue
            before=os.stat(name,dir_fd=fd,follow_symlinks=False)
            import stat
            if not stat.S_ISREG(before.st_mode) or now-before.st_mtime<7*86400:continue
            after=os.stat(name,dir_fd=fd,follow_symlinks=False)
            if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):continue
            os.unlink(name,dir_fd=fd);count+=1;size+=before.st_size
        os.fsync(fd)
    finally:os.close(fd)
    return dict(files=count,bytes=size,code='SCAN_BUDGET') if limited else dict(files=count,bytes=size)

def run(cancel=lambda:False,progress=lambda **kw:None,force=False):
    from artwork_gate import writer
    from profile_transaction import writing
    from guide_store import day_window
    if cancel():return dict(code='CANCELLED')
    with writer(),writing(timeout=.1):
        from artwork_migration import busy
        if busy():return dict(code='ACTIVE_MIGRATION_PROTECTED')
        prior=read();now=time.time()
        if not force and prior.get('version')==VERSION and prior.get('state')=='DONE' and now-prior.get('at',0)<3600:return prior
        record=dict(version=VERSION,state='RUNNING',at=now,free_before=free())
        journal(record)
        try:protected=reference_intervals()
        except (OSError,ValueError,sqlite3.Error):
            record.update(state='PAUSED',code='REFERENCE_PROOF_BLOCKED',free_after=free(),observed_free_change=0)
            journal(record);return record
        temp=expire_temp(cancel,now)
        tables=[('guide_v1.sqlite',('programmes','guide44_inputs','guide44_ranges')),
                ('programme_meta46.sqlite',('metadata',)),('programme_artwork.sqlite',('facts',))]
        results=[]
        for name,owned_tables in tables:
            if cancel():break
            result=expire_epg(root()/name,owned_tables,day_window(-7,now)[0],protected)
            results.append(dict(category=name,**result));progress(stage='RETENTION',done=len(results),files=3)
        record.update(state='PAUSED' if cancel() or any(r['code'] in ('MORE','WAL_BUSY','SQLITE_BUSY_OR_BUDGET','RESERVE_BLOCKED') for r in results) else 'DONE',
                      temp=temp,databases=results,free_after=free(),artwork_orphans='OPEN_REFERENCE_PROOF_REQUIRED',
                      kodi_cache='PROTECTED',fallback90='PROTECTED')
        record['observed_free_change']=record['free_after']-record['free_before']
        journal(record);return record

def startup(cancel=lambda:False):
    """Existing data worker calls before bulk warm-up; no new boot threads."""
    global _due
    if time.monotonic()<_due:return
    _due=time.monotonic()+300
    try:
        value=run(cancel)
        if value.get('state')=='PAUSED':_due=time.monotonic()+30
    except (OSError,ValueError,TimeoutError,sqlite3.Error):pass

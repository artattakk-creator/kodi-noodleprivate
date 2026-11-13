"""Proven EPG backup retention, distinct from RAM-only XMLTV downloads.

Keep the latest authorized, hash/config/SQLite-verified recovery set. Remove
only older exact owned sets with valid manifests, bounded and journalled.
Unknown raw feeds or user-selected local XMLTV sources are never deleted.
"""
import hashlib,json,os,re,sqlite3,time
from pathlib import Path
from urllib.parse import quote

def stamp(file):
    st=file.stat(follow_symlinks=False)
    return (st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)

def digest(file,cancel):
    h=hashlib.sha256()
    with file.open('rb') as stream:
        for part in iter(lambda:stream.read(65536),b''):
            if cancel():raise InterruptedError('CANCELLED')
            h.update(part)
    return h.hexdigest()

def proof(folder,name,cancel):
    if not re.fullmatch(r'guide-[0-9]{16,20}\.sqlite',name):raise ValueError('SKIPPED_UNPROVEN')
    dbfile=folder/name;receipt=folder/(name+'.json');config=folder/(name+'.sources.json')
    for file in (dbfile,receipt):
        if not file.is_file() or file.is_symlink():raise ValueError('SKIPPED_UNPROVEN')
    if receipt.stat().st_size>4096:raise ValueError('SKIPPED_UNPROVEN')
    value=json.loads(receipt.read_bytes());before=stamp(dbfile)
    if value.get('code')!='BACKUP_VERIFIED' or value.get('backup')!=name or value.get('bytes')!=before[2]:raise ValueError('SKIPPED_UNPROVEN')
    if not re.fullmatch('[a-f0-9]{64}',value.get('sha256','')) or digest(dbfile,cancel)!=value['sha256']:raise ValueError('SKIPPED_UNPROVEN')
    files=[dbfile,receipt]
    if value.get('source_config_sha256'):
        if config.is_symlink() or not config.is_file() or config.stat().st_size>4*1024**2:raise ValueError('SKIPPED_UNPROVEN')
        if digest(config,cancel)!=value['source_config_sha256']:raise ValueError('SKIPPED_UNPROVEN')
        json.loads(config.read_bytes());files.append(config)
    elif config.exists():raise ValueError('SKIPPED_UNPROVEN')
    # A backup currently opened/modified by SQLite is not a closed recovery set.
    if any(Path(str(dbfile)+suffix).exists() for suffix in ('-wal','-shm','-journal')):raise ValueError('SKIPPED_UNPROVEN')
    db=sqlite3.connect('file:'+quote(str(dbfile),safe='/')+'?mode=ro&immutable=1',uri=True,timeout=.03)
    try:
        deadline=time.monotonic()+2;db.set_progress_handler(lambda:int(cancel() or time.monotonic()>deadline),1000)
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('SKIPPED_UNPROVEN')
        if db.execute('SELECT count(*) FROM programmes').fetchone()[0]!=value.get('events'):raise ValueError('SKIPPED_UNPROVEN')
        revisions=db.execute('SELECT pid,revision FROM guide_meta').fetchall()
        if not revisions:raise ValueError('SKIPPED_UNPROVEN')
    finally:db.close()
    if before!=stamp(dbfile):raise ValueError('SKIPPED_UNPROVEN')
    return dict(sha=value['sha256'],files=files,stamps={str(p):stamp(p) for p in files})

def active_hash(db):
    row=db.execute("SELECT backup_sha FROM guide44_authorization WHERE kind='VERIFIED_BACKUP' ORDER BY created DESC LIMIT 1").fetchone()
    if not row or not re.fullmatch('[a-f0-9]{64}',row[0]):raise ValueError('NO_RECOVERY_AUTHORIZATION')
    return row[0]

def prune(cancel=lambda:False,journal=lambda value:None,maximum=2):
    from storage_maintenance92 import root
    folder=root()/'guide_backups44';source=root()/'guide_v1.sqlite'
    result=dict(code='NO_BACKUPS',deleted_files=0,deleted_bytes=0,skipped=0,raw_deleted_bytes=0,
                raw_status='RAW_FEEDS_RAM_ONLY; UNKNOWN_FILES_SKIPPED_UNPROVEN')
    if not folder.exists() or not source.is_file():return result
    if folder.is_symlink() or source.is_symlink() or any(p.is_symlink() for p in folder.parents):raise OSError('UNSAFE_EPG_ROOT')
    if folder.stat().st_dev!=root().stat().st_dev:return dict(result,code='BACKUP_VOLUME_UNVERIFIED')
    names=[]
    with os.scandir(folder) as entries:
        for number,entry in enumerate(entries):
            if number>=256:return dict(result,code='BACKUP_SCAN_BUDGET')
            if re.fullmatch(r'guide-[0-9]{16,20}\.sqlite',entry.name):names.append(entry.name)
    db=sqlite3.connect('file:'+quote(str(source),safe='/')+'?mode=rw',uri=True,timeout=.03)
    try:
        wanted=active_hash(db);keep=None
        for name in sorted(names,reverse=True):
            receipt=folder/(name+'.json')
            try:
                if receipt.is_symlink() or receipt.stat().st_size>4096:continue
                if json.loads(receipt.read_bytes()).get('sha256')!=wanted:continue
                keep=proof(folder,name,cancel);break
            except (OSError,ValueError,sqlite3.Error):continue
        if keep is None:return dict(result,code='RECOVERY_PROOF_BLOCKED')
        result.update(code='VERIFIED_BACKUP_RETENTION',kept_sha256=wanted)
        for name in sorted(names):
            if cancel():result['code']='CANCELLED';break
            if result['deleted_files']>=maximum:result['code']='MORE';break
            if str(folder/name) in keep['stamps']:continue
            try:old=proof(folder,name,cancel)
            except (OSError,ValueError,sqlite3.Error):result['skipped']+=1;continue
            db.execute('BEGIN IMMEDIATE')
            try:
                if active_hash(db)!=wanted or any(stamp(Path(p))!=st for p,st in keep['stamps'].items()):raise ValueError('RECOVERY_CHANGED')
                if any(stamp(Path(p))!=st for p,st in old['stamps'].items()):raise ValueError('BACKUP_CHANGED')
                active=set()
                try:
                    for entry in Path('/proc/self/fd').iterdir():
                        try:active.add(os.readlink(entry))
                        except OSError:pass
                except OSError:raise OSError('OPEN_FILE_PROOF_UNAVAILABLE')
                if any(str(file) in active for file in old['files']):
                    result['skipped']+=1;continue
                journal(dict(result,pending=name,pending_sha256=old['sha']))
                # Delete the old DB first, then only its proven sidecars. Power
                # loss leaves an untrusted orphan receipt, never a lost keeper.
                for file in old['files']:
                    size=file.stat().st_size;file.unlink();result['deleted_bytes']+=size
                result['deleted_files']+=1
                fd=os.open(folder,os.O_RDONLY|os.O_DIRECTORY)
                try:os.fsync(fd)
                finally:os.close(fd)
                journal(result)
            finally:db.rollback()  # Lock only; active guide is never modified.
        return result
    except (OSError,ValueError,sqlite3.Error):return dict(result,code='RECOVERY_PROOF_BLOCKED')
    finally:db.close()

def imported(pid,revision):
    """Observe real architecture after cold commit readback, no pretend XML delete."""
    from epg_snapshot92 import committed
    if not committed(pid,revision):return dict(code='IMPORT_READBACK_FAILED',raw_deleted_bytes=0)
    __import__('epg_status').update(pid,'raw_retention93','IMPORT_CONFIRMED_RAW_NOT_PERSISTED',bytes=0)
    return dict(code='IMPORT_CONFIRMED_RAW_NOT_PERSISTED',raw_deleted_bytes=0,
                retained='ACTIVE_DB_SOURCE_METADATA_AND_LAST_GOOD',unknown_raw='SKIPPED_UNPROVEN')

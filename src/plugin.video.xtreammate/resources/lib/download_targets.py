"""Capability-based download targets; immutable local stage for external copies."""
import errno,hashlib,json,os,re,sqlite3,time,uuid
from pathlib import Path


class Failure(OSError):
    def __init__(self,code,step='TARGET',number=0):
        self.code=code;self.step=step;self.number=number;super().__init__(code)


def db():
    from utils import addon_data_dir
    path=os.path.join(addon_data_dir(),'download_targets_v1.sqlite')
    connection=sqlite3.connect(path,timeout=.25);connection.row_factory=sqlite3.Row;os.chmod(path,0o600)
    connection.executescript('''CREATE TABLE IF NOT EXISTS approvals(target TEXT PRIMARY KEY);
      CREATE TABLE IF NOT EXISTS volumes(target TEXT PRIMARY KEY,device TEXT,inode TEXT);
      CREATE TABLE IF NOT EXISTS transfers(token TEXT PRIMARY KEY,job TEXT,target TEXT,part TEXT,file TEXT,status TEXT);''')
    return connection


def normalize(root):
    if root.startswith('smb://'):
        from download_smb import normalized
        return normalized(root)
    if root.startswith('special://'):
        import xbmcvfs
        root=xbmcvfs.translatePath(root)
    if '://' in root or not os.path.isabs(root) or '\0' in root:raise Failure('TARGET_ANDROID_ACCESS_REQUIRED','PATH')
    return os.path.normpath(root)


def approved(root,save=False):
    key=hashlib.sha256(normalize(root).encode()).hexdigest();connection=db()
    try:
        if save:
            with connection:connection.execute('INSERT OR IGNORE INTO approvals VALUES(?)',(key,))
        return connection.execute('SELECT 1 FROM approvals WHERE target=?',(key,)).fetchone() is not None
    finally:connection.close()


def record(token,job,target,part,final,status):
    connection=db()
    try:
        with connection:connection.execute('INSERT OR REPLACE INTO transfers VALUES(?,?,?,?,?,?)',(token,job,target,part,final,status))
    finally:connection.close()


def receipts(job,final):
    connection=db()
    try:return [dict(r) for r in connection.execute('SELECT * FROM transfers WHERE job=? AND file=?',(job,final))]
    finally:connection.close()


def owned(job,final):
    return any(r['status'] in ('COPYING','READY_RENAME','RENAMED','VERIFIED') for r in receipts(job,final))


def recoverable(job,final):
    values=receipts(job,final)
    if any(r['status'] in ('VERIFIED','RENAMED') for r in values):return True
    if not final.startswith('smb://'):return any(r['status']=='COPYING' for r in values)
    import download_smb as smb
    return any(r['status']=='READY_RENAME' and r['part'] and not smb.exists(r['part']) for r in values)


def identity(root):
    if root.startswith('smb://'):return {}
    try:value=os.stat(normalize(root),follow_symlinks=False)
    except OSError as exc:raise Failure('TARGET_REMOVED','MOUNT_STAT',exc.errno or 0) from None
    import stat
    if not stat.S_ISDIR(value.st_mode):raise Failure('TARGET_NOT_DIRECTORY','MOUNT_STAT')
    return dict(target_device=str(value.st_dev),target_inode=str(value.st_ino))


def bind(root):
    if root.startswith('smb://'):return
    value=identity(root);key=hashlib.sha256(normalize(root).encode()).hexdigest();connection=db()
    try:
        with connection:connection.execute('INSERT OR REPLACE INTO volumes VALUES(?,?,?)',(key,value['target_device'],value['target_inode']))
    finally:connection.close()


def check_identity(root,media=None):
    if root.startswith('smb://'):return
    expected={k:str((media or {}).get(k) or '') for k in ('target_device','target_inode')}
    if not all(expected.values()):
        key=hashlib.sha256(normalize(root).encode()).hexdigest();connection=db()
        try:row=connection.execute('SELECT device,inode FROM volumes WHERE target=?',(key,)).fetchone()
        finally:connection.close()
        if row is None:return
        expected=dict(target_device=row['device'],target_inode=row['inode'])
    if identity(root)!=expected:raise Failure('TARGET_CHANGED','MOUNT_IDENTITY')


def configured():
    from utils import setting
    selected=setting('downloads_folder','').strip() if setting('downloads_folder_enabled','')=='1' else ''
    if selected:return normalize(selected)
    from capture_target import configured as recording_target
    return recording_target()


def stage_root():
    from utils import addon_data_dir
    from atomic_media import probe,StorageFailure
    candidates=[os.path.join(addon_data_dir(),'download_staging')]
    private=os.environ.get('ANDROID_PRIVATE','')
    if private and os.path.isdir(private):candidates.append(os.path.join(private,'XCMate','download_staging'))
    for base in ('/data/user/0/org.xbmc.kodi/files','/data/data/org.xbmc.kodi/files'):
        if os.path.isdir(base):candidates.append(os.path.join(base,'XCMate','download_staging'))
    for path in dict.fromkeys(candidates):
        try:probe(path,create=True);return path
        except StorageFailure:continue
    raise Failure('STAGING_UNAVAILABLE','STAGING_PROBE')


def _usb_probe(root):
    from atomic_media import failure
    name='.xcmate-probe-'+uuid.uuid4().hex;path=os.path.join(root,name);created=False;own=None
    try:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);created=True;own=os.fstat(fd)
        with os.fdopen(fd,'wb') as stream:stream.write(b'XCMate');stream.flush();os.fsync(stream.fileno())
        if Path(path).read_bytes()!=b'XCMate':raise Failure('TARGET_VERIFY_FAILED','READ')
        try:
            collision=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        except FileExistsError:pass
        else:os.close(collision);raise Failure('TARGET_NO_EXCLUSIVE_CREATE','OPEN_EXCLUSIVE')
    except OSError as exc:
        if isinstance(exc,Failure):raise
        raise failure(exc,'USB_PROBE') from None
    finally:
        if created:
            stat=os.stat(path,follow_symlinks=False)
            if (stat.st_dev,stat.st_ino)==(own.st_dev,own.st_ino):os.unlink(path)


def _smb_probe(root):
    import download_smb as smb
    from media_files import join
    token=uuid.uuid4().hex;one=join(root,'.xcmate-probe-'+token+'.a');two=one+'.b';final=one+'.verified'
    source=Path(stage_root())/(token+'.probe');expected=b'XCMate SMB2 capability probe';created=[];own=None
    try:
        fd=os.open(str(source),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);own=os.fstat(fd)
        with os.fdopen(fd,'wb') as stream:stream.write(expected);stream.flush();os.fsync(stream.fileno())
        with smb.session(root) as (connection,share,path):
            if not connection.getAttributes(share,path or '/',timeout=10).isDirectory:raise Failure('TARGET_NOT_DIRECTORY','SMB_STAT')
        smb.upload_exclusive(str(source),one);created.append(one)
        smb.upload_exclusive(str(source),two);created.append(two)
        try:smb.upload_exclusive(str(source),two)
        except smb.Failure as exc:
            if exc.code!='TARGET_EXISTS':raise
        else:raise Failure('TARGET_NO_EXCLUSIVE_CREATE','SMB_CREATE')
        try:smb.rename(one,two)
        except smb.Failure as exc:
            if exc.code!='TARGET_EXISTS':raise
        else:raise Failure('TARGET_UNSAFE_RENAME','SMB_RENAME')
        digest=hashlib.sha256(expected).hexdigest()
        if smb.digest(two,len(expected))!=digest:raise Failure('TARGET_VERIFY_FAILED','SMB_HASH')
        smb.rename(one,final);created.remove(one);created.append(final)
        if smb.digest(final,len(expected))!=digest:raise Failure('TARGET_VERIFY_FAILED','SMB_HASH')
    finally:
        if own is not None:
            try:
                current=source.lstat()
                if (current.st_dev,current.st_ino)==(own.st_dev,own.st_ino):source.unlink()
            except FileNotFoundError:pass
        for uri in created:
            try:smb.remove(uri)
            except smb.Failure:pass


def assess(root):
    from atomic_media import probe as native_probe,StorageFailure
    from media_files import file_limit
    root=normalize(root)
    if root.startswith('smb://'):
        _smb_probe(root)
        return dict(backend='SMB2_STAGE_VERIFY',type='SMB',writable=True,free=None,max_bytes=file_limit(root),vfs=True,
                    atomic_publish=True,fsync_directory=False,offline=False,resume='LOCAL_STAGE',staging=True)
    try:
        result=native_probe(root,create=True)
        return dict(backend='NATIVE',type='LOCAL',writable=True,free=result['free'],max_bytes=file_limit(root),vfs=False,
                    atomic_publish=True,fsync_directory=True,offline=True,resume='HTTP_RANGE',staging=False)
    except StorageFailure as exc:
        if exc.code not in ('TARGET_SYNC_UNSUPPORTED','TARGET_ATOMIC_PUBLISH_UNAVAILABLE'):raise
        _usb_probe(root);stage_root()
        import shutil
        return dict(backend='LOCAL_STAGE_VERIFY',type='LOCAL_USB',writable=True,free=shutil.disk_usage(root).free,max_bytes=file_limit(root),vfs=False,
                    atomic_publish=False,fsync_directory=False,offline=True,resume='LOCAL_STAGE',staging=True)


def probe(root):
    # An external-copy backend is never enabled merely by editing a folder URI.
    root=normalize(root)
    if root.startswith('smb://') and not approved(root):raise Failure('STAGING_CONSENT_REQUIRED','TARGET_APPROVAL')
    check_identity(root)
    result=assess(root)
    if result['staging'] and not approved(root):raise Failure('STAGING_CONSENT_REQUIRED','TARGET_APPROVAL')
    return result


def publish(source,final,job,total,expected,caps,cancel=lambda:False,progress=lambda n:None,
            destination=lambda uri:None,claim=lambda:True):
    import media_files as files
    if not caps['staging']:
        files.rename(source,final);return final
    token=uuid.uuid4().hex;target=final.rsplit('/',1)[0]
    if caps['type']=='SMB':
        import download_smb as smb
        remote=files.join(target,'.xcmate-'+job+'-'+token+'.part')
        if smb.exists(final):
            if not owned(job,final):raise Failure('TARGET_EXISTS','SMB_RENAME')
            base=re.sub(r'--target-[0-9a-f]{32}(?=\.[a-z0-9]+$)','',final)
            stem,ext=os.path.splitext(base);final=stem+'--target-'+token+ext
        record(token,job,target,remote,final,'COPYING');destination(final)
        smb.upload_exclusive(source,remote,cancel,progress)
        if smb.size(remote)!=total or smb.digest(remote,total,cancel)!=expected:raise Failure('TARGET_VERIFY_FAILED','SMB_HASH')
        record(token,job,target,remote,final,'READY_RENAME')
        if cancel() or not claim():raise InterruptedError()
        smb.rename(remote,final);record(token,job,target,remote,final,'RENAMED')
        if smb.size(final)!=total or smb.digest(final,total,cancel)!=expected:raise Failure('TARGET_VERIFY_FAILED','SMB_HASH_FINAL')
    else:
        from download_worker import _hash
        base=re.sub(r'--target-[0-9a-f]{32}(?=\.[a-z0-9]+$)','',final)
        stem,ext=os.path.splitext(base);final=stem+'--target-'+token+ext
        record(token,job,target,'',final,'RESERVED');destination(final)
        count=0
        with files.reader(source) as stream,files.writer(final) as output:
            record(token,job,target,'',final,'COPYING')
            while True:
                if cancel():raise InterruptedError()
                data=stream.read(65536)
                if not data:break
                output.write(data);count+=len(data);progress(count)
            files.flush(output)
        if files.size(final)!=total or _hash(final,total,cancel)!=expected:raise Failure('TARGET_VERIFY_FAILED','USB_HASH')
        if cancel() or not claim():raise InterruptedError()
    record(token,job,target,'',final,'VERIFIED')
    # Keep the fully fsynced local stage: no automatic user-file/cache deletion.
    return final

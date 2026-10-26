"""Read-only physical inventory and explicit journalled dynamic-mode cleanup.

Fixed internal artwork roots only. No glob deletion, no Kodi textures or DB
removal. Directory handles and O_NOFOLLOW keep symlink/path swaps out of scope.
Cleanup never starts/resumes itself; every run needs a fresh UI confirmation.
"""
import hashlib,os,sqlite3,stat,time,uuid
from contextlib import contextmanager
ROOTS=('media_art_v1','tv_logos')
LIMIT=3*1024*1024

class InventoryFailure(OSError):
    def __init__(self,code):self.code=code;super().__init__(code)


def profile():
    from utils import addon_data_dir
    return addon_data_dir()


def filename():return os.path.join(profile(),'artwork_cleanup_v1.sqlite')


def valid_name(name):return len(name)==68 and name.endswith('.img') and all(c in '0123456789abcdef' for c in name[:64])


@contextmanager
def roots():
    pfd=os.open(profile(),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);opened={}
    try:
        for name in ROOTS:
            try:fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=pfd)
            except FileNotFoundError:continue
            except OSError:raise InventoryFailure('ARTWORK_ROOT_UNSAFE') from None
            opened[name]=fd
        yield pfd,opened
    finally:
        for fd in opened.values():os.close(fd)
        os.close(pfd)


def identity(info):return [info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns]


def read_image(fd,name):
    handle=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
    try:
        info=os.fstat(handle)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or not 0<info.st_size<=LIMIT:raise InventoryFailure('ARTWORK_FILE_UNSAFE')
        chunks=[];remaining=LIMIT+1
        while remaining:
            chunk=os.read(handle,min(65536,remaining))
            if not chunk:break
            chunks.append(chunk);remaining-=len(chunk)
        data=b''.join(chunks)
        from artwork_vfs import image_valid
        if len(data)!=info.st_size or not image_valid(data):raise InventoryFailure('ARTWORK_IMAGE_INVALID')
        return dict(identity=identity(info),bytes=len(data),sha=hashlib.sha256(data).hexdigest())
    finally:os.close(handle)


def free():
    try:
        s=os.statvfs(profile());return s.f_bavail*s.f_frsize
    except OSError:return None


def inventory(cancel=lambda:False,progress=lambda **kw:None):
    """No marker/journal/DB creation; UI invocation alone cannot authorize delete."""
    result=dict(files=0,bytes=0,skipped=0,entries=[],free=free(),complete=True)
    with roots() as (pfd,opened):
        result['roots']={name:identity(os.fstat(fd))[:2] for name,fd in opened.items()}
        result['profile']=identity(os.fstat(pfd))[:2]
        for name,fd in opened.items():
            for leaf in os.listdir(fd):
                if cancel():result['complete']=False;return result
                if not valid_name(leaf):result['skipped']+=1;continue
                try:record=read_image(fd,leaf)
                except (OSError,ValueError):result['skipped']+=1;continue
                record.update(root=name,name=leaf);result['entries'].append(record);result['files']+=1;result['bytes']+=record['bytes']
                if result['files']%32==0:progress(stage='INVENTORY',files=result['files'],bytes=result['bytes'])
    return result


def _db():
    if os.path.islink(filename()):raise InventoryFailure('ARTWORK_DB_UNSAFE')
    db=sqlite3.connect(filename(),timeout=.05);db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,profile TEXT,roots TEXT,free_before INTEGER);'
                    'CREATE TABLE IF NOT EXISTS images(run TEXT,root TEXT,name TEXT,identity TEXT,bytes INTEGER,sha TEXT,phase TEXT,PRIMARY KEY(run,root,name));')
    return db


def prepare(snapshot,confirmed=False):
    """Only after inventory+double confirmation. Journal contains no private URLs."""
    from artwork_config import read
    if confirmed is not True or read()['mode']!='dynamic' or not snapshot.get('complete') or not snapshot.get('files'):raise InventoryFailure('CLEANUP_NOT_AUTHORIZED')
    import json
    ident=uuid.uuid4().hex;db=_db()
    try:
        with db:
            db.execute('INSERT INTO runs VALUES(?,?,?,?)',(ident,json.dumps(snapshot['profile']),json.dumps(snapshot['roots']),snapshot['free']))
            db.executemany("INSERT INTO images VALUES(?,?,?,?,?,?,'PENDING')",[(ident,r['root'],r['name'],json.dumps(r['identity']),r['bytes'],r['sha']) for r in snapshot['entries']])
        return ident
    finally:db.close()


def pending():
    if not os.path.isfile(filename()):return None
    db=sqlite3.connect('file:'+__import__('urllib.parse',fromlist=['quote']).quote(filename(),safe='/')+'?mode=ro',uri=True,timeout=.05)
    try:
        row=db.execute("SELECT r.id,count(*),sum(i.bytes) FROM runs r JOIN images i ON i.run=r.id WHERE i.phase!='DONE' GROUP BY r.id ORDER BY r.rowid DESC LIMIT 1").fetchone()
        return dict(id=row[0],files=row[1],bytes=row[2]) if row else None
    finally:db.close()


def _reconcile(ident):
    from artwork_db import path
    if not os.path.isfile(path()):return
    if os.path.islink(path()):raise InventoryFailure('ARTWORK_DB_UNSAFE')
    db=sqlite3.connect(path(),timeout=.05)
    try:
        with db:db.execute("UPDATE jobs SET status='MISSING',bytes=0,updated=? WHERE ident=? AND status='READY'",(time.time(),ident))
    finally:db.close()


def execute(challenge,confirmed=False,cancel=lambda:False,progress=lambda **kw:None):
    from artwork_config import read
    from artwork_gate import writer
    import json
    if confirmed is not True or read()['mode']!='dynamic':raise InventoryFailure('CLEANUP_NOT_AUTHORIZED')
    with writer():
        if read()['mode']!='dynamic':raise InventoryFailure('CLEANUP_NOT_AUTHORIZED')
        from artwork_migration import status
        if status()['stage'] not in ('IDLE','ACTIVE','CLEANED'):raise InventoryFailure('MIGRATION_PENDING')
        db=_db();done=0;removed=0
        try:
            run=db.execute('SELECT * FROM runs WHERE id=?',(challenge,)).fetchone()
            if run is None:raise InventoryFailure('CLEANUP_NOT_AUTHORIZED')
            with roots() as (pfd,opened):
                if identity(os.fstat(pfd))[:2]!=json.loads(run['profile']):raise InventoryFailure('ARTWORK_ROOT_CHANGED')
                root_ids=json.loads(run['roots'])
                rows=db.execute("SELECT * FROM images WHERE run=? AND phase!='DONE' ORDER BY root,name",(challenge,)).fetchall()
                for row in rows:
                    if cancel():break
                    name=row['root'];leaf=row['name']
                    if name not in ROOTS or name not in opened or not valid_name(leaf):raise InventoryFailure('ARTWORK_ROOT_UNSAFE')
                    fd=opened[name]
                    actual=os.stat(name,dir_fd=pfd,follow_symlinks=False)
                    if stat.S_ISLNK(actual.st_mode) or identity(actual)[:2]!=root_ids[name] or identity(os.fstat(fd))[:2]!=root_ids[name]:raise InventoryFailure('ARTWORK_ROOT_CHANGED')
                    try:value=read_image(fd,leaf)
                    except FileNotFoundError:
                        if row['phase'] not in ('DELETING','DELETED'):raise InventoryFailure('ARTWORK_SOURCE_CHANGED') from None
                        value=None
                    if value:
                        if value['identity']!=json.loads(row['identity']) or value['sha']!=row['sha'] or value['bytes']!=row['bytes']:raise InventoryFailure('ARTWORK_SOURCE_CHANGED')
                        latest=os.stat(leaf,dir_fd=fd,follow_symlinks=False)
                        if identity(latest)!=value['identity']:raise InventoryFailure('ARTWORK_SOURCE_CHANGED')
                        with db:db.execute("UPDATE images SET phase='DELETING' WHERE run=? AND root=? AND name=?",(challenge,name,leaf))
                        os.unlink(leaf,dir_fd=fd);removed+=row['bytes']
                    with db:db.execute("UPDATE images SET phase='DELETED' WHERE run=? AND root=? AND name=?",(challenge,name,leaf))
                    if name=='media_art_v1':_reconcile(leaf[:-4])
                    with db:db.execute("UPDATE images SET phase='DONE' WHERE run=? AND root=? AND name=?",(challenge,name,leaf))
                    done+=1
                    if done%16==0:progress(stage='CLEANUP',done=done,files=len(rows),done_bytes=removed)
            after=free();return dict(done=done,removed_bytes_this_run=removed,free_before=run['free_before'],free_after=after,measured_free_delta=after-run['free_before'] if isinstance(after,int) and isinstance(run['free_before'],int) else None,pending=pending() is not None)
        finally:db.close()

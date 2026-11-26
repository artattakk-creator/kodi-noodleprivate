"""Explicit, private, hash-guarded file plans. Never called by startup/service."""
import errno,hashlib,json,os,stat,tempfile,time,uuid
from contextlib import nullcontext
from pathlib import Path
LIMIT=8*1024*1024


def sha(data):return hashlib.sha256(data).hexdigest()


def private_folder(name):
    from utils import addon_data_dir
    base=Path(addon_data_dir())
    root=base/name
    if not base.is_absolute() or base.is_symlink() or root.is_symlink():raise ValueError('UNSAFE_BACKUP_FOLDER')
    try:root.mkdir(mode=0o700)
    except FileExistsError:
        if not root.is_dir() or root.is_symlink():raise ValueError('UNSAFE_BACKUP_FOLDER') from None
    else:sync_dir(base)
    return root.resolve(strict=True)


def folder():
    return private_folder('widget50_plans')


def plan_id(token):
    if not isinstance(token,str) or len(token)!=32 or any(c not in '0123456789abcdef' for c in token):
        raise ValueError('UNSAFE_PLAN')
    return token


def sync_dir(path):
    """Persist new and replaced directory entries where the filesystem supports it."""
    if not hasattr(os,'O_DIRECTORY'):return
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:
        try:os.fsync(fd)
        except OSError as exc:
            if exc.errno not in (errno.EINVAL,errno.ENOTSUP,errno.ENOSYS):raise
    finally:os.close(fd)


def read(path):
    path=Path(path)
    if path.is_symlink():raise ValueError('UNSAFE_TARGET')
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
    with os.fdopen(fd,'rb') as stream:
        info=os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size>LIMIT:raise ValueError('UNSAFE_TARGET')
        data=stream.read(LIMIT+1)
        if len(data)>LIMIT:raise ValueError('UNSAFE_TARGET')
        return data


def private(path,data):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())


def replace(path,data,expected,mode=0o600):
    path=Path(path);fd,temp=tempfile.mkstemp(prefix='.xcmate50-',dir=path.parent)
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        if sha(read(path))!=expected:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
        os.replace(temp,path)
        sync_dir(path.parent)
        if sha(read(path))!=sha(data):raise ValueError('TARGET_VERIFY_FAILED')
    finally:
        if os.path.exists(temp):os.unlink(temp)


def state(plan,value):
    path=folder()/plan['id']/'state.json';data=json.dumps(dict(state=value)).encode()
    if path.exists():replace(path,data,sha(read(path)))
    else:private(path,data)


def prepare(kind,changes,metadata=None,*,originals=None):
    if kind not in ('binding','skin') or not 1<=len(changes)<=(8 if kind=='skin' else 4):raise ValueError('UNSAFE_PLAN')
    if len(changes) in (6,7):raise ValueError('UNSAFE_PLAN')
    if len(changes)==8:
        from widget_skin78 import FILES
        if [Path(p).name for p,_ in changes]!=[Path(p).name for p in FILES]:raise ValueError('UNSAFE_PLAN')
    if len(changes)==5 and [Path(p).name for p,_ in changes]!=['IncludesHomeWidgets.xml','IncludesHomeBingie.xml','overrides.xml','template.xml','IncludesBingie.xml']:raise ValueError('UNSAFE_PLAN')
    if originals is not None and len(originals)!=len(changes):raise ValueError('UNSAFE_PLAN')
    token=uuid.uuid4().hex;root=folder()/token;root.mkdir(mode=0o700)
    entries=[]
    for index,(target,new) in enumerate(changes):
        target=Path(target)
        if target.is_symlink():raise ValueError('UNSAFE_TARGET')
        old=read(target);target=target.resolve()
        if originals is not None and old!=originals[index]:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
        if not isinstance(new,bytes) or len(new)>LIMIT:raise ValueError('UNSAFE_PLAN')
        private(root/('original.'+str(index)),old);private(root/('candidate.'+str(index)),new)
        if read(root/('original.'+str(index)))!=old or read(root/('candidate.'+str(index)))!=new:raise ValueError('BACKUP_VERIFY_FAILED')
        check=root/('restore-check.'+str(index));private(check,new)
        replace(check,old,sha(new))
        if read(check)!=old:raise ValueError('BACKUP_VERIFY_FAILED')
        entries.append(dict(target=str(target),before=sha(old),after=sha(new),mode=stat.S_IMODE(target.stat().st_mode)))
    plan=dict(id=token,kind=kind,entries=entries,metadata=metadata or {},at=time.time())
    private(root/'plan.json',json.dumps(plan).encode());state(plan,'PREPARED')
    sync_dir(root);sync_dir(root.parent)
    return plan


def load(token,kind):
    root=folder()/plan_id(token)
    if root.is_symlink():raise ValueError('UNSAFE_PLAN')
    plan=json.loads(read(root/'plan.json'))
    if plan.get('id')!=token or plan.get('kind')!=kind:raise ValueError('UNSAFE_PLAN')
    return plan


def apply(token,kind,targets,*,confirmed=False,restore=False):
    if confirmed is not True:raise PermissionError('EXPLICIT_APPROVAL_REQUIRED')
    try:import fcntl
    except ImportError:raise ValueError('PATCH_LOCK_UNAVAILABLE') from None
    from skin_patch103 import phase
    scope=phase if kind=='skin' else lambda _:nullcontext()
    with scope('journal'):
        root=folder()
        lock_path=root/'.lock'
        if lock_path.is_symlink():raise ValueError('UNSAFE_BACKUP_FOLDER')
        try:fd=os.open(lock_path,os.O_WRONLY|os.O_CREAT|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0),0o600)
        except OSError as exc:
            if exc.errno==errno.ELOOP:raise ValueError('UNSAFE_BACKUP_FOLDER') from None
            raise
    with os.fdopen(fd,'a') as lock, scope('journal'):
        if not stat.S_ISREG(os.fstat(lock.fileno()).st_mode):raise ValueError('UNSAFE_BACKUP_FOLDER')
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('PLAN_BUSY') from None
        plan=load(token,kind);entries=plan['entries']
        if len(entries)!=len(targets):raise ValueError('UNSAFE_PLAN')
        payload=[]
        for i,(entry,target) in enumerate(zip(entries,targets)):
            target=Path(target)
            if target.is_symlink() or str(target.resolve())!=entry['target']:raise ValueError('UNSAFE_TARGET')
            old=read(root/token/('original.'+str(i)));new=read(root/token/('candidate.'+str(i)))
            if sha(old)!=entry['before'] or sha(new)!=entry['after']:raise ValueError('BACKUP_VERIFY_FAILED')
            with scope('target'):
                current=sha(read(target));allowed=(entry['before'],entry['after']) if restore else (entry['before'],)
                if current not in allowed:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
            payload.append((target,entry,old,new,current))
        done=[];state(plan,'RESTORING' if restore else 'APPLYING')
        try:
            # Install definitions before callers; restore callers before definitions.
            with scope('target'):
                for target,entry,old,new,current in (reversed(payload) if restore else payload):
                    data=old if restore else new
                    if current==sha(data):continue
                    done.append((target,entry,old,new))
                    replace(target,data,current,entry['mode'])
        except Exception as exc:
            blocked=False
            if not restore:
                for target,entry,old,new in reversed(done):
                    try:
                        current=sha(read(target))
                        if current==entry['before']:continue
                        if current!=entry['after']:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
                        replace(target,old,entry['after'],entry['mode'])
                    except (OSError,ValueError):blocked=True
            outcome='INTERRUPTED' if restore or blocked else 'ROLLED_BACK'
            state(plan,outcome)
            if kind=='skin' and hasattr(exc,'stage'):exc.journal=outcome
            raise
        state(plan,'RESTORED' if restore else 'APPLIED')
        return dict(code='RESTORED' if restore else 'SAVED',id=token)

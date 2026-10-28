"""Explicit, private, hash-guarded file plans. Never called by startup/service."""
import hashlib,json,os,stat,tempfile,time,uuid
from pathlib import Path
LIMIT=8*1024*1024


def sha(data):return hashlib.sha256(data).hexdigest()


def folder():
    from utils import addon_data_dir
    root=Path(addon_data_dir())/'widget50_plans'
    if root.is_symlink():raise ValueError('UNSAFE_BACKUP_FOLDER')
    root.mkdir(mode=0o700,exist_ok=True)
    return root.resolve()


def read(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>LIMIT:raise ValueError('UNSAFE_TARGET')
    return path.read_bytes()


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
        if sha(read(path))!=sha(data):raise ValueError('TARGET_VERIFY_FAILED')
    finally:
        if os.path.exists(temp):os.unlink(temp)


def state(plan,value):
    path=folder()/plan['id']/'state.json';data=json.dumps(dict(state=value)).encode()
    if path.exists():replace(path,data,sha(read(path)))
    else:private(path,data)


def prepare(kind,changes,metadata=None):
    if kind not in ('binding','skin') or not 1<=len(changes)<=4:raise ValueError('UNSAFE_PLAN')
    token=uuid.uuid4().hex;root=folder()/token;root.mkdir(mode=0o700)
    entries=[]
    for index,(target,new) in enumerate(changes):
        target=Path(target)
        if target.is_symlink():raise ValueError('UNSAFE_TARGET')
        old=read(target);target=target.resolve()
        if not isinstance(new,bytes) or len(new)>LIMIT:raise ValueError('UNSAFE_PLAN')
        private(root/('original.'+str(index)),old);private(root/('candidate.'+str(index)),new)
        if read(root/('original.'+str(index)))!=old or read(root/('candidate.'+str(index)))!=new:raise ValueError('BACKUP_VERIFY_FAILED')
        check=root/('restore-check.'+str(index));private(check,new)
        replace(check,old,sha(new))
        if read(check)!=old:raise ValueError('BACKUP_VERIFY_FAILED')
        entries.append(dict(target=str(target),before=sha(old),after=sha(new),mode=stat.S_IMODE(target.stat().st_mode)))
    plan=dict(id=token,kind=kind,entries=entries,metadata=metadata or {},at=time.time())
    private(root/'plan.json',json.dumps(plan).encode());state(plan,'PREPARED')
    return plan


def load(token,kind):
    if len(token)!=32 or any(c not in '0123456789abcdef' for c in token):raise ValueError('UNSAFE_PLAN')
    root=folder()/token
    if root.is_symlink():raise ValueError('UNSAFE_PLAN')
    plan=json.loads(read(root/'plan.json'))
    if plan.get('id')!=token or plan.get('kind')!=kind:raise ValueError('UNSAFE_PLAN')
    return plan


def apply(token,kind,targets,*,confirmed=False,restore=False):
    if confirmed is not True:raise PermissionError('EXPLICIT_APPROVAL_REQUIRED')
    import fcntl
    root=folder();lock=open(root/'.lock','a')
    try:
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
            current=sha(read(target));allowed=(entry['before'],entry['after']) if restore else (entry['before'],)
            if current not in allowed:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
            payload.append((target,entry,old,new,current))
        done=[];state(plan,'RESTORING' if restore else 'APPLYING')
        try:
            # Install definitions before callers; restore callers before definitions.
            for target,entry,old,new,current in (reversed(payload) if restore else payload):
                data=old if restore else new
                if current==sha(data):continue
                done.append((target,entry,old,new))
                replace(target,data,current,entry['mode'])
        except Exception:
            blocked=False
            if not restore:
                for target,entry,old,new in reversed(done):
                    try:
                        current=sha(read(target))
                        if current==entry['before']:continue
                        if current!=entry['after']:raise ValueError('TARGET_CHANGED_NO_OVERWRITE')
                        replace(target,old,entry['after'],entry['mode'])
                    except (OSError,ValueError):blocked=True
            state(plan,'INTERRUPTED' if restore or blocked else 'ROLLED_BACK')
            raise
        state(plan,'RESTORED' if restore else 'APPLIED')
        return dict(code='RESTORED' if restore else 'SAVED',id=token)
    finally:lock.close()

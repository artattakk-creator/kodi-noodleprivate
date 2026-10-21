"""Artwork-only policy and verified, non-destructive local-volume migration.

All policy files and locks stay in the private addon profile. URI paths never
reach Python filesystem calls. Kodi VFS cannot report target free bytes, so
unmounted SMB/VFS destinations pause explicitly rather than guessing a reserve.
"""
import contextlib
import errno
import hashlib
import json
import os
import shutil
import threading
import time
import uuid
from urllib.parse import urlsplit

MIB=1024*1024
MAX_MB=1024*1024
PROFILES={'small':256,'standard':1024,'large':16384,'auto':0}
_guard=threading.RLock()
_usage={}
_migration=None


class Paused(OSError):
    def __init__(self,code):
        super().__init__(errno.ENOSPC if code in ('QUOTA_FULL','DISK_LOW','DISK_FULL') else errno.EAGAIN,code)
        self.code=code


def _profile():
    from utils import addon_data_dir
    return addon_data_dir()


def _path(name):return os.path.join(_profile(),name)
def default_root():return _path('media_art_v1')


def _read(name):
    try:
        with open(_path(name),encoding='utf-8') as stream:value=json.load(stream)
        return value if isinstance(value,dict) else {}
    except (OSError,ValueError):return {}


def _save(name,value):
    filename=_path(name);tmp=filename+'.'+uuid.uuid4().hex+'.tmp'
    try:
        fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(value,stream);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,filename)
        fd=os.open(_profile(),os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        try:os.unlink(tmp)
        except FileNotFoundError:pass


def policy():
    from utils import setting_int
    saved=_read('media_art_storage_v1.json')
    if not saved:
        if os.path.exists(_path('media_art_storage_v1.json')):raise Paused('POLICY_INVALID')
        return dict(profile='legacy',budget_mb=max(32,setting_int('media_art_budget_mb',512)),
                    reserve_mb=32,root=default_root(),previous=[],generation='legacy')
    if (saved.get('profile') not in (*PROFILES,'expert','legacy') or
            not isinstance(saved.get('root'),str) or
            not isinstance(saved.get('budget_mb'),int) or saved['budget_mb']<0 or
            not isinstance(saved.get('reserve_mb'),int) or saved['reserve_mb']<32):
        raise Paused('POLICY_INVALID')
    return saved


def root():return policy()['root']

def is_vfs(path):return bool(urlsplit(path).scheme) and not os.path.isabs(path)


def _available(config):
    path=config['root']
    if is_vfs(path):
        # Kodi VFS exists/Stat do not provide reliable free-volume capacity.
        # Never leak credentials by returning/logging the URI or exception.
        raise Paused('CAPACITY_UNKNOWN')
    if config.get('marker'):
        try:
            with open(os.path.join(path,'.xcmate-artwork-volume'),encoding='ascii') as stream:
                if stream.read(64)!=config['marker']:raise Paused('STORAGE_OFFLINE')
        except OSError:raise Paused('STORAGE_OFFLINE') from None
    else:
        # Only the original addon-owned internal directory may be recreated.
        if os.path.realpath(path)!=os.path.realpath(default_root()):raise Paused('STORAGE_OFFLINE')
        os.makedirs(path,exist_ok=True)
    try:return shutil.disk_usage(path)
    except OSError:raise Paused('STORAGE_OFFLINE') from None


def used(refresh=False,config=None):
    cfg=config or policy();path=cfg['root'];now=time.monotonic()
    prior=_usage.get(path)
    if prior and not refresh and now-prior[0]<60:return prior[1]
    _available(cfg)  # detached destinations must not be recreated
    total=0
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file(follow_symlinks=False) and (entry.name.endswith('.img') or entry.name.startswith('.art-')):
                total+=entry.stat(follow_symlinks=False).st_size
    _usage[path]=(now,total)
    return total


def invalidate():_usage.clear()


def account(path,delta):
    prior=_usage.get(path)
    if prior:_usage[path]=(prior[0],max(0,prior[1]+delta))


def budget():
    cfg=policy()
    if cfg['profile']!='auto':return cfg['budget_mb']*MIB
    capacity=_available(cfg)
    return used(config=cfg)+max(0,capacity.free-cfg['reserve_mb']*MIB)


def check(size=0,quota=True):
    cfg=policy();capacity=_available(cfg)
    if quota and budget()-used(config=cfg)<size:raise Paused('QUOTA_FULL')
    if capacity.free<cfg['reserve_mb']*MIB+size:raise Paused('DISK_LOW')
    return cfg['root']


@contextlib.contextmanager
def lock(exclusive=False):
    # Nonblocking: a key or another process never waits for a large copy.
    if not _guard.acquire(blocking=False):raise Paused('MIGRATING')
    fd=None
    try:
        try:import fcntl
        except ImportError:raise Paused('LOCK_UNSUPPORTED') from None
        fd=os.open(_path('media_art_storage.lock'),os.O_CREAT|os.O_RDWR,0o600)
        try:fcntl.flock(fd,(fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)|fcntl.LOCK_NB)
        except OSError:raise Paused('MIGRATING') from None
        yield
    finally:
        if fd is not None:os.close(fd)
        _guard.release()


def _new_policy(profile,budget_mb=None,reserve_mb=512):
    if profile not in (*PROFILES,'expert'):raise ValueError('invalid profile')
    amount=int(budget_mb) if profile=='expert' else PROFILES[profile]
    reserve=int(reserve_mb)
    if profile!='auto' and not 32<=amount<=MAX_MB:raise ValueError('budget: 32..1048576 MiB')
    if not 32<=reserve<=MAX_MB:raise ValueError('reserve: 32..1048576 MiB')
    cfg=policy();cfg.update(profile=profile,budget_mb=amount,reserve_mb=reserve,generation=uuid.uuid4().hex)
    return cfg


def configure(profile,budget_mb=None,reserve_mb=512):
    with lock(exclusive=True):
        cfg=_new_policy(profile,budget_mb,reserve_mb)
        _available(cfg) # preserve old policy if target disappeared
        _save('media_art_storage_v1.json',cfg)
    from art_store import resume_capacity
    import sqlite3
    try:resume_capacity()
    except (sqlite3.Error,OSError):pass # saved policy remains valid; DB health reports the queue problem
    return cfg


def _hash(path):
    digest=hashlib.sha256()
    with open(path,'rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def _migrate_locked(parent,cancel=lambda:False):
    """Worker only, after explicit confirmation. Originals always survive.

    Resume after interruption by selecting the same destination. Each file is
    verified anew; the active root changes only after the entire copy verifies.
    """
    result=dict(code='COPYING',copied=0,verified=0,updated=time.time())
    with lock(exclusive=True):
        cfg=policy();source=cfg['root']
        try:
            if is_vfs(parent):raise Paused('CAPACITY_UNKNOWN')
            if not os.path.isabs(parent) or not os.path.isdir(parent):raise Paused('STORAGE_OFFLINE')
            target=os.path.join(os.path.realpath(parent),'XCMateArtwork','media_art_v1')
            if os.path.realpath(source)==target:raise ValueError('same destination')
            # Reject nested source/target layouts and symbolic-link destinations.
            if os.path.commonpath([os.path.realpath(source),target]) in (os.path.realpath(source),target):
                raise ValueError('nested destination')
            cursor=target
            while cursor!=os.path.dirname(cursor):
                if os.path.islink(cursor):raise ValueError('symlink destination')
                cursor=os.path.dirname(cursor)
            _available(cfg)
            os.makedirs(target,exist_ok=True)
            marker_file=os.path.join(target,'.xcmate-artwork-volume')
            if os.path.exists(marker_file):
                with open(marker_file,encoding='ascii') as stream:marker=stream.read(64)
                if len(marker)!=32 or any(c not in '0123456789abcdef' for c in marker):raise ValueError('invalid marker')
            else:
                marker=uuid.uuid4().hex
                with open(marker_file,'x',encoding='ascii') as stream:stream.write(marker);stream.flush();os.fsync(stream.fileno())
            destination=dict(cfg,root=target,marker=marker)
            result.update(source=source,target=target)
            _save('media_art_migration_v1.json',result)
            with os.scandir(source) as entries:
                for entry in entries:
                    if not entry.name.endswith('.img'):continue
                    if not entry.is_file(follow_symlinks=False):raise ValueError('nonregular image')
                    if cancel():raise InterruptedError()
                    dest=os.path.join(target,entry.name);digest=_hash(entry.path)
                    if not os.path.isfile(dest) or os.path.islink(dest) or _hash(dest)!=digest:
                        if os.path.lexists(dest):raise ValueError('destination conflict')
                        capacity=_available(destination)
                        if capacity.free<entry.stat().st_size+cfg['reserve_mb']*MIB:raise Paused('DISK_LOW')
                        tmp=dest+'.partial-'+uuid.uuid4().hex
                        try:
                            with open(entry.path,'rb') as inp,open(tmp,'xb') as out:
                                while True:
                                    if cancel():raise InterruptedError()
                                    chunk=inp.read(1024*1024)
                                    if not chunk:break
                                    if _available(destination).free<len(chunk)+cfg['reserve_mb']*MIB:raise Paused('DISK_LOW')
                                    out.write(chunk)
                                out.flush();os.fsync(out.fileno())
                            if _hash(tmp)!=digest:raise ValueError('copy verification failed')
                            os.replace(tmp,dest);result['copied']+=1
                        finally:
                            try:os.unlink(tmp)
                            except FileNotFoundError:pass
                    if _hash(dest)!=digest:raise ValueError('final verification failed')
                    result['verified']+=1
                    if result['verified']%32==0:_save('media_art_migration_v1.json',result)
            fd=os.open(target,os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
            try:os.fsync(fd)
            finally:os.close(fd)
            _available(destination)
            destination.update(previous=list(dict.fromkeys([source]+cfg.get('previous',[]))),generation=uuid.uuid4().hex)
            _save('media_art_storage_v1.json',destination)
            invalidate();result['code']='VERIFIED'
        except Exception as exc:
            result['code']=getattr(exc,'code','CANCELLED' if isinstance(exc,InterruptedError) else 'FAILED')
            result['error']=type(exc).__name__  # no private path or URI
        result['updated']=time.time();_save('media_art_migration_v1.json',result)
    return result


def migrate(parent,cancel=lambda:False):
    try:return _migrate_locked(parent,cancel)
    except Paused as exc:
        result=dict(code=exc.code,copied=0,verified=0,updated=time.time())
        _save('media_art_migration_v1.json',result)
        return result


def _migration_worker(parent):
    import xbmc
    monitor=xbmc.Monitor()
    # The GUI returns immediately. Existing bounded fetches may finish before
    # migration acquires its exclusive volume lock; new queue work is paused.
    for _ in range(40):
        result=migrate(parent,cancel=monitor.abortRequested)
        if result['code']!='MIGRATING':break
        if monitor.waitForAbort(.25):break
    from art_store import resume_capacity
    try:resume_capacity()
    except Exception:pass


def start_migration(parent):
    global _migration
    if _migration is not None and _migration.is_alive():return False
    from art_store import pause_migration
    pause_migration()
    _migration=threading.Thread(target=_migration_worker,args=(parent,),daemon=True,name='XCMate-art-migration')
    _migration.start();return True


def candidates():
    cfg=policy()
    for path in dict.fromkeys([cfg['root']]+cfg.get('previous',[])):
        if not is_vfs(path):yield path


def diagnostic():
    cfg=policy();result=dict(profile=cfg['profile'],budget_mb=cfg['budget_mb'],reserve_mb=cfg['reserve_mb'],
                            root=cfg['root'] if not is_vfs(cfg['root']) else 'VFS',code='OK',
                            migration=_read('media_art_migration_v1.json'))
    try:
        capacity=_available(cfg)
        result.update(total=capacity.total,free=capacity.free,used=used(refresh=True),budget=budget())
    except Paused as exc:result['code']=exc.code
    return result

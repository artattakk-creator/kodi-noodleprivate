"""Profile-local versioned choice. Missing mode never means fresh installation.

Only the entry/service preflight positively initializes an empty profile;
ordinary image/status reads default safely to the existing internal archive.
No Kodi settings, pictures, jobs, texture cache or portal data are rewritten.
"""
import contextlib
import fcntl
import json
import os
import tempfile
import time
import uuid

VERSION=1
NAME='artwork_config_v1.json'
MODES=('dynamic','internal','external')


def root():
    from utils import addon_data_dir
    return addon_data_dir()


def read():
    try:
        with open(os.path.join(root(),NAME),encoding='utf-8') as stream:value=json.load(stream)
        if value.get('version')==VERSION and value.get('mode') in MODES and isinstance(value.get('profile'),str) and len(value['profile'])==32:
            return value
    except (OSError,ValueError,TypeError,AttributeError):pass
    return dict(version=0,mode='internal',strategy='demand',target='',profile='')


@contextlib.contextmanager
def locked():
    fd=os.open(os.path.join(root(),'.artwork-config.lock'),os.O_CREAT|os.O_RDWR,0o600)
    try:
        deadline=time.monotonic()+.05
        while True:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);break
            except BlockingIOError:
                if time.monotonic()>=deadline:raise
                time.sleep(.005)
        yield
    finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)


def _write(value):
    fd,temp=tempfile.mkstemp(prefix='.artwork-config-',dir=root())
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(value,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
        os.replace(temp,os.path.join(root(),NAME));temp=''
        directory=os.open(root(),os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if temp:
            try:os.unlink(temp)
            except OSError:pass


def initialize():
    """Run BEFORE setup/data workers. Any unknown/legacy signal fails internal."""
    with locked():
        value=read()
        if value['version']==VERSION:return value
        entries=[name for name in os.listdir(root()) if name!='.artwork-config.lock' and not name.startswith('.artwork-config-')]
        fresh=not entries
        value=dict(version=VERSION,mode='dynamic' if fresh else 'internal',strategy='demand',target='',
                   profile=uuid.uuid4().hex,origin='FRESH' if fresh else 'LEGACY')
        _write(value);return value


def choose(mode,*,target=None,strategy=None):
    """Explicit UI action only; external activation is owned by the migrator."""
    if mode not in MODES:raise ValueError('INVALID_ARTWORK_MODE')
    initialize()
    with locked():
        value=read()
        if mode=='external' and not target:raise ValueError('VERIFIED_TARGET_REQUIRED')
        value['mode']=mode
        if target is not None:value['target']=target
        if strategy is not None:
            if strategy not in ('demand','all'):raise ValueError('INVALID_ARTWORK_STRATEGY')
            value['strategy']=strategy
        _write(value);return value


def persistent():return read()['mode']!='dynamic'

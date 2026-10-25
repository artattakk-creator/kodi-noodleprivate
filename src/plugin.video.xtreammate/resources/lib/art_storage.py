"""Artwork-only capacity policy. Never changes settings or removes cached files."""
import errno
import hashlib
import os
import xml.etree.ElementTree as ET

MIB=1048576
MIN_RESERVE=32*MIB
WRITE_HEADROOM=256*1024  # SQLite/page/allocation overhead beyond image bytes


class ArtworkFailure(OSError):
    def __init__(self,code,reason='',storage=None):
        self.code=code;self.reason=reason;self.storage=storage or {}
        super().__init__(errno.ENOSPC if code=='DISK_FULL' else errno.EDQUOT if code=='BUDGET_FULL' else errno.EIO,code)


def budget():
    from utils import setting_int,addon_data_dir
    value=max(0,setting_int('media_art_budget_mb',0))
    # Kodi persists default-valued settings too. A saved default 512 is not
    # evidence of an intentional cap. Explicit values (including 512) survive.
    if value==512:
        try:
            node=ET.parse(os.path.join(addon_data_dir(),'settings.xml')).find(".//setting[@id='media_art_budget_mb']")
            if node is not None and node.get('default')=='true':value=0
        except (OSError,ET.ParseError):pass
    return value*MIB


def reserve():
    from utils import setting_int
    return max(MIN_RESERVE,setting_int('media_art_reserve_mb',1024)*MIB)


def capacity(location=None,backend=None):
    from artwork_backend import active_backend,LocalArtworkStorage
    storage=backend if backend is not None else active_backend() if location is None else LocalArtworkStorage(location)
    value=storage.free_or_unknown()
    external=bool((getattr(storage,'is_external',False) is True))
    separate=external and not value.get('same_as_internal',False)
    protected=max(MIN_RESERVE,min(256*MIB,int(value['total']*.02))) if separate and value.get('total') else MIN_RESERVE if separate else reserve()
    from artwork_config import read
    if not separate and read().get('reserve_policy')=='adaptive' and value.get('total'):
        protected=max(64*MIB,min(reserve(),int(value['total']*.02)))
    return dict(value,reserve=protected,budget=budget(),external=external,storage_availability='AVAILABLE' if value.get('free') is not None else storage.availability() if external else 'UNKNOWN')


def check(upcoming,limit=None,used=None,location=None,backend=None):
    value=capacity(backend=backend) if backend is not None else capacity() if location is None else capacity(location)
    if value.get('storage_availability')=='STORAGE_OFFLINE':raise ArtworkFailure('STORAGE_OFFLINE')
    if value.get('free') is None:
        if not value.get('external'):raise ArtworkFailure('CACHE_ERROR','CAPACITY_UNKNOWN',value)
        # Explicitly probed VFS: bounded verified write, capacity stays UNKNOWN.
    elif value['free']<value['reserve']+max(0,upcoming)+WRITE_HEADROOM:
        reason='BLOCKED_REAL_DISK' if value['free']<max(0,upcoming)+WRITE_HEADROOM else 'RESERVE_BLOCKED'
        raise ArtworkFailure('DISK_FULL',reason,value)
    limit=budget() if limit is None else limit
    if limit:
        if used is None:
            from art_store import used as current_bytes
            used=current_bytes()
        if used+upcoming>limit:raise ArtworkFailure('BUDGET_FULL','BUDGET_FULL',value)
    return value


def token():
    # Actual free bytes are intentionally excluded: a fluctuating disk does
    # not grant unbounded fresh retries to an already exhausted job.
    from artwork_config import read
    config=read();policy='v20:%d:%d'%(budget(),reserve())
    if config['mode']=='external' or config.get('reserve_policy')=='adaptive':
        policy+=':v37:'+str(config.get('target',''))+':'+str(config.get('reserve_policy','fixed'))
    return hashlib.sha256(policy.encode()).hexdigest()


def explain(value,upcoming,used=None):
    if value.get('storage_availability')=='STORAGE_OFFLINE':return 'STORAGE_OFFLINE'
    free=value.get('free');reserve_bytes=value.get('reserve');limit=value.get('budget')
    if not isinstance(free,(int,float)) or not isinstance(reserve_bytes,(int,float)):return 'UNKNOWN'
    if free<max(0,upcoming)+WRITE_HEADROOM:return 'BLOCKED_REAL_DISK'
    if free<reserve_bytes+max(0,upcoming)+WRITE_HEADROOM:return 'RESERVE_BLOCKED'
    if limit:
        if used is None:return 'UNKNOWN'
        if used+upcoming>limit:return 'BUDGET_FULL'
    return 'OK'

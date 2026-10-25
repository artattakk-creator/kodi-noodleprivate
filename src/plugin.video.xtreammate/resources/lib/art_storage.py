"""Artwork-only capacity policy. Never changes settings or removes cached files."""
import errno
import hashlib
import os
import shutil
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


def capacity(location=None):
    from media_art import folder
    root=os.fspath(location) if location is not None else folder()
    usage=shutil.disk_usage(root if os.path.isdir(root) else os.path.dirname(root))
    return dict(free=usage.free,total=usage.total,reserve=reserve(),budget=budget())


def check(upcoming,limit=None,used=None,location=None):
    value=capacity() if location is None else capacity(location)
    if value['free']<value['reserve']+max(0,upcoming)+WRITE_HEADROOM:
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
    return hashlib.sha256(('v20:%d:%d'%(budget(),reserve())).encode()).hexdigest()


def explain(value,upcoming,used=None):
    free=value.get('free');reserve_bytes=value.get('reserve');limit=value.get('budget')
    if not isinstance(free,(int,float)) or not isinstance(reserve_bytes,(int,float)):return 'UNKNOWN'
    if free<max(0,upcoming)+WRITE_HEADROOM:return 'BLOCKED_REAL_DISK'
    if free<reserve_bytes+max(0,upcoming)+WRITE_HEADROOM:return 'RESERVE_BLOCKED'
    if limit:
        if used is None:return 'UNKNOWN'
        if used+upcoming>limit:return 'BUDGET_FULL'
    return 'OK'

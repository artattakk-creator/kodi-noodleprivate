"""Artwork-only capacity policy. Never changes settings or removes cached files."""
import errno
import hashlib
import os
import shutil
import xml.etree.ElementTree as ET

MIB=1048576
MIN_RESERVE=32*MIB


class ArtworkFailure(OSError):
    def __init__(self,code):
        self.code=code
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


def capacity():
    from media_art import folder
    usage=shutil.disk_usage(os.path.dirname(folder()))
    return dict(free=usage.free,total=usage.total,reserve=reserve(),budget=budget())


def check(upcoming,limit=None,used=None):
    value=capacity()
    if value['free']<value['reserve']+max(0,upcoming):raise ArtworkFailure('DISK_FULL')
    limit=budget() if limit is None else limit
    if limit:
        if used is None:
            from art_store import used as current_bytes
            used=current_bytes()
        if used+upcoming>limit:raise ArtworkFailure('BUDGET_FULL')
    return value


def token():
    # Actual free bytes are intentionally excluded: a fluctuating disk does
    # not grant unbounded fresh retries to an already exhausted job.
    return hashlib.sha256(('v20:%d:%d'%(budget(),reserve())).encode()).hexdigest()

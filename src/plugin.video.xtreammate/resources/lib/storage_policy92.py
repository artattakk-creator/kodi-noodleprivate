"""Explicit image-EPG preference. Missing value preserves every legacy choice."""
import json
from pathlib import Path

def path():
    from utils import addon_data_dir
    return Path(addon_data_dir())/'storage_policy92.json'

def read():
    file = path()
    if not file.exists():return dict(version=1, image_epg='legacy', staging='internal')
    if file.is_symlink() or file.stat().st_size > 4096:raise OSError('STORAGE_POLICY_INVALID')
    value = json.loads(file.read_bytes())
    if value.get('version') != 1 or value.get('image_epg') not in ('yes','no','later','legacy'):
        raise OSError('STORAGE_POLICY_INVALID')
    return value

def images_enabled():
    # Read once on a data/IO path, never in a Kodi texture callback.
    try:return read()['image_epg'] in ('legacy','yes')
    except (OSError,ValueError):return False

def choose(decision):
    if decision not in ('yes','no','later'):raise ValueError('INVALID_IMAGE_EPG_CHOICE')
    from profile_transaction import writing
    from storage_metadata92 import check
    from logo_store89 import atomic
    with writing(timeout=.2):
        value = dict(read(), image_epg=decision)
        raw = json.dumps(value,sort_keys=True).encode();check(path(),len(raw),kind='policy')
        atomic(path(),raw)
        if read()!=value:raise OSError('STORAGE_POLICY_READBACK')
    return value

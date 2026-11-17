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
    if not isinstance(value,dict) or value.get('version') != 1 or value.get('image_epg') not in ('yes','no','later','legacy'):
        raise OSError('STORAGE_POLICY_INVALID')
    return value

def publish(enabled,code=None):
    try:
        import xbmcgui
        from epg_handoff63 import profile_scope
        window=xbmcgui.Window(10000);scope=profile_scope()
        window.setProperty('XCMate.Storage92.Disabled.'+scope,'' if enabled else 'true')
        window.setProperty('XCMate.Storage92.Reason.'+scope,code or ('READY' if enabled else 'IMAGE_EPG_DISABLED'))
    except (ImportError,AttributeError,RuntimeError):pass

def images_enabled():
    # Worker/startup IO only. Focus callbacks consume just the scoped property.
    try:
        choice=read()['image_epg'];enabled=choice in ('legacy','yes')
        code='READY' if enabled else 'IMAGE_EPG_DEFERRED' if choice=='later' else 'IMAGE_EPG_DISABLED'
    except (OSError,ValueError):enabled=False;code='STORAGE_POLICY_INVALID'
    publish(enabled,code);return enabled

def prepare_choice(decision):
    """Load write dependencies before any caller holds a config lock."""
    if decision not in ('yes','no','later'):raise ValueError('INVALID_IMAGE_EPG_CHOICE')
    from profile_transaction import writing
    from storage_metadata92 import check
    from logo_store89 import atomic
    def commit():
        with writing(timeout=.2):
            value = dict(read(), image_epg=decision)
            raw = json.dumps(value,sort_keys=True).encode();check(path(),len(raw),kind='policy')
            atomic(path(),raw)
            if read()!=value:raise OSError('STORAGE_POLICY_READBACK')
        return value
    return commit

def choose(decision):
    value=prepare_choice(decision)()
    publish(decision=='yes','READY' if decision=='yes' else 'IMAGE_EPG_DEFERRED' if decision=='later' else 'IMAGE_EPG_DISABLED')
    return value

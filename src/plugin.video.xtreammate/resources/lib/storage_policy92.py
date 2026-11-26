"""Legacy storage preferences and source-derived image-EPG availability."""
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
    # Worker/startup only. Focus callbacks use the scoped availability flag.
    from agent_programme100 import pictures_enabled
    from artwork_sources96 import enabled, health, token_valid
    from media_sources43 import SourceError

    code = health()
    try:
        active = code in ('READY', 'NOT_CREATED') and (
            pictures_enabled() or enabled('xmltv') or enabled('tvmaze') or
            (enabled('tmdb') and token_valid())
        )
    except SourceError as exc:
        code = exc.code
        active = False
    if code in ('READY', 'NOT_CREATED'):
        code = 'READY' if active else 'IMAGE_EPG_DISABLED'
    publish(active, code)
    return active

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
    images_enabled()
    return value

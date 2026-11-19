"""Once-per-profile authorized source migration. Token bytes are read-only.

Only service/data workers call ensure(). No file/network work in focus. Explicit
opt-outs and completed migrations are authoritative across Kodi restarts.
"""
import json,threading,time
_lock=threading.RLock();_next={}
STATE='programme_sources_state77'
FLAGS=('programme_tmdb46','tmdb_research43','programme_tvmaze67')

def explicit_off():
    """Kodi persists non-default values separately from default='true' entries.

    Inspect only the three boolean decisions; never return settings contents.
    Older explicit false values remain an opt-out, not a missing default.
    """
    from settings_guard96 import snapshot
    state=snapshot()
    return set(FLAGS)&state['explicit_off'] if state['code']=='READY' else set()

def decision(source,enabled,addon=None):
    import xbmcaddon
    addon=addon or xbmcaddon.Addon()
    addon.setSetting('programme_'+source+'_optout77','false' if enabled else 'true')
    if source=='tmdb':
        addon.setSetting('programme_tmdb46',str(bool(enabled)).lower());addon.setSetting('tmdb_research43',str(bool(enabled)).lower())
    elif source=='tvmaze':addon.setSetting('programme_tvmaze67',str(bool(enabled)).lower())

def ensure(force=False):
    from epg_handoff63 import profile_scope
    from utils import setting,setting_bool
    import xbmcaddon
    from settings_guard96 import rebuild_pending,snapshot
    if rebuild_pending():return 'RESTART_REQUIRED'
    health=snapshot()['code']
    if health not in ('READY','NOT_CREATED'):return health
    profile=profile_scope();now=time.monotonic()
    with _lock:
        if not force and now<_next.get(profile,0):return 'DEFERRED'
        _next[profile]=now+30
        while len(_next)>8:_next.pop(next(iter(_next)))
        try:value=json.loads(setting(STATE,'') or '{}')
        except (TypeError,ValueError):return 'MIGRATION_STATE_INVALID'
        if not isinstance(value,dict):return 'MIGRATION_STATE_INVALID'
        if value.get('done'):return value.get('token','CONFIGURED')
        addon=xbmcaddon.Addon();off=explicit_off() if not value.get('initialized') else set()
        if not value.get('initialized'):
            if any(key in off for key in FLAGS[:2]):addon.setSetting('programme_tmdb_optout77','true')
            if FLAGS[2] in off:addon.setSetting('programme_tvmaze_optout77','true')
            # .96: token presence/defaults alone are not consent on another
            # installation. Existing flags remain; hub/import is explicit.
            # No external supplier is enabled by this migration.
            value.update(initialized=True,notice=True)
        from tmdb_token61 import effective_tmdb_read_token,validate,TokenError
        try:
            token=effective_tmdb_read_token(force=True)
            if not token:code='TOKEN_MISSING'
            else:validate(token.encode('utf-8'));code='TOKEN_FORMAT_VALID'
        except (TokenError,OSError,UnicodeError):code='TOKEN_INVALID'
        # No token value or fingerprint is persisted/logged here.
        if code=='TOKEN_FORMAT_VALID':
            value['done']=True
        value['token']=code;addon.setSetting(STATE,json.dumps(value,separators=(',',':')))
        if value.pop('notice',False):
            from localization import tr
            from utils import notify
            notify(tr(38200));addon.setSetting(STATE,json.dumps(value,separators=(',',':')))
        return code

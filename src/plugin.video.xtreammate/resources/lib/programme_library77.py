"""Worker-only bounded negative schema lease; never repairs Kodi databases."""
import time
_seen={}
def available():
    from epg_handoff63 import profile_scope
    scope=profile_scope();now=time.monotonic();prior=_seen.get(scope)
    if prior and now<prior[0]:return prior[1]
    from kodi_schema75 import inspect
    status=inspect()
    ok=status.get('code') not in ('KODI_LIBRARY_MISSING_VIEWS','KODI_LIBRARY_INTEGRITY_ERROR','KODI_LIBRARY_VERSION_UNVERIFIED')
    _seen[scope]=(now+300,ok)
    while len(_seen)>8:_seen.pop(next(iter(_seen)))
    return ok

"""Resolve exactly one requested account; no all-account deep copy for playback.

Retry once only for a temporary read/transaction race AND a still-valid own
media intent. No credentials in properties/logs, no cached old account bypass.
"""
import time
CODES=frozenset(('OK','UNKNOWN','PROFILE_BUSY','PROFILE_RACE','PROFILE_BUDGET','INVALID_PROFILE','READ_IO','MEMORY','MEMORY_PAUSE','CANCELLED','DISABLED','NOT_FOUND'))


def trace(stage,reason='OK',origin='catalog'):
    if stage not in ('PORTAL_READ','PORTAL_RETRY','INTENT','RESOLVE','REJECTED'):return
    reason=reason if reason in CODES else 'UNKNOWN'
    origin=origin if origin in ('search','catalog','widget') else 'other'
    try:
        import xbmc
        xbmc.log('[XCMate][MEDIA44] stage='+stage+' reason='+reason+' origin='+origin,xbmc.LOGINFO)
    except Exception:pass


def selected(router):
    from portals import get_by_id
    from portal_snapshot import PortalReadError
    pid=router._params.get('pid','');play=router._params.get('action')=='media_play'
    def valid():
        if not play:return False
        from media_intent import allowed
        p=router._params
        return allowed(str(p.get('intent','')),pid,p.get('kind','vod'),str(p.get('sid','')))
    origin=router._params.get('origin44','catalog')
    for attempt in range(2):
        try:portal=get_by_id(pid)
        except PortalReadError as exc:
            reason=getattr(exc,'reason','UNKNOWN');trace('PORTAL_READ',reason,origin)
            if not attempt and reason in ('PROFILE_BUSY','PROFILE_RACE','READ_IO') and valid():
                trace('PORTAL_RETRY',reason,origin);time.sleep(.03);continue
            raise
        trace('PORTAL_READ','DISABLED' if portal and not portal.get('enabled',True) else 'OK' if portal else 'NOT_FOUND',origin)
        return portal if portal and portal.get('enabled',True) else None

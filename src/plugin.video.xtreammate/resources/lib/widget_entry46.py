"""Existing native widget URLs without importing the full legacy app router."""
ROUTES=frozenset(('widget_live_start_group','widget_recent_vod','widget_recent_series'))


def dispatch(router):
    action=router._params.get('action','')
    if action not in ROUTES or router._handle<0:return False
    from boot_diagnostics import mark
    mark('ROUTE',action=action)
    from portals import get_by_id
    pid=router._params.get('pid','')
    if pid:portal=get_by_id(pid)
    else:
        from app_routes import portal_for
        portal=portal_for(router)  # Preserve legacy widget URLs without pid.
    if not portal or not portal.get('enabled',True):
        from boot_diagnostics import finish_directory
        finish_directory(router,False,cacheToDisc=False);return True
    if action=='widget_live_start_group':  # Same saved URL, complete logo row with or without the legacy flag.
        from widget_home50 import render
        render(router,portal);return True
    from app_routes import widget
    widget(router,portal,action);return True

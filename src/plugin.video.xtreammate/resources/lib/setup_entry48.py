"""Wizard dispatch before the full application import or Home anchoring.

A directory bookmark is completed before the service continues via RunPlugin;
it does not recursively load root or start widget/catalogue imports first.
"""


def dispatch(router):
    if router._params.get('action')!='setup_wizard':return False
    from boot_diagnostics import finish_directory
    from setup_navigation import run,_queue,active
    from setup_trace import mark
    mark('ENTRY48')
    if router._handle>=0:
        finish_directory(router,succeeded=False,cacheToDisc=False)
        if not active():_queue('launch',url=router.url(action='setup_wizard'),direct48=True)
        mark('QUEUED48')
    else:run(router)
    return True

"""Safe, opt-in-on-first-open XCMate setup entry for an empty Kodi profile.

Only a truly empty portal store may trigger the automatic wizard. Having any
stored account, including intentionally disabled accounts, MUST suppress it.
Running it never migrates legacy settings or writes a new profile on Cancel.
"""


def should_autostart(all_portals):
    """A readable empty profile triggers setup; errors never look like empty."""
    return isinstance(all_portals, list) and len(all_portals) == 0


def launch_once(router):
    """Run existing verified setup transaction after root directory is closed.

    Kodi home-window property guards overlapping root invocations (widgets,
    container-refresh races). The property is always released on Cancel/error.
    """
    import xbmcgui
    marker = xbmcgui.Window(10000)
    key = 'XCMate.FirstRunWizardRunning'
    if marker.getProperty(key) == 'true':
        return False
    marker.setProperty(key, 'true')
    try:
        from portals import load_all
        # Re-read after directory generation: another root may have created
        # a portal. Do not prompt merely because all accounts are disabled.
        if not should_autostart(load_all()):
            return False
        from setup_wizard import setup
        portal = setup()
        if portal:
            import xbmc
            xbmc.executebuiltin(
                'Container.Update({},replace)'.format(
                    router.url(action='portal_home', pid=portal['id'])))
        # On Cancel the empty-profile root remains visible with a manual
        # setup entry. Do NOT Container.Refresh(): that would reopen wizard.
        return True
    finally:
        marker.clearProperty(key)

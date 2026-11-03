"""One explicit migration, one atomic publication, one valid Kodi directory."""


def import_settings():
    # Caller holds profile_transaction.serialized; publish all slots together.
    import portals
    from utils import setting,setting_bool,setting_int
    from setup_diagnostics71 import emit
    existing=portals.load_all()
    if existing:
        emit('LEGACY_SKIPPED',total=len(existing));return False
    pending=[]
    for number in range(1,4):
        prefix='playlist'+str(number)+'_'
        if not setting_bool(prefix+'enabled',number==1):continue
        kind=setting_int(prefix+'type',0)
        data=dict(name=setting(prefix+'name') or 'Playlist '+str(number),epg_url=setting(prefix+'epg_url'))
        if kind in (0,1):
            data.update(type='m3u',m3u_url=setting(prefix+'url'))
            valid=bool(data['m3u_url'])
        elif kind==2:
            data.update(type='xtream',xc_host=setting(prefix+'xc_host'),xc_user=setting(prefix+'xc_user'),xc_pass=setting(prefix+'xc_pass'))
            valid=bool(data['xc_host'] and data['xc_user'])
        elif kind==3:
            data.update(type='stb',stb_url=setting(prefix+'stb_url'),stb_mac=setting(prefix+'stb_mac'))
            valid=bool(data['stb_url'] and data['stb_mac'])
        else:continue
        if valid:pending.append(portals._record(data))
    if not pending:
        emit('LEGACY_SKIPPED',code='NO_INPUT');return False
    from setup_commit71 import backup
    backup('legacy')
    try:
        portals.save_all(pending)
    except BaseException:
        # Only this unpublished batch may be reverted, under the same lock.
        portals.save_all(existing)
        raise
    emit('LEGACY_DONE',total=len(pending))
    return True


def run(router):
    import xbmc,xbmcgui,portals
    from boot_diagnostics import phase
    try:
        with phase('PORTALS_MIGRATION'):changed=portals.import_from_settings()
    except (OSError,ValueError) as exc:
        from setup_diagnostics71 import emit
        emit('FAILED','legacy',error=exc)
        xbmcgui.Dialog().ok('XCMate','Vorhandene Playlists konnten nicht sicher übernommen werden. Einstellungen bleiben erhalten; lokalen Speicher prüfen.')
        changed=False
    if router._handle>=0:
        # Render in this invocation. Refreshing this action re-ran the import
        # and left Kodi with an empty/inconsistent directory handoff.
        router._root(_legacy71=True)
    elif changed:
        # RunPlugin is an action, not a directory: no endOfDirectory(-1).
        xbmcgui.Dialog().notification('XCMate','Vorhandene Playlists sicher übernommen.')
        from urllib.parse import urlsplit
        try:own=urlsplit(xbmc.getInfoLabel('Container.FolderPath')).netloc=='plugin.video.xtreammate'
        except (AttributeError,RuntimeError,ValueError):own=False
        if own:xbmc.executebuiltin('Container.Update('+router.url(action='root')+',replace)')

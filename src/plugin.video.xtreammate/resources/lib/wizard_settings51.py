"""Read only the explicit new-portal form; never borrow an active account."""
FIELDS = {
    3: ('xc_host', 'xc_user', 'xc_pass'),
    2: ('m3u_url',), 1: ('m3u_url',), 0: ('stb_url', 'stb_mac'),
}


def proposal():
    import xbmcaddon
    addon = xbmcaddon.Addon('plugin.video.xtreammate')
    def read(key):
        return addon.getSetting('new_portal_' + key) or ''
    try:
        choice = {0: 2, 1: 1, 2: 3, 3: 0}[int(read('type') or '0')]
    except (ValueError, KeyError):
        return None
    data = {key: read(key) for key in FIELDS[choice]}
    # The factory MAC is not evidence of a configured Stalker account.
    present = ('stb_url',) if choice == 0 else FIELDS[choice]
    if not any(data.get(key, '').strip() for key in present):
        return None
    data.update(name=read('name') or 'Meine TV-Liste', epg_url=read('epg_url'),
                epg_show=read('epg_show').lower() != 'false',
                enabled=read('enabled').lower() != 'false')
    return choice, data

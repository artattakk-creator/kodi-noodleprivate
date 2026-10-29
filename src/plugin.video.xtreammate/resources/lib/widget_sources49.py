"""Browsable Kodi widget sources; only BINGIE's picker saves skin bindings.

No skinshortcuts profile/XML writes, refresh rebinds or playback on selection.
The three folder URLs are the existing .47/.48 runtime/widget entry points.
"""
from localization import tr

SOURCES=((36300,'widget_live_start_group','home_live'),
         (36301,'widget_recent_vod','movies_home'),
         (36302,'widget_recent_series','series_home'))


def show(router,portal):
    if router._handle<0:
        # Compatibility with old non-folder settings/bookmarked RunPlugin URLs.
        # There is no directory request to complete on handle -1.
        import xbmc
        xbmc.executebuiltin('ActivateWindow(Videos,'+router.url(
            action='widget_setup',pid=portal['id'])+',return)')
        return
    import xbmcgui,xbmcplugin
    from boot_diagnostics import finish_directory
    from menu_icons45 import icon
    from widget_binding50 import source
    xbmcplugin.setContent(router._handle,'files')
    xbmcplugin.setPluginCategory(router._handle,tr(32443))
    for kind,(label,action,art) in zip(('live','vod','series'),SOURCES):
        item=xbmcgui.ListItem(tr(label))
        item.setProperty('IsPlayable','false')
        item.setInfo('video',{'title':tr(label),'plot':tr(36304)})
        item.setArt({'icon':icon(art),'thumb':icon(art)})
        xbmcplugin.addDirectoryItem(router._handle,
            source(kind,portal['id']),item,isFolder=True)
    finish_directory(router,succeeded=True,cacheToDisc=False)


def help():
    import xbmcgui
    xbmcgui.Dialog().ok(tr(36305),tr(36306))

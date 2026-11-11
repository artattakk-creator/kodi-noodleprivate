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
            action='widget_sources49',pid=portal['id'] if portal else None)+',return)')
        return
    import xbmcgui,xbmcplugin
    from boot_diagnostics import finish_directory
    from menu_icons45 import icon
    from widget_binding50 import source
    xbmcplugin.setContent(router._handle,'files')
    xbmcplugin.setPluginCategory(router._handle,tr(32443))
    if portal is None:
        # A fresh picker is discoverable without inventing a portal or saving
        # broken pid URLs. Setup is explicit; opening this folder never runs it.
        item=xbmcgui.ListItem(tr(32420));item.setInfo('video',{'title':tr(32420),'plot':tr(32466)})
        item.setProperty('IsPlayable','false');item.setArt({'icon':icon('settings'),'thumb':icon('settings')})
        xbmcplugin.addDirectoryItem(router._handle,router.url(action='setup_wizard'),item,isFolder=True)
        __import__('picker_entry90').note('PICKER_PORTAL_REQUIRED')
        finish_directory(router,succeeded=True,cacheToDisc=False);return
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

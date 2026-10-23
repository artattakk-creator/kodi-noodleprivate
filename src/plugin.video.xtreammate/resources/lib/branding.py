"""One immutable original icon, with a content-addressed Kodi cache key."""
import hashlib
import os

SHA256='81da1003a2753ec6afbdd50b2a320e738a2131ad9f0d76606da1babdd0d2f135'
FILENAME='icon-'+SHA256[:16]+'.png'


def icon():
    import xbmcaddon
    root=xbmcaddon.Addon().getAddonInfo('path')
    return os.path.join(root,FILENAME)


def inspect():
    """Read-only runtime report: basenames/codes, no URLs/account paths."""
    import xbmcaddon
    addon=xbmcaddon.Addon();root=addon.getAddonInfo('path');runtime=addon.getAddonInfo('icon') or ''
    result=dict(packaged='MISSING',runtime='OTHER_REFERENCE',reference=FILENAME)
    try:
        with open(icon(),'rb') as stream:data=stream.read(1024*1024)
        result['packaged']='ORIGINAL' if hashlib.sha256(data).hexdigest()==SHA256 else 'WRONG_BYTES'
    except OSError:pass
    if runtime.replace('\\','/').endswith('/'+FILENAME) or runtime==FILENAME:result['runtime']='CONTENT_ADDRESSED'
    elif runtime.replace('\\','/').endswith('/icon.png'):result['runtime']='LEGACY_REFERENCE'
    return result


def show_status():
    import xbmcgui
    from localization import tr
    report=inspect()
    xbmcgui.Dialog().textviewer(tr(33701),'XCMate · GS Media\n'+tr(33702)+'\n'+
        '\n'.join(k+': '+str(v) for k,v in report.items())+'\nSHA256: '+SHA256)

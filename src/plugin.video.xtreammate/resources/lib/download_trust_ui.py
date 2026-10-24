"""Explicit portal-bound target consent; all host details stay on the device."""
import xbmcgui
from localization import tr


def approve(row):
    from capture_ui import work
    from download_trust import pending,grant
    from download_redirect import addresses
    from download_sources import DownloadFailure
    value=work(lambda:pending(row['id'],row['media']['pid']))
    if not value:return
    text=tr(34601)+'\n'+value['source']+' → '+value['target']
    if not xbmcgui.Dialog().yesno('XCMate',text):return
    lan=False
    try:work(lambda:addresses(value['target']))
    except DownloadFailure as exc:
        if exc.code!='REDIRECT_PRIVATE_ADDRESS':raise
        if not xbmcgui.Dialog().yesno('XCMate',tr(34602)):return
        # Explicit LAN still excludes loopback, link-local, metadata/multicast,
        # mapped unsafe addresses and unsupported schemes. Never bypass checks.
        work(lambda:addresses(value['target'],lan=True));lan=True
    work(lambda:grant(value,lan))
    xbmcgui.Dialog().ok('XCMate',tr(34603))


def manage(pid):
    from capture_ui import work
    from download_trust import grants,revoke
    values=work(lambda:grants(pid))
    if not values:xbmcgui.Dialog().ok('XCMate',tr(34606));return
    index=xbmcgui.Dialog().select(tr(34604),[v['source']+' → '+v['target']+(' · LAN' if v['lan'] else '') for v in values])
    if not 0<=index<len(values):return
    if xbmcgui.Dialog().yesno('XCMate',tr(34605)):work(lambda:revoke(values[index]))

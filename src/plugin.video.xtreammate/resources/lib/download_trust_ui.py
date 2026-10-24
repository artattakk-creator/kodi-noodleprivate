"""Explicit portal-bound target consent; all host details stay on the device."""
import xbmcgui
from localization import tr


def approve(row):
    from capture_ui import work
    from download_trust import pending,grant_pending
    from download_redirect import addresses
    from download_sources import DownloadFailure
    value=work(lambda:pending(row['id'],row['media']['pid']))
    if not value:return False
    text=tr(35001)+'\n'+value['source']+' → '+value['target']
    # Default/cancel keeps the host blocked. Origin presence is not verification.
    choice=xbmcgui.Dialog().select(text,[tr(35002),tr(35003)])
    if choice!=1:return False
    if not xbmcgui.Dialog().yesno('XCMate',tr(34601)+'\n'+value['source']+' → '+value['target']):return False
    lan=False
    try:work(lambda:addresses(value['target']))
    except DownloadFailure as exc:
        if exc.code!='REDIRECT_PRIVATE_ADDRESS':raise
        if not xbmcgui.Dialog().yesno('XCMate',tr(34602)):return False
        work(lambda:addresses(value['target'],lan=True));lan=True
    if not work(lambda:grant_pending(value,lan)):
        xbmcgui.Dialog().ok('XCMate',tr(35006));return False
    # Granting does not start network IO. Retry is a second explicit job action.
    if xbmcgui.Dialog().yesno('XCMate',tr(35004)):
        from download_store import get,command
        def retry():
            current=get(row['id'])
            if not current or current['media']['pid']!=row['media']['pid'] or current['state']!='FAILED':return False
            if not current['code'].startswith(('REDIRECT_UNTRUSTED_TARGET','REDIRECT_PRIVATE_ADDRESS')):return False
            return command(row['id'],'retry',required_state='FAILED',required_code=current['code'])
        changed=work(retry)
        xbmcgui.Dialog().notification('XCMate',tr(34216 if changed else 35005))
    else:xbmcgui.Dialog().ok('XCMate',tr(34603))
    return True



def manage(pid):
    from capture_ui import work
    from download_trust import grants,revoke
    values=work(lambda:grants(pid))
    if not values:xbmcgui.Dialog().ok('XCMate',tr(34606));return
    index=xbmcgui.Dialog().select(tr(34604),[v['source']+' → '+v['target']+(' · LAN' if v['lan'] else '') for v in values])
    if not 0<=index<len(values):return
    if xbmcgui.Dialog().yesno('XCMate',tr(34605)):work(lambda:revoke(values[index]))

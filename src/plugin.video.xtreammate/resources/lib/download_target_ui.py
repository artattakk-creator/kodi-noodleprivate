"""Local/USB/SMB picker, explicit staging consent, persistent separate target."""
import xbmcaddon,xbmcgui
from localization import tr


def capabilities(value):
    free=tr(34704) if value['free'] is None else '{:.2f} GiB'.format(value['free']/1024**3)
    return '\n'.join((tr(34702)+': '+value['type'],tr(34703)+': '+value['backend'],
        'READ / WRITE: '+tr(34705),'PUBLISH: '+('ATOMIC NO-REPLACE' if value['atomic_publish'] else 'EXCLUSIVE COPY + SHA256'),
        'CAPACITY: '+free,'FILE LIMIT: {:.2f} GiB'.format(value['max_bytes']/1024**3),
        'RESUME: '+value['resume'],tr(34706)+': '+tr(34705 if value['offline'] else 34707),
        tr(34708)+': '+tr(34705 if value['staging'] else 34707)))


def choose(check_only=False):
    from capture_ui import work
    from download_targets import configured,normalize,assess,approved
    from transfer_diagnostics import describe
    try:
        old=configured()
        selected=old if check_only else xbmcgui.Dialog().browseSingle(0,tr(34700),'files',defaultt=old)
        if not selected:return
        if selected.startswith('smb://'):
            from download_smb import configure,Failure,credentials
            selected=work(lambda:configure(selected))
            if not selected:return
        selected=normalize(selected)
        try:value=work(lambda:assess(selected))
        except Exception as exc:
            if not selected.startswith('smb://') or getattr(exc,'code','') not in ('SMB_AUTH_REQUIRED','SMB_AUTH_FAILED'):raise
            if not xbmcgui.Dialog().yesno('XCMate',tr(34716)):return
            user=xbmcgui.Dialog().input(tr(34717))
            if not user:return
            password=xbmcgui.Dialog().input(tr(34718),option=xbmcgui.ALPHANUM_HIDE_INPUT)
            if password is None:return
            domain=''
            if '\\' in user:domain,user=user.split('\\',1)
            work(lambda:credentials(selected,(user,password,domain)))
            value=work(lambda:assess(selected))
        if value is None:return
        text=capabilities(value)
        if check_only:xbmcgui.Dialog().ok('XCMate',text);return
        if value['staging'] and not xbmcgui.Dialog().yesno('XCMate',tr(34709)+'\n\n'+text):return
        if not xbmcgui.Dialog().yesno('XCMate',tr(34712)+'\n\n'+text):return
        if value['staging']:work(lambda:approved(selected,save=True))
        xbmcaddon.Addon().setSetting('downloads_folder',selected)
        xbmcaddon.Addon().setSetting('downloads_folder_enabled','1')
        xbmcgui.Dialog().ok('XCMate',tr(34713))
    except Exception as exc:xbmcgui.Dialog().ok('XCMate',describe(exc,'download')+'\n'+tr(34714))

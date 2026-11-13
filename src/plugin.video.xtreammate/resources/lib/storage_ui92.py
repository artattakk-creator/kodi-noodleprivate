"""Storage entry point; all filesystem/SQLite work stays on the existing worker."""
import json
from localization import tr

def show(value):
    import xbmcgui
    xbmcgui.Dialog().textviewer(tr(38700),json.dumps(value,ensure_ascii=False,indent=2))

def image_choice():
    import xbmcgui
    from artwork_ui import job
    choice=xbmcgui.Dialog().select(tr(38703),[tr(38704),tr(38705),tr(38706)])
    if choice in (0,1,2):
        decision=('yes','no','later')[choice]
        return job(lambda cancel,progress:__import__('storage_policy92').choose(decision))

def pick_usb():
    import xbmcgui
    from artwork_ui import job
    from storage_sources import external_sources
    values=job(lambda cancel,progress:external_sources())
    if not values:return None
    index=xbmcgui.Dialog().select(tr(38707),[v['label'] for v in values])
    if 0<=index<len(values):return xbmcgui.Dialog().browseSingle(3,tr(38707),'files',defaultt=values[index]['path']) or None

def manage(setup=False):
    import xbmcgui
    from artwork_ui import job,_render
    import artwork_migration as migration
    from storage_transfer92 import prepare
    dialog=xbmcgui.Dialog()
    if setup:image_choice()
    labels=[tr(i) for i in (38701,38702,38703,38707,38708,38709,38710,38711,38712,38713,38714)]
    while True:
        choice=dialog.select(tr(38700),labels)
        if choice<0:return
        try:
            if choice==0:show(job(lambda cancel,progress:__import__('storage_inventory92').collect(cancel,progress)))
            elif choice==1:show(job(lambda cancel,progress:__import__('storage_maintenance92').run(cancel,progress,force=True)))
            elif choice==2:image_choice()
            elif choice==3:
                target=pick_usb()
                if not target:continue
                # No write/probe before separate, explicit confirmation.
                if dialog.yesno(tr(38700),tr(38715)):
                    show(job(lambda cancel,progress:prepare(target,confirmed=True)))
            elif choice==4:show(job(lambda cancel,progress:migration.copy(cancel,progress)))
            elif choice==5:
                valid=job(lambda cancel,progress:migration.verify(cancel,progress))
                if valid:
                    uri=job(lambda cancel,progress:migration.display_candidate())
                    probe=None
                    if not uri:
                        probe=job(lambda cancel,progress:migration.probe_image());uri=probe['uri'] if probe else ''
                    approved=_render(uri)
                    if probe:job(lambda cancel,progress:migration.remove_probe(probe))
                    job(lambda cancel,progress:migration.approve_render(approved))
                    if approved:dialog.ok(tr(38700),tr(38716))
            elif choice==6:show(job(lambda cancel,progress:migration.activate(cancel,progress)))
            elif choice==7:
                current=job(lambda cancel,progress:migration.status())
                if current and dialog.yesno(tr(38700),tr(38717)) and dialog.yesno(tr(38700),tr(38718)):
                    show(job(lambda cancel,progress:migration.cleanup_report(current.get('transfer',''),cancel,progress)))
            elif choice==8:__import__('artwork_ui').manage()
            elif choice==9:show(job(lambda cancel,progress:dict(migration=migration.status(),policy=__import__('storage_policy92').read(),maintenance=__import__('storage_maintenance92').read())))
            elif choice==10:
                # Actual Kodi 21 global cache settings; no fabricated per-stream knob.
                __import__('xbmc').executebuiltin('ActivateWindow(systemsettings)')
        except (OSError,ValueError,TimeoutError,__import__('sqlite3').Error) as error:
            code=getattr(error,'code','STORAGE_OPERATION_BLOCKED')
            # Exception text can contain a path / credentials. Only fixed codes.
            if not isinstance(code,str) or not __import__('re').fullmatch('[A-Z0-9_:-]{1,100}',code):code='STORAGE_OPERATION_BLOCKED'
            dialog.ok(tr(38700),tr(38719)+'\n'+code)


def setup(nonce):
    """Fresh installer bridge, owned by this add-on's normal route/GUI owner."""
    import re,xbmcgui
    if not re.fullmatch('[a-f0-9]{32}',nonce or ''):raise ValueError('SETUP_NONCE_INVALID')
    from artwork_ui import job
    from storage_policy92 import read
    dialog=xbmcgui.Dialog();state='DEFERRED'
    try:
        policy=job(lambda cancel,progress:read())
        # A legacy profile must not have its existing source opt-ins reset.
        if policy and policy['image_epg']=='legacy':image_choice()
        target=dialog.select(tr(38724),[tr(38725),tr(38707),tr(38726),tr(38706)])
        if target==0:
            # Internal is the existing default. Never undo an active migration.
            config=job(lambda cancel,progress:__import__('artwork_config').read())
            state='PREPARED' if config and config.get('mode') in ('internal','dynamic') else 'DEFERRED'
        elif target==1:
            selected=pick_usb()
            if selected and dialog.yesno(tr(38700),tr(38715)):
                result=job(lambda cancel,progress:__import__('storage_transfer92').prepare(selected,confirmed=True))
                if result:state='PREPARED';dialog.ok(tr(38700),tr(38727))
        elif target==2:
            dialog.ok(tr(38700),tr(38728))
            __import__('artwork_ui').manage()
        # Existing data worker owns automatic bounded maintenance, no new thread.
    except (OSError,ValueError,TimeoutError,__import__('sqlite3').Error):
        dialog.ok(tr(38700),tr(38719))
    finally:
        xbmcgui.Window(10000).setProperty('XCMate.Storage92.SetupAck',json.dumps(dict(nonce=nonce,state=state)))

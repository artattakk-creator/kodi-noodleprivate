"""Explicit artwork policy changes; copies never run in the GUI thread."""
from localization import tr


def show_status():
    import xbmcgui
    from art_store import status
    from artwork_db import diagnostic
    try:
        value=status();storage=value['storage'];health=diagnostic()
        lines=[tr(32920),tr(32935,storage['profile']),tr(32936,storage['root']),
               tr(32937,value['bytes']//1048576,value['budget']//1048576),
               tr(32938,storage.get('free',0)//1048576,storage.get('total',0)//1048576),
               tr(32939,storage['reserve_mb']),tr(32940,storage['code']),tr(32941)]
        for code,count in sorted(value['counts'].items()):lines.append(code+': '+str(count))
        if value['pause']:lines.append(tr(32942,value['pause'].get('code','')))
        lines.append(tr(32943))
        for entry in value['inventory']:
            lines.append(tr(32944,entry['kind'],entry['items'],entry['poster_missing'],entry['fanart_missing'],entry['complete']))
        lines.extend([tr(32945,health.get('code','NOT_CHECKED')),tr(32946),
                      tr(32947,str(health.get('checked_at',health.get('updated','—')))),
                      tr(32948,str(health.get('sqlite_code',0))),
                      tr(32949,str(health.get('backup','—'))),
                      tr(32950,'yes' if health.get('code') in ('CORRUPT','RECOVERY_REQUIRED','SCHEMA_ERROR','INDEX_DEFECT','REPAIR_REQUIRED') else '—'),
                      tr(32951),tr(32952,str(storage.get('migration',{}).get('code','—')))])
        xbmcgui.Dialog().textviewer(tr(32661),'\n'.join(lines))
    except Exception:
        xbmcgui.Dialog().notification('XCMate',tr(32953))


def configure():
    import xbmcgui,xbmcvfs
    from art_storage import policy,configure as save,start_migration,Paused,is_vfs
    dialog=xbmcgui.Dialog()
    action=dialog.select(tr(32920),[tr(32921),tr(32922),tr(32661)])
    if action==2:show_status();return
    if action==0:
        profiles=('small','standard','large','auto','expert')
        selected=dialog.select(tr(32921),[tr(n) for n in range(32923,32928)])
        if not 0<=selected<len(profiles):return
        profile=profiles[selected];amount=None
        try:
            if profile=='expert':
                text=dialog.input(tr(32928),type=xbmcgui.INPUT_NUMERIC)
                if not text:return
                amount=int(text)
            text=dialog.input(tr(32929),defaultt=str(policy()['reserve_mb']),type=xbmcgui.INPUT_NUMERIC)
            if not text:return
            reserve=int(text)
            from art_storage import _new_policy
            candidate=_new_policy(profile,amount,reserve)
            if not dialog.yesno(tr(32920),tr(32930,tr(32923+selected),candidate['budget_mb'],reserve)):return
            save(profile,amount,reserve)
            dialog.notification('XCMate',tr(32931))
        except (OSError,ValueError):dialog.notification('XCMate',tr(32932))
    elif action==1:
        target=dialog.browseSingle(0,tr(32922),'files',defaultt='')
        if not target:return
        # VFS target remains a VFS URI; never pass smb:// to os/open/statvfs.
        if target.startswith('special://'):target=xbmcvfs.translatePath(target)
        if is_vfs(target):
            dialog.ok(tr(32920),tr(32933));return
        if not dialog.yesno(tr(32922),tr(32934)):return
        if start_migration(target):dialog.notification('XCMate',tr(32954))

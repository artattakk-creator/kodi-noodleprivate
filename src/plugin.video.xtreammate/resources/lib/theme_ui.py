"""Native Kodi theme management; only explicit jobs can use the network."""
from concurrent.futures import ThreadPoolExecutor
import os
import tempfile
import threading

from localization import tr
from theme_package import ThemeError, MAX_ZIP, fail


def job(function):
    """Native cancellable progress dialog; GUI never waits on a network call."""
    import xbmc
    import xbmcgui
    cancelled = threading.Event()
    pool = ThreadPoolExecutor(max_workers=1)
    progress = xbmcgui.DialogProgress()
    progress.create(tr(32800), tr(32810))
    monitor = xbmc.Monitor()
    future = pool.submit(lambda: function(cancelled.is_set))
    try:
        while not future.done():
            if progress.iscanceled() or monitor.waitForAbort(.1):
                cancelled.set(); fail('CANCELLED')
        if progress.iscanceled(): cancelled.set(); fail('CANCELLED')
        return future.result()
    finally:
        progress.close()
        pool.shutdown(wait=False, cancel_futures=True)


def local_import(uri, cancel=lambda: False):
    """Bounded VFS copy supports local/USB/SMB without trusting VFS zip paths."""
    import xbmcvfs
    from theme_store import root, install, check_space
    fd, temp = tempfile.mkstemp(prefix='.import-', dir=root())
    try:
        with os.fdopen(fd, 'wb') as output:
            source = xbmcvfs.File(uri)
            try:
                size = 0
                while True:
                    if cancel(): fail('CANCELLED')
                    chunk = source.readBytes(65536)
                    if not chunk: break
                    size += len(chunk)
                    if size > MAX_ZIP: fail('LIMIT')
                    check_space(len(chunk))
                    output.write(chunk)
            finally: source.close()
        return install(temp, cancel=cancel)
    finally:
        if os.path.exists(temp): os.unlink(temp)


def _message(code):
    import xbmcgui
    ids = {'SPACE':32815, 'BUSY':32816, 'INCOMPATIBLE':32817, 'DOWNLOAD':32818,
           'CHECKSUM':32819, 'INCOMPLETE':32820, 'SAME_VERSION':32821, 'DOWNGRADE':32822,
           'CATALOG_NOT_PUBLISHED':32824}
    xbmcgui.Dialog().ok(tr(32800), tr(ids.get(code, 32814)))


def preview():
    """Bundled original preview; works before download and completely offline."""
    import xbmcaddon,xbmcgui
    from branding import icon
    media=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources/media')
    class Preview(xbmcgui.WindowDialog):
        def __init__(self):
            super().__init__()
            self.addControls([xbmcgui.ControlImage(0,0,1280,720,os.path.join(media,'space-premium-preview.jpg')),
                xbmcgui.ControlImage(1120,12,120,120,icon(),aspectRatio=2),
                xbmcgui.ControlLabel(44,640,1160,64,tr(33802)+' – '+tr(33812),'font13','0xFFFFFFFF')])
        def onAction(self,action):
            if action.getId() in (7,9,10,92):self.close()
    window=Preview()
    try:window.doModal()
    finally:window.close()


def manage():
    import xbmcgui
    from theme_store import installed,select,remove,core_version
    from theme_catalog import catalogue,download
    from theme_render import snapshot,choice_items
    dialog=xbmcgui.Dialog()
    def activate(revision):
        deferred=select(revision);dialog.ok(tr(32800),tr(32809) if deferred else tr(33811))
    def online(ident=None):
        rows=job(lambda cancel:catalogue(core_version(),cancel))
        if ident:rows=[r for r in rows if r['id']==ident]
        if not rows:dialog.ok(tr(32800),tr(32812));return
        selected=0 if ident and len(rows)==1 else dialog.select(tr(32802),[r['name']+' '+r['version'] for r in rows])
        if selected<0:return
        row=rows[selected]
        if not dialog.yesno(tr(33807),row['name']+' '+row['version']):return
        job(lambda cancel:download(row,cancel));dialog.ok(tr(32800),tr(32811))
    while True:
        try:
            rows=job(lambda cancel:installed());theme=snapshot()
            premium=[r for r in rows if r['spec']['id']=='space-premium']
            active=bool(theme and theme['spec']['id']=='space-premium')
            status=33805 if active else 33804 if premium else 33803
            labels=[tr(33801)+(' · '+tr(33805) if not theme else ''),tr(33802)+' · '+tr(status),tr(32823),tr(32803),tr(33810)]
            choice=dialog.select(tr(33813),choice_items(labels,['icon.start','icon.shared.info','icon.shared.search','icon.shared.forward','icon.shared.clear'],theme),useDetails=bool(theme))
            if choice<0:return
            if choice==0:activate('')
            elif choice==1:
                action=dialog.select(tr(33802),choice_items([tr(i) for i in (33806,33807,33808,33809,33810)],['icon.shared.info','icon.shared.forward','icon.shared.check','icon.shared.close','icon.shared.clear'],theme),useDetails=bool(theme))
                if action==0:preview()
                elif action==1:online('space-premium')
                elif action==2:
                    if premium:
                        from theme_package import version
                        activate(max(premium,key=lambda r:version(r['spec']['version']))['revision'])
                    else:dialog.ok(tr(32800),tr(33803))
                elif action==3:activate('')
                elif action==4 and premium and dialog.yesno(tr(33810),tr(33802)):remove('space-premium')
            elif choice==2:online()
            elif choice==3:
                uri=dialog.browseSingle(1,tr(32803),'files',mask='.zip',treatAsFolder=False)
                if uri:job(lambda cancel:local_import(uri,cancel));dialog.ok(tr(32800),tr(32811))
            elif choice==4:
                if not rows:dialog.ok(tr(32800),tr(32813));continue
                selected=dialog.select(tr(33810),[r['spec']['name']+' '+r['spec']['version'] for r in rows])
                if selected>=0 and dialog.yesno(tr(33810),rows[selected]['spec']['name']):remove(rows[selected]['spec']['id'])
        except ThemeError as error:
            if str(error)!='CANCELLED':_message(str(error))
        except OSError as error:_message('SPACE' if error.errno==28 else 'DOWNLOAD')
        except (ValueError,KeyError,RuntimeError,TimeoutError):_message('ARCHIVE')

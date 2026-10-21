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


def manage():
    import xbmcgui
    from theme_store import installed, select, remove, core_version
    from theme_catalog import catalogue, download
    from theme_render import choice_items, snapshot
    dialog = xbmcgui.Dialog()
    while True:
        theme=snapshot()
        choice = dialog.select(tr(32800), choice_items([tr(i) for i in (32801,32823,32803,32804,32805)],
            ['icon.shared.check','icon.shared.search','icon.shared.forward','icon.shared.clear','icon.shared.close'],theme),useDetails=bool(theme))
        if choice < 0: return
        try:
            if choice == 2:
                uri = dialog.browseSingle(1, tr(32803), 'files', mask='.zip', treatAsFolder=False)
                if not uri: continue
                job(lambda cancel: local_import(uri, cancel))
                dialog.ok(tr(32800), tr(32811))
            elif choice == 1:
                rows = job(lambda cancel: catalogue(core_version(), cancel))
                if not rows: dialog.ok(tr(32800), tr(32812)); continue
                selected = dialog.select(tr(32802), [r['name']+' '+r['version'] for r in rows])
                if selected < 0: continue
                row = rows[selected]
                if not dialog.yesno(tr(32802), row['name']+' '+row['version']): continue
                job(lambda cancel: download(row, cancel))
                dialog.ok(tr(32800), tr(32811))
            elif choice == 3:
                deferred = select('')
                dialog.ok(tr(32800), tr(32809 if deferred else 32808))
            elif choice in (0,4):
                rows = job(lambda cancel: installed())
                if not rows: dialog.ok(tr(32800), tr(32813)); continue
                selected = dialog.select(tr(32801), [r['spec']['name']+' '+r['spec']['version'] for r in rows])
                if selected < 0: continue
                row = rows[selected]
                if choice == 4:
                    if dialog.yesno(tr(32805), tr(32807, row['spec']['name'])): remove(row['spec']['id'])
                else:
                    deferred = select(row['revision'])
                    dialog.ok(tr(32800), tr(32809 if deferred else 32808))
        except ThemeError as error:
            if str(error) != 'CANCELLED': _message(str(error))
        except OSError as error:
            _message('SPACE' if error.errno == 28 else 'DOWNLOAD')
        except (ValueError, KeyError, RuntimeError, TimeoutError): _message('ARCHIVE')

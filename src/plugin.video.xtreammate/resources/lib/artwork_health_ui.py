"""Explicit artwork diagnostics/recovery; UI stays on the invoking thread."""
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import xbmc
import xbmcgui
from localization import tr


def _work(job):
    cancelled=threading.Event();pool=ThreadPoolExecutor(max_workers=1)
    dialog=xbmcgui.DialogProgress();monitor=xbmc.Monitor()
    try:
        dialog.create('XCMate',tr(32903))
        future=pool.submit(job,cancelled.is_set)
        while not future.done():
            if dialog.iscanceled():cancelled.set()
            if monitor.waitForAbort(.05):
                cancelled.set();time.sleep(.05)
        return future.result()
    finally:
        cancelled.set();dialog.close();pool.shutdown(wait=False,cancel_futures=True)


def manage():
    from artwork_db import maintain,rebuild,diagnostic
    try:result=_work(lambda cancel:maintain(force=True,cancel=cancel))
    except Exception:result=dict(code='CHECK_FAILED')
    # Fixed diagnostic fields only. No path, private URL or exception text.
    text='\n'.join(key+': '+str(result[key]) for key in ('code','phase','sqlite_code','backup') if key in result)
    xbmcgui.Dialog().textviewer(tr(32900),text)
    if result.get('code') in ('RECOVERY_REQUIRED','SCHEMA_ERROR'):
        if xbmcgui.Dialog().yesno('XCMate',tr(32902)):
            try:result=_work(lambda cancel:rebuild(confirmed=True,cancel=cancel))
            except Exception:result=dict(code='RECOVERY_FAILED')
            text='\n'.join(key+': '+str(result[key]) for key in ('code','phase','backup') if key in result)
            if result.get('background_paused'):text+='\n\n'+tr(32904)
            xbmcgui.Dialog().textviewer(tr(32900),text)

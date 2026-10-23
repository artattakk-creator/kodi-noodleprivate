"""Explicit manual Start/Stop; no timers, no player stop and no global keymaps."""
import os
import xbmc
import xbmcgui
import xbmcvfs
from localization import tr


def work(fn):
    from theme_ui import job
    return job(lambda cancel:None if cancel() else fn())


def _start(portal):
    from library_index import Reader
    from capture_store import add
    from utils import setting,addon_data_dir
    dialog=xbmcgui.Dialog()
    query=dialog.input(tr(34000))
    if not query or not query.strip():return
    result=work(lambda:Reader(portal['id'],timeout=.15,query_seconds=1).page('live',str(query)[:200],limit=100))
    if result is None:return
    channels,total=result
    if not channels:dialog.ok('XCMate',tr(33907));return
    choice=dialog.select(tr(34001),[c['name'] for c in channels])
    if not 0<=choice<len(channels):return
    duration=dialog.select(tr(34002),[tr(34003,n) for n in (2,5,30,60,120)])
    if duration not in range(5):return
    # A second provider connection is always explicit, even with no player.
    if not dialog.yesno('XCMate',tr(34004)):return
    target=xbmcvfs.translatePath(setting('recordings_folder',os.path.join(addon_data_dir(),'recordings')))
    if not os.path.isabs(target) or '://' in target:
        dialog.ok('XCMate',tr(34005));return
    ident=work(lambda:add(portal,channels[choice],target,(2,5,30,60,120)[duration]*60))
    if ident:dialog.notification('XCMate',tr(34006))


def _manage():
    from capture_store import rows,finish
    values=work(rows)
    if not values:xbmcgui.Dialog().ok('XCMate',tr(34007));return
    choice=xbmcgui.Dialog().select(tr(34008),[r['label']+' · '+r['status']+' · '+str(r['bytes']//1048576)+' MiB'+(' · '+r['code'] if r['code'] else '') for r in values])
    if not 0<=choice<len(values):return
    item=values[choice]
    if item['status'] in ('pending','starting','recording'):
        if xbmcgui.Dialog().yesno('XCMate',tr(34009)):work(lambda:finish(item['id']))
    elif item['status']=='complete' and item['file']:
        from pathlib import Path
        # Only an owned finalized basename, never .part or a foreign path.
        name=item['file']
        if name!=item['id']+'.ts':return
        path=Path(item['target'])/name
        if path.is_file() and not path.is_symlink() and xbmcgui.Dialog().yesno('XCMate',tr(34010)):
            xbmc.Player().play(str(path))


def report():
    return tr(34011)+'\n'+tr(34005)+'\n'+tr(34004)


def start(portal):
    try:_start(portal)
    except Exception:xbmcgui.Dialog().ok('XCMate',tr(34012))


def manage():
    try:_manage()
    except Exception:xbmcgui.Dialog().ok('XCMate',tr(34012))

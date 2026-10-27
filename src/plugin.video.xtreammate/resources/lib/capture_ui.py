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
    choice=__import__('menu_icons45').select(dialog,tr(34001),[c['name'] for c in channels],default='record')
    if not 0<=choice<len(channels):return
    duration=__import__('menu_icons45').select(dialog,tr(34002),[tr(34003,n) for n in (2,5,30,60,120)],default='record')
    if duration not in range(5):return
    # A second provider connection is always explicit, even with no player.
    if not dialog.yesno('XCMate',tr(34004)):return
    target=select_target()
    if target is None:return
    ident=work(lambda:add(portal,channels[choice],target,(2,5,30,60,120)[duration]*60))
    if ident:dialog.notification('XCMate',tr(34006))


def select_target(component='capture'):
    from capture_target import configured,probe,compatible_default,TargetFailure
    from transfer_diagnostics import describe,mark
    target=configured()
    try:
        if work(lambda:probe(target,create=True)) is None:return None
        mark('DOWNLOAD' if component=='download' else 'CAPTURE','TARGET_READY')
        return target
    except TargetFailure as exc:
        xbmcgui.Dialog().ok('XCMate',describe(exc,component))
        alternative=work(compatible_default)
        if not alternative:
            xbmcgui.Dialog().ok('XCMate',tr(34411));return None
        if not xbmcgui.Dialog().yesno('XCMate',tr(34101)):return None
        import xbmcaddon
        xbmcaddon.Addon().setSetting('recordings_folder',alternative)
        return alternative


def _manage():
    from capture_store import rows,finish
    from transfer_diagnostics import describe
    values=work(rows)
    if not values:xbmcgui.Dialog().ok('XCMate',tr(34007));return
    status_ids={'pending':34420,'starting':34421,'recording':34422,'complete':34423,'failed':34424,'partial':34425}
    choice=__import__('menu_icons45').select(xbmcgui.Dialog(),tr(34008),[r['label']+' · '+tr(status_ids.get(r['status'],34424))+' · '+format(r['bytes']/1048576,'.2f')+' MiB ('+str(r['bytes'])+' Bytes)'+(' · '+r['code'] if r['code'] else '') for r in values],default='record')
    if not 0<=choice<len(values):return
    item=values[choice]
    if item['status'] in ('pending','starting','recording'):
        if xbmcgui.Dialog().yesno('XCMate',tr(34009)):work(lambda:finish(item['id']))
    elif item['status'] in ('failed','partial'):
        xbmcgui.Dialog().ok('XCMate',describe(item['code']))
    elif item['status']=='complete' and item['file']:
        from pathlib import Path
        # Only an owned finalized basename, never .part or a foreign path.
        name=item['file']
        if name!=item['id']+'.ts':return
        path=Path(item['target'])/name
        if path.is_file() and not path.is_symlink() and xbmcgui.Dialog().yesno('XCMate',tr(34010)):
            xbmc.Player().play(str(path))


def report():
    from capture_target import configured,probe
    from transfer_diagnostics import describe
    try:
        result=work(lambda:probe(configured(),create=True))
        state=tr(34410)+' ('+result['publish']+')' if result else tr(34406)
    except Exception as exc:state=describe(exc)
    return tr(34011)+'\n'+state+'\n'+tr(34412)+'\n'+tr(34004)


def start(portal):
    from experimental45 import run
    return run(lambda:_start45(portal))


def _start45(portal):
    try:_start(portal)
    except Exception as exc:
        from transfer_diagnostics import describe
        xbmcgui.Dialog().ok('XCMate',describe(exc))


def manage():
    from experimental45 import run
    return run(lambda:_manage45())


def _manage45():
    try:_manage()
    except Exception as exc:
        from transfer_diagnostics import describe
        xbmcgui.Dialog().ok('XCMate',describe(exc))

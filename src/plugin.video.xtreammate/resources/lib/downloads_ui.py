"""Explicit movie/episode downloads and ID-only job actions."""
import xbmc
import xbmcgui
from localization import tr


def request(window):
    try:
        kind='vod' if window.kind=='vod' else 'episode';sid=str(window.selected['sid']);series=''
        if kind=='episode':
            if window.selected.get('series_flat'):kind='series_item'
            else:
                episodes=list(window.episodes)
                if not episodes:xbmcgui.Dialog().ok('XCMate',tr(34205));return
                choice=xbmcgui.Dialog().select(tr(34201),['S{:02d}E{:02d} · {}'.format(int(e['season']),int(e['episode']),e['name']) for e in episodes])
                if not 0<=choice<len(episodes):return
                series=sid;sid=str(episodes[choice]['sid'])
        if not xbmcgui.Dialog().yesno('XCMate',tr(34206)):return
        portal=dict(window.portal)
        def enqueue():
            from downloads import enqueue
            from transfer_diagnostics import encode
            try:return dict(id=enqueue(portal,kind,sid,series))
            except Exception as exc:return dict(error=encode(exc))
        def ready(result):
            if result.get('error'):
                from transfer_diagnostics import describe
                xbmcgui.Dialog().ok('XCMate',describe(result['error'],'download'))
            else:xbmcgui.Dialog().notification('XCMate',tr(34207))
        window._request(enqueue,ready)
    except Exception as exc:
        from transfer_diagnostics import describe
        xbmcgui.Dialog().ok('XCMate',describe(exc,'download'))


def manage():
    from capture_ui import work
    try:
        from download_store import snapshot,command
        from downloads import playable
        rows=work(snapshot)
        if not rows:xbmcgui.Dialog().ok('XCMate',tr(34209));return
        labels=[tr(34210)+' · '+r['media']['title']+' · '+tr(34711 if r['state']=='TRANSFERRING' else 34220+('QUEUED','RUNNING','PAUSED','COMPLETE','FAILED','CANCELLED','PUBLISHING','TRANSFERRING').index(r['state']))+(' '+str(r.get('copy_bytes',0)//1048576)+' MiB' if r['state']=='TRANSFERRING' else '')+' · '+str(r['bytes']//1048576)+' / '+str(r['total']//1048576)+' MiB'+(' · '+r['code'] if r['code'] else '') for r in rows]
        selected=xbmcgui.Dialog().select(tr(34202),labels)
        if not 0<=selected<len(rows):return
        row=rows[selected];state=row['state']
        if state=='FAILED':
            from transfer_diagnostics import describe
            xbmcgui.Dialog().ok('XCMate',describe(row['code'],'download'))
        actions=['play'] if state=='COMPLETE' else ['pause','cancel'] if state in ('QUEUED','RUNNING','TRANSFERRING') else ['resume','cancel'] if state=='PAUSED' else ['retry'] if state in ('FAILED','CANCELLED') else []
        from download_trust import pending
        if work(lambda:pending(row['id'],row['media']['pid'])):actions.append('trust')
        actions.append('trusts')
        if not actions:return
        words={'play':34211,'pause':34212,'cancel':34213,'resume':34214,'retry':34215,'trust':34600,'trusts':34604}
        choice=xbmcgui.Dialog().select(tr(34202),[tr(words[a]) for a in actions])
        if not 0<=choice<len(actions):return
        action=actions[choice]
        if action in ('trust','trusts'):
            from download_trust_ui import approve,manage
            if action=='trust':approve(row)
            else:manage(row['media']['pid'])
        elif action=='play':
            path=work(lambda:playable(row))
            if path:xbmc.Player().play(path)
        else:
            changed=work(lambda:command(row['id'],action))
            xbmcgui.Dialog().notification('XCMate',tr(34216 if changed else 34217))
    except Exception as exc:
        from transfer_diagnostics import describe
        xbmcgui.Dialog().ok('XCMate',describe(exc,'download'))

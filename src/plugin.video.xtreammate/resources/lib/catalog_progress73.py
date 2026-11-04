"""RAM-only GUI observer of existing work; no focus, provider IO or new jobs.

Kodi's native extended progress dialog controls placement in the active skin.
Hidden during playback to avoid covering player controls. One stable dialog.
"""
import time
_lock=__import__('threading').Lock()
_snapshot=None;_dialog=None;_last=None;_next=0


def prepare():
    global _snapshot,_next
    if time.monotonic()<_next:return
    _next=time.monotonic()+1
    from catalog_jobs73 import jobs
    rows=jobs()
    row=next((r for r in reversed(rows) if r['state'] in ('RUNNING','WAITING','INTERRUPTED') and r.get('resume')),None)
    if row is None and rows:row=rows[-1]
    if row is None:
        # Existing .72/delta background imports are observed, not replaced.
        from catalog_delta import _read
        jobs52=list(_read()['jobs'].values())
        candidates=[r for r in jobs52 if r['code'] in ('PENDING','RUNNING','FAILED')]
        if candidates:
            r=max(candidates,key=lambda r:r.get('updated',0))
            row=dict(id='delta-'+r['pid']+'-'+r['kind']+'-'+r['cid'],
                state={'PENDING':'WAITING','RUNNING':'WAITING','FAILED':'FAILED'}[r['code']],
                kind=r['kind'],group=r['cid'],processed=r.get('received',0),code='',updated=r.get('updated',0))
    with _lock:_snapshot=dict(row) if row else None


def poll():
    global _dialog,_last
    import xbmc,xbmcgui
    from localization import tr
    with _lock:row=dict(_snapshot) if _snapshot else None
    if xbmc.getCondVisibility('Player.HasMedia'):
        if _dialog is not None:_dialog.close();_dialog=None
        return
    if not row:return
    identity=(row['id'],row['state'],row.get('updated'))
    if identity==_last and _dialog is not None:return
    terminal=row['state'] in ('DONE','FAILED','INTERRUPTED') and not row.get('resume')
    if terminal:
        if _dialog is not None:_dialog.close();_dialog=None
        if _last and _last[0]==row['id'] and _last[1]!=row['state']:
            from catalog_ui73 import report
            xbmcgui.Dialog().notification('XCMate',report(row).replace('\n',' · '))
        _last=identity;return
    state=tr(38004 if row['state']=='RUNNING' else 38003)
    kind=tr({'live':32401,'vod':32403,'series':32404}.get(row.get('kind'),38000))
    group=str(row.get('group',''))
    detail=tr(38020,group,row.get('group_number',0),row['group_total']) if row.get('group_total') else group
    message=kind+(' → '+detail if detail else '')+' · '+tr(38021,row.get('processed',0)+row.get('group_read',0))+' · '+state
    if row.get('code'):message+=' · '+row['code']
    if _dialog is None:_dialog=xbmcgui.DialogProgressBG();_dialog.create(tr(38002),message)
    # Zero is Kodi's indeterminate state; never present a guessed percentage.
    _dialog.update(0,tr(38002),message);_last=identity


def legacy(pid,kind,cid,name,code,counts):
    """Called by a live legacy worker only, with real group and batch counts."""
    global _snapshot
    state={'INDEXING':'RUNNING','READY':'DONE','CACHED':'DONE','FAILED':'FAILED','CANCELLED':'INTERRUPTED'}.get(code,'FAILED')
    row=dict(id='delta-'+str(pid)+'-'+kind+'-'+str(cid),state=state,kind=kind,group=name,
        processed=counts.get('received',0),group_stored=counts.get('stored',0),updated=time.time(),code=code)
    with _lock:_snapshot=row

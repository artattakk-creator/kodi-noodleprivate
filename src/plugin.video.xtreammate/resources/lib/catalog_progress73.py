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
    from utils import setting_bool
    from localization import tr
    with _lock:row=dict(_snapshot) if _snapshot else None
    window=xbmcgui.Window(10000)
    # Retire an existing dialog without replacing it with another overlay.
    if _dialog is not None:_dialog.close();_dialog=None
    if not row or xbmc.getCondVisibility('Player.HasMedia'):
        window.clearProperty('XCMate.Catalog81.Text');return
    identity=(row['id'],row['state'],row.get('updated'))
    terminal=row['state'] in ('DONE','FAILED','INTERRUPTED') and not row.get('resume')
    if terminal:
        window.clearProperty('XCMate.Catalog81.Text')
        if setting_bool('catalog_summary81',False) and not row['id'].startswith('delta-') and _last and _last[0]==row['id'] and _last[1]!=row['state']:
            from catalog_ui73 import report
            xbmcgui.Dialog().notification('XCMate',report(row).replace('\n',' · '))
        _last=identity;return
    if setting_bool('catalog_status81',False):
        state=tr(38004 if row['state']=='RUNNING' else 38003)
        window.setProperty('XCMate.Catalog81.Text',state+' · '+str(row.get('group',''))[:80]+' · '+str(row.get('processed',0)))
    else:window.clearProperty('XCMate.Catalog81.Text')
    _last=identity


def legacy(pid,kind,cid,name,code,counts):
    """Called by a live legacy worker only, with real group and batch counts."""
    global _snapshot
    state={'INDEXING':'RUNNING','READY':'DONE','CACHED':'DONE','FAILED':'FAILED','CANCELLED':'INTERRUPTED'}.get(code,'FAILED')
    row=dict(id='delta-'+str(pid)+'-'+kind+'-'+str(cid),state=state,kind=kind,group=name,
        processed=counts.get('received',0),group_stored=counts.get('stored',0),updated=time.time(),code=code)
    with _lock:_snapshot=row

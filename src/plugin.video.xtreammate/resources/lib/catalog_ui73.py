"""Enqueue once, close immediately. No hidden Start screen or GUI network IO."""
from localization import tr


def show(portal):
    import xbmcgui
    from catalog_jobs73 import request,jobs,control,KINDS
    from menu_icons45 import multiselect,select
    dialog=xbmcgui.Dialog()
    current=[r for r in jobs() if r['pid']==str(portal['id'])]
    active=next((r for r in reversed(current) if r['state'] in ('WAITING','RUNNING','INTERRUPTED','FAILED')),None)
    if not active and current:
        choice=select(dialog,tr(38000),[tr(38011),tr(38014)],default='list')
        if choice==0:dialog.textviewer(tr(38011),report(current[-1]));return
        if choice!=1:return
    if active:
        choice=select(dialog,tr(38000),[tr(38011),tr(38012),tr(38013),tr(38014)],default='list')
        if choice==0:
            dialog.textviewer(tr(38011),report(active));return
        if choice==1:control(active['id'],resume=True);return
        if choice==2:control(active['id']);return
        if choice!=3:return
        if active.get('resume') or active['state']=='RUNNING':
            dialog.ok('XCMate',tr(38015));return
    choice=multiselect(dialog,tr(38000),[tr(32401),tr(32403),tr(32404),tr(38016)],preselect=[0,1,2],default='list')
    if not choice or not any(i in choice for i in (0,1,2)):return
    if not dialog.yesno(tr(38000),tr(38017)):return
    try:
        token=request(portal,[k for i,k in enumerate(KINDS) if i in choice],epg=3 in choice)
        dialog.notification('XCMate',tr(38018,token[:8]))
    except (OSError,ValueError,RuntimeError) as exc:
        from vodsync_api72 import failure
        dialog.ok('XCMate',tr(38019,failure(exc).code))


def report(job):
    import time
    def dates81(values):return ', '.join(str(k)+': '+time.strftime('%d.%m.%Y %H:%M',time.localtime(v)) for k,v in values.items() if isinstance(v,(int,float))) or '—'
    state=tr({'WAITING':38003,'RUNNING':38004,'DONE':38005,'FAILED':38006,'INTERRUPTED':38007}.get(job['state'],38003))
    return '\n'.join([tr(37151) if __import__('utils').setting_bool('xc_background_prefetch',False) else tr(37150),state,'ID: '+job['id'][:8],tr(38020,job.get('group',''),job.get('cursor',0),len(job.get('units') or [])),
        tr(38021,job.get('processed',0)),tr(38022,str(job.get('counts',{}))),
        tr(38023,str(job.get('readback89',job.get('readback',{})))),tr(32791,str(job.get('delta81',{}))),tr(32796,len(job.get('failed_groups81',[]))),tr(32792,dates81(job.get('last_api_success81',{}))),tr(32793,dates81(job.get('last_full_sync81',{}))),tr(38019,job.get('code','') or 'OK')])

"""Bounded selected-group workers, LastGood and selection-owned publication."""
import hashlib,json,threading,time
from concurrent.futures import Future
_slots=threading.BoundedSemaphore(2)

def trace94(nav,code,count=0,reason=''):
    try:
        import xbmc
        key=hashlib.sha256((str(nav.portal['id'])+'|'+str(nav.category_id)).encode()).hexdigest()[:16]
        allowed={'GROUP_SELECTED','GROUP_READY','GROUP_EMPTY_CONFIRMED','GROUP_UI_VISIBLE','GROUP_PENDING','GROUP_SQL_BUSY','GROUP_RETRY_EXHAUSTED','GROUP_UNAVAILABLE','GROUP_STALE_IGNORED'}
        if code not in allowed:return
        causes={'','BUDGET','SQLITE_BUSY','SQLITE_LOCKED','GROUP_NOT_IMPORTED','GROUP_NOT_AVAILABLE','REVISION_CHANGED','LOCAL_LIVE_UNAVAILABLE','GROUP_DISABLED','BUSY'}
        xbmc.log('[XCMate][GROUP96] code='+code+' group='+key+' rows='+str(max(0,count))+' reason='+(reason if reason in causes else 'UNKNOWN'),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError):pass

def selected(nav):
    pending=getattr(nav,'_group_verify94',set());cid=str(nav.category_id)
    pending.add(cid);nav._group_verify94=pending
    nav._group_selection96=getattr(nav,'_group_selection96',0)+1
    task=getattr(nav,'_group_task93',None)
    if task and task[0]!=cid:nav._group_task93=None # Old worker releases its own slot; never publishes GUI.
    attempts=getattr(nav,'_group_attempts96',{});attempts[cid]=0;nav._group_attempts96=attempts
    due=getattr(nav,'_group_due96',{});due[cid]=0;nav._group_due96=due
    nav._group_retry93=0
    trace94(nav,'GROUP_SELECTED')

def state(nav):return getattr(nav,'_group_states94',{}).get(str(nav.category_id),'')

def refresh_due(nav):
    marker=__import__('live_warm68').token(nav.portal)
    previous=getattr(nav,'_group_catalog_token96',marker);nav._group_catalog_token96=marker
    if previous!=marker:selected(nav)
    task=getattr(nav,'_group_task93',None)
    if task:return task[1].done()
    cid=str(nav.category_id)
    return cid in getattr(nav,'_group_verify94',set()) and getattr(nav,'_group_attempts96',{}).get(cid,0)<3 and time.monotonic()>=getattr(nav,'_group_due96',{}).get(cid,0)

def rows(nav):
    cid=str(nav.category_id)
    if cid=='*' or not nav.enabled or cid not in nav.enabled:return None
    pid=str(nav.portal['id']);scope=hashlib.sha256(json.dumps([nav.portal.get(k) for k in ('id','type','xc_host','xc_user','xc_pass')]).encode()).hexdigest()
    if getattr(nav,'_group_owner94',pid)!=pid or getattr(nav,'_group_scope96',scope)!=scope:
        nav._group_rows93={};nav._group_states94={};nav._group_task93=None;nav._group_attempts96={};nav._group_due96={}
    nav._group_owner94=pid;nav._group_scope96=scope
    saved=getattr(nav,'_group_rows93',{});states=getattr(nav,'_group_states94',{});nav._group_states94=states
    verify=getattr(nav,'_group_verify94',set());nav._group_verify94=verify
    attempts=getattr(nav,'_group_attempts96',{});nav._group_attempts96=attempts
    due=getattr(nav,'_group_due96',{});nav._group_due96=due
    task=getattr(nav,'_group_task93',None)
    if task and task[1].done():
        selected_cid,future=task;nav._group_task93=None
        try:
            model=future.result()
            current=selected_cid==cid and model.get('selection96',getattr(nav,'_group_selection96',0))==getattr(nav,'_group_selection96',0)
            if selected_cid in nav.enabled and model.get('pid94')==pid and model.get('scope96',scope)==scope:
                saved[selected_cid]=model['channels'];nav._group_rows93=saved
                if current:
                    states[selected_cid]='GROUP_READY' if model['channels'] else 'GROUP_EMPTY_CONFIRMED'
                    proofs=getattr(nav,'_group_proofs94',{});proofs[selected_cid]=model.get('proof94',{});nav._group_proofs94=proofs
                    if getattr(nav,'index',None) is model.get('base_index93'):
                        nav.channels=model['merged_channels93'];nav.index=model['merged_index93']
                        verify.discard(selected_cid)
                    else:
                        # Full catalogue changed while this group was read.
                        # Keep its LastGood rows, rebuild against the new base.
                        verify.add(selected_cid);attempts[selected_cid]=0;due[selected_cid]=0
                    trace94(nav,states[selected_cid],len(model['channels']))
                else:trace94(nav,'GROUP_STALE_IGNORED')
                while len(saved)>4:saved.pop(next(iter(saved)))
        except Exception as exc:
            reason=getattr(exc,'code',str(exc.args[0]) if exc.args else 'LOCAL_LIVE_UNAVAILABLE')
            status='GROUP_SQL_BUSY' if reason in ('BUDGET','SQLITE_BUSY','SQLITE_LOCKED','BUSY') else 'GROUP_PENDING' if reason in ('GROUP_NOT_IMPORTED','REVISION_CHANGED') else 'GROUP_UNAVAILABLE'
            states[selected_cid]=status;verify.add(selected_cid)
            due[selected_cid]=time.monotonic()+(2 if attempts.get(selected_cid,1)<2 else 5)
            nav._group_retry93=due[selected_cid];trace94(nav,status,reason=reason)
    if cid in saved and cid not in verify:return saved[cid]
    if getattr(nav,'_group_task93',None) or time.monotonic()<due.get(cid,0):return saved.get(cid) or None
    if attempts.get(cid,0)>=3:
        if states.get(cid)!='GROUP_RETRY_EXHAUSTED':states[cid]='GROUP_RETRY_EXHAUSTED';trace94(nav,'GROUP_RETRY_EXHAUSTED')
        return saved.get(cid) or None
    if not _slots.acquire(blocking=False):verify.add(cid);due[cid]=time.monotonic()+.5;return saved.get(cid) or None
    attempts[cid]=attempts.get(cid,0)+1;states[cid]='LOADING_GROUP';verify.add(cid)
    future=Future();nav._group_task93=(cid,future)
    portal=dict(nav.portal);client=nav.xc;epoch=getattr(nav,'_group_selection96',0)
    sync_due=getattr(nav,'_group_sync_due93',{});may_sync=time.monotonic()>=sync_due.get(cid,0)
    if may_sync:sync_due[cid]=time.monotonic()+60;nav._group_sync_due93=sync_due
    base_index=getattr(nav,'index',None);base_channels=list(getattr(nav,'channels',[]))
    def work():
        try:
            if not future.set_running_or_notify_cancel():return
            from live_catalog46 import read
            from live_prepare47 import model
            proof={};categories,streams=read(portal,only=cid,receipt94=proof)
            if streams is None:raise OSError('GROUP_NOT_IMPORTED')
            value=model(portal,client,categories,streams)
            from tv_data import CatalogIndex
            merged=[c for c in base_channels if str(c.extra.get('category_id',''))!=cid]+value['channels']
            value.update(proof94=proof,pid94=pid,scope96=scope,selection96=epoch,base_index93=base_index,merged_channels93=merged,merged_index93=CatalogIndex(merged))
            future.set_result(value)
        except Exception as exc:
            if (getattr(exc,'code','') or str(exc))=='GROUP_NOT_IMPORTED' and may_sync:
                __import__('catalog_sync').request(portal,'live',preferred=cid,priority=0)
            if not future.done():future.set_exception(exc)
        finally:_slots.release()
    try:threading.Thread(target=work,name='XCMate-group96',daemon=True).start()
    except (RuntimeError,MemoryError):
        _slots.release();nav._group_task93=None;due[cid]=time.monotonic()+2
    return saved.get(cid) or None

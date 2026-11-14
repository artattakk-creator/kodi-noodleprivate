"""Single-flight local group reads, independent of EPG and full-catalog warmup."""
import threading,time
from concurrent.futures import Future
_slots=threading.BoundedSemaphore(2)

def trace94(nav,code,count=0):
    try:
        import hashlib
        key=hashlib.sha256((str(nav.portal['id'])+'|'+str(nav.category_id)).encode()).hexdigest()[:24]
        __import__('live_diagnostics').record('catalog_performance',code,item_tag=key,count=count)
    except Exception:pass


def selected(nav):
    pending=getattr(nav,'_group_verify94',set())
    pending.add(str(nav.category_id));nav._group_verify94=pending
    trace94(nav,'GROUP_SELECTED')


def state(nav):
    return getattr(nav,'_group_states94',{}).get(str(nav.category_id),'')


def rows(nav):
    cid=str(nav.category_id)
    if cid=='*' or not nav.enabled or cid not in nav.enabled:return None
    pid=str(nav.portal['id'])
    base=getattr(nav,'_group_base94',None)
    if getattr(nav,'_group_owner94',pid)!=pid or base is not None and base is not getattr(nav,'index',None):
        nav._group_rows93={};nav._group_states94={}
    nav._group_owner94=pid;nav._group_base94=getattr(nav,'index',None)
    saved=getattr(nav,'_group_rows93',{})
    states=getattr(nav,'_group_states94',{});nav._group_states94=states
    verify=getattr(nav,'_group_verify94',set())
    task=getattr(nav,'_group_task93',None)
    if task and task[1].done():
        selected,future=task;nav._group_task93=None
        try:
            model=future.result()
            if selected in nav.enabled and model.get('pid94')==pid and getattr(nav,'index',None) is model.get('base_index93'):
                states[selected]='GROUP_READY' if model['channels'] else 'GROUP_EMPTY_CONFIRMED'
                if selected==cid:trace94(nav,states[selected],len(model['channels']))
                proofs=getattr(nav,'_group_proofs94',{});proofs[selected]=model.get('proof94',{});nav._group_proofs94=proofs
                verify.discard(selected)
                saved[selected]=model['channels'];nav._group_rows93=saved
                if getattr(nav,'index',None) is model.get('base_index93'):
                    nav.channels=model['merged_channels93'];nav.index=model['merged_index93'];nav._group_base94=getattr(nav,'index',None)
                while len(saved)>4:saved.pop(next(iter(saved)))
        except Exception:
            states[selected]='GROUP_UNAVAILABLE';verify.discard(selected)
            nav._group_retry93=time.monotonic()+5
    if cid in saved and cid not in verify:return saved[cid]
    if getattr(nav,'_group_task93',None) or time.monotonic()<getattr(nav,'_group_retry93',0):return saved.get(cid)
    if not _slots.acquire(blocking=False):return None
    states[cid]='LOADING_GROUP'
    future=Future();nav._group_task93=(cid,future)
    portal=dict(nav.portal);client=nav.xc
    due=getattr(nav,'_group_sync_due93',{})
    may_sync=time.monotonic()>=due.get(cid,0)
    if may_sync:due[cid]=time.monotonic()+60;nav._group_sync_due93=due
    base_index=getattr(nav,'index',None);base_channels=list(getattr(nav,'channels',[]))
    def work():
        try:
            if not future.set_running_or_notify_cancel():return
            from live_catalog46 import read
            from live_prepare47 import model
            proof94={}
            categories,streams=read(portal,only=cid,receipt94=proof94)
            if streams is None:raise OSError('GROUP_PENDING')
            value=model(portal,client,categories,streams)
            from tv_data import CatalogIndex
            merged=[c for c in base_channels if str(c.extra.get('category_id',''))!=cid]+value['channels']
            value.update(proof94=proof94,pid94=pid,base_index93=base_index,merged_channels93=merged,merged_index93=CatalogIndex(merged))
            future.set_result(value)
        except Exception as error:
            if str(error)=='GROUP_NOT_IMPORTED' and may_sync:
                __import__('catalog_sync').request(portal,'live',preferred=cid,priority=0)
            future.set_exception(error)
        finally:_slots.release()
    try:threading.Thread(target=work,name='XCMate-group94',daemon=True).start()
    except (RuntimeError,MemoryError):
        _slots.release();nav._group_task93=None;nav._group_retry93=time.monotonic()+5
    return None

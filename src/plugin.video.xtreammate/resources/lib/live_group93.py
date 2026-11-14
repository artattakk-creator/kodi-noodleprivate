"""Single-flight local group reads, independent of EPG and full-catalog warmup."""
import threading,time
from concurrent.futures import Future
_slots=threading.BoundedSemaphore(2)

def rows(nav):
    cid=str(nav.category_id)
    if cid=='*' or cid not in nav.enabled:return None
    saved=getattr(nav,'_group_rows93',{})
    task=getattr(nav,'_group_task93',None)
    if task and task[1].done():
        selected,future=task;nav._group_task93=None
        try:
            model=future.result()
            if selected in nav.enabled:
                saved[selected]=model['channels'];nav._group_rows93=saved
                if getattr(nav,'index',None) is model.get('base_index93'):
                    nav.channels=model['merged_channels93'];nav.index=model['merged_index93']
                while len(saved)>4:saved.pop(next(iter(saved)))
        except Exception:
            nav._group_retry93=time.monotonic()+5
    if cid in saved:return saved[cid]
    if getattr(nav,'_group_task93',None) or time.monotonic()<getattr(nav,'_group_retry93',0):return None
    if not _slots.acquire(blocking=False):return None
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
            categories,streams=read(portal,only=cid)
            if streams is None:raise OSError('GROUP_PENDING')
            value=model(portal,client,categories,streams)
            from tv_data import CatalogIndex
            merged=[c for c in base_channels if str(c.extra.get('category_id',''))!=cid]+value['channels']
            value.update(base_index93=base_index,merged_channels93=merged,merged_index93=CatalogIndex(merged))
            future.set_result(value)
        except Exception as error:
            if str(error)=='GROUP_NOT_IMPORTED' and may_sync:
                __import__('catalog_sync').request(portal,'live',preferred=cid,priority=0)
            future.set_exception(error)
        finally:_slots.release()
    try:threading.Thread(target=work,name='XCMate-group93',daemon=True).start()
    except (RuntimeError,MemoryError):
        _slots.release();nav._group_task93=None;nav._group_retry93=time.monotonic()+5
    return None

"""Small indexed metadata adapter for the service-owned live navigator."""
import json
import threading
import time
from concurrent.futures import Future
_prepared={}
_lock=threading.Lock()


def prepare(portal,client,force=False):
    """Single-flight local disk/index preparation; never block the GUI owner."""
    from utils import addon_data_dir
    key=(addon_data_dir(),str(portal['id']))
    with _lock:
        previous=_prepared.get(key)
        if previous and not previous[0].done():return previous[0]
        if previous and not force:
            future,started=previous
            if not future.done():return future
            if not future.exception() and future.result()[1] is not None and time.monotonic()-started<10:return future
        # Bound concurrent cold portals as well as completed snapshots.
        if key not in _prepared and sum(not f.done() for f,_ in _prepared.values())>=4:
            future=Future();future.set_result((None,None));return future
        future=Future();_prepared[key]=(future,time.monotonic())
        if len(_prepared)>4:
            for other,(task,_) in list(_prepared.items()):
                if other!=key and task.done():_prepared.pop(other)
        def load():
            if not future.set_running_or_notify_cancel():return
            try:
                from live_catalog46 import read as indexed46
                from live_prepare47 import model,trace as trace47
                trace47(portal,'LOCAL_READ_BEGIN')
                def first47(first):
                    future.first_model47=model(portal,client,*first)
                    future.first46=first
                    trace47(portal,'START_GROUP_MODEL_READY',len(future.first_model47['channels']))
                # The local index already contains the configured category
                # names. Do not deserialize provider JSON before first group.
                value=indexed46(portal,first47) if portal.get('type')=='xtream' else None
                value=value if value is not None else read(portal,client)
                if value[0] is not None and value[1] is not None:
                    future.model47=model(portal,client,*value)
                    trace47(portal,'FULL_MODEL_READY',len(future.model47['channels']))
                future.set_result(value)
            except BaseException as error:future.set_exception(error)
        threading.Thread(target=load,name='XCMate-live-catalog',daemon=True).start()
        return future


def read(portal,client):
    if portal.get('type')=='xtream':
        from live_catalog46 import read as indexed46
        from library_index import IndexReadError
        try:value=indexed46(portal)
        except IndexReadError:return None,None
        if value is not None:return value
    categories=client.get_cached_catalog('get_live_categories')
    if portal.get('type')=='xtream':
        from library_index import Reader, IndexReadError
        reader=Reader(portal['id'],timeout=.15,query_seconds=1)
        try:
            if reader.state('live') is not None:
                if categories is None:
                    categories=[dict(category_id=g['cid'],category_name=g['title']) for g in reader.groups('live')]
                from group_selection import enabled_ids
                selected=enabled_ids(portal['id'],'live',categories)
                indexed={g['cid'] for g in reader._query('SELECT cid FROM groups WHERE pid=? AND kind=?',(portal['id'],'live'))}
                if not selected.issubset(indexed):
                    # A newly checked group may not be indexed yet. Retain the
                    # established cache-only list instead of losing its rows.
                    return categories,client.get_cached_catalog('get_live_streams')
                where='pid=? AND kind=?'+reader._filter('live')
                raw=reader._query('SELECT payload FROM titles WHERE '+where+' GROUP BY sid ORDER BY ordinal LIMIT 50001',
                                  (portal['id'],'live'),'live')
                if len(raw)>50000:return categories,None
                streams=[json.loads(r['payload']) for r in raw]
                return categories,[dict(row,stream_id=row['sid']) for row in streams]
        except IndexReadError:
            return categories,None
    return categories,client.get_cached_catalog('get_live_streams')

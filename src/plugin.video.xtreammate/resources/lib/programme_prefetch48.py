"""Rotate eight visible/start-group events independently of widget repaint.

An unchanged published widget used to skip the artwork cursor along with the
repaint, so only its first sixteen events were prepared until the next minute.
This lane never scans the source archive and uses the existing 24-job queue.
"""
import time
_positions={};_next={};_future56={}


def prepare(portal,rows,cancel=lambda:False):
    key=str(portal['id']);now=time.monotonic()
    if not rows or now<_next.get(key,0) or cancel():return False
    _next[key]=now+5
    pos=_positions.get(key,0)%len(rows)
    batch=[rows[(pos+i)%len(rows)] for i in range(min(8,len(rows)))]
    _positions[key]=(pos+len(batch))%len(rows)
    if len(_positions)>8:
        old=next(iter(_positions));_positions.pop(old);_next.pop(old,None)
    from local_epg import now_next
    from epg_sources import configuration
    from programme_events46 import from_info
    from programme_urls55 import enqueue,refreshed
    from programme_read47 import session
    from programme_index46 import publish
    with session():
        infos=now_next(portal['id'],batch,configuration(portal['id'])['mappings'])
        records=[]
        revision=next((info.get('snapshot_revision') for info in infos.values()),None)
        allow_lookup=refreshed(portal['id'],revision)
        for row in batch:
            if cancel():return False
            event=from_info(portal,row,infos.get(str(row['sid']),{}))
            if event.get('title'):
                records.append(event);enqueue(event,allow_lookup=allow_lookup)
            # NEXT is resolved ahead of its transition, with the same local
            # canonical/source identity as NOW; never borrow NOW's picture.
            from programme_events46 import describe
            info=infos.get(str(row['sid']),{})
            upcoming=[v for v in info.get('events',[]) if v.get('start',0)>event.get('start',0)]
            selected=upcoming[:1]
            if len(upcoming)>1:
                # The already-read bounded local page, not a second feed scan:
                # prepare explicitly classified announced films/episodes first.
                def priority57(value):
                    genre=str(value.get('genre') or value.get('category') or '').casefold()
                    return 0 if any(v in genre for v in ('spielfilm','movie','film')) else 1 if value.get('season') and value.get('episode') else 2
                later57=sorted(upcoming[1:],key=priority57)
                cursor=(key,str(row['sid']));pos56=_future56.get(cursor,0)%len(later57)
                selected.append(later57[pos56]);_future56[cursor]=pos56+1
                if len(_future56)>1024:_future56.pop(next(iter(_future56)))
            for following in selected:
                future=describe(portal,row,following,event.get('canonical',''),revision)
                if future.get('title'):records.append(future);enqueue(future,allow_lookup=allow_lookup)
    if records:publish(records,include_art=False)
    return bool(records)

"""Rotate eight visible/start-group events independently of widget repaint.

An unchanged published widget used to skip the artwork cursor along with the
repaint, so only its first sixteen events were prepared until the next minute.
This lane never scans the source archive and uses the existing 24-job queue.
"""
import time
_positions={};_next={}


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
    from programme_art46 import enqueue
    from programme_read47 import session
    from programme_index46 import publish
    with session():
        infos=now_next(portal['id'],batch,configuration(portal['id'])['mappings'])
        records=[]
        for row in batch:
            if cancel():return False
            event=from_info(portal,row,infos.get(str(row['sid']),{}))
            if event.get('title'):records.append(event);enqueue(event)
    if records:publish(records)
    return bool(records)

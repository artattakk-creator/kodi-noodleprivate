"""Rotate eight visible/start-group events independently of widget repaint.

An unchanged published widget used to skip the artwork cursor along with the
repaint, so only its first sixteen events were prepared until the next minute.
This lane never scans the source archive and uses the existing 24-job queue.
"""
import time
_positions={};_next={};_future56={}

def station90(row):
    value=row.extra if hasattr(row,'extra') else row
    return str(value.get('sid',value.get('stream_id','')))

def visible75(portal,rows):
    """Focused first, then its actual horizontal viewport; no IO or new worker."""
    if not rows:return []
    from hero_epg63 import focused64
    sid=focused64(str(portal['id'])) or str(portal.get('start_stream_id') or '')
    index=next((i for i,row in enumerate(rows) if station90(row)==sid),0)
    from home_schedule75 import visible_position
    left=visible_position(str(portal['id']),index)
    batch=[rows[index]]
    for row in rows[max(0,left):max(0,left)+5]:
        if row not in batch:batch.append(row)
    return batch[:5]


def prepare(portal,rows,cancel=lambda:False):
    key=str(portal['id']);now=time.monotonic()
    if not rows or now<_next.get(key,0) or cancel():return False
    _next[key]=now+5
    pos=_positions.get(key,0)%len(rows)
    from hero_epg63 import focused64
    sid64=focused64(key);preferred=next((row for row in rows if str(row.get('sid',''))==sid64),None) if sid64 else None
    from home_schedule75 import rest_allowed
    batch=visible75(portal,rows);seen64={str(row.get('sid','')) for row in batch};advance64=0
    viewport84=__import__('home_schedule75').applicable()
    maximum75=5 if viewport84 else 8 if rest_allowed() else 5
    while len(batch)<min(maximum75,len(rows)) and advance64<len(rows):
        row=rows[(pos+advance64)%len(rows)];advance64+=1
        if str(row.get('sid','')) not in seen64:batch.append(row);seen64.add(str(row.get('sid','')))
    _positions[key]=(pos+advance64)%len(rows)
    if len(_positions)>8:
        old=next(iter(_positions));_positions.pop(old);_next.pop(old,None)
    from epg_coverage66 import warm
    warm(portal,batch)
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
        from programme_refresh63 import active as explicit63
        from utils import setting_bool
        opted67=setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False) or setting_bool('programme_tvmaze67',False)
        allow_lookup=refreshed(portal['id'],revision) or explicit63(portal['id']) or opted67
        for row in batch:
            if cancel():return False
            event=from_info(portal,row,infos.get(str(row['sid']),{}))
            if event.get('title'):
                records.append(event);enqueue(event,allow_lookup=allow_lookup,local_image63=setting_bool('programme_art_local69',False),priority68=2 if row==batch[0] else row in batch[:5])
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
            for following in ([] if viewport84 else selected if rest_allowed() else selected[:1] if row==batch[0] else []):
                future=describe(portal,row,following,event.get('canonical',''),revision)
                if future.get('title'):records.append(future);enqueue(future,allow_lookup=allow_lookup,local_image63=setting_bool('programme_art_local69',False))
    if records:publish(records,include_art=False)
    from home_schedule75 import trace
    trace('VISIBLE5_QUEUED',count=min(5,len(batch)))
    from epg_snapshot75 import checkpoint
    checkpoint(portal['id'],batch)
    return bool(records)

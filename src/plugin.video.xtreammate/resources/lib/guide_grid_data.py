"""Bounded read-only EPG viewport; no imports, HTTP or provider mutations."""
import os
import sqlite3
import time
from urllib.parse import quote

ROWS=8
SPAN=3*3600
CELLS=24


def rectangle(start,stop,origin,span=SPAN,width=896):
    left=max(start,origin);right=min(stop,origin+span)
    if right<=left:return None
    x=int((left-origin)*width/span);end=int((right-origin)*width/span)
    return x,max(1,end-x)


def page(portal,offset,origin,category=None,client=None):
    from library_index import Reader
    from epg_sources import configuration
    from guide_store import path
    from epg_events import deduplicate
    reader=Reader(portal['id']);channels,total=reader.page('live',category=category,offset=offset,limit=ROWS)
    mappings=configuration(portal['id']).get('mappings',{});db=None;result=[]
    from local_epg import window,channel_keys
    snapshot=window(portal['id'],channels,mappings,origin,origin+SPAN,limit=101)
    state='OK' if snapshot is not None else 'NOT_CREATED'
    for channel in channels:
        sid,ids=channel_keys(channel,mappings);manual=mappings.get(sid)
        events=[];resolved='';mapping='MANUAL' if manual else 'UNMAPPED'
        if snapshot is not None:
            for ident in ids:
                raw=snapshot.get(ident,[])
                if raw:
                    resolved=snapshot.canonical.get(ident,ident)
                    events=deduplicate(raw[:100],channel=resolved)
                    if not manual:mapping='STREAM_ALIAS' if ident==sid else 'PROVIDER_ID'
                    break
        if not events and not manual and client is not None and origin<=time.time()<origin+SPAN:
            from epg_views import cached_short_guide
            short=cached_short_guide(client,sid)
            events=[dict(e,source=-1) for e in short.get('events',[]) if e['start']<origin+SPAN and e['stop']>origin]
            if events:mapping='SHORT_EPG'
        result.append(dict(channel=channel,events=events,mapping=mapping,epg_id=resolved,
                           truncated=len(events)>CELLS))
    # Original persistent artwork cache, queued from this viewport worker.
    # No remote texture ever reaches the GUI and no cache path is changed.
    from media_art import request
    request(channels)
    return dict(rows=result,total=total,groups=reader.groups('live'),code=state,origin=origin,offset=offset)


def initial(portal,origin,client=None):
    """Select one enabled start group and reveal the unmodified channel order."""
    from library_index import Reader
    reader=Reader(portal['id']);groups=reader.groups('live')
    allowed={str(g['cid']) for g in groups}
    start=reader.get('live',str(portal.get('start_stream_id') or ''))
    saved=str(portal.get('start_group_id') or '')
    category=saved if saved in allowed else ''
    position=reader.position('live',start['sid'],category) if start and category else None
    if start and not category:
        candidate=str(start.get('category_id') or '')
        if candidate in allowed:category=candidate
    if not category:category=str(groups[0]['cid']) if groups else ''
    position=reader.position('live',start['sid'],category) if start and category else None
    start_in_group=position is not None
    position=position if position is not None else 0
    offset=position//ROWS*ROWS
    # Empty category is deliberately an empty selection, never category=None.
    value=page(portal,offset,origin,category,client)
    value.update(category=category,row=position-offset)
    try:
        import xbmc
        xbmc.log('[XCMate][GUIDE_GROUP] stage=INITIAL groups={} saved_active={} selected_saved={} start_found={} start_in_group={} rows={} category_empty={} category_star={}'.format(
            len(groups),int(saved in allowed),int(bool(saved) and category==saved),int(start is not None),
            int(start_in_group),len(value['rows']),int(category==''),int(category=='*')),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError):pass
    return value

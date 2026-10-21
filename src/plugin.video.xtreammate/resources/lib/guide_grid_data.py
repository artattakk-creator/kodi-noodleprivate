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
    filename=path();state='NOT_CREATED'
    if os.path.exists(filename):
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05);db.row_factory=sqlite3.Row
        deadline=time.monotonic()+.4;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000);state='OK'
    try:
        for channel in channels:
            manual=mappings.get(channel['sid']);ids=[str(manual)] if manual else list(dict.fromkeys([channel['sid'],str(channel.get('epg_channel_id') or '')]))
            events=[];resolved='';mapping='MANUAL' if manual else 'UNMAPPED'
            if db is not None:
                for ident in ids:
                    if not ident:continue
                    alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(portal['id'],ident)).fetchone()
                    cid=alias[0] if alias else ident
                    raw=[dict(r) for r in db.execute('SELECT * FROM programmes WHERE pid=? AND cid=? AND start<? AND stop>? ORDER BY start,stop LIMIT 101',
                         (portal['id'],cid,origin+SPAN,origin))]
                    if raw:
                        events=deduplicate(raw[:100],channel=cid);resolved=cid
                        if not manual:mapping='STREAM_ALIAS' if ident==channel['sid'] else 'PROVIDER_ID'
                        break
            # Cache-only short fallback is local and never fills a future day
            # with invented schedules. Explicit manual mappings stay authoritative.
            if not events and not manual and client is not None and origin<=time.time()<origin+SPAN:
                from epg_views import cached_short_guide
                short=cached_short_guide(client,channel['sid'])
                events=[dict(e,source=-1) for e in short.get('events',[]) if e['start']<origin+SPAN and e['stop']>origin]
                if events:mapping='SHORT_EPG'
            result.append(dict(channel=channel,events=events,mapping=mapping,epg_id=resolved,
                               truncated=len(events)>CELLS))
    finally:
        if db is not None:db.close()
    return dict(rows=result,total=total,groups=reader.groups('live'),code=state,origin=origin,offset=offset)

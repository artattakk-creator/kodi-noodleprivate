"""Read a complete enabled Live start group in bounded keyset pages.

No COUNT, OFFSET, catalogue import or HTTP. The published generation is pinned
for one read; legacy groups remain supported. Native Kodi owns horizontal
scrolling/texture demand. Only a page is hydrated by each SQLite operation.
"""
import json
import sqlite3
import time
from urllib.parse import quote
PAGE=64


def pages(portal):
    saved68=str(portal.get('start_group_id') or '')
    if saved68:
        from live_home62 import read as start_group68,Failure
        try:selected68,_=start_group68(portal)
        except Failure as failure68:
            if failure68.code in ('GROUP_DISABLED','START_GROUP_UNAVAILABLE','START_GROUP_MISSING','DISABLED'):return
            from library_index import IndexReadError
            error68=IndexReadError(failure68.code);error68.code=failure68.code;raise error68 from None
        # Preserve the saved legacy widget's start-station pin exactly once.
        pinned68=str(portal.get('start_stream_id') or '')
        row68=next((row for row in selected68 if row['sid']==pinned68),None)
        if row68:selected68=[row68]+[row for row in selected68 if row['sid']!=pinned68]
        for offset68 in range(0,len(selected68),PAGE):yield selected68[offset68:offset68+PAGE]
        return
    from widget_movie47 import MovieReader
    from library_index import path,initial_group,IndexReadError
    from widget_query44 import groups,get
    reader=MovieReader(portal['id'],kind='live')
    try:
        start=get(reader,'live',str(portal.get('start_stream_id') or ''))
        cid=initial_group(portal,groups(reader,'live'),start)
    finally:reader.close()
    if not cid:return
    db=sqlite3.connect('file:'+quote(reader.filename or path(),safe='/')+'?mode=ro',uri=True,timeout=.05)
    db.row_factory=sqlite3.Row
    try:
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        head=db.execute('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?',(reader.pid,'live',cid)).fetchone()
        table='items_v2' if head else 'titles'
        where='pid=? AND kind=? AND cid=?';args=[reader.pid,'live',cid]
        if head:where+=' AND generation=?';args.append(head[0])
        last=None;first=True;pinned=start if start and str(start.get('category_id',''))==str(cid) else None
        while True:
            deadline=time.monotonic()+.25
            db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
            suffix=' AND (ordinal>? OR (ordinal=? AND sid>?))' if last else ''
            params=args+(list(last) if last else [])+[PAGE]
            rows=db.execute('SELECT ordinal,sid,payload FROM '+table+' WHERE '+where+suffix+' ORDER BY ordinal,sid LIMIT ?',params).fetchall()
            if not rows:
                if first and pinned:yield [pinned]
                return
            data=[json.loads(row['payload']) for row in rows if not pinned or row['sid']!=pinned['sid']]
            # Pin once; do not lose the final row of the group when it moves.
            if first and pinned:data.insert(0,pinned)
            first=False;last=(rows[-1]['ordinal'],rows[-1]['ordinal'],rows[-1]['sid'])
            if data:yield data
    except sqlite3.Error as exc:
        error=IndexReadError('BUDGET' if getattr(exc,'sqlite_errorname','')=='SQLITE_INTERRUPT' else 'SQLITE_BUSY')
        error.code=str(error);raise error from None
    finally:db.close()


def snapshot(portal):
    """Compatibility list for existing callers; pages are the render hot path."""
    return [row for page in pages(portal) for row in page]


def infos(portal,rows):
    from programme_read47 import memo
    from epg_status import revision
    from epg_handoff63 import profile_scope
    key=('live-text63',profile_scope(),str(portal['id']),str(revision(portal['id'])),
         tuple((str(r.get('sid','')),str(r.get('epg_channel_id') or r.get('tvg_id') or r.get('xmltv_id') or '')) for r in rows))
    return memo(key,lambda:_infos63(portal,rows))


def _infos63(portal,rows):
    from local_epg import now_next
    from epg_sources import configuration
    mappings=configuration(portal['id'])['mappings'];result={}
    from epg_handoff63 import get,meta_key
    from epg_status import revision
    import xbmcgui
    config_revision65=revision(portal['id']);guide_revision65=xbmcgui.Window(10000).getProperty(meta_key(portal['id']))
    missing=[]
    for row in rows:
        sid=str(row['sid']);value=get(portal['id'],sid,mappings=mappings)
        if value is not None:result[sid]=value
        else:missing.append(row)
    if revision(portal['id'])!=config_revision65 or xbmcgui.Window(10000).getProperty(meta_key(portal['id']))!=guide_revision65:
        result={};missing=list(rows)
    for offset in range(0,len(missing),16):result.update(now_next(portal['id'],missing[offset:offset+16],mappings,display_only65=True))
    return result

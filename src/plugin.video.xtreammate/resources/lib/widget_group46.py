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
    from local_epg import now_next
    from epg_sources import configuration
    mappings=configuration(portal['id'])['mappings'];result={}
    for offset in range(0,len(rows),16):result.update(now_next(portal['id'],rows[offset:offset+16],mappings))
    return result

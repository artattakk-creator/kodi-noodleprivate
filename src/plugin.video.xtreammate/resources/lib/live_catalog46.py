"""Generation-pinned Live metadata, no UNION/GROUP BY of full payloads."""
import json,os,sqlite3,time
from urllib.parse import quote


def read(portal,publish=lambda value:None,categories=None):
    from widget_data41 import WidgetReader
    from library_index import path,initial_group,IndexReadError
    reader=WidgetReader(portal['id']);state=reader.state('live')
    if state is None:return None
    groups=reader.groups('live')
    from group_selection import load,enabled_ids
    selected=load(portal['id'],'live')
    if selected and not selected.issubset({g['cid'] for g in groups}):return None
    if categories is not None and not enabled_ids(portal['id'],'live',categories).issubset({g['cid'] for g in groups}):return None
    categories=categories if categories is not None else [dict(category_id=g['cid'],category_name=g['title']) for g in groups]
    start=reader.get('live',str(portal.get('start_stream_id') or ''));cid=initial_group(portal,groups,start)
    ordered=sorted(groups,key=lambda g:g['cid']!=cid)
    db=sqlite3.connect('file:'+quote(reader.filename or path(),safe='/')+'?mode=ro',uri=True,timeout=.05);db.row_factory=sqlite3.Row
    streams=[];seen=set()
    try:
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        for group in ordered:
            head=db.execute('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?',(reader.pid,'live',group['cid'])).fetchone()
            table='items_v2' if head else 'titles';args=[reader.pid,'live',group['cid']]
            where='pid=? AND kind=? AND cid=?'
            if head:where+=' AND generation=?';args.append(head[0])
            last=None
            while True:
                deadline=time.monotonic()+.25;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
                suffix=' AND (ordinal>? OR (ordinal=? AND sid>?))' if last else ''
                rows=db.execute('SELECT ordinal,sid,payload FROM '+table+' WHERE '+where+suffix+' ORDER BY ordinal,sid LIMIT 128',args+(list(last) if last else [])).fetchall()
                if not rows:break
                for row in rows:
                    if row['sid'] in seen:continue
                    seen.add(row['sid']);item=json.loads(row['payload']);streams.append(dict(item,stream_id=item['sid']))
                    if len(streams)>50000:return categories,None
                last=(rows[-1]['ordinal'],rows[-1]['ordinal'],rows[-1]['sid'])
            if group['cid']==cid:publish((categories,list(streams)))
        return categories,streams
    except (sqlite3.Error,ValueError,TypeError) as exc:
        raise IndexReadError('LOCAL_LIVE_UNAVAILABLE') from None
    finally:db.close()

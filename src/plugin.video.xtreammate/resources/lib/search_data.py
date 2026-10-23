"""Worker-only local search; same group filters and guide aliases as the grid."""
import json
import os
import sqlite3
import time
from urllib.parse import quote

KINDS=('live','vod','series')
PAGE=48


def live_matches(portal,query,reader,now):
    from library_index import normalized
    from guide_store import path
    from epg_sources import configuration
    where='pid=? AND kind=?'+reader._filter('live')
    raw=reader._query('SELECT payload FROM titles WHERE '+where+' GROUP BY sid ORDER BY ordinal LIMIT 50001',
                      (portal['id'],'live'),'live')
    if len(raw)>50000:raise ValueError('SEARCH_CHANNEL_LIMIT')
    channels=[json.loads(r['payload']) for r in raw]
    events={};aliases={};code='NO_EPG';db=None
    try:
        if os.path.exists(path()):
            db=sqlite3.connect('file:'+quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.075)
            db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON')
            deadline=time.monotonic()+1
            db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
            aliases={r[0]:r[1] for r in db.execute('SELECT alias,cid FROM guide_alias WHERE pid=?',(portal['id'],))}
            rows=db.execute('SELECT * FROM programmes WHERE pid=? AND start<=? AND stop>? ORDER BY source,start DESC LIMIT 50001',(portal['id'],now,now)).fetchall()
            if len(rows)>50000:raise ValueError('SEARCH_GUIDE_LIMIT')
            for row in rows:events.setdefault(row['cid'],dict(row))
            code='READY'
    except (sqlite3.Error,OSError,ValueError):events={};aliases={};code='EPG_UNAVAILABLE'
    finally:
        if db is not None:db.close()
    mappings=configuration(portal['id']).get('mappings',{})
    tokens=list(dict.fromkeys(normalized(query).split()));result=[]
    for row in channels:
        manual=mappings.get(row['sid'])
        ids=[str(manual)] if manual else [row['sid'],str(row.get('epg_channel_id') or '')]
        event=next((events[aliases.get(ident,ident)] for ident in ids if ident and aliases.get(ident,ident) in events),None)
        channel_name=normalized(row.get('name',''));programme_name=normalized(event['title']) if event else ''
        name=all(t in channel_name for t in tokens)
        programme=bool(event and all(t in programme_name for t in tokens))
        if name or programme:result.append(dict(row,_now_title=event['title'] if programme else '',_now_match=programme))
    return result,code


def search(portal,query,kind='vod',offset=0,now=None):
    from library_index import Reader,IndexReadError
    from catalog_sync import request
    reader=Reader(portal['id'],timeout=.15,query_seconds=1)
    query=str(query).strip()[:200];result={}
    for section in KINDS:
        if not portal.get('include_'+section,True):
            result[section]=dict(rows=[],total=0,code='DISABLED');continue
        start=max(0,offset) if section==kind else 0
        try:
            state=reader.state(section)
            if not state:
                request(portal,section,portal.get('start_group_id','') if section=='live' else '',priority=5)
                result[section]=dict(rows=[],total=None,code='INDEX_PENDING');continue
            if section=='live':
                rows,code=live_matches(portal,query,reader,int(time.time() if now is None else now))
                total=len(rows);rows=rows[start:start+PAGE]
            else:rows,total=reader.page(section,query,offset=start,limit=PAGE);code='READY'
            result[section]=dict(rows=rows,total=total,code=code)
        except (IndexReadError,sqlite3.Error,OSError,ValueError):
            result[section]=dict(rows=[],total=None,code='INDEX_ERROR')
    return result

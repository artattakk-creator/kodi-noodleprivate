"""Read only a worker's requested Now/Next viewport from the existing guide DB."""
import os
import sqlite3
import time
from urllib.parse import quote


def cache(pid,channels,mappings,now):
    import guide_store
    path=getattr(guide_store,'path',lambda:'')()
    if not path or not os.path.isfile(path):return None
    db=None
    try:
        db=sqlite3.connect('file:'+quote(path,safe='/')+'?mode=ro',uri=True,timeout=.075)
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON')
        deadline=time.monotonic()+.5
        db.set_progress_handler(lambda:int(time.monotonic()>=deadline),1000)
        if not db.execute('SELECT 1 FROM guide_meta WHERE pid=?',(pid,)).fetchone():return None
        result={}
        # One transaction makes aliases and rows a consistent read snapshot.
        db.execute('BEGIN')
        for channel in channels[:16]:
            sid=str(channel.extra.get('stream_id',''))
            manual=mappings.get(sid)
            keys=[str(manual)] if manual else [sid,str(channel.tvg_id or '')]
            for ident in keys:
                if not ident or ident in result:continue
                alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(pid,ident)).fetchone()
                cid=alias[0] if alias else ident
                rows=db.execute('SELECT title,description,start,stop,source FROM programmes WHERE pid=? AND cid=? AND stop>? AND start<? ORDER BY start,source,stop LIMIT 48',
                                (pid,cid,now,now+2*86400)).fetchall()
                result[ident]=[dict(name=r['title'],descr=r['description'],start_timestamp=r['start'],
                                    stop_timestamp=r['stop'],_source_index=r['source']) for r in rows]
        return result
    except (OSError,sqlite3.Error):return None
    finally:
        if db is not None:db.close()

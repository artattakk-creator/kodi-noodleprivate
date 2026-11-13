"""Bounded now/next cache; full source-aware horizon stays in the central guide."""
import time

def short(data,now=None):
    now=time.time() if now is None else now
    from epg_views import _as_int
    import json
    output={};count=0
    # Big provider lists use just current/next. The long horizon stays in SQL.
    per_channel=2 if len(data)>1024 else 7
    for cid,entries in data.items():
        if not isinstance(entries,list):continue
        active=[];upcoming=[];previous=[]
        for entry in entries:
            if not isinstance(entry,dict):continue
            start=_as_int(entry.get('start_timestamp'));stop=_as_int(entry.get('stop_timestamp'))
            if stop<=start:continue
            if start<=now<stop:active.append(entry)
            elif start>now:upcoming.append(entry)
            elif now-6*3600<stop<=now:previous.append(entry)
        active.sort(key=lambda e:_as_int(e.get('start_timestamp')),reverse=True)
        upcoming.sort(key=lambda e:_as_int(e.get('start_timestamp')))
        chosen=(active[:1]+upcoming)[:max(1,per_channel-(1 if per_channel>2 and previous else 0))]
        if per_channel>2 and previous:
            chosen.append(max(previous,key=lambda e:_as_int(e.get('stop_timestamp'))))
        rows=[]
        for entry in chosen:
            # Short UI text only. Original full descriptions, source IDs and
            # artwork references have already passed the central DB readback.
            row=dict(entry)
            for key in ('description','desc','plot'):
                if isinstance(row.get(key),str):row[key]=row[key][:512]
            rows.append(row)
        rows.sort(key=lambda e:_as_int(e.get('start_timestamp')))
        if rows:output[cid]=rows;count+=len(rows)
        if count>40000:raise OSError('SNAPSHOT_BUDGET')
    if len(json.dumps(output,ensure_ascii=False,separators=(',',':')).encode())>16*1024**2:
        raise OSError('SNAPSHOT_BYTE_BUDGET')
    return output

def committed(pid,revision):
    """Cold read after central commit, before publishing a reduced disk cache."""
    from guide_store import path
    import sqlite3
    from urllib.parse import quote
    db=sqlite3.connect('file:'+quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.05)
    try:
        row=db.execute('SELECT revision FROM guide_meta WHERE pid=?',(str(pid),)).fetchone()
        return bool(row and row[0]==revision)
    finally:db.close()

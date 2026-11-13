"""Bounded now/next cache; full source-aware horizon stays in the central guide."""
import time

def short(data,now=None):
    now=time.time() if now is None else now
    from epg_views import _as_int
    output={};count=0
    for cid,entries in data.items():
        if not isinstance(entries,list):continue
        # No independent image matching or modification of source metadata.
        eligible=[e for e in entries if isinstance(e,dict)
                  and _as_int(e.get('stop_timestamp'))>now-6*3600
                  and _as_int(e.get('start_timestamp'))<now+24*3600]
        eligible.sort(key=lambda e:_as_int(e.get('start_timestamp')))
        chosen=eligible[:12]
        if not chosen:
            upcoming=[e for e in entries if isinstance(e,dict) and _as_int(e.get('start_timestamp'))>now]
            if upcoming:chosen=[min(upcoming,key=lambda e:_as_int(e.get('start_timestamp')))]
        if chosen:output[cid]=chosen;count+=len(chosen)
        if count>40000:raise OSError('SNAPSHOT_BUDGET')
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

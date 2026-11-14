"""Source-qualified pre-commit proof and independent post-commit SQLite readback."""
import hashlib,json,sqlite3
from urllib.parse import quote


def digest(db,pid,source,cancel=lambda:False,progress=lambda count:None):
    h=hashlib.sha256();count=0;first=None;last=None
    db.set_progress_handler(lambda:int(cancel()),1000)
    try:
        for row in db.execute('SELECT cid,start,stop,title,description,rank FROM guide44_inputs WHERE pid=? AND source_id=? ORDER BY cid,start,stop',(str(pid),source)):
            if cancel():raise InterruptedError('EPG_CANCELLED')
            h.update(json.dumps(tuple(row),ensure_ascii=False,separators=(',',':')).encode());h.update(b'\n')
            count+=1;first=row[1] if first is None else min(first,row[1]);last=row[2] if last is None else max(last,row[2])
            if count%1024==0:progress(count)
        progress(count)
        return dict(rows=count,digest=h.hexdigest(),first=first,last=last)
    except sqlite3.Error:
        if cancel():raise InterruptedError('EPG_CANCELLED')
        raise
    finally:db.set_progress_handler(None,0)


def verify(filename,pid,source,expected,revision,cancel=lambda:False,progress=lambda count:None):
    db=sqlite3.connect('file:'+quote(str(filename),safe='/')+'?mode=ro',uri=True,timeout=.25)
    try:
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        row=db.execute('SELECT revision FROM guide_meta WHERE pid=?',(str(pid),)).fetchone()
        if not row or row[0]!=revision:raise OSError('EPG_READBACK_REVISION_CHANGED')
        actual=digest(db,pid,source,cancel,progress)
        if not actual['rows'] or actual!=expected:raise OSError('EPG_READBACK_MISMATCH')
        return actual
    finally:db.close()

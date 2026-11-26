"""Read-only, revision/file-pinned per-source inventory."""
import copy
import os
import sqlite3
import threading
import time
from datetime import date
from urllib.parse import quote

_cache={}
_lock=threading.RLock()


def token(filename):
    result=[]
    for suffix in ('','-wal'):
        try:
            entry=os.stat(filename+suffix)
            # SQLite may open a zero-byte WAL even on a read-only connection.
            # A WAL containing frames or a changed main file remains decisive.
            if suffix and entry.st_size==0:
                result.append(None)
            else:
                result.append((entry.st_dev,entry.st_ino,entry.st_size,entry.st_mtime_ns))
        except FileNotFoundError:
            result.append(None)
    return tuple(result)


def collect(pid,filename,seconds=8,source_seconds=2,cancel=lambda:False,*,now=None):
    started=time.monotonic()
    end=started+seconds
    db=None
    rows=[]
    total=first=last=None
    code='READY'
    from epg_horizon102 import stored
    now=time.time() if now is None else now
    horizon=None
    key=(filename,str(pid),date.fromtimestamp(now))

    def result(status):
        return dict(code=status,sources=rows,programmes=total,first=first,last=last,horizon102=horizon)

    try:
        if cancel():
            return result('INVENTORY_CANCELLED')
        if not os.path.isfile(filename):
            total=0
            return result('NOT_CREATED')
        before=token(filename)
        with _lock:
            cached=_cache.get(key)
        if cached and cached[0]==before:
            return copy.deepcopy(cached[1])
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.1)
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        db.set_progress_handler(lambda:int(cancel() or time.monotonic()>=end),1000)
        ids=[r[0] for r in db.execute('SELECT DISTINCT source_id FROM guide44_inputs WHERE pid=? LIMIT 129',(str(pid),))]
        if len(ids)>128:
            return result('INVENTORY_BUDGET')
        total,first,last=db.execute('SELECT count(*),min(start),max(stop) FROM programmes WHERE pid=?',(str(pid),)).fetchone()
        for source in ids:
            if cancel():
                return result('INVENTORY_CANCELLED')
            deadline=min(end,time.monotonic()+source_seconds)
            db.set_progress_handler(lambda:int(cancel() or time.monotonic()>=deadline),1000)
            try:
                if time.monotonic()>=deadline:
                    raise TimeoutError('INVENTORY_BUDGET')
                # The primary key orders this scan by source and channel.
                # Aggregate in SQLite to avoid materializing every event in Python.
                channels,n,left,right=db.execute("""
                    SELECT count(*),sum(events),min(first),max(last)
                    FROM (
                        SELECT count(*) AS events,min(start) AS first,max(stop) AS last
                        FROM guide44_inputs WHERE pid=? AND source_id=? GROUP BY cid
                    )
                    """,(str(pid),source)).fetchone()
                if cancel():
                    return result('INVENTORY_CANCELLED')
                if time.monotonic()>=deadline or n>=1000000:
                    raise TimeoutError('INVENTORY_BUDGET')
                row=dict(id=source,code='READY',channels=channels,programmes=n,first=left,last=right)
            except (TimeoutError,sqlite3.Error) as exc:
                if cancel():
                    return result('INVENTORY_CANCELLED')
                reason='DB_BUSY' if getattr(exc,'sqlite_errorcode',0)&255 in (5,6) else 'INVENTORY_BUDGET'
                row=dict(id=source,code=reason,channels=None,programmes=None,first=None,last=None)
                code='PARTIAL'
            if row['code']=='READY':
                try:
                    row['horizon102']=stored(db,now,str(pid),source,row['first'],row['last'])
                except sqlite3.OperationalError:
                    row['horizon102']=None
                    code='PARTIAL'
            rows.append(row)
        db.set_progress_handler(lambda:int(cancel() or time.monotonic()>=end),1000)
        if not cancel() and time.monotonic()<end:
            try:
                horizon=stored(db,now,str(pid),first=first,last=last)
            except sqlite3.OperationalError:
                code='PARTIAL'
        else:
            code='PARTIAL'
        if cancel():
            return result('INVENTORY_CANCELLED')
        value=dict(result(code),elapsed_ms=round((time.monotonic()-started)*1000,2))
        if code=='READY' and token(filename)==before:
            with _lock:
                if len(_cache)>=16:
                    _cache.pop(next(iter(_cache)))
                _cache[key]=(before,copy.deepcopy(value))
        return value
    except sqlite3.Error as exc:
        if cancel():
            return result('INVENTORY_CANCELLED')
        number=getattr(exc,'sqlite_errorcode',0)&255
        return result('DB_BUSY' if number in (5,6) else 'INVENTORY_BUDGET' if number==9 else 'DB_SCHEMA_MISSING')
    except OSError:
        return result('STORAGE_IO')
    except (TypeError,ValueError):
        return result('DB_SCHEMA_MISSING')
    finally:
        if db is not None:
            db.close()

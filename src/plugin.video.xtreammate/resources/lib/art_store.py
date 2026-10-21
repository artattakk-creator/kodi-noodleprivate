"""Durable artwork jobs/budget. Private URLs never enter diagnostics.

Completed files are never automatically evicted. A full budget pauses new work;
only an explicit user action retries failed jobs or removes a chosen file.
"""
import hashlib
import os
import sqlite3
import time
import uuid

_ADOPTED=set()


def connect():
    from artwork_db import connect as open_jobs
    return open_jobs()


def budget():
    from art_storage import budget as value
    return value()


def key(url): return hashlib.sha256(url.encode()).hexdigest()


def enqueue(urls,priority=0):
    from media_art import cached
    from artwork_db import path
    from import_budget import check_space
    check_space(path(),sum(len(u) for u in urls)*3)
    db=connect()
    try:
        with db:
            for url in urls:
                if cached(url): continue
                db.execute('''INSERT INTO jobs VALUES(?,?,'PENDING',?,0,0,?,0)
                  ON CONFLICT(ident) DO UPDATE SET url=excluded.url,
                  priority=min(priority,excluded.priority),
                  status=CASE WHEN status='READY' THEN 'PENDING' ELSE status END''',
                    (key(url),url,priority,time.time()))
    finally: db.close()


def ready(url,size):
    db=connect()
    try:
        with db: db.execute("INSERT OR REPLACE INTO jobs VALUES(?,?,'READY',0,0,0,?,?)",(key(url),url,time.time(),size))
    finally: db.close()


def used():
    from art_storage import used as value
    return value()


def _pause(db):
    row=db.execute("SELECT value FROM art_state WHERE name='pause'").fetchone()
    if not row:return {}
    import json
    try:return json.loads(row[0])
    except ValueError:return {}


def resume_capacity():
    db=connect()
    try:
        with db:
            db.execute("DELETE FROM art_state WHERE name='pause'")
            db.execute("UPDATE jobs SET next_at=0,attempts=CASE WHEN status='SPACE_FULL' THEN 0 ELSE attempts END WHERE status IN ('SPACE_FULL','QUOTA_FULL','DISK_LOW','DISK_FULL','STORAGE_OFFLINE','CAPACITY_UNKNOWN','MIGRATING','PERMISSION_DENIED')")
    finally:db.close()


def pause_migration():
    import json
    from art_storage import policy
    db=connect()
    try:
        with db:db.execute("INSERT OR REPLACE INTO art_state VALUES('pause',?)",(json.dumps(dict(code='MIGRATING',until=time.time()+60,generation=policy()['generation'])),))
    finally:db.close()


def run_one(now=None):
    from media_art import fetch
    now=time.time() if now is None else now
    owner=uuid.uuid4().hex
    db=connect()
    try:
        db.execute('BEGIN IMMEDIATE')
        if _pause(db).get('until',0)>now:return False
        if db.execute('SELECT until FROM worker WHERE id=1').fetchone()[0]>now:return False
        row=db.execute("SELECT * FROM jobs WHERE status!='READY' AND attempts<3 AND next_at<=? ORDER BY priority,updated LIMIT 1",(now,)).fetchone()
        if not row: return False
        job=dict(row)
        # Claim with a finite lease, survives an interrupted Kodi process.
        with db:
            db.execute('UPDATE worker SET until=?,owner=? WHERE id=1',(now+30,owner))
            claimed=db.execute("UPDATE jobs SET next_at=?,status='RUNNING' WHERE ident=? AND next_at<=?",(now+30,job['ident'],now)).rowcount
        if not claimed: return False
    finally: db.close()
    try:
        if not fetch(job['url']):raise ValueError('no supported image')
    except Exception as exc:
        from art_storage import Paused
        import errno,json
        capacity=isinstance(exc,Paused) or (isinstance(exc,OSError) and getattr(exc,'errno',0) in (errno.ENOSPC,errno.EACCES,errno.EPERM,errno.EROFS))
        code=exc.code if isinstance(exc,Paused) else 'DISK_FULL' if capacity and exc.errno==errno.ENOSPC else 'PERMISSION_DENIED' if capacity else 'FAILED'
        db=connect()
        try:
            with db:
                db.execute('UPDATE jobs SET status=?,attempts=attempts+?,next_at=?,updated=? WHERE ident=?',
                    (code,0 if capacity else 1,now+(60 if capacity else min(1800,60*2**job['attempts'])),now,job['ident']))
                if capacity:
                    from art_storage import policy
                    db.execute("INSERT OR REPLACE INTO art_state VALUES('pause',?)",(json.dumps(dict(code=code,until=now+60,generation=policy()['generation'])),))
        finally:db.close()
    finally:
        db=connect()
        try:
            with db: db.execute("UPDATE worker SET until=0,owner='' WHERE id=1 AND owner=?",(owner,))
        finally: db.close()
    return True


def status():
    db=connect()
    try: counts={r[0]:r[1] for r in db.execute('SELECT status,count(*) FROM jobs GROUP BY status')}
    finally: db.close()
    from art_storage import diagnostic
    storage=diagnostic()
    db=connect()
    try:
        pause=_pause(db)
        inventory=[dict(r) for r in db.execute('SELECT pid,kind,items,poster_missing,fanart_missing,complete FROM art_inventory')]
    finally:db.close()
    return dict(counts=counts,bytes=storage.get('used',0),budget=storage.get('budget',0),storage=storage,pause=pause,inventory=inventory)


def retry():
    from artwork_db import reset_retry
    reset_retry()
    resume_capacity()
    db=connect()
    try:
        with db: db.execute("UPDATE jobs SET attempts=0,next_at=0,status='PENDING' WHERE status!='READY'")
    finally: db.close()


def prefetch_selected():
    """One local page per service cycle; never enqueue disabled categories."""
    from artwork_db import diagnostic
    if diagnostic().get('background_paused'):return
    from portals import get_active
    from library_index import Reader
    from media_art import sources,ensure_worker,valid_url
    ensure_worker()
    for portal in get_active():
        for kind in ('vod','series'):
            if not portal.get('include_'+kind,True): continue
            reader=Reader(portal['id']);state=reader.state(kind)
            # Bound priority seeding as well as the catalog scan. Local ID-only
            # state is paged without materialising every favourite on each tick.
            from media_state import art_priority_page
            for rail,priority in (('continue',0),('favourites',5)):
                name='priority:'+portal['id']+':'+kind+':'+rail
                db=connect()
                try:
                    row=db.execute('SELECT value FROM art_state WHERE name=?',(name,)).fetchone()
                finally:db.close()
                offset=int(row[0]) if row else 0
                important,next_offset=art_priority_page(portal['id'],kind,reader,rail,offset)
                from media_art import request
                if request(important,priority=priority):
                    db=connect()
                    try:
                        with db:db.execute('INSERT OR REPLACE INTO art_state VALUES(?,?)',(name,str(next_offset)))
                    finally:db.close()
            if not state: continue
            revision=state['revision']+str([g['cid'] for g in reader.groups(kind)])
            db=connect()
            try: prior=db.execute('SELECT revision,offset FROM scan WHERE pid=? AND kind=?',(portal['id'],kind)).fetchone()
            finally: db.close()
            offset=prior['offset'] if prior and prior['revision']==revision else 0
            if offset<0: continue
            rows,total=reader.page(kind,offset=offset,limit=48)
            from media_art import request
            if not request(rows,priority=20) and rows:continue
            db=connect()
            try:
                with db:
                    db.execute('INSERT OR REPLACE INTO scan VALUES(?,?,?,?)',(portal['id'],kind,revision,offset+len(rows) if rows and offset+len(rows)<total else -1))
                    if offset==0:db.execute('DELETE FROM art_inventory WHERE pid=? AND kind=?',(portal['id'],kind))
                    missing_poster=sum(not valid_url(sources(item)[0]) for item in rows)
                    missing_fanart=sum(not any(valid_url(u) for u in (item.get('backdrop_path') if isinstance(item.get('backdrop_path'),list) else [item.get('backdrop_path')])) for item in rows)
                    db.execute("""INSERT INTO art_inventory VALUES(?,?,?,?,?,?) ON CONFLICT(pid,kind) DO UPDATE SET
                        items=items+excluded.items,poster_missing=poster_missing+excluded.poster_missing,
                        fanart_missing=fanart_missing+excluded.fanart_missing,complete=excluded.complete""",
                        (portal['id'],kind,len(rows),missing_poster,missing_fanart,int(offset+len(rows)>=total)))
            finally: db.close()

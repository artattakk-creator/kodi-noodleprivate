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
    from utils import setting_int
    return max(32,min(4096,setting_int('media_art_budget_mb',512)))*1024*1024


def key(url): return hashlib.sha256(url.encode()).hexdigest()


def enqueue(urls,priority=0):
    from media_art import cached,folder
    from import_budget import check_space
    check_space(os.path.join(os.path.dirname(folder()),'media_art_jobs_v1.sqlite'),sum(len(u) for u in urls)*3)
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
    from media_art import folder
    root=folder();db=connect()
    try:
        if root not in _ADOPTED:
            known={r[0] for r in db.execute('SELECT ident FROM jobs')}
            pending=[]
            if os.path.isdir(root):
                with os.scandir(root) as entries:
                    for entry in entries:
                        if entry.name.endswith('.img') and entry.name[:-4] not in known and entry.is_file():
                            pending.append((entry.name[:-4],time.time(),entry.stat().st_size))
            for start in range(0,len(pending),64):
                with db:db.executemany("INSERT OR IGNORE INTO jobs VALUES(?,'','READY',0,0,0,?,?)",pending[start:start+64])
            _ADOPTED.add(root)
        return db.execute('SELECT coalesce(sum(bytes),0) FROM jobs').fetchone()[0]
    finally: db.close()


def run_one(now=None):
    from media_art import fetch
    now=time.time() if now is None else now
    owner=uuid.uuid4().hex
    db=connect()
    try:
        # Empty queues and another active lease do not need a write lock.
        if db.execute('SELECT until FROM worker WHERE id=1').fetchone()[0]>now: return False
        row=db.execute("SELECT * FROM jobs WHERE status!='READY' AND attempts<3 AND next_at<=? ORDER BY priority,updated LIMIT 1",(now,)).fetchone()
        if not row: return False
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT until FROM worker WHERE id=1').fetchone()[0]>now:return False
        job=dict(row)
        # Claim with a finite lease, survives an interrupted Kodi process.
        with db:
            db.execute('UPDATE worker SET until=?,owner=? WHERE id=1',(now+30,owner))
            claimed=db.execute("UPDATE jobs SET next_at=?,status='RUNNING' WHERE ident=? AND next_at<=?",(now+30,job['ident'],now)).rowcount
        if not claimed: return False
    finally: db.close()
    try: fetch(job['url'])
    except sqlite3.Error:
        # A completed file survives; the finite claim expires and a later
        # attempt adopts it. No network-attempt counter or reset is needed.
        return False
    except Exception as exc:
        code='SPACE_FULL' if isinstance(exc,OSError) and getattr(exc,'errno',None)==28 else 'FAILED'
        db=connect()
        try:
            with db: db.execute('UPDATE jobs SET status=?,attempts=attempts+1,next_at=?,updated=? WHERE ident=?',
                (code,now+min(1800,60*2**job['attempts']),now,job['ident']))
        finally: db.close()
    finally:
        try:
            db=connect()
            try:
                with db:db.execute("UPDATE worker SET until=0,owner='' WHERE id=1 AND owner=?",(owner,))
            finally:db.close()
        except sqlite3.Error:pass # finite lease; never turn BUSY into data loss
    return True


def status(cancel=lambda:False):
    from artwork_db import snapshot,diagnostic
    import shutil
    value=dict(budget=budget(),bytes=None,counts=None,code='UNAVAILABLE',health=diagnostic())
    # All waits happen in the status worker, at most one short retry. Never
    # reuse the writer connector or run file adoption from a status route.
    for attempt in range(2):
        value.update(snapshot(cancel))
        if value['code']!='BUSY' or attempt or cancel():break
        import xbmc
        if xbmc.Monitor().waitForAbort(.04):break
    try:
        from media_art import folder
        capacity=shutil.disk_usage(os.path.dirname(folder()))
        value.update(free=capacity.free,total=capacity.total)
    except OSError:value['capacity_code']='UNAVAILABLE'
    return value


def retry():
    from artwork_db import reset_retry
    reset_retry()
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
    from media_art import sources
    for portal in get_active():
        for kind in ('vod','series'):
            if not portal.get('include_'+kind,True): continue
            reader=Reader(portal['id']);state=reader.state(kind)
            if not state: continue
            revision=state['revision']+str([g['cid'] for g in reader.groups(kind)])
            db=connect()
            try: prior=db.execute('SELECT revision,offset FROM scan WHERE pid=? AND kind=?',(portal['id'],kind)).fetchone()
            finally: db.close()
            offset=prior['offset'] if prior and prior['revision']==revision else 0
            if offset<0: continue
            rows,total=reader.page(kind,offset=offset,limit=48)
            from media_art import request
            request(rows,priority=20)
            db=connect()
            try:
                with db: db.execute('INSERT OR REPLACE INTO scan VALUES(?,?,?,?)',(portal['id'],kind,revision,offset+len(rows) if rows and offset+len(rows)<total else -1))
            finally: db.close()

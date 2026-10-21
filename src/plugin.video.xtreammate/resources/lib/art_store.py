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
            # Adopt old 64-file cache once, without moving/deleting its files.
            with db:
                if os.path.isdir(root):
                    for entry in os.scandir(root):
                        if not entry.name.endswith('.img') or not entry.is_file(): continue
                        db.execute("INSERT OR IGNORE INTO jobs VALUES(?,'','READY',0,0,0,?,?)",(entry.name[:-4],time.time(),entry.stat().st_size))
            _ADOPTED.add(root)
        return db.execute('SELECT coalesce(sum(bytes),0) FROM jobs').fetchone()[0]
    finally: db.close()


def run_one(now=None):
    from media_art import fetch
    now=time.time() if now is None else now
    owner=uuid.uuid4().hex
    db=connect()
    try:
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT until FROM worker WHERE id=1').fetchone()[0]>now: return False
        row=db.execute("SELECT * FROM jobs WHERE status!='READY' AND attempts<3 AND next_at<=? ORDER BY priority,updated LIMIT 1",(now,)).fetchone()
        if not row: return False
        job=dict(row)
        # Claim with a finite lease, survives an interrupted Kodi process.
        with db:
            db.execute('UPDATE worker SET until=?,owner=? WHERE id=1',(now+30,owner))
            claimed=db.execute("UPDATE jobs SET next_at=?,status='RUNNING' WHERE ident=? AND next_at<=?",(now+30,job['ident'],now)).rowcount
        if not claimed: return False
    finally: db.close()
    try: fetch(job['url'])
    except Exception as exc:
        code='SPACE_FULL' if isinstance(exc,OSError) and getattr(exc,'errno',None)==28 else 'FAILED'
        db=connect()
        try:
            with db: db.execute('UPDATE jobs SET status=?,attempts=attempts+1,next_at=?,updated=? WHERE ident=?',
                (code,now+min(1800,60*2**job['attempts']),now,job['ident']))
        finally: db.close()
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
    return dict(counts=counts,bytes=used(),budget=budget())


def retry():
    from artwork_db import reset_retry
    reset_retry()
    db=connect()
    try:
        with db: db.execute("UPDATE jobs SET attempts=0,next_at=0,status='PENDING' WHERE status!='READY'")
    finally: db.close()


def prefetch_selected():
    """One local page per service cycle; never enqueue disabled categories."""
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

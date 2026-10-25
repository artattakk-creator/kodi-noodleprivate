"""Durable artwork jobs/budget. Private URLs never enter diagnostics.

Completed files are never automatically evicted. A full budget pauses new work;
only an explicit user action retries failed jobs or removes a chosen file.
"""
import hashlib
import sqlite3
import time
import uuid

_ADOPTED=set()
_recovery_due={}
_served=0


def connect():
    from artwork_db import connect as open_jobs
    return open_jobs()


def budget():
    from art_storage import budget as configured
    return configured()


def key(url): return hashlib.sha256(url.encode()).hexdigest()


def enqueue(urls,priority=0):
    from artwork_config import persistent
    if not persistent():return
    from media_art import cached,_cached_at
    from artwork_backend import active_backend
    storage=active_backend();external=getattr(storage,'is_external',False) is True
    if external and storage.availability()!='AVAILABLE':
        from artwork_vfs import StorageFailure
        raise StorageFailure('STORAGE_OFFLINE')
    from import_budget import check_space
    # Persist small metadata under the import reserve. The full configured
    # image reserve remains enforced by fetch before HTTP and before writing.
    expected=sum(len(u) for u in urls)*3+65536
    from artwork_db import path
    check_space(path(),expected)
    db=connect()
    try:
        with db:
            for url in urls:
                if _cached_at(storage,key(url)) if external else cached(url):continue
                if external:
                    prior=db.execute('SELECT status FROM jobs WHERE ident=?',(key(url),)).fetchone()
                    if prior and prior[0]=='READY':continue  # Offline/missing external file never resets READY.
                db.execute('''INSERT INTO jobs VALUES(?,?,'PENDING',?,0,0,?,0)
                  ON CONFLICT(ident) DO UPDATE SET url=excluded.url,
                  priority=min(priority,excluded.priority),
                  status=CASE WHEN status='READY' THEN 'PENDING' ELSE status END
                  WHERE jobs.url!=excluded.url OR jobs.priority>excluded.priority OR jobs.status='READY' ''',
                    (key(url),url,priority,time.time()))
    finally: db.close()


def ready(url,size):
    db=connect()
    try:
        with db: db.execute("INSERT OR REPLACE INTO jobs VALUES(?,?,'READY',0,0,0,?,?)",(key(url),url,time.time(),size))
    finally: db.close()


def used():
    from artwork_backend import active_backend
    storage=active_backend();root=storage.resolve_target();db=connect()
    try:
        if root not in _ADOPTED:
            known={r[0] for r in db.execute('SELECT ident FROM jobs')}
            pending=[]
            for entry in storage.enumerate_for_migration():
                if entry['ident'] not in known:
                    pending.append((entry['ident'],time.time(),entry['bytes']))
            for start in range(0,len(pending),64):
                with db:db.executemany("INSERT OR IGNORE INTO jobs VALUES(?,'','READY',0,0,0,?,?)",pending[start:start+64])
            _ADOPTED.add(root)
        return db.execute('SELECT coalesce(sum(bytes),0) FROM jobs').fetchone()[0]
    finally: db.close()


def recover_space(now=None):
    """One bounded, durable opportunity per blocked job and policy. No deletes."""
    from art_storage import check,token,ArtworkFailure
    from artwork_db import path
    from media_art import MAX_BYTES
    now=time.time() if now is None else now
    filename=path()
    if now<_recovery_due.get(filename,0):return 0
    _recovery_due[filename]=now+5
    try:
        # Distinguish actual capacity from a configured cap before touching jobs.
        check(MAX_BYTES,limit=0)
        cap=budget()
        if cap and used()>=cap:return 0
    except (OSError,sqlite3.Error):return 0
    policy=token();db=connect()
    try:
        if not db.execute("SELECT 1 FROM jobs j LEFT JOIN art_recovery r ON r.ident=j.ident WHERE j.status IN ('SPACE_FULL','BUDGET_FULL','DISK_FULL') AND (r.policy IS NULL OR r.policy!=?) LIMIT 1",(policy,)).fetchone():return 0
        db.execute('BEGIN IMMEDIATE')
        rows=list(db.execute("""SELECT j.ident FROM jobs j LEFT JOIN art_recovery r ON r.ident=j.ident
          WHERE j.status IN ('SPACE_FULL','BUDGET_FULL','DISK_FULL') AND (r.policy IS NULL OR r.policy!=?)
          ORDER BY j.priority,j.updated LIMIT 32""",(policy,)))
        with db:
            for row in rows:
                db.execute('INSERT OR REPLACE INTO art_recovery VALUES(?,?)',(row['ident'],policy))
                db.execute("UPDATE jobs SET status='PENDING',attempts=0,next_at=0,updated=? WHERE ident=?",(now,row['ident']))
        return len(rows)
    finally:db.close()


def run_one(now=None):
    from artwork_config import persistent
    if not persistent():return False
    from artwork_migration import busy
    if busy():return False
    from artwork_backend import active_backend
    if active_backend().availability() not in ('AVAILABLE',):
        from art_diagnostics import publish
        publish('worker','STORAGE_OFFLINE');return False
    from media_art import fetch
    from utils import setting_bool
    if setting_bool('media_art_paused',False):return False
    global _served
    now=time.time() if now is None else now
    owner=uuid.uuid4().hex
    recover_space(now)
    db=connect()
    try:
        if db.execute('SELECT until FROM worker WHERE id=1').fetchone()[0]>now:return False
        # Storage blocks are only eligible via the bounded policy recovery above.
        from art_errors import CODES
        eligible=','.join("'"+c+"'" for c in CODES)
        order='updated,priority' if _served%8==7 else 'priority,updated'
        row=db.execute("SELECT * FROM jobs WHERE status IN ('PENDING','RUNNING','FAILED','NETWORK_ERROR','CACHE_ERROR',"+eligible+") AND attempts<3 AND next_at<=? ORDER BY "+order+" LIMIT 1",(now,)).fetchone()
        if not row:return False
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT until FROM worker WHERE id=1').fetchone()[0]>now:return False
        job=dict(row)
        with db:
            db.execute('UPDATE worker SET until=?,owner=? WHERE id=1',(now+30,owner))
            claimed=db.execute("UPDATE jobs SET next_at=?,status='RUNNING',updated=? WHERE ident=? AND status!='READY' AND attempts<3 AND next_at<=?",(now+30,now,job['ident'],now)).rowcount
        if not claimed:
            with db:db.execute("UPDATE worker SET until=0,owner='' WHERE id=1 AND owner=?",(owner,))
            return False
        _served+=1
    finally:db.close()
    try:fetch(job['url'])
    except sqlite3.Error:
        return False  # Existing file survives; lease expires; no network retry consumed.
    except Exception as exc:
        from art_storage import ArtworkFailure
        if isinstance(exc,ArtworkFailure):code=exc.code
        elif isinstance(exc,OSError) and getattr(exc,'errno',None)==28:code='DISK_FULL'
        elif isinstance(exc,OSError) and getattr(exc,'errno',None) in (13,30):code='CACHE_ERROR'
        else:code='NETWORK_ERROR'
        from art_errors import PERMANENT
        from artwork_gate import WriterBusy
        if code=='STORAGE_OFFLINE' or isinstance(exc,WriterBusy) or getattr(exc,'code','')=='MODE_CHANGED':
            return False  # Keep the leased row recoverable, no failure/reset wave.
        exhausted=code in PERMANENT or code in ('BUDGET_FULL','DISK_FULL')
        attempts=3 if exhausted else job['attempts']+1
        db=connect()
        try:
            with db:db.execute('UPDATE jobs SET status=?,attempts=?,next_at=?,updated=? WHERE ident=? AND EXISTS(SELECT 1 FROM worker WHERE id=1 AND owner=?)',
                (code,attempts,now+(getattr(exc,'retry_after',300) if code=='HTTP_RATE_LIMIT' else min(1800,60*2**min(job['attempts'],3))),now,job['ident'],owner))
        finally:db.close()
    finally:
        try:
            db=connect()
            try:
                with db:db.execute("UPDATE worker SET until=0,owner='' WHERE id=1 AND owner=?",(owner,))
            finally:db.close()
        except sqlite3.Error:pass
    return True


def status(cancel=lambda:False):
    from artwork_db import snapshot,diagnostic
    value=dict(budget=budget(),bytes=None,counts=None,code='UNAVAILABLE',health=diagnostic())
    from art_storage import reserve
    value['reserve']=reserve()
    from utils import setting_bool
    value['paused']=setting_bool('media_art_paused',False)
    # All waits happen in the status worker, at most one short retry. Never
    # reuse the writer connector or run file adoption from a status route.
    for attempt in range(2):
        value.update(snapshot(cancel))
        if value['code']!='BUSY' or attempt or cancel():break
        import xbmc
        if xbmc.Monitor().waitForAbort(.04):break
    try:
        from art_storage import capacity as read_capacity
        value.update(read_capacity())
    except OSError:value['capacity_code']='UNAVAILABLE'
    from art_diagnostics import augment
    value=augment(value,cancel)
    from artwork_config import read
    value['artwork_mode']=read()['mode']
    if value['artwork_mode']=='dynamic':value['storage_result']='DYNAMIC_NO_XCMATE_ARCHIVE'
    return value


def retry():
    from artwork_db import reset_retry
    reset_retry()
    db=connect()
    try:
        with db:
            db.execute("UPDATE jobs SET attempts=0,next_at=0,status='PENDING' WHERE status!='READY'")
            db.execute("UPDATE art_recovery SET policy=''")
    finally: db.close()


def prefetch_selected():
    """One local page per service cycle; never enqueue disabled categories."""
    from artwork_config import read
    config=read()
    if config['mode']=='dynamic':return
    if config['version'] and config.get('strategy','demand')!='all' and config.get('origin')!='LEGACY':return
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
            revision=state['revision']+str([g['cid'] for g in reader.groups(kind)])+str(config.get('preload_generation',''))
            db=connect()
            try: prior=db.execute('SELECT revision,offset FROM scan WHERE pid=? AND kind=?',(portal['id'],kind)).fetchone()
            finally: db.close()
            acknowledged=revision+'|persisted36'
            if prior and prior['revision'] in (revision,acknowledged):
                offset=prior['offset']
                if offset<0:
                    # Older scans advanced after an in-memory request, before
                    # enrolment committed. Recover once ONLY when the durable
                    # queue is empty; never reset existing failed/READY jobs.
                    if prior['revision']==acknowledged:continue
                    db=connect()
                    try:has_jobs=db.execute('SELECT 1 FROM jobs LIMIT 1').fetchone()
                    finally:db.close()
                    if has_jobs:continue
                    offset=0
            else:offset=0
            rows,total=reader.page(kind,offset=offset,limit=48)
            from media_art import valid_source
            from art_diagnostics import sources as observe_sources
            observe_sources(rows,valid_source)
            urls=list(dict.fromkeys(url for row in rows for url in sources(row) if url))
            # This caller already runs on the service's data worker. Advance
            # only after the persistent transaction has acknowledged this page.
            from art_diagnostics import publish,enrol_failure
            try:enqueue(urls,priority=20)
            except (OSError,RuntimeError,sqlite3.Error) as error:
                enrol_failure(error);raise
            publish('enrol','ENQUEUED',items=len(urls))
            db=connect()
            try:
                with db: db.execute('INSERT OR REPLACE INTO scan VALUES(?,?,?,?)',(portal['id'],kind,acknowledged,offset+len(rows) if rows and offset+len(rows)<total else -1))
            finally: db.close()


def retry_one(url,now=None):
    """Only this URL; durable 60 s user-action limit and server cooldown."""
    from media_art import cached,valid_source
    if not valid_source(url):return 'INVALID_SOURCE'
    if cached(url):return 'READY'
    now=time.time() if now is None else now
    db=connect()
    try:
        db.execute('CREATE TABLE IF NOT EXISTS art_retry_limits(ident TEXT PRIMARY KEY,next_at REAL)')
        db.execute('BEGIN IMMEDIATE')
        job=db.execute('SELECT status,next_at FROM jobs WHERE ident=?',(key(url),)).fetchone()
        if job and job['status']=='READY' and cached(url):return 'READY'
        if job and job['status']=='RUNNING' and job['next_at']>now:return 'RUNNING'
        if job and job['status']=='HTTP_RATE_LIMIT' and job['next_at']>now:return 'WAIT'
        prior=db.execute('SELECT next_at FROM art_retry_limits WHERE ident=?',(key(url),)).fetchone()
        if prior and prior[0]>now:return 'WAIT'
        with db:
            db.execute('INSERT OR REPLACE INTO art_retry_limits VALUES(?,?)',(key(url),now+60))
            if job:db.execute("UPDATE jobs SET status='PENDING',attempts=0,next_at=0,priority=-20,updated=? WHERE ident=?",(now,key(url)))
    finally:db.close()
    if not job:enqueue([url],-20)
    return 'PENDING'

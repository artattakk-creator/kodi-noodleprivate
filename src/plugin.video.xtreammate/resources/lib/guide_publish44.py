"""Conservative additive EPG publisher; never replace a sparse feed's envelope.

All records from a source keep their stable source identity. Published legacy
rows remain the last good baseline; non-exact conflicts retain that baseline
instead of cutting programmes or silently dropping coverage. No schema change
on an existing populated guide without the explicit verified-backup action.
"""
import hashlib,json,os,sqlite3,time

class BackupRequired(RuntimeError):
    code='BACKUP_REQUIRED'


def ready(db):
    return db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='guide44_inputs'").fetchone() is not None


def initialize(db):
    # Only a new empty guide or an explicitly backed-up legacy copy may call.
    schema='''CREATE TABLE IF NOT EXISTS guide44_inputs(
      pid TEXT,source_id TEXT,cid TEXT,start INTEGER,stop INTEGER,title TEXT,
      description TEXT,rank INTEGER,PRIMARY KEY(pid,source_id,cid,start,stop));
      CREATE INDEX IF NOT EXISTS guide44_source_time ON guide44_inputs(pid,source_id,cid,start);
      CREATE TABLE IF NOT EXISTS guide44_outcomes(pid TEXT PRIMARY KEY,code TEXT,payload TEXT);
      CREATE TABLE IF NOT EXISTS guide44_authorization(kind TEXT,backup_sha TEXT,created REAL);
      CREATE TABLE IF NOT EXISTS guide44_ranges(pid TEXT,cid TEXT,start INTEGER,stop INTEGER,PRIMARY KEY(pid,cid,start));'''
    for statement in schema.split(';'):
        if statement.strip():db.execute(statement)


def require(db):
    if not ready(db):raise BackupRequired('BACKUP_REQUIRED')


def source_id(source,index):
    if index==0:return 'provider'
    ident=source.get('id') or source.get('uri')
    # Legacy synthetic adapters may omit an ID; never store raw source URI.
    return 'external:'+hashlib.sha256(str(ident or 'legacy-index-'+str(index)).encode()).hexdigest()[:24]


def publish(db,pid,table,where='',args=(),*,source='compatibility',rank=None,revision='',now=None,cancel=lambda:False):
    """Caller owns one transaction, including revision and aliases.

    'table' and SQL clause are internal constants, never source input. Preserve
    every published interval on partial/empty/conflicting input. Exact interval
    corrections need equal/higher priority, compatibility caches only fill gaps.
    """
    require(db);now=time.time() if now is None else now
    if table not in ('incoming','xml_stage'):raise ValueError('INVALID_STAGE')
    selector=(' WHERE '+where) if where else ' WHERE 1=1'
    condition=(' AND '+where) if where else ''
    count=db.execute('SELECT count(*) FROM '+table+selector,args).fetchone()[0]
    if not count:return dict(code='NO_NEW_GUIDE',incoming=0,added=0,corrected=0,conflicts=0)
    compatibility=rank is None
    # Raw per-source records survive source reordering and equal channel IDs.
    # No destructive historical/source-retention operation is part of .44.
    db.execute('''INSERT INTO guide44_inputs SELECT ?,?,cid,start,stop,title,description,'''+('source' if compatibility else '?')+' FROM '+table+selector+'''
      ON CONFLICT(pid,source_id,cid,start,stop) DO UPDATE SET
      title=excluded.title,description=excluded.description,rank=excluded.rank''',
      [pid,source]+([] if compatibility else [rank])+list(args))
    if db.execute('SELECT count(*) FROM guide44_inputs WHERE pid=?',(pid,)).fetchone()[0]>2000000:
        raise ValueError('GUIDE_SOURCE_BUDGET')
    if cancel():raise InterruptedError('CANCELLED')
    # Rebuild only the private coverage index, not the published guide. A
    # disjoint union permits logarithmic overlap lookups even for 160k events
    # on one channel; a naive two-end SQL inequality becomes quadratic.
    db.execute('DELETE FROM guide44_ranges WHERE pid=?',(pid,))
    previous=None
    for cid,start,stop in db.execute('SELECT cid,start,stop FROM programmes WHERE pid=? ORDER BY cid,start,stop',(pid,)):
        if previous and cid==previous[0] and start<=previous[2]:
            previous=(cid,previous[1],max(previous[2],stop))
        else:
            if previous:db.execute('INSERT INTO guide44_ranges VALUES(?,?,?,?)',(pid,*previous))
            previous=(cid,start,stop)
    if previous:db.execute('INSERT INTO guide44_ranges VALUES(?,?,?,?)',(pid,*previous))
    added=corrected=conflicts=0
    query='SELECT cid,start,stop,title,description,'+('source' if compatibility else '?')+' FROM '+table+selector+' ORDER BY cid,start,stop'
    for n,row in enumerate(db.execute(query,([] if compatibility else [rank])+list(args))):
        if n%256==0 and cancel():raise InterruptedError('CANCELLED')
        cid,start,stop,title,description,priority=row
        exact=db.execute('SELECT source,title,description FROM programmes WHERE pid=? AND cid=? AND start=? AND stop=?',(pid,cid,start,stop)).fetchone()
        if exact:
            if not compatibility and priority<=exact[0] and (title,description,priority)!=(exact[1],exact[2],exact[0]):
                db.execute('UPDATE programmes SET title=?,description=?,source=? WHERE pid=? AND cid=? AND start=? AND stop=?',(title,description,priority,pid,cid,start,stop));corrected+=1
            continue
        before=db.execute('SELECT start,stop FROM guide44_ranges WHERE pid=? AND cid=? AND start<=? ORDER BY start DESC LIMIT 1',(pid,cid,start)).fetchone()
        following=db.execute('SELECT start,stop FROM guide44_ranges WHERE pid=? AND cid=? AND start>? ORDER BY start LIMIT 1',(pid,cid,start)).fetchone()
        if before and before[1]>start or following and following[0]<stop:
            conflicts+=1;continue
        db.execute('INSERT INTO programmes VALUES(?,?,?,?,?,?,?)',(pid,cid,start,stop,title,description,priority));added+=1
        left=before[0] if before and before[1]==start else start
        right=following[1] if following and following[0]==stop else stop
        if before and before[1]==start:db.execute('DELETE FROM guide44_ranges WHERE pid=? AND cid=? AND start=?',(pid,cid,before[0]))
        if following and following[0]==stop:db.execute('DELETE FROM guide44_ranges WHERE pid=? AND cid=? AND start=?',(pid,cid,following[0]))
        db.execute('INSERT INTO guide44_ranges VALUES(?,?,?,?)',(pid,cid,left,right))
    if cancel():raise InterruptedError('CANCELLED')
    code='PARTIAL_PRESERVED' if conflicts else 'VERIFIED' if added or corrected else 'UNCHANGED'
    if added or corrected:
        db.execute('INSERT OR REPLACE INTO guide_meta VALUES(?,?,?)',(pid,revision or 'guide44-'+str(time.time_ns()),now))
    fields=dict(incoming=count,added=added,corrected=corrected,conflicts=conflicts)
    db.execute('INSERT OR REPLACE INTO guide44_outcomes VALUES(?,?,?)',(pid,code,json.dumps(fields)))
    return dict(code=code,**fields)


def diagnose(filename,pid):
    """Read-only counts/coverage by source rank/day, no names, IDs or URLs."""
    from urllib.parse import quote
    if not os.path.isfile(filename):return dict(code='NOT_CREATED')
    db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.2)
    try:
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        meta=db.execute('SELECT revision,updated FROM guide_meta WHERE pid=?',(pid,)).fetchone()
        rows=db.execute("SELECT source,date(start,'unixepoch'),count(*),min(start),max(stop) FROM programmes WHERE pid=? GROUP BY source,date(start,'unixepoch')",(pid,)).fetchall()
        return dict(code='READY' if ready(db) else 'BACKUP_REQUIRED',revision=hashlib.sha256(str(meta).encode()).hexdigest()[:16],
                    groups=[dict(source_rank=r[0],utc_day=r[1],events=r[2],first=r[3],last=r[4]) for r in rows],events=sum(r[2] for r in rows))
    finally:db.close()


def history_days(pid,filename,now=None):
    """Actual local calendar coverage, seven bounded read-only existence queries."""
    if not os.path.isfile(filename):return None
    from guide_store import day_window
    from urllib.parse import quote
    db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
    try:
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        deadline=time.monotonic()+.15;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        days=[]
        for day in range(-7,0):
            start,stop=day_window(day,now)
            if db.execute('SELECT 1 FROM programmes WHERE pid=? AND start<? AND stop>? LIMIT 1',(pid,stop,start)).fetchone():days.append(day)
        return days
    except sqlite3.Error:return None  # Unknown is not a false empty history.
    finally:db.close()


def access(filename):
    """Cheap read-only gate, no coverage scan in a user-action callback."""
    if not os.path.isfile(filename):return 'NOT_CREATED'
    from urllib.parse import quote
    db=None
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
        db.execute('PRAGMA query_only=ON')
        return 'READY' if ready(db) else 'BACKUP_REQUIRED'
    except sqlite3.Error as exc:
        return 'GUIDE_BUSY' if isinstance(exc,sqlite3.OperationalError) else 'GUIDE_UNAVAILABLE'
    finally:
        if db is not None:db.close()

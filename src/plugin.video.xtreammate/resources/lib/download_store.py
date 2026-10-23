"""Private ID-only download queue. Each worker owns its SQLite connection."""
import hashlib,json,os,sqlite3,time,uuid

FIELDS=('pid','kind','sid','series_id','season','episode','title','series_title','year','duration','poster','target')
STATES=frozenset(('QUEUED','RUNNING','PAUSED','COMPLETE','FAILED','CANCELLED','PUBLISHING','TRANSFERRING'))


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'downloads_v1.sqlite')


def db():
    connection=sqlite3.connect(path(),timeout=.25);connection.row_factory=sqlite3.Row
    os.chmod(path(),0o600)
    connection.execute('PRAGMA journal_mode=WAL')
    connection.executescript('''CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,payload TEXT NOT NULL,
      state TEXT NOT NULL,code TEXT NOT NULL DEFAULT '',bytes INTEGER NOT NULL DEFAULT 0,total INTEGER NOT NULL DEFAULT 0,
      speed REAL NOT NULL DEFAULT 0,part TEXT NOT NULL DEFAULT '',file TEXT NOT NULL DEFAULT '',etag TEXT NOT NULL DEFAULT '',
      modified TEXT NOT NULL DEFAULT '',fingerprint TEXT NOT NULL DEFAULT '',digest TEXT NOT NULL DEFAULT '',
      attempts INTEGER NOT NULL DEFAULT 0,next_at REAL NOT NULL DEFAULT 0,retry_at REAL NOT NULL DEFAULT 0,
      owner TEXT NOT NULL DEFAULT '',lease REAL NOT NULL DEFAULT 0,updated REAL NOT NULL,hidden INTEGER NOT NULL DEFAULT 0);
      CREATE TABLE IF NOT EXISTS worker(id INTEGER PRIMARY KEY,owner TEXT,lease REAL);
      INSERT OR IGNORE INTO worker VALUES(1,'',0);''')
    if 'copy_bytes' not in {row[1] for row in connection.execute('PRAGMA table_info(jobs)')}:
        try:connection.execute('ALTER TABLE jobs ADD COLUMN copy_bytes INTEGER NOT NULL DEFAULT 0')
        except sqlite3.OperationalError:
            if 'copy_bytes' not in {row[1] for row in connection.execute('PRAGMA table_info(jobs)')}:raise
    return connection


def decode(row):
    value=dict(row);value['media']=json.loads(value.pop('payload'));return value


def snapshot():
    if not os.path.isfile(path()):return []
    from urllib.parse import quote
    conn=sqlite3.connect('file:'+quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.05);conn.row_factory=sqlite3.Row
    try:return [decode(row) for row in conn.execute('SELECT * FROM jobs WHERE hidden=0 ORDER BY updated DESC LIMIT 1000')]
    finally:conn.close()


def get(ident):
    conn=db()
    try:
        row=conn.execute('SELECT * FROM jobs WHERE id=?',(ident,)).fetchone();return decode(row) if row else None
    finally:conn.close()


def enqueue(media):
    if media.get('kind') not in ('vod','episode','series_item') or not all(str(media.get(k) or '') for k in ('pid','sid','target')):raise ValueError('media identity')
    if media['kind']=='episode' and not all(str(media.get(k) or '').isdigit() for k in ('season','episode')):raise ValueError('episode identity')
    ident=hashlib.sha256(json.dumps([str(media.get(k,'')) for k in ('pid','kind','sid','series_id','season')]).encode()).hexdigest()
    if any(len(str(media.get(k,'')))>128 for k in ('pid','sid','series_id')) or len(str(media['target']))>4096:raise ValueError('identity length')
    if media['kind']=='episode' and (len(str(media['season']))>4 or len(str(media['episode']))>5):raise ValueError('episode numbers')
    value={k:str(media.get(k,''))[:4096 if k=='target' else 1024] for k in FIELDS};conn=db()
    try:
        with conn:
            if conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]>=1000 and not conn.execute('SELECT 1 FROM jobs WHERE id=?',(ident,)).fetchone():raise ValueError('queue limit')
            conn.execute("INSERT OR IGNORE INTO jobs(id,payload,state,updated) VALUES(?,?,'QUEUED',?)",(ident,json.dumps(value),time.time()))
            conn.execute('UPDATE jobs SET hidden=0 WHERE id=?',(ident,))
    finally:conn.close()
    return ident


def claim(now=None):
    now=time.time() if now is None else now;owner=uuid.uuid4().hex;conn=db()
    try:
        conn.execute('BEGIN IMMEDIATE')
        # A disappeared worker does not cause uncontrolled automatic restarts.
        conn.execute("UPDATE jobs SET state='PAUSED',code='INTERRUPTED',owner='',speed=0 WHERE state IN ('RUNNING','PUBLISHING','TRANSFERRING') AND lease<=?",(now,))
        if conn.execute('SELECT lease FROM worker WHERE id=1').fetchone()[0]>now:conn.rollback();return None
        row=conn.execute("SELECT * FROM jobs WHERE state='QUEUED' AND next_at<=? ORDER BY updated LIMIT 1",(now,)).fetchone()
        if row is None:conn.commit();return None
        conn.execute("UPDATE jobs SET state='RUNNING',owner=?,lease=?,attempts=attempts+1,code='' WHERE id=?",(owner,now+30,row['id']))
        conn.execute('UPDATE worker SET owner=?,lease=? WHERE id=1',(owner,now+30));conn.commit()
        value=decode(row);value.update(owner=owner,state='RUNNING',attempts=value['attempts']+1);return value
    finally:conn.close()


def checkpoint(ident,owner,**values):
    allowed={'bytes','total','speed','part','file','etag','modified','fingerprint','digest','copy_bytes'}
    if set(values)-allowed:raise ValueError('checkpoint fields')
    now=time.time();conn=db()
    try:
        with conn:
            changed=conn.execute('UPDATE jobs SET '+','.join(k+'=?' for k in values)+',updated=?,lease=? WHERE id=? AND owner=?',(*values.values(),now,now+30,ident,owner)).rowcount
            if changed:conn.execute('UPDATE worker SET lease=? WHERE id=1 AND owner=?',(now+30,owner))
            row=conn.execute('SELECT state FROM jobs WHERE id=? AND owner=?',(ident,owner)).fetchone()
        return row[0] if row else 'CANCELLED'
    finally:conn.close()


def finish(ident,owner,state,code=''):
    if state not in STATES:raise ValueError('state')
    conn=db()
    try:
        with conn:
            row=conn.execute('SELECT state FROM jobs WHERE id=? AND owner=?',(ident,owner)).fetchone()
            if row and row[0] in ('RUNNING','PUBLISHING','TRANSFERRING'):
                conn.execute('UPDATE jobs SET state=?,code=?,speed=0,owner=\'\',lease=0,updated=? WHERE id=? AND owner=?',(state,code,time.time(),ident,owner))
            if row and row[0] in ('PAUSED','CANCELLED'):conn.execute("UPDATE jobs SET owner='',lease=0,speed=0 WHERE id=? AND owner=?",(ident,owner))
            conn.execute("UPDATE worker SET lease=0,owner='' WHERE id=1 AND owner=?",(owner,))
    finally:conn.close()


def fail(ident,owner,code,transient=False):
    row=get(ident);conn=db()
    try:
        with conn:
            if row and row['owner']==owner and row['state'] in ('RUNNING','PUBLISHING','TRANSFERRING'):
                retry=transient and row['attempts']<3
                conn.execute("UPDATE jobs SET state=?,code=?,next_at=?,speed=0,owner='',lease=0,updated=? WHERE id=? AND owner=?",('QUEUED' if retry else 'FAILED',code,time.time()+30*2**row['attempts'],time.time(),ident,owner))
            conn.execute("UPDATE worker SET lease=0,owner='' WHERE id=1 AND owner=?",(owner,))
    finally:conn.close()


def command(ident,action,now=None):
    now=time.time() if now is None else now;conn=db()
    try:
        conn.execute('BEGIN IMMEDIATE');row=conn.execute('SELECT * FROM jobs WHERE id=?',(ident,)).fetchone()
        if row is None:conn.rollback();return False
        state=row['state']
        if action=='pause' and state in ('QUEUED','RUNNING','TRANSFERRING'):conn.execute("UPDATE jobs SET state='PAUSED',speed=0 WHERE id=?",(ident,))
        elif action=='cancel' and state in ('QUEUED','RUNNING','TRANSFERRING','PAUSED','FAILED'):conn.execute("UPDATE jobs SET state='CANCELLED',speed=0 WHERE id=?",(ident,))
        elif action in ('resume','retry') and state in ('PAUSED','FAILED','CANCELLED'):
            if row['lease']>now or (state!='PAUSED' and row['retry_at']>now):conn.rollback();return False
            conn.execute("UPDATE jobs SET state='QUEUED',attempts=0,next_at=0,retry_at=?,hidden=0,updated=? WHERE id=?",(now+60,now,ident))
        elif action=='hide' and state in ('COMPLETE','FAILED','CANCELLED'):conn.execute('UPDATE jobs SET hidden=1 WHERE id=?',(ident,))
        else:conn.rollback();return False
        conn.commit();return True
    finally:conn.close()

"""Portal/source-bound private grants. Never store media paths, queries or headers."""
import os,sqlite3,time


def connect():
    from utils import addon_data_dir
    path=os.path.join(addon_data_dir(),'download_trust_v1.sqlite')
    db=sqlite3.connect(path,timeout=.25);db.row_factory=sqlite3.Row;os.chmod(path,0o600)
    db.executescript('''CREATE TABLE IF NOT EXISTS grants(pid TEXT,source TEXT,target TEXT,lan INTEGER,
      PRIMARY KEY(pid,source,target));
      CREATE TABLE IF NOT EXISTS pending(job TEXT PRIMARY KEY,pid TEXT,source TEXT,target TEXT,updated REAL);''')
    return db


def allowed(pid,source,target,lan=False):
    if not pid:return False
    db=connect()
    try:
        row=db.execute('SELECT lan FROM grants WHERE pid=? AND source=? AND target=?',(str(pid),source,target)).fetchone()
        return row is not None and (not lan or row['lan']==1)
    finally:db.close()


def remember(job,pid,source,target):
    if not job or not pid:return
    db=connect()
    try:
        with db:
            db.execute('DELETE FROM pending WHERE updated<?',(time.time()-86400,))
            db.execute('INSERT OR REPLACE INTO pending VALUES(?,?,?,?,?)',(job,str(pid),source,target,time.time()))
    finally:db.close()


def pending(job,pid):
    db=connect()
    try:
        row=db.execute('SELECT * FROM pending WHERE job=? AND pid=? AND updated>?',(job,str(pid),time.time()-86400)).fetchone()
        return dict(row) if row else None
    finally:db.close()


def grant(value,lan=False):
    from download_redirect import origin
    # Accept origins only, never a URL path, userinfo, fragment or query.
    for key in ('source','target'):
        if origin(value[key])!=value[key]:raise ValueError('INVALID_ORIGIN')
    db=connect()
    try:
        with db:db.execute('INSERT OR REPLACE INTO grants VALUES(?,?,?,?)',(str(value['pid']),value['source'],value['target'],int(bool(lan))))
    finally:db.close()


def grants(pid):
    db=connect()
    try:return [dict(row) for row in db.execute('SELECT * FROM grants WHERE pid=? ORDER BY target',(str(pid),))]
    finally:db.close()


def revoke(value):
    db=connect()
    try:
        with db:db.execute('DELETE FROM grants WHERE pid=? AND source=? AND target=?',(str(value['pid']),value['source'],value['target']))
    finally:db.close()

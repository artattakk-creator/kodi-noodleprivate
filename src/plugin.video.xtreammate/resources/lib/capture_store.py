"""Private manual-capture commands; no stream URLs, no existing data migration."""
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager

ACTIVE=('pending','recording','starting')


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'manual_capture_v1.sqlite')


@contextmanager
def connect():
    filename=path();db=sqlite3.connect(filename,timeout=.15);db.row_factory=sqlite3.Row
    try:
        os.chmod(filename,0o600)
        db.execute('CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,pid TEXT,sid TEXT,label TEXT,target TEXT,status TEXT,duration INTEGER,bytes INTEGER,seconds REAL,code TEXT,file TEXT,stop INTEGER,created REAL,updated REAL)')
        yield db
    finally:db.close()


def add(portal,channel,target,duration):
    if not 1<=int(duration)<=21600:raise ValueError('INVALID_DURATION')
    if not os.path.isabs(target) or '://' in target:raise ValueError('UNSUPPORTED_TARGET')
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        if db.execute("SELECT 1 FROM jobs WHERE status IN ('pending','recording','starting')").fetchone():raise ValueError('RECORDING_BUSY')
        ident=uuid.uuid4().hex;now=time.time()
        with db:db.execute("INSERT INTO jobs VALUES(?,?,?,?,?,'pending',?,0,0,'','',0,?,?)",
            (ident,str(portal['id']),str(channel['sid']),str(channel.get('name',''))[:512],target,int(duration),now,now))
    return ident


def rows():
    if not os.path.exists(path()):return []
    with connect() as db:return [dict(r) for r in db.execute('SELECT * FROM jobs ORDER BY created DESC LIMIT 100')]


def update(ident,**values):
    allowed={'status','bytes','seconds','code','file'}
    if not values or not set(values).issubset(allowed):raise ValueError('INVALID_UPDATE')
    with connect() as db:
        with db:db.execute('UPDATE jobs SET '+','.join(k+'=?' for k in values)+',updated=? WHERE id=?',[*values.values(),time.time(),ident])


def finish(ident):
    with connect() as db:
        with db:db.execute("UPDATE jobs SET stop=1,updated=? WHERE id=? AND status IN ('pending','starting','recording')",(time.time(),ident))


def interrupted():
    if not os.path.exists(path()):return
    with connect() as db:
        with db:db.execute("UPDATE jobs SET status='partial',code='SERVICE_INTERRUPTED',updated=? WHERE status IN ('starting','recording')",(time.time(),))

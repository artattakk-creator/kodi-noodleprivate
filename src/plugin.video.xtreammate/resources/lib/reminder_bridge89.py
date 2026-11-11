"""Recoverable bookmark/timer transaction on the EXISTING timer database.

The intent commits before either file changes. Recovery applies the same
idempotent desired state, preserving all unrelated bookmarks and timer rows.
"""
import hashlib,json,os,sqlite3,time,tempfile
from pathlib import Path

def init(conn):
 if conn.execute("SELECT 1 FROM sqlite_master WHERE name='bookmark_intents89'").fetchone():return
 from utils import addon_data_dir
 root=Path(addon_data_dir());target=root/'guide_timers_v1.sqlite.before89.bak'
 if target.is_symlink():raise OSError('TIMER_BACKUP_UNSAFE')
 if conn.execute('SELECT count(*) FROM timers').fetchone()[0] and not target.exists():
  from import_budget import check_space
  check_space(str(target),max(65536,(root/'guide_timers_v1.sqlite').stat().st_size*2))
  fd,tmp=tempfile.mkstemp(prefix='.timers89-backup-',dir=root);os.close(fd)
  try:
   backup=sqlite3.connect(tmp)
   try:
    conn.backup(backup)
    if backup.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise OSError('TIMER_BACKUP_READBACK')
   finally:backup.close()
   if target.is_symlink():raise OSError('TIMER_BACKUP_UNSAFE')
   with open(tmp,'rb') as stable:os.fsync(stable.fileno())
   os.replace(tmp,target)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
 conn.executescript('''CREATE TABLE IF NOT EXISTS bookmark_intents89(id TEXT PRIMARY KEY,payload TEXT);
 CREATE TABLE IF NOT EXISTS alarm_dispatch89(slot INTEGER PRIMARY KEY,id TEXT,nonce TEXT,state TEXT,at REAL);
 CREATE TABLE IF NOT EXISTS legacy_reminders89(id TEXT PRIMARY KEY,state TEXT);''')
 conn.commit()

def bookmarks():
 from utils import addon_data_dir
 path=Path(addon_data_dir())/'guide_bookmarks_v1.json'
 if path.is_symlink() or path.exists() and path.stat().st_size>1024*1024:raise OSError('BOOKMARK_UNSAFE')
 try:value=json.loads(path.read_bytes())
 except FileNotFoundError:value={}
 if not isinstance(value,dict):raise ValueError('BOOKMARK_SCHEMA')
 return path,value

def apply(conn,ident,intent):
 from logo_store89 import atomic
 from import_budget import check_space
 path,values=bookmarks();event=intent['event'];wanted=intent['wanted']
 if wanted:values[ident]=dict(event)
 else:values.pop(ident,None)
 raw=json.dumps(values,ensure_ascii=False,separators=(',',':')).encode()
 if len(raw)>1024*1024:raise OSError('BOOKMARK_LIMIT')
 check_space(str(path),len(raw)+65536);atomic(path,raw)
 if path.read_bytes()!=raw:raise OSError('BOOKMARK_READBACK')
 with conn:
  if wanted and event['start']>time.time():
   conn.execute('''INSERT INTO timers VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
     channel=excluded.channel,title=excluded.title,notify_at=CASE WHEN timers.state IN ('cancelled','dismissed','missed') THEN excluded.notify_at ELSE timers.notify_at END,
     state=CASE WHEN timers.state IN ('cancelled','dismissed','missed') THEN 'pending' ELSE timers.state END''',
    (ident,event['pid'],event['sid'],intent['channel'],event['title'],event['start'],event['stop'],event['start']-300,'pending'))
  elif not wanted:conn.execute("UPDATE timers SET state='cancelled' WHERE id=? AND state IN ('pending','notified')",(ident,))
 # A separate connection must see the committed state before the recoverable
 # intent can be removed. Reading our own uncommitted transaction is no proof.
 from guide_timers import db
 cold=db()
 try:
  row=cold.execute('SELECT pid,sid,start,stop,state FROM timers WHERE id=?',(ident,)).fetchone()
  if wanted and event['start']>time.time():
   if not row or list(row)[:4]!=[event[k] for k in ('pid','sid','start','stop')]:raise OSError('TIMER_READBACK')
  elif not wanted and row and row['state'] in ('pending','notified'):raise OSError('TIMER_CANCEL_READBACK')
 finally:cold.close()
 with conn:conn.execute('DELETE FROM bookmark_intents89 WHERE id=?',(ident,))

def recover(conn):
 from profile_transaction import writing
 with writing(timeout=.2):
  init(conn)
  for row in conn.execute('SELECT id,payload FROM bookmark_intents89 LIMIT 64').fetchall():apply(conn,row[0],json.loads(row[1]))

def toggle(event,cancel=lambda:False,wanted=None):
 from programme_actions88 import bookmark_id,_toggle88
 from profile_transaction import writing
 from guide_timers import db
 clean={k:event[k] for k in ('pid','sid','title','start','stop')};clean.update(pid=str(clean['pid']),sid=str(clean['sid']),title=str(clean['title'])[:512],start=int(clean['start']),stop=int(clean['stop']))
 if not clean['sid'] or not 0<clean['start']<clean['stop']:raise ValueError('BOOKMARK_INVALID')
 from station_rows88 import header
 if header(dict(sid=clean['sid'],name='')):raise ValueError('CHANNEL_UNAVAILABLE')
 # Current/past programmes remain plain bookmarks; do not invent a late timer.
 from utils import addon_data_dir
 if clean['start']<=time.time() and not (Path(addon_data_dir())/'guide_timers_v1.sqlite').exists() and wanted is None:return _toggle88(event,cancel)
 with writing(timeout=.2):
  if cancel():raise InterruptedError('CANCELLED')
  conn=db()
  try:
   recover(conn);path,values=bookmarks();ident=bookmark_id(clean);added=ident not in values if wanted is None else bool(wanted)
   channel=str(event.get('channel') or '')[:160]
   if added and clean['start']>time.time():
    from portals import get_by_id
    from library_index import Reader
    portal=get_by_id(clean['pid']);row=Reader(clean['pid'],timeout=.15,query_seconds=.3).get('live',clean['sid']) if portal and portal.get('enabled',True) else None
    if not row or header(row):raise ValueError('CHANNEL_UNAVAILABLE')
    channel=str(row.get('name') or '')[:160]
   intent=dict(event=clean,wanted=added,channel=channel)
   with conn:conn.execute('INSERT OR REPLACE INTO bookmark_intents89 VALUES(?,?)',(ident,json.dumps(intent,separators=(',',':'))))
   if cancel():
    with conn:conn.execute('DELETE FROM bookmark_intents89 WHERE id=?',(ident,))
    raise InterruptedError('CANCELLED')
   apply(conn,ident,intent);return added
  finally:conn.close()

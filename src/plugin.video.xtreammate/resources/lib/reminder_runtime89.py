"""One shared durable alarm engine; existing workers produce, owner GUI consumes."""
import hashlib,json,threading,time,uuid
from urllib.parse import urlencode
_guard=threading.Lock();_next=0;_legacy_stamp=None
PREFIX='XCMate.Reminder89.'
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def read(name):
 try:
  raw=window().getProperty(PREFIX+name);value=json.loads(raw) if raw and len(raw)<8192 else {}
  return value if isinstance(value,dict) else {}
 except (ValueError,TypeError):return {}
def put(name,value):window().setProperty(PREFIX+name,json.dumps(value,separators=(',',':')))

def channel(row):
 from portals import get_by_id
 from library_index import Reader
 from station_rows88 import header
 portal=get_by_id(str(row['pid']))
 if not portal or not portal.get('enabled',True) or portal.get('type') not in ('xtream','m3u','stb'):return None,None
 item=Reader(portal['id'],timeout=.15,query_seconds=.3).get('live',str(row['sid']))
 return (portal,item) if item and not header(item) else (None,None)

def legacy(conn):
 """Keep the legacy file unchanged. Ambiguous identities never auto-tune."""
 global _legacy_stamp
 from utils import addon_data_dir
 from pathlib import Path
 path=Path(addon_data_dir())/'reminders.json'
 try:
  stat=path.stat();stamp=(str(path),stat.st_mtime_ns,stat.st_size)
  if stamp==_legacy_stamp or stat.st_size>1024*1024 or path.is_symlink():return
  rows=json.loads(path.read_bytes())
  if not isinstance(rows,list):return
  from portals import get_active
  from library_index import Reader
  from programme_actions88 import bookmark_id
  for old in rows[:256]:
   if not isinstance(old,dict) or not old.get('channel') or not old.get('title'):continue
   tag=hashlib.sha256(json.dumps(old,sort_keys=True).encode()).hexdigest()
   if conn.execute('SELECT 1 FROM legacy_reminders89 WHERE id=?',(tag,)).fetchone():continue
   found=[]
   for portal in get_active()[:4]:
    candidates=Reader(portal['id'],timeout=.1,query_seconds=.2).page('live',str(old['channel']),limit=32)[0]
    for item in candidates:
     if item.get('name')==old['channel'] and legacy_identity(old,portal,item):found.append((str(portal['id']),str(item['sid'])))
   if len(found)!=1:continue
   pid,sid=found[0];start,stop=int(old['start']),int(old['stop'])
   if not 0<start<stop:continue
   event=dict(pid=pid,sid=sid,start=start,stop=stop,title=str(old['title'])[:512]);ident=bookmark_id(event)
   with conn:
    conn.execute('INSERT OR IGNORE INTO timers VALUES(?,?,?,?,?,?,?,?,?)',(ident,pid,sid,str(old['channel'])[:160],event['title'],start,stop,int(old.get('notify_at',start-300)),'notified' if old.get('notified') else 'pending'))
    conn.execute('INSERT OR IGNORE INTO legacy_reminders89 VALUES(?,?)',(tag,'IMPORTED:'+ident))
  _legacy_stamp=stamp
 except (OSError,ValueError,TypeError,KeyError):return

def worker(now=None):
 global _next
 if not _guard.acquire(False):return
 conn=None
 try:
  ready=read('Ready');choice=read('Choice')
  if choice and choice.get('nonce')!=ready.get('nonce'):window().clearProperty(PREFIX+'Choice');choice={}
  if now is None and time.monotonic()<_next and not choice:return
  _next=time.monotonic()+1;now=int(time.time() if now is None else now)
  from guide_timers import db
  from reminder_bridge89 import recover
  from profile_transaction import writing
  with writing(timeout=.2):
   conn=db();recover(conn);legacy(conn)
   if choice and ready.get('nonce')==choice.get('nonce'):
    row=conn.execute("SELECT * FROM timers WHERE id=? AND state='notified'",(ready.get('id'),)).fetchone();ack=dict(nonce=choice['nonce'],choice='dismiss',code='DISMISSED')
    if row and choice.get('choice')=='switch' and row['stop']>now:
     try:
      portal,item=channel(dict(row));valid=bool(portal and item and validate_event(portal,item,dict(row)))
     except (OSError,ValueError,RuntimeError,TypeError):portal=item=None;valid=False
     if valid:
      ack.update(choice='switch',code='SWITCH_REQUESTED',pid=str(portal['id']),sid=str(item['sid']),url='plugin://plugin.video.xtreammate/?'+urlencode(dict(action='play_live' if portal['type']=='xtream' else 'source_play',pid=portal['id'],sid=item['sid'],name=item.get('name',''))))
     else:ack['code']='CHANNEL_UNAVAILABLE'
    with conn:
     conn.execute("UPDATE timers SET state=? WHERE id=? AND state='notified'",('selected' if ack['choice']=='switch' else 'dismissed',ready.get('id')))
     conn.execute("UPDATE alarm_dispatch89 SET state='closed' WHERE slot=1")
    verify=db()
    try:
     stored=verify.execute('SELECT state FROM timers WHERE id=?',(ready.get('id'),)).fetchone()
     if row and (not stored or stored[0]!=('selected' if ack['choice']=='switch' else 'dismissed')):raise OSError('TIMER_CHOICE_READBACK')
    finally:verify.close()
    put('Ack',ack);window().clearProperty(PREFIX+'Ready');window().clearProperty(PREFIX+'Choice');return
   if ready:
    row=conn.execute('SELECT state FROM timers WHERE id=?',(ready.get('id'),)).fetchone()
    if row and ready.get('stop',0)<=now:
     with conn:conn.execute("UPDATE timers SET state='missed' WHERE id=? AND state='notified'",(ready.get('id'),))
     row=None
    if not row or row[0]!='notified':put('Ack',dict(nonce=ready.get('nonce'),choice='dismiss',code='CANCELLED'));window().clearProperty(PREFIX+'Ready')
    return
   with conn:
    conn.execute('BEGIN IMMEDIATE')
    conn.execute("UPDATE timers SET state='missed' WHERE state='pending' AND stop<=?",(now,))
    # Orphaned dispatches were durably claimed before showing. Do not replay
    # a possibly already displayed popup after interpreter/Kodi shutdown.
    orphan=conn.execute("SELECT id FROM alarm_dispatch89 WHERE slot=1 AND state!='closed'").fetchone()
    if orphan:conn.execute("UPDATE timers SET state=CASE WHEN stop<=? THEN 'missed' ELSE 'dismissed' END WHERE id=? AND state='notified'",(now,orphan[0]))
    conn.execute("UPDATE alarm_dispatch89 SET state='closed' WHERE slot=1 AND state!='closed'")
    row=conn.execute("SELECT * FROM timers WHERE state='pending' AND notify_at<=? AND stop>? AND id NOT IN (SELECT id FROM bookmark_intents89) ORDER BY start,id LIMIT 1",(now,now)).fetchone()
    if row:
     nonce=uuid.uuid4().hex;conn.execute("UPDATE timers SET state='notified' WHERE id=? AND state='pending'",(row['id'],))
     conn.execute("INSERT OR REPLACE INTO alarm_dispatch89 VALUES(1,?,?,'published',?)",(row['id'],nonce,now))
   if row:put('Ready',dict(row,nonce=nonce,at=time.time()))
 finally:
  if conn is not None:conn.close()
  _guard.release()


def legacy_identity(old,portal,item):
 if str(old.get('pid',''))==str(portal['id']) and str(old.get('sid',''))==str(item['sid']):return True
 source=old.get('stream_url','')
 if not source:return False
 if portal.get('type')!='xtream':return source in (item.get('url'),item.get('stream_url'))
 from urllib.parse import urlsplit,unquote
 try:
  value=urlsplit(source);origin=urlsplit(portal.get('xc_host',''));parts=[unquote(p) for p in value.path.split('/')]
  position=parts.index('live')
  return (value.scheme,value.hostname,value.port)==(origin.scheme,origin.hostname,origin.port) and parts[position+1:position+3]==[portal.get('xc_user'),portal.get('xc_pass')] and parts[position+3].rsplit('.',1)[0]==str(item['sid'])
 except (ValueError,IndexError,TypeError):return False


def validate_event(portal,item,event):
 from programme_events46 import load
 from epg_events import title_key
 try:
  actual=load(portal,item,event)
  return actual.get('code')=='LOCAL_EVENT' and int(actual.get('start',0))==int(event['start']) and int(actual.get('stop',0))==int(event['stop']) and title_key(actual.get('title'))==title_key(event['title'])
 except (OSError,ValueError,TypeError,KeyError):return False

def cancel_legacy(record):
 from guide_timers import db,cancel
 conn=db()
 try:
  from reminder_bridge89 import init
  init(conn);tag=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest();row=conn.execute('SELECT state FROM legacy_reminders89 WHERE id=?',(tag,)).fetchone()
 finally:conn.close()
 if row and row[0].startswith('IMPORTED:'):cancel(row[0].partition(':')[2])

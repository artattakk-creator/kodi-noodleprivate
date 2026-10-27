"""Optional rich-event sidecar. Never alters, creates or migrates guide_v1.

Only metadata from a successfully committed source generation is published.
Readers require the exact canonical channel, interval, title and source rank.
Failures in this bounded cache cannot fail or modify the authoritative guide.
"""
import hashlib,json,os,sqlite3,time
from urllib.parse import quote
MAX_BYTES=32*1024*1024

def path(guide=None):
 if guide:return str(guide)+'.programme46.sqlite'
 from utils import addon_data_dir
 return os.path.join(addon_data_dir(),'programme_meta46.sqlite')

def title_hash(title):
 from epg_events import title_key
 return hashlib.sha256(title_key(title).encode()).hexdigest()

def metadata(event):
 """Bounded source facts, no title/description replacement or network calls."""
 result={}
 for target,keys,limit in [('subtitle',('sub_title','sub-title','subtitle'),512),('genre',('category','genre'),256),('episode_label',('episode',),128),('xmltv_image',('screenshot_uri','icon'),2048),('provider_image',('programme_image','event_image'),2048)]:
  value=next((event[k] for k in keys if isinstance(event.get(k),str) and event[k].strip()),'')
  if value:result[target]=value.strip()[:limit]
 for target,keys in [('season',('season','season_number')),('episode',('episode_number',)),('year',('year','date'))]:
  raw=next((event[k] for k in keys if event.get(k) not in ('',None)),None)
  try:
   value=int(str(raw)[:4] if target=='year' else raw)
   if (1880<=value<=2200 if target=='year' else 0<value<10000):result[target]=value
  except (TypeError,ValueError):pass
 cast=event.get('cast')
 if isinstance(cast,list) and any(isinstance(v,str) and v.strip() for v in cast):result['cast']=[v[:120] for v in cast[:24] if isinstance(v,str) and v.strip()]
 return result

def connect(write=False,guide=None):
 filename=path(guide)
 if os.path.islink(filename):raise OSError('SIDECAR_UNSAFE')
 if not write:
  if not os.path.isfile(filename):return None
  db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.03);db.execute('PRAGMA query_only=ON');return db
 from import_budget import check_space
 check_space(filename,32768)
 db=sqlite3.connect(filename,timeout=.05)
 try:
  db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA max_page_count=8192')
  db.executescript('''CREATE TABLE IF NOT EXISTS metadata(pid TEXT,cid TEXT,start INTEGER,stop INTEGER,titlehash TEXT,source INTEGER,data TEXT,PRIMARY KEY(pid,cid,start,stop,titlehash,source));
   CREATE TABLE IF NOT EXISTS pending(generation TEXT,pid TEXT,cid TEXT,start INTEGER,stop INTEGER,titlehash TEXT,source INTEGER,data TEXT,PRIMARY KEY(generation,pid,cid,start,stop,titlehash,source));''')
  return db
 except Exception:db.close();raise

class Stage:
 def __init__(self,pid,generation,source,guide=None,source_identity='compatibility',source_records=None):self.source_records=source_records;self.pid=str(pid);self.generation=generation;self.source=source;self.guide=guide;self.source_identity=source_identity;self.rows=[];self.failed=False
 def add(self,event):
  if self.failed:return
  value=metadata(event)
  if not value:return
  source=int(event.get('_source_index',self.source))
  value['epg_source46']=__import__('guide_publish44').source_id(self.source_records.get(source,{}),source) if self.source_records is not None else self.source_identity
  value['epg_text46']=hashlib.sha256(str(event.get('descr') or event.get('description') or '')[:4096].encode()).hexdigest()
  try:
   self.rows.append((self.generation,self.pid,str(event.get('channel') or event.get('cid') or ''),int(event.get('start_timestamp',event.get('start',0))),int(event.get('stop_timestamp',event.get('stop',0))),title_hash(event.get('name') or event.get('title')),int(event.get('_source_index',self.source)),json.dumps(value,ensure_ascii=False)))
   if len(self.rows)>=128:self.flush()
  except (ValueError,TypeError):pass
  except MemoryError:self.failed=True;self.rows.clear()
 def flush(self):
  if not self.rows:return
  db=None
  try:
   db=connect(True,self.guide)
   with db:db.executemany('INSERT OR REPLACE INTO pending VALUES(?,?,?,?,?,?,?,?)',self.rows)
  except (OSError,sqlite3.Error,ValueError,MemoryError):self.failed=True
  finally:
   if db is not None:db.close()
   self.rows.clear()
 def finish(self,publish=False):
  self.flush();finish(self.pid,self.generation,publish and not self.failed,self.guide)

def finish(pid,generation,publish,guide=None):
 if not os.path.isfile(path(guide)):return
 db=None
 try:
  db=connect(True,guide)
  with db:
   while True:
    rows=db.execute('SELECT cid,start,stop,titlehash,source,data FROM pending WHERE pid=? AND generation=? LIMIT 128',(str(pid),generation)).fetchall()
    if not rows:break
    # Free only this new unpublished stage before insertion, so promotion does
    # not require twice its disk budget. Published old metadata stays atomic.
    db.executemany('DELETE FROM pending WHERE generation=? AND pid=? AND cid=? AND start=? AND stop=? AND titlehash=? AND source=?',[(generation,str(pid),*row[:5]) for row in rows])
    if publish:db.executemany('INSERT OR REPLACE INTO metadata VALUES(?,?,?,?,?,?,?)',[(str(pid),*row) for row in rows])
 except (OSError,sqlite3.Error,ValueError,MemoryError):
  if db is not None:
   try:
    db.rollback()
    with db:db.execute('DELETE FROM pending WHERE pid=? AND generation=?',(str(pid),generation))
   except (OSError,sqlite3.Error):pass

 finally:
  if db is not None:db.close()

def read(pid,cid,event,guide=None,verify_source=False):
 db=None
 try:
  db=connect(False,guide)
  if db is None:return {}
  row=db.execute('SELECT data FROM metadata WHERE pid=? AND cid=? AND start=? AND stop=? AND titlehash=? AND source=?',(str(pid),str(cid),int(event['start']),int(event['stop']),title_hash(event['title']),int(event.get('source',0)))).fetchone()
  if not row or len(row[0])>16384:return {}
  value=json.loads(row[0])
  if not isinstance(value,dict):return {}
  if ('description' in event or 'descr' in event) and value.get('epg_text46')!=hashlib.sha256(str(event.get('description') or event.get('descr') or '')[:4096].encode()).hexdigest():return {'metadata_code46':'TEXT_IDENTITY_MISMATCH'}
  if verify_source and not origin_matches(pid,cid,event,value.get('epg_source46'),guide):return {'metadata_code46':'SOURCE_AMBIGUOUS_OR_BUDGET'}
  return value
 except (OSError,sqlite3.Error,ValueError,TypeError,KeyError):return {}
 finally:
  if db is not None:db.close()


def origin_matches(pid,cid,event,identity,guide=None):
 """Reject ambiguous source archives rather than guess after source reordering."""
 db=None
 try:
  from guide_store import path as guide_path
  filename=guide or guide_path()
  db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.02)
  deadline=time.monotonic()+.02;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
  rows=db.execute('SELECT DISTINCT source_id FROM guide44_inputs WHERE pid=? AND cid=? AND start=? AND stop=? AND title=? AND rank=? LIMIT 2',(str(pid),str(cid),event['start'],event['stop'],event['title'],event.get('source',0))).fetchall()
  return rows==[(identity,)]
 except (OSError,sqlite3.Error):return False
 finally:
  if db is not None:db.close()

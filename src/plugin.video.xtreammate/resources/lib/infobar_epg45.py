"""One bounded read-only previous-event lookup in the existing guide worker."""
import os,sqlite3,time
from urllib.parse import quote

def previous(pid,channel,mappings,now,revision):
 from guide_store import path
 from local_epg import channel_keys
 filename=path()
 if not os.path.isfile(filename) or not revision:return ''
 db=None
 try:
  db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.03)
  db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
  deadline=time.monotonic()+.08;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
  meta=db.execute('SELECT revision,updated FROM guide_meta WHERE pid=?',(pid,)).fetchone()
  if not meta or tuple(meta)!=tuple(revision):return ''
  sid,keys=channel_keys(channel,mappings)
  for key in keys:
   alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(pid,key)).fetchone();cid=alias[0] if alias else key
   row=db.execute('SELECT title FROM programmes WHERE pid=? AND cid=? AND start>=? AND start<=? AND stop<=? ORDER BY start DESC LIMIT 1',(pid,cid,now-8*86400,now,now)).fetchone()
   if row:return str(row[0])
  return ''
 except (sqlite3.Error,OSError,ValueError,TypeError):return ''
 finally:
  if db is not None:db.close()

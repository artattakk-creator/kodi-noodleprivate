"""Bounded read-only history from the same published guide revision."""
import os,sqlite3,time
from urllib.parse import quote

def history(pid,channel,mappings,now,revision,*,guide_id=None,limit=2):
 from guide_store import path
 from local_epg import channel_keys
 from epg_binding48 import binding
 from epg_events import deduplicate
 filename=path()
 if not os.path.isfile(filename) or not revision:return []
 db=None
 try:
  db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.03)
  db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
  deadline=time.monotonic()+.08;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
  meta=db.execute('SELECT revision,updated FROM guide_meta WHERE pid=?',(pid,)).fetchone()
  if not meta or tuple(meta)!=tuple(revision):return []
  sid,keys=channel_keys(channel,mappings)
  selection=binding(mappings,sid)
  if guide_id is not None:keys=[guide_id] if guide_id in keys else []
  for key in keys:
   if selection:
    cid=selection['channel'];source=selection['source']
    rows=db.execute('SELECT title,description,start,stop,rank FROM guide44_inputs WHERE pid=? AND source_id=? AND cid=? AND start>=? AND start<=? AND stop<=? ORDER BY start DESC LIMIT ?',
                    (pid,source,cid,now-8*86400,now,now,limit*4))
   else:
    source=''
    alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(pid,key)).fetchone();cid=alias[0] if alias else key
    rows=db.execute('SELECT title,description,start,stop,source FROM programmes WHERE pid=? AND cid=? AND start>=? AND start<=? AND stop<=? ORDER BY start DESC,source LIMIT ?',
                    (pid,cid,now-8*86400,now,now,limit*4))
   events=deduplicate([dict(title=r[0],description=r[1],start=r[2],stop=r[3],source=r[4],source_key46=source) for r in rows],channel=cid)
   if events:return [dict(event,canonical46=cid,revision68=revision) for event in events[-limit:]]
  return []
 except (sqlite3.Error,OSError,ValueError,TypeError):return []
 finally:
  if db is not None:db.close()


def previous(pid,channel,mappings,now,revision):
 events=history(pid,channel,mappings,now,revision,limit=1)
 return events[0]['title'] if events else ''

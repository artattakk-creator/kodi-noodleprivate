"""Worker-only cold-start coverage for every supplied row; no HTTP or new guide."""
import os,sqlite3,time
from urllib.parse import quote
_seen={}
def warm(portal,rows):
 from guide_store import path
 from epg_status import revision
 from epg_handoff63 import profile_scope
 filename=path()
 def stamp(name):
  try:return os.stat(name).st_mtime_ns
  except OSError:return 0
 key=(profile_scope(),str(portal['id']))
 signature=(revision(portal['id']),stamp(filename),stamp(filename+'-wal'),tuple(str(r.get('sid','')) for r in rows))
 prior=_seen.get(key);now=time.monotonic()
 if prior and prior[0]==signature and now-prior[1]<30:return False
 from widget_group46 import _infos63
 _infos63(portal,rows)
 _seen[key]=(signature,now)
 if len(_seen)>8:_seen.pop(next(iter(_seen)))
 return True
def classify(info,has_mapping,first=None,last=None,now=None,readable=True):
 now=time.time() if now is None else now
 if info.get('now'):return 'READY'
 if not readable:return 'DB_UNAVAILABLE'
 if not has_mapping or info.get('reason')=='MANUAL_ID_MISSING':return 'UNMAPPED'
 if first is None or last is None:return 'SOURCE_EMPTY'
 if last<=now:return 'STALE'
 return 'EVENT_OUT_OF_WINDOW'
def report(portal,rows,now=None):
 from local_epg import now_next,channel_keys
 from epg_sources import configuration
 from epg_binding48 import binding
 from guide_store import path
 now=time.time() if now is None else now;mappings=configuration(portal['id'])['mappings'];infos={}
 for offset in range(0,len(rows),16):infos.update(now_next(portal['id'],rows[offset:offset+16],mappings,now=now,display_only65=True))
 filename=path();db=None;result=[];readable=False
 try:
  if os.path.isfile(filename):
   db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05);db.execute('PRAGMA query_only=ON');db.execute('BEGIN');readable=True
   deadline=time.monotonic()+1;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
  for row in rows:
   sid,keys=channel_keys(row,mappings);info=infos.get(sid,{});cid=info.get('canonical46') or info.get('epg_id','')
   selected=binding(mappings,sid);first=last=None
   if readable and cid:
    if selected:bounds=db.execute('SELECT min(start),max(stop) FROM guide44_inputs WHERE pid=? AND source_id=? AND cid=?',(str(portal['id']),selected['source'],selected['channel'])).fetchone()
    else:bounds=db.execute('SELECT min(start),max(stop) FROM programmes WHERE pid=? AND cid=?',(str(portal['id']),cid)).fetchone()
    first,last=bounds
   result.append(dict(sid=sid,code=classify(info,bool(cid),first,last,now,readable),first=first,last=last,revision=info.get('snapshot_revision'),source=selected['source'] if selected else 'merged'))
 except (OSError,sqlite3.Error):
  return [dict(sid=str(row.get('sid','')),code='DB_UNAVAILABLE') for row in rows]
 finally:
  if db is not None:db.close()
 return result

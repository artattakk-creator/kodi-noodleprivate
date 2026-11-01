"""Source-qualified restart evidence from the ONE existing guide, no creation."""
import os,sqlite3,time
from urllib.parse import quote
def restart_anchors(pid):
 from guide_store import path
 filename=path();db=None
 if not os.path.isfile(filename):return {}
 try:
  db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
  db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
  deadline=time.monotonic()+.25;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
  meta=db.execute('SELECT updated FROM guide_meta WHERE pid=?',(str(pid),)).fetchone()
  if not meta:return {}
  return {str(row[0]):float(meta[0]) for row in db.execute('SELECT DISTINCT source_id FROM guide44_inputs WHERE pid=?',(str(pid),))}
 except (OSError,sqlite3.Error,ValueError):return {}
 finally:
  if db is not None:db.close()
def receipt(db,generation):
 import hashlib,json
 digest=hashlib.sha256();count=0;first=None;last=None;channels=set()
 for cid,start,stop,title,description in db.execute('SELECT cid,start,stop,title,description FROM xml_stage WHERE generation=? ORDER BY cid,start,stop',(generation,)):
  digest.update(json.dumps([cid,start,stop,title,description],ensure_ascii=False,separators=(',',':')).encode())
  count+=1;channels.add(cid);first=start if first is None else min(first,start);last=stop if last is None else max(last,stop)
 return dict(revision66=digest.hexdigest(),min_start66=first,max_end66=last,mapped_channels66=len(channels),stored_unique66=count)

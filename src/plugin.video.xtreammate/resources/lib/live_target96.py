"""Selected group only: RO, indexed, generation-pinned; no EPG or widget scan."""
import os,sqlite3,time
from urllib.parse import quote

def failure(code):
 from library_index import IndexReadError
 error=IndexReadError(code);error.code=code;return error

def head(filename,pid,cid):
 db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.2)
 try:
  end=time.monotonic()+1;db.set_progress_handler(lambda:int(time.monotonic()>end),1000)
  row=db.execute('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?',(str(pid),'live',str(cid))).fetchone()
  return row[0] if row else None
 finally:db.close()

def read(portal,cid,receipt=None):
 from library_index import path
 from live_home62 import read as group_read,Failure
 from group_selection import load
 filename=path();pid=str(portal['id'])
 if not os.path.isfile(filename):raise failure('GROUP_NOT_IMPORTED')
 try:
  before=head(filename,pid,cid)
  rows,code=group_read(dict(portal,start_group_id=cid),filename,seconds=6,page_seconds=1.5)
  if head(filename,pid,cid)!=before:raise failure('REVISION_CHANGED')
  # Category metadata is small; missing unrelated group heads do not block us.
  db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.2)
  try:
   end=time.monotonic()+1;db.set_progress_handler(lambda:int(time.monotonic()>end),1000)
   groups=[dict(category_id=r[0],category_name=r[1]) for r in db.execute('SELECT cid,title FROM groups WHERE pid=? AND kind=? ORDER BY ordinal,cid',(pid,'live'))]
  finally:db.close()
  known={g['category_id'] for g in groups}
  for missing in sorted((load(pid,'live') or set())-known):groups.append(dict(category_id=missing,category_name=missing))
  if receipt is not None:receipt.update(generation=before,count=len(rows),code=code)
  return groups,[dict(row,stream_id=row['sid']) for row in rows]
 except Failure as exc:
  code='GROUP_NOT_IMPORTED' if exc.code in ('INDEX_MISSING','GENERATION_MISSING','START_GROUP_UNAVAILABLE') else exc.code
  raise failure(code) from None
 except sqlite3.Error as exc:
  number=getattr(exc,'sqlite_errorcode',0)&255
  raise failure('BUDGET' if number==9 else 'SQLITE_BUSY' if number in (5,6) else 'LOCAL_LIVE_UNAVAILABLE') from None

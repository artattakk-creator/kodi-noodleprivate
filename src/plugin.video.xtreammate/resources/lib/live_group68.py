"""All enabled groups, one RO transaction, provider order and SID dedup."""
import json,sqlite3,time
from urllib.parse import quote
def read(portal,filename):
 from live_home62 import Failure
 from group_selection import enabled_ids
 db=None;remaining=1.5
 try:
  db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
  db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
  def query(sql,args):
   nonlocal remaining
   if remaining<=0:raise Failure('BUDGET','PAGE')
   started=time.monotonic();deadline=started+min(.5,remaining)
   db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
   try:return db.execute(sql,args).fetchall()
   finally:remaining-=time.monotonic()-started
  groups=query('SELECT cid FROM groups WHERE pid=? AND kind=? ORDER BY ordinal,cid',(str(portal['id']),'live'))
  allowed=enabled_ids(portal['id'],'live',[dict(category_id=g['cid']) for g in groups])
  output=[];seen=set()
  for group in groups:
   cid=group['cid']
   if cid not in allowed:continue
   head=query('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?',(str(portal['id']),'live',cid))
   table,index=('items_v2','group_order_v2') if head else ('titles','category_titles')
   where='pid=? AND kind=? AND cid=?';args=[str(portal['id']),'live',cid]
   if head:where+=' AND generation=?';args.append(head[0]['generation'])
   last=None
   while True:
    rows=query('SELECT sid,title,payload,ordinal FROM '+table+' INDEXED BY '+index+' WHERE '+where+(' AND (ordinal,sid)>(?,?)' if last else '')+' ORDER BY ordinal,sid LIMIT 128',args+(list(last) if last else []))
    if not rows:break
    for row in rows:
     sid=row['sid']
     if not isinstance(sid,str) or not sid or not isinstance(row['title'],str) or not row['title']:raise Failure('PAYLOAD_INVALID','PAYLOAD')
     if sid in seen:continue
     seen.add(sid)
     try:
      value=json.loads(row['payload'])
      if not isinstance(value,dict) or str(value.get('sid',''))!=sid or str(value.get('category_id',''))!=cid:raise ValueError()
     except (ValueError,TypeError):value={}
     value.update(sid=sid,name=row['title'][:512],category_id=cid,kind='live');output.append(value)
    last=(rows[-1]['ordinal'],rows[-1]['sid'])
  return output,'READY' if output else 'EMPTY_GROUP'
 except sqlite3.Error as exc:
  name=getattr(exc,'sqlite_errorname','SQLITE_ERROR')
  raise Failure('BUDGET' if name=='SQLITE_INTERRUPT' else 'SQLITE_BUSY' if name.startswith('SQLITE_BUSY') else 'SQLITE_ERROR','PAGE') from None
 finally:
  if db is not None:db.close()

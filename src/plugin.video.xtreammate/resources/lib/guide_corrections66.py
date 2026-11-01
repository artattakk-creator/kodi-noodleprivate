"""Proven same-source time corrections; caller owns the existing guide transaction."""
def apply(db,pid,table,where,args,source,rank,cancel=lambda:False):
 if table!='xml_stage' or rank is None:return 0
 from epg_events import title_key
 selector=' WHERE '+where if where else ''
 candidates=[];used=set()
 for cid,start,stop,title,description in db.execute('SELECT cid,start,stop,title,description FROM '+table+selector,args):
  if cancel():raise InterruptedError('CANCELLED')
  if not description or len(description.strip())<12:continue
  if db.execute('SELECT 1 FROM programmes WHERE pid=? AND cid=? AND start=? AND stop=?',(pid,cid,start,stop)).fetchone():continue
  possible=[]
  for old in db.execute('''SELECT p.start,p.stop,p.title,p.description FROM programmes p JOIN guide44_inputs g
    ON g.pid=p.pid AND g.cid=p.cid AND g.start=p.start AND g.stop=p.stop
    WHERE p.pid=? AND p.cid=? AND g.source_id=? AND p.source=? AND g.rank=? AND p.stop>? AND p.start<?''',(pid,cid,source,rank,rank,start,stop)):
   left,right,old_title,old_description=old
   overlap=max(0,min(stop,right)-max(start,left))
   if title_key(old_title)==title_key(title) and old_description.strip()==description.strip() and abs(start-left)<=900 and abs((stop-start)-(right-left))<=300 and overlap>=.8*max(stop-start,right-left):possible.append((left,right))
  if len(possible)!=1:continue
  old=possible[0];identity=(cid,*old)
  if identity in used:return 0
  used.add(identity);candidates.append((cid,old[0],old[1],start,stop))
 if not candidates:return 0
 # Refuse a correction that would overlap any unaffected committed programme.
 for cid,left,right,start,stop in candidates:
  for other_start,other_stop in db.execute('SELECT start,stop FROM programmes WHERE pid=? AND cid=? AND stop>? AND start<?',(pid,cid,start,stop)):
   if (cid,other_start,other_stop) not in used:return 0
 for i,one in enumerate(candidates):
  for two in candidates[i+1:]:
   if one[0]==two[0] and one[3]<two[4] and two[3]<one[4]:return 0
 for cid,left,right,start,stop in candidates:
  if cancel():raise InterruptedError('CANCELLED')
  db.execute('UPDATE programmes SET start=?,stop=? WHERE pid=? AND cid=? AND start=? AND stop=?',(start,stop,pid,cid,left,right))
  if db.execute('SELECT 1 FROM guide44_inputs WHERE pid=? AND source_id=? AND cid=? AND start=? AND stop=?',(pid,source,cid,start,stop)).fetchone():
   # Only this obsolete, uniquely proven interval is merged into its already
   # stored correction. The transaction retains every unrelated programme.
   db.execute('DELETE FROM guide44_inputs WHERE pid=? AND source_id=? AND cid=? AND start=? AND stop=?',(pid,source,cid,left,right))
  else:db.execute('UPDATE guide44_inputs SET start=?,stop=? WHERE pid=? AND source_id=? AND cid=? AND start=? AND stop=?',(start,stop,pid,source,cid,left,right))
 return len(candidates)

"""One in-flight local batch per exact profile/source/binding generation.

Contenders never wait on the GUI or open competing readers. A validated warm
snapshot remains usable. Busy means pending, not a confirmed empty database.
"""
import threading,time
_lock=threading.Lock();_active=set()
def run(pid,channels,mappings,now,display,read):
 from epg_poll77 import key,read as cached
 from epg_handoff63 import get
 from local_epg import channel_keys
 ts=time.time() if now is None else now;ident=key(pid,channels,mappings,display)
 with _lock:
  busy=ident in _active
  if not busy:_active.add(ident)
 if busy:
  value=cached(ident,ts)
  if value is not None:return value
  result={}
  for channel in channels[:16]:
   sid=channel_keys(channel,mappings)[0];value=get(pid,sid,now=ts,mappings=mappings)
   if value:result[sid]=value
  return result
 try:return read()
 finally:
  with _lock:_active.discard(ident)


def aliases(db,pid,channels,mappings):
 """One bounded query in the same RO transaction, instead of 32 roundtrips."""
 from local_epg import channel_keys
 identifiers=sorted({ident for row in channels[:16] for ident in channel_keys(row,mappings)[1]})
 if not identifiers:return {}
 marks=','.join('?' for _ in identifiers)
 return {row[0]:(row[1],) for row in db.execute('SELECT alias,cid FROM guide_alias WHERE pid=? AND alias IN ('+marks+')',[pid]+identifiers)}

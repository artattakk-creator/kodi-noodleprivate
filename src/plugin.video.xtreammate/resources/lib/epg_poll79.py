"""Per-channel read leases: mixed/focused batches cannot bypass missing backoff.

Exact profile/guide/WAL/manual-binding identity from the existing reader. New
committed data invalidates immediately. No fuzzy matching or persistent guide.
"""
import copy,threading,time
_lock=threading.RLock();_values={}
def select(pid,channels,mappings,now,display):
 from epg_poll77 import key
 from local_epg import channel_keys
 parked={};todo=[]
 for row in channels:
  cache_key=key(pid,[row],mappings,display)
  with _lock:record=_values.get(cache_key)
  if not record:
   record=__import__('epg_negative80').read(cache_key)
   if record:
    with _lock:_values[cache_key]=record
  if record and time.monotonic()<record['until'] and abs(now-record['now'])<60:
   info=record['value'];sid=channel_keys(row,mappings)[0]
   valid=info.get('start',0)<=now<info.get('stop',0) if info.get('now') else not (0<info.get('next_start',0)<=now)
   if valid:parked[sid]=copy.deepcopy(info);continue
  todo.append(row)
 return parked,todo

def remember(pid,channels,mappings,now,display,result,expected=None):
 from epg_poll77 import key
 from local_epg import channel_keys
 for row in channels:
  sid=channel_keys(row,mappings)[0];value=result.get(sid)
  if value is None:continue
  cache_key=key(pid,[row],mappings,display)
  if expected is not None and expected.get(sid)!=cache_key:continue
  with _lock:
   prior=_values.get(cache_key,{});misses=0 if value.get('now') else min(3,prior.get('misses',0)+1)
   ttl=15 if value.get('now') else min(60,15*2**(misses-1))
   _values[cache_key]=dict(until=time.monotonic()+ttl,now=now,value=copy.deepcopy(value),misses=misses)
   __import__('epg_negative80').remember(cache_key,_values[cache_key])
   while len(_values)>256:_values.pop(next(iter(_values)))

def keys(pid,channels,mappings,display):
 from epg_poll77 import key
 from local_epg import channel_keys
 return {channel_keys(row,mappings)[0]:key(pid,[row],mappings,display) for row in channels}

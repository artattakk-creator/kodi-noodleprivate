"""Bounded volatile outcomes and deferred metadata persistence; no image archive."""
from collections import OrderedDict
import copy,threading,time
_lock=threading.RLock()
_values=OrderedDict();_attempts=OrderedDict()
_next_flush=0
MAX_RECORDS=128

def key(event):
 from programme_requests68 import identity
 from programme_policy68 import negative_scope
 return identity(event),negative_scope(event)

def get(event):
 k=key(event)
 with _lock:
  item=_values.get(k)
  if not item or item['value'].get('until',0)<=time.time():return None
  _values.move_to_end(k)
  return copy.deepcopy(item['value'])

def remember(event,value,persisted=False,update=False):
 now=time.time();value=dict(value)
 if not isinstance(value.get('until'),(float,int)) or not now<value['until']<=now+86400:value['until']=now+300
 k=key(event)
 if value.get('source')=='placeholder' and not update:
  with _lock:
   count=min(3,_attempts.get(k,0)+1);_attempts[k]=count
   while len(_attempts)>256:_attempts.popitem(last=False)
  if value.get('code') in ('NO_MATCH','NO_UNIQUE_MATCH','NO_MATCH_AMBIGUOUS','NO_ARTWORK','NOT_CLASSIFIED_MOVIE','NO_YEAR','TMDB_DISABLED'):
   value['until']=max(value['until'],now+6*3600)
  else:value['until']=max(value['until'],now+(60,300,6*3600)[count-1])
 value['persisted69']=bool(persisted)
 value['storage69']='PERSISTED' if persisted else 'RAM_ONLY'
 from epg_handoff63 import profile_scope
 with _lock:
  _values[k]=dict(event=copy.deepcopy(event),value=copy.deepcopy(value),profile=profile_scope(),next_write=now+5)
  _values.move_to_end(k)
  while len(_values)>MAX_RECORDS:_values.popitem(last=False)
 return value

def persist(event,value):
 from programme_index46 import publish_result69,path
 from programme_writes69 import permit,last
 if not permit(path()):return dict(value,persisted69=False,storage69='RAM_ONLY',storage_code69=last(path()))
 committed=dict(value,persisted69=True,storage69='PERSISTED',storage_code69='READY')
 if publish_result69(event,committed):
  return dict(value,persisted69=True,storage69='PERSISTED',storage_code69='READY')
 return dict(value,persisted69=False,storage69='RAM_ONLY',storage_code69=last(path()))

def flush(cancel=lambda:False):
 global _next_flush
 now=time.time()
 if now<_next_flush or cancel():return False
 _next_flush=now+5
 from programme_index46 import path
 from programme_writes69 import permit
 if not permit(path()):return False
 from epg_handoff63 import profile_scope
 with _lock:items=[(k,copy.deepcopy(v)) for k,v in _values.items() if not v['value'].get('persisted69') and v['profile']==profile_scope() and v['next_write']<=now and v['value'].get('until',0)>now][:4]
 for k,item in items:
  if cancel():break
  value=persist(item['event'],item['value'])
  with _lock:
   current=_values.get(k)
   if current and current['value'].get('resolved_at55')==item['value'].get('resolved_at55'):
    current['value']=value;current['next_write']=now+30
  if value.get('persisted69'):
   from programme_requests68 import completed
   completed(item['event'],value)
 return bool(items)

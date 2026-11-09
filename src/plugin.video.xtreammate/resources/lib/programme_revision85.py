"""Exact mismatch reasons and bounded current-event recovery, no identity bypass."""
import time
_due={}
REASONS=('EVENT_CHANGED','SOURCE_CHANGED','FILE_INVALID','EXPIRED','POLICY_CHANGED','NO_SOURCE_FACTS')
def reason(event,old):
 if not event.get('title') or not event.get('start') or event.get('code') not in (None,'LOCAL_EVENT'):return 'NO_SOURCE_FACTS'
 if not isinstance(old,dict):return 'NO_SOURCE_FACTS'
 if old.get('key') and old['key']!=event.get('key'):return 'EVENT_CHANGED'
 if old.get('until',float('inf'))<=time.time():return 'EXPIRED'
 from programme_policy68 import negative_scope
 if old.get('policy69') and old['policy69']!=negative_scope({}):return 'POLICY_CHANGED'
 from programme_art46 import fingerprint
 if old.get('fingerprint') and old['fingerprint']!=fingerprint(event):return 'SOURCE_CHANGED'
 return 'FILE_INVALID'
def recover(event):
 from programme_requests68 import identity,request
 tag=identity(event);now=time.monotonic()
 if now<_due.get(tag,0):return False
 _due[tag]=now+30
 while len(_due)>128:_due.pop(next(iter(_due)))
 return request(event,priority=True)
def outcome(event,old,explicit=None):
 code=explicit if explicit in REASONS else reason(event,old)
 from programme_lastgood80 import note
 note(event,code)
 recover(event)
 return dict(code=code,source='placeholder',until=time.time()+30)

_failures={}
def delay(event,code):
 from programme_requests68 import identity
 key=(identity(event),code);count=min(4,_failures.get(key,0)+1);_failures[key]=count
 while len(_failures)>128:_failures.pop(next(iter(_failures)))
 return (30,120,300,900)[count-1]

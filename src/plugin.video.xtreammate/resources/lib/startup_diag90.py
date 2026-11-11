"""Bounded numeric startup evidence. Never URLs, IDs, labels or credentials."""
import json,time
_seen={}
CODES=frozenset(('MANIFEST_LOAD_MS','LOCAL_HIT','REMOTE_FETCH_COUNT','PERSIST_COMMIT_MS','EPG_LASTGOOD_AGE','CALLBACK_FAIL_REASON','GROUPS_VISIBLE','GROUP_CHANNELS_READY','GROUP_SQL_BUSY','GROUP_SNAPSHOT_REUSED','GROUP_SWITCH_PENDING'))
REASONS=frozenset(('PROFILE_BUSY','READ_IO','INVALID_PROFILE','PROFILE_RACE','PROFILE_BUDGET','MEMORY','MEMORY_PAUSE','UNKNOWN','BUDGET','SQLITE_BUSY','SQLITE_LOCKED','LOCAL_LIVE_UNAVAILABLE'))
def note(code,**facts):
 if code not in CODES:return
 safe={k:min(v,3600000 if k in ('ms','age_ms') else 50000) for k,v in facts.items() if k in ('ms','age_ms','count','total','groups') and type(v) is int and v>=0}
 if facts.get('reason') in REASONS:safe['reason']=facts['reason']
 key=(code,safe.get('count'),safe.get('total'),safe.get('reason'));now=time.monotonic()
 if now-_seen.get(key,-1e9)<30:return
 _seen[key]=now
 while len(_seen)>128:_seen.pop(next(iter(_seen)))
 try:
  import xbmc
  xbmc.log('[XCMate][START90] '+json.dumps(dict(code=code,**safe),separators=(',',':')),xbmc.LOGINFO)
 except (ImportError,AttributeError,RuntimeError):pass

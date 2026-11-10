"""Bounded token/URL/title-free evidence, never guesses visible Android pixels."""
import hashlib,json,threading,time
_local=threading.local();_seen={};_guard=threading.Lock();_inflight=set();_results={}
STAGES={'TOKEN_PRESENT','ENABLED','OPT_OUT','QUEUED','SKIPPED_REASON','HTTP_REQUEST_SENT','HTTP_STATUS','TITLE_NORMALIZED','MATCH_CONFIRMED','MATCH_REJECTED','IMAGE_BACKDROP_READY','IMAGE_POSTER_READY','SOURCE_COMMITTED','SOURCE_RETAINED','CACHE','TEXTURE_REQUESTED','TEXTURE_CACHED','NOT_VISIBLE','SOURCE_DECIDED','DECODED_LOCAL','RENDER_READY','BANK_SWITCHED'}
def note(event,stage,code='OK',**facts):
 if stage not in STAGES:return
 __import__('hero_timing87').note(event,stage,code)
 tag=hashlib.sha256(json.dumps([event.get(k) for k in ('pid','sid','key','start','stop')],sort_keys=True).encode()).hexdigest()[:12]
 # Only fixed enums/numbers; exception messages, paths and account data excluded.
 fixed=code if isinstance(code,str) and 1<=len(code)<=40 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789' for c in code) else 'UNCLASSIFIED'
 key=(tag,stage,fixed);now=time.monotonic()
 if now-_seen.get(key,-1e9)<30:return
 _seen[key]=now
 while len(_seen)>512:_seen.pop(next(iter(_seen)))
 clean={k:v for k,v in facts.items() if k in ('ms','status','count','width','height','free','reserve','budget') and type(v) in (int,float,bool)}
 import xbmc
 try:xbmc.log('[XCMate][ART81] event='+tag+' stage='+stage+' code='+fixed+' '+json.dumps(clean,separators=(',',':')),xbmc.LOGINFO)
 except (AttributeError,RuntimeError):pass

def own(event,call):
 from utils import setting_bool
 from tmdb_token61 import effective_tmdb_read_token,TokenError
 try:present=bool(effective_tmdb_read_token())
 except TokenError:present=False
 enabled=setting_bool('programme_tmdb46',False) and setting_bool('tmdb_research43',False)
 optout=setting_bool('programme_tmdb_optout77',False)
 note(event,'TOKEN_PRESENT','YES' if present else 'NO');note(event,'ENABLED','YES' if enabled else 'NO');note(event,'OPT_OUT','YES' if optout else 'NO')
 if optout or not enabled or not present:
  note(event,'SKIPPED_REASON','OPT_OUT' if optout else 'DISABLED' if not enabled else 'TOKEN_MISSING');return None
 from event_art81 import key
 tag=key(event);now=time.monotonic()
 with _guard:
  if tag in _inflight:
   note(event,'SKIPPED_REASON','INFLIGHT');return None
  hit=_results.get(tag)
  if hit and now<hit[0]:
   note(event,'CACHE','MATCH' if hit[1] else 'NO_MATCH');return dict(hit[1]) if hit[1] else None
  _inflight.add(tag)
 previous=getattr(_local,'event',None);_local.event=event
 try:
  note(event,'TITLE_NORMALIZED');value=call()
  note(event,'MATCH_CONFIRMED' if value else 'MATCH_REJECTED','EXACT' if value else 'NO_MATCH')
  if value:note(event,'IMAGE_POSTER_READY' if value.get('role81')=='poster' else 'IMAGE_BACKDROP_READY')
  with _guard:_results[tag]=(time.monotonic()+(300 if value else 60),dict(value) if value else None)
  return value
 except Exception:
  with _guard:_results[tag]=(time.monotonic()+60,None)
  raise
 finally:
  _local.event=previous
  with _guard:
   _inflight.discard(tag)
   while len(_results)>256:_results.pop(next(iter(_results)))

def request(stage,code='OK',**facts):
 event=getattr(_local,'event',None)
 if event:note(event,stage,code,**facts)

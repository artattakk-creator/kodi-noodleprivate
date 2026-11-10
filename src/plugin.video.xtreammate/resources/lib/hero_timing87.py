"""Bounded event-scoped stage latencies; reference/decode/pixels stay distinct."""
import hashlib,json,math,threading,time
_lock=threading.RLock();_events={};_samples={}
STAGES={'QUEUED','TITLE_NORMALIZED','MATCH_CONFIRMED','HTTP_REQUEST_SENT','HTTP_STATUS','IMAGE_BACKDROP_READY','IMAGE_POSTER_READY','SOURCE_DECIDED','DECODED_LOCAL','TEXTURE_CACHED','RENDER_READY','BANK_SWITCHED'}
def correlation(event):return hashlib.sha256(__import__('event_art81').key(event).encode()).hexdigest()

def pipeline(event,stage,code):
 mapping={'EPG_EVENT':'LOCAL_EPG_IDENTIFIED','URL_SECURITY':'URL_POLICY','HTTP_RESPONSE':'IMAGE_RESPONSE','LOCAL_CACHE':'CACHE_REFERENCE','RENDER_CONTROL':'CONTROL_REQUESTED','ACTUAL_TEXTURE':'TEXTURE_RECEIPT'}
 if stage in mapping:note(event,mapping[stage],code)

def note(event,stage,code=''):
 if stage not in STAGES and stage not in ('LOCAL_EPG_IDENTIFIED','URL_POLICY','IMAGE_RESPONSE','CACHE_REFERENCE','CONTROL_REQUESTED','TEXTURE_RECEIPT'):return
 ident=correlation(event);now=time.monotonic()
 with _lock:
  value=_events.setdefault(ident,dict(started=now,stages={}))
  if stage in value['stages']:return
  elapsed=max(0,round((now-value['started'])*1000));value['stages'][stage]=elapsed
  samples=_samples.setdefault(stage,[]);samples.append(elapsed);del samples[:-128]
  while len(_events)>128:_events.pop(next(iter(_events)))
  # Preserve the existing atomic GUI commit boundary: after Active flips,
  # this stage records RAM only. The next worker stage exports the receipt.
  if stage=='BANK_SWITCHED':return
  import xbmcgui
  xbmcgui.Window(10000).setProperty('XCMate.Hero87.Trace',json.dumps(dict(event=ident,stages=value['stages'],evidence='REFERENCE_AND_DECODE_NOT_VISIBLE_PIXELS'),separators=(',',':')))
def summary():
 with _lock:
  return {stage:dict(count=len(values),p50_ms=sorted(values)[max(0,math.ceil(len(values)*.5)-1)],p95_ms=sorted(values)[max(0,math.ceil(len(values)*.95)-1)]) for stage,values in _samples.items() if values}

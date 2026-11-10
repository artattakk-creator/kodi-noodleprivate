"""Cross-invoker negative diagnostic lease, no user facts or disk writes."""
import hashlib,json,time
def admit(stage,event,code,seconds=300):
 try:
  from epg_handoff63 import profile_scope
  import xbmcgui
  material=[profile_scope(),stage,code]+[event.get(k) for k in ('key','source_key46','fact_revision46','epg_source46','revision')]
  key=hashlib.sha256(json.dumps(material,sort_keys=True,default=str).encode()).hexdigest()
  slot='XCMate.NegativeLog86.'+str(int(key[:8],16)%256);window=xbmcgui.Window(10000);now=time.time()
  raw=window.getProperty(slot);old=json.loads(raw) if raw and len(raw)<256 else {}
  if old.get('key')==key and 0<=now-old.get('at',0)<seconds:return False
  window.setProperty(slot,json.dumps(dict(key=key,at=now),separators=(',',':')));return True
 except (ImportError,AttributeError,RuntimeError,ValueError,TypeError):return True

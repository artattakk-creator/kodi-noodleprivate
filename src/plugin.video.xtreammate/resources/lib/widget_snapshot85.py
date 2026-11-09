"""Short cross-interpreter catalogue memo; source stat/policy changes invalidate.

Existing rows are never emptied on an optional write/cache failure.
"""
import hashlib,json,os,time
MAX_BYTES=256*1024

def signature(portal,kind):
 from widget_data41 import policy
 from library_index import path
 try:
  p=path();s=os.stat(p);wal=p+'-wal';w=os.stat(wal) if os.path.isfile(wal) else None
  stamp=[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,[w.st_size,w.st_mtime_ns] if w else None]
 except OSError:return None
 return hashlib.sha256(json.dumps([policy(portal,kind),stamp]).encode()).hexdigest()

def cached(portal,kind):
 from epg_handoff63 import identity
 import xbmcgui
 key='XCMate.Catalogue85.'+identity(portal['id'],kind)
 try:
  raw=xbmcgui.Window(10000).getProperty(key)
  if not raw or len(raw.encode())>MAX_BYTES:return None
  record=json.loads(raw)
  if record['signature']!=signature(portal,kind) or not 0<=time.time()-record['at']<120:return None
  return record['rows'],record['code']
 except (AttributeError,RuntimeError,ValueError,TypeError,KeyError):return None

def remember(portal,kind,rows,code):
 if kind not in ('vod','series') or code not in ('READY','CACHE','READ_ONLY'):return
 from epg_handoff63 import identity
 import xbmcgui
 digest=signature(portal,kind)
 if digest is None:return
 raw=json.dumps(dict(signature=digest,at=time.time(),rows=rows[:24],code=code),separators=(',',':'))
 if len(raw.encode())<=MAX_BYTES:xbmcgui.Window(10000).setProperty('XCMate.Catalogue85.'+identity(portal['id'],kind),raw)

def snapshot(original,portal,kind,background=False):
 import xbmcgui
 enabled=kind in ('vod','series') and __import__('home_schedule75').applicable() and callable(getattr(xbmcgui.Window(10000),'getProperty',None))
 if enabled:
  hit=cached(portal,kind)
  if hit is not None:return hit
 result=original(portal,kind,background=background)
 if enabled and isinstance(result,tuple) and len(result)==2:remember(portal,kind,*result)
 return result

def semantic(value):
 """Lease renewal is not a catalogue/image edition or a full-row reload."""
 result=dict(value);props=dict(result.get('props',{}));result['props']=props
 for k in ('XCMate.ProgrammePercent46',):props.pop(k,None)
 for k,v in list(props.items()):
  if k.endswith('Proof69') and isinstance(v,str):
   try:
    proof=json.loads(v)
    for field in ('until','resolved_at55','status68'):proof.pop(field,None)
    props[k]=json.dumps(proof,sort_keys=True,separators=(',',':'))
   except (ValueError,TypeError):pass
 result.pop('_programme46',None)
 return result

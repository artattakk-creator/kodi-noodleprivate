"""Bounded cross-interpreter missing-channel receipts, scoped by real revision."""
import json,time
PREFIX='XCMate.EpgNegative80.'

def read(key):
 import xbmcgui
 try:
  raw=xbmcgui.Window(10000).getProperty(PREFIX+str(int(key[:8],16)%128))
  value=json.loads(raw) if raw and len(raw)<16384 else {}
  if value.get('key')!=key or value.get('until',0)<=time.monotonic() or not 0<=time.time()-value.get('at',0)<65:return None
  if not isinstance(value.get('value'),dict) or value['value'].get('now'):return None
  return value
 except (ValueError,TypeError,AttributeError,RuntimeError):return None

def remember(key,record):
 if record['value'].get('now'):return
 import xbmcgui
 value=dict(record,key=key,at=time.time());raw=json.dumps(value,separators=(',',':'),default=str)
 if len(raw)<16384:xbmcgui.Window(10000).setProperty(PREFIX+str(int(key[:8],16)%128),raw)

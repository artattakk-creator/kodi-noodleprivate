"""Exact-event positive admission; file validation stays on the worker lane."""
import hashlib,math,os,time
_files={};_notes={}

def positive(event,value):
 if not isinstance(value,dict) or value.get('key')!=event.get('key'):return False
 until=value.get('until',0)
 if type(until) not in (int,float) or not math.isfinite(until) or until<=time.time():return False
 if value.get('fingerprint') and value['fingerprint']!=__import__('programme_art46').fingerprint(event):return False
 from programme_image69 import eligible
 return eligible(value,event)

def file_valid(value):
 image=value.get('image','')
 if not os.path.isabs(image):return True
 from programme_assets47 import local_uri
 if not local_uri(image):return False
 expected=value.get('sha256')
 if not expected:return True
 try:
  stat=os.stat(image);key=(image,stat.st_mtime_ns,stat.st_size,expected);now=time.monotonic()
  if now<_files.get(key,0):return True
  with open(image,'rb') as stream:actual=hashlib.sha256(stream.read(3*1024*1024+1)).hexdigest()
  if actual!=expected:return False
  _files[key]=now+30
  while len(_files)>64:_files.pop(next(iter(_files)))
  return True
 except OSError:return False

def note(event,reason):
 if reason not in ('SAME_EVENT_RETRY','EXPIRED','EVENT_CHANGED','SOURCE_CHANGED','FILE_INVALID','POLICY_CHANGED'):return
 from programme_requests68 import identity
 tag=identity(event)[:12];key=(tag,reason);now=time.monotonic()
 if now-_notes.get(key,-1e9)<30:return
 _notes[key]=now
 while len(_notes)>128:_notes.pop(next(iter(_notes)))
 import xbmc
 try:xbmc.log('[XCMate][ART80] event='+tag+' reason='+reason,xbmc.LOGINFO)
 except (AttributeError,RuntimeError):pass

def choose(event,value,previous,check_file=False):
 if positive(event,value):
  if not check_file or file_valid(value):
   if positive(event,previous) and (not check_file or file_valid(previous)):return __import__('event_art81').select(value,previous)
   return value
  note(event,'FILE_INVALID');value=dict(code='CACHE_MISMATCH',source='placeholder')
 if positive(event,previous):
  if not check_file or file_valid(previous):
   note(event,'SAME_EVENT_RETRY');return dict(previous,retry80=str((value or {}).get('code','MISSING')))
  note(event,'FILE_INVALID')
 elif isinstance(previous,dict) and previous.get('source') not in (None,'','placeholder'):
  reason='EVENT_CHANGED' if previous.get('key')!=event.get('key') else 'EXPIRED' if isinstance(previous.get('until'),(int,float)) and previous['until']<=time.time() else 'SOURCE_CHANGED' if previous.get('fingerprint')!=__import__('programme_art46').fingerprint(event) else 'POLICY_CHANGED'
  note(event,reason)
 return value

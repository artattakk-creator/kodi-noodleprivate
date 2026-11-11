"""Exact-event bookmarks and existing owner-pump tuning, no alternate player."""
import hashlib,json,math,os,tempfile,time
from pathlib import Path
def bookmark_id(event):
 return hashlib.sha256(json.dumps([str(event['pid']),str(event['sid']),int(event['start']),int(event['stop'])]).encode()).hexdigest()
def toggle(event,cancel=lambda:False):
 return __import__('reminder_bridge89').toggle(event,cancel)

def _toggle88(event,cancel=lambda:False):
 from profile_transaction import writing
 from utils import addon_data_dir
 if not event.get('sid') or not 0<int(event.get('start',0))<int(event.get('stop',0)):raise ValueError('BOOKMARK_INVALID')
 path=Path(addon_data_dir())/'guide_bookmarks_v1.json'
 with writing(timeout=.2):
  if cancel():raise InterruptedError('CANCELLED')
  if path.is_symlink() or path.exists() and path.stat().st_size>1024*1024:raise ValueError('BOOKMARK_UNSAFE')
  try:values=json.loads(path.read_bytes())
  except FileNotFoundError:values={}
  if not isinstance(values,dict):raise ValueError('BOOKMARK_INVALID')
  tag=bookmark_id(event);added=tag not in values
  if added:values[tag]={k:event[k] for k in ('pid','sid','start','stop','title')}
  else:values.pop(tag)
  raw=json.dumps(values,ensure_ascii=False,separators=(',',':')).encode()
  if len(raw)>1024*1024:raise ValueError('BOOKMARK_LIMIT')
  fd,tmp=tempfile.mkstemp(prefix='.bookmark88-',dir=path.parent)
  try:
   os.fchmod(fd,0o600)
   with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
   if cancel():raise InterruptedError('CANCELLED')
   os.replace(tmp,path)
   directory=os.open(path.parent,os.O_RDONLY)
   try:os.fsync(directory)
   finally:os.close(directory)
   if path.read_bytes()!=raw:raise OSError('BOOKMARK_READBACK')
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
  return added
def timeline(event,now=None):
 now=time.time() if now is None else now;start=event.get('start',0);stop=event.get('stop',0)
 if not 0<start<stop:return '',0
 times=time.strftime('%H:%M',time.localtime(start))+'–'+time.strftime('%H:%M',time.localtime(stop))
 minutes=max(0,math.ceil((stop-now)/60));duration=max(1,math.ceil((stop-start)/60))
 state='beginnt in '+str(max(0,math.ceil((start-now)/60)))+' Min.' if now<start else 'beendet' if now>=stop else 'noch '+str(minutes)+' Min.'
 return times+' · '+str(duration)+' Min. · '+state,max(0,min(100,(now-start)*100/(stop-start)))
def rating(value):
 score=value.get('vote_average88');votes=value.get('vote_count88')
 if not str(value.get('source','')).startswith('tmdb') or value.get('provisional85') or type(score) not in (int,float) or not math.isfinite(score) or not 0<score<=10 or type(votes) is not int or votes<=0:return ''
 return 'TMDB '+format(score,'.1f').replace('.',',')+'/10'
def tune(parent,portal,channel):
 if parent is None:return False
 sid=str(channel.get('sid',''))
 if not sid or __import__('station_rows88').header(channel):return False
 if hasattr(parent,'_entry_player') and hasattr(parent,'_play_request'):
  from guide_playback import request
  from window_lifecycle import capture
  parent._play_request=request(portal,channel,parent._entry_player,capture(parent))
  parent._leaving=True;parent._leave_after=time.monotonic()+.15
  parent._generation+=1
  pending=getattr(parent,'_pending_future',None)
  if pending:pending.cancel()
  parent._pending_future=None;parent._pending_apply=None
  return True
 if hasattr(parent,'_tune') and hasattr(parent,'index'):
  target=parent.index.by_sid.get(sid)
  if target is not None:parent._tune(target);return True
 return False

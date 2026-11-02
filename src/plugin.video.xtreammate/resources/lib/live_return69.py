"""Bounded post-Stop Home observation/recovery, independent of player teardown."""
import hashlib,json,time
from urllib.parse import urlsplit,parse_qs,urlencode
_seen={}
def _trace(value,stage,reason='NONE'):
 allowed={'BEGIN','HOME_REQUESTED','HOME_VISIBLE','COMPLETE','FAILED','WAIT_MODAL','WAIT_OWNER'}
 if stage not in allowed:return
 session=value.get('session',{});digest=hashlib.sha256(str(session.get('nonce','')).encode()).hexdigest()[:12]
 signature=(digest,stage,reason)
 if signature in _seen:return
 _seen[signature]=time.monotonic()
 while len(_seen)>64:_seen.pop(next(iter(_seen)))
 try:
  import xbmc,xbmcgui
  elapsed=max(0,int((time.monotonic()-value.get('return_started69',time.monotonic()))*1000))
  xbmc.log('[XCMate][RETURN69] session='+digest+' stage='+stage+' reason='+reason+' elapsed_ms='+str(elapsed)+' window='+str(xbmcgui.getCurrentWindowId())+' dialog='+str(xbmcgui.getCurrentWindowDialogId()),xbmc.LOGINFO)
 except (AttributeError,RuntimeError):pass
def begin(value):
 from live_exit import state,_save
 current=state()
 if not current or current['session']['nonce']!=value['session']['nonce'] or current['phase'] not in ('home','complete'):return
 if not current.get('return_started69'):
  current['return_started69']=time.monotonic();current['return_deadline69']=time.monotonic()+8
  current['return_attempts69']=0;current['return_stage69']='BEGIN';_save(current);_trace(current,'BEGIN')
def _folder():
 import xbmc
 try:
  parts=urlsplit(xbmc.getInfoLabel('Container.FolderPath'));query=parse_qs(parts.query)
  return parts,query
 except (ValueError,TypeError):return None,{}
def visible(value,snapshot):
 if snapshot.get('modal') or snapshot.get('dialog') not in (0,-1,9999) or snapshot.get('updating'):return False
 if value.get('origin_window48')==10000:return snapshot.get('window')==10000
 parts,query=_folder()
 return bool(snapshot.get('window')==10025 and parts and parts.scheme=='plugin' and parts.netloc=='plugin.video.xtreammate' and query.get('action')==['xcmate_home'] and query.get('pid')==[str(value['session']['pid'])])
def _commit(value,stage,reason):
 from live_exit import state,_save
 current=state()
 if not current or current['session']['nonce']!=value['session']['nonce'] or current.get('return_stage69') in ('COMPLETE','FAILED'):return False
 current.update({k:v for k,v in value.items() if k.startswith('return_')})
 current['return_stage69']=stage
 if stage=='COMPLETE':current['phase']='complete'
 if stage=='FAILED':current['phase']='failed'
 _save(current);_trace(current,stage,reason);return True

def poll():
 from live_exit import state
 value=state()
 if not value or value['phase'] not in ('home','complete') or value.get('return_stage69') in ('COMPLETE','FAILED'):return False
 begin(value);value=state()
 if not value:return False
 from live_return59 import stop_confirmed
 from exit_jobs import state as stop_job69
 if not stop_confirmed(value,stop_job69()):
  if time.monotonic()>=value.get('return_deadline69',time.monotonic()):_commit(value,'FAILED','STOP_ACK_UNCONFIRMED')
  return False
 import xbmc
 from window_lifecycle import state as native,lease
 snapshot=native()
 # The service already waits for native Stop ACK. No Player.stop or PlayerControl
 # is ever issued here; any new/foreign media aborts this navigation attempt.
 try:
  player=xbmc.Player()
  if getattr(player,'isPlaying',player.isPlayingVideo)():
   _commit(value,'FAILED','MEDIA_ACTIVE');return False
 except (AttributeError,RuntimeError):
  _commit(value,'FAILED','PLAYER_STATE_UNAVAILABLE');return False
 from live_overlay import session_from_property
 import xbmcgui
 current=session_from_property(xbmcgui.Window(10000).getProperty('XtreamMate.LiveSession'))
 if current and current.get('nonce')!=value['session']['nonce']:
  _commit(value,'FAILED','NEW_SESSION');return False
 if visible(value,snapshot):
  _trace(value,'HOME_VISIBLE');_commit(value,'COMPLETE','VISIBLE_AND_USABLE');return True
 now=time.monotonic()
 modal=snapshot.get('modal') or snapshot.get('dialog') not in (0,-1,9999)
 if modal:
  from programme_lifecycle69 import cancel_matching
  own=cancel_matching(value,snapshot)
  if now>=value.get('return_deadline69',now):_commit(value,'FAILED','OWN_MODAL_NOT_RELEASED' if own else 'FOREIGN_MODAL_RETAINED')
  else:_trace(value,'WAIT_MODAL','OWN_CANCEL_REQUESTED' if own else 'FOREIGN_MODAL_RETAINED')
  return False
 if now>=value.get('return_deadline69',now):
  _commit(value,'FAILED','RETURN_DEADLINE');return False
 # Allow the original fast path a short natural release interval. Directory
 # updating is not a permanent veto after a positively stopped own session.
 if now-value['return_started69']<1:return False
 parts,query=_folder()
 own_folder=bool(parts and parts.scheme=='plugin' and parts.netloc=='plugin.video.xtreammate' and query.get('pid')==[str(value['session']['pid'])])
 if snapshot.get('window') not in (10000,10025,12005):
  from programme_lifecycle69 import cancel_matching
  if cancel_matching(value,snapshot):
   _trace(value,'WAIT_OWNER','OWN_CANCEL_REQUESTED');return False
  _commit(value,'FAILED','FOREIGN_WINDOW');return False
 if snapshot.get('updating') and not own_folder:
  _trace(value,'WAIT_OWNER','FOREIGN_DIRECTORY');return False
 if lease():
  # An active own Guide/detail is asked to close on its actual owner thread.
  from programme_lifecycle69 import cancel_matching
  cancel_matching(value,snapshot)
  if not own_folder:
   _trace(value,'WAIT_OWNER','UNCONFIRMED_LEASE');return False
 attempts=value.get('return_attempts69',0)
 if attempts>=2 or now<value.get('return_next69',0):return False
 destination='Home' if value.get('origin_window48')==10000 else 'Videos,plugin://plugin.video.xtreammate/?'+urlencode(dict(action='xcmate_home',pid=value['session']['pid'],entry='return'))+',return'
 value['return_attempts69']=attempts+1;value['return_next69']=now+3;value['return_stage69']='HOME_REQUESTED'
 from live_exit import state,_save
 fresh=state()
 if not fresh or fresh['session']['nonce']!=value['session']['nonce'] or fresh['phase'] not in ('home','complete'):return False
 fresh.update({k:v for k,v in value.items() if k.startswith('return_')});_save(fresh)
 xbmc.executebuiltin('ActivateWindow('+destination+')',wait=False)
 _trace(fresh,'HOME_REQUESTED','OWN_RETURN_RECOVERY')
 return False

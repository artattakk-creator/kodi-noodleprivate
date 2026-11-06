"""Synthetic owned media/native Stop controller; actual Kodi player and ACK."""
import sys,json,time,uuid,hashlib,traceback
from pathlib import Path
import xbmc,xbmcgui,xbmcaddon
native=xbmcaddon.Addon;xbmcaddon.Addon=lambda *a,**k:native(*a,**k) if a or k else native('plugin.video.xtreammate')
sys.path.insert(0,native('plugin.video.xtreammate').getAddonInfo('path')+'/resources/lib')
command=json.loads(Path('/root/media77-command.json').read_text())
try:
 if command['action']=='start':
  from media_progress import PROPERTY,UNIQUE_ID
  from media_autoplay import Events,observe
  kind=command['kind'];nonce=uuid.uuid4().hex;session=dict(pid='fixture67',sid='native77',nonce=nonce,at=time.time(),kind=kind,series_id='synthetic77',season='1',episode='1')
  xbmcgui.Window(10000).setProperty(PROPERTY,json.dumps(session))
  item=xbmcgui.ListItem('Synthetic native .77 '+kind,path='/root/media/sample.mp4')
  item.setInfo('video',dict(title='Synthetic native .77',mediatype='episode' if kind=='episode' else 'movie'))
  item.setUniqueIDs({UNIQUE_ID:nonce});item.setProperty('IsPlayable','true')
  events=Events();observer=observe(events)
  xbmc.Player().play('/root/media/sample.mp4',item)
  # Keep the real native callback object alive through Stop in this invoker.
  for _ in range(200):
   if Path('/root/media77-stop-request').exists():break
   xbmc.sleep(50)
  else:raise RuntimeError('STOP_REQUEST_NOT_RECEIVED')
  from exit_jobs import request,poll,state,blocked
  if not request(reason='USER_BACK'):raise RuntimeError('OWNED_STOP_NOT_ACCEPTED')
  for _ in range(240):
   poll();value=state() or {}
   if value.get('worker_done') and value.get('result')=='complete':break
   if value.get('phase') in ('failed','timeout'):raise RuntimeError('NATIVE_STOP_'+str(value.get('result') or value['phase']))
   xbmc.sleep(25)
  else:raise RuntimeError('NATIVE_STOP_ACK_TIMEOUT')
  from native_stop41 import returned
  if not returned(value) or blocked():raise RuntimeError('STOP_WITHOUT_NATIVE_ACK')
  from media_state import progress
  record=progress('fixture67',kind,'native77','synthetic77','1')
  Path('/root/media77-result.json').write_text(json.dumps(dict(kind=kind,native_ack=True,phase=value['phase'],stops=1,progress_position=record.get('position',0),snapshot=value.get('snapshot77'),callbacks=[k for k,s in events.drain()],android='ANDROID_NOT_TESTED')))
 elif command['action']=='live_stop':
  from exit_jobs import request,poll,state
  from native_stop41 import returned
  if not request(reason='USER_BACK'):raise RuntimeError('LIVE_STOP_NOT_ACCEPTED')
  for _ in range(240):
   poll();value=state() or {}
   if value.get('worker_done') and value.get('result')=='complete':break
   if value.get('phase') in ('failed','timeout'):raise RuntimeError('LIVE_STOP_TIMEOUT')
   xbmc.sleep(25)
  if not returned(value):raise RuntimeError('LIVE_NO_ACK')
  Path('/root/media77-result.json').write_text(json.dumps(dict(kind='live',native_ack=True,phase=value['phase'],stops=1,android='ANDROID_NOT_TESTED')))
except Exception:
 Path('/root/media77-error.txt').write_text(traceback.format_exc());raise

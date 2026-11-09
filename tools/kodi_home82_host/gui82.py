"""Every native .81 case plus real paused-worker/rail-idle regression."""
from pathlib import Path
import json,os,time,importlib,threading,io
original_write82=Path.write_text
original_read82=Path.read_text
finished82=False

def read82(self,*args,**kwargs):
 text82=original_read82(self,*args,**kwargs)
 if str(self)=='/base_gui79.py':
  # Snapshot screenshot bytes once; Kodi may still be finishing the PNG.
  # Retry incomplete data, retaining every original geometry/pixel assertion.
  text82=text82.replace('Image.open(path)','Image.open(io.BytesIO(path.read_bytes()))')
  text82=text82.replace('except (OSError,ValueError):','except (OSError,ValueError,SyntaxError):')
 return text82

def stability82():
 from unittest.mock import patch
 import artwork_db as db
 import widget_assets69 as assets
 from widget_data41 import snapshot
 from widget_refresh45 import publish,read
 from portals import get_active
 # The .81 fixture has deliberately completed service teardown. A new module
 # here models a new disposable service session, not an app profile migration.
 assets=importlib.reload(assets);portal82=get_active()[0]
 from widget_assets69 import renderable
 originals82={}
 for kind82 in ('live','vod','series'):
  # Earlier cases exercise native read-only directory replies. This new
  # fault case explicitly seeds the writable publication under test.
  selected82,_=snapshot(portal82,kind82)
  check(publish(portal82,kind82,selected82),'CACHED82_INITIAL_PUBLISH_FAILED')
  frame82=read(portal82['id'],kind82)
  if frame82 is None:
   from widget_refresh45 import path as frame_path82
   raw82=Path(frame_path82(portal82['id'],kind82))
   diagnostic82=dict(kind=kind82,exists=raw82.exists(),pid=portal82['id'])
   if raw82.exists():diagnostic82['raw']=json.loads(raw82.read_text())
   Path('/root/stability82-error.json').write_text(json.dumps(diagnostic82))
  check(frame82 is not None,'CACHED82_FRAME_MISSING')
  originals82[kind82]=frame82['art_status74']
  # The historical native fixture deliberately has no provider logo for
  # sender 87. Keep that negative case; never invent an image to claim READY.
  missing82=[v['props']['XCMate.MediaId'] for v in frame82['items'] if not renderable(v['art'].get('poster'))]
  check(not missing82 or kind82=='live' and missing82==['87'],('CACHED82_UNEXPECTED_MISSING',kind82,missing82))
 # The preceding movie-return case deliberately backs through native Home.
 # Wait for that navigation and the 300ms sideblade animation, then establish
 # the visible Live test view through its real Back navigation. A dimmed
 # menu is not a lost logo; no test-view actions are sent during the soak.
 settled82=None
 for _ in range(160):
  if xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):
   settled82=None;xbmc.sleep(50);continue
  menu82=home.getProperty('ShowViewSubMenu')=='show' or xbmc.getCondVisibility('ControlGroup(9001).HasFocus()') or home.getFocusId()==900
  if menu82:
   # BINGIE's native 900 onback clears ShowViewSubMenu and enters 77777.
   # setFocusId alone does not clear that independent skin property.
   home.setFocusId(900);xbmc.executebuiltin('Action(Back)',wait=False);settled82=None
   xbmc.sleep(100);continue
  elif home.getFocusId()!=2510:
   home.setFocusId(2510);home.getControl(2510).selectItem(0);settled82=None
  visible82=xbmc.getCondVisibility('Control.IsVisible(296751)')
  if home.getFocusId()==2510 and visible82 and not menu82:
   if settled82 is None:settled82=time.monotonic()
   if time.monotonic()-settled82>=1:break
  else:settled82=None
  pump();xbmc.sleep(50)
 else:raise RuntimeError('VIEW82_PRECONDITION_NOT_READY')
 _,baseline82=capture('home82-before-pause')
 check(max(abs(a-b) for a,b in zip(baseline82.getpixel((330,665)),(20,90,150)))<=8,'VIEW82_BASELINE_LOGO_NOT_READY')
 filename82=db.path();old82=db._failures.get(filename82)
 seconds82=max(2,int(os.environ.get('XCMATE_FAULT_IDLE82','0')))
 db._failures[filename82]=dict(identity=db._identity(filename82),code='BUSY',retry_after=time.time()+seconds82+60)
 rows82,_=snapshot(portal82,'vod');job82=dict(rows82[0],sid='worker-probe82',name='Synthetic paused worker probe')
 errors82=[];original_hook82=threading.excepthook
 def hook82(args):
  if args.thread.name=='XCMate-provider-art69':errors82.append(args.exc_type.__name__)
  else:original_hook82(args)
 threading.excepthook=hook82
 checkpoints82=[];started82=time.monotonic();next_poll82=0;recovered82=False
 try:
  check(assets.prepare(portal82,'live',[job82]),'WORKER82_NOT_STARTED');worker82=assets._thread
  for _ in range(100):
   if assets._deferred82:break
   xbmc.sleep(20)
  check(bool(assets._deferred82),'WORKER82_PAUSE_NOT_OBSERVED')
  for _ in range(443):check(not assets.prepare(portal82,'live',[job82]),'WORKER82_DUPLICATE')
  while time.monotonic()-started82<seconds82:
   pump();elapsed82=time.monotonic()-started82
   check(assets._thread is worker82 and worker82.is_alive() and not assets._fatal82,'WORKER82_DIED_OR_RESPAWNED')
   if elapsed82>=next_poll82:
    next_poll82=elapsed82+60;states82={}
    for kind82 in ('live','vod','series'):
     selected82,code82=snapshot(portal82,kind82)
     # Inject a missing optional art-DB read, not a missing provider catalogue.
     with patch('programme_assets47.read_many',return_value={}):
      check(publish(portal82,kind82,selected82),'RAIL82_NOT_PUBLISHED')
     frame82=read(portal82['id'],kind82);states82[kind82]=frame82['art_status74']
     check(states82[kind82]==originals82[kind82],'RAIL82_READY_DOWNGRADE')
    checkpoints82.append(dict(elapsed=round(elapsed82,2),art=states82))
    path82,rgb82=capture('home82-paused-'+str(int(elapsed82)))
    check(max(abs(a-b) for a,b in zip(rgb82.getpixel((330,665)),(20,90,150)))<=8,'LOGO82_PIXELS_LOST')
   xbmc.sleep(100)
  check(not errors82,'WORKER82_UNHANDLED_EXCEPTION')
  db._failures.pop(filename82,None)
  for _ in range(150):
   if not assets._pending:recovered82=True;break
   xbmc.sleep(20)
  check(recovered82 and assets._thread is worker82 and worker82.is_alive(),'WORKER82_NOT_RECOVERED')
 finally:
  if old82 is None:db._failures.pop(filename82,None)
  else:db._failures[filename82]=old82
  assets.shutdown();worker82=assets._thread
  if worker82:worker82.join(5)
  threading.excepthook=original_hook82
  check(not worker82 or not worker82.is_alive(),'WORKER82_DID_NOT_STOP')
  # Publication starts the existing programme worker inside this disposable
  # GUI script too. Match service teardown before native Application.Quit;
  # no process killing or relaxed restart timeout may hide leaked invokers.
  for name82 in ('programme_urls55','programme_requests68','programme_art46'):
   module82=__import__(name82);module82.shutdown()
   owned82=[getattr(module82,'_thread',None)]+list(getattr(module82,'_workers',[]))
   for thread82 in owned82:
    if thread82 and thread82 is not threading.current_thread():thread82.join(5)
   check(not any(t and t.is_alive() for t in owned82),'PROGRAMME82_FIXTURE_NOT_STOPPED')
 return dict(status='PASS',scope='real Linux Kodi + injected artwork DB pause',seconds=round(time.monotonic()-started82,2),duplicate_polls=443,worker_threads=1,recovered_same_worker=recovered82,unhandled=errors82,checkpoints=checkpoints82,android='ANDROID_NOT_TESTED')

def write82(self,data,*args,**kwargs):
 global finished82
 if str(self)=='/root/home75.json' and not finished82:
  finished82=True
  report82=json.loads(data);report82['stability82']=stability82()
  data=json.dumps(report82,indent=2)
 return original_write82(self,data,*args,**kwargs)
Path.write_text=write82
Path.read_text=read82
try:exec(compile(Path('/base_gui81.py').read_text(),'native-home82','exec'),globals())
finally:
 Path.write_text=original_write82;Path.read_text=original_read82

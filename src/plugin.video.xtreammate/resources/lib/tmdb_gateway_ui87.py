"""Explicit status/pair/revoke UI; one bounded job, no blocking key callback."""
import threading,time
from localization import tr
import tmdb_gateway_client87 as client
_busy=threading.Lock()
def task(function):
 import xbmc,xbmcgui
 if not _busy.acquire(False):return 'WORKER_BUSY'
 stop=threading.Event();result=[];progress=xbmcgui.DialogProgress();started=False
 def run():
  try:result.append(function(stop.is_set))
  except client.GatewayError as error:result.append(error.code)
  except Exception:result.append('SERVER_UNAVAILABLE')
  finally:_busy.release()
 try:
  progress.create(tr(37130),tr(37131));threading.Thread(target=run,name='XCMate-gateway87',daemon=True).start();started=True
  end=time.monotonic()+8;monitor=xbmc.Monitor()
  while not result and time.monotonic()<end:
   if progress.iscanceled() or monitor.waitForAbort(.05):stop.set();return 'USER_CANCELLED'
  return result[0] if result else 'GATEWAY_TIMEOUT'
 finally:
  stop.set();progress.close()
  if not started:_busy.release()
def show():
 import xbmcgui,xbmcaddon
 dialog=xbmcgui.Dialog()
 while True:
  state=client.status();choice=dialog.select(tr(37130)+' · '+state,[tr(37132),tr(37133),tr(37134),tr(37135),tr(37136)])
  if choice not in range(4):return
  if choice==0:
   if state=='GATEWAY_PAIRED':dialog.ok(tr(37130),task(lambda cancel:client.check(cancel)))
   elif client.configured():dialog.ok(tr(37130),tr(37137))
   else:dialog.ok(tr(37130),tr(37138))
   continue
  if choice==3:
   if not dialog.yesno(tr(37130),tr(37139),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):continue
   code=task(lambda cancel:client.revoke(cancel))
  elif choice==1:
   if state=='LOCAL_TOKEN_VALID':dialog.ok(tr(37130),tr(37140));continue
   if not dialog.yesno(tr(37130),tr(37141),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):continue
   code=task(lambda cancel:client.begin(cancel))
   if code=='PENDING':
    public=client.public_pairing();dialog.ok(tr(37130),tr(37142,public['user_code']));continue
  else:code=task(lambda cancel:client.poll(cancel))
  if code=='GATEWAY_PAIRED':
   from tmdb_access61 import activate
   activate(xbmcaddon.Addon(),automatic=True)
  dialog.ok(tr(37130),tr(37143)+' '+code)

"""100 real plugin-invoker + native WindowXML detail/Back cycles, Linux only.

Executed in the existing disposable Kodi/BINGIE renderer after its pixel proof.
Metadata fixtures are synthetic. Router/entry/owner/native input stay real.
"""
from pathlib import Path
import json,time,threading
import xbmc,xbmcgui,xbmcaddon
from urllib.parse import urlencode
from portals import get_active
from widget_group46 import snapshot
from widget_data41 import snapshot as media_snapshot
from widget_live47 import publish
from programme_events46 import load
from programme_window46 import ProgrammeWindow46

def run():
 home=xbmcgui.Window(10000);portal=get_active()[0];stations=snapshot(portal)
 log=Path('/root/.kodi/temp/kodi.log');offset=log.stat().st_size
 stop=threading.Event();errors=[];passes=[];started=time.monotonic()
 def check(condition,code):
  if not condition:raise RuntimeError(code)
 def wait(predicate,code,seconds=6):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   if predicate():return
   xbmc.sleep(25)
  raise RuntimeError(code)
 def background():
  try:
   while not stop.is_set():
    __import__('widget_group46').infos(portal,stations[:5])
    publish(portal,'live',stations)
    for kind in ('vod','series'):
     rows,_=media_snapshot(portal,kind);publish(portal,kind,rows)
    stop.wait(.4)
  except Exception as error:errors.append(type(error).__name__)
 worker=threading.Thread(target=background,name='Synthetic86-background');worker.start()
 try:
  for cycle in range(100):
   xbmc.executebuiltin('ActivateWindow(Home)',wait=False)
   wait(lambda:xbmcgui.getCurrentWindowId()==10000,'NAV86_HOME_TIMEOUT')
   home.setFocusId(2510);home.getControl(2510).selectItem(cycle%5)
   # Actual child dialog on the selected locally stored EPG programme.
   row=stations[cycle%5];event=load(portal,row)
   view=ProgrammeWindow46('XCMateProgramme46.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p')
   view.configure(portal,row,event);view.show()
   wait(lambda:view._ready,'NAV86_PROGRAMME_INIT')
   for _ in range(4):view.pump();xbmc.sleep(25)
   xbmc.executebuiltin('Action(Back)',wait=False)
   wait(lambda:view._closed,'NAV86_PROGRAMME_BACK')
   kind='vod' if cycle%2==0 else 'series';sequence=str(cycle)
   xbmcgui.Window(10000).setProperty('XCMate.Nav90.Sequence',sequence)
   home.clearProperty('XCMate.Nav86.State')
   direct=cycle%3==0
   action='media_detail' if direct else 'movies_home' if kind=='vod' else 'series_home'
   query=urlencode(dict(action=action,pid=portal['id'],kind=kind,sid='0' if direct else '',nav86=sequence))
   xbmc.executebuiltin('RunPlugin(plugin://plugin.video.xtreammate/?'+query+')',wait=False)
   def state():
    raw=xbmcgui.Window(10000).getProperty('XCMate.Nav86.State');value=json.loads(raw) if raw else {}
    return value if value.get('sequence')==sequence else {}
   if not direct:
    wait(lambda:state().get('mode')=='landing' and state().get('rows',0)>0 and state().get('focus') in (110,111,112),'NAV86_LANDING_TIMEOUT')
    # Real IR-equivalent native input, not direct calls to Python callbacks.
    xbmc.executebuiltin('Action(Select)',wait=False)
   wait(lambda:state().get('mode')=='detail' and state().get('actions',0)>0,'NAV86_DETAIL_TIMEOUT')
   xbmc.executebuiltin('Action(Back)',wait=False)
   wait(lambda:state().get('mode')=='landing','NAV86_DETAIL_BACK_TIMEOUT')
   xbmc.executebuiltin('Action(Back)',wait=False)
   receipt=Path('/root/nav86-route-'+sequence+'.json')
   wait(receipt.exists,'NAV86_INVOKER_NOT_RETURNED',seconds=4)
   check(json.loads(receipt.read_text()).get('returned'),'NAV86_ROUTE_FAILED')
   check(not errors,'NAV86_BACKGROUND_FAILED')
   passes.append(dict(cycle=cycle,kind=kind,route=action,detail_back='PASS',route_return='PASS'))
 finally:
  stop.set();worker.join(2)
  xbmcgui.Window(10000).clearProperty('XCMate.Nav90.Sequence')
  with log.open('rb') as stream:stream.seek(offset);tail=stream.read().decode(errors='replace')
  counts={name:tail.count(text) for name,text in dict(native_index='EXCEPTION: Index out of range',dispatch_failed='DISPATCH_FAILED',directory_failed='GetDirectory - Error',invoker_kill='script didn\'t stop in 5 seconds').items()}
  last_raw=xbmcgui.Window(10000).getProperty('XCMate.Nav86.State');last_state=json.loads(last_raw) if last_raw else {}
  report=dict(last_state=last_state,window=xbmcgui.getCurrentWindowId(),dialog=xbmcgui.getCurrentWindowDialogId(),status='PASS' if len(passes)==100 and not any(counts.values()) and not errors and not worker.is_alive() else 'FAIL',cycles=len(passes),counts=counts,elapsed_ms=int((time.monotonic()-started)*1000),background_errors=errors,android='ANDROID_NOT_TESTED',cases=passes)
  Path('/root/navigation86.json').write_text(json.dumps(report,indent=2))
 check(report['status']=='PASS','NAV86_FINAL_COUNTER_FAILED '+json.dumps(counts))
 print('NAVIGATION86 '+json.dumps({k:v for k,v in report.items() if k!='cases'}),flush=True)

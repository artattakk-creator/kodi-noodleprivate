"""Native .87 renderer with real non-XCMate plugin source paths.

The independent addons/data are synthetic. This proves Kodi/BINGIE consumers,
not real MP3/SHOUTcast services or physical Android hardware.
"""
from pathlib import Path
line87="Path('/root/'+('post75.json' if cold else 'visible84.json')).write_text(json.dumps(report,indent=2))"
# Remove only the actual final write line, never the same text inside the
# legacy wrapper's string replacement (that would re-enable early success).
base87='\n'.join(line for line in Path('/base_gui86.py').read_text().splitlines() if line.strip()!=line87)
# The fixture disables the actual service: model its existing one-second
# preparation tick on the already owned data lane, including lease renewal
# and read-only cache recovery. Never claim unattended rendering without it.
anchor87="base=Path('/base_gui84.py').read_text()"
assert base87.count(anchor87)==1,'NATIVE87_BASE_READER_CHANGED'
base87=base87.replace(anchor87,anchor87+"\nbase=base.replace(\"hero_epg63.prepare(portal['id'])\",\"hero_epg63.prepare(portal['id']);__import__('widget_fast69').prepare()\")")
# Every final Hero screenshot must prove actual pixels, not just Kind/READY.
base87=base87.replace("shot86,rgb86=capture('visible84-hero86-final')", """for frame87 in range(100):
 pump();xbmc.sleep(100)
 shot86,rgb86=capture('visible84-hero86-final')
 final_pixels87=sum(max(abs(a-b) for a,b in zip(pixel,(20,80,130)))<=8 for pixel in rgb86.crop((300,50,1100,520)).getdata())
 logo_pixels87=sum(max(abs(a-b) for a,b in zip(pixel,(25,100,160)))<=8 for pixel in rgb86.crop((270,640,470,715)).getdata())
 if final_pixels87>3000 and logo_pixels87>1500:break
else:
 from widget_assets69 import read as refs87
 from logo_manifest86 import read as logos87
 rows87=live_rows(portal);a87=__import__('widget_assets69');first87=rows87[0]
 print('LOGO87_NATIVE_DIAGNOSTIC '+json.dumps(dict(assets=len(refs87(portal,'live',rows87)),logos=len(logos87(portal,rows87)),source_present=bool(__import__('station_logos87').source(first87)),worker_alive=bool(a87._thread and a87._thread.is_alive()),worker_stopped=a87._stop.is_set(),fatal=a87._fatal82,pending=len(a87._pending),deferred=[v[1] for v in a87._deferred82.values()],directory_poster_present=bool(xbmc.getInfoLabel('Container(2510).ListItem.Art(poster)')))),flush=True)
 raise RuntimeError(('HERO87_FINAL_PIXELS_MISSING',final_pixels87,logo_pixels87))""")

# .88 has the approved opposite composition: text left, photo right.
base87=base87.replace("getWidth()==1620", "getWidth()==1760")

# Complete logo/EPG/Hero reference readiness hides the compact loading line.
# Preserve the visible-status assertion while incomplete, and verify all
# prerequisites before accepting the deliberately hidden completed status.
status88="""status88=json.loads(home.getProperty('XCMate.Home86.Rail') or '{}')
if home.getProperty('XCMate.Home86.State')=='REFERENCE_READY':
 check(status88.get('total')==88 and status88.get('local',0)+status88.get('ram',0)>=88,'STATUS88_FALSE_COMPLETE')
 check(not xbmc.getCondVisibility('Control.IsVisible(296887)'),'STATUS88_COMPLETED_LINE_NOT_HIDDEN')
else:check(xbmc.getCondVisibility('Control.IsVisible(296887)'),'STATUS86_NOT_VISIBLE')"""
base87=base87.replace("check(xbmc.getCondVisibility('Control.IsVisible(296887)'),'STATUS86_NOT_VISIBLE')",status88)

base87=base87.replace("rgb86.crop((300,30,1100,620))", "rgb86.crop((1000,30,1800,620))")
base87=base87.replace("rgb86.crop((300,50,1100,520))", "rgb86.crop((1000,50,1800,520))")
anchor88="base=Path('/base_gui84.py').read_text()"
adapt88="\nbase=base.replace('(560,280)','(680,560)').replace('(480,160,1040,440)','(1050,30,1730,590)').replace('(300,50,1100,520)','(1000,50,1800,520)').replace('(1355,300)','(155,300)').replace('(300,50,1100,500)','(1000,50,1800,500)').replace('Synthetic Linux Kodi .84','Synthetic Linux Kodi .88')"
base87=base87.replace(anchor88,anchor88+adapt88)
# gui86 constructs a separate settled-pixel loop from a literal; cover its
# generated assertion as well as the inner gui84 original.
base87=base87.replace('(300,50,1100,520)','(1000,50,1800,520)')

exec(compile(base87,'/base_gui86.py','exec'),globals())
import sys
sys.path.insert(0,'/')
from spec87 import FOREIGN,uri
from widget_inventory87 import collect,compare
import xbmcvfs
profile87=Path(xbmcvfs.translatePath('special://profile/'));skin87=Path(xbmcvfs.translatePath('special://skin/'))
inventory87=collect(profile87,skin87)
check(sum(v['external'] for v in inventory87['widgets'])==13,'FOREIGN87_SAVED_DEFINITIONS_LOST')
if not cold:
 import runpy
 runpy.run_path('/icons86.py')['run'](capture)
 runpy.run_path('/navigation86.py')['run']()
 report['native_icons87']=json.loads(Path('/root/icons86.json').read_text())
 report['native_navigation87']=json.loads(Path('/root/navigation86.json').read_text())
foreign_cases87=[]
for menu87,indices87 in ((0,range(5)),(1,range(8))):
 home.setFocusId(900);home.getControl(900).selectItem(0)
 for _ in range(20):pump();xbmc.sleep(50)
 for index87 in indices87:
  control87=2540+index87*10 if menu87==0 else 3510+index87*10
  home.setFocusId(control87)
  for pending87 in range(200):
   if pending87%10==0:home.setFocusId(control87)
   if xbmc.getInfoLabel('Container('+str(control87)+').NumItems')=='8':break
   pump();xbmc.sleep(50)
  check(xbmc.getInfoLabel('Container('+str(control87)+').NumItems')=='8',('FOREIGN87_DIRECTORY_EMPTY',menu87,index87,control87,xbmcgui.getCurrentWindowId(),xbmcgui.getCurrentWindowDialogId(),home.getFocusId(),xbmc.getInfoLabel('Container('+str(control87)+').NumItems'),xbmc.getCondVisibility('Control.IsVisible('+str(control87)+')')))
  home.setFocusId(control87);home.getControl(control87).selectItem(0)
  for _ in range(30):pump();xbmc.sleep(50)
  name87,addon87,content87,target87,color87=FOREIGN[index87]
  check(xbmc.getInfoLabel('Container('+str(control87)+').ListItem.Property(Foreign87)')==str(index87),('FOREIGN87_WRONG_SOURCE',control87))
  check(home.getFocusId()==control87,('FOREIGN87_FOCUS_LOST',control87,home.getFocusId()))
  path87,rgb87=capture('visible84-foreign87-'+('cold-' if cold else 'warm-')+str(menu87)+'-'+str(index87))
  pixels87=sum(max(abs(a-b) for a,b in zip(pixel,color87))<=8 for pixel in rgb87.crop((260,640,1890,1040)).getdata())
  check(pixels87>1500,('FOREIGN87_NOT_VISIBLE',menu87,index87,pixels87))
  foreign_cases87.append(dict(menu=menu87,row=index87,addon=addon87,items=8,native_focus=control87,rail_pixels=pixels87,screenshot=path87.name))
  # First and last independent sources really receive OK and start a native
  # local WAV. This is an audio engine smoke, not a remote-provider media test.
  if menu87==1 and index87 in (0,7):
   xbmc.executebuiltin('Action(Select)',wait=False)
   for _ in range(100):
    if xbmc.Player().isPlaying():break
    xbmc.sleep(50)
   check(xbmc.Player().isPlaying(),('FOREIGN87_OK_DID_NOT_START',index87))
   xbmc.executebuiltin('PlayerControl(Stop)',wait=False)
   for _ in range(100):
    if not xbmc.Player().isPlaying():break
    xbmc.sleep(50)
   check(not xbmc.Player().isPlaying(),'FOREIGN87_NATIVE_STOP_TIMEOUT')
   xbmc.executebuiltin('ActivateWindow(Home)',wait=False)
   for settle87 in range(100):
    if xbmcgui.getCurrentWindowId()==10000 and xbmcgui.getCurrentWindowDialogId() in (0,-1,9999) and not xbmc.getCondVisibility('System.HasActiveModalDialog'):break
    xbmc.sleep(50)
   check(xbmcgui.getCurrentWindowId()==10000,'FOREIGN87_RETURN_NOT_HOME')
   xbmc.sleep(500)
   home.setFocusId(900);home.getControl(900).selectItem(0);xbmc.sleep(200)
compare(profile87,inventory87)
# Ten complete transitions among distinct external sources keep their rows,
# definitions and focus. No foreign consumer is routed through XCMate.
# Native audio return opens BINGIE's independent sideblade. Close that
# actual level with Back before testing row-to-row focus; setFocus alone
# cannot clear ShowViewSubMenu and the skin's onback animation.
for settle87 in range(160):
 menu_open87=home.getProperty('ShowViewSubMenu')=='show' or home.getFocusId()==900
 if menu_open87:
  home.setFocusId(900);xbmc.executebuiltin('Action(Back)',wait=False);xbmc.sleep(100);continue
 if xbmcgui.getCurrentWindowId()==10000 and xbmcgui.getCurrentWindowDialogId() in (0,-1,9999):break
 xbmc.sleep(50)
else:raise RuntimeError('FOREIGN87_MENU_RETURN_NOT_READY')
for cycle87 in range(10):
 for cid87 in (3510,3530,3540,3550,3560,3580):
  home.setFocusId(cid87)
  for settle87 in range(80):
   if home.getFocusId()==cid87:break
   xbmc.sleep(25)
  check(home.getFocusId()==cid87,('FOREIGN87_CYCLE_FOCUS_LOST',cycle87,cid87,home.getFocusId(),home.getProperty('ShowViewSubMenu')))
  check(xbmc.getInfoLabel('Container('+str(cid87)+').NumItems')=='8','FOREIGN87_CYCLE_EMPTY')
compare(profile87,inventory87)
from hero_timing87 import summary
report['version']=xbmcaddon.Addon().getAddonInfo('version')
report['foreign87']=dict(status='PASS',saved_definitions=13,independent_sources=len({v[1] for v in FOREIGN}),cases=foreign_cases87,cycles=10,native_ok_audio=2,inventory_sha256=inventory87['sha256'],unchanged='PASS',source_kind='Synthetic independent plugins with actual non-XCMate URLs',android='ANDROID_NOT_TESTED')
report['timing87']=summary();report['reference_image']='REFERENZBILD_NICHT_VERFÜGBAR'

if not cold:
 # Actual native WindowXML, production event/read/result/pump and decoded
 # byte bridge. Synthetic EPG/content, explicitly not physical Android.
 from programme_window46 import ProgrammeWindow46
 from programme_actions88 import timeline
 detail88=ProgrammeWindow46('XCMateProgramme46.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
 row88=live_rows(portal)[0];event88=load(portal,row88)
 from programme_urls55 import resolve
 def image88():
  value88=resolve(event88,allow_lookup=True,url_mode69=True)
  completed(event88,value88)
 worker88=threading.Thread(target=image88);worker88.start()
 while worker88.is_alive():pump();xbmc.sleep(50)
 detail88.configure(portal,row88,event88,None);detail88.show()
 began88=time.monotonic();marks88=[];last88=''
 try:
  while time.monotonic()-began88<306:
   detail88.pump();xbmc.sleep(100)
   elapsed88=time.monotonic()-began88
   if elapsed88>45:
    __import__('programme_requests68').status(event88,'IMAGE_LOOKUP_TIMEOUT',dict(source='placeholder',code='IMAGE_LOOKUP_TIMEOUT'))
   if len(marks88)<4 and elapsed88>=(2,46,121,305)[len(marks88)]:
    path88,rgb88=capture('visible84-sticky88-'+str(int(elapsed88)))
    blue88=sum(max(abs(a-b) for a,b in zip(pixel,(20,80,130)))<=8 for pixel in rgb88.crop((100,220,850,580)).getdata())
    check(blue88>3000,('STICKY88_DETAIL_PIXELS_LOST',elapsed88,blue88))
    check(detail88._art68.get('source') not in ('placeholder',None),'STICKY88_SOURCE_LOST')
    image_uri88=detail88._art68.get('image')
    check(not last88 or image_uri88==last88,'STICKY88_IMAGE_CHANGED')
    last88=image_uri88;marks88.append(dict(seconds=round(elapsed88,2),pixels=blue88,screenshot=path88.name))
 finally:detail88.close()
 check(len(marks88)==4 and marks88[-1]['seconds']>=305,'STICKY88_DURATION_NOT_MET')
 report['sticky88']=dict(status='PASS',wall_seconds=round(time.monotonic()-began88,2),checkpoints=marks88,negative_status_after=45,android='ANDROID_NOT_TESTED')

Path('/root/foreign87.json').write_text(json.dumps(report['foreign87'],indent=2))
Path('/root/'+('post75.json' if cold else 'visible84.json')).write_text(json.dumps(report,indent=2))

__import__('decoded_assets88').shutdown()

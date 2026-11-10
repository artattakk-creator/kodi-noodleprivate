"""Native .87 renderer with real non-XCMate plugin source paths.

The independent addons/data are synthetic. This proves Kodi/BINGIE consumers,
not real MP3/SHOUTcast services or physical Android hardware.
"""
from pathlib import Path
exec(compile(Path('/base_gui86.py').read_text(),'/base_gui86.py','exec'),globals())
import sys
sys.path.insert(0,'/')
from spec87 import FOREIGN,uri
from widget_inventory87 import collect,compare
import xbmcvfs
profile87=Path(xbmcvfs.translatePath('special://profile/'));skin87=Path(xbmcvfs.translatePath('special://skin/'))
inventory87=collect(profile87,skin87)
check(sum(v['external'] for v in inventory87['widgets'])==13,'FOREIGN87_SAVED_DEFINITIONS_LOST')
foreign_cases87=[]
for menu87,indices87 in ((0,range(5)),(1,range(8))):
 home.setFocusId(900);home.getControl(900).selectItem(menu87)
 for _ in range(20):pump();xbmc.sleep(50)
 for index87 in indices87:
  control87=2540+index87*10 if menu87==0 else 3510+index87*10
  for _ in range(80):
   if xbmc.getInfoLabel('Container('+str(control87)+').NumItems')=='8':break
   pump();xbmc.sleep(50)
  check(xbmc.getInfoLabel('Container('+str(control87)+').NumItems')=='8',('FOREIGN87_DIRECTORY_EMPTY',menu87,index87,control87))
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
   xbmc.executebuiltin('ActivateWindow(Home)',wait=False);xbmc.sleep(300)
   home.setFocusId(900);home.getControl(900).selectItem(menu87);xbmc.sleep(200)
compare(profile87,inventory87)
# Ten complete transitions among distinct external sources keep their rows,
# definitions and focus. No foreign consumer is routed through XCMate.
for cycle87 in range(10):
 for cid87 in (3510,3530,3540,3550,3560,3580):
  home.setFocusId(cid87);xbmc.sleep(40)
  check(home.getFocusId()==cid87,('FOREIGN87_CYCLE_FOCUS_LOST',cycle87,cid87))
  check(xbmc.getInfoLabel('Container('+str(cid87)+').NumItems')=='8','FOREIGN87_CYCLE_EMPTY')
compare(profile87,inventory87)
from hero_timing87 import summary
report['foreign87']=dict(status='PASS',saved_definitions=13,independent_sources=len({v[1] for v in FOREIGN}),cases=foreign_cases87,cycles=10,native_ok_audio=2,inventory_sha256=inventory87['sha256'],unchanged='PASS',source_kind='Synthetic independent plugins with actual non-XCMate URLs',android='ANDROID_NOT_TESTED')
report['timing87']=summary();report['reference_image']='REFERENZBILD_NICHT_VERFÜGBAR'
Path('/root/foreign87.json').write_text(json.dumps(report['foreign87'],indent=2))
Path('/root/'+('post75.json' if cold else 'visible84.json')).write_text(json.dumps(report,indent=2))

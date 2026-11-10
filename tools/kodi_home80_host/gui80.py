"""Native .80 geometry, initial row, idle and real detail-button playback.

Reuse every historical native case; only explicit .80 layout expectations
change. The controlled provider/AV stream is synthetic, never Android PASS.
"""
from pathlib import Path
source80=Path('/base_gui79.py').read_text()
for old80,new80 in (("Path('/root/home75.json')","Path('/root/home75-base80.json')"),('range(600,1040)','range(480,1040)'),('((270,20),1080,580)','((270,0),1620,480)'),('getpixel((330,645))','getpixel((330,525))'),('getpixel((800,150))','getpixel((1000,150))')):
 if old80 not in source80:raise RuntimeError('NATIVE80_BASE_CONTRACT_CHANGED')
 source80=source80.replace(old80,new80)
# A true initial unfocused VOD pixel receipt, before any Down/movie focus.
anchor80="select(2510,0,'live')\ncheck(json.loads(home.getProperty(schedule.KEY)))"
needle80="select(2510,0,'live')\ncheck(json.loads(home.getProperty(schedule.KEY))['phase']==1"
if needle80 not in source80:raise RuntimeError('NATIVE80_INITIAL_ANCHOR_CHANGED')
source80=source80.replace(needle80,"select(2510,0,'live')\ninitial80_path,initial80_rgb=capture('home80-initial')\nPath('/root/debug80.json').write_text(json.dumps(dict(pixel=initial80_rgb.getpixel((350,800)),quoted=xbmc.getCondVisibility('String.StartsWith(\"plugin://plugin.video.xtreammate/?action=widget_recent_vod&pid=fixture59\",plugin://plugin.video.xtreammate/)'),plain=xbmc.getCondVisibility('String.StartsWith(plugin://plugin.video.xtreammate/?action=widget_recent_vod&pid=fixture59,plugin://plugin.video.xtreammate/)'))))\ncheck(max(abs(a-b) for a,b in zip(initial80_rgb.getpixel((350,800)),(40,70,120)))<=8,'MOVIE80_NOT_VISIBLE_BEFORE_FOCUS')\ncheck(max(abs(a-b) for a,b in zip(initial80_rgb.getpixel((300,150)),(20,80,130)))<=8,'HERO80_NOT_FULL_BLEED')\ncheck(json.loads(home.getProperty(schedule.KEY))['phase']==1")
# Retain all idle/count checks and strengthen the interval/actual image check.
source80=source80.replace("duration=int(os.environ.get('XCMATE_IDLE74','0'))", "home.setFocusId(2510);home.getControl(2510).selectItem(0);pump();xbmc.sleep(300)\nsettle_idle86()\nduration=int(os.environ.get('XCMATE_IDLE74','0'))")
source80=source80.replace("elapsed-checkpoints[-1]['elapsed']>=900", "elapsed-checkpoints[-1]['elapsed']>=30")
source80=source80.replace("check(counts==[88,24,24],counts)", "check(counts==[88,24,24],counts)\n        check(max(abs(a-b) for a,b in zip(rgb.getpixel((500,300)),(20,80,130)))<=8,'IDLE80_HERO_LOST')\n        check(max(abs(a-b) for a,b in zip(rgb.getpixel((330,525)),(20,90,150)))<=8,'IDLE80_LOGO_LOST')")
# Focus changes schedule Kodi textures asynchronously. Keep exact pixel
# assertions, but await the selected media texture rather than a fixed delay.
# The initial unfocused row assertion above remains immediate and unchanged.
source80=source80.replace("path=Path('/root/'+name+'.png')", "path=Path('/root/'+name+'.png')\n    path.unlink(missing_ok=True)")
source80=source80.replace("path,rgb=capture('home75-'+kind+'-'+str(index))", "path,rgb=capture_selected80(kind,index)")
def capture_selected80(kind,index):
 deadline80=time.monotonic()+5;name80='home75-'+kind+'-'+str(index);attempt80=0
 expected80=((180,100,30) if kind=='vod' and index==0 else tuple((v+index*step)%240 for v,step in zip((40,70,120) if kind=='vod' else (100,50,20),(19,31,13)))) if kind in ('vod','series') else None
 while True:
  path80,rgb80=capture(name80);actual80=rgb80.getpixel((1000,150));attempt80+=1
  if expected80 is None or max(abs(a-b) for a,b in zip(actual80,expected80))<=6:return path80,rgb80
  if time.monotonic()>=deadline80:
   Path('/root/render80-error.json').write_text(json.dumps(dict(kind=kind,index=index,actual=actual80,expected=expected80,attempts=attempt80)))
   return path80,rgb80 # The original strict pixel assertion reports failure.
  pump();xbmc.sleep(100)
def settle_idle86():
 if xbmcaddon.Addon().getAddonInfo('version')!='0.1.29.86':return
 # .86 correctly shows a station logo until the selected event's renderer
 # receipt exists. Start the unchanged soak only on its actual settled pixels.
 deadline=time.monotonic()+5
 while True:
  pump();xbmc.sleep(100);_,frame=capture('home86-before-idle')
  hero=frame.getpixel((500,300));logo=frame.getpixel((330,525))
  if max(abs(a-b) for a,b in zip(hero,(20,80,130)))<=8 and max(abs(a-b) for a,b in zip(logo,(20,90,150)))<=8:return
  if time.monotonic()>=deadline:
   prefix='XCMate.Hero63.'+home.getProperty('XCMate.Hero63.Active')+'.'
   raise RuntimeError(str(dict(code='IDLE86_PRECONDITION_NOT_RENDERED',hero=hero,logo=logo,kind=home.getProperty(prefix+'Kind86'),source=home.getProperty(prefix+'ArtSource'))))
exec(compile(source80,'native-home80-base','exec'),globals())
# Keep every real TLS/cache assertion from .79, including full decode.
cache80=Path('/base_gui_cache79.py').read_text().split('import widget_cache79 as cache79',1)[1]
cache80='import widget_cache79 as cache79'+cache80
cache80=cache80.replace("Path('/root/home75-base79.json')","Path('/root/home75-base80.json')").replace("Path('/root/home75.json')","Path('/root/home75-cache80.json')")
exec(compile(cache80,'native-home80-cache','exec'),globals())
# Native large-guide entry, long text and exact gray-blue focus pixels.
from guide_grid_window import GuideGridWindow
from types import SimpleNamespace
from urllib.parse import urlencode
guide80=GuideGridWindow('XCMateGuideGrid.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
guide80.configure(SimpleNamespace(_handle=-1,_params=dict(guide_sid80='5'),_xc=lambda p:None,url=lambda **p:'plugin://plugin.video.xtreammate/?'+urlencode(p)),get_active()[0])
try:
 guide80.show()
 for _ in range(200):
  if guide80._ready:guide80.pump()
  if guide80.rows and not guide80._loading and guide80.getFocusId()>=1000:break
  xbmc.sleep(50)
 else:raise RuntimeError('GUIDE80_NOT_READY')
 check(guide80.rows[guide80.row]['channel']['sid']=='5','GUIDE80_SELECTED_CHANNEL_LOST')
 selected80=guide80._selected()
 check(selected80 is not None,'GUIDE80_NO_LOCAL_EPG')
 selected80['title']='Very long programme title '*30
 guide80.rows[guide80.row]['channel']['name']='A very long channel name '*20
 guide80._render();xbmc.sleep(300)
 focus80=guide80.getControl(guide80.getFocusId());x80,y80=focus80.getPosition();width80=focus80.getWidth()
 path80,rgb80=capture('home80-guide')
 # This own 720p XML is scaled to the normalized 1920x1080 receipt.
 border80=rgb80.getpixel((round((x80+width80/2)*1.5),round((y80+2)*1.5)))
 check(max(abs(a-b) for a,b in zip(border80,(58,75,91)))<12,('GUIDE80_GRAY_FOCUS',border80))
 check(len(focus80.getLabel())<len(selected80['title']),'GUIDE80_UNBOUNDED_TITLE')
 Path('/root/guide80.json').write_text(json.dumps(dict(status='PASS',selected_sid='5',start_sid=str(get_active()[0].get('start_stream_id')),local_epg=True,long_title_bounded=True,focus_rgb=border80,android='ANDROID_NOT_TESTED')))
finally:guide80.close()
xbmc.sleep(300)
# The exact real Home widget route, actual native detail and OK callback.
home.setFocusId(2520);home.getControl(2520).selectItem(0)
xbmc.executebuiltin('Action(Select)',wait=False)
started80=time.monotonic();detail80=None
for _ in range(300):
 current80=xbmcgui.getCurrentWindowId()
 count80=xbmc.getInfoLabel('Container(300).NumItems')
 if current80>=13000 and count80.isdigit() and int(count80)>0 and xbmc.getInfoLabel('System.CurrentControlId')=='300':
  detail80=True;detail_id80=current80;break
 xbmc.sleep(50)
if detail80 is None:raise RuntimeError('VOD80_DETAIL_NOT_OPEN')
capture('home80-vod-detail')
xbmc.executebuiltin('Action(Select)',wait=False)
player80=xbmc.Player()
for _ in range(300):
 if player80.isPlayingVideo():break
 xbmc.sleep(50)
else:raise RuntimeError('VOD80_BUTTON_NO_VIDEO')
import json,time
players80=json.loads(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=80,method='Player.GetActivePlayers'))))['result']
native80=json.loads(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=80,method='Player.GetProperties',params=dict(playerid=players80[0]['playerid'],properties=['videostreams','audiostreams','time'])))))['result']
if not native80['videostreams'] or not native80['audiostreams']:raise RuntimeError('VOD80_MISSING_AV_STREAMS')
# Native isPlaying can precede Kodi's AV-start/Busy release. Wait for the
# actual stable presentation state before a simulated user's Stop.
for _ in range(200):
 if xbmcgui.getCurrentWindowDialogId() in (0,9999) and not xbmc.getCondVisibility('System.HasActiveModalDialog'):break
 xbmc.sleep(50)
else:raise RuntimeError('VOD80_START_BUSY_NOT_RELEASED')
capture('home80-vod-playing')
from exit_jobs import request as stop80,poll as stop_poll80,state as stop_state80
if not stop80(reason='USER_BACK'):raise RuntimeError('VOD80_STOP_NOT_OWNED')
for _ in range(240):
 stop_poll80();outcome80=stop_state80() or {}
 if outcome80.get('worker_done') and outcome80.get('result')=='complete':break
 xbmc.sleep(25)
else:raise RuntimeError('VOD80_STOP_NO_ACK')
if xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)'):xbmc.executebuiltin('Action(Back)',wait=False)
for _ in range(200):
 if xbmcgui.getCurrentWindowId()==detail_id80:break
 xbmc.sleep(50)
else:raise RuntimeError('VOD80_NO_DETAIL_RETURN')
capture('home80-vod-return')
for _ in range(6):
 if xbmcgui.getCurrentWindowId()==10000:break
 xbmc.executebuiltin('Action(Back)',wait=False);xbmc.sleep(250)
Path('/root/vod80.json').write_text(json.dumps(dict(status='PASS',native_button=True,actual_video=True,audio_streams=len(native80['audiostreams']),video_streams=len(native80['videostreams']),native_stop_ack=True,detail_return=True,elapsed_ms=round((time.monotonic()-started80)*1000,2),android='ANDROID_NOT_TESTED')))
home.setFocusId(2510);home.getControl(2510).selectItem(0);pump();xbmc.sleep(300)
capture('home80-idle')
result80=json.loads(Path('/root/home75-cache80.json').read_text());result80['vod80']=json.loads(Path('/root/vod80.json').read_text());result80['layout80']='FULL_BLEED_CONTAIN_INITIAL_MOVIE_PIXELS';result80['guide80']=json.loads(Path('/root/guide80.json').read_text())
Path('/root/home75.json').write_text(json.dumps(result80,indent=2))

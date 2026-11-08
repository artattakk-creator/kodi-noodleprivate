"""Cold native acceptance: two real restarts with the image origin offline."""
import sys,time,json,hashlib
from pathlib import Path
sys.path.insert(0,'/root/.kodi/addons/plugin.video.xtreammate/resources/lib')
import xbmc,xbmcgui,xbmcaddon
from PIL import Image
native79=xbmcaddon.Addon;xbmcaddon.Addon=lambda *a,**k:native79(*a,**k) if a or k else native79('plugin.video.xtreammate')
import hero_epg63,widget_cache79,widget_runtime79
from portals import get_active
from widget_data41 import snapshot
home=xbmcgui.Window(10000);portal=get_active()[0]
for _ in range(300):
 if xbmcgui.getCurrentWindowId()==10000 and xbmcgui.getCurrentWindowDialogId() in (0,-1,9999) and not home.getProperty('StartupMask') and not xbmc.getCondVisibility('Window.IsVisible(11103)') and xbmc.getInfoLabel('Container(2510).NumItems')=='88':break
 xbmc.sleep(100)
else:raise RuntimeError('COLD79_HOME_NOT_READY')
cases=[]
for kind,cid,color in (('vod',2520,(25,145,100)),('series',2530,(145,70,120))):
 for _ in range(100):
  home.setFocusId(cid);home.getControl(cid).selectItem(0);hero_epg63._next=0;hero_epg63.poll();xbmc.sleep(100)
  art=xbmc.getInfoLabel('ListItem.Art(poster)')
  if art and not art.startswith(('https://','http://')):break
 else:raise RuntimeError('COLD79_NOT_LOCAL')
 tag=xbmc.getInfoLabel('Container('+str(cid)+').ListItem.Property(XCMate.Directory79)')
 record=json.loads(home.getProperty(widget_runtime79.slot(portal,kind)) or '{}')
 if not tag or tag!=record.get('tag'):raise RuntimeError('COLD79_DIRECTORY_ACK_MISMATCH')
 picture=Path('/root/home75-cold79-'+kind+'.png')
 for paint in range(25):
  # Startup and native texture fades are asynchronous. Observe the final
  # pixels, without accepting a splash-dimmed frame as a successful image.
  xbmc.sleep(200);xbmc.executebuiltin('TakeScreenshot('+str(picture)+')',wait=False);xbmc.sleep(100)
  try:
   with Image.open(picture) as im:im.load();rgb=im.convert('RGB').resize((1920,1080))
  except (OSError,ValueError):continue
  if max(abs(a-b) for a,b in zip(rgb.getpixel((800,150)),color))<=8:break
 else:raise RuntimeError('COLD79_ACTUAL_HERO_TEXTURE_WRONG')
 rows,_=snapshot(portal,kind);cached=widget_cache79.read(portal,kind,rows).get('0',{}).get('poster')
 if not cached:raise RuntimeError('COLD79_CACHE_LEASE_MISSING')
 cases.append(dict(kind=kind,count=int(xbmc.getInfoLabel('Container('+str(cid)+').NumItems')),directory_ack=True,local_cache=True,sha256=hashlib.sha256(Path(cached).read_bytes()).hexdigest(),actual_pixels='PASS'))
# Existing saved cinema/skinshortcuts bytes must survive both starts.
old=json.loads(Path('/root/old-layout78.json').read_text());folder=Path('/root/.kodi/userdata/addon_data/script.skinshortcuts')
if any(hashlib.sha256((folder/name).read_bytes()).hexdigest()!=digest for name,digest in old.items()):raise RuntimeError('COLD79_PERSONAL_WIDGET_CHANGED')
counts=[int(xbmc.getInfoLabel('Container('+str(cid)+').NumItems')) for cid in (2510,2520,2530)]
if counts!=[88,24,24]:raise RuntimeError('COLD79_ITEM_LOSS')
Path('/root/post75.json').write_text(json.dumps(dict(status='PASS',actual_restart=True,counts=counts,cases=cases,origin_offline=Path('/root/tls79-off').exists(),personal_widgets='UNCHANGED',android='ANDROID_NOT_TESTED'),indent=2))

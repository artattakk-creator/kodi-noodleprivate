"""Actual Linux BINGIE pictures under synthetic XCMate reserve pressure.

Real Kodi ListItems, TLS, texture files and screenshot pixels. Not Android,
not a physical ENOSPC test; the C++ texture writer has real host free space.
"""
import sys,time,json,threading,hashlib,io
from pathlib import Path
sys.path.insert(0,'/root/.kodi/addons/plugin.video.xtreammate/resources/lib')
sys.path.insert(0,'/root/.kodi/addons/plugin.video.xtreammate')
import xbmc,xbmcgui,xbmcaddon
from PIL import Image
native_addon=xbmcaddon.Addon
xbmcaddon.Addon=lambda *a,**k:native_addon(*a,**k) if a or k else native_addon('plugin.video.xtreammate')
from fixture66 import install
install()
from portals import get_active
from widget_group46 import snapshot as live_rows
from widget_data41 import snapshot
from widget_assets69 import prepare,read
from programme_events46 import load
from programme_requests68 import completed
from widget_live47 import publish
import home_schedule75,hero_epg63,widget_notice46,widget_hooks45
portal=get_active()[0];home=xbmcgui.Window(10000);home_schedule75.configure([portal])
# Only known reload hooks are discovered in the actual preapproved candidate.
widget_hooks45.prepare()
from artwork_display84 import state
pressure=state();assert pressure['free']==27*1024**2 and pressure['code']!='READY',pressure
watermark=xbmcgui.ControlLabel(20,1048,1850,30,'Synthetic Linux Kodi .84 / NOT Android / Python 27 MiB capacity injection',font='Reg18',textColor='FFFFFFFF');home.addControl(watermark)
baseline=json.loads(Path('/root/baseline84.json').read_text());errors=[];phases=[];events=[]
cold=Path('/root/tls79-off').exists()
def check(condition,detail):
 if not condition:raise RuntimeError(str(detail))
def pump():
 hero_epg63._next=0;hero_epg63.poll();widget_notice46._next=0;widget_notice46.poll()
def worker():
 try:
  rows=live_rows(portal);check(len(rows)==88,'LIVE84_COUNT')
  prepare(portal,'live',rows)
  for _ in range(100):
   if len(read(portal,'live',rows))>=5:break
   time.sleep(.1)
  check(len(read(portal,'live',rows))>=5,'LIVE84_NO_REFS')
  phases.append(dict(kind='live',at=time.monotonic(),refs=len(read(portal,'live',rows))))
  # All five exact XMLTV events fully decode through the real HTTPS transport.
  for row in rows[:1 if cold else 5]:
   event=load(portal,row)
   from programme_urls55 import resolve
   value=resolve(event,allow_lookup=False,url_mode69=True)
   check(value and value.get('code')=='READY',('EVENT84_NOT_READY',value))
   completed(event,value);events.append(dict(sid=row['sid'],event=event['key'],source=value['source'],decoded=value.get('decoded77'),storage=value.get('storage69')))
  publish(portal,'live',rows)
  # Observe native Live readiness before admitting new movie/series fetches.
  for _ in range(300):
   if json.loads(home.getProperty(home_schedule75.KEY)).get('phase',0)>=1:break
   time.sleep(.1)
  else:raise RuntimeError('LIVE84_RECEIVER_NOT_READY')
  for kind in ('vod','series'):
   rows,code=snapshot(portal,kind);check(len(rows)==24,(kind,code,len(rows)))
   prepare(portal,kind,rows)
   for _ in range(150):
    if len(read(portal,kind,rows))==24:break
    time.sleep(.1)
   check(len(read(portal,kind,rows))==24,('MEDIA84_NO_REFS',kind,len(read(portal,kind,rows))))
   publish(portal,kind,rows);home_schedule75.prepared(kind,len(rows),portal=portal,rows=rows)
   phases.append(dict(kind=kind,at=time.monotonic(),refs=24))
 except Exception:
  import traceback;errors.append(traceback.format_exc())
thread=threading.Thread(target=worker,daemon=True);thread.start()
# The active Live list stays focused while hidden media are prepared.
for _ in range(900):
 if errors:raise RuntimeError(errors[0])
 if xbmc.getInfoLabel('Container(2510).NumItems')=='88':
  home.setFocusId(2510);home.getControl(2510).selectItem(0)
 pump();xbmc.sleep(100)
 if not thread.is_alive():break
else:raise RuntimeError('WORKER84_TIMEOUT')
check(not errors,errors);check([v['kind'] for v in phases]==['live','vod','series'],phases)
# Only an active native receiver may report visible; preparation is separate.
check(json.loads(home.getProperty(home_schedule75.KEY))['visible']==['live'],'HIDDEN84_CLAIMED_VISIBLE')
stop=threading.Event()
def hero_worker():
 while not stop.wait(.15):hero_epg63.prepare(portal['id'])
threading.Thread(target=hero_worker,daemon=True).start()
def capture(name):
 path=Path('/root/'+name+'.png');xbmc.executebuiltin('TakeScreenshot('+str(path)+')',wait=False)
 for _ in range(100):
  xbmc.sleep(50)
  try:
   raw=path.read_bytes()
   with Image.open(io.BytesIO(raw)) as im:im.load();rgb=im.convert('RGB').resize((1920,1080))
   return path,rgb
  except (OSError,ValueError):continue
 raise RuntimeError('SCREENSHOT84_INCOMPLETE')
cases=[]
for kind,control,hero_color,rail_color in (('live',2510,(20,80,130),(25,100,160)),('vod',2520,(35,120,80),(180,100,30)),('series',2530,(35,120,80),(100,60,180))):
 for _ in range(200):
  if xbmc.getInfoLabel('Container('+str(control)+').NumItems')==('88' if kind=='live' else '24'):break
  pump();xbmc.sleep(100)
 home.setFocusId(control);home.getControl(control).selectItem(0)
 for _ in range(60):pump();xbmc.sleep(50)
 path,rgb=capture('visible84-'+('cold-' if cold else 'warm-')+kind)
 # Inner flat-colour fixture regions avoid text, outlines and overlay gradients.
 def pixels(color,box):
  return sum(max(abs(a-b) for a,b in zip(pixel,color))<=8 for pixel in rgb.crop(box).getdata())
 hero_pixels=pixels(hero_color,(300,50,1100,520));rail_pixels=pixels(rail_color,(275,615,480,1010))
 check(hero_pixels>3000,('HERO84_PIXELS_MISSING',kind,hero_pixels))
 check(rail_pixels>1500,('RAIL84_PIXELS_MISSING',kind,rail_pixels))
 # Ask Kodi's real receiver for its current art, then fully decode actual cache.
 selected=home.getControl(control).getSelectedItem();poster=selected.getArt('poster');check(poster,('NO84_LISTITEM_ART',kind))
 from widget_cache82 import prepare as recover
 rows=live_rows(portal) if kind=='live' else snapshot(portal,kind)[0]
 for _ in range(8):recover(portal,kind,rows);xbmc.sleep(520)
 refs=read(portal,kind,rows);local=refs.get(str(rows[0]['sid']),{}).get('poster','')
 check(local.startswith('/'),('NO84_LOCAL_TEXTURE',kind,local))
 with Image.open(local) as decoded:decoded.load();size=decoded.size
 cases.append(dict(kind=kind,items=int(xbmc.getInfoLabel('Container('+str(control)+').NumItems')),focus=home.getFocusId(),poster_local=local.startswith('/'),decoded_size=size,hero_pixels=hero_pixels,rail_pixels=rail_pixels,screenshot=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
stop.set()
for path,digest in baseline.items():check(hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,'PROTECTED84_CONFIG_CHANGED')
from utils import addon_data_dir
archive=[p for p in Path(addon_data_dir()).rglob('*') if p.is_file() and p.suffix.lower() in ('.png','.jpg','.img','.jpeg')]
check(not archive,'UNEXPECTED84_ARCHIVE_IMAGES')
check(xbmcaddon.Addon().getSetting('tmdb_read_token43')=='SYNTHETIC84_UNCHANGED_NOT_A_REAL_TOKEN','TOKEN84_CHANGED')
report=dict(status='PASS',platform='Linux Kodi synthetic / NOT Android',cold=cold,pressure=pressure,capacity_injection='XCMate Python only, not physical ENOSPC; Kodi C++ texture storage uses real free space',phases=phases,events=events,cases=cases,archive_images=0,config_hashes='PASS',android='ANDROID_NOT_TESTED')
Path('/root/'+('post75.json' if cold else 'visible84.json')).write_text(json.dumps(report,indent=2))

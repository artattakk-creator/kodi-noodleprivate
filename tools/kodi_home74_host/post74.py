"""Actual native Home after isolated Kodi restart: rows, focus, reload, pixels.

Only a disposable synthetic profile; no playback or saved binding/skin edits.
"""
import hashlib,io,json,sys,time
from pathlib import Path
sys.path.insert(0,'/root/.kodi/addons/plugin.video.xtreammate/resources/lib')
import xbmc,xbmcgui,xbmcaddon
from PIL import Image,UnidentifiedImageError
real=xbmcaddon.Addon
xbmcaddon.Addon=lambda *a,**kw:real(*a,**kw) if a or kw else real('plugin.video.xtreammate')
import hero_epg63
home=xbmcgui.Window(10000);monitor=xbmc.Monitor();cases=[]
def wait_rows():
 deadline=time.monotonic()+30
 while time.monotonic()<deadline and not monitor.abortRequested():
  counts=[xbmc.getInfoLabel('Container('+str(i)+').NumItems') for i in (2510,2520,2530)]
  if counts==['88','24','24'] and xbmcgui.getCurrentWindowId()==10000:return counts
  monitor.waitForAbort(.1)
 raise RuntimeError('POST74_NATIVE_ROWS '+repr(counts))
def contours(rgb):
 width,height=rgb.size;raw=rgb.tobytes();points=set()
 for y in range(height):
  for x in range(100,width):
   off=(y*width+x)*3;r,g,b=raw[off:off+3]
   if r<60 and g>140 and b>220 and g-r>100 and b-r>160:points.add(y*width+x)
 boxes=[]
 while points:
  seed=points.pop();todo=[seed];left=right=seed%width;top=bottom=seed//width
  while todo:
   item=todo.pop();x,y=item%width,item//width;left=min(left,x);right=max(right,x);top=min(top,y);bottom=max(bottom,y)
   for nxt in (item-1,item+1,item-width,item+width):
    if nxt in points:points.remove(nxt);todo.append(nxt)
  if right-left>100 and bottom-top>50:boxes.append([left,top,right+1,bottom+1])
 return boxes
def capture(label,focus,colour=None):
 for _ in range(35):
  hero_epg63.poll();monitor.waitForAbort(.1)
  path=Path('/root/post74-'+label+'-last.png');xbmc.executebuiltin('TakeScreenshot('+str(path)+')',wait=False);monitor.waitForAbort(.4)
  try:
   raw=path.read_bytes()
   with Image.open(io.BytesIO(raw)) as image:image.load();native=image.size;rgb=image.convert('RGB').resize((1920,1080))
   boxes=contours(rgb)
   if len(boxes)!=1 or home.getFocusId()!=focus:continue
   if colour is not None:
    x1,y1,x2,y2=boxes[0];pixel=rgb.getpixel(((x1+x2)//2,y1+(y2-y1)//4))
    if max(abs(a-b) for a,b in zip(pixel,colour))>8:continue
   destination=Path('/root/post74-'+label+'.png');destination.write_bytes(raw)
   cases.append(dict(name=label,focus=focus,frames=boxes,counts=wait_rows(),native_resolution=native,sha256=hashlib.sha256(raw).hexdigest()));return
  except (OSError,UnidentifiedImageError):pass
 raise RuntimeError('POST74_NATIVE_PIXELS '+label)
wait_rows();home.setFocusId(2510);home.getControl(2510).selectItem(0);monitor.waitForAbort(.8)
capture('restart-live',2510,(20,90,150))
for action,focus,colour in (('Down',2520,(40,70,120)),('Down',2530,(100,50,20)),('Up',2520,(40,70,120)),('Up',2510,(20,90,150))):
 xbmc.executebuiltin('Action('+action+')');monitor.waitForAbort(.8);home.getControl(focus).selectItem(0)
 capture('vertical-'+str(len(cases)),focus,colour)
# A verified native existing reload URL is referenced by the Live provider.
# No rebinding, profile write or mandatory setup step.
home.setProperty('XCMate.Widget45.Reload.live','post74-manual-reload');monitor.waitForAbort(1)
wait_rows();home.setFocusId(2510);home.getControl(2510).selectItem(0);capture('manual-live-reload',2510,(20,90,150))
# A skin reload re-resolves all native directories. Files/settings stay intact.
xbmc.executebuiltin('ReloadSkin()',wait=False);monitor.waitForAbort(3)
home=xbmcgui.Window(10000);wait_rows();home.setFocusId(2510);home.getControl(2510).selectItem(0);capture('skin-reload',2510,(20,90,150))
Path('/root/post74.json').write_text(json.dumps(dict(status='PASS',actual_restart=True,cases=cases,android='ANDROID_NOT_TESTED')))

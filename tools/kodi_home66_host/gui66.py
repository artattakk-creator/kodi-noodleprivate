"""Inspect the actual Home window, never open a replacement preview dialog."""
import json
import time
from pathlib import Path
import sys
sys.path.insert(0,'/root/.kodi/addons/plugin.video.xtreammate/resources/lib')
import xbmc
import xbmcgui

def check64(condition,detail='NATIVE_GUI64_CONTRACT'):
    if not condition:raise RuntimeError(str(detail))
home = xbmcgui.Window(10000)
for _ in range(200):
    if xbmcgui.getCurrentWindowId() == 10000 and xbmc.getInfoLabel('Container(2510).NumItems') == '88':
        break
    xbmc.sleep(100)
else:
    raise RuntimeError('BINGIE_HOME_LIVE_NOT_LOADED')
watermark=xbmcgui.ControlLabel(20,1045,1800,30,'Synthetic provider / Kodi Linux / BINGIE 2.2.3 / NOT Android',font='Reg18',textColor='FFFFFFFF')
home.addControl(watermark)
home.setFocusId(2510)
for index in (0, 1, 87):
    home.getControl(2510).selectItem(index)
    started = time.monotonic()
    import hero_epg63
    for ready in range(30):
        # Simulate the production 100-ms UI pump after Kodi has propagated
        # focus to its global ListItem; selecting the container alone is earlier.
        hero_epg63._next=0;hero_epg63.poll()
        selected=xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.MediaId)')
        token=xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.WidgetToken41)')
        bank=home.getProperty('XCMate.Hero63.Active')
        if selected==str(index) and home.getProperty('XCMate.Hero63.'+bank+'.Identity')==token:
            break
        xbmc.sleep(50)
    else:
        raise RuntimeError('FOCUS_PUMP_NOT_PUBLISHED '+repr((selected,bank,token)))
    # Wait for the existing source's native clock, if its initial bounded
    # local read returned a placeholder. No manual reset or URL change.
    for attempt in range(375):
        path = xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.ProgrammeImage46)')
        if index == 87 or '/programme_images46/' in path:
            break
        xbmc.sleep(200)
    else:
        raise RuntimeError('LOCAL_HERO_NOT_PUBLISHED')
    from PIL import Image, UnidentifiedImageError
    expected = ((20 + index * 17) % 230, (90 + index * 23) % 230, (150 + index * 13) % 230)
    for attempt in range(30):
        # Kodi encodes asynchronously. Never let a later pending capture
        # overwrite the already verified evidence filename.
        capture = Path('/root/capture63-' + str(index) + '-' + str(attempt) + '.png')
        xbmc.executebuiltin('TakeScreenshot(' + str(capture) + ')', wait=False)
        xbmc.sleep(350)
        try:
            import io
            captured_bytes = capture.read_bytes()
            with Image.open(io.BytesIO(captured_bytes)) as frame:
                frame.load()
                rgb = frame.convert('RGB')
            hero = (20,80,130) if index == 0 else (130,50,30)
            logo_ready=max(abs(a-b) for a,b in zip(rgb.getpixel((330,645)),expected))<=5 if index<87 else sum(1 for r,g,b in rgb.crop((285,617,405,675)).getdata() if min(r,g,b)>170)>20
            if logo_ready and (index==87 or all(max(abs(a-b) for a,b in zip(rgb.getpixel(point),hero))<=5 for point in ((1450,180),(1700,180),(1880,180)))):
                Path('/root/home66-' + str(index) + '.png').write_bytes(captured_bytes)
                break
        except (OSError, UnidentifiedImageError):
            pass
    else:
        raise RuntimeError('NATIVE_HERO_LOGO_PIXELS_NOT_READY')
    props = {key: xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.' + key + ')') for key in ('ProgrammeChannel46', 'ProgrammeTitle46', 'ProgrammeNext46', 'ProgrammeDescription46', 'ProgrammeImage46', 'Home50')}
    props['items'] = xbmc.getInfoLabel('Container(2510).NumItems')
    props['visible'] = xbmc.getCondVisibility('Control.IsVisible(2510)')
    props['hero_condition'] = xbmc.getCondVisibility('Window.IsActive(Home) + ControlGroup(77777).HasFocus() + String.IsEqual(ListItem.Property(XCMate.Home50),true)')
    props['window'] = xbmcgui.getCurrentWindowId()
    props['focus'] = home.getFocusId()
    bank=home.getProperty('XCMate.Hero63.Active')
    props['hero_active_bank']=bank
    props['hero_percent']=home.getProperty('XCMate.Hero63.'+bank+'.Percent')
    props['row_percent']=xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.ProgrammePercent46)')
    props['host_ready_ms'] = round((time.monotonic() - started) * 1000)
    from tv_data import GuideSnapshot
    from unittest import mock
    seed_started=time.monotonic()
    with mock.patch('sqlite3.connect',side_effect=AssertionError('WARM_HANDOFF_SQL')),mock.patch('urllib.request.urlopen',side_effect=AssertionError('WARM_HANDOFF_HTTP')):
        snapshot=GuideSnapshot(dict(id='fixture59'),None,initial_sid=str(index));warm=snapshot.get(str(index))
    props['warm_seed_ms']=round((time.monotonic()-seed_started)*1000,3)
    props['warm_now']=warm.get('now','');props['warm_next']=warm.get('next','');props['warm_key']=warm.get('programme_key47','')
    props['warm_phase']='HOST_RAM_SNAPSHOT_ONLY_NOT_NATIVE_AV'
    if index<87:
        check64(warm['now']==props['ProgrammeTitle46'] and warm['next']==props['ProgrammeNext46'],'WARM64_TEXT_MISMATCH')
        check64(props['warm_seed_ms']<1000 and warm['programme_key47'],'WARM64_SEED_BUDGET')
    Path('/root/home66-' + str(index) + '.json').write_text(json.dumps(props))
home.setProperty('Home64.Complete', 'true')


# Native media focus, using real row layouts with global fixed frames enabled.
from PIL import ImageChops
def frames64(rgb):
 data=rgb.tobytes();width,height=rgb.size;points=set()
 for y in range(height):
  for x in range(100,width):
   offset=(y*width+x)*3;r,g,b=data[offset:offset+3]
   if r<100 and g>100 and b>180 and g-r>40 and b-r>60:points.add(y*width+x)
 boxes=[]
 while points:
  seed=points.pop();todo=[seed];left=right=seed%width;top=bottom=seed//width
  while todo:
   pos=todo.pop();x,y=pos%width,pos//width;left=min(left,x);right=max(right,x);top=min(top,y);bottom=max(bottom,y)
   for nxt in (pos-1,pos+1,pos-width,pos+width):
    if nxt in points:points.remove(nxt);todo.append(nxt)
  if right-left>100 and bottom-top>50:boxes.append((left,top,right+1,bottom+1))
 return boxes
media66=[]
for ident,kind,indices in ((2520,'vod',(0,5)),(2530,'series',tuple(range(10))),(2520,'vod',(1,))):
 home.setFocusId(ident);xbmc.sleep(600)
 for index in indices:
  home.getControl(ident).selectItem(index);xbmc.sleep(250)
  for attempt in range(20):
   capture=Path('/root/media66-last.png');xbmc.executebuiltin('TakeScreenshot('+str(capture)+')',wait=False);xbmc.sleep(350)
   try:
    raw=capture.read_bytes()
    import io
    with Image.open(io.BytesIO(raw)) as source:source.load();rgb=source.convert('RGB')
    boxes=frames64(rgb)
    if len(boxes)!=1:continue
    x1,y1,x2,y2=box=boxes[0]
    expected=tuple((v+index*step)%240 for v,step in zip((40,70,120) if kind=='vod' else (100,50,20),(19,31,13)))
    actual=rgb.getpixel(((x1+x2)//2,y1+(y2-y1)//4))
    if 210<=x2-x1<=260 and 300<=y2-y1<=345 and max(abs(a-b) for a,b in zip(actual,expected))<=8:
     break
   except (OSError,UnidentifiedImageError):pass
  else:
   Path('/root/media66-error.json').write_text(json.dumps(dict(id=ident,kind=kind,index=index,boxes=boxes,focus=home.getFocusId())))
   raise RuntimeError('MEDIA64_FOCUS_OR_POSTER_PIXELS '+repr((ident,kind,index,boxes)))
  props={name:xbmc.getInfoLabel('Container('+str(ident)+').ListItem.Property('+name+')') for name in ('XCMate.MediaId','XCMate.WidgetKind41','XCMate.SeriesArt64','XCMate.Home50')}
  check64(home.getFocusId()==ident and props['XCMate.WidgetKind41']==kind and props['XCMate.MediaId']==str(index),props)
  check64(props['XCMate.Home50']!='true','MEDIA64_FOREIGN_HERO')
  item=dict(kind=kind,index=index,focus=ident,bounds=box,poster_pixels='PASS',selected=props['XCMate.MediaId'])
  if kind=='series':check64(props['XCMate.SeriesArt64']=='SERIES_ART_URI_READY',props)
  media66.append(item)
  if index in (0,5,9):Path('/root/media66-'+kind+'-'+str(index)+'.png').write_bytes(raw)
home.setFocusId(2510);xbmc.sleep(500)
check64(home.getFocusId()==2510,'LIVE64_FOCUS_RETURN')
Path('/root/media66-base.json').write_text(json.dumps(dict(cases=media66,series_posters=10,film_series_live_return=True,global_fixed_frames=True,android='NOT_TESTED')))


# Missing .64 cases: third-party poster and square music layouts with no
# XCMate.WidgetKind41; compare contour against actual colored item pixels.
xbmc.executebuiltin('Skin.SetString(ViewDetailsBorderFocusColor,FF00BBFF)')
xbmc.executebuiltin('Skin.SetString(BingiePlotTextColor,FFFF00FF)')
xbmc.sleep(500)
foreign66=[]
def colored_bbox66(rgb,color):
 from PIL import ImageChops
 masks=[band.point(lambda value,c=expected:255 if abs(value-c)<=8 else 0) for band,expected in zip(rgb.split(),color)]
 return ImageChops.multiply(ImageChops.multiply(masks[0],masks[1]),masks[2]).getbbox()
def plot_bbox66(rgb,bottom):
 from PIL import ImageChops
 crop=rgb.crop((120,0,1100,max(1,bottom)))
 red,green,blue=crop.split()
 mask=ImageChops.multiply(ImageChops.multiply(red.point(lambda v:255 if v>245 else 0),blue.point(lambda v:255 if v>245 else 0)),green.point(lambda v:255 if v<10 else 0))
 return mask.getbbox()
for ident,kind,indices in ((2540,'poster',(0,1,2,23)),(2550,'music',(0,1,23)),(2560,'television',(0,1,2,23)),(2540,'poster',(2,))):
 home.setFocusId(ident);xbmc.sleep(700)
 for index in indices:
  home.getControl(ident).selectItem(index);xbmc.sleep(500)
  expected=((60+index*7)%180+20,(90+index*5)%140+40,(40+index*11)%150+30)
  detail={}
  for attempt in range(12):
   capture=Path('/root/foreign66-last.png');xbmc.executebuiltin('TakeScreenshot('+str(capture)+')',wait=False);xbmc.sleep(350)
   try:
    raw=capture.read_bytes()
    import io
    with Image.open(io.BytesIO(raw)) as source:source.load();rgb=source.convert('RGB')
    boxes=frames64(rgb);tile=colored_bbox66(rgb,expected)
    if len(boxes)!=1 or not tile:detail=dict(boxes=boxes,tile=tile);continue
    frame=boxes[0];width=frame[2]-frame[0];height=frame[3]-frame[1]
    correct=abs(frame[0]-tile[0])<=14 and abs(frame[1]-tile[1])<=14 and abs(width-(tile[2]-tile[0]))<=28
    correct=correct and (195<=height<=270 if kind=='music' else 295<=height<=350)
    plot=plot_bbox66(rgb,tile[1])
    collision=bool(plot and plot[3]>tile[1]-30)
    detail=dict(frame=frame,tile=tile,plot=plot,collision=collision,focus=home.getFocusId(),selected=xbmc.getInfoLabel('Container('+str(ident)+').ListItem.Property(Fixture66.Index)'))
    if correct and not collision and detail['selected']==str(index):break
   except (OSError,UnidentifiedImageError):pass
  else:
   Path('/root/media66-last.png').write_bytes(raw)
   Path('/root/media66-error.json').write_text(json.dumps(dict(kind=kind,index=index,detail=detail)))
   raise RuntimeError('FOREIGN66_CONTOUR_OR_PLOT '+repr((kind,index,detail)))
  Path('/root/foreign66-'+kind+'-'+str(index)+'.png').write_bytes(raw)
  foreign66.append(dict(kind=kind,index=index,geometry=detail,contour='PASS',plot_collision='ABSENT'))

# Materialized TV artwork is the same event/file in actual Home and details.
home.setFocusId(2510);home.getControl(2510).selectItem(2);xbmc.sleep(800)
for _ in range(30):
 hero_epg63._next=0;hero_epg63.poll();xbmc.sleep(50)
art66=json.loads(Path('/root/art66.json').read_text())
from programme_window46 import ProgrammeWindow46
import xbmcaddon
window66=ProgrammeWindow46('XCMateProgramme46.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
window66.configure(dict(id='fixture59'),dict(sid='2',name='NITRO fixture',epg_channel_id='xml2'))
window66.show()
for _ in range(100):
 window66.pump()
 if window66.event:break
 xbmc.sleep(50)
check64(window66.event and window66.event['key']==art66['key'],'ART66_DETAIL_IDENTITY')
for attempt in range(30):
 window66.pump();capture=Path('/root/detail66-last.png');xbmc.executebuiltin('TakeScreenshot('+str(capture)+')',wait=False);xbmc.sleep(350)
 try:
  raw=capture.read_bytes()
  with Image.open(io.BytesIO(raw)) as source:source.load();rgb=source.convert('RGB')
  # 720p programme dialog coordinates scaled by Kodi to 1080p.
  if max(abs(a-b) for a,b in zip(rgb.getpixel((500,400)),(40,120,160)))<=6:break
 except (OSError,UnidentifiedImageError):pass
else:raise RuntimeError('ART66_DETAIL_TEXTURE_NOT_RENDERED')
Path('/root/detail66.png').write_bytes(raw)
window66.close();home.setFocusId(2510);xbmc.sleep(500)
result66=json.loads(Path('/root/media66-base.json').read_text())
result66.update(foreign66=foreign66,tv_artwork66=dict(source=art66['source'],scope=art66['scope'],same_event=True,local_file=True,detail_pixels='PASS'),android='NOT_TESTED')
Path('/root/media66.json').write_text(json.dumps(result66))

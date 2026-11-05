"""Native BINGIE Home receiver / screenshot test. Synthetic, never Android."""
import sys,time,json,hashlib,os
from pathlib import Path
sys.path.insert(0,'/root/.kodi/addons/plugin.video.xtreammate/resources/lib')
import xbmc,xbmcgui,xbmcaddon
from PIL import Image,ImageChops
native_addon=xbmcaddon.Addon
xbmcaddon.Addon=lambda *a,**k:native_addon(*a,**k) if a or k else native_addon('plugin.video.xtreammate')
import hero_epg63,home_schedule75 as schedule
from portals import get_active
home=xbmcgui.Window(10000)
for _ in range(200):
    if xbmc.getInfoLabel('Container(2510).NumItems')=='88':break
    xbmc.sleep(100)
else:raise RuntimeError('LIVE75_NOT_LOADED')
watermark=xbmcgui.ControlLabel(20,1048,1850,30,'Synthetic host / Kodi Linux / NOT Android / .75',font='Reg18',textColor='FFFFFFFF')
home.addControl(watermark)
schedule.configure(get_active())
cases=[];traces=[]
def check(value,detail):
    if not value:raise RuntimeError(str(detail))
def pump():
    hero_epg63._next=0;hero_epg63.poll();schedule.observe()
def capture(name):
    path=Path('/root/'+name+'.png')
    xbmc.executebuiltin('TakeScreenshot('+str(path)+')',wait=False)
    for _ in range(40):
        xbmc.sleep(100)
        try:
            with Image.open(path) as image:image.load();rgb=image.convert('RGB').resize((1920,1080))
            return path,rgb
        except (OSError,ValueError):continue
    raise RuntimeError('SCREENSHOT75_INCOMPLETE')
def contours(rgb):
    red,green,blue=rgb.split()
    mask=ImageChops.multiply(ImageChops.multiply(red.point(lambda v:255 if v<50 else 0),green.point(lambda v:255 if v>150 else 0)),blue.point(lambda v:255 if v>220 else 0))
    # Exclude glyphs and watermark: find long cyan lines of the focus frame.
    spans=[]
    for y in range(600,1040):
        run=0;longest=0
        for x in range(240,1880):
            run=run+1 if mask.getpixel((x,y)) else 0;longest=max(longest,run)
        if longest>=90:spans.append(y)
    groups=[]
    for y in spans:
        if not groups or y>groups[-1][-1]+4:groups.append([y])
        else:groups[-1].append(y)
    return [(g[0],g[-1]) for g in groups]
def select(ident,index,kind):
    started=time.monotonic()
    home.setFocusId(ident);home.getControl(ident).selectItem(index)
    for _ in range(30):pump();xbmc.sleep(50)
    path,rgb=capture('home75-'+kind+'-'+str(index))
    frames=contours(rgb)
    # Both boundaries belong to one local focus rectangle; no second rail.
    check(1<=len(frames)<=2,(kind,index,frames))
    title=xbmc.getInfoLabel('ListItem.Label')
    check(home.getFocusId()==ident and title,(kind,index,home.getFocusId(),title))
    image=home.getControl(296751)
    box=(tuple(image.getPosition()),image.getWidth(),image.getHeight())
    check(box==((270,20),1080,580),box)
    if kind=='live' and index==0:
        check(max(abs(a-b) for a,b in zip(rgb.getpixel((500,300)),(20,80,130)))<=5,'EVENT_IMAGE_PIXELS')
        check(max(abs(a-b) for a,b in zip(rgb.getpixel((330,645)),(20,90,150)))<=5,'STATION_LOGO_PIXELS')
    elif kind in ('vod','series'):
        expected=(180,100,30) if kind=='vod' and index==0 else tuple((v+index*step)%240 for v,step in zip((40,70,120) if kind=='vod' else (100,50,20),(19,31,13)))
        check(max(abs(a-b) for a,b in zip(rgb.getpixel((800,150)),expected))<=6,'MEDIA_HERO_PIXELS')
    elif kind.startswith('foreign-'):
        role=kind.removeprefix('foreign-')
        expected=(40+(index%6)*30,60+(index//6)*40,{'poster':45,'music':135,'television':225}[role])
        check(max(abs(a-b) for a,b in zip(rgb.getpixel((800,150)),expected))<=6,'FOREIGN_MEDIA_HERO_PIXELS')
    # The old native caption box leaked here even though the new table was
    # correct. Its absence must be checked on actual pixels, not XML alone.
    check(sum(1 for r,g,b in rgb.crop((120,20,250,500)).getdata() if min(r,g,b)>180)<20,'OLD_LEFT_CAPTION_VISIBLE')
    cases.append(dict(kind=kind,index=index,focus=ident,frames=frames,hero=box,settled_render_ms=round((time.monotonic()-started)*1000,2),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    traces.append(json.loads(home.getProperty(schedule.KEY)))
    return rgb
select(2510,0,'live')
check(json.loads(home.getProperty(schedule.KEY))['phase']==1,'NO_NATIVE_LIVE_READY')
from widget_fast69 import prepare
prepare();xbmc.sleep(300)
select(2520,0,'vod')
check(json.loads(home.getProperty(schedule.KEY))['phase']==2,'NO_NATIVE_MOVIES_READY')
__import__('widget_fast69')._next=0;prepare();xbmc.sleep(300)
select(2530,0,'series')
check(json.loads(home.getProperty(schedule.KEY))['phase']==3,'NO_NATIVE_SERIES_READY')
for i in range(20):select((2510,2520,2530)[i%3],i%20,('live','vod','series')[i%3])
for ident,kind in ((2540,'poster'),(2550,'music'),(2560,'television')):
    for index in (0,23):select(ident,index,'foreign-'+kind)
actions=[]
home.setFocusId(2510);home.getControl(2510).selectItem(0);xbmc.sleep(300)
for i in range(20):
    position=i%10;action='Down' if position<5 else 'Up'
    xbmc.executebuiltin('Action('+action+')',wait=False);xbmc.sleep(350);pump()
    ident=home.getFocusId();path,rgb=capture('home75-action-'+str(i))
    check(ident in (2510,2520,2530,2540,2550,2560),('NATIVE_DIRECTION',action,ident))
    expected_id=(2520,2530,2540,2550,2560,2550,2540,2530,2520,2510)[position]
    check(ident==expected_id,('NATIVE_DIRECTION_DID_NOT_MOVE',action,ident,expected_id))
    check(1<=len(contours(rgb))<=2,('NATIVE_ONE_RAIL',i))
    actions.append(dict(action=action,focus=ident))
home.setFocusId(2510);home.getControl(2510).selectItem(0);xbmc.sleep(200)
xbmc.executebuiltin('Action(Left)',wait=False);xbmc.sleep(400)
check(home.getFocusId()==900,('MENU75_NOT_FOCUSED',home.getFocusId()))
capture('home75-menu')
xbmc.executebuiltin('Action(Right)',wait=False);xbmc.sleep(400)
check(home.getFocusId()!=900,'MENU75_NOT_RELEASED')
# Prove missing progress controls do not abort atomic EPG text publication.
home.setFocusId(2510);home.getControl(2510).selectItem(1);xbmc.sleep(300)
for cid in (296301,296302):
    try:home.removeControl(home.getControl(cid))
    except RuntimeError:pass
hero_epg63._last=None;pump()
bank=home.getProperty('XCMate.Hero63.Active')
check(home.getProperty('XCMate.Hero63.'+bank+'.Title').startswith('Synthetic long programme'),'MISSING_CONTROL_TEXT')
check(home.getProperty('XCMate.Hero63.'+bank+'.ProgressControl')=='UNAVAILABLE','MISSING_CONTROL_NOT_EXERCISED')
duration=int(os.environ.get('XCMATE_IDLE74','0'));started=time.monotonic();checkpoints=[]
while time.monotonic()-started<duration:
    pump()
    elapsed=time.monotonic()-started
    if not checkpoints or elapsed-checkpoints[-1]['elapsed']>=900:
        path,rgb=capture('home75-soak-'+str(int(elapsed)))
        counts=[int(xbmc.getInfoLabel('Container('+str(cid)+').NumItems')) for cid in (2510,2520,2530)]
        check(counts==[88,24,24],counts)
        checkpoints.append(dict(elapsed=elapsed,counts=counts,picture=path.name))
    xbmc.sleep(200)
path,rgb=capture('home75-final')
result=dict(status='PASS',android='ANDROID_NOT_TESTED',kodi=xbmc.getInfoLabel('System.BuildVersion'),cases=cases,traces=traces,native_actions=actions,elapsed_seconds=time.monotonic()-started,checkpoints=checkpoints,missing_control='PASS')
Path('/root/home75.json').write_text(json.dumps(result,indent=2))

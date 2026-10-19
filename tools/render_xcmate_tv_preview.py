"""Fixture layout preview from control coordinates; NOT a Kodi screenshot."""
from pathlib import Path
import sys,time
from PIL import Image,ImageDraw,ImageFont
REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'tests'))
from test_xcmate_kodi21_overlay import OverlayLifecycleTests,ControlImage,ControlLabel,ControlButton
case=OverlayLifecycleTests();case.setUp()
o=case.overlay
root=REPO/'docs/XCMate/assets/026';root.mkdir(parents=True,exist_ok=True)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
try:
 for ch in o.channels:
  now=time.time()
  o._guide._values[ch.extra['stream_id']]=sys.modules['epg_views'].guide_for_channel({'x':[
   dict(name='Nachrichten (Testdaten)',start_timestamp=now-3540,stop_timestamp=now+1860),
   dict(name='Dokumentation (Testdaten)',start_timestamp=now+1860,stop_timestamp=now+5460)]},'x')
 def render(mode,name):
  o._switch(mode)
  im=Image.new('RGBA',(1280,760),(27,29,33,255));d=ImageDraw.Draw(im)
  for y in range(720):d.line((0,y,1280,y),fill=(25+y//18,37+y//25,48+y//30))
  d.text((900,50),'TV-Bild (Platzhalter)',font=ImageFont.truetype(fontpath,20),fill='#B6BCC6')
  for c in o.controls:
   if not c.visible:continue
   opts=c.options;x,y=getattr(c,'position',(opts.get('x',0),opts.get('y',0)))
   w,h=int(getattr(c,'width',opts.get('width',0))),int(opts.get('height',0))
   if w<=0 or h<=0:continue
   if isinstance(c,(ControlImage,ControlButton)):
    texture=getattr(c,'image',opts.get('filename')) if isinstance(c,ControlImage) else opts.get('focusTexture' if o.focus is c else 'noFocusTexture')
    if texture and Path(texture).is_file():
     asset=Image.open(texture).convert('RGBA')
     if opts.get('aspectRatio')==2:
      asset.thumbnail((w,h));im.alpha_composite(asset,(int(x+(w-asset.width)/2),int(y+(h-asset.height)/2)))
     else:im.alpha_composite(asset.resize((w,h)),(int(x),int(y)))
   if isinstance(c,(ControlLabel,ControlButton)):
    label=getattr(c,'label',opts.get('label',''))
    size={'font16':28,'font13':21,'font12':17}.get(opts.get('font'),21)
    layer=Image.new('RGBA',(w,h));draw=ImageDraw.Draw(layer)
    offset=int(opts.get('textOffsetX',0)) if isinstance(c,ControlButton) else 0
    draw.text((offset,2),label,font=ImageFont.truetype(fontpath,size),
              fill='#F0F2F5' if c.enabled else '#6F7780')
    im.alpha_composite(layer,(int(x),int(y)))
  ImageDraw.Draw(im).text((32,731),'Layoutmodell aus Control-Koordinaten / Testdaten / keine Kodi- oder Android-Aufnahme',font=ImageFont.truetype(fontpath,17),fill='#D2D8E0')
  im.convert('RGB').save(root/name)
 render('info','infobar-layout.png')
 render('channels','channels-layout.png')
 render('controls','controls-layout.png')
 render('extras','settings-layout.png')
finally:case.doCleanups()

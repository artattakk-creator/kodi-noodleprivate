"""Host rendering of real InfoBar controls, not an Android screenshot."""
from pathlib import Path
import io,sys,types,re
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];ADDON=ROOT/'src/plugin.video.xtreammate';sys.path.insert(0,str(ADDON/'resources/lib'))
class Control:
 def __init__(self,x,y,width,height,label='',font=None,textColor='0xFFFFFFFF',**kwargs):self.x=x;self.y=y;self.width=width;self.height=height;self.label=label;self.font=font;self.color=textColor;self.visible=True;self.alignment=kwargs.get('alignment',0)
 def setVisible(self,v):self.visible=v
 def setLabel(self,v):self.label=v
 def setImage(self,v):self.label=v
 def setWidth(self,v):self.width=v
 def setHeight(self,v):self.height=v
 def setPosition(self,x,y):self.x=x;self.y=y
class Picture(Control):pass
fontxml=('<fonts><fontset>'+''.join('<font><name>Host'+('Bold' if b else 'Regular')+str(s)+'</name><size>'+str(s)+'</size><style>'+('bold' if b else '')+'</style></font>' for b in (False,True) for s in range(8,81))+'</fontset></fonts>').encode()
sys.modules['xbmcgui']=types.SimpleNamespace(ControlImage=Picture,ControlLabel=Control)
sys.modules['xbmcaddon']=types.SimpleNamespace(Addon=lambda:types.SimpleNamespace(getAddonInfo=lambda _:str(ADDON)))
sys.modules['utils']=types.SimpleNamespace(setting=lambda key,default='':'de_de' if key=='xcmate_ui_language' else default)
sys.modules['xbmcvfs']=types.SimpleNamespace(exists=lambda _:True,File=lambda _:types.SimpleNamespace(readBytes=lambda n:fontxml,close=lambda:None))
from infobar45 import InfoBar
out=ROOT/'docs/XCMate';out.mkdir(exist_ok=True,parents=True)
fontroot=Path('/usr/share/fonts/truetype/dejavu')
def font(size,bold=False):return ImageFont.truetype(str(fontroot/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')),size)
logo=Image.new('RGBA',(416,276));d=ImageDraw.Draw(logo);d.rounded_rectangle((0,0,415,275),radius=42,fill=(5,43,63,255));d.text((208,130),'WELT',font=font(88,True),fill='white',anchor='mm');d.text((208,220),'HD',font=font(34,True),fill='#B7C8D2',anchor='mm');logopath=ROOT/'docs/XCMate/INFOBAR45_HOST_LOGO.png';logo.save(logopath)
for width,height in [(1920,1080),(1280,720)]:
 owner=types.SimpleNamespace();bar=InfoBar(owner,str(ADDON/'resources/media'),width,height)
 info=dict(previous='Talk Spezial',now='Nachrichten am Abend',next='Wirtschaft Live',now_time='20:15',now_end_time='21:00',next_time='21:00',next_end_time='22:00',progress=21/45)
 details=dict(width='1920',height='1080',video='h264',audio='ac3',channels='5.1',language='deu',subtitle_enabled=False,fps='25')
 bar.render('WELT HD',str(logopath),info,details,'Di, 27. Okt. 2026','20:36')
 image=Image.new('RGBA',(width,height));draw=ImageDraw.Draw(image)
 for y in range(height):draw.line((0,y,width,y),fill=(18+int(14*y/height),28+int(16*y/height),42+int(22*y/height),255))
 draw.text((28,30),'HOST-VORSCHAU · Testdaten · kein Android-Screenshot',font=font(round(19*height/1080)),fill='#AAB8C8')
 for c in bar.controls+bar.technology.controls:
  if not c.visible:continue
  if isinstance(c,Picture):
   texture=Image.open(c.label).convert('RGBA').resize((c.width,c.height),Image.Resampling.LANCZOS)
   image.alpha_composite(texture,(c.x,c.y));continue
  if not c.label:continue
  px=int(re.search(r'(\d+)$',c.font).group(1)) if re.search(r'(\d+)$',c.font) else 18
  f=font(px,'Bold' in c.font);text=c.label
  if f.getlength(text)>c.width:raise AssertionError('Reference value clips: '+text+' in '+str(c.width))
  layer=Image.new('RGBA',(c.width,c.height));ld=ImageDraw.Draw(layer);raw=int(c.color.replace('0x',''),16);color=((raw>>16)&255,(raw>>8)&255,raw&255,(raw>>24)&255)
  x=c.width/2 if c.alignment==2 else 0;ld.text((x,c.height/2),text,font=f,fill=color,anchor='mm' if c.alignment==2 else 'lm')
  image.alpha_composite(layer,(c.x,c.y))
 image.convert('RGB').save(out/f'INFOBAR45_HOST_{height}.png',optimize=True)
 print(out/f'INFOBAR45_HOST_{height}.png')
logopath.unlink()

"""Actual addon XML geometry, clearly synthetic host-only preview; no photos."""
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];ADDON=ROOT/'src/plugin.video.xtreammate'
xml=E.parse(ADDON/'resources/skins/Default/720p/XCMateLiveHero48.xml')
image=Image.new('RGB',(1280,720),(9,17,27));draw=ImageDraw.Draw(image)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
values={'ProgrammeChannel46':'TEST TV · synthetischer Sender','ProgrammeTitle46':'Beispielsendung am Abend','ProgrammeTimes46':'20:15 – 21:00','ProgrammeDescription46':'Hier erscheint die tatsächlich gespeicherte Beschreibung der laufenden Sendung. Der Fokus auf einem kleinen Senderbutton ändert die Vorschau; erst OK startet Live-TV.\n\nDas Beispielbild ist ein neutraler Platzhalter. Echte Sendungsbilder und Android-Darstellung sind nicht abgenommen.','ProgrammeNext46':'Die nächste Beispielsendung','ProgrammeNextTimes48':'21:00 – 21:45'}
def textfit(node,x,y,w,h,value):
 size={'font12':16,'font13':20,'font16':28}.get(node.findtext('font'),20);font=ImageFont.truetype(fontpath,size)
 layer=Image.new('RGBA',(w,h));ld=ImageDraw.Draw(layer);lines=[]
 for paragraph in value.split('\n'):
  line=''
  for word in paragraph.split():
   if line and font.getlength(line+' '+word)>w-4:lines.append(line);line=''
   line+=((' ' if line else '')+word)
  lines.append(line)
 for index,line in enumerate(lines):ld.text((0,index*(size+6)),line,font=font,fill='#f2f5f8')
 image.paste(layer,(x,y),layer)
group=xml.find('controls/control')
for node in group:
 if node.tag!='control':continue
 x,y,w,h=[int(node.findtext(k,'0')) for k in ('left','top','width','height')]
 if not w or not h:continue
 kind=node.get('type')
 if kind=='image':
  value=node.findtext('texture','')
  if 'ProgrammeImage46' in value:value=str(ADDON/'resources/media/programme46/neutral.png')
  elif 'ProgrammeLogo46' in value:
   draw.rounded_rectangle((x,y,x+w,y+h),radius=5,fill='#174b71');draw.text((x+7,y+15),'TEST TV',font=ImageFont.truetype(fontpath,17),fill='white');continue
  if value.startswith('special://home/addons/plugin.video.xtreammate/'):value=str(ADDON/value.split('plugin.video.xtreammate/',1)[1])
  if Path(value).is_file():
   art=Image.open(value).convert('RGBA');art=art.resize((w,h));image.paste(art,(x,y),art)
 elif kind in ('label','textbox'):
  value=node.findtext('label','')
  if node.get('id')=='101':value='XCMate .48 · Live-TV-Vorschau · synthetische Beispieldaten'
  for field,replacement in values.items():value=value.replace('$INFO[Container(200).ListItem.Property(XCMate.'+field+')] ',replacement+' ').replace('$INFO[Container(200).ListItem.Property(XCMate.'+field+')]',replacement)
  textfit(node,x,y,w,h,value)
 elif kind=='progress':
  draw.rounded_rectangle((x,y,x+w,y+h),radius=4,fill='#46515d');draw.rounded_rectangle((x,y,x+int(w*.46),y+h),radius=4,fill='#4ccf4c')
 elif kind=='panel':
  width=int(node.find('itemlayout').get('width'))
  for i in range(w//width):
   left=x+i*width;draw.rounded_rectangle((left+2,y+2,left+width-4,y+100),radius=6,fill='#183145',outline='#4ccf4c' if i==2 else '#304253',width=3)
   draw.rounded_rectangle((left+37,y+10,left+105,y+50),radius=4,fill='#174b71');draw.text((left+41,y+21),'TEST '+str(i+1),font=ImageFont.truetype(fontpath,13),fill='white')
   draw.text((left+12,y+65),'Sender '+str(i+1),font=ImageFont.truetype(fontpath,16),fill='white')
draw.text((44,694),'HOST-ENTWURF · kein Android-Screenshot · BINGIE-Anbindung separat BLOCKED_SKIN_INTEGRATION',font=ImageFont.truetype(fontpath,13),fill='#aab9cb')
output=ROOT/'docs/XCMate/LIVE_HERO_02948_HOST.png';output.parent.mkdir(parents=True,exist_ok=True);image.save(output,optimize=True);print(output)

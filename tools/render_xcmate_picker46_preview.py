"""Host-only rendering of the actual picker geometry, with synthetic artwork."""
from pathlib import Path
import sys,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];A=R/'src/plugin.video.xtreammate'
sys.path.insert(0,str(A/'resources/lib'))
from localization import read_catalog
texts=read_catalog(A/'resources/language/resource.language.de_de/strings.po')
root=ET.parse(A/'resources/skins/Default/720p/XCMateArtwork43.xml')
canvas=Image.new('RGB',(1280,720),(9,17,28));draw=ImageDraw.Draw(canvas)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def write(x,y,text,size=16,color='#f1f4f7'):draw.text((x,y),str(text),font=ImageFont.truetype(font,size),fill=color)
write(60,8,'HOST-VORSCHAU · synthetische Musterbilder · kein Android-Screenshot',13,'#8fa8bf')
draw.rounded_rectangle((48,28,1232,692),radius=16,fill='#111c2c');write(78,46,'Cover / Metadaten auswählen',24);write(78,84,'Testtitel – tatsächliche Bildquellen und Gerätedarstellung sind NOT_TESTED',17,'#b7c7d8')
for cid,n in [(401,35900),(402,35901),(403,35902),(404,35903),(405,35904),(406,36121),(407,35931),(408,35932)]:
 node=root.find('.//control[@id="'+str(cid)+'"]');x,y,w,h=[int(node.findtext(k)) for k in ('left','top','width','height')]
 draw.rounded_rectangle((x,y,x+w,y+h),radius=5,fill='#23597a' if cid==406 else '#1d3045')
 label=texts.get(n,str(n));fit=ImageFont.truetype(font,15)
 while fit.getlength(label)>w-32:label=label[:-2].rstrip('…')+'…'
 write(x+16,y+8,label,15)
node=root.find('.//control[@id="200"]');x,y,w,h=[int(node.findtext(k)) for k in ('left','top','width','height')];layout=node.find('itemlayout');cw,ch=int(layout.get('width')),int(layout.get('height'))
for pos in range(10):
 left=x+(pos%5)*cw;top=y+(pos//5)*ch
 if pos==0:draw.rounded_rectangle((left,top,left+216,top+206),radius=6,outline='#71df74',width=3)
 draw.rectangle((left+58,top+6,left+158,top+156),fill=['#294761','#49567b','#366659','#6b4c64','#535f74'][pos%5])
 draw.ellipse((left+85,top+45,left+130,top+90),outline='#c3d2dd',width=3);write(left+70,top+114,'MUSTER',13)
 write(left+8,top+158,'Vorschlag '+str(pos+1),16);write(left+8,top+182,'OK: größere Vorschau',12,'#b5c6d6')
write(78,650,'Testdaten: keine echten Providerbilder. Auswahl → Vorschau → Übernehmen → Speichern.',16,'#f1d18a')
output=R/'docs/XCMate/COVER46_HOST_720.png';canvas.save(output,optimize=True);print(output)

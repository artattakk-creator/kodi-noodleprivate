"""Render the actual programme XML geometry with clearly marked host test data."""
from pathlib import Path
import textwrap,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];A=R/'src/plugin.video.xtreammate';OUT=R/'docs/XCMate';OUT.mkdir(parents=True,exist_ok=True)
FONT=Path('/usr/share/fonts/truetype/dejavu');tree=ET.parse(A/'resources/skins/Default/720p/XCMateProgramme46.xml')
labels={'101':'Beispielserie','104':'Neutraler Platzhalter · kein verifiziertes Sendungsbild','106':'Hoch/Runter: Beschreibung lesen · Zurück: Details schließen','501':'Zurück','112':'TEST TV','103':'TEST TV\nBeispielserie\n27.10. 20:15 – 21:00 · 45 min\nDie Rückkehr\nStaffel 2 · Folge 3\nDrama\n2024\nBesetzung: Darsteller A, Darsteller B\n\nDies ist eine Hostvorschau mit Testdaten. Die lokale EPG-Beschreibung bleibt auch ohne Internet lesbar. Das Senderlogo liegt als separate Ebene links oben auf dem Programmbild.\n\nDie echte Android-Darstellung, Bilder der Provider und die Fernbedienungsabnahme sind NOT_TESTED.'}
for width,height in [(1280,720),(1920,1080)]:
 scale=width/1280;im=Image.new('RGB',(width,height),(9,17,28));d=ImageDraw.Draw(im)
 for n in tree.findall('.//control'):
  cid=n.get('id');kind=n.get('type');x,y,w,h=[int(int(n.findtext(k,'0'))*scale) for k in ('left','top','width','height')]
  if not w or not h:continue
  if kind=='image':
   texture=n.findtext('texture') or ''
   if cid=='110':texture=str(A/'resources/media/programme46/series.png')
   elif cid=='111':continue
   elif cid=='881':texture=str(A/'resources/media/menu45/full/back.png')
   elif cid=='121':w=round(536*.46*scale)
   if texture.startswith('special://home/addons/plugin.video.xtreammate/'):texture=str(A/texture.split('plugin.video.xtreammate/',1)[1])
   if texture and Path(texture).is_file():
    image=Image.open(texture).convert('RGBA');image.thumbnail((w,h)) if n.findtext('aspectratio')=='keep' else None
    if n.findtext('aspectratio')!='keep':image=image.resize((w,h))
    im.paste(image,(x+(w-image.width)//2,y+(h-image.height)//2),image)
  elif kind in ('label','textbox','button'):
   if kind=='button':d.rounded_rectangle((x,y,x+w,y+h),radius=8,fill='#225f83')
   text=labels.get(cid,'');size={'font16':28,'font13':20,'font12':15}.get(n.findtext('font'),18);font=ImageFont.truetype(str(FONT/'DejaVuSans.ttf'),round(size*scale));color='#f1f4f7' if kind!='label' or cid=='101' else '#b5c4d2'
   lines=[]
   for paragraph in text.split('\n'):
    line=''
    for word in paragraph.split(' '):
     if font.getlength(line+word)>w-8 and line:lines.append(line.rstrip());line=''
     line+=word+' '
    lines.append(line.rstrip())
   layer=Image.new('RGBA',(w,h));ld=ImageDraw.Draw(layer)
   for i,line in enumerate(lines):ld.text((40*scale if kind=='button' else 0,i*round(size*1.35*scale)),line,font=font,fill=color)
   im.paste(layer,(x,y),layer)
 d.text((35*scale,8*scale),'HOST-VORSCHAU · Testdaten · kein Android-Screenshot',font=ImageFont.truetype(str(FONT/'DejaVuSans.ttf'),round(12*scale)),fill='#90a3b9')
 file=OUT/f'PROGRAMME46_HOST_{height}.png';im.save(file,optimize=True);print(file)

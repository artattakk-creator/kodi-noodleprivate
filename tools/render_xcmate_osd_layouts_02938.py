"""Three local design diagrams, explicitly not Android screenshots or approval."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/XCMate/osd_02938'
MEDIA=ROOT/'src/plugin.video.xtreammate/resources/media/navigation'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(size):return ImageFont.truetype(FONT,size)
def main():
 OUT.mkdir(exist_ok=True);manifest={}
 variants=[('A','Zweizeilige Transportbar – technischer Kandidat'),('B','Zentrale Transportgruppe mit seitlichen Aktionen'),('C','Kompakte Kinoleiste mit getrennten Optionen')]
 for name,title in variants:
  im=Image.new('RGB',(1280,720),(28,31,36));d=ImageDraw.Draw(im)
  for y in range(110,510):d.line((0,y,1280,y),fill=(24+y//24,26+y//24,31+y//24))
  d.text((36,24),'XCMate · Entwurf '+name,font=font(30),fill='#edf1f5');d.text((36,68),title,font=font(23),fill='#bfc7d2')
  d.text((36,142),'Layoutskizze mit Beispieldaten · kein Android-Screenshot',font=font(19),fill='#bec4cd')
  panel=(28,400,1252,692) if name=='A' else (100,440,1180,690) if name=='B' else (28,494,1252,692)
  d.rounded_rectangle(panel,18,fill='#20242b',outline='#5b646f',width=2)
  d.text((panel[0]+24,panel[1]+18),'Filmtitel / Serienfolge',font=font(24),fill='#f5f7f9')
  d.text((panel[0]+24,panel[1]+54),'00:10:00  /  00:45:00     Noch 00:35:00',font=font(18),fill='#bdc5cf')
  x0,x1=panel[0]+24,panel[2]-24-(180 if name=='B' else 0);y=panel[1]+88
  d.rounded_rectangle((x0,y,x1,y+6),3,fill='#626a76');d.rounded_rectangle((x0,y,x0+(x1-x0)*.22,y+6),3,fill='#90d4f5')
  transport=[('player-track-prev','Spulen'),('rewind-backward-10','−10 s'),('player-pause','Pause'),('player-stop','Stop'),('rewind-forward-30','+30 s'),('player-track-next','Spulen')]
  settings=[('volume','Ton'),('badge-cc','Untertitel'),('device-tv','Bild'),('adjustments','Audio'),('info-circle','Info'),('calendar','EPG / Optionen')]
  rows=[(transport,panel[1]+110),(settings,panel[1]+190)] if name=='A' else [(transport,panel[1]+115)] if name=='B' else [(transport[1:5],panel[1]+112)]
  for entries,top in rows:
   step=(panel[2]-panel[0]-48-(180 if name=='B' else 0))//len(entries)
   for i,(icon,label) in enumerate(entries):
    x=x0+i*step;selected=icon=='player-pause'
    d.rounded_rectangle((x,top,x+step-10,top+66),9,fill='#404c5a' if selected else '#2b3039',outline='#b4e0f9' if selected else '#434a56',width=2)
    art=Image.open(MEDIA/(icon+'-focused.png')).convert('RGBA').resize((28,28));im.paste(art,(x+12,top+18),art)
    d.text((x+47,top+23),label,font=font(15),fill='#f0f3f7')
  if name=='B':
   d.line((996,452,996,676),fill='#626a76',width=2)
   for i,(ico,label) in enumerate(settings[:3]+[settings[4]]):
    x,top=1010,453+i*56;d.rounded_rectangle((x,top,1156,top+46),8,fill='#2b3039',outline='#626a76')
    art=Image.open(MEDIA/(ico+'-focused.png')).convert('RGBA').resize((24,24));im.paste(art,(x+8,top+11),art)
    d.text((x+40,top+14),label,font=font(14),fill='#edf1f5')
  if name=='C':
   d.rounded_rectangle((1030,510,1220,556),8,fill='#2b3039',outline='#626a76')
   d.text((1052,524),'Optionen ▾',font=font(17),fill='#edf1f5')
  d.text((36,360),'Live: 1× OK Info · 2× OK/Runter Controls. VOD: Kodi-Fähigkeiten bestimmen verfügbare Aktionen.',font=font(17),fill='#c5ced9')
  path=OUT/(name+'.png');im.save(path,optimize=True);manifest[name]=dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),status='DESIGN_NOT_APPROVED; NOT_A_DEVICE_SCREENSHOT')
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()

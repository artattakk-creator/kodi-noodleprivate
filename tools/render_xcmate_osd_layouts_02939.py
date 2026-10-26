"""Two reproducible design diagrams; no Android screenshot or approved design."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/XCMate/osd_02939'
MEDIA=ROOT/'src/plugin.video.xtreammate/resources/media/navigation'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def main():
    OUT.mkdir(exist_ok=True);manifest={}
    for variant,title in [('A','Transport groß · technische Arbeitsvariante'),('B','Transport zentral · Optionen seitlich')]:
        canvas=Image.new('RGB',(1280,720),'#141b27');draw=ImageDraw.Draw(canvas)
        def text(x,y,value,size=20,color='#edf2f9'):
            draw.text((x,y),value,font=ImageFont.truetype(FONT,size),fill=color)
        text(32,22,'XCMate .39 · Entwurf '+variant,30)
        text(32,66,title,23,'#b9c7d8')
        text(32,110,'Layoutskizze mit fiktiven Beispieldaten · Android NOT_TESTED · Design nicht abgenommen',17,'#a6b5c8')
        draw.rounded_rectangle((32,168,1248,304),12,fill='#202d40',outline='#526783',width=2)
        text(54,184,'1× OK Live: Sender · JETZT Beispielsendung · DANACH Folgeprogramm',23)
        text(54,224,'1920×1080i · 50 fps · H.264 | AAC 2.0 · DE | Untertitel: aus',19,'#b9c7d8')
        text(54,264,'Nur tatsächlich gemeldete Kodi21-Felder anzeigen; fehlende Werte bleiben unbekannt.',17,'#a6b5c8')
        draw.rounded_rectangle((28,340,1252,694),16,fill='#202734',outline='#526783',width=2)
        text(52,360,'Filmtitel / Serienfolge',25)
        text(52,402,'00:10:00 / 00:45:00 · Noch 00:35:00',18,'#b9c7d8')
        end=1216 if variant=='A' else 956
        draw.rounded_rectangle((52,438,end,445),3,fill='#526783')
        draw.rounded_rectangle((52,438,52+(end-52)*.22,445),3,fill='#87d4fb')
        actions=[('player-track-prev','Zurückspulen'),('player-skip-back','−30 s'),('rewind-backward-10','−10 s'),('player-pause','Pause'),('player-stop','Stop'),('rewind-forward-30','+30 s'),('player-skip-forward','+10 s'),('player-track-next','Vorspulen')]
        step=(end-52)//len(actions)
        for i,(icon,label) in enumerate(actions):
            x=52+i*step;selected=icon=='player-pause'
            draw.rounded_rectangle((x,472,x+step-8,578),10,fill='#354e69' if selected else '#2a3444',outline='#a7e4ff' if selected else '#526783',width=3 if selected else 1)
            art=Image.open(MEDIA/(icon+'-focused.png')).convert('RGBA').resize((48,48))
            canvas.paste(art,(x+(step-48)//2-4,480),art)
            label_font=ImageFont.truetype(FONT,14 if variant=='A' else 12)
            box=draw.textbbox((0,0),label,font=label_font)
            draw.text((x+(step-8-box[2])//2,547),label,font=label_font,fill='#f3f7fb')
        options=[('volume','Ton'),('badge-cc','Untertitel'),('device-tv','Bild'),('adjustments','Audio'),('info-circle','Technik / Info'),('playlist','Autoplay')]
        for i,(icon,label) in enumerate(options):
            x,y,width=(52+i*194,610,182) if variant=='A' else (988,356+i*50,236)
            draw.rounded_rectangle((x,y,x+width,y+40),7,fill='#2a3444',outline='#526783')
            art=Image.open(MEDIA/(icon+'-normal.png')).convert('RGBA').resize((24,24));canvas.paste(art,(x+8,y+8),art)
            text(x+42,y+10,label,16)
        text(52,668,'VOD: sichtbares OSD → Back blendet aus · verborgenes Vollbild → Back stoppt und kehrt zurück',16,'#b9c7d8')
        target=OUT/(variant+'.png');canvas.save(target,optimize=True)
        manifest[variant]=dict(file=target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),status='DESIGN_NOT_APPROVED; NOT_A_DEVICE_SCREENSHOT; SAMPLE_DATA')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()

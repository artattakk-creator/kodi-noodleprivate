"""Original generic geometric UI symbols, no external icon/font dependency."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'src/plugin.video.xtreammate/resources/media/infomicro44';folder.mkdir(exist_ok=True)
for kind in ('monitor','speaker'):
    image=Image.new('RGBA',(384,384));draw=ImageDraw.Draw(image);color=(182,188,198,255)
    if kind=='monitor':
        draw.rounded_rectangle((32,52,352,272),radius=16,outline=color,width=16)
        draw.line((192,274,192,328),fill=color,width=16);draw.line((132,332,252,332),fill=color,width=16)
    else:
        draw.line([(40,148),(112,148),(200,72),(200,312),(112,236),(40,236),(40,148)],fill=color,width=16,joint='curve')
        draw.arc((140,100,292,284),-65,65,fill=color,width=14);draw.arc((104,52,348,332),-65,65,fill=color,width=14)
    image.resize((96,96),Image.Resampling.LANCZOS).save(folder/(kind+'.png'),optimize=True)
(folder/'ORIGIN.txt').write_text('Original GS Media / XCMate generic monitor and speaker geometry.\nCreated by tools/build_xcmate_infomicro44.py; project GPL-2.0-only license.\nNo external logos, fonts or third-party image source.\n')

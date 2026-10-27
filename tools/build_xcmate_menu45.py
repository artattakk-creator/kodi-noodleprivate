"""Original geometric menu glyphs, local GPL-2.0-only assets; no font/network."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/media/menu45'
NAMES=('tv','movie','series','search','star','calendar','database','refresh','user','plus','pencil','link','list','play','speaker','cc','globe','remote','image','grid','palette','drive','shield','info','flask-lock','record','download','activity','clock','document','settings','trash','back','wand','check')
def build(name):
 im=Image.new('RGBA',(384,384));d=ImageDraw.Draw(im);c=(205,213,222,255);w=16
 def line(points):d.line([(int(x*4),int(y*4)) for x,y in points],fill=c,width=w,joint='curve')
 def rect(box,r=5):d.rounded_rectangle(tuple(int(x*4) for x in box),radius=r*4,outline=c,width=w)
 def ellipse(box):d.ellipse(tuple(int(x*4) for x in box),outline=c,width=w)
 if name in ('tv','series'):
  rect((12,20,84,70));line([(48,70),(48,82)]);line([(30,82),(66,82)])
  if name=='series':line([(24,11),(72,11)])
 elif name=='movie':
  rect((12,29,84,78));rect((12,14,84,29),1)
  for x in (22,44,66):line([(x,15),(x+10,28)])
 elif name=='search':ellipse((12,12,64,64));line([(58,58),(84,84)])
 elif name=='star':line([(48,10),(59,35),(86,37),(65,56),(72,84),(48,69),(24,84),(31,56),(10,37),(37,35),(48,10)])
 elif name=='calendar':rect((15,20,81,83));line([(15,37),(81,37)]);line([(31,12),(31,27)]);line([(65,12),(65,27)]);line([(30,54),(41,54)]);line([(55,68),(66,68)])
 elif name=='database':
  ellipse((15,12,81,36));line([(15,24),(15,72)]);line([(81,24),(81,72)]);d.arc((60,232,324,344),0,180,fill=c,width=w);d.arc((60,128,324,240),0,180,fill=c,width=w)
 elif name=='refresh':d.arc((48,48,336,336),-55,240,fill=c,width=w);line([(80,15),(80,40),(57,40)]);line([(16,82),(16,58),(39,58)])
 elif name=='user':ellipse((31,10,65,44));d.arc((56,200,328,384),180,360,fill=c,width=w);line([(14,73),(14,84)]);line([(82,73),(82,84)])
 elif name=='plus':line([(48,15),(48,81)]);line([(15,48),(81,48)])
 elif name=='pencil':line([(17,65),(64,18),(79,33),(32,80),(14,83),(17,65)]);line([(57,25),(72,40)])
 elif name=='link':d.arc((32,112,216,320),45,315,fill=c,width=w);d.arc((168,48,352,256),225,495,fill=c,width=w);line([(34,62),(64,32)])
 elif name=='list':
  for y in (24,48,72):ellipse((13,y-2,17,y+2));line([(31,y),(83,y)])
 elif name=='play':ellipse((10,10,86,86));line([(39,28),(67,48),(39,68),(39,28)])
 elif name=='speaker':line([(14,36),(29,36),(48,18),(48,78),(29,60),(14,60),(14,36)]);d.arc((120,72,328,312),-65,65,fill=c,width=w)
 elif name=='cc':
  rect((10,20,86,76))
  for x in (16,48):d.arc((x*4,128,(x+29)*4,256),55,305,fill=c,width=w)
 elif name=='globe':ellipse((10,10,86,86));ellipse((31,10,65,86));line([(12,48),(84,48)]);d.arc((40,40,344,216),0,180,fill=c,width=w);d.arc((40,168,344,344),180,360,fill=c,width=w)
 elif name=='remote':
  rect((26,8,70,88),12);ellipse((38,19,58,39))
  for x in (36,54):
   for y in (53,67,79):rect((x,y,x+5,y+4),1)
 elif name=='image':rect((10,14,86,82));ellipse((25,25,39,39));line([(13,70),(39,45),(56,62),(68,49),(84,66)])
 elif name=='grid':
  for x in (14,54):
   for y in (14,54):rect((x,y,x+28,y+28))
 elif name=='palette':
  d.arc((40,40,344,344),-30,280,fill=c,width=w);line([(55,12),(79,19),(86,36),(69,47),(58,43),(50,51),(56,65),(50,82)])
  for x,y in ((27,31),(43,23),(24,51)):ellipse((x,y,x+7,y+7))
 elif name=='drive':rect((12,19,84,77));line([(12,57),(84,57)]);ellipse((67,65,72,70));line([(24,67),(39,67)])
 elif name=='shield':line([(48,10),(81,23),(76,60),(63,77),(48,87),(33,77),(20,60),(15,23),(48,10)]);line([(31,47),(43,59),(66,34)])
 elif name=='info':ellipse((11,11,85,85));line([(48,42),(48,70)]);ellipse((46,26,50,30))
 elif name=='flask-lock':line([(31,13),(56,13)]);line([(35,14),(35,38),(15,75),(20,83),(62,83),(66,75),(51,38),(51,14)]);line([(27,58),(58,58)]);rect((60,54,87,82));d.arc((244,160,344,264),180,360,fill=c,width=w)
 elif name=='record':ellipse((12,12,84,84));d.ellipse((112,112,272,272),fill=c)
 elif name=='download':line([(48,12),(48,64)]);line([(28,46),(48,66),(68,46)]);line([(16,69),(16,83),(80,83),(80,69)])
 elif name=='activity':line([(9,51),(28,51),(39,21),(57,78),(69,42),(79,51),(88,51)])
 elif name=='clock':ellipse((10,10,86,86));line([(48,25),(48,49),(66,59)])
 elif name=='document':line([(24,10),(58,10),(78,30),(78,86),(24,86),(24,10)]);line([(57,12),(57,31),(76,31)]);line([(35,49),(66,49)]);line([(35,65),(66,65)])
 elif name=='settings':
  ellipse((23,23,73,73));ellipse((38,38,58,58))
  for pts in [[(48,9),(48,24)],[(48,72),(48,87)],[(9,48),(24,48)],[(72,48),(87,48)],[(20,20),(30,30)],[(66,66),(77,77)],[(20,77),(30,66)],[(66,30),(77,20)]]:line(pts)
 elif name=='trash':rect((25,28,71,84));line([(17,24),(79,24)]);line([(37,14),(59,14)]);line([(39,40),(39,70)]);line([(57,40),(57,70)])
 elif name=='back':line([(38,18),(13,43),(38,68)]);line([(15,43),(60,43),(80,58),(80,81)])
 elif name=='wand':line([(18,80),(71,27)]);line([(28,85),(78,35)]);line([(57,14),(57,3)]);line([(82,11),(89,4)]);line([(84,27),(95,27)])
 elif name=='check':line([(17,49),(38,71),(81,24)])
 return im.resize((96,96),Image.Resampling.LANCZOS)
if __name__=='__main__':
 ROOT.mkdir(exist_ok=True);(ROOT/'full').mkdir(exist_ok=True)
 for name in NAMES:
  glyph=build(name);glyph.save(ROOT/'full'/(name+'.png'),optimize=True)
  canvas=Image.new('RGBA',(96,96));canvas.alpha_composite(glyph.resize((36,36),Image.Resampling.LANCZOS),(30,30));canvas.save(ROOT/(name+'.png'),optimize=True)
 (ROOT/'ORIGIN.txt').write_text('Original GS Media / XCMate generic geometric menu symbols.\nGPL-2.0-only, same license as project. Generated by tools/build_xcmate_menu45.py.\nNo external images, marks, fonts or network. Full glyphs for own XML; padded glyphs for Kodi-native ListItems.\n')

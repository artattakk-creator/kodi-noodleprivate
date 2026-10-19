"""Render original geometric TV icons and Slate panels; requires Pillow."""
from pathlib import Path
from PIL import Image,ImageDraw
folder=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/media'
Image.new('RGBA',(16,16),(27,29,33,225)).save(folder/'tv_panel.png')
Image.new('RGBA',(16,8),(110,189,217,255)).save(folder/'tv_progress.png')
Image.new('RGBA',(16,16),(58,75,91,255)).save(folder/'tv_focus.png')
Image.new('RGBA',(16,16),(41,45,51,245)).save(folder/'tv_normal.png')
for name in ('pause','play','live','stop','back','forward','more','audio','video','subtitle','epg','settings','tv'):
 im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im);c=(240,242,245,255)
 if name=='pause':
  d.rectangle((16,12,26,52),fill=c);d.rectangle((38,12,48,52),fill=c)
 elif name=='play':d.polygon([(19,12),(51,32),(19,52)],fill=c)
 elif name=='live':
  d.polygon([(12,14),(39,32),(12,50)],fill=c);d.rectangle((44,14,50,50),fill=c)
 elif name=='stop':d.rounded_rectangle((14,14,50,50),radius=3,fill=c)
 elif name in ('back','forward'):
  d.polygon([(12,32),(31,14),(31,50)],fill=c);d.polygon([(31,32),(51,14),(51,50)],fill=c)
  if name=='forward':im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 elif name=='more':
  for x in (12,28,44):d.ellipse((x,27,x+8,35),fill=c)
 elif name=='audio':
  d.polygon([(10,25),(22,25),(36,14),(36,50),(22,39),(10,39)],fill=c)
  d.arc((28,12,57,52),-60,60,fill=c,width=4)
 elif name=='subtitle':
  d.rounded_rectangle((5,13,59,51),radius=5,outline=c,width=4)
  for x in (17,36):d.arc((x,23,x+13,41),70,290,fill=c,width=3)
 elif name=='settings':
  d.ellipse((12,12,52,52),outline=c,width=9);d.ellipse((27,27,37,37),fill=c)
  for xy in ((27,5,37,15),(27,49,37,59),(5,27,15,37),(49,27,59,37)):d.rectangle(xy,fill=c)
 else:
  d.rounded_rectangle((7,12,57,47),radius=4,outline=c,width=4)
  if name=='epg':
   for y in (22,32,41):d.line((16,y,47,y),fill=c,width=3)
  else:d.line((23,54,41,54),fill=c,width=4)
 im.save(folder/('tv_'+name+'.png'))

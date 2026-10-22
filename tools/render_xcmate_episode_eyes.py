"""Small deterministic Kodi PNGs; user's green=unseen / red=watched convention."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/media'
for name,color in [('eye_unseen.png',(67,225,92,255)),('eye_watched.png',(246,71,76,255))]:
    image=Image.new('RGBA',(40,24));draw=ImageDraw.Draw(image)
    draw.polygon([(2,12),(9,5),(20,2),(31,5),(38,12),(31,19),(20,22),(9,19)],fill=color)
    draw.ellipse((11,3,29,21),fill=(16,20,24,255));draw.ellipse((15,7,25,17),fill=color)
    image.save(ROOT/name,optimize=False)

"""Render/check only selected pinned MIT Tabler icons. Never runtime downloads."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'third_party/tabler-icons'
TARGET=ROOT/'src/plugin.video.xtreammate/resources/media/navigation'
COLORS=dict(normal='#bec4cd',focused='#ffffff',selected='#8bd2f4',disabled='#727985')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');p.add_argument('--check',action='store_true');args=p.parse_args()
 if args.render:
  import cairosvg
  TARGET.mkdir(parents=True,exist_ok=True);data=json.loads((SOURCE/'upstream.json').read_text());data['license']='MIT';data['icons']={}
  for svg in sorted(SOURCE.glob('*.svg')):
   entry=dict(source='third_party/tabler-icons/'+svg.name,source_sha256=sha(svg),textures={})
   for state,color in COLORS.items():
    out=TARGET/(svg.stem+'-'+state+'.png');text=svg.read_text().replace('currentColor',color)
    cairosvg.svg2png(bytestring=text.encode(),write_to=str(out),output_width=96,output_height=96)
    entry['textures'][state]=dict(file=out.name,sha256=sha(out))
   data['icons'][svg.stem]=entry
  (TARGET/'manifest.json').write_text(json.dumps(data,indent=2)+'\n')
  (ROOT/'src/plugin.video.xtreammate/THIRD_PARTY_TABLER.txt').write_text('XCMate navigation and player controls\nTabler Icons '+data['version']+'\nhttps://github.com/tabler/tabler-icons/tree/'+data['commit']+'\nOriginal SVGs, hashes and derived PNGs: resources/media/navigation/manifest.json\n\n'+(SOURCE/'LICENSE').read_text())
 from PIL import Image
 data=json.loads((TARGET/'manifest.json').read_text());count=0
 assert data['license']=='MIT' and len(data['commit'])==40
 assert 'MIT License' in (ROOT/'src/plugin.video.xtreammate/THIRD_PARTY_TABLER.txt').read_text()
 for entry in data['icons'].values():
  assert sha(ROOT/entry['source'])==entry['source_sha256']
  for texture in entry['textures'].values():
   path=TARGET/texture['file'];assert sha(path)==texture['sha256']
   with Image.open(path) as im:im.verify()
   with Image.open(path) as im:assert im.size==(96,96) and im.mode=='RGBA'
   count+=1
 print('Tabler provenance, license and PNG verification PASS:',count,'textures')
if __name__=='__main__':main()

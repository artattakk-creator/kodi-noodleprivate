"""Install disposable independent fixture sources and private existing layout."""
from pathlib import Path
import hashlib,json,math,shutil,struct,wave
from PIL import Image
import sys
sys.path.insert(0,'/')
from spec87 import FOREIGN,uri
root=Path('/root/.kodi');folder=root/'userdata/addon_data/script.skinshortcuts';folder.mkdir(parents=True,exist_ok=True)
rows=[]
for menu,values in [('10000',[("Live-TV",'plugin://plugin.video.xtreammate/?action=widget_live_start_group&pid=fixture59&home50=1','videos'),('Filme','plugin://plugin.video.xtreammate/?action=widget_recent_vod&pid=fixture59','videos'),('Serien','plugin://plugin.video.xtreammate/?action=widget_recent_series&pid=fixture59','videos')]+[(v[0],uri(i),v[3]) for i,v in enumerate(FOREIGN[:5])]),('10001',[(v[0],uri(i),v[3]) for i,v in enumerate(FOREIGN)])]:
 for i,(name,path,target) in enumerate(values):
  suffix='.'+str(i) if i else ''
  for key,value in dict(widget='Addon',widgetName=name,widgetPath=path,widgetTarget=target,widgetStyle='poster').items():rows.append(['mainmenu',menu,key+suffix,value])
(folder/'skin.titan.bingie.mod.properties').write_text(repr(rows))
# The native compiler output has already been installed from /candidate.
protected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}
Path('/root/old-layout78.json').write_text(json.dumps(protected))
Path('/root/foreign87-inventory.json').write_text(json.dumps(rows))
for i,(name,addon,content,target,color) in enumerate(FOREIGN):
 Image.new('RGB',(240,360),color).save('/root/foreign87-'+str(i)+'.png')
 path=root/'addons'/addon;path.mkdir(exist_ok=True)
 (path/'addon.xml').write_text('<addon id="'+addon+'" name="Synthetic independent '+name+'" version="1.0.0" provider-name="Test"><requires><import addon="xbmc.python" version="3.0.1"/></requires><extension point="xbmc.python.pluginsource" library="default.py"><provides>audio video</provides></extension><extension point="xbmc.addon.metadata"><summary lang="en_GB">Synthetic fixture</summary><description lang="en_GB">Not the actual external provider implementation.</description><platform>all</platform><license>GPL-2.0-only</license></extension></addon>')
 shutil.copyfile('/foreign87.py',path/'default.py')
with wave.open('/root/foreign87.wav','wb') as stream:
 stream.setnchannels(1);stream.setsampwidth(2);stream.setframerate(8000);stream.writeframes(b''.join(struct.pack('<h',int(2000*math.sin(i/8000*2*math.pi*440))) for i in range(8000*8)))

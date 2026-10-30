"""Synthetic provider rows; delegates all regular invocations to real default.py."""
import os,sys,json,time,hashlib
from pathlib import Path
from urllib.parse import parse_qs
import xbmc,xbmcgui,xbmcplugin,xbmcaddon
root=Path(__file__).parent;sys.path.insert(0,str(root/'resources/lib'))
p=parse_qs(sys.argv[2].lstrip('?'));handle=int(sys.argv[1])
if p.get('fixture59')==['seed']:
 from utils import addon_data_dir
 from library_index import replace_catalog
 import portals
 from PIL import Image,ImageDraw
 portal=dict(id='fixture59',name='Synthetic fixture only',type='xtream',enabled=True,xc_host='https://provider.example.test',xc_user='fixture',xc_pass='synthetic',include_live=True,include_vod=True,include_series=True,start_group_id='a',start_stream_id='1',autoplay_start=False)
 portals.save_all([portal]);data=Path(addon_data_dir());(data/'artwork_config_v1.json').write_text(json.dumps(dict(version=1,mode='internal',strategy='demand',target='',profile='1'*32)))
 art=data/'media_art_v1';art.mkdir(exist_ok=True)
 for kind in ('vod','series'):
  rows=[]
  for i in range(24):
   uri='https://provider.example.test/'+kind+'/'+str(i)+'.png'
   item=dict(name='Provider '+kind+' '+str(i),stream_id=str(i),series_id=str(i),category_id='a',added=int(time.time())-i,cover=uri,stream_icon=uri,plot='Synthetic provider metadata',year='2026')
   rows.append(item);base=(40,70,120) if kind=='vod' else (100,50,20);image=Image.new('RGB',(120,180),tuple((v+i*step)%240 for v,step in zip(base,(19,31,13))));ImageDraw.Draw(image).text((15,80),kind+' '+str(i),fill='white');image.save(art/(hashlib.sha256(uri.encode()).hexdigest()+'.img'),format='PNG')
  replace_catalog(portal['id'],kind,rows,[dict(category_id='a',category_name='Synthetic group')])
 li=xbmcgui.ListItem('Seeded');xbmcplugin.addDirectoryItem(handle,'fixture',li,False);xbmcplugin.endOfDirectory(handle)

else:
 import importlib.util
 spec=importlib.util.spec_from_file_location('real_xcmate_default59',root/'default.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.run()

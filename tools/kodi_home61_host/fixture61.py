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
 from guide_store import import_cache
 from programme_events46 import load
 from programme_urls55 import resolve
 import media_sources43
 stations=[];events={};now=int(time.time())
 for i in range(88):
  uri='https://provider.example.test/logo/'+str(i)+'.png'
  stations.append(dict(stream_id=str(i),name='Station '+str(i),category_id='a',epg_channel_id='xml'+str(i),stream_icon=uri))
  Image.new('RGB',(120,60),((20+i*17)%230,(90+i*23)%230,(150+i*13)%230)).save(art/(hashlib.sha256(uri.encode()).hexdigest()+'.img'),format='PNG')
  if i<87:events['xml'+str(i)]=[dict(name='Synthetic film '+str(i),title='Synthetic film '+str(i),channel='xml'+str(i),descr='Exact local description '+str(i),category='Spielfilm',year=2024,start_timestamp=now-600,stop_timestamp=now+1200),dict(name='Next '+str(i),channel='xml'+str(i),descr='Next event',start_timestamp=now+1200,stop_timestamp=now+2400)]
 replace_catalog(portal['id'],'live',stations,[dict(category_id='a',category_name='Synthetic start group')])
 # No EPG or token for the P0 test.
 addon=xbmcaddon.Addon();addon.setSetting('programme_tmdb46','false');addon.setSetting('tmdb_research43','false');addon.setSetting('tmdb_read_token43','');addon.setSetting('programme_helper57','false');addon.setSetting('programme_catalog57','false')
 li=xbmcgui.ListItem('Seeded');xbmcplugin.addDirectoryItem(handle,'fixture',li,False);xbmcplugin.endOfDirectory(handle)

else:
 import widget_manager50,traceback
 original_error=widget_manager50.error
 def fixture_error(exc):
  Path('/root/manager61-error.txt').write_text(traceback.format_exc())
  return original_error(exc)
 widget_manager50.error=fixture_error
 import programme_events46
 original_describe60=programme_events46.describe
 def diagnostic_describe60(*a,**kw):
  value=original_describe60(*a,**kw)
  if value.get('sid') in ('0','1'):
   from programme_art46 import fingerprint
   Path('/root/read60-'+value['sid']+'.json').write_text(json.dumps(dict(event=value,fingerprint=fingerprint(value))))
  return value
 programme_events46.describe=diagnostic_describe60
 import media_sources43
 def no_gui_metadata(*a,**kw):raise AssertionError('DIRECTORY_METADATA_NETWORK')
 media_sources43.get=no_gui_metadata
 import importlib.util
 spec=importlib.util.spec_from_file_location('real_xcmate_default59',root/'default.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.run()

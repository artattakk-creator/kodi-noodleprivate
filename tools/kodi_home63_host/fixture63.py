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
  stations.append(dict(stream_id=str(i),name='Station '+str(i),category_id='a',epg_channel_id='xml'+str(i),stream_icon=uri if i<87 else ''))
  Image.new('RGB',(120,60),((20+i*17)%230,(90+i*23)%230,(150+i*13)%230)).save(art/(hashlib.sha256(uri.encode()).hexdigest()+'.img'),format='PNG')
  if i<87:events['xml'+str(i)]=[dict(name='Synthetic film '+str(i),title='Synthetic film '+str(i),channel='xml'+str(i),descr='Exact local description '+str(i),category='Spielfilm',year=2024,start_timestamp=now-600,stop_timestamp=now+1200),dict(name='Next '+str(i),channel='xml'+str(i),descr='Next event',start_timestamp=now+1200,stop_timestamp=now+2400)]
 replace_catalog(portal['id'],'live',stations,[dict(category_id='a',category_name='Synthetic start group')]+[dict(category_id='unused'+str(i),category_name='Unused group '+str(i)) for i in range(802)])
 Path('/root/stress63.json').write_text(json.dumps(dict(groups=803,stations=len(stations))))
 import_cache(portal['id'],events,'synthetic-home60',now=now,trusted_feed=True)
 addon=xbmcaddon.Addon();addon.setSetting('programme_tmdb46','true');addon.setSetting('tmdb_research43','true');addon.setSetting('tmdb_read_token43','SYNTHETIC_FIXTURE_NOT_A_TOKEN');addon.setSetting('programme_helper57','false');addon.setSetting('programme_catalog57','false')
 import io
 for i in (0,1):
  event=load(portal,dict(stations[i],sid=str(i)));event.update(genre='Spielfilm',year=2024)
  png=io.BytesIO();Image.new('RGB',(160,90),(20,80,130) if i==0 else (130,50,30)).save(png,'PNG')
  replies=iter([dict(total_pages=1,total_results=1,results=[dict(id=100+i,title=event['title'],release_date='2024-01-01')]),dict(id=100+i,title=event['title'],release_date='2024-01-01',backdrop_path='/epg'+str(i)+'.png'),png.getvalue()])
  original=media_sources43.get
  try:
   media_sources43.get=lambda *a,**kw:next(replies)
   value=resolve(event,allow_lookup=True)
   Path('/root/seed60-'+str(i)+'.json').write_text(json.dumps(dict(event=event,art=value)))
   assert value['code']=='READY' and Path(value['image']).is_file(),value.get('code')
  finally:media_sources43.get=original
 li=xbmcgui.ListItem('Seeded');xbmcplugin.addDirectoryItem(handle,'fixture',li,False);xbmcplugin.endOfDirectory(handle)

else:
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
 spec=importlib.util.spec_from_file_location('real_xcmate_default59',root/'default.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 try:module.run()
 finally:
  if p.get('action')==['widget_skin50']:Path('/root/layout63-invocation-finished').write_text('done')

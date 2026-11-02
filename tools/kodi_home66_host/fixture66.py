"""Synthetic provider rows; delegates all regular invocations to real default.py."""
import os,sys,json,time,hashlib
from pathlib import Path
from urllib.parse import parse_qs
import xbmc,xbmcgui,xbmcplugin,xbmcaddon
def check64(condition,detail='NATIVE_FIXTURE64_CONTRACT'):
 if not condition:raise RuntimeError(str(detail))
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
 records64=[]
 for kind in ('vod','series'):
  rows=[]
  for i in range(24):
   uri='https://provider.example.test/'+kind+'/'+str(i)+'.png'
   item=dict(name='Provider '+kind+' '+str(i),stream_id=str(i),series_id=str(i),category_id='a',added=int(time.time())-i,cover=uri,stream_icon=uri,plot='Synthetic provider metadata',year='2026')
   rows.append(item);base=(40,70,120) if kind=='vod' else (100,50,20);image=Image.new('RGB',(120,180),tuple((v+i*step)%240 for v,step in zip(base,(19,31,13))));ImageDraw.Draw(image).text((15,80),kind+' '+str(i),fill='white');destination64=art/(hashlib.sha256(uri.encode()).hexdigest()+'.img') if kind=='vod' else data/'series66'/('poster-'+str(i)+'.png');destination64.parent.mkdir(exist_ok=True);image.save(destination64,format='PNG')
   if kind=='series':records64.append((str(i),'poster',hashlib.sha256(uri.encode()).hexdigest(),dict(uri=str(destination64),mode='local',code='LOCAL_HEADER_VALID',until=time.time()+86400)))
  replace_catalog(portal['id'],kind,rows,[dict(category_id='a',category_name='Synthetic group')])
 from programme_assets47 import _store
 check64(_store(portal['id'],'series',records64),'SERIES64_STORE_FAILED')
 from programme_assets47 import read_many
 from widget_data41 import snapshot
 def check_series66(stage):
  rows,code=snapshot(portal,'series');refs=read_many(portal['id'],'series',rows,provider_only=True)
  Path('/root/series66-'+stage+'.json').write_text(json.dumps(dict(stage=stage,rows=len(rows),refs=len(refs),code=code,sids=[r['sid'] for r in rows],sources=[r.get('cover','') for r in rows])))
  check64(len(rows)==24 and len(refs)==24,(stage,code,len(rows),len(refs)))
 check_series66('stored')
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
 events['xml1'][0]['name']=events['xml1'][0]['title']='Synthetic long programme title with enough words for the two-line Hero layout'
 replace_catalog(portal['id'],'live',stations,[dict(category_id='a',category_name='Synthetic start group')]+[dict(category_id='unused'+str(i),category_name='Unused group '+str(i)) for i in range(802)])
 import sqlite3,library_index
 db=sqlite3.connect(library_index.path());groups63=db.execute("SELECT count(*) FROM groups WHERE pid=? AND kind='live'",(portal['id'],)).fetchone()[0];db.close();check64(groups63==803,'GROUP64_COUNT')
 Path('/root/stress66.json').write_text(json.dumps(dict(groups=groups63,stations=len(stations))))
 events['xml2'][0].update(name='MacGyver',title='MacGyver',category='Krimiserie',year=2016)
 import_cache(portal['id'],events,'synthetic-home60',now=now,trusted_feed=True)
 addon=xbmcaddon.Addon();addon.setSetting('programme_art_local69','true');addon.setSetting('programme_tmdb46','true');addon.setSetting('tmdb_research43','true');addon.setSetting('tmdb_read_token43','SYNTHETIC_FIXTURE_NOT_A_TOKEN');addon.setSetting('programme_helper57','false');addon.setSetting('programme_catalog57','false')
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
   check64(value['code']=='READY' and Path(value['image']).is_file(),value.get('code'))
  finally:media_sources43.get=original
 # Distinct synthetic TV search/details/image chain, no episode IDs invented.
 event=load(portal,dict(stations[2],sid='2'));event.update(genre='Krimiserie',year=2016)
 png=io.BytesIO();Image.new('RGB',(160,90),(40,120,160)).save(png,'PNG')
 replies=iter([dict(total_pages=1,total_results=1,results=[dict(id=6602,name='MacGyver',first_air_date='2016-01-01')]),dict(id=6602,name='MacGyver',first_air_date='2016-01-01',backdrop_path='/tv66.png'),png.getvalue()])
 original=media_sources43.get
 try:
  media_sources43.get=lambda *a,**kw:next(replies)
  value=resolve(event,allow_lookup=True,local_image63=True)
  check64(value['code']=='READY' and value['source']=='tmdb_series' and value['image_scope57']=='series_fallback','TV66_LOCAL_CHAIN')
  Path('/root/art66.json').write_text(json.dumps(dict(key=event['key'],image=value['image'],sha256=value['sha256'],source=value['source'],scope=value['image_scope57'])))
 finally:media_sources43.get=original
 check_series66('after-guide')
 li=xbmcgui.ListItem('Seeded');xbmcplugin.addDirectoryItem(handle,'fixture',li,False);xbmcplugin.endOfDirectory(handle)

elif p.get('fixture66'):
 from PIL import Image,ImageDraw
 kind=p['fixture66'][0];folder=root/'foreign66';folder.mkdir(exist_ok=True)
 titles=('HOPE','Coco','Lupin')
 for i in range(24):
  color=(40+(i%6)*30,60+(i//6)*40,{'poster':45,'music':135,'television':225}[kind])
  filename=folder/(kind+'-'+str(i)+'.png')
  size=(180,180) if kind=='music' else (120,180)
  image=Image.new('RGB',size,color);ImageDraw.Draw(image).text((12,65),titles[i%3],fill='white');image.save(filename)
  title=titles[i%3] if i<3 else 'Long title fixture with six bounded title lines and missing fanart '+str(i)
  item=xbmcgui.ListItem(title);item.setInfo('music' if kind=='music' else 'video',dict(title=title,**({'album':title,'artist':['Synthetic musician'],'comment':'Synthetic foreign description. '*40,'mediatype':'album'} if kind=='music' else {'plot':'Synthetic foreign description. '*40,'year':2026,'mediatype':'movie'})))
  item.setArt(dict(poster=str(filename),thumb=str(filename),icon=str(filename)))
  item.setProperty('Fixture66.Index',str(i));item.setProperty('Fixture66.Kind',kind)
  xbmcplugin.addDirectoryItem(handle,'plugin://plugin.video.xtreammate/?fixture66=play-disabled&id='+str(i),item,False)
 xbmcplugin.setContent(handle,'albums' if kind=='music' else 'movies');xbmcplugin.endOfDirectory(handle)

else:
 import programme_assets47
 original_assets64=programme_assets47.read_many
 def diagnose_assets64(pid,kind,rows,**kwargs):
  started=time.monotonic();value=original_assets64(pid,kind,rows,**kwargs)
  if kind=='series':
   import programme_index46
   db=programme_index46.connect(False)
   raw=list(db.execute("SELECT sid,fingerprint,data,expires FROM asset_refs47 WHERE pid=? AND kind='series'",(str(pid),))) if db is not None else []
   if db is not None:db.close()
   first=rows[0] if rows else {}
   Path('/root/series66-route.json').write_text(json.dumps(dict(rows=len(rows),ready=len(value),raw=len(raw),first=first,source=programme_assets47.sources(first,provider_only=True),record=raw[0] if raw else None,ms=round((time.monotonic()-started)*1000,2))))
  return value
 programme_assets47.read_many=diagnose_assets64
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
  if p.get('action')==['widget_skin50']:Path('/root/layout66-invocation-finished').write_text('done')

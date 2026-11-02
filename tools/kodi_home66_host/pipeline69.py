"""Uncached URL-only production queue + real TLS/Kodi pixels under DB reserve."""
import importlib,io,json,threading,time
from pathlib import Path
from unittest import mock
import xbmc,xbmcaddon,xbmcgui
from PIL import Image,UnidentifiedImageError
import programme_urls55,programme_requests68 as broker,media_sources43,hero_epg63,portals
from programme_events46 import load
from programme_preview67 import Preview
from programme_window46 import ProgrammeWindow46
from programme_index46 import path as dbpath
from programme_writes69 import record
from import_budget import ReserveBlocked
from utils import addon_data_dir
programme_urls55.shutdown()
if programme_urls55._thread:programme_urls55._thread.join(timeout=2)
importlib.reload(programme_urls55)
addon=xbmcaddon.Addon('plugin.video.xtreammate');addon.setSetting('programme_art_local69','false')
portal=portals.get_by_id('fixture59');home=xbmcgui.Window(10000);results=[]
def files():return sorted(str(p.relative_to(addon_data_dir())) for p in Path(addon_data_dir()).rglob('*') if p.is_file() and 'programme_images46' in p.parts)
before=files()
def capture(name,points,color,pump):
 for attempt in range(50):
  pump();xbmc.sleep(100);path=Path('/root/'+name+'-last.png')
  xbmc.executebuiltin('TakeScreenshot('+str(path)+')',wait=False);xbmc.sleep(250)
  try:
   raw=path.read_bytes()
   with Image.open(io.BytesIO(raw)) as source:source.load();rgb=source.convert('RGB')
   if all(max(abs(a-b) for a,b in zip(rgb.getpixel(point),color))<=8 for point in points):
    Path('/root/'+name+'.png').write_bytes(raw);return
  except (OSError,UnidentifiedImageError):pass
 raise RuntimeError('URL69_NATIVE_PIXELS '+name)
for sid,format_,color in (('5','PNG',(25,145,100)),('6','JPEG',(145,70,120))):
 holder={};calls=[];finished=threading.Event();preview=Preview(home,(1240,50,480,270));started=time.monotonic()
 def synthetic(uri,**kw):
  if uri.startswith('https://image.tmdb.org/'):raise AssertionError('NO_IMAGE_ARCHIVE69')
  event=holder['event']
  if '/search/' in uri:
   calls.append('SYNTHETIC_OWN_TOKEN_SEARCH')
   return dict(total_pages=1,total_results=1,results=[dict(id=6900+int(sid),title=event['title'],name=event['title'],release_date='2024-01-01',first_air_date='2024-01-01')])
  calls.append('SYNTHETIC_OWN_TOKEN_DETAILS')
  return dict(id=6900+int(sid),title=event['title'],name=event['title'],release_date='2024-01-01',first_air_date='2024-01-01',backdrop_path='/url69-'+sid+'.jpg')
 def worker():
  try:
   event=load(portal,dict(sid=sid,name='Station '+sid,epg_channel_id='xml'+sid));holder['event']=event
   record(dbpath(),ReserveBlocked(16*1024*1024,32*1024*1024,65536))
   # Only synthetic image DNS is replaced in this isolated test. TLS/SNI and
   # certificate validation, image-header probe and Kodi Curl are production.
   with mock.patch('download_redirect.addresses',return_value=['127.0.0.1']),mock.patch('media_sources43.get',side_effect=synthetic):
    broker.request(event,priority=True);deadline=time.monotonic()+20
    while time.monotonic()<deadline:
     broker.drain();value=broker.result(event)
     if value.get('status68')=='IMAGE_URL_READY_RAM':holder['art']=value;holder['ready_ms']=round((time.monotonic()-started)*1000);break
     xbmc.sleep(25)
    else:raise RuntimeError('URL69_NOT_READY '+json.dumps(broker.result(event)))
    initial=len(calls)
    for _ in range(18):broker.request(event,priority=True);broker.drain();xbmc.sleep(10)
    if len(calls)!=initial:raise RuntimeError('URL69_REPEATED_MATCHING')
   art=holder['art']
   if art.get('storage_code69')!='SAFE_RESERVE_BLOCKED' or not art['image'].startswith('https://image.tmdb.org/'):raise RuntimeError('URL69_STORAGE_OR_IMAGE')
  except Exception:
   import traceback
   holder['error']=traceback.format_exc()
  finally:finished.set()
 task=threading.Thread(target=worker,daemon=True);task.start()
 while not finished.is_set() and time.monotonic()-started<25:xbmc.sleep(50)
 if not finished.is_set() or holder.get('error'):raise RuntimeError(holder.get('error','URL69_WORKER_TIMEOUT'))
 event=holder['event'];art=holder['art']
 # .70 regression: the valid RAM-only URL must remain consumable after the
 # old five-minute envelope cutoff. Age only this synthetic broker record.
 marker_key=broker.PREFIX+'status.'+str(int(broker.identity(event)[:8],16)%broker.SLOTS)
 envelope=json.loads(home.getProperty(marker_key));envelope['at']-=360;home.setProperty(marker_key,json.dumps(envelope))
 if broker.result(event).get('image')!=art['image']:raise RuntimeError('STATUS70_EXPIRED_BEFORE_ART_TTL')
 capture('pipeline69-preview-'+sid,[(1260,70)],color,lambda:preview.render(portal,dict(sid=sid,name='Station '+sid,epg_channel_id='xml'+sid),event))
 if not preview.logo.isVisible():raise RuntimeError('URL69_TMDB_LOGO')
 preview.hide();home.removeControls(list(preview.controls))
 home.setFocusId(2510);home.getControl(2510).selectItem(int(sid));xbmc.sleep(700)
 stop=threading.Event()
 def intake():
  while not stop.is_set():broker.drain(cancel=stop.is_set);xbmc.sleep(50)
 intake_task=threading.Thread(target=intake,daemon=True);intake_task.start()
 def pump_home():hero_epg63._next=0;hero_epg63.poll()
 try:capture('pipeline69-home-'+sid,[(1450,180),(1700,180),(1880,180)],color,pump_home)
 finally:stop.set();intake_task.join(timeout=1)
 window=ProgrammeWindow46('XCMateProgramme46.xml',addon.getAddonInfo('path'),'Default','720p');window.configure(portal,dict(sid=sid,name='Station '+sid,epg_channel_id='xml'+sid));window.show()
 try:capture('pipeline69-detail-'+sid,[(500,400)],color,window.pump)
 finally:window.close()
 results.append(dict(sid=sid,format=format_,source=art['source'],code=art['code'],storage=art['storage69'],reason=art['storage_code69'],matching_calls=calls,repeated_requests=18,lookup_repeat=0,status_age_seconds=360,status_lifetime70='PASS',ready_ms=holder['ready_ms'],total_with_captures_ms=round((time.monotonic()-started)*1000),preview_pixels='PASS',home_pixels='PASS',detail_pixels='PASS',android='NOT_TESTED'))
if before!=files():raise RuntimeError('URL69_ADDED_ARCHIVE_FILE')
requests=[json.loads(s) for s in Path('/root/tls69-requests.jsonl').read_text().splitlines()]
if not requests or any(r['authorization'] or r['cookie'] for r in requests):raise RuntimeError('URL69_CREDENTIAL_LEAK')
programme_urls55.shutdown()
if programme_urls55._thread:programme_urls55._thread.join(timeout=2)
Path('/root/pipeline69.json').write_text(json.dumps(dict(cases=results,tls='real verified TLS/SNI using disposable synthetic CA/origin',api='synthetic own-token responses; production matching',private_live_tmdb_api='NOT_TESTED',no_xcmate_image_archive='PASS',no_auth_on_image_origin='PASS',android='NOT_TESTED')))

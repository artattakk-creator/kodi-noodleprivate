"""Uncached native .68 producer test; synthetic API transport, real Kodi pixels."""
import io,json,threading,time
from pathlib import Path
from unittest import mock
import xbmc,xbmcaddon,xbmcgui
from PIL import Image,UnidentifiedImageError
import programme_requests68 as broker
import programme_urls55,media_sources43,hero_epg63,portals
from programme_events46 import load
from programme_preview67 import Preview
from programme_window46 import ProgrammeWindow46
portal=portals.get_by_id('fixture59')
home=xbmcgui.Window(10000);results=[]

def capture(name,points,color,pump):
 for attempt in range(40):
  pump();xbmc.sleep(100)
  path=Path('/root/'+name+'-last.png')
  xbmc.executebuiltin('TakeScreenshot('+str(path)+')',wait=False);xbmc.sleep(250)
  try:
   raw=path.read_bytes()
   with Image.open(io.BytesIO(raw)) as source:source.load();rgb=source.convert('RGB')
   if all(max(abs(a-b) for a,b in zip(rgb.getpixel(point),color))<=8 for point in points):
    Path('/root/'+name+'.png').write_bytes(raw);return
  except (OSError,UnidentifiedImageError):pass
 raise RuntimeError('PIPELINE68_NATIVE_PIXELS '+name)

for sid,format68,color in (('3','PNG',(120,35,80)),('4','JPEG',(75,130,25))):
 holder={};calls=[];finished=threading.Event();preview=Preview(home,(1240,50,480,270))
 def worker():
  try:
   event=load(portal,dict(sid=sid,name='Station '+sid,epg_channel_id='xml'+sid))
   from programme_art46 import cached
   prior=cached(event)
   if prior.get('source')!='placeholder':raise RuntimeError('PIPELINE68_MUST_START_UNCACHED')
   holder['event']=event
   png=io.BytesIO();Image.new('RGB',(160,90),color).save(png,format68);image=png.getvalue()
   def synthetic(uri,**kw):
    if uri.startswith('https://image.tmdb.org/'):
     calls.append('IMAGE_BYTES');return image
    if '/search/' in uri:
     calls.append('TOKEN_SEARCH')
     return dict(total_pages=1,total_results=1,results=[dict(id=6800+int(sid),title=event['title'],name=event['title'],release_date='2024-01-01',first_air_date='2024-01-01')])
    calls.append('TOKEN_DETAILS')
    return dict(id=6800+int(sid),title=event['title'],name=event['title'],release_date='2024-01-01',first_air_date='2024-01-01',backdrop_path='/pipeline68-'+sid+'.jpg')
   with mock.patch('media_sources43.get',side_effect=synthetic):
    broker.request(event,priority=True)
    deadline=time.monotonic()+20
    while time.monotonic()<deadline:
     broker.drain()
     value=broker.result(event)
     if value.get('status68')=='LOCAL_IMAGE_READY':
      holder['art']=value;break
     xbmc.sleep(25)
    else:raise RuntimeError('PIPELINE68_NO_LOCAL_IMAGE '+json.dumps(broker.result(event)))
   if calls.count('TOKEN_SEARCH')<1 or calls.count('TOKEN_DETAILS')<1 or calls.count('IMAGE_BYTES')!=1:raise RuntimeError('PIPELINE68_INCOMPLETE_TRANSPORT')
  except Exception:
   import traceback
   holder['error']=traceback.format_exc()
  finally:finished.set()
 thread=threading.Thread(target=worker,name='XCMate-native-pipeline68',daemon=True);thread.start()
 deadline=time.monotonic()+25
 while not finished.is_set() and time.monotonic()<deadline:xbmc.sleep(50)
 if not finished.is_set() or holder.get('error'):raise RuntimeError(holder.get('error','PIPELINE68_WORKER_TIMEOUT'))
 event=holder['event'];art=holder['art']
 if not Path(art['image']).is_file():raise RuntimeError('PIPELINE68_LOCAL_FILE_MISSING')
 # Shared production Guide/Mini renderer reads the file produced above.
 def pump_preview():
  preview.render(portal,dict(sid=sid,name='Station '+sid,epg_channel_id='xml'+sid),event)
 capture('pipeline68-preview-'+sid,[(1260,70)],color,pump_preview)
 if not preview.logo.isVisible():raise RuntimeError('PIPELINE68_TMDB_LOGO_MISSING')
 preview.hide();home.removeControls(list(preview.controls))
 # Home focus reload is a worker, its GUI pump stays property/RAM-only.
 home.setFocusId(2510);home.getControl(2510).selectItem(int(sid));xbmc.sleep(700)
 for _ in range(5):hero_epg63._next=0;hero_epg63.poll();xbmc.sleep(50)
 intake_stop=threading.Event()
 def intake():
  while not intake_stop.is_set():
   broker.drain(cancel=intake_stop.is_set);xbmc.sleep(50)
 task=threading.Thread(target=intake,daemon=True);task.start()
 def pump_home():hero_epg63._next=0;hero_epg63.poll()
 try:
  with mock.patch('hero_epg63.prepare',side_effect=AssertionError('HOME68_MUST_NOT_WAIT_FOR_BULK_PREPARE')):
   capture('pipeline68-home-'+sid,[(1450,180),(1700,180),(1880,180)],color,pump_home)
 finally:intake_stop.set();task.join(timeout=1)
 window=ProgrammeWindow46('XCMateProgramme46.xml',xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path'),'Default','720p')
 window.configure(portal,dict(sid=sid,name='Station '+sid,epg_channel_id='xml'+sid));window.show()
 try:
  capture('pipeline68-detail-'+sid,[(500,400)],color,window.pump)
  if not window.event or window.event['key']!=event['key'] or not window.getControl(130).isVisible():raise RuntimeError('PIPELINE68_DETAIL_IDENTITY_OR_LOGO')
 finally:window.close()
 results.append(dict(sid=sid,format=format68,initial='CACHE_MISS',transport=calls,status='LOCAL_IMAGE_READY',same_event=True,sha256=art['sha256'],preview_pixels='PASS',home_pixels='PASS',detail_pixels='PASS',tmdb_logo='VISIBLE',android='NOT_TESTED'))
programme_urls55.shutdown()
if programme_urls55._thread:programme_urls55._thread.join(timeout=2)
Path('/root/pipeline68.json').write_text(json.dumps(dict(cases=results,transport='synthetic credentialless API responses; real production matching/queue/cache',gui='native Kodi 21.2 Linux / BINGIE 2.2.3',android='NOT_TESTED')))

"""Real elapsed native Home soak; synthetic catalogue, production workers."""
import contextlib,importlib,json,os,threading,time,hashlib
from unittest import mock
from pathlib import Path
import xbmc,xbmcgui
from PIL import Image
import portals,widget_data41,widget_refresh45,widget_live47,programme_assets47,local_epg,epg_refresh74,hero_epg63
from epg_sources import configuration
seconds=int(os.environ.get('XCMATE_IDLE74','0'))
if seconds:
 portal=portals.get_by_id('fixture59');home=xbmcgui.Window(10000);stop=threading.Event();errors=[];ticks=[];samples=[]
 started=time.monotonic();initial={};max_rss=0
 import programme_urls55 as urls,media_sources43,programme_requests68 as requests
 importlib.reload(urls)
 transport=mock.patch('media_sources43.get',side_effect=media_sources43.SourceError('TIMEOUT'));transport.start()
 def background():
  while not stop.is_set():
   tick=dict(at=round(time.monotonic()-started,2),counts={})
   try:
    for kind in ('live','vod','series'):
     # A read-budget failure is not an authoritative empty catalogue.
     inject=len(ticks)%6==5
     from library_index import IndexReadError
     failure=IndexReadError('BUDGET');failure.code='BUDGET'
     with mock.patch('library_index.Reader.state',side_effect=failure) if inject else contextlib.nullcontext():
      rows,code=widget_data41.snapshot(portal,kind,background=True)
     if inject:tick['fault']='SQLITE_READ_BUDGET'
     if not rows:raise RuntimeError('EMPTY_'+kind+'_'+code)
     programme_assets47.prepare(portal,kind,rows[:24])
     if kind=='live':local_epg.now_next(portal['id'],rows[:16],configuration(portal['id'])['mappings'],display_only65=True)
     widget_live47.publish(portal,kind,rows,code)
     tick['counts'][kind]=len(rows)
    # Actual missing/stale handoff coalescing worker, no provider request.
    epg_refresh74.request(portal['id'],'86')
    from programme_events46 import load
    event=load(portal,dict(sid='86',name='Station 86',epg_channel_id='xml86'))
    urls.enqueue(event,allow_lookup=True,priority68=True);requests.drain()
    tick['artwork_code']=requests.result(event).get('code','PENDING')
    ticks.append(tick)
   except Exception as exc:errors.append(dict(at=tick['at'],type=type(exc).__name__))
   stop.wait(20)
 worker=threading.Thread(target=background,name='XCMate74-native-soak',daemon=True);worker.start()
 try:
  home.setFocusId(2510);home.getControl(2510).selectItem(0);xbmc.sleep(800)
  checkpoints=sorted(set([0,seconds]+[v for v in (900,1800,3600) if v<=seconds]));index=0
  while not xbmc.Monitor().abortRequested():
   elapsed=time.monotonic()-started
   hero_epg63.poll();widget_refresh45.poll()
   if elapsed>=checkpoints[index]:
    counts={str(i):xbmc.getInfoLabel('Container('+str(i)+').NumItems') for i in (2510,2520,2530)}
    if not initial:initial=counts
    if counts!=initial or counts['2510']!='88' or not all(int(v)>0 for v in counts.values()):raise RuntimeError('NATIVE_IDLE74_COUNTS '+repr(counts))
    bank=home.getProperty('XCMate.Hero63.Active');title=home.getProperty('XCMate.Hero63.'+bank+'.Title')
    if title!='Synthetic film 0':raise RuntimeError('NATIVE_IDLE74_NOW_LOST '+repr(title))
    if home.getFocusId()!=2510:raise RuntimeError('NATIVE_IDLE74_FOCUS_LOST')
    picture=Path('/root/idle74-'+str(checkpoints[index]//60)+'.png');xbmc.executebuiltin('TakeScreenshot('+str(picture)+')',wait=False);xbmc.sleep(500)
    with Image.open(picture) as image:
     native_size=image.size;rgb=image.convert('RGB').resize((1920,1080))
     if max(abs(a-b) for a,b in zip(rgb.getpixel((330,645)),(20,90,150)))>7:raise RuntimeError('NATIVE_IDLE74_LOGO_PIXELS')
    from epg_handoff63 import get
    rollover=get(portal['id'],'86')
    samples.append(dict(elapsed_seconds=round(elapsed,3),counts=counts,now=title,focus=home.getFocusId(),native_resolution=native_size,rollover_title=(rollover or {}).get('now'),image_sha256=hashlib.sha256(picture.read_bytes()).hexdigest()))
    Path('/root/idle74-progress.json').write_text(json.dumps(dict(elapsed_seconds=round(elapsed,3),samples=samples,worker_ticks=len(ticks),errors=errors)))
    index+=1
    if index==len(checkpoints):break
   xbmc.sleep(100)
  if errors:raise RuntimeError('NATIVE_IDLE74_WORKER_ERRORS '+repr(errors[:5]))
  result=dict(status='PASS',elapsed_seconds=round(time.monotonic()-started,3),requested_seconds=seconds,samples=samples,worker_ticks=ticks,background='production snapshot, assets, publication, local EPG refresh + GUI pumps; full service disabled in disposable harness',android='ANDROID_NOT_TESTED',clock='real monotonic; no fast-forward')
  Path('/root/idle74.json').write_text(json.dumps(result))
 finally:stop.set();worker.join(timeout=5);urls.shutdown();transport.stop()

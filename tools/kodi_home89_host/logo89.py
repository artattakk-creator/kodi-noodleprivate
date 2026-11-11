"""Real files/manifest/renderer; documented capacity injected, NOT Android."""
import json,time
from pathlib import Path

def run(portal,rows,pump,capture,cold,check,home):
 import logo_manifest86,logo_store89,station_logos88,art_storage82,xbmc
 original=art_storage82.capacity;before=logo_manifest86.read(portal,rows,with_fallback=False);calls=[]
 fetch=station_logos88.fetch
 def counted(*args,**kw):
  calls.append(1)
  if cold:raise AssertionError('UNCHANGED_LOGO_REQUESTED_AFTER_RESTART')
  return fetch(*args,**kw)
 def measured(path,*args,**kw):
  facts=original(path,*args,**kw)
  if str(path).endswith(('/tv_logos','/verified_posters89')):
   # Explicit same-volume synthetic receipt, not a real free-space claim.
   facts.update(free=228114432,total=4034297856,capacity82='SAME_VOLUME_VERIFIED',volume82='fixture89same',mount82='fuse')
  return facts
 art_storage82.capacity=measured;station_logos88.fetch=counted
 try:
  if cold:check(len(before)==88,('LOGO89_COLD_MANIFEST_MISSING',len(before)))
  for tick in range(70):
   station_logos88.prepare(portal,rows)
   refs=logo_manifest86.read(portal,rows,with_fallback=False)
   if len(refs)==88:break
   pump()
  check(len(refs)==88,('LOGO89_PERSISTENT_LOGOS_MISSING',len(refs)))
  logo_store89._verified.clear();refs=logo_manifest86.read(portal,rows,with_fallback=False)
  check(len(refs)==88,'LOGO89_COLD_HASH_READBACK_FAILED')
  root=Path(logo_manifest86.location()[0].root);manifest=Path(logo_manifest86.location()[1]);records=json.loads(manifest.read_bytes())['records']
  check(all(v.get('storage89')=='PERSISTED_LOGO' for v in records.values()),'LOGO89_FALSE_DURABLE_RECORD')
  check(sum(p.stat().st_size for p in root.iterdir() if p.is_file())<=logo_store89.QUOTA+logo_store89.MAX_MANIFEST,'LOGO89_QUOTA_EXCEEDED')
  station_logos88.prepare(portal,rows)
  after=len(calls);station_logos88.prepare(portal,rows);check(len(calls)==after,'LOGO89_WARM_REPEAT_HTTP')
  # The inherited .88 fixture explicitly stopped its data lane before this
  # additional phase. Exercise a new bounded publication on a fixture worker
  # using the production publisher, never disk/SQL on Kodi's input thread.
  import threading,widget_runtime79,widget_hooks45
  failures=[];poster_refs89={};poster_rows89={}
  def publish89():
   try:
    widget_runtime79._next=0;widget_runtime79.prepare([portal]);widget_hooks45._next=0;widget_hooks45.prepare()
    __import__('widget_live47').publish(portal,'live',rows)
    import poster_store89
    for kind89 in ('vod','series'):
     selected89=__import__('widget_data41').snapshot(portal,kind89,background=True)[0][:5];poster_rows89[kind89]=selected89
     for attempt89 in range(12):
      poster_store89.prepare(portal,kind89,selected89)
      found89=poster_store89.read(portal,kind89,selected89)
      if len(found89)==5 and all(v.get('poster') for v in found89.values()):break
     check(len(found89)==5 and all(v.get('poster') for v in found89.values()),('POSTER89_PERSISTENCE_MISSING',kind89,len(found89)))
     poster_refs89[kind89]=found89
     __import__('widget_refresh45').publish(portal,kind89,__import__('widget_data41').snapshot(portal,kind89,background=True)[0])
   except Exception as error:failures.append(type(error).__name__)
  lane=threading.Thread(target=publish89);lane.start();joined=time.monotonic()+45
  while lane.is_alive() and time.monotonic()<joined:pump();xbmc.sleep(50)
  lane.join(.1);check(not lane.is_alive() and not failures,('LOGO89_PUBLICATION_FAILED',failures))
  # The existing publisher/hook must deliver the own file to the real Kodi
  # DirectoryProvider. Do not replace the control or manually inject items.
  home.setFocusId(900);home.getControl(900).selectItem(0)
  for settle in range(160):
   pump();xbmc.sleep(50)
   if home.getProperty('ShowViewSubMenu')=='show' or home.getFocusId()==900:
    home.setFocusId(900);xbmc.executebuiltin('Action(Back)',wait=False);xbmc.sleep(100);continue
   break
  home.setFocusId(2510);home.getControl(2510).selectItem(0)
  until=time.monotonic()+90
  while time.monotonic()<until:
   pump();xbmc.sleep(100)
   uri=xbmc.getInfoLabel('Container(2510).ListItem.Art(poster)')
   if uri in refs.values():break
  check(uri in refs.values(),('LOGO89_RENDERER_NOT_USING_OWN_FILE',bool(uri)))
  home.setFocusId(2510);xbmc.sleep(250)
  picture,rgb=capture('visible84-logo89-'+('cold' if cold else 'warm'))
  pixels=sum(max(abs(a-b) for a,b in zip(p,(25,100,160)))<=12 for p in rgb.crop((270,640,470,715)).getdata())
  check(pixels>1500,('LOGO89_LOCAL_RAIL_PIXELS_MISSING',pixels))
  cover_cases89=[]
  from PIL import Image
  for kind89,cid89 in (('vod',2520),('series',2530)):
   home.setFocusId(cid89);seen89=set();until89=time.monotonic()+90
   while time.monotonic()<until89:
    home.setFocusId(cid89);home.getControl(cid89).selectItem(0);pump();xbmc.sleep(100)
    shown89=xbmc.getInfoLabel('ListItem.Art(poster)');sid89=xbmc.getInfoLabel('ListItem.Property(XCMate.MediaId)')
    if shown89==poster_refs89[kind89].get(sid89,{}).get('poster'):break
   check(shown89==poster_refs89[kind89].get(sid89,{}).get('poster'),('POSTER89_NATIVE_OWN_FILE_MISSING',kind89))
   for index89 in range(5):
    home.getControl(cid89).selectItem(index89)
    for settle89 in range(40):
     pump();xbmc.sleep(50)
     sid89=xbmc.getInfoLabel('ListItem.Property(XCMate.MediaId)');shown89=xbmc.getInfoLabel('ListItem.Art(poster)')
     if shown89==poster_refs89[kind89].get(sid89,{}).get('poster'):break
    check(shown89==poster_refs89[kind89].get(sid89,{}).get('poster'),('POSTER89_ITEM_NOT_LOCAL',kind89,index89));seen89.add(sid89)
   check(len(seen89)==5,('POSTER89_NOT_FIVE_DISTINCT_ITEMS',kind89,len(seen89)))
   picture89,frame89=capture('visible84-poster89-'+kind89+'-'+('cold' if cold else 'warm'))
   with Image.open(shown89) as own89:color89=own89.convert('RGB').getpixel((own89.width//2,own89.height//2))
   pixels89=sum(max(abs(a-b) for a,b in zip(p,color89))<=12 for p in frame89.crop((260,640,1890,1040)).getdata())
   check(pixels89>1500,('POSTER89_NATIVE_PIXELS_MISSING',kind89,pixels89));cover_cases89.append(dict(kind=kind89,distinct_local_items=len(seen89),pixels=pixels89,screenshot=picture89.name))
  result=dict(posters89=cover_cases89,status='PASS',records=len(records),own_references=len(refs),unique_files=len(set(refs.values())),request_count=len(calls),after_restart_no_repeated_downloads=not calls if cold else None,manifest_bytes=manifest.stat().st_size,own_bytes=sum(p.stat().st_size for p in root.iterdir() if p.is_file()),selected_free_injection=228114432,global_reserve=__import__('art_storage').reserve(),actual_native_list_file=True,rail_pixels=pixels,screenshot=picture.name,android='ANDROID_NOT_TESTED')
  print('LOGO89_RECEIPT '+json.dumps(result),flush=True);return result
 finally:art_storage82.capacity=original;station_logos88.fetch=fetch

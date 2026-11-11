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
  if str(path).endswith('/tv_logos'):
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
  # The existing publisher/hook must deliver the own file to the real Kodi
  # DirectoryProvider. Do not replace the control or manually inject items.
  home.setFocusId(900);home.getControl(900).selectItem(0)
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
  result=dict(status='PASS',records=len(records),own_references=len(refs),unique_files=len(set(refs.values())),request_count=len(calls),after_restart_no_repeated_downloads=not calls if cold else None,manifest_bytes=manifest.stat().st_size,own_bytes=sum(p.stat().st_size for p in root.iterdir() if p.is_file()),selected_free_injection=228114432,global_reserve=__import__('art_storage').reserve(),actual_native_list_file=True,rail_pixels=pixels,screenshot=picture.name,android='ANDROID_NOT_TESTED')
  print('LOGO89_RECEIPT '+json.dumps(result),flush=True);return result
 finally:art_storage82.capacity=original;station_logos88.fetch=fetch

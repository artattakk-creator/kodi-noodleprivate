"""Synthetic Linux Kodi .90: actual pixels/IR, never Android acceptance."""
import json,time,hashlib,threading
from pathlib import Path

def run(portal,rows,pump,capture,cold,check,home,early_logo):
 import xbmc,xbmcgui,epg_handoff63,epg_snapshot75,logo_manifest86,logo_store89,station_logos88,art_storage82
 from widget_inventory87 import collect,compare
 import xbmcvfs
 profile=Path(xbmcvfs.translatePath('special://profile/'));skin=Path(xbmcvfs.translatePath('special://skin/'))
 inventory=collect(profile,skin)
 refs=logo_manifest86.read(portal,rows,False);check(len(refs)==88,'START90_MANIFEST_NOT_COMPLETE')
 manifest=Path(logo_manifest86.location()[1]);before=hashlib.sha256(manifest.read_bytes()).hexdigest()
 count=[];oldfetch=station_logos88.fetch;oldcap=art_storage82.capacity
 def forbidden(*a,**kw):count.append(1);raise AssertionError('START90_DUPLICATE_HTTP')
 def measured(path,*a,**kw):
  facts=oldcap(path,*a,**kw)
  if str(path).endswith('/tv_logos'):facts.update(free=115*1024**2,total=4034297856,capacity82='SAME_VOLUME_VERIFIED',volume82='native90-synthetic',mount82='fuse')
  return facts
 try:
  art_storage82.capacity=measured;station_logos88.fetch=forbidden
  logo_manifest86._manifest90.clear();logo_store89._verified.clear()
  check(station_logos88.prepare(portal,rows)=='READY','START90_LOWSPACE_VALID_FILES_LOST')
  check(hashlib.sha256(manifest.read_bytes()).hexdigest()==before,'START90_DUPLICATE_COMMIT')
 finally:station_logos88.fetch=oldfetch;art_storage82.capacity=oldcap
 # Existing live fixture prepared actual local EPG; persist its valid events
 # through the production checkpoint, then verify cold reads without a player.
 import shutil,collections
 old_usage90=shutil.disk_usage
 def metadata_usage90(path):
  if str(path)==str(Path(epg_snapshot75._path(portal['id'])).parent):return collections.namedtuple('usage','total used free')(4034297856,4034297856-115*1024**2,115*1024**2)
  return old_usage90(path)
 metadata_usage90.fault84=True;shutil.disk_usage=metadata_usage90
 try:
  epg_snapshot75._due85.clear();written90=epg_snapshot75.checkpoint(portal['id'],rows[:5])
  check(written90 or Path(epg_snapshot75._path(portal['id'])).is_file(),'START90_EPG_CHECKPOINT_FAILED')
 finally:shutil.disk_usage=old_usage90
 epg=[epg_handoff63.get(portal['id'],str(row['sid'])) for row in rows[:5]]
 check(all(v and v.get('now') and v.get('next') for v in epg),'START90_NOW_NEXT_NOT_FIVE')
 if cold:check(early_logo['elapsed_ms']<=10000,('START90_COLD_FIRST_PIXELS_OVER_10S',early_logo['elapsed_ms']))
 # Native IR follows the restored foreign factory: no manual re-focus after
 # the starting row. This independently covers E rather than producer JSON.
 home.setFocusId(3540);xbmc.sleep(400)
 ir=[]
 for action in ('Down','Down','Up','Up'):
  previous=home.getFocusId();xbmc.executebuiltin('Action('+action+')',wait=False);xbmc.sleep(300)
  current=home.getFocusId();check(current!=previous,('START90_FOREIGN_IR_STUCK',action,current));ir.append([previous,current])
 groups90=None
 if not cold:
  from groups90 import run as group_run90
  groups90=group_run90(portal,pump,capture,check)
 from manual90 import run as manual_run90
 manual90=manual_run90(portal,rows,pump,capture,cold,check)
 # Continuous 15-minute Home run. Every focus is a real native ListItem;
 # photos remain measured pixels, not inferred from REFERENCE_READY.
 samples=[];started=time.monotonic();duration=0 if cold else 900
 interval=0
 home.setFocusId(2510);home.getControl(2510).selectItem(0)
 while time.monotonic()-started<duration:
  pump();elapsed=time.monotonic()-started
  if interval<20 and elapsed>=interval*40:
   cid=(2510,2520,2530)[interval%3];home.setFocusId(cid);home.getControl(cid).selectItem(interval%5);interval+=1
   check(xbmcgui.getCurrentWindowId()==10000 and home.getFocusId()==cid,('START90_HOME_FOCUS_LOST',cid,home.getFocusId()))
  if not samples or elapsed>=(450 if len(samples)==1 else 899):
   picture,rgb=capture('visible84-start90-'+('cold' if cold else str(len(samples))))
   pixels=sum(max(p)-min(p)>25 and max(p)>45 for p in rgb.crop((260,640,1890,1040)).getdata())
   check(pixels>1500,'START90_RAIL_PIXELS_EMPTY');samples.append(dict(seconds=round(elapsed,1),pixels=pixels,screenshot=picture.name))
  xbmc.sleep(200)
 check(cold or interval==20,'START90_FOCUS_CYCLE_COUNT')
 compare(profile,inventory)
 text=Path('/root/.kodi/temp/kodi.log').read_text(errors='replace')
 errors=sum('GUI86' in line and 'CALLBACK_FAILED' in line for line in text.splitlines())
 check(errors==0,('START90_CALLBACK_FAILED',errors))
 report=dict(manual90=manual90,groups90=groups90,status='PASS',android='ANDROID_NOT_TESTED',first_rail_pixels_ms=early_logo['elapsed_ms'],lowspace_injected_bytes=115*1024**2,global_reserve=__import__('art_storage').reserve(),persistent_logos=88,duplicate_http=len(count),duplicate_commits=0,now_next_ready=len(epg),home_seconds=round(time.monotonic()-started,1),focus_changes=interval,callback_failures=errors,foreign_ir=ir,pixel_samples=samples,protected_inventory=inventory['sha256'])
 Path('/root/startup90.json').write_text(json.dumps(report,indent=2));print('START90_NATIVE '+json.dumps(report),flush=True)
 return report

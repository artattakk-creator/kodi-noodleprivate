"""Same synthetic .89 provider, plus 58 actually persisted pre-start logos.

115 MiB is an explicit Python capacity injection, never physical ENOSPC or
Android proof. Real local HTTPS bytes, original safe URL and SHA persist paths.
"""
from pathlib import Path
base=Path('/base_fixture86.py').read_text(encoding='utf-8').replace("if __name__=='__main__':run()",'')
exec(compile(base,'/base_fixture86.py','exec'),globals())
install86=install

def install():
 install86()
 import art_storage82
 previous=art_storage82.capacity
 if getattr(previous,'native90',False):return
 def capacity90(path,*args,**kw):
  facts=previous(path,*args,**kw)
  if str(path).endswith('/tv_logos'):facts.update(free=115*1024**2,total=4034297856,capacity82='SAME_VOLUME_VERIFIED',volume82='native90-synthetic',mount82='fuse')
  return facts
 capacity90.native90=True;art_storage82.capacity=capacity90
seed86=seed

def seed():
 seed86();install()
 import time,json,logo_store89,station_logos88,station_logos87
 from portals import get_active
 from widget_group46 import snapshot
 portal=get_active()[0];rows=snapshot(portal);start=time.monotonic()
 for row in rows[:58]:logo_store89.persist(portal,row,station_logos88.fetch(portal,station_logos87.source(row),lambda:False))
 Path('/root/seed90.json').write_text(json.dumps(dict(own_logos_before_home=58,capacity_injected_bytes=115*1024**2,preparation_ms=int((time.monotonic()-start)*1000),android='ANDROID_NOT_TESTED')))
def observe_nav90():
 import xbmcgui,json
 from media_window import MediaView
 original=MediaView.pump
 if getattr(original,'observed90',False):return
 def observed(view):
  result=original(view);home=xbmcgui.Window(10000);sequence=home.getProperty('XCMate.Nav90.Sequence')
  if sequence.isdigit() and len(sequence)<=3:home.setProperty('XCMate.Nav86.State',json.dumps(dict(sequence=sequence,mode=view.mode,kind=view.kind,closed=view._closed,generation=view._generation,actions=len(getattr(view,'actions',[])),rows=len(view.rows),focus=view.getFocusId())))
  return result
 observed.observed90=True;MediaView.pump=observed
 action90=MediaView.onAction
 def observe_action90(view,action):
  before=view.mode;result=action90(view,action)
  print('NAV90_OBSERVE '+json.dumps(dict(action=action.getId(),before=before,after=view.mode,closed=view._closed,leaving=view._leaving,window=xbmcgui.getCurrentWindowId(),sequence=xbmcgui.Window(10000).getProperty('XCMate.Nav90.Sequence'))),flush=True)
  return result
 MediaView.onAction=observe_action90
original_run90=run
def run():
 import sys,json
 from urllib.parse import parse_qs
 args90=parse_qs(sys.argv[2].lstrip('?'))
 print('FIXTURE90_ROUTE '+json.dumps(dict(action=args90.get('action',[''])[0],sequence=args90.get('nav86',[''])[0])),flush=True)
 return original_run90()
if __name__=='__main__':run()

"""Real WindowDialog/IR, paged SQLite catalogue, own-tagged native video."""
import time,json,sqlite3
from pathlib import Path
from types import SimpleNamespace

def run(portal,pump,capture,check):
 import xbmc,xbmcgui,library_index
 from live_overlay import LiveNavigator
 groups=[dict(category_id=str(i),category_name='Native group '+str(i)) for i in range(20)]
 streams=[dict(stream_id=str(i*1000+j+1),category_id=str(i),name='Native station '+str(j)) for i in range(20) for j in range(137)]
 selected=dict(portal,id='navigation90',start_group_id='0',start_stream_id='1')
 # A separate synthetic portal key leaves every Home catalogue untouched.
 check(bool(library_index.Reader('navigation90').state('live')),'GROUP90_FIXTURE_CATALOGUE_NOT_SEEDED')
 client=SimpleNamespace(live_stream_url=lambda *a:'/root/navigation90.mp4',get_cached_catalog=lambda action:groups if action=='get_live_categories' else streams if action=='get_live_streams' else [],get_short_epg=lambda *a,**kw:[])
 nav=LiveNavigator(selected,'1',client)
 def until(predicate,reason,seconds=12):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   # Service is disabled in this native rig. Exercise its actual owner poll,
   # including own-standard-OSD recovery, rather than an inert dialog object.
   nav.tick()
   if predicate():return
   xbmc.sleep(30)
  try:capture('visible84-groups90-failure')
  except Exception:pass
  try:focus90=nav.getFocusId()
  except RuntimeError:focus90=-1
  raise RuntimeError((reason,nav.mode,nav.sid,nav._closed,xbmcgui.getCurrentWindowId(),xbmcgui.getCurrentWindowDialogId(),focus90))
 def native_sid90():
  try:return json.loads(xbmc.Player().getVideoInfoTag().getUniqueID('xcmate_live'))['sid']
  except (ValueError,RuntimeError,KeyError):return ''
 try:
  def complete90():
   nav.refresh_from_cache()
   return nav._catalog_ready and not getattr(nav,'_catalog_partial46',False)
  until(complete90,'GROUP90_CATALOGUE_NOT_READY')
  check(len(nav.channels)==2740,('GROUP90_CHANNELS_MISSING',len(nav.channels)))
  # Match the real service lifecycle: native video/fullscreen first, then
  # show its input owner. Showing a dialog on Home before Player.play lets
  # Kodi's later FullscreenVideo activation cover that dialog.
  nav._tune(nav.index.by_sid['1']);until(nav.owns_playback,'GROUP90_NATIVE_VIDEO_NOT_OWNED')
  until(lambda:xbmcgui.getCurrentWindowId()==12005,'GROUP90_NATIVE_FULLSCREEN_NOT_VISIBLE')
  nav.show()
  def active90():
   try:return xbmcgui.Window(xbmcgui.getCurrentWindowDialogId()).getProperty('XtreamMate.NavigatorIdentity')==nav._window_nonce
   except RuntimeError:return False
  until(active90,'GROUP90_NATIVE_INPUT_OWNER_NOT_ACTIVE')
  cases=[]
  # Keep an actual WAL writer open: the generation-pinned read path and
  # existing EPG worker must remain independently usable. This is a WAL
  # concurrency test, not a fabricated SQLITE_BUSY outcome.
  writer=sqlite3.connect(library_index.path());writer.execute('BEGIN IMMEDIATE')
  try:
   for group in range(20):
    for mode in ('channels','groups'):
     check(xbmc.Player().isPlayingVideo(),'GROUP90_NAVIGATION_STOPPED_PLAYER')
     xbmc.executebuiltin('Action(Left)',wait=False);until(lambda:nav.mode==mode,'GROUP90_LEFT_LEVEL_'+mode)
    index=next(i for i,r in enumerate(nav.rows) if r[0]==str(group));nav.control.selectItem(index);xbmc.executebuiltin('Action(Select)',wait=False)
    until(lambda:nav.mode=='channels' and nav.category_id==str(group),'GROUP90_WRONG_GROUP')
    check(len(nav.visible_channels)==137,('GROUP90_FALSE_EMPTY',group,len(nav.visible_channels)))
    xbmc.executebuiltin('Action(PageDown)',wait=False);until(lambda:nav._highlight['channels']==100,'GROUP90_PAGE_NOT_MOVED')
    for _ in range(36):xbmc.executebuiltin('Action(Down)',wait=False);xbmc.sleep(30)
    until(lambda:nav._highlight['channels']==136,'GROUP90_LAST_PAGE_WRONG_POSITION')
    expected=str(group*1000+137);xbmc.executebuiltin('Action(Select)',wait=False)
    # Ownership deliberately accepts the previous verified session during a
    # native tune. Require the new C++ item tag before declaring the zap done.
    until(lambda:nav.sid==expected and nav.mode=='hidden' and nav.owns_playback() and native_sid90()==expected,'GROUP90_WRONG_STATION')
    tag=json.loads(xbmc.Player().getVideoInfoTag().getUniqueID('xcmate_live'));check(tag['sid']==expected,'GROUP90_PLAYER_TAG_MISMATCH')
    cases.append(dict(group=group,total=137,last_index=136,correct_sid=True,native_video=True))
   screenshot,_=capture('visible84-groups90-native')
  finally:writer.rollback();writer.close()
 finally:
  nav.close();xbmc.executebuiltin('PlayerControl(Stop)',wait=False)
  for _ in range(150):
   if not xbmc.Player().isPlaying():break
   xbmc.sleep(50)
  check(not xbmc.Player().isPlaying(),'GROUP90_CLEANUP_STOP_NOT_RETURNED')
  xbmc.executebuiltin('ActivateWindow(Home)',wait=False);xbmc.sleep(500)
 report=dict(status='PASS',native_groups=20,native_station_changes=20,catalogue_rows=2740,page_size=100,wal_writer_held=True,cases=cases,screenshot=screenshot.name,android='ANDROID_NOT_TESTED')
 Path('/root/groups90.json').write_text(json.dumps(report,indent=2));print('GROUP90_NATIVE '+json.dumps(report),flush=True);return report

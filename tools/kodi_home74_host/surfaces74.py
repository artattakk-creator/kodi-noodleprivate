"""Actual MiniProgramme + actual GuideGrid XML surface, shared exact URL art."""
import io,json,time,types
from pathlib import Path
from PIL import Image,UnidentifiedImageError
import xbmc,xbmcgui,xbmcaddon
import portals,local_epg
from programme_events46 import load
portal=portals.get_by_id('fixture59');channel=dict(sid='5',name='Station 5',epg_channel_id='xml5');event=load(portal,channel)
color=(25,145,100);root=xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path')
def capture(name,points,pump):
 for _ in range(60):
  pump();xbmc.sleep(100);path=Path('/root/'+name+'-last.png');xbmc.executebuiltin('TakeScreenshot('+str(path)+')',wait=False);xbmc.sleep(400)
  try:
   raw=path.read_bytes()
   with Image.open(io.BytesIO(raw)) as image:image.load();rgb=image.convert('RGB').resize((1920,1080))
   if all(max(abs(a-b) for a,b in zip(rgb.getpixel(point),color))<=8 for point in points):Path('/root/'+name+'.png').write_bytes(raw);return
  except (OSError,UnidentifiedImageError):pass
 raise RuntimeError('NATIVE74_SURFACE_PIXELS '+name)
# Real production miniature programme column; a disposable owner replaces only
# the live player overlay shell, without starting/stopping any player.
from mini_epg import MiniProgramme
class MiniOwner74(xbmcgui.WindowDialog):pass
owner=MiniOwner74();owner._width=1280;owner._height=720;owner._media=root+'/resources/media';owner.portal=portal
owner._highlight={'channels':0};owner.visible_channels=[types.SimpleNamespace(name=channel['name'],extra={'stream_id':'5'})]
info=local_epg.now_next(portal['id'],[channel],{})['5'];owner._guide=types.SimpleNamespace(get=lambda sid:info)
owner.show();mini=MiniProgramme(owner)
try:
 mini.render();capture('mini74',[(1360,200)],mini.render)
 if not mini.preview67.image.isVisible():raise RuntimeError('NATIVE74_MINI_HIDDEN')
finally:mini.visible(False);owner.close()
# Real owner-dispatched guide, eight rows, actual enlarged 320x180 preview.
from guide_grid_window import GuideGridWindow
router=types.SimpleNamespace(_params={},_navigation_dispatch='synthetic74')
guide=GuideGridWindow('XCMateGuideGrid.xml',root,'Default','720p');guide.configure(router,dict(portal,start_stream_id='5'));guide.show()
try:
 deadline=time.monotonic()+15
 while time.monotonic()<deadline:
  if guide._init_error:raise guide._init_error
  if guide._native_initialized:guide.pump()
  if guide.rows and not guide._loading:break
  xbmc.Monitor().waitForAbort(.05)
 if not guide.rows or guide.rows[guide.row]['channel']['sid']!='5':raise RuntimeError('NATIVE74_GUIDE_SELECTION')
 def pump():guide.pump();guide._focus_cell()
 capture('guide74',[(1400,800),(1840,980)],pump)
 if not guide._preview67.image.isVisible():raise RuntimeError('NATIVE74_GUIDE_HIDDEN')
finally:guide.close()
Path('/root/surfaces74.json').write_text(json.dumps(dict(mini='PASS',guide='PASS',image='actual HTTPS synthetic PNG / verified Kodi pixels',guide_preview=[920,518,320,180],player_start=False,android='ANDROID_NOT_TESTED')))

"""Actual disposable Kodi restart, native reload and preserved Home receivers."""
from pathlib import Path
# Reuse the explicit runtime/pixel checks; no assertions stripped by Kodi -O.
source=Path('/work/gui66.py').read_text()
prefix=source.split("select(2510,0,'live')",1)[0]
exec(compile(prefix,'home75-post-helpers','exec'),globals())
select(2510,0,'live')
from widget_fast69 import prepare
prepare();xbmc.sleep(300)
select(2520,0,'vod');__import__('widget_fast69')._next=0;prepare();xbmc.sleep(300)
select(2530,0,'series')
for action,ident,kind in (('Up',2520,'vod'),('Up',2510,'live')):
    xbmc.executebuiltin('Action('+action+')',wait=False);xbmc.sleep(500)
    check(home.getFocusId()==ident,('POST75_DIRECTION',action,home.getFocusId()))
    select(ident,0,kind)
home.setProperty('XCMate.Widget45.Reload.live','post75-reload')
xbmc.sleep(1200);select(2510,0,'live')
xbmc.executebuiltin('ReloadSkin()',wait=False);xbmc.sleep(3500)
home=xbmcgui.Window(10000)
for _ in range(100):
    if xbmc.getInfoLabel('Container(2510).NumItems')=='88':break
    xbmc.sleep(100)
else:raise RuntimeError('POST75_RELOAD_NO_ROWS')
select(2510,0,'live')
counts=[int(xbmc.getInfoLabel('Container('+str(cid)+').NumItems')) for cid in (2510,2520,2530)]
check(counts==[88,24,24],counts)
Path('/root/post75.json').write_text(json.dumps(dict(status='PASS',actual_restart=True,cases=cases,counts=counts,android='ANDROID_NOT_TESTED'),indent=2))

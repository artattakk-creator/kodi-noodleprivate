"""Inspect the actual Home window, never open a replacement preview dialog."""
import json
import time
from pathlib import Path
import xbmc
import xbmcgui

home = xbmcgui.Window(10000)
for _ in range(200):
    if xbmcgui.getCurrentWindowId() == 10000 and xbmc.getInfoLabel('Container(2510).NumItems') == '88':
        break
    xbmc.sleep(100)
else:
    raise RuntimeError('BINGIE_HOME_LIVE_NOT_LOADED')
watermark=xbmcgui.ControlLabel(20,1045,1800,30,'Synthetic provider / Kodi Linux / BINGIE 2.2.3 / NOT Android',font='Reg18',textColor='FFFFFFFF')
home.addControl(watermark)
home.setFocusId(2510)
for index in (0, 1, 87):
    home.getControl(2510).selectItem(index)
    started = time.monotonic()
    from PIL import Image, UnidentifiedImageError
    expected = ((20 + index * 17) % 230, (90 + index * 23) % 230, (150 + index * 13) % 230)
    for attempt in range(10):
        # Kodi encodes asynchronously. Never let a later pending capture
        # overwrite the already verified evidence filename.
        capture = Path('/root/capture62-' + str(index) + '-' + str(attempt) + '.png')
        xbmc.executebuiltin('TakeScreenshot(' + str(capture) + ')', wait=False)
        for pending in range(40):
            if capture.exists() and capture.stat().st_size>1000:break
            xbmc.sleep(100)
        try:
            import io
            captured_bytes = capture.read_bytes()
            with Image.open(io.BytesIO(captured_bytes)) as frame:
                frame.load()
                rgb = frame.convert('RGB')
            text_pixels=sum(1 for r,g,b in rgb.crop((285,617,405,675)).getdata() if min(r,g,b)>170)
            logo_ready=max(abs(a-b) for a,b in zip(rgb.getpixel((330,645)), expected))<=5 if index<87 else text_pixels>20
            if logo_ready:
                Path('/root/home62-' + str(index) + '.png').write_bytes(captured_bytes)
                break
        except (OSError, UnidentifiedImageError):
            pass
    else:
        raise RuntimeError('NATIVE_HERO_LOGO_PIXELS_NOT_READY')
    props = {key: xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.' + key + ')') for key in ('ProgrammeChannel46', 'ProgrammeTitle46', 'ProgrammeNext46', 'ProgrammeDescription46', 'ProgrammeImage46', 'Home50')}
    props['items'] = xbmc.getInfoLabel('Container(2510).NumItems')
    props['visible'] = xbmc.getCondVisibility('Control.IsVisible(2510)')
    props['hero_condition'] = xbmc.getCondVisibility('Window.IsActive(Home) + ControlGroup(77777).HasFocus() + String.IsEqual(ListItem.Property(XCMate.Home50),true)')
    props['window'] = xbmcgui.getCurrentWindowId()
    props['focus'] = home.getFocusId()
    props['host_ready_ms'] = round((time.monotonic() - started) * 1000)
    Path('/root/home62-' + str(index) + '.json').write_text(json.dumps(props))
home.setProperty('Home61.Complete', 'true')

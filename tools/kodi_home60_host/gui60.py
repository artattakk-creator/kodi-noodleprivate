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
    # Wait for the existing source's native clock, if its initial bounded
    # local read returned a placeholder. No manual reset or URL change.
    for attempt in range(375):
        path = xbmc.getInfoLabel('Container(2510).ListItem.Property(XCMate.ProgrammeImage46)')
        if index == 87 or '/programme_images46/' in path:
            break
        xbmc.sleep(200)
    else:
        raise RuntimeError('LOCAL_HERO_NOT_PUBLISHED')
    from PIL import Image, UnidentifiedImageError
    expected = ((20 + index * 17) % 230, (90 + index * 23) % 230, (150 + index * 13) % 230)
    for attempt in range(30):
        # Kodi encodes asynchronously. Never let a later pending capture
        # overwrite the already verified evidence filename.
        capture = Path('/root/capture60-' + str(index) + '-' + str(attempt) + '.png')
        xbmc.executebuiltin('TakeScreenshot(' + str(capture) + ')', wait=False)
        xbmc.sleep(350)
        try:
            import io
            captured_bytes = capture.read_bytes()
            with Image.open(io.BytesIO(captured_bytes)) as frame:
                frame.load()
                rgb = frame.convert('RGB')
            hero = (20,80,130) if index == 0 else (130,50,30)
            if (max(abs(a-b) for a,b in zip(rgb.getpixel((330,645)), expected)) <= 5 and
                    (index == 87 or max(abs(a-b) for a,b in zip(rgb.getpixel((1700,180)), hero)) <= 5)):
                Path('/root/home60-' + str(index) + '.png').write_bytes(captured_bytes)
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
    Path('/root/home60-' + str(index) + '.json').write_text(json.dumps(props))
home.setProperty('Home60.Complete', 'true')

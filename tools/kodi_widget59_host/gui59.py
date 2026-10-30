from pathlib import Path
import xbmc,xbmcgui,json
root=Path(__file__).parent
class Window(xbmcgui.WindowXML):
 def onInit(self):pass
w=Window('NativeWidget59.xml',str(root),'Default','720p')
for i in range(200):
 if xbmcgui.getCurrentWindowDialogId() in (0,-1,9999) and not xbmc.getCondVisibility('System.HasActiveModalDialog'):break
 xbmc.sleep(100)
else:raise RuntimeError('FRESH_FIXTURE_MODAL_NOT_RELEASED')
w.show()
for i in range(200):
 a=xbmc.getInfoLabel('Container(510).NumItems');b=xbmc.getInfoLabel('Container(520).NumItems')
 if a=='24' and b=='24':
  xbmc.sleep(1000)
  xbmc.executebuiltin('TakeScreenshot(/root/native-widget59.png)',wait=False)
  xbmcgui.Window(10000).setProperty('NativeWidget59.Result',json.dumps(dict(vod=int(a),series=int(b),window=xbmcgui.getCurrentWindowId())))
  break
 xbmc.sleep(100)
xbmc.sleep(3000);w.close()

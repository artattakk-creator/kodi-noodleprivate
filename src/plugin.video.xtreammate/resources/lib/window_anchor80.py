"""Complete this invocation's Home widget request, never close a foreign modal."""
import time

def home(router):
 import xbmc,xbmcgui
 if xbmcgui.getCurrentWindowId()!=10000:return None
 dialog=xbmcgui.getCurrentWindowDialogId()
 if dialog not in (0,-1,9999,10138):return False
 if router._handle<0:return dialog in (0,-1,9999)
 from boot_diagnostics import finish_directory
 finish_directory(router,succeeded=False,cacheToDisc=False)
 monitor=xbmc.Monitor();until=time.monotonic()+1
 while time.monotonic()<until:
  if xbmcgui.getCurrentWindowId()!=10000:return False
  dialog=xbmcgui.getCurrentWindowDialogId()
  if dialog in (0,-1,9999):return True
  if dialog!=10138 or monitor.waitForAbort(.025):return False
 return False

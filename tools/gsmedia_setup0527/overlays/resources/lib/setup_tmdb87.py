"""Optional post-install pairing. Contains no endpoint, token or device secret."""
import importlib,os,sys
from pathlib import Path
CODES={'SKIPPED','PENDING','PAIRED','AUTH_FAILED','SERVER_UNAVAILABLE'}
def classify(state):
 if state=='GATEWAY_PAIRED':return 'PAIRED'
 if state=='PENDING':return 'PENDING'
 if state in ('LOCAL_TOKEN_VALID','LOCAL_TOKEN_INVALID','OPTED_OUT','NOT_CONFIGURED','NOT_PAIRED','USER_CANCELLED'):return 'SKIPPED'
 return 'AUTH_FAILED' if state in ('AUTH_FAILED','PAIRING_EXPIRED','GATEWAY_ENDPOINT_CHANGED') else 'SERVER_UNAVAILABLE'
def _offer(profile,manual=False):
 """Owner-thread UI; network remains the bounded .87 client task's work.

 No secret-bearing result is copied into the installer journal or properties.
 Missing server/client and Skip are never a component installation failure.
 """
 import xbmcaddon,xbmcgui
 try:
  addon=xbmcaddon.Addon('plugin.video.xtreammate')
  version=tuple(int(v) for v in addon.getAddonInfo('version').split('.'))
  if version<(0,1,29,87):return 'SKIPPED'
  lib=Path(addon.getAddonInfo('path'))/'resources/lib'
  if str(lib) not in sys.path:sys.path.insert(0,str(lib))
  client=importlib.import_module('tmdb_gateway_client87');state=client.status()
  if state in ('NOT_CONFIGURED','OPTED_OUT','LOCAL_TOKEN_VALID','LOCAL_TOKEN_INVALID','GATEWAY_PAIRED'):return classify(state)
  dialog=xbmcgui.Dialog()
  if not manual and not dialog.yesno('TMDB sicher verbinden','Optional: Diese neue Box mit dem privaten Gateway verbinden? Die Freigabe erfolgt durch den Administrator. Später ist ebenfalls möglich.',defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):return 'SKIPPED'
  importlib.import_module('tmdb_gateway_ui87').show()
  return classify(client.status())
 except (ImportError,OSError,ValueError,RuntimeError,AttributeError):return 'SERVER_UNAVAILABLE'

def offer(profile,manual=False):
 code=_offer(profile,manual)
 # Kodi owns atomic settings persistence. Only this five-value public state
 # goes into the installer journal, never the device verifier or permission.
 try:
  import xbmcaddon
  xbmcaddon.Addon('script.gsmedia.setup').setSetting('tmdb_pairing_state87',code if code in CODES else 'SERVER_UNAVAILABLE')
 except (RuntimeError,AttributeError):pass
 return code

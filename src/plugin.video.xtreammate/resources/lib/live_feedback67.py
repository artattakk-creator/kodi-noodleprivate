"""Kodi error signal only; never stops/retries/routes any player."""
import threading,time
_lock=threading.Lock();_pending=None;_seen={}
def monitor():
 import xbmc
 class Errors(xbmc.Player):
  def onPlayBackError(self):
   global _pending
   import xbmcgui
   from live_overlay import SESSION_KEY,session_from_property
   value=session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
   if value and 0<=time.time()-value.get('at',0)<60:
    with _lock:_pending=value
 return Errors()
def poll():
 global _pending
 with _lock:value=_pending;_pending=None
 if not value:return
 import xbmc,xbmcgui
 from live_overlay import SESSION_KEY,session_from_property
 current=session_from_property(xbmcgui.Window(10000).getProperty(SESSION_KEY))
 if current!=value or xbmc.Player().isPlayingVideo() or value['nonce'] in _seen:return
 _seen[value['nonce']]=True
 while len(_seen)>16:_seen.pop(next(iter(_seen)))
 xbmc.log('[XCMate][LIVE67] code=NATIVE_PLAYBACK_ERROR_SIGNAL; exact HTTP/format cause unconfirmed',xbmc.LOGWARNING)
 xbmcgui.Dialog().notification('XCMate','Live-Start fehlgeschlagen: Netzwerk oder Streamformat. Unter Live-TV → Live-Stream prüfen diagnostizieren.')

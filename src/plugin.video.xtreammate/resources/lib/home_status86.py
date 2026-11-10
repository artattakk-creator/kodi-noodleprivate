"""Truthful compact Home status. Reference publication is not a rendered frame."""
import json,time
_started={}
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def rail(portal,count,local):
 pid=str(portal['id']);_started.setdefault(pid,time.monotonic())
 while len(_started)>8:_started.pop(next(iter(_started)))
 window().setProperty('XCMate.Home86.Rail',json.dumps(dict(pid=pid,total=count,local=local,at=time.monotonic())))
 window().setProperty('XCMate.Home86.Text','Sender '+str(count)+' · Logos '+str(local)+'/'+str(count)+' · EPG/Hero werden ergänzt')
 window().setProperty('XCMate.Home86.IdentityReady','true' if count else '')
def observe():
 import xbmc,xbmcgui
 if xbmc.getSkinDir()!='skin.titan.bingie.mod' or xbmcgui.getCurrentWindowId()!=10000:return
 win=window()
 try:data=json.loads(win.getProperty('XCMate.Home86.Rail') or '{}')
 except ValueError:return
 if not data:return
 if time.monotonic()-data.get('at',0)>60:
  win.setProperty('XCMate.Home86.Text','Sender '+str(data['total'])+' · Logos '+str(data['local'])+'/'+str(data['total'])+' · fehlende Bilder: Diagnose verfügbar')
 else:
  ready=bool(xbmc.getInfoLabel('Control.GetLabel(296752)'))
  win.setProperty('XCMate.Home86.Text','Sender '+str(data['total'])+' · Logos '+str(data['local'])+'/'+str(data['total'])+' · EPG '+('bereit' if ready else 'ausstehend'))

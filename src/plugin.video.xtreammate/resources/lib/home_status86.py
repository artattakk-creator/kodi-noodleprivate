"""Truthful compact Home status. Reference publication is not a rendered frame."""
import json,time
_started={};_seen={}
def note(code,**facts):
 if code not in ('GROUP_READ_MS','LOGOS_LOCAL_READY','LOGOS_RAM_READY','LOGOS_EXTERNAL_READY','LOGOS_FALLBACK','RAIL_CONTROL_READY_MS','EPG_TEXT_READY_MS','HERO_REFERENCE_READY_MS','DIRECTORY_REINVOCATION_REASON'):return
 safe={k:v for k,v in facts.items() if k in ('ms','count','total') and type(v) in (int,float)}
 tag=(code,tuple((k,v) for k,v in safe.items() if k!='ms'));now=time.monotonic()
 if now-_seen.get(tag,-1e9)<30:return
 _seen[tag]=now
 while len(_seen)>64:_seen.pop(next(iter(_seen)))
 import xbmc
 try:xbmc.log('[XCMate][HOME86] '+code+' '+json.dumps(safe,separators=(',',':')),xbmc.LOGINFO)
 except (AttributeError,RuntimeError):pass
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def rail(portal,count,local,ram=0,external=0):
 from epg_handoff63 import profile_scope
 pid=str(portal['id']);_started.setdefault(pid,time.monotonic())
 while len(_started)>8:_started.pop(next(iter(_started)))
 try:prior=json.loads(window().getProperty('XCMate.Home86.Rail') or '{}')
 except ValueError:prior={}
 context=__import__('logo_manifest86').context(portal)
 first=prior.get('first_at',time.monotonic()) if prior.get('context')==context else time.monotonic()
 note('LOGOS_LOCAL_READY',count=local,total=count)
 if ram:note('LOGOS_RAM_READY',count=ram,total=count)
 if external:note('LOGOS_EXTERNAL_READY',count=external,total=count)
 window().setProperty('XCMate.Home86.Rail',json.dumps(dict(context=context,first_at=first,profile=profile_scope(),pid=pid,total=count,local=local,ram=ram,external=external,at=time.monotonic())))
 from localization import tr
 if prior.get('context')!=context or not window().getProperty('XCMate.Home86.State'):
  window().setProperty('XCMate.Home86.Text',tr(37103))
  window().setProperty('XCMate.Home86.State','LOADING')
 window().setProperty('XCMate.Home86.IdentityReady','true' if count else '')
 window().setProperty('XCMate.Home86.Profile',profile_scope())
def observe():
 import xbmc,xbmcgui
 try:
  if xbmc.getSkinDir()!='skin.titan.bingie.mod' or xbmcgui.getCurrentWindowId()!=10000:return
 except (AttributeError,RuntimeError):return
 win=window()
 try:data=json.loads(win.getProperty('XCMate.Home86.Rail') or '{}')
 except ValueError:return
 if not data:return
 if data.get('profile')!=__import__('epg_handoff63').profile_scope():return
 from widget_runtime79 import _plans,_lock
 with _lock:plan=dict(_plans.get((data.get('pid'),'live'),{}))
 if plan.get('scope')!=data.get('profile') or time.monotonic()-plan.get('at',-1e9)>60:plan={}
 receipt87=None
 try:directory87=json.loads(win.getProperty(plan.get('slot','')) or '{}')
 except ValueError:directory87={}
 for cid in plan.get('ids',[])[:8]:
  raw=xbmc.getInfoLabel('Container('+str(cid)+').NumItems')
  if str(raw)==str(data.get('total')) and xbmc.getCondVisibility('Control.IsVisible('+str(cid)+')') and len(directory87.get('tag',''))==64 and xbmc.getInfoLabel('Container('+str(cid)+').ListItem.Property(XCMate.Directory79)')==directory87['tag']:
   receipt87=directory87['tag']
   if win.getProperty('XCMate.Home87.FirstControl')!=receipt87:
    note('RAIL_CONTROL_READY_MS',ms=int((time.monotonic()-data.get('first_at',time.monotonic()))*1000),count=data['total'])
    win.setProperty('XCMate.Home87.FirstControl',receipt87)
   break
 from localization import tr
 bank=win.getProperty('XCMate.Hero63.Active');prefix='XCMate.Hero63.'+bank+'.'
 epg=bool(win.getProperty(prefix+'Title'))
 kind=win.getProperty(prefix+'Kind86');image=kind in ('hero_backdrop','official_poster')
 complete=bool(receipt87 and data.get('total') and data.get('local',0)+data.get('ram',0)+data.get('external',0)>=data['total'] and epg and image)
 if complete:
  win.setProperty('XCMate.Home86.State','REFERENCE_READY');win.setProperty('XCMate.Home86.Text','');return
 expired=time.monotonic()-data.get('first_at',data.get('at',0))>60
 win.setProperty('XCMate.Home86.State','ERROR' if expired else 'READY_PARTIAL')
 # These are reference/control states; only screenshot tests prove pixels.
 available88=data['local']+data.get('ram',0)+data.get('external',0)
 text=tr(37104).format(data['total'],available88) if expired else tr(37099).format(data['total'],available88,tr(37100) if epg else tr(37101),tr(37100) if image else tr(37101))
 win.setProperty('XCMate.Home86.Text',text)

"""Four optional native source providers on the existing worker/GUI lanes.

Worker: bounded private inventory and installed/enabled checks, no network.
GUI: RAM/native labels only; one source admitted at a time, no reload pulses,
no source queries on focus, no retries that start another thread/provider.
"""
import json,threading,time
from pathlib import Path
from widget_six_sources import EXTRAS
_lock=threading.RLock();_plan=None;_stamp=None;_next=0;_rows={};_scope=None
PREFIX='XCMate.SixRows.'
TERMINAL={'READY','EMPTY_OR_ERROR','ERROR','TIMEOUT','SOURCE_NOT_CONFIGURED','SOURCE_AMBIGUOUS','SOURCE_UNAVAILABLE'}
TEXT={'WAITING':'Wartet auf die vorherige Reihe …','LOADING':'Wird geladen …','READY':'','EMPTY_OR_ERROR':'Keine Einträge · Quelle bei Bedarf prüfen','ERROR':'Quelle momentan nicht erreichbar','TIMEOUT':'Quelle antwortet nicht · später erneut öffnen','SOURCE_NOT_CONFIGURED':'Keine passende Quelle eingerichtet','SOURCE_AMBIGUOUS':'Mehrere Quellen eingerichtet · Auswahl prüfen','SOURCE_UNAVAILABLE':'Benötigtes Add-on fehlt oder ist deaktiviert'}

def selected_portal(portals,pid):
 # Exactly the same preference semantics as the preserved pid-less widget
 # routes; several enabled providers are not an ambiguous new source choice.
 if pid:
  rows=[p for p in portals if str(p['id'])==pid and p.get('enabled',True)]
  return rows[0] if len(rows)==1 else None
 return __import__('home_menu').active_portal(portals)

def prepare(portals):
 global _plan,_stamp,_next
 now=time.monotonic()
 if now<_next:return
 _next=now+5
 import xbmc,xbmcvfs,xbmcgui
 if xbmc.getSkinDir()!='skin.titan.bingie.mod':return
 from widget_transaction50 import read
 from widget_six_consumer import runtime_binding
 from widget_six_sources import discover
 profile=Path(xbmcvfs.translatePath('special://profile/'));skin=Path(xbmcvfs.translatePath('special://skin/'))
 target=skin/'xml/script-skinshortcuts-includes.xml'
 def stat(path):
  try:s=path.stat();return (str(path),s.st_mtime_ns,s.st_size)
  except OSError:return (str(path),None,None)
 reloads=tuple((name,xbmcgui.Window(10000).getProperty(name)) for name in ('widgetreload','widgetreload2','widgetreloadmovies','widgetreloadtvshows','TMDbHelper.Widgets.Reload'))
 portal_stamp=(tuple(str(p['id']) for p in portals),str(__import__('utils').setting('active_portal_id','')))
 stamp=(str(profile),portal_stamp,reloads,stat(target),tuple(stat(p) for p in sorted((profile/'addon_data/script.skinshortcuts').glob('*.properties'))),tuple(stat(p) for p in sorted((profile/'addon_data/script.skinshortcuts').glob('*-mainmenu.DATA.xml'))),int(now//60))
 if stamp==_stamp:return
 if not target.is_file():return
 binding=runtime_binding(read(target))
 if not binding:
  with _lock:_plan=None
  return
 selected=selected_portal(portals,binding['pid'])
 if selected is None:
  with _lock:_plan=None
  return
 checked={}
 def enabled(addon):
  if addon not in checked:
   try:
    reply=json.loads(xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=438,method='Addons.GetAddonDetails',params=dict(addonid=addon,properties=['enabled'])))))
    checked[addon]=reply.get('result',{}).get('addon',{}).get('enabled') is True
   except (ValueError,TypeError,RuntimeError):checked[addon]=False
  return checked[addon]
 plan=discover(profile,selected['id'],enabled,dict(reloads).get)
 if plan['code']!='READY':return
 plan.update(binding=binding,scope=(str(profile),str(selected['id'])),profile_scope=__import__('epg_handoff63').profile_scope())
 with _lock:_plan=plan;_stamp=stamp

def step(rows,sources,observed,now,admitted):
 """Pure transition function, including timeout without fake source success."""
 result={kind:dict(row) for kind,row in rows.items()}
 for kind,source in sources.items():
  previous=result.get(kind)
  signature=(source['source_hash'],source['code'])
  if previous is None or previous['signature']!=signature:
   keep=previous is not None and previous['signature'][0]==source['source_hash'] and previous.get('path')
   result[kind]=dict(signature=signature,state=source['code'],at=now,updating_seen=False,path=previous['path'] if keep else '',count=previous['count'] if keep else 0)
 # A timed-out native provider can still be active. Do not start another one
 # until Kodi confirms release; never clear its last-good path or list items.
 blocked=False
 for kind,row in result.items():
  observation=observed.get(kind,(0,False));count,updating=observation[:2]
  token=observation[2] if len(observation)>2 else str(count)
  if row['state']=='LOADING':
   row['count']=count;row['updating_seen']|=updating
   if not updating and count>0 and (row['updating_seen'] or token!=row.get('before')):row['state']='READY'
   elif now-row['at']>=60:row['state']='TIMEOUT'
   elif row['updating_seen'] and not updating:row['state']='EMPTY_OR_ERROR'
  if row['state']=='LOADING' or row['state']=='TIMEOUT' and updating:blocked=True
 if admitted and not blocked:
  for kind,_,_,_ in EXTRAS:
   row=result[kind]
   if row['state']=='WAITING':
    observed_before=observed.get(kind,(0,False));before=observed_before[2] if len(observed_before)>2 else str(observed_before[0])
    row.update(state='LOADING',at=now,path=sources[kind]['uri'],before=before);break
 return result

def poll():
 global _rows,_scope
 import xbmc,xbmcgui
 with _lock:plan=_plan
 if plan is None or plan['profile_scope']!=__import__('epg_handoff63').profile_scope():return
 home=xbmcgui.Window(10000)
 if xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999) or xbmc.getCondVisibility('System.HasActiveModalDialog'):return
 # This marker belongs to the already user-confirmed guarded skin plan.
 if xbmc.getInfoLabel('$VAR[XCMate.SixRows.Contract]')!='READY':return
 if _scope!=plan['scope']:
  _rows={};_scope=plan['scope']
  for kind,_,_,_ in EXTRAS:home.clearProperty(PREFIX+kind+'.Path')
 observed={}
 for kind,_,cid,_ in EXTRAS:
  raw=xbmc.getInfoLabel('Container('+str(cid)+').NumItems')
  observed[kind]=(int(raw) if str(raw).isdigit() else 0,bool(xbmc.getCondVisibility('Container('+str(cid)+').IsUpdating')),xbmc.getInfoLabel('Container('+str(cid)+').ListItem.FileNameAndPath')+'|'+xbmc.getInfoLabel('Container('+str(cid)+').ListItem.Label'))
 from home_schedule75 import rest_allowed
 # The existing schedule admits extras only after the Live page, films and
 # series have been prepared. No second catalogue/artwork warmup is created.
 _rows=step(_rows,plan['sources'],observed,time.monotonic(),rest_allowed())
 for kind,row in _rows.items():
  for field,value in (('Kind',kind),('State',row['state']),('Busy','true' if row['state']=='LOADING' else ''),('Text',TEXT.get(row['state'],'')),('Path',row['path']),('Expanded','true' if row['state']=='LOADING' or observed[kind][0]>0 else '')):
   key=PREFIX+kind+'.'+field
   if home.getProperty(key)!=value:home.setProperty(key,value)
 # Native directional links skip genuinely empty sources; extra headers stay
 # in the layout. The existing tail and every personal widget remain intact.
 populated=[(kind,cid) for kind,_,cid,_ in EXTRAS if observed[kind][0]>0]
 base=plan['binding']['series'];tail=plan['binding']['tail']
 home.setProperty(PREFIX+'series.Down',str(populated[0][1] if populated else tail))
 for index,(kind,cid) in enumerate(populated):
  home.setProperty(PREFIX+kind+'.Up',str(populated[index-1][1] if index else base))
  home.setProperty(PREFIX+kind+'.Down',str(populated[index+1][1] if index+1<len(populated) else tail))

 # Bind real Kodi controls. Static XML links remain safe before preparation.
 try:
  native=home.getControl(base)
  native.controlDown(home.getControl(populated[0][1] if populated else tail))
  for index,(kind,cid) in enumerate(populated):
   current=home.getControl(cid)
   current.controlUp(home.getControl(populated[index-1][1] if index else base))
   current.controlDown(home.getControl(populated[index+1][1] if index+1<len(populated) else tail))
 except (RuntimeError,AttributeError):pass  # Kodi can be rebuilding this Home.

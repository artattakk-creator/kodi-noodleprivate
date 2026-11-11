"""Correlate real directory items with active Home consumers, never fake pixels.

Worker reads saved consumers and sources; GUI reads RAM/native controls only.
At most two targeted retries per directory generation. No new user bindings,
layout defaults, global rebuild or DB write on the input thread.
"""
import hashlib,json,threading,time
_lock=threading.RLock();_plans={};_next=0;_seen={};_tries={};_static={};_repair_stamp=None
PREFIX='XCMate.Directory79.'
def slot(portal,kind):
 from widget_data41 import policy
 return PREFIX+hashlib.sha256((policy(portal,kind)+'|'+kind).encode()).hexdigest()[:32]
def generation(portal,kind,rows,assets=None):
 from widget_data41 import policy
 from home_publication74 import source_refs
 return hashlib.sha256(json.dumps([policy(portal,kind),[str(r['sid']) for r in rows],source_refs(rows),assets or {}],sort_keys=True).encode()).hexdigest()
def directory(portal,kind,items,tag):
 import xbmcgui
 from widget_assets69 import renderable
 value=dict(tag=tag,count=len(items),at=time.time(),images=sum(renderable(v.get('art',{}).get('poster')) for v in items))
 xbmcgui.Window(10000).setProperty(slot(portal,kind),json.dumps(value,separators=(',',':')))
 note(portal,kind,'SOURCE_READY' if items else 'SOURCE_WAITING',tag,count=len(items))
 note(portal,kind,'DIRECTORY_ITEMS',tag,count=len(items))
def note(portal,kind,stage,tag='',**facts):
 allowed={'SOURCE_READY','SOURCE_WAITING','DIRECTORY_ITEMS','SKIN_CONSUMER_READY','CONTROL_MISSING','CONTROL_HIDDEN','CONTROL_EMPTY','RELOAD_REQUESTED','RELOAD_ACK','ACTIVE_CONTROL','TEXTURE_REQUESTED','TEXTURE_CACHED','TEXTURE_PENDING'}
 if stage not in allowed:return
 if stage in ('ACTIVE_CONTROL','TEXTURE_REQUESTED','TEXTURE_PENDING'):
  from home_metrics82 import note as metric82
  metric82({'ACTIVE_CONTROL':'SKIN_CONTROL_ACTIVE','TEXTURE_REQUESTED':'IMAGE_DECODE_REQUESTED','TEXTURE_PENDING':'IMAGE_PENDING'}[stage],kind,**{k:v for k,v in facts.items() if k in ('control','count')})
 from epg_handoff63 import profile_scope
 identity=hashlib.sha256((profile_scope()+'|'+str(portal['id'])+'|'+kind+'|'+tag).encode()).hexdigest()[:12];key=(identity,stage);now=time.monotonic()
 if key in _seen and stage in ('RELOAD_ACK','ACTIVE_CONTROL','TEXTURE_REQUESTED','TEXTURE_CACHED'):return
 if now-_seen.get(key,-1e9)<30:return
 _seen[key]=now
 while len(_seen)>256:_seen.pop(next(iter(_seen)))
 clean={k:v for k,v in facts.items() if k in ('count','control','width','height','decoded','visible') and type(v) in (int,bool)}
 try:
  import xbmc
  xbmc.log('[XCMate][WIDGET79] generation='+identity+' kind='+kind+' stage='+stage+' '+json.dumps(clean,separators=(',',':')),xbmc.LOGINFO)
 except (AttributeError,RuntimeError):pass

def prepare(portals):
 global _next,_repair_stamp
 if time.monotonic()<_next:return
 _next=time.monotonic()+5
 import xbmc,xbmcvfs,xbmcgui
 if xbmc.getSkinDir()!='skin.titan.bingie.mod':return
 from widget_consumer58 import status
 from widget_hooks45 import read as hooks
 bindings=hooks().get('bindings',[]);plans={}
 from pathlib import Path
 import os
 skin=xbmcvfs.translatePath('special://skin/');profile=xbmcvfs.translatePath('special://profile/')
 def stamp(p):
  try:v=os.stat(p);return (v.st_mtime_ns,v.st_size)
  except OSError:return None
 layout_stamp=(skin,profile,stamp(Path(skin)/'xml/script-skinshortcuts-includes.xml'),stamp(Path(profile)/'addon_data/script.skinshortcuts/skin.titan.bingie.mod.properties'))
 __import__('widget_audit89').prepare(profile,skin)
 for portal in portals[:4]:
  static_key=(layout_stamp,str(portal['id']))
  static=_static.get(static_key)
  if static is None:
   static=status(portal['id'],observe=False);_static[static_key]=static
   while len(_static)>8:_static.pop(next(iter(_static)))
  for kind in ('live','vod','series'):
   state=static.get('kinds',{}).get(kind,{})
   hook_names=sorted({h for r in bindings if r.get('pid')==str(portal['id']) and r.get('kind')==kind for h in __import__('widget_hooks45').isolated89(r.get('hooks',[]))})
   plans[(str(portal['id']),kind)]=dict(portal=dict(portal),scope=__import__('epg_handoff63').profile_scope(),slot=slot(portal,kind),ids=state.get('control_ids59',[])[:8],hooks=hook_names,at=time.monotonic())
 with _lock:_plans.clear();_plans.update(plans)
 # Repair missing generated own hooks even when the .78 skin itself already
 # exists. Saved SkinShortcuts are read-only; this uses its private backup.
 try:
  from widget_skin78 import installed
  if _repair_stamp!=layout_stamp and installed(skin) and not xbmc.getCondVisibility('Player.HasMedia') and not xbmcgui.Window(10000).getProperty('skinshortcuts-isrunning'):
   from widget_reload78 import repair
   _repair_stamp=layout_stamp
   if repair(profile,skin):__import__('home_activation78').request('consumer79',consumers_changed=True)
 except (OSError,ValueError,RuntimeError,AttributeError):pass

def poll():
 import xbmc,xbmcgui
 if xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
 if xbmc.getCondVisibility('System.HasActiveModalDialog') or xbmc.getCondVisibility('Player.HasMedia'):return
 __import__('widget_audit89').poll()
 window=xbmcgui.Window(10000);now=time.monotonic()
 with _lock:plans=list(_plans.items())
 for (_,kind),plan in plans:
  if now-plan['at']>60 or plan['scope']!=__import__('epg_handoff63').profile_scope():continue
  portal=plan['portal']
  try:record=json.loads(window.getProperty(plan['slot']) or '{}')
  except (ValueError,TypeError):continue
  tag=record.get('tag','');expected=record.get('count',0)
  if len(tag)!=64 or type(expected) is not int or expected<=0:continue
  known=False;empty=False;ack=False
  for cid in plan['ids']:
   try:__import__('home_runtime77').control(window,cid)
   except (RuntimeError,AttributeError):note(portal,kind,'CONTROL_MISSING',tag,control=cid);continue
   note(portal,kind,'SKIN_CONSUMER_READY',tag,control=cid)
   label=lambda name:xbmc.getInfoLabel('Container('+str(cid)+').'+name)
   raw=label('NumItems')
   if not str(raw).isdigit():continue
   count=int(raw);visible=bool(xbmc.getCondVisibility('Control.IsVisible('+str(cid)+')'))
   if not visible:note(portal,kind,'CONTROL_HIDDEN',tag,control=cid,count=count);continue
   known=True
   if count==0:empty=True;note(portal,kind,'CONTROL_EMPTY',tag,control=cid);continue
   actual=label('ListItem.Property(XCMate.Directory79)')
   if actual!=tag:continue  # Counts from a foreign/older directory are no ACK.
   ack=True
   note(portal,kind,'RELOAD_ACK',tag,control=cid,count=count)
   note(portal,kind,'ACTIVE_CONTROL',tag,control=cid,count=count,visible=True)
   image=label('ListItem.Art(poster)')
   note(portal,kind,'TEXTURE_REQUESTED' if image else 'TEXTURE_PENDING',tag,control=cid,visible=True)
  if known and empty and not ack and plan['hooks']:
   key=(plan['slot'],tag);attempt,due=_tries.get(key,(0,now+2))
   if key not in _tries:_tries[key]=(0,due)
   elif attempt<2 and now>=due:
    for hook in plan['hooks']:
     if hook.startswith('XCMate.Widget45.Reload.') or hook in ('widgetreload','widgetreload2','widgetreloadmovies','widgetreloadtvshows'):window.setProperty(hook,tag+'.retry79.'+str(attempt))
    _tries[key]=(attempt+1,now+2);note(portal,kind,'RELOAD_REQUESTED',tag,count=attempt+1)
   while len(_tries)>64:_tries.pop(next(iter(_tries)))

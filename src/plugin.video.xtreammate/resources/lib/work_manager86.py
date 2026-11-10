"""Remote-operated manual work research. Empty results always allow editing."""
import time
import xbmc,xbmcgui
from localization import tr
from menu_icons45 import select as icon_select

def wait(event,operation,**options):
 from work_requests86 import request,result,cancel
 nonce=request(event,operation,**options);progress=xbmcgui.DialogProgress();progress.create('XCMate',tr(37086));monitor=xbmc.Monitor();deadline=time.monotonic()+30
 try:
  while not progress.iscanceled() and not monitor.abortRequested() and time.monotonic()<deadline:
   value=result(nonce)
   if value:return value
   if monitor.waitForAbort(.05):break
 finally:progress.close();cancel(nonce)
 return dict(code='CANCELLED',rows=[])

def event_for(parent):
 if getattr(parent,'event',None):return dict(parent.event)
 selected=getattr(parent,'selected',None)
 if isinstance(selected,dict) and getattr(parent,'kind','') in ('vod','series'):
  return dict(pid=str(parent.portal['id']),sid=str(selected['sid']),title=str(selected.get('name') or ''),year=selected.get('year'),media_kind86=parent.kind)
 # Even failed EPG reads must offer editable search, but cannot save stale work.
 selected=selected if isinstance(selected,dict) else {}
 channel=getattr(parent,'channel',{})
 return dict(selected,pid=str(parent.portal['id']),sid=str(channel.get('sid','')),title=str(selected.get('title') or ''))

def open(parent):
 if getattr(parent,'_closed',False):return False
 event=event_for(parent);query=str(event.get('title') or '')[:200];kind='movie' if event.get('media_kind86')=='vod' else 'tv';source='tmdb';page=1;changed=False
 dialog=xbmcgui.Dialog()
 while not getattr(parent,'_closed',False) and not xbmc.Monitor().abortRequested():
  action=icon_select(dialog,tr(37080),[tr(37081)+' · '+query,tr(37082)+' · '+source+' '+kind,tr(37083),tr(37084),tr(37085),tr(37098)])
  if action<0:return changed
  if action==5:
   image=dialog.browse(1,tr(37098),'files','.jpg|.jpeg|.png',False,False,'')
   if image and dialog.yesno('XCMate',tr(37089)):
    answer=wait(event,'local',path=image)
    if answer.get('code')=='SAVED':return True
    dialog.ok('XCMate',status(answer.get('code')))
   continue
  if action in (3,4):
   if not dialog.yesno('XCMate',tr(37087)):continue
   answer=wait(event,'save',action='automatic' if action==3 else 'hide')
   if answer.get('code')=='SAVED':changed=True;return changed
   dialog.ok('XCMate',status(answer.get('code')));continue
  if action==1:
   selected=icon_select(dialog,tr(37082),['TMDB · TV','TMDB · Movie','TVMaze · TV'])
   if selected<0:continue
   source,kind=(('tmdb','tv'),('tmdb','movie'),('tvmaze','tv'))[selected];page=1;continue
  if action==0 or not query:
   edited=dialog.input(tr(37081),defaultt=query)
   if not edited.strip():continue
   query=edited.strip()[:200];page=1
  answer=wait(event,'search',query=query,kind=kind,source=source,page=page)
  rows=answer.get('rows',[])
  if not rows:
   dialog.ok('XCMate',status(answer.get('code')));continue
  items=[]
  for row in rows:
   label=row['title']+' · '+str(row['year'])+' · '+','.join(row.get('country',[]))+' · '+row['source']+' '+row['media_type86']
   item=xbmcgui.ListItem(label,label2=row.get('overview',''));items.append(item)
   if row.get('thumb86'):item.setArt(dict(thumb=row['thumb86']))
   # Candidate URLs remain references, not evidence of visible Kodi pixels.
  items.append(xbmcgui.ListItem(tr(37081)))
  if answer.get('more'):items.append(xbmcgui.ListItem(tr(37088)))
  picked=icon_select(dialog,tr(37080),items,useDetails=True)
  if picked<0:continue
  if picked==len(rows):query=dialog.input(tr(37081),defaultt=query) or query;page=1;continue
  if picked>len(rows):page+=1;continue
  chosen=rows[picked]
  message=chosen['title']+' ('+str(chosen['year'])+') · '+chosen['source']+' '+chosen['media_type86']+'\n'+chosen.get('overview','')+'\n'+tr(37089)
  if not dialog.yesno('XCMate',message):continue
  answer=wait(event,'save',candidate=chosen)
  if answer.get('code')=='SAVED':return True
  dialog.ok('XCMate',status(answer.get('code')))
 return changed

def status(code):
 codes={'SOURCE_DISABLED':37090,'TMDB_TOKEN_MISSING':37091,'ZERO_RESULTS':37092,'EPG_REVISION_CHANGED':37093,'CANDIDATES_REJECTED':37094,'CANCELLED':37095,'SAVE_BLOCKED':37096,'UNCHANGED':37095}
 return tr(codes.get(code,37097))

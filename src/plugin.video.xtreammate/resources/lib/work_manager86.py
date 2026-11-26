"""Remote-operated manual work research. Empty results always allow editing."""
import time
import xbmc,xbmcgui
from localization import tr
from menu_icons45 import select as icon_select

def wait(event,operation,**options):
 from work_requests86 import request,result,cancel
 from work_trace87 import mark,picked,worker
 nonce=request(event,operation,**options);progress=xbmcgui.DialogProgress();progress.create('XCMate',tr(37110) if operation in ('save','local') else tr(37086));monitor=xbmc.Monitor();deadline=time.monotonic()+30
 try:
  while True:
   # A committed readback wins over a simultaneous Cancel, never claim it was undone.
   value=result(nonce)
   if value:
    mark(nonce,'UI_CONSUMED');mark(nonce,'UI_ACK');return value
   if operation=='save' and __import__('programme_mapping85').committed89(event,nonce):
    mark(nonce,'UI_ACK');return dict(code='SAVED',rows=[])
   if monitor.abortRequested():return dict(code='KODI_STOPPED',rows=[])
   if progress.iscanceled():return dict(code='USER_CANCELLED',rows=[])
   if time.monotonic()>=deadline:
    code='REQUEST_TIMEOUT' if picked(nonce) else 'WORKER_BUSY' if worker()!='WORKER_STOPPED' else 'WORKER_STOPPED'
    return dict(code=code,rows=[])
   monitor.waitForAbort(.05)
 finally:progress.close();cancel(nonce)

def event_for(parent):
 if getattr(parent,'event',None):return dict(parent.event)
 selected=getattr(parent,'selected',None)
 if isinstance(selected,dict) and getattr(parent,'kind','') in ('vod','series'):
  return dict(pid=str(parent.portal['id']),sid=str(selected['sid']),title=str(selected.get('name') or ''),year=selected.get('year'),media_kind86=parent.kind)
 # Even failed EPG reads must offer editable search, but cannot save stale work.
 selected=selected if isinstance(selected,dict) else {}
 channel=getattr(parent,'channel',{})
 return dict(selected,pid=str(parent.portal['id']),sid=str(channel.get('sid','')),title=str(selected.get('title') or ''))

def open(parent,*,source96=None):
 if getattr(parent,'_closed',False) or not __import__('programme_window46').permitted(parent):return False
 event=event_for(parent);query=str(event.get('title') or '')[:200];kind='movie' if event.get('media_kind86')=='vod' else 'tv';source='tmdb';page=1;changed=False
 dialog=xbmcgui.Dialog()
 if source96=='xmltv_event':source,kind='xmltv_event','event'
 from agent_work103 import LABELS, SOURCE
 live=event.get('media_kind86','live')=='live'
 filters={}
 rescan96=source96=='xmltv_event'
 while not getattr(parent,'_closed',False) and not xbmc.Monitor().abortRequested():
  action=2 if rescan96 else icon_select(dialog,tr(37080),[tr(37081)+' · '+query,tr(37082)+' · '+('EPG Agent' if source==SOURCE else source+' '+kind),tr(37083),tr(37084),tr(37085),tr(37098)]+([tr(39026),'EPG Agent · Bildersuche im lokalen Datenbestand'] if live else [])+(['EPG Agent · Suchfilter'] if live and source==SOURCE else []))
  rescan96=False
  if action in (6,7):source,kind=('xmltv_event' if action==6 else SOURCE),'event';page=1;action=2
  if action==8:
   filters=agent_filters(dialog,filters);page=1;action=2
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
   selected=icon_select(dialog,tr(37082),['TMDB · TV','TMDB · Movie','TVMaze · TV']+(['XMLTV','EPG Agent'] if live else []))
   if selected<0:continue
   source,kind=(('tmdb','tv'),('tmdb','movie'),('tvmaze','tv'),('xmltv_event','event'),(SOURCE,'event'))[selected];page=1;continue
  if action==0 or not query and source!=SOURCE:
   edited=dialog.input(tr(37081),defaultt=query)
   if not edited.strip():continue
   query=edited.strip()[:200];page=1
  answer=wait(event,'search',query=query,kind=kind,source=source,page=page,**(filters if source==SOURCE else {}))
  rows=answer.get('rows',[])
  if not rows and not answer.get('more'):
   dialog.ok('XCMate',status(answer.get('code')));continue
  items=[];labels=[]
  for row in rows:
   origin=('XMLTV' if row['source']=='xmltv_event' else row['source']+' '+row['media_type86'])
   if row['source']==SOURCE:
    origin=' · '.join(part for part in (LABELS[row['role']],row['attribution'],row.get('channel',''),
                         f"S{row['season']} E{row['episode']}" if row.get('season') and row.get('episode') else '',
                         row.get('work_id','')) if part)
   label=' · '.join(part for part in (row['title'],str(row.get('year') or ''),','.join(row.get('country',[])),origin) if part)
   item=xbmcgui.ListItem(label,label2=row.get('overview',''));items.append(item);labels.append(label)
   if row.get('thumb86'):item.setArt(dict(thumb=row['thumb86']))
   # Candidate URLs remain references, not evidence of visible Kodi pixels.
  items.append(xbmcgui.ListItem(tr(37081)))
  if answer.get('more'):items.append(xbmcgui.ListItem(tr(37088)))
  picked=icon_select(dialog,tr(37080),items,useDetails=True)
  if picked<0:continue
  if picked==len(rows):query=dialog.input(tr(37081),defaultt=query) or query;page=1;continue
  if picked>len(rows):page+=1;continue
  chosen=rows[picked]
  label=labels[picked]
  if chosen['source']==SOURCE:
   answer=wait(event,'preview',candidate=chosen)
   if answer.get('code')!='READY' or not answer.get('rows'):
    dialog.ok('XCMate',status(answer.get('code')));continue
   preview=xbmcgui.ListItem(label,label2=tr(37089));preview.setArt(dict(thumb=answer['rows'][0]['thumb86']))
   if icon_select(dialog,'EPG Agent · Bildvorschau',[preview,tr(37081)])!=0:continue
  reference=' · '.join(str(event[k]) for k in ('subtitle','year') if event.get(k))
  message=label+'\n'+chosen.get('overview','')+'\n'
  if reference and chosen['source']!=SOURCE:message+='EPG · '+reference+'\n'
  message+=tr(37089)
  if not dialog.yesno('XCMate',message):continue
  answer=wait(event,'save',candidate=chosen)
  if answer.get('code')=='SAVED':
   dialog.ok('XCMate',tr(38720));return True
  dialog.ok('XCMate',status(answer.get('code')))
 return changed

def agent_filters(dialog,filters):
 from agent_work103 import LABELS
 sources={'agent_tmdb':'TMDB','agent_tvmaze':'TVMaze','agent_xmltv':'XMLTV'}
 result=dict(filters)
 labels={'role':'Bildrolle','image_source':'Bildquelle','year':'Jahr','season':'Staffel','episode':'Folge'}
 definitions={'role':LABELS,'image_source':sources}
 keys=list(labels)
 def label(key):
  value=result.get(key,'')
  return labels[key]+' · '+str(definitions.get(key,{}).get(value,value) or 'Alle')
 picked=icon_select(dialog,'EPG Agent · Suchfilter',[label(key) for key in keys]+['Filter zurücksetzen'])
 if picked<0:return result
 if picked==len(keys):return {}
 key=keys[picked]
 if key in definitions:
  options=definitions[key]
  selected=icon_select(dialog,labels[key],['Alle']+list(options.values()))
  if selected>=0:result[key]=(['']+list(options))[selected]
 else:
  text=dialog.input(labels[key],defaultt=str(result.get(key,'')),type=xbmcgui.INPUT_NUMERIC)
  if text and text.isdecimal():result[key]=int(text)
 return result

def status(code):
 codes={'RESERVE_BLOCKED':38721,'PROFILE_BUSY':38722,'SQLITE_BUSY':38722,'WRITE_DENIED':38723,'SOURCE_DISABLED':37090,'TMDB_TOKEN_MISSING':37091,'ZERO_RESULTS':37092,'EPG_REVISION_CHANGED':37093,'CANDIDATES_REJECTED':37094,'CANCELLED':37111,'USER_CANCELLED':37111,'REQUEST_TIMEOUT':37112,'WORKER_BUSY':37113,'WORKER_STOPPED':37114,'KODI_STOPPED':37115,'NETWORK_TIMEOUT':37116,'PERSISTENCE_BLOCKED':37117,'READBACK_FAILED':37117,'SAVE_BLOCKED':37096,'UNCHANGED':37095}
 if code in ('BLOCKED_IMAGE_HOST_OR_URL','BLOCKED_CREDENTIAL_URL','NO_ARTWORK','AGENT_CACHE_UNAVAILABLE',
             'DNS_ERROR','TLS_ERROR','HTTP_AUTH','HTTP_NOT_FOUND','HTTP_RATE_LIMIT','HTTP_SERVER','NETWORK_ERROR'):
  return tr(37097)+' · '+code
 return tr(codes.get(code,37097))

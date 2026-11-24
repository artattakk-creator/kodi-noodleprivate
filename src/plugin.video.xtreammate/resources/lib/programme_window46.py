"""Owned child programme dialog; preserves parent grid, player and focus.

Callbacks queue intent. Only the parent's pump opens a child, with an exact
parent dialog identity check. Never close foreign modals or use Container.Update.
"""
import threading,time
from concurrent.futures import Future
import xbmc,xbmcgui,xbmcaddon
from localization import tr
_slots=threading.BoundedSemaphore(2)

def channel_row(channel):
 if isinstance(channel,dict):return dict(channel)
 return dict(channel.extra,sid=str(channel.extra.get('stream_id','')),name=channel.name,epg_channel_id=getattr(channel,'tvg_id',''))

def request(parent,channel,event=None):
 if getattr(parent,'_closed',False) or getattr(parent,'_leaving',False) or channel is None:return
 parent._programme_request46=(channel_row(channel),dict(event) if event else None)

def permitted(parent=None):
 try:dialog=int(xbmcgui.getCurrentWindowDialogId())
 except (AttributeError,RuntimeError,ValueError,TypeError):return False
 if dialog in (0,-1,9999):return True
 if parent is not None:
  owner=getattr(parent,'_owner69','')
  if owner and xbmcgui.Window(dialog).getProperty('XCMate.NativeOwner')==owner:return True
  if dialog==getattr(parent,'_native_dialog_id',None):return True
  nonce=getattr(parent,'_window_nonce',None)
  if nonce and xbmcgui.Window(dialog).getProperty('XtreamMate.NavigatorIdentity')==nonce:return True
 return False

def open_pending(parent):
 wanted=getattr(parent,'_programme_request46',None)
 if not wanted:return
 parent._programme_request46=None
 if parent._closed or getattr(parent,'_leaving',False):return
 if not permitted(parent):xbmcgui.Dialog().notification('XCMate',tr(36105));return
 return show(parent.portal,wanted[0],wanted[1],parent)

def show(portal,channel,event=None,parent=None,*,manual96=False):
 if not permitted(parent):xbmcgui.Dialog().notification('XCMate',tr(36105));return
 dialog=ProgrammeWindow46('XCMateProgramme46.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
 dialog.configure(portal,channel,event,parent);dialog._manual96=bool(manual96);dialog.run()
 if dialog._tune88 and parent is not None:
  if not __import__('programme_actions88').tune(parent,portal,channel):xbmcgui.Dialog().notification('XCMate','Sender kann aus dieser Ansicht momentan nicht umgeschaltet werden.')
 return dialog

class ProgrammeWindow46(xbmcgui.WindowXMLDialog):
 def configure(self,portal,channel,event=None,parent=None):
  self.portal,self.channel,self.selected,self.parent=portal,dict(channel),event,parent
  self._owner=threading.get_ident();self._closed=False;self._ready=False;self._shown=False;self._init_error69=False;self._read_deadline69=0
  self._retries85=0;self._retry_after85=0
  self._intent88=None;self._action88=None;self._tune88=False;self._timeline88=''
  self._hero_art={};self._poster_art={};self._next_art_intent=0
  self._cancel=threading.Event();self._future=None;self.event=None;self._art_signature=None;self._next=0;self._scroll46=0;self._art68={}
 def _gui(self):
  if threading.get_ident()!=self._owner:raise RuntimeError('PROGRAMME_OWNER_THREAD')
 @__import__('programme_lifecycle69').initialized
 def onInit(self):
  self._gui()
  if self._ready:return
  for cid in (104,105,107,108,110,114,115,116,120,121,130):
   self.getControl(cid).setVisible(False)
  self._shown=True;self._ready=True;self.getControl(501).setLabel(tr(36101));self.getControl(101).setLabel(tr(36100))
  from menu_icons45 import icon
  self.getControl(881).setImage(icon('back',full=True));self.setFocusId(501)
  self._paint_facts(dict(self.selected or {},channel=self.channel.get('name','')))
  self.getControl(502).setLabel('Sendung merken');self.getControl(503).setLabel('Jetzt umschalten')
  self._start_read85()
 def _start_read85(self):
  if not _slots.acquire(blocking=False):return
  future=Future();self._future=future;self._read_deadline69=time.monotonic()+5
  def work():
   try:
    if not future.set_running_or_notify_cancel():return
    try:
     from programme_events46 import load,source_name
     from media_art import local_art,request as request_logos
     value=load(self.portal,self.channel,self.selected)
     value['_source_label100']=source_name(self.portal,value)
     value['_detail93']=True
     if self.selected and self.selected.get('_no_art_request68'):value['_no_art_request68']=True
     logos88=__import__('logo_manifest86').read(self.portal,[self.channel])
     verified_logo=logos88.get(str(self.channel.get('sid')),'')
     value['logo']=verified_logo or local_art(self.channel)['thumb'];request_logos([self.channel])
     from programme_art46 import cached
     from programme_requests68 import request
     value['_art68']=__import__('programme_preview67').shared(value) or cached(value)
     if not self._cancel.is_set():self._advertise_art(value,request)
     future.set_result(value)
    except Exception:future.set_exception(RuntimeError('PROGRAMME_READ_FAILED'))
   finally:_slots.release()
  try:threading.Thread(target=work,name='XCMate-programme-detail46',daemon=True).start()
  except (RuntimeError,MemoryError):_slots.release();self._future=None
 def _paint_facts(self,event):
  from presentation80 import text
  from programme_assets47 import station_image

  def label(cid,value):
   control=self.getControl(cid);control.setLabel(value);control.setVisible(bool(value))

  logo=event.get('logo','')
  real=station_image(logo)
  self.getControl(111).setImage(logo if real else '')
  self.getControl(111).setVisible(real)
  label(112,'' if real else text(event.get('channel')))
  label(101,text(event.get('title')))
  episode=event.get('subtitle') or event.get('episode_label')
  if not episode and event.get('season') and event.get('episode'):
   episode=tr(36103,event['season'],event['episode'])
  label(102,text(episode))
  label(106,' · '.join(text(event[k]) for k in ('year','genre','age_rating') if event.get(k)))
  source=event.get('_source_label100','')
  label(109,tr(32753)+' · '+source if source else '')

  body=[]
  if event.get('description'):body.append(text(event['description']))
  cast=event.get('cast')
  if isinstance(cast,list) and cast:
   body.append(tr(36104)+' · '+', '.join(text(name) for name in cast))
  if event.get('director'):body.append('Regie · '+text(event['director']))
  if event.get('following46'):
   body.append('Danach\n'+'\n'.join(
       time.strftime('%H:%M',time.localtime(row['start']))+'  '+text(row['title'])
       for row in event['following46']))
  self.getControl(103).setText('\n\n'.join(body))
  self.getControl(103).setVisible(bool(body))
  self.getControl(117).setVisible(bool(body))
  self._paint_time(event)

 def _paint_time(self,event):
  stamp,percent=__import__('programme_actions88').timeline(event)
  if stamp:
   stamp=time.strftime('%d.%m. · ',time.localtime(event['start']))+stamp
  if stamp!=self._timeline88:
   self.getControl(107).setLabel(stamp);self._timeline88=stamp
  self.getControl(107).setVisible(bool(stamp))
  current=bool(stamp and event['start']<=time.time()<event['stop'])
  for cid in (120,121):self.getControl(cid).setVisible(current)
  if current:self.getControl(121).setWidth(max(1,int(520*percent/100)))

 @staticmethod
 def _advertise_art(event,request):
  request(event,priority=True)
  art=event.get('agent_art') or {}
  if art.get('backdrop'):request(dict(event,_art_view499='hero'),priority=True)
  if art.get('poster'):request(dict(event,_art_view499='card'),priority=False)

 def _paint_art(self,art,hero,poster):
  from programme_actions88 import rating,tmdb_source
  from programme_image69 import eligible

  def image(value,view=None):
   event=dict(self.event,_art_view499=view) if view else self.event
   return value.get('image','') if not value.get('provisional85') and eligible(value,event) else ''

  hero_image=image(hero,'hero')
  poster_image=image(poster,'card')
  detail_image=image(art)
  confirmed=__import__('agent_programme100').manual(art)
  ready=detail_image if confirmed and art.get('role81')!='poster' else hero_image
  if not ready and art.get('role81')!='poster':ready=detail_image
  cover=poster_image if poster.get('role81')=='poster' else ''
  if (confirmed or not cover) and art.get('role81')=='poster':cover=detail_image
  if cover==ready:cover=''
  primary=art if confirmed and detail_image else hero if hero_image else poster if cover and cover==poster_image and not ready else art
  source=primary.get('source','') if ready or cover else ''
  score_scope={'tmdb_movie':'Film','tmdb_series':'Serie','tmdb_episode':'Folge'}.get(source)
  score=rating(primary) if score_scope else ''
  signature=(ready,cover,source,score)
  if signature==self._art_signature:return
  self._art_signature=signature
  for cid,uri in ((110,ready),(114,cover)):
   control=self.getControl(cid);control.setImage(uri);control.setVisible(bool(uri))
  for cid in (115,116):self.getControl(cid).setVisible(bool(ready))
  self.getControl(130).setVisible(tmdb_source(source))
  self.getControl(108).setLabel(score+' · '+score_scope if score else '')
  self.getControl(108).setVisible(bool(score))
  names={'provider_event':'Anbieter','xmltv_event':'XMLTV','agent_xmltv':'XMLTV',
         'tvmaze_series':'TVMaze','tvmaze_episode':'TVMaze','agent_tvmaze':'TVMaze',
         'user_local86':'Manuell'}
  image_source='TMDB' if tmdb_source(source) else names.get(source,'')
  self.getControl(105).setLabel('Bild · '+image_source if image_source else '')
  self.getControl(105).setVisible(bool(image_source))
  # Text can move up into the neutral area when no hero is available.
  self.getControl(117).setPosition(58,362 if ready or cover else 351)
  self.getControl(103).setPosition(82,381 if ready or cover else 370)
  self.getControl(103).setHeight(184 if ready or cover else 195)
  __import__('programme_pipeline77').note(self.event,'RENDER_CONTROL',
      'IMAGE_REQUESTED' if ready or cover else 'SOURCE_MISSING',
      control=110,visible=bool(ready or cover))

 def pump(self):
  self._gui()
  if self._closed:return
  if __import__('programme_lifecycle69').pulse(self):return
  if self.parent is not None and self.parent._closed:self.close();return
  if self._intent88=='bookmark' and self.event and self._action88 is None and _slots.acquire(blocking=False):
   self._intent88=None;future88=Future();self._action88=future88;event88=dict(self.event)
   def save88():
    try:
     if future88.set_running_or_notify_cancel():
      try:future88.set_result(__import__('programme_actions88').bookmark(event88,self._cancel.is_set))
      except Exception:future88.set_exception(OSError('BOOKMARK_FAILED'))
    finally:_slots.release()
   try:threading.Thread(target=save88,name='XCMate-programme-bookmark88',daemon=True).start()
   except RuntimeError:_slots.release();self._action88=None
  if self._action88 is not None and self._action88.done():
   try:
    added88=self._action88.result();self.getControl(502).setLabel('Nicht mehr merken' if added88 else 'Sendung merken')
    if added88:xbmcgui.Dialog().notification('XCMate',tr(33116))
   except Exception:xbmcgui.Dialog().notification('XCMate','Merkliste konnte nicht gespeichert werden.')
   self._action88=None
  if getattr(self,'_series_menu85',False):
   self._series_menu85=False
   if __import__('work_manager86').open(self):
    self._art68={};self._art_signature=None;self._next=0
    if self.event:__import__('programme_requests68').request(self.event,priority=True)
   return
  if self._future is not None and not self._future.done() and time.monotonic()>self._read_deadline69:
   self._cancel.set();self._future.cancel();self._future=None
   __import__('programme_lifecycle69').mark(self,'READ_TIMEOUT')
  if self._future is not None and self._future.done():
   future=self._future;self._future=None
   try:self.event=future.result()
   except Exception:__import__('programme_lifecycle69').mark(self,'READ_FAILED')
   else:
    if getattr(self,'_manual96',False):self._series_menu85=True;self._manual96=False
    self._art68=self.event.pop('_art68',{})
    self._paint_facts(self.event)
  if self.event and time.monotonic()>=self._next:
   self._next=time.monotonic()+.5
   from programme_image69 import eligible
   from programme_lastgood80 import choose
   from programme_requests68 import request,result

   art=choose(self.event,result(self.event,self._art68),self._art68) or {}
   if eligible(art,self.event):self._art68=dict(art)
   roles=self.event.get('agent_art') or {}
   for role,view,field in (('backdrop','hero','_hero_art'),('poster','card','_poster_art')):
    if roles.get(role):
     event_view=dict(self.event,_art_view499=view)
     prior=getattr(self,field)
     setattr(self,field,choose(event_view,result(event_view,prior),prior) or {})
   if art.get('source') in (None,'','placeholder') and time.monotonic()>=self._next_art_intent:
    self._next_art_intent=time.monotonic()+5
    self._advertise_art(self.event,request)
   self._paint_art(art,self._hero_art,self._poster_art)
   self._paint_time(self.event)
 def run(self):
  self._gui();monitor=xbmc.Monitor();start=time.monotonic()
  try:
   if not permitted(self.parent):return
   self.show()
   while not self._closed:
    if self._init_error69:break
    if self._ready:self.pump()
    elif time.monotonic()-start>10:break
    if monitor.waitForAbort(.05):break
  finally:self.close()
 def onAction(self,action):
  self._gui()
  key=action.getId()
  if key==117 or key==1 and self.getFocusId()==501:self._series_menu85=True
  elif key in (9,10,92):self.close()
  elif key in (3,4,5,6):
   self._scroll46=max(0,min(512,self._scroll46+(-1 if key==3 else 1 if key==4 else -10 if key==5 else 10)))
   self.getControl(103).scroll(self._scroll46)
 def onClick(self,cid):
  self._gui()
  if cid==501:self.close()
  elif cid==502 and self.event and self._action88 is None:self._intent88='bookmark'
  elif cid==503 and not self._tune88 and not __import__('station_rows88').header(self.channel):self._tune88=True;self.close()
 def close(self):
  self._gui()
  if self._closed:return
  self._closed=True;self._cancel.set()
  if self._art68.get('asset88'):__import__('decoded_assets88').release(self._art68['asset88'])
  __import__('programme_lifecycle69').mark(self,'CLOSE')
  __import__('programme_lifecycle69').unregister(self)
  if self._future:self._future.cancel()
  if self._action88:self._action88.cancel()
  if self._shown:super().close()

def launch_standalone(portal,channel,selected=None):
 """Serialize root dispatches; wait briefly for natural modal release only.

This runs in the plugin interpreter, never in a parent's GUI callback. Parent
children use the exact parent identity path instead and retain its owner lease.
"""
 from window_navigation import ownership
 with ownership() as acquired:
  if not acquired:xbmcgui.Dialog().notification('XCMate',tr(36105));return
  deadline=time.monotonic()+2;monitor=xbmc.Monitor()
  while not permitted():
   if time.monotonic()>=deadline or monitor.waitForAbort(.05):
    xbmcgui.Dialog().notification('XCMate',tr(36105));return
  return show(portal,channel,selected)


def route(router,portal):
 from boot_diagnostics import finish_directory
 if router._handle>=0:finish_directory(router,succeeded=False,cacheToDisc=False)
 if not portal:return
 try:
  params=router._params
  from library_index import Reader
  channel=Reader(portal['id']).get('live',str(params.get('sid','')))
  if not channel:return
  selected=dict(start=int(params.get('start',0)),stop=int(params.get('stop',0)),key=str(params.get('event','')),source_key46=str(params.get('source',''))[:128])
  dialog88=launch_standalone(portal,channel,selected if selected['start'] else None)
  if dialog88 and dialog88._tune88:
   from guide_playback import request,handoff,player_state
   handoff(router,portal,request(portal,channel,player_state()))
  return dialog88
 except (ValueError,TypeError):xbmcgui.Dialog().notification('XCMate',tr(36107))

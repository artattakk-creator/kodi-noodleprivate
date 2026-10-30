"""Owned child programme dialog; preserves parent grid, player and focus.

Callbacks queue intent. Only the parent's pump opens a child, with an exact
parent dialog identity check. Never close foreign modals or use Container.Update.
"""
import os,threading,time
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

def show(portal,channel,event=None,parent=None):
 if not permitted(parent):xbmcgui.Dialog().notification('XCMate',tr(36105));return
 dialog=ProgrammeWindow46('XCMateProgramme46.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
 dialog.configure(portal,channel,event,parent);dialog.run();return dialog

class ProgrammeWindow46(xbmcgui.WindowXMLDialog):
 def configure(self,portal,channel,event=None,parent=None):
  self.portal,self.channel,self.selected,self.parent=portal,dict(channel),event,parent
  self._owner=threading.get_ident();self._closed=False;self._ready=False;self._shown=False
  self._cancel=threading.Event();self._future=None;self.event=None;self._art_signature=None;self._next=0;self._scroll46=0
 def _gui(self):
  if threading.get_ident()!=self._owner:raise RuntimeError('PROGRAMME_OWNER_THREAD')
 def onInit(self):
  self._gui()
  if self._ready:return
  self._shown=True;self._ready=True;self.getControl(501).setLabel(tr(36101));self.getControl(101).setLabel(tr(36100))
  from menu_icons45 import icon
  self.getControl(881).setImage(icon('back',full=True));self.setFocusId(501)
  self.getControl(103).setText(tr(36106));self.getControl(106).setLabel(tr(36119))
  if not _slots.acquire(blocking=False):self.getControl(103).setText(tr(36107));return
  future=Future();self._future=future
  def work():
   try:
    if not future.set_running_or_notify_cancel():return
    try:
     from programme_events46 import load
     from media_art import local_art,request as request_logos
     value=load(self.portal,self.channel,self.selected)
     value['logo']=local_art(self.channel)['thumb'];request_logos([self.channel])
     future.set_result(value)
    except Exception:future.set_exception(RuntimeError('PROGRAMME_READ_FAILED'))
   finally:_slots.release()
  try:threading.Thread(target=work,name='XCMate-programme-detail46',daemon=True).start()
  except (RuntimeError,MemoryError):_slots.release();self._future=None;self.getControl(103).setText(tr(36107))
 def pump(self):
  self._gui()
  if self._closed:return
  if self.parent is not None and self.parent._closed:self.close();return
  if self._future is not None and self._future.done():
   future=self._future;self._future=None
   try:self.event=future.result()
   except Exception:self.getControl(103).setText(tr(36107))
   else:
    from programme_events46 import summary
    self.getControl(101).setLabel(self.event.get('title') or tr(36102));self.getControl(103).setText(summary(self.event))
    from programme_assets47 import station_image
    logo=self.event.get('logo','');real=station_image(logo)
    self.getControl(111).setImage(logo if real else '');self.getControl(111).setVisible(real)
    self.getControl(112).setLabel('' if real else self.event['channel']);self.getControl(112).setVisible(not real)
  if self.event and time.monotonic()>=self._next:
   self._next=time.monotonic()+.5
   from programme_art46 import cached
   art=cached(self.event);signature=(art.get('image'),art.get('code'),art.get('source'),art.get('match'))
   if signature!=self._art_signature:
    self._art_signature=signature;self.getControl(110).setImage(art.get('image') or self.event['placeholder'])
    from programme_diagnostics59 import message
    self.getControl(104).setLabel(message(self.event,art))
    self.getControl(105).setText(str(art.get('attribution',''))[:500])
   now=time.time();e=self.event;current=e.get('start',0)<=now<e.get('stop',0)
   self.getControl(120).setVisible(current);self.getControl(121).setVisible(current)
   if current:self.getControl(121).setWidth(max(1,int(536*(now-e['start'])/(e['stop']-e['start']))))
 def run(self):
  self._gui();monitor=xbmc.Monitor();start=time.monotonic()
  try:
   if not permitted(self.parent):return
   self.show()
   while not self._closed:
    if self._ready:self.pump()
    elif time.monotonic()-start>10:break
    if monitor.waitForAbort(.05):break
  finally:self.close()
 def onAction(self,action):
  self._gui()
  key=action.getId()
  if key in (9,10,92):self.close()
  elif key in (3,4,5,6):
   self._scroll46=max(0,min(512,self._scroll46+(-1 if key==3 else 1 if key==4 else -10 if key==5 else 10)))
   self.getControl(103).scroll(self._scroll46)
 def onClick(self,cid):
  self._gui()
  if cid==501:self.close()
 def close(self):
  self._gui()
  if self._closed:return
  self._closed=True;self._cancel.set()
  if self._future:self._future.cancel()
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
  selected=dict(start=int(params.get('start',0)),stop=int(params.get('stop',0)),key=str(params.get('event','')))
  return launch_standalone(portal,channel,selected if selected['start'] else None)
 except (ValueError,TypeError):xbmcgui.Dialog().notification('XCMate',tr(36107))

"""Single coalescing local-cache reader; no GUI SQL/files/HTTP."""
import os,threading,time,uuid
_lock=threading.Lock();_wanted={};_done={};_wake=threading.Event();_thread=None
def eligible(art):
 return bool(art and art.get('code') in ('READY','READY_STALE') and art.get('source') not in ('placeholder','') and isinstance(art.get('image'),str) and os.path.isabs(art['image']) and not art.get('url_version55'))
def _work():
 import xbmc
 monitor=xbmc.Monitor()
 while not monitor.abortRequested():
  _wake.wait(.5);_wake.clear()
  with _lock:jobs=list(_wanted.items());_wanted.clear()
  for token,(key,portal,channel,event) in jobs:
   try:
    from programme_events46 import describe
    from programme_art46 import cached
    value=describe(portal,channel,event,event.get('canonical46',''));art=cached(value)
    art=dict(art) if eligible(art) else {}
   except Exception:art={}
   with _lock:
    if token in _done and _done[token][0]==key:_done[token]=(key,art)
class Preview:
 def __init__(self,owner,rect):
  import xbmcgui,xbmcaddon
  self.controls=();self.available=callable(getattr(owner,'addControls',None))
  self.token=uuid.uuid4().hex;self._next=0;self._key=None;self.owner=owner
  if not self.available:return
  x,y,w,h=rect;root=xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('path')
  self.image=xbmcgui.ControlImage(x,y,w,h,'',aspectRatio=2)
  self.logo=xbmcgui.ControlImage(x+w-46,y+h-24,42,20,os.path.join(root,'resources/media/tmdb60/tmdb.png'),aspectRatio=2)
  self.source=xbmcgui.ControlLabel(x,y+h+2,w,22,'','font12','0xFFBEC4CD')
  self.controls=(self.image,self.logo,self.source);owner.addControls(list(self.controls));self.hide()
 def hide(self):
  for control in self.controls:control.setVisible(False)
  with _lock:_wanted.pop(self.token,None);_done.pop(self.token,None)
  self._key=None
 def render(self,portal,channel,event):
  global _thread
  if not self.available or not portal or not event or not channel:self.hide();return
  from programme_events46 import key
  row=dict(channel.extra,sid=str(channel.extra.get('stream_id','')),name=channel.name) if hasattr(channel,'extra') else dict(channel)
  identity=key(portal['id'],row.get('sid',row.get('stream_id','')),event)
  if self._key!=identity:self.hide();self._key=identity
  now=time.monotonic()
  with _lock:
   if now>=self._next:
    self._next=now+.5;_done.setdefault(self.token,(identity,{}));_wanted[self.token]=(identity,dict(portal),row,dict(event))
    while len(_wanted)>2:_wanted.pop(next(iter(_wanted)))
    if _thread is None or not _thread.is_alive():_thread=threading.Thread(target=_work,name='XCMate-local-preview67',daemon=True);_thread.start()
    _wake.set()
   current=_done.get(self.token,(None,{}));art=current[1] if current[0]==identity else {}
  real=eligible(art)
  if real:self.image.setImage(art['image'])
  self.image.setVisible(real);self.logo.setVisible(real and str(art.get('source','')).startswith('tmdb'))
  self.source.setLabel(('TMDB' if str(art.get('source','')).startswith('tmdb') else 'TVmaze' if str(art.get('source','')).startswith('tvmaze') else 'XMLTV' if art.get('source')=='xmltv_event' else 'Provider')+(' · Serienbild' if art.get('image_scope57')=='series_fallback' else '') if real else '')
  self.source.setVisible(real)

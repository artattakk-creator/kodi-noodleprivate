"""Owned EPG-detail context menu; user confirmation is the only mapping writer."""
import time
import xbmc,xbmcgui,xbmcaddon

def open(parent):
 from programme_mapping85 import current,set_mapping,namespace
 if not __import__('programme_window46').permitted(parent) or getattr(parent,'_closed',False):return
 event=parent.event
 binding=namespace(event or {})
 if not event or not event.get('title'):return
 state=current(event)
 choices=['Zuordnung ändern' if state and not state.get('hidden') else 'Serie/Bild zuweisen','Automatische Zuordnung verwenden','Kein Serienbild verwenden' if state and state.get('id') else 'Bildvorschlag ausblenden']
 option=xbmcgui.Dialog().contextmenu(choices)
 if option<0:return
 try:
  if option==1:set_mapping(event,automatic=True)
  elif option==2:set_mapping(event,hidden=True)
  else:
   from series_requests85 import request,result,cancel
   nonce=request(event)
   if not nonce:return
   progress=xbmcgui.DialogProgress();progress.create('Serie/Bild zuweisen','Serien werden gesucht …')
   monitor=xbmc.Monitor();answer=None;deadline=time.monotonic()+30
   try:
    while time.monotonic()<deadline and not monitor.abortRequested() and not progress.iscanceled():
     answer=result(nonce)
     if answer:break
     if monitor.waitForAbort(.05):break
   finally:progress.close();cancel(nonce)
   if not answer:return
   if answer.get('code')!='READY' or not answer.get('rows'):
    xbmcgui.Dialog().ok('Serie/Bild zuweisen','Momentan sind keine überprüften Serienkandidaten verfügbar. Senderlogo und EPG bleiben erhalten.');return
   if answer.get('binding')!=binding or namespace(event)!=binding:return
   dialog=SeriesWindow85('XCMateSeries85.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p');dialog.configure(answer['rows'],state,event);dialog.run()
   if dialog.chosen is None:return
   if namespace(event)!=binding or getattr(parent,'_closed',False):return
   set_mapping(event,dialog.chosen)
  # Request a new proof under the new mapping policy; do not bless old pixels.
  parent._art68={};parent._art_signature=None;parent._next=0
  __import__('programme_requests68').request(event,priority=True)
 except (OSError,ValueError,TypeError,TimeoutError):
  xbmcgui.Dialog().ok('Zuordnung nicht gespeichert','Die Zuordnung konnte nicht dauerhaft und geprüft gespeichert werden. Speicher und Schreibrechte prüfen. Eine erfolgreiche dauerhafte Speicherung wurde nicht bestätigt.')

class SeriesWindow85(xbmcgui.WindowXMLDialog):
 def configure(self,rows,state=None,event=None):
  self.rows=rows[:8];self.chosen=None;self.position=-1;self.state=state or {};self.event=event;self.portal={'id':str((event or {}).get('pid',''))};self._closed=False;self._ready=False;self._nonce85=None;self._requested85=set()
 def run(self):
  monitor=xbmc.Monitor();self.show();deadline=time.monotonic()+5
  try:
   while not self._closed and not monitor.abortRequested():
    if self._ready:self.pump()
    elif time.monotonic()>deadline:break
    if monitor.waitForAbort(.05):break
  finally:self.close()
 def close(self):
  if self._closed:return
  self._closed=True
  __import__('programme_lifecycle69').unregister(self)
  if self._nonce85:__import__('series_requests85').cancel(self._nonce85)
  super().close()
 def pump(self):
  if __import__('programme_lifecycle69').pulse(self):return
  from series_requests85 import request,result,cancel
  position=self.getControl(200).getSelectedPosition()
  if 0<=position<len(self.rows):
   row=self.rows[position]
   if self.event and not row.get('thumb85') and position not in self._requested85:
    if self._nonce85:cancel(self._nonce85)
    self._requested85.add(position);self._nonce85=request(self.event,thumbnail=row)
  answer=result(self._nonce85) if self._nonce85 else None
  if answer:
   cancel(self._nonce85);self._nonce85=None
   if answer.get('code')!='THUMB' or answer.get('binding')!=__import__('programme_mapping85').namespace(self.event):return
   for candidate in answer.get('rows',[]):
    for i,row in enumerate(self.rows):
     if row['source']==candidate.get('source') and row['id']==candidate.get('id') and candidate.get('thumb85'):
      row['thumb85']=candidate['thumb85'];self.getControl(200).getListItem(i).setArt({'thumb':candidate['thumb85'],'icon':candidate['thumb85']})
 def onInit(self):
  __import__('programme_lifecycle69').register(self,'DETAIL')
  self.getControl(101).setLabel('Serie/Bild zuweisen · Auswahl ausdrücklich bestätigen')
  items=[]
  for row in self.rows:
   label=row['title']+' · '+str(row['year'])+' · '+('/'.join(row.get('country') or []) or 'Land nicht angegeben')
   status='manuell' if self.state.get('source')==row['source'] and self.state.get('id')==row['id'] else 'Vorschlag'
   item=xbmcgui.ListItem(label=label+' · '+status,label2=row.get('original',''))
   item.setProperty('Overview85',row.get('original','')+'\n'+row.get('overview','')+'\n\n'+row['source'].upper()+' · ID '+str(row['id'])+' · '+status)
   if row.get('thumb85'):item.setArt({'thumb':row['thumb85'],'icon':row['thumb85']})
   items.append(item)
  self.getControl(200).addItems(items);self.setFocusId(200);self._ready=True;self.paint()
 def paint(self):
  position=self.getControl(200).getSelectedPosition()
  if position==self.position or not 0<=position<len(self.rows):return
  self.position=position;row=self.rows[position]
 def onAction(self,action):
  if action.getId() in (9,10,92):self.close()
  elif action.getId() in (3,4,5,6):self.position=-1
 def onClick(self,ident):
  if ident==501:self.close()
  elif ident==201:
   pos=self.getControl(200).getSelectedPosition()
   if 0<=pos<len(self.rows):self.chosen=dict(self.rows[pos]);self.close()
  else:self.paint()
 def onFocus(self,ident):self.paint()

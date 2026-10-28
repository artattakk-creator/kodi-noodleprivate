"""Owned mapping dialog with reversible, memory-only preview in the real grid."""
from concurrent.futures import Future
import threading
import time
import xbmc
import xbmcaddon
import xbmcgui
_slots=threading.BoundedSemaphore(1)


def request(parent):
    if not parent.rows or parent._loading or parent._leaving:return
    parent._mapping_request48=True


def open_pending(parent):
    if not getattr(parent,'_mapping_request48',False):return
    parent._mapping_request48=False
    from programme_window46 import permitted
    if parent._closed or parent._leaving or not permitted(parent):return
    parent._generation+=1
    if parent._pending_future is not None:parent._pending_future.cancel()
    parent._pending_future=parent._pending_apply=None
    dialog=MappingWindow48('XCMateMapping48.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
    dialog.configure(parent);dialog.run()


class MappingWindow48(xbmcgui.WindowXMLDialog):
    def configure(self,parent):
        self.parent=parent;self.portal=parent.portal;self.channel=dict(parent.rows[parent.row]['channel'])
        self.owner=threading.get_ident();self._closed=False;self._ready=False;self._shown=False
        self.cancel=threading.Event();self.future=None;self.apply=None
        self.source=None;self.candidate=None;self.query='';self.offset=0;self.rows=[];self.previewed=False;self.saved=False
        self.original={k:getattr(parent,k) for k in ('rows','total','groups','row','offset','cursor','origin','category','_focus_zone','_header')}
        self._parent_focus48=parent.getFocusId()
        self._saving53=False;self.scroll53=0;self.detail_offset53=0
    def _gui(self):
        if threading.get_ident()!=self.owner:raise RuntimeError('MAPPING_OWNER_THREAD')
    def _submit(self,call,apply):
        if self.future or not _slots.acquire(blocking=False):return
        future=Future();self.future=future;self.apply=apply
        def work():
            try:
                if not future.set_running_or_notify_cancel():return
                try:future.set_result(call())
                except Exception:future.set_exception(RuntimeError('LOCAL_READ_UNAVAILABLE'))
            finally:_slots.release()
        try:threading.Thread(target=work,name='XCMate-map48',daemon=True).start()
        except (RuntimeError,MemoryError):_slots.release();self.future=None
        self.getControl(103).setText('Lokale EPG-Daten werden gelesen …')
    def onInit(self):
        self._gui();self._ready=True
        self.getControl(101).setLabel('EPG zuweisen · '+str(self.channel['name']))
        for cid,label in ((401,'Quelle wählen'),(402,'Kanal suchen'),(403,'Weitere Kanäle'),(404,'Vorschau im Raster'),(405,'Speichern'),(406,'Abbrechen'),(407,'Vorige Kanäle'),(408,'Sendungen hoch'),(409,'Sendungen runter'),(410,'Nächster Zeitraum')):
            self.getControl(cid).setLabel(label)
        self.getControl(405).setEnabled(False);self.getControl(404).setEnabled(False)
        self.setFocusId(401)
        self.getControl(103).setText('Quelle wählen. Erst „Speichern“ ändert die Zuordnung.')
    def _choose_source(self):
        from epg_binding48 import sources
        def ready(rows):
            from menu_icons45 import select
            choice=select(xbmcgui.Dialog(),'EPG-Anbieter wählen',[r['name'] for r in rows],default='database')
            if not 0<=choice<len(rows):return
            self.source=rows[choice];self.query='';self.offset=0;self._channels()
        self._submit(lambda:sources(self.portal),ready)
    def _channels(self):
        if not self.source:return
        from epg_binding48 import channels
        def ready(rows):
            self.getControl(900).setVisible(True)
            if not rows and self.offset:
                self.offset=max(0,self.offset-100);self.getControl(103).setText('Keine weiteren Kanäle. Suche oder vorige Seite verwenden.');return
            self.rows=rows;self.candidate=None;self.previewed=False
            self.getControl(405).setEnabled(False);self.getControl(404).setEnabled(False)
            control=self.getControl(200);control.reset()
            control.addItems([xbmcgui.ListItem(r['name'],label2='EPG-ID: '+r['id']) for r in rows])
            self.getControl(103).setText(self.source['name']+' · '+str(len(rows))+' Kanäle · nur lokal gespeichert. Kein Import.')
            self.setFocusId(200 if rows else 401)
        source=self.source['id'];query=self.query;offset=self.offset
        self._submit(lambda:channels(self.portal['id'],source,query,offset),ready)
    def _preview(self):
        if not self.candidate or not self.source:return
        candidate=dict(self.candidate);source=self.source['id'];parent=self.parent
        original_rows=list(self.original['rows']);offset=self.detail_offset53
        def load():
            from epg_sources import configuration
            from epg_binding48 import preview
            from guide_grid_data import page
            mappings=preview(configuration(self.portal['id'])['mappings'],self.channel['sid'],candidate['id'],source)
            value=page(self.portal,self.original['offset'],self.original['origin'],self.original['category'],None,mappings48=mappings)
            from local_epg import window
            start=self.original['origin']+offset*3*3600
            detail=window(self.portal['id'],[self.channel],mappings,start,start+2*86400,limit=96)
            value['details53']=list((detail or {}).get(candidate['id'],[]))
            return value
        def ready(value):
            if self.parent._closed:return
            selected=next((row for row in value['rows'] if str(row['channel']['sid'])==str(self.channel['sid'])),None)
            if selected is None:return
            parent.rows=[selected if str(row['channel']['sid'])==str(self.channel['sid']) else row for row in original_rows]
            zone=parent._focus_zone;parent._focus_zone='preview48'
            parent._preview53=True
            try:parent._render()
            finally:parent._focus_zone=zone;parent._preview53=False
            parent.getControl(102).setLabel('VORSCHAU · '+self.source['name']+' · '+candidate['id']+' · noch nicht gespeichert')
            self.getControl(900).setVisible(True)
            lines=[]
            for event in value.get('details53',[])[:96]:
                lines.append(time.strftime('%d.%m. %H:%M',time.localtime(event['start_timestamp']))+' – '+time.strftime('%H:%M',time.localtime(event['stop_timestamp']))+'  '+str(event['name']))
                if event.get('descr'):lines.append(str(event['descr'])[:2000])
                lines.append('')
            self.getControl(301).setText('\n'.join(lines) or 'Keine gespeicherten Sendungen in diesem Zeitraum.')
            self.scroll53=0;self.getControl(301).scroll(0)
            self.previewed=True;self.getControl(405).setEnabled(True)
            count=sum(len(row['events']) for row in parent.rows if str(row['channel']['sid'])==str(self.channel['sid']))
            self.getControl(103).setText('Vorschau: '+str(count)+' gespeicherte Sendungen. Speichern oder Abbrechen.' if count else 'Keine gespeicherten Sendungen in diesem Zeitfenster. Kein Import. Zuordnung nur auf Wunsch speichern.')
            self.setFocusId(200 if self.rows else 401)
        self._submit(load,ready)
    def pump(self):
        self._gui()
        if self._closed:return
        if self.future and self.future.done():
            future,apply=self.future,self.apply;self.future=self.apply=None
            if future.cancelled():return
            self._saving53=False
            try:value=future.result()
            except Exception:self.getControl(103).setText('Lokaler EPG-Zugriff nicht verfügbar. Zuordnung unverändert.')
            else:apply(value)
    def onClick(self,cid):
        self._gui()
        if cid==406:self.close();return
        if self.future:return
        if cid==401:self._choose_source()
        elif cid==402 and self.source:
            query=xbmcgui.Dialog().input('EPG-Kanalname oder EPG-ID',defaultt=self.query)
            self.query=str(query)[:160];self.offset=0;self._channels()
        elif cid==403 and self.source:self.offset+=100;self._channels()
        elif cid==407 and self.source:self.offset=max(0,self.offset-100);self._channels()
        elif cid in (408,409):
            self.scroll53=max(0,self.scroll53+(-8 if cid==408 else 8));self.getControl(301).scroll(self.scroll53)
        elif cid==410 and self.candidate:
            self.detail_offset53=(self.detail_offset53+1)%16;self._preview()
        elif cid==200:
            pos=self.getControl(200).getSelectedPosition()
            if 0<=pos<len(self.rows):
                self.candidate=self.rows[pos];self.detail_offset53=0;self.previewed=False;self.getControl(405).setEnabled(False)
                self.getControl(404).setEnabled(True);self._preview()
        elif cid==404:self._preview()
        elif cid==405 and self.previewed:
            from epg_binding48 import save
            # A single explicit atomic configuration write is linearized on
            # the owner: Back cannot race a queued Save after the panel closed.
            try:ok=save(self.portal,self.channel['sid'],self.candidate['id'],self.source['id'])
            except (OSError,ValueError):
                self.getControl(103).setText('Zuordnung nicht gespeichert. Quelle und Schreibrechte prüfen.');return
            if ok:self.saved=True;self.close()
    def onAction(self,action):
        if action.getId() in (9,10,92):self.close()
    def run(self):
        self._gui();monitor=xbmc.Monitor();started=time.monotonic()
        try:
            self._shown=True;self.show()
            while not self._closed and not self.parent._closed:
                if self._ready:self.pump()
                elif time.monotonic()-started>10:break
                if monitor.waitForAbort(.05):break
        finally:
            self.close()
            if not self.parent._closed:
                if not self.saved:
                    for key,value in self.original.items():setattr(self.parent,key,value)
                    self.parent._render();self.parent.setFocusId(self._parent_focus48)
                else:self.parent._load(background=True)
    def close(self):
        self._gui()
        if self._closed:return
        if self._saving53 and self.future is not None:
            self.getControl(103).setText('Explizite Zuordnung wird gespeichert. Bitte kurz warten.');return
        self._closed=True;self.cancel.set()
        if self.future:self.future.cancel()
        if self._shown:super().close()

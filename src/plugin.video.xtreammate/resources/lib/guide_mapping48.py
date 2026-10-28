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
        self.getControl(103).setLabel('Lokale EPG-Daten werden gelesen …')
    def onInit(self):
        self._gui();self._ready=True
        self.getControl(101).setLabel('EPG zuweisen · '+str(self.channel['name']))
        for cid,label in ((401,'Quelle wählen'),(402,'Kanal suchen'),(403,'Weitere Kanäle'),(404,'Vorschau im Raster'),(405,'Speichern'),(406,'Abbrechen')):
            self.getControl(cid).setLabel(label)
        self.getControl(405).setEnabled(False);self.getControl(404).setEnabled(False)
        self.setFocusId(401)
        self.getControl(103).setLabel('Quelle wählen. Erst „Speichern“ ändert die Zuordnung.')
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
            self.rows=rows;self.candidate=None;self.previewed=False
            self.getControl(405).setEnabled(False);self.getControl(404).setEnabled(False)
            control=self.getControl(200);control.reset()
            control.addItems([xbmcgui.ListItem(r['name'],label2='EPG-ID: '+r['id']) for r in rows])
            self.getControl(103).setLabel(self.source['name']+' · '+str(len(rows))+' Kanäle · nur lokal gespeichert. Kein Import.')
            self.setFocusId(200 if rows else 401)
        source=self.source['id'];query=self.query;offset=self.offset
        self._submit(lambda:channels(self.portal['id'],source,query,offset),ready)
    def _preview(self):
        if not self.candidate or not self.source:return
        candidate=dict(self.candidate);source=self.source['id'];parent=self.parent
        def load():
            from epg_sources import configuration
            from epg_binding48 import preview
            from guide_grid_data import page
            mappings=preview(configuration(self.portal['id'])['mappings'],self.channel['sid'],candidate['id'],source)
            return page(self.portal,parent.offset,parent.origin,parent.category,None,mappings48=mappings)
        def ready(value):
            if self.parent._closed:return
            parent.rows=value['rows']
            zone=parent._focus_zone;parent._focus_zone='preview48'
            try:parent._render()
            finally:parent._focus_zone=zone
            parent.getControl(102).setLabel('VORSCHAU · '+self.source['name']+' · '+candidate['id']+' · noch nicht gespeichert')
            self.getControl(900).setVisible(False)
            self.previewed=True;self.getControl(405).setEnabled(True)
            count=sum(len(row['events']) for row in parent.rows if str(row['channel']['sid'])==str(self.channel['sid']))
            self.getControl(103).setLabel('Vorschau: '+str(count)+' gespeicherte Sendungen. Speichern oder Abbrechen.' if count else 'Keine gespeicherten Sendungen in diesem Zeitfenster. Kein Import. Zuordnung nur auf Wunsch speichern.')
            self.setFocusId(405)
        self._submit(load,ready)
    def pump(self):
        self._gui()
        if self.future and self.future.done():
            future,apply=self.future,self.apply;self.future=self.apply=None
            if future.cancelled():return
            try:value=future.result()
            except Exception:self.getControl(103).setLabel('Lokaler EPG-Zugriff nicht verfügbar. Zuordnung unverändert.')
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
        elif cid==200:
            pos=self.getControl(200).getSelectedPosition()
            if 0<=pos<len(self.rows):
                self.candidate=self.rows[pos];self.previewed=False;self.getControl(405).setEnabled(False)
                self.getControl(404).setEnabled(True);self._preview()
        elif cid==404:self._preview()
        elif cid==405 and self.previewed:
            from epg_binding48 import save
            def saved(ok):
                if ok:self.saved=True;self.close()
            self._submit(lambda:save(self.portal,self.channel['sid'],self.candidate['id'],self.source['id']),saved)
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
        self._closed=True;self.cancel.set()
        if self.future:self.future.cancel()
        if self._shown:super().close()

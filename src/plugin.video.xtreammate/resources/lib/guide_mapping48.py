"""Shared mapping controller with reversible grid and Mini-EPG view adapters."""
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


def request_mini(parent):
    from mapping_context96 import mini_channel
    channel=mini_channel(parent)
    if channel is None:return False
    from programme_window46 import channel_row
    parent._mapping_request96=channel_row(channel)
    return True


def open_pending(parent):
    mini=getattr(parent,'_mapping_request96',None)
    if not mini and not getattr(parent,'_mapping_request48',False):return
    parent._mapping_request48=False;parent._mapping_request96=None
    from programme_window46 import permitted
    if parent._closed or getattr(parent,'_leaving',False) or not permitted(parent):return
    from mapping_context96 import GridAdapter,MiniAdapter,mini_channel
    if mini:
        channel=mini_channel(parent)
        if channel is None or str(channel.extra.get('stream_id'))!=mini['sid']:return
        adapter=MiniAdapter(parent,channel)
    else:
        parent._generation+=1
        if parent._pending_future is not None:parent._pending_future.cancel()
        parent._pending_future=parent._pending_apply=None
        adapter=GridAdapter(parent)
    dialog=MappingWindow48('XCMateMapping48.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
    dialog.configure(parent,adapter);dialog.run()


class MappingWindow48(xbmcgui.WindowXMLDialog):
    def configure(self,parent,adapter=None):
        from mapping_context96 import GridAdapter
        self.adapter96=adapter or GridAdapter(parent)
        self.parent=parent;self.portal=self.adapter96.portal;self.channel=self.adapter96.channel
        self.owner=threading.get_ident();self._closed=False;self._ready=False;self._shown=False
        self.cancel=threading.Event();self.future=None;self.apply=None
        self.source=None;self.candidate=None;self.query=str(self.channel.get('name') or self.channel.get('epg_channel_id') or '')[:160];self.offset=0;self.rows=[];self.previewed=False;self.saved=False
        self.original=self.adapter96.original
        self._parent_focus48=self.adapter96.focus
        self._saving53=False;self.scroll53=0;self.detail_offset53=0
        self._entry482=True;self._switch482=False;self._cold482=False;self._proof482=None
        self._job_stop482=None;self._job_started482=0;self._job_timedout482=False
        from epg_candidate53 import Candidates
        self.cold53=Candidates()
    def _gui(self):
        if threading.get_ident()!=self.owner:raise RuntimeError('MAPPING_OWNER_THREAD')
    def _submit(self,call,apply):
        if self.future or not _slots.acquire(blocking=False):return False
        future=Future();self.future=future;self.apply=apply
        def work():
            value=None;error=None
            try:
                if not future.set_running_or_notify_cancel():return
                try:value=call()
                except Exception as exc:
                    from epg_binding48 import MappingSaveError
                    from mapping_search482 import MappingReadError,failure
                    error=exc if isinstance(exc,(MappingSaveError,MappingReadError)) else MappingReadError(failure(exc))
            finally:_slots.release()
            if error is not None:future.set_exception(error)
            else:future.set_result(value)
        try:threading.Thread(target=work,name='XCMate-map48',daemon=True).start()
        except (RuntimeError,MemoryError):_slots.release();self.future=None;return False
        return True
    def _status482(self,code,text=None,busy=False):
        messages={'MAPPING_BUSY':'Andere EPG-Abfrage läuft. Bitte erneut versuchen.',
                  'DB_BUSY':'EPG-Datenbank belegt. Bitte erneut versuchen.',
                  'SOURCE_TIMEOUT':'Quelle antwortet zu langsam. Bitte erneut laden.',
                  'SOURCE_UNAVAILABLE':'Quelle nicht erreichbar. Bitte erneut versuchen.',
                  'SOURCE_INVALID':'Quelldaten nicht lesbar. Andere Quelle prüfen.',
                  'SOURCE_LIMIT':'Quelle überschreitet das begrenzte Lesebudget.',
                  'NO_LOCAL_INDEX':'Kein lokaler Kanalindex. „Quelle laden“ ist optional.',
                  'NO_MATCH':'Kein lokaler Treffer. Suchbegriff oder Quelle ändern.',
                  'NO_PROGRAMMES':'Keine Sendungen gefunden. Quelle oder Zeitraum ändern.',
                  'MAPPING_CANCELLED':'Abfrage abgebrochen. Erneute Auswahl ist möglich.'}
        self._state482=code
        self.getControl(103).setText((text or messages.get(code,'Quelle und Auswahl prüfen.'))+'\n('+code+')')
        self.getControl(104).setVisible(busy)
        self.getControl(105).setLabel(str((self.source or {}).get('name',''))[:72])
        if code=='NO_LOCAL_INDEX':
            self.getControl(404).setLabel('Quelle laden');self.getControl(404).setEnabled(True)
        elif self.source and code in ('DB_BUSY','SOURCE_TIMEOUT','SOURCE_UNAVAILABLE','SOURCE_INVALID','SOURCE_LIMIT','MAPPING_BUSY','MAPPING_CANCELLED'):
            self.getControl(404).setLabel('Erneut laden');self.getControl(404).setEnabled(True)
    def _launch482(self,phase,call,apply,stop=None):
        if self.future:
            self._status482('MAPPING_BUSY',busy=not self._job_timedout482);return False
        self._job_stop482=stop or threading.Event();self._job_timedout482=False
        self._job_started482=time.monotonic()
        accepted=self._submit(call,apply)
        if accepted is False:
            self._status482('MAPPING_BUSY');return False
        if self.future:
            self._status482(phase,{'SOURCES_LOADING':'EPG-Quellen werden lokal gelesen …',
                'CHANNELS_LOADING':'Lokale Sendervorschläge werden gelesen …',
                'SOURCE_COLD_LOAD':'Quelle wird begrenzt geladen …',
                'PREVIEW_LOADING':'Lade Vorschau …'}[phase],busy=True)
        return True
    def onInit(self):
        self._gui();self._ready=True
        self.getControl(101).setLabel('EPG zuweisen · '+str(self.channel['name']))
        for cid,label in ((401,'Quelle wählen'),(402,'Kanal suchen'),(403,'Weitere Kanäle'),(404,self.adapter96.preview_label),(405,'Speichern'),(406,'Abbrechen'),(407,'Vorige Kanäle'),(408,'Sendungen hoch'),(409,'Sendungen runter'),(410,'Nächster Zeitraum')):
            self.getControl(cid).setLabel(label)
        self.getControl(405).setEnabled(False);self.getControl(404).setEnabled(False)
        self.getControl(104).setVisible(False);self.getControl(105).setLabel('')
        self.setFocusId(401)
        self.getControl(103).setText('Quelle wählen. Erst „Speichern“ ändert die Zuordnung.')
    def _choose_source(self):
        from mapping_search482 import source_rows
        self._entry482=False
        def ready(rows):
            from menu_icons45 import select
            reasons={'DB_BUSY':'Datenbank belegt','SOURCE_TIMEOUT':'Abfragezeit überschritten',
                     'SOURCE_UNAVAILABLE':'Daten nicht erreichbar','NO_LOCAL_INDEX':'Index nicht verfügbar'}
            labels=[r['name']+' · lokal: '+(str(r['local_count'])+' Kanäle' if r['local_count'] is not None else reasons.get(r['local_code'],'Index nicht verfügbar')) for r in rows]
            choice=select(xbmcgui.Dialog(),'EPG-Anbieter wählen',labels,default='database')
            if not 0<=choice<len(rows):
                self._status482('SOURCE_SELECT','Keine Quelle gewählt. Bitte „Quelle wählen“ verwenden.');return
            self.source=rows[choice];self.offset=0;self._cold482=False;self._channels()
        self._launch482('SOURCES_LOADING',lambda:source_rows(self.portal),ready)
    def _channels(self):
        if not self.source:return
        # A failed source/search reload must never leave Save authorized by
        # a preview belonging to the previously selected source/channel.
        self.candidate=None;self.previewed=False;self._proof482=None
        self.rows=[];self.getControl(200).reset()
        self.getControl(405).setEnabled(False);self.getControl(404).setEnabled(False)
        from epg_binding48 import channels
        def ready(rows):
            self.getControl(900).setVisible(True)
            if not rows and self.offset:
                self.offset=max(0,self.offset-100);self.getControl(103).setText('Keine weiteren Kanäle. Suche oder vorige Seite verwenden.');return
            self.rows=rows;self.candidate=None;self.previewed=False
            self.getControl(405).setEnabled(False);self.getControl(404).setEnabled(False)
            control=self.getControl(200);control.reset()
            control.addItems([xbmcgui.ListItem(r['name'],label2='EPG-ID: '+r['id']) for r in rows])
            self._status482('CHANNELS_READY',str(len(rows))+' lokale Treffer. OK zeigt die Vorschau.') if rows else self._status482('NO_MATCH')
            self.setFocusId(200 if rows else 401)
        source=self.source['id'];query=self.query;offset=self.offset;stop=threading.Event()
        def load():
            if self._cold482 or self.cold53.catalogue is not None and self.cold53.catalogue[0]==source:
                return self.cold53.channels(self.portal,source,query,offset,lambda:self.cancel.is_set() or stop.is_set())
            return channels(self.portal['id'],source,query,offset,strict482=True)
        self._launch482('SOURCE_COLD_LOAD' if self._cold482 else 'CHANNELS_LOADING',load,ready,stop)
    def _preview(self):
        if not self.candidate or not self.source:return
        candidate=dict(self.candidate);source=dict(self.source);offset=self.detail_offset53;stop=threading.Event()
        self.previewed=False;self._proof482=None;self.getControl(405).setEnabled(False)
        self.getControl(404).setLabel(self.adapter96.preview_label)
        def load():
            return self.adapter96.load_preview(candidate,source['id'],offset,self.cold53,lambda:self.cancel.is_set() or stop.is_set())
        def ready(value):
            if self._closed:return
            if not self.source or self.source['id']!=source['id'] or not self.candidate or self.candidate['id']!=candidate['id']:return
            count=self.adapter96.apply_preview(value,source,candidate)
            if count is None:return
            self.getControl(900).setVisible(True)
            lines=[]
            for event in value.get('details53',[])[:96]:
                lines.append(time.strftime('%d.%m. %H:%M',time.localtime(event['start_timestamp']))+' – '+time.strftime('%H:%M',time.localtime(event['stop_timestamp']))+'  '+str(event['name']))
                if event.get('descr'):lines.append(str(event['descr'])[:2000])
                lines.append('')
            self.getControl(301).setText('\n'.join(lines) or 'Keine Sendungen in diesem Zeitraum; Quelle und Kanal prüfen.')
            self.scroll53=0;self.getControl(301).scroll(0)
            valid=bool(count or any(e.get('name') and e.get('start_timestamp',0)<e.get('stop_timestamp',0) for e in value.get('details53',[])))
            self.previewed=valid;self.getControl(405).setEnabled(valid)
            self._proof482=(source['id'],candidate['id']) if valid else None
            self._status482('PREVIEW_READY','Vorschau geprüft. Erst „Speichern“ übernimmt die Zuordnung.') if valid else self._status482('NO_PROGRAMMES')
            self.setFocusId(200 if self.rows else 401)
        self._launch482('PREVIEW_LOADING',load,ready,stop)
    def pump(self):
        self._gui()
        if self._closed:return
        if self._entry482:
            self._entry482=False
            if self.source is None and self.future is None:self._choose_source()
        if self.future and not self.future.done() and not self._saving53 and time.monotonic()-self._job_started482>12:
            self._job_timedout482=True
            if self._job_stop482:self._job_stop482.set()
            self._status482('SOURCE_TIMEOUT')
        if self.future and self.future.done():
            future,apply=self.future,self.apply;self.future=self.apply=None
            self.getControl(104).setVisible(False)
            if self._switch482:
                self._switch482=False;self._choose_source();return
            if self._job_timedout482:return
            if future.cancelled():return
            saving=self._saving53;self._saving53=False
            try:value=future.result()
            except Exception as exc:
                if saving:self._save_error474(getattr(exc,'code','MAPPING_WRITE_FAILED'))
                else:
                    from mapping_search482 import failure
                    self._status482(failure(exc))
            else:apply(value)
    def onClick(self,cid):
        self._gui()
        if cid==406:self.close();return
        if self.future:
            if cid==401 and not self._saving53:
                if self._job_stop482:self._job_stop482.set()
                self._switch482=True;self.previewed=False;self._proof482=None;self.getControl(405).setEnabled(False)
                self._status482('MAPPING_CANCELLED','Abfrage wird beendet; danach Quelle wählen.',busy=True)
            else:self._status482('SAVING' if self._saving53 else 'MAPPING_BUSY','Speichern wird geprüft …' if self._saving53 else None,busy=True)
            return
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
        elif cid==404:
            if not self.candidate and getattr(self,'_state482','')=='NO_LOCAL_INDEX':self._cold482=True;self._channels()
            elif not self.candidate and self.source:self._channels()
            else:self._preview()
        elif cid==405 and self.previewed:
            if self._proof482!=(self.source['id'],self.candidate['id']):
                self.previewed=False;self.getControl(405).setEnabled(False);self._status482('MAPPING_CANCELLED');return
            from epg_binding48 import commit_verified
            identity=self.source['id'];candidate=dict(self.candidate);portal=dict(self.portal);sid=self.channel['sid']
            events=list(self.cold53.selected(identity,candidate['id']))
            def prepare():
                from epg_binding48 import MappingSaveError
                if self.cancel.is_set() or self.parent._closed:raise MappingSaveError('MAPPING_CANCELLED')
                value=self.adapter96.prepare_saved(candidate,identity)
                if self.cancel.is_set() or self.parent._closed:raise MappingSaveError('MAPPING_CANCELLED')
                return value
            def commit():
                try:
                    if self.cancel.is_set() or self.parent._closed:return dict(error='MAPPING_CANCELLED')
                    if events:
                        from epg_candidate53 import publish
                        publish(portal,identity,candidate['id'],candidate.get('name',candidate['id']),events)
                    return commit_verified(portal,sid,candidate['id'],identity,
                        prepare=prepare)
                except (OSError,ValueError,RuntimeError) as exc:
                    return dict(error=getattr(exc,'code','MAPPING_WRITE_FAILED'))
            self._saving53=True
            accepted=self._submit(commit,self._committed474)
            if accepted is False:
                self._saving53=False;self._save_error474('MAPPING_BUSY')
            elif self.future:self._status482('SAVING','Speichern und EPG-Ansicht werden geprüft …',busy=True)
    def _save_error474(self,code):
        safe={'MAPPING_BUSY','MAPPING_CANCELLED','MAPPING_WRITE_FAILED','MAPPING_READBACK_FAILED','MAPPING_RELOAD_FAILED',
              'MAPPING_UI_REFRESH_FAILED','MAPPING_ROLLBACK_UNCONFIRMED','MAPPING_CONFLICT','MAPPING_PROFILE_CHANGED'}
        code=code if code in safe else 'MAPPING_WRITE_FAILED'
        uncertain=code in ('MAPPING_ROLLBACK_UNCONFIRMED','MAPPING_CONFLICT','MAPPING_PROFILE_CHANGED')
        text='Speicherzustand nicht bestätigt. Bitte Diagnose prüfen.' if uncertain else 'Zuordnung nicht gespeichert; vorherige Zuordnung erhalten.'
        self.getControl(103).setText(text+' ('+code+')')
    def _committed474(self,receipt):
        self._saving53=False
        if receipt.get('error'):
            self._save_error474(receipt['error']);return
        from epg_binding48 import rollback_verified,confirm_verified
        try:
            with confirm_verified(receipt):
                self.adapter96.apply_saved(receipt['prepared'])
                self.getControl(103).setText('EPG-Zuordnung gespeichert und geprüft.')
                try:xbmcgui.Dialog().notification('XCMate','EPG-Zuordnung gespeichert und geprüft.',time=3000)
                except RuntimeError:pass
                self.saved=True
        except Exception as exc:
            self.saved=False
            code=getattr(exc,'code','MAPPING_UI_REFRESH_FAILED')
            try:rollback_verified(receipt)
            except Exception as rollback:code=getattr(rollback,'code','MAPPING_ROLLBACK_UNCONFIRMED')
            try:
                restore=getattr(self.adapter96,'restore_saved',None)
                if restore:restore()
                else:self.adapter96.finish(False)
            except Exception:pass
            self._save_error474(code);return
        self.close()
    @staticmethod
    def _retire474(future):
        if future.cancelled():return
        try:receipt=future.result()
        except Exception:return
        if not isinstance(receipt,dict) or receipt.get('error'):return
        try:__import__('epg_binding48').rollback_verified(receipt)
        except (OSError,ValueError,RuntimeError):
            xbmc.log('[XCMate][MAPPING474] UNCONFIRMED_ON_EXIT',xbmc.LOGWARNING)
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
            if self._saving53 and self.future is not None:
                future=self.future;self.future=self.apply=None;self._saving53=False
                self.cancel.set();future.add_done_callback(self._retire474);future.cancel()
            self.close()
            self.adapter96.finish(self.saved)
    def close(self):
        self._gui()
        if self._closed:return
        if self._saving53 and self.future is not None:
            self.getControl(103).setText('Explizite Zuordnung wird gespeichert. Bitte kurz warten.');return
        self._closed=True;self.cancel.set()
        if self.future:self.future.cancel()
        if self._shown:super().close()

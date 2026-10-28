"""One native XML setup flow. All source work runs on a cancellable worker."""
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import xbmcgui
from localization import tr


def _failure_details(exc):
    """Show only preapproved failure reasons: never echo provider URLs or credentials."""
    codes={'XM-SETUP-VERIFY':32782,'XM-SETUP-SAVE-BUSY':32783,'XM-SETUP-RESCAN':32785,'XM-SETUP-ROLLBACK':32786}
    code=getattr(exc,'code',None)
    if code=='XM-SETUP-WORKER-BUSY':return code,tr(36501)
    if isinstance(exc, TimeoutError):return 'XM-SETUP-TIMEOUT',tr(36502)
    if code=='XM-SETUP-EPG-BACKUP':return code,'Bestehenden EPG zuerst über die Sicherungsfunktion verifizieren (BACKUP_VERIFIED). Keine Daten wurden ersetzt.'
    if code in codes: return code,tr(codes[code])
    if isinstance(exc, ValueError):
        reason = str(exc)
        if reason.startswith('Bitte ') or reason.startswith('Die Stalker-MAC-Adresse'):
            return 'XM-SETUP-INPUT', ('Serveradresse und Port kontrollieren. '
                                      'Nur den Server eintragen, keine komplette '
                                      'M3U-/API-URL mit Zugangsdaten.')
        if reason == 'Benutzername und Kennwort sind erforderlich.':
            return 'XM-SETUP-CREDENTIALS', ('Benutzername und Passwort '
                                            'duerfen nicht leer sein.')
        if reason in ('authentication failed', 'provider authentication failed'):
            return 'XM-SETUP-AUTH', ('Anmeldung fehlgeschlagen. Bitte Serveradresse, '
                                     'Benutzername und Passwort kontrollieren.')
        if reason == 'no usable categories':
            return 'XM-SETUP-GROUPS', ('Der Anbieter hat keine nutzbaren Sender-, Film- '
                                      'oder Seriengruppen geliefert. Portal pruefen.')
        if reason == 'select at least one category':
            return 'XM-SETUP-SELECT', 'Bitte mindestens eine Gruppe auswaehlen.'
        if reason == 'no selected content imported':
            return 'XM-SETUP-EMPTY', ('Die ausgewaehlten Gruppen liefern keine '
                                     'importierbaren Inhalte. Andere Gruppe testen.')
        return 'XM-SETUP-DATA', 'Unerwartete Anbieter- oder Importdaten.'
    if isinstance(exc, (OSError, TimeoutError, ConnectionError)):
        return 'XM-SETUP-NET', 'Verbindung oder Dateizugriff fehlgeschlagen.'
    return 'XM-SETUP-OTHER', 'Einrichtungsfehler. Kodi-Protokoll zur Diagnose sichern.'


class _WorkState:
    """Pure data referenced by workers; never retain a native Kodi window."""
    def __init__(self,cancel):
        self.cancel=cancel;self.lock=threading.RLock();self.latest=None
        self.cleanup=lambda:None;self.disposed=False;self.progress_at=time.monotonic()
    def status(self,percent,text):
        with self.lock:
            if not self.cancel.is_set():
                self.latest=(percent,str(text));self.progress_at=time.monotonic()
    def finished(self,future=None):
        with self.lock:
            if not self.cancel.is_set() or self.disposed:return
            self.disposed=True;cleanup=self.cleanup
        cleanup()


class WorkWindow(xbmcgui.WindowXML):
    """Workers return data; only the Window's Python owner touches Kodi GUI.

    run() pumps futures after show()/Monitor.waitForAbort(), including when the
    user presses no key. Completion callbacks may only release non-GUI data.
    """
    def configure_work(self):
        self._owner=threading.get_ident();self._initialized=False
        self._closed=False;self._disposed=False;self.busy=False;self.cancel=threading.Event()
        self._data_state=_WorkState(self.cancel);self._lock=self._data_state.lock
        self._pool=ThreadPoolExecutor(max_workers=1)
        self._future=None;self._apply=None
    def _gui(self):
        if threading.get_ident()!=self._owner: raise RuntimeError('XM-SETUP-GUI-THREAD')
    def status(self,percent,text):
        # Coalesce rather than queue an unbounded event per imported item.
        self._data_state.status(percent,text)
        if threading.get_ident()==self._owner and self._initialized: self._paint_status()
    def _paint_status(self):
        self._gui()
        with self._lock: value=self._data_state.latest;self._data_state.latest=None
        if value and not self._closed:
            percent,text=value
            self.getControl(3).setText(text)
            self.getControl(4).setVisible(True)
            self.getControl(4).setPercent(max(0,min(100,percent)) if percent is not None else 0)
            self._activity_text=text if percent is None else ''
    def work(self,job,apply):
        self._gui()
        if self.busy or self._closed: return
        self.busy=True;self._apply=apply
        self._job_started=time.monotonic();self._data_state.progress_at=self._job_started
        self.working()
        self._future=self._pool.submit(job)
        # This callback never reads or changes a Kodi control or closes a GUI.
        self._future.add_done_callback(self._data_state.finished)
    def working(self): pass
    def _dispose_once(self):
        self._data_state.finished();self._disposed=self._data_state.disposed
    def pump(self):
        self._gui()
        if self._closed or not self._initialized: return
        self._paint_status()
        if self.busy and getattr(self,'_activity_text',''):
            # Activity, not an invented byte/time percentage.
            frame=('·','··','···')[int(__import__('time').monotonic()*2)%3]
            self.getControl(3).setText(self._activity_text+' '+frame)
        future=self._future
        if future is not None and not future.done():
            # Platform DNS cannot be killed safely. Close the responsive UI,
            # cancel cooperatively, retain the worker lease until cleanup.
            now=time.monotonic()
            expired=(now-self._job_started>35 if getattr(self,'stage','')=='discover'
                     else now-self._data_state.progress_at>180)
            if expired:
                from setup_trace import mark
                mark('WORK_TIMEOUT',getattr(getattr(self,'draft',None),'pid',''))
                self.close()
                xbmcgui.Dialog().ok('XCMate',tr(36502)+' [XM-SETUP-TIMEOUT]')
                return
        if future is None or not future.done(): return
        apply=self._apply;self._future=None;self._apply=None;self.busy=False
        try: apply(future.result())
        except InterruptedError: self.close()
        except Exception as exc: self.failed_work(exc)
    def run(self):
        import xbmc
        self._gui();monitor=xbmc.Monitor();started48=__import__('time').monotonic()
        try:
            self.show()  # Kodi dispatches WindowXML.onInit; never call it here.
            while not self._closed:
                if not self._initialized and __import__('time').monotonic()-started48>=10:
                    from setup_trace import mark
                    mark('NATIVE_INIT_TIMEOUT48');self.close();break
                self.pump()
                if monitor.waitForAbort(.05): self.close()
        finally: self.close()
    def failed_work(self,exc):
        self._gui()
        code,message=_failure_details(exc)
        try:
            from utils import warn
            warn('XCMate setup: stage={} code={} type={}'.format(
                getattr(self,'stage','unknown'),code,type(exc).__name__))
        except Exception: pass
        self.status(None,'{} [{}]'.format(message,code))
    def dispose(self): pass
    def close(self):
        self._gui()
        with self._lock:
            if self._closed: return
            self._closed=True;self.cancel.set()
            future=self._future;self._future=None;self._apply=None
        try:
            import xbmcgui
            ident=xbmcgui.getCurrentWindowId()
            if ident>=13000:xbmcgui.Window(10000).setProperty('XCMate.SetupClosedId37',str(ident))
        except (AttributeError,RuntimeError,TypeError):pass
        super().close()
        self._pool.shutdown(wait=False,cancel_futures=True)
        if future is None or future.done(): self._dispose_once()
    def onAction(self,action):
        if action.getId() in (9,10,92): self.close()
        # Native arrows/OK are never replayed.

from wizard_groups51 import GroupRows


class SetupWindow(GroupRows,WorkWindow):
    def configure(self,draft):
        self.configure_work();self.draft=draft;self._data_state.cleanup=draft.dispose;self.kind='live';self.stage='discover';self.result=None
        self._entries=[];self.configure_rows()
    def _show_discover_ui(self):
        self.getControl(2).setLabel(tr(32700))
        for ident in (5,6,10,11,12,13,14,15,16,17,100,101,102):
            self.getControl(ident).setVisible(False)
        self.getControl(18).setVisible(True)
        self.getControl(18).setLabel('Abbrechen')
        self.status(0,'Verbindung und Gruppen werden geprueft ...')
        # The group list is empty until discovery completes. Never focus it.
        self.setFocusId(18)

    def _start_discovery(self):
        self.stage='discover'
        self._show_discover_ui()
        draft=self.draft;cancel=self.cancel.is_set;status=self._data_state.status
        self.work(lambda:draft.discover(cancel,status),self.discovered)

    def onInit(self):
        if self._initialized:return  # Re-activation must not submit discovery twice.
        self._initialized=True
        if self.stage!='discover': self.render();return
        self._start_discovery()

    def dispose(self): self.draft.dispose()

    def failed_work(self,exc):
        if self.stage in ('groups','summary'):
            self.render();self.setFocusId(17)
        super().failed_work(exc)
        if self.stage=='discover':
            self.stage='failed'
            for ident in (5,6,10,11,12,13,14,15,16,100,101,102):
                self.getControl(ident).setVisible(False)
            self.getControl(17).setLabel('Erneut versuchen')
            self.getControl(17).setVisible(True)
            self.getControl(18).setLabel('Abbrechen')
            self.getControl(18).setVisible(True)
            self.setFocusId(17)

    def discovered(self,result):
        self._mark51('SETUP_DISCOVER_DONE',total=sum(len(v) for v in self.draft.categories.values()))
        self.stage='groups'
        self.kind=next((kind for kind in ('live','vod','series')
                        if self.draft.categories.get(kind)), 'live')
        self.render()
        self.setFocusId(self.list_id if self._entries else 17)
    def working(self):
        for ident in (10,11,12,13,14,15,16,17,100,101,102): self.getControl(ident).setVisible(False)
        self.getControl(18).setVisible(True);self.setFocusId(18)
    def _selection_status(self):
        self.getControl(5).setLabel(self._row_labels[32780].format(len(self.draft.selected[self.kind]),len(self._entries)))
    @property
    def list_id(self): return 100+('live','vod','series').index(self.kind)
    def render(self):
        self._gui()
        groups=self.stage=='groups'
        for ident,label in ((10,32701),(11,32702),(12,32703),(13,32704),(14,32705),(15,32706),(16,32710),(17,32709 if self.stage=='summary' else 32707),(18,32708)):
            self.getControl(ident).setLabel(tr(label))
            self.getControl(ident).setVisible(groups or ident in (16,17,18))
        self.setProperty('XCMate.SetupKind',self.kind if groups else '')
        self._entries=self.draft.categories[self.kind]
        if groups: self._groups()
        for number,kind in enumerate(('live','vod','series')):
            self.getControl(100+number).setVisible(groups and kind==self.kind and bool(self._entries))
        self.getControl(5).setVisible(groups);self.getControl(6).setVisible(groups and not self._entries)
        self.getControl(6).setLabel(tr(32781))
        self.getControl(3).setHeight(80 if groups else 240)
        self.getControl(4).setPosition(45,170 if groups else 330)
        if groups:
            self._render_status();self._selection_status()
        else:
            r=self.draft.report
            lines=[self.draft.data['name'],tr(32714,r['live'],r['vod'],r['series'],r['epg'])]
            for source in r['sources']: lines.append(tr(32748)+': '+str(source))
            if r['warnings']: lines.append(tr(32752,len(r['warnings'])))
            self.status(100,'\n'.join(lines));self.setFocusId(17)
    def choose_epg(self):
        from epg_sources import PRESET_FEEDS
        import uuid
        choices=[(tr(32717),'provider')]
        if self.draft.data.get('epg_url'): choices.append((tr(32718),'configured'))
        choices.extend((title,uri) for key,title,uri in PRESET_FEEDS)
        choices.append((tr(32719),'custom'))
        selected=xbmcgui.Dialog().multiselect(tr(32706),[c[0] for c in choices],preselect=[i for i,(_,uri) in enumerate(choices) if (uri=='provider' and self.draft.provider_epg) or any(s['uri']==uri for s in self.draft.epg_sources)])
        if selected is None: return
        sources=[];self.draft.provider_epg=False
        for i in selected:
            title,uri=choices[i]
            if uri=='provider': self.draft.provider_epg=True;continue
            if uri=='configured': uri=self.draft.data['epg_url']
            if uri=='custom': uri=xbmcgui.Dialog().input(tr(32719)).strip()
            if not uri: continue
            from urllib.parse import urlsplit
            if urlsplit(uri).scheme not in ('http','https'): raise ValueError('invalid XMLTV URL')
            sources.append(dict(id=uuid.uuid4().hex,name=title,uri=uri,local=False,enabled=True))
        self.draft.epg_sources=sources;self.draft.scanned=False
        self.status(0,str(len(sources)+int(self.draft.provider_epg))+' · '+tr(32706))
    def onClick(self,controlId):
        if controlId==18: self.close();return
        if self.busy: return
        if self.stage=='failed':
            if controlId==17: self._start_discovery()
            return
        try:
            if self.stage=='groups':
                if controlId in (10,11,12):
                    self.kind=('live','vod','series')[controlId-10]
                    self.render()
                    self.setFocusId(self.list_id if self._entries else 17)
                elif controlId in (100,101,102):
                    if controlId!=self.list_id:return
                    pos=self.getControl(self.list_id).getSelectedPosition()
                    if 0<=pos<(self._rendered[self.kind] or 0):
                        cid=str(self._entries[pos]['category_id']);selected=self.draft.selected[self.kind]
                        selected.remove(cid) if cid in selected else selected.add(cid)
                        self.draft.scanned=False
                        self._item_state(self.getControl(self.list_id).getListItem(pos),cid in selected)
                        self._selection_status()
                        self._mark51('GROUP_TOGGLE',kind=self.kind,total=len(selected))
                elif controlId in (13,14):
                    self.bulk_selection(controlId==13)
                elif controlId==15: self.choose_epg()
                elif controlId==16: self.close()
                elif controlId==17:
                    self.status(0,tr(32713))
                    draft=self.draft;cancel=self.cancel.is_set;status=self._data_state.status
                    self.work(lambda:draft.scan(cancel,status),self.scanned)
            elif self.stage=='summary' and controlId==16:
                self.stage='groups';self.render();self.setFocusId(self.list_id if self._entries else 17)
            elif self.stage=='summary' and controlId==17:
                self.status(0,tr(32716));draft=self.draft;cancel=self.cancel.is_set
                self._mark51('SETUP_SAVE_BEGIN')
                status=self._data_state.status
                self.work(lambda:draft.save(cancel,status),self.saved)
        except (ValueError,OSError) as exc: self.status(0,tr(32743,type(exc).__name__))
    def onAction(self,action):
        if action.getId()==117 and not self.busy and self.stage=='groups' and self.draft.data['type']=='m3u':
            pos=self.getControl(self.list_id).getSelectedPosition()
            if not 0<=pos<len(self._entries): return
            target=xbmcgui.Dialog().select(tr(32736),[tr(32701),tr(32702),tr(32703)])
            if target<0: return
            group=self._entries[pos];cid=str(group['category_id']);kind=('live','vod','series')[target]
            from m3u_store import group as update_group
            update_group(self.draft.playlist,group['category_name'],kind,cid)
            self.draft.selected[self.kind].discard(cid)
            self.draft.categories[self.kind].remove(group);self.draft.categories[kind].append(group);self._groups_loaded=False;self.draft.scanned=False;self.render()
            self.setFocusId(self.list_id if self._entries else 17)
            return
        super().onAction(action)
        if action.getId() in (1,2,3,4) and self.stage=='groups':self.onFocus(self.getFocusId())
    def scanned(self,result): self.stage='summary';self.render()
    def saved(self,portal):
        self._gui()
        self._mark51('SETUP_SAVE_END')
        from setup_trace import mark
        mark('GUI_CLOSE_BEGIN',getattr(self.draft,'pid',''))
        self.result=portal
        # The just-imported catalog is already complete; do not immediately
        # enqueue the same provider scan a second time.
        pid=getattr(self.draft,'pid','')
        self.close()
        mark('GUI_CLOSE_DONE',pid)



def open_setup(data):
    from setup_draft import Draft
    import xbmcaddon
    from wizard_session51 import acquire
    release=acquire()
    try:draft=Draft(data)
    except BaseException:release();raise
    def cleanup():
        try:draft.dispose()
        finally:release()
    configured=False
    try:
        window=SetupWindow('XCMateSetup.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
        window.configure(draft);window._data_state.cleanup=cleanup;configured=True
        window.run();return window.result
    finally:
        if not configured:cleanup()

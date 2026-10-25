"""One native XML setup flow. All source work runs on a cancellable worker."""
import threading
from concurrent.futures import ThreadPoolExecutor
import xbmcgui
from localization import tr


def _failure_details(exc):
    """Show only preapproved failure reasons: never echo provider URLs or credentials."""
    codes={'XM-SETUP-VERIFY':32782,'XM-SETUP-SAVE-BUSY':32783,'XM-SETUP-RESCAN':32785,'XM-SETUP-ROLLBACK':32786}
    code=getattr(exc,'code',None)
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


class WorkWindow(xbmcgui.WindowXML):
    """Workers return data; only the Window's Python owner touches Kodi GUI.

    run() pumps futures after show()/Monitor.waitForAbort(), including when the
    user presses no key. Completion callbacks may only release non-GUI data.
    """
    def configure_work(self):
        self._owner=threading.get_ident();self._initialized=False
        self._closed=False;self._disposed=False;self.busy=False;self.cancel=threading.Event()
        self._pool=ThreadPoolExecutor(max_workers=1);self._lock=threading.RLock()
        self._future=None;self._apply=None;self._progress=None
    def _gui(self):
        if threading.get_ident()!=self._owner: raise RuntimeError('XM-SETUP-GUI-THREAD')
    def status(self,percent,text):
        # Coalesce rather than queue an unbounded event per imported item.
        with self._lock:
            if not self._closed: self._progress=(percent,str(text))
        if threading.get_ident()==self._owner and self._initialized: self._paint_status()
    def _paint_status(self):
        self._gui()
        with self._lock: value=self._progress;self._progress=None
        if value and not self._closed:
            percent,text=value
            self.getControl(3).setText(text)
            self.getControl(4).setVisible(percent is not None)
            if percent is not None: self.getControl(4).setPercent(max(0,min(100,percent)))
    def work(self,job,apply):
        self._gui()
        if self.busy or self._closed: return
        self.busy=True;self._apply=apply
        self.working()
        self._future=self._pool.submit(job)
        # This callback never reads or changes a Kodi control or closes a GUI.
        self._future.add_done_callback(self._finished_cleanup)
    def working(self): pass
    def _finished_cleanup(self,future):
        if self._closed: self._dispose_once()
    def _dispose_once(self):
        with self._lock:
            if self._disposed: return
            self._disposed=True
        self.dispose()
    def pump(self):
        self._gui()
        if self._closed or not self._initialized: return
        self._paint_status()
        future=self._future
        if future is None or not future.done(): return
        apply=self._apply;self._future=None;self._apply=None;self.busy=False
        try: apply(future.result())
        except InterruptedError: self.close()
        except Exception as exc: self.failed_work(exc)
    def run(self):
        import xbmc
        self._gui();monitor=xbmc.Monitor()
        try:
            self.show()  # Kodi dispatches WindowXML.onInit; never call it here.
            while not self._closed:
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
        super().close()
        self._pool.shutdown(wait=False,cancel_futures=True)
        if self._future is None or self._future.done(): self._dispose_once()
    def onAction(self,action):
        if action.getId() in (9,10,92): self.close()
        # Native arrows/OK are never replayed.

class SetupWindow(WorkWindow):
    def configure(self,draft):
        self.configure_work();self.draft=draft;self.kind='live';self.stage='discover';self.result=None
        self._entries=[]
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
        self.work(lambda:self.draft.discover(self.cancel.is_set,self.status),
                  self.discovered)

    def onInit(self):
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
        self.stage='groups'
        self.kind=next((kind for kind in ('live','vod','series')
                        if self.draft.categories.get(kind)), 'live')
        self.render()
        self.setFocusId(self.list_id if self._entries else 17)
    def working(self):
        for ident in (10,11,12,13,14,15,16,17,100,101,102): self.getControl(ident).setVisible(False)
        self.getControl(18).setVisible(True);self.setFocusId(18)
    def _item_state(self,item,selected):
        import os,xbmcaddon
        item.setProperty('setup_selected','true' if selected else 'false')
        image=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media',
                           'setup_checked.png' if selected else 'setup_unchecked.png')
        item.setArt({'icon':image})
    def _groups(self):
        if getattr(self,'_groups_loaded',False): return
        for number,kind in enumerate(('live','vod','series')):
            control=self.getControl(100+number);control.reset();items=[]
            for group in self.draft.categories[kind]:
                item=xbmcgui.ListItem(str(group['category_name']))
                self._item_state(item,str(group['category_id']) in self.draft.selected[kind]);items.append(item)
            control.addItems(items)
        self._groups_loaded=True
    def _selection_status(self):
        self.getControl(5).setLabel(tr(32780,len(self.draft.selected[self.kind]),len(self._entries)))
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
        if groups:
            self.status(None,tr(32712));self._selection_status()
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
                    pos=self.getControl(self.list_id).getSelectedPosition()
                    if 0<=pos<len(self._entries):
                        cid=str(self._entries[pos]['category_id']);selected=self.draft.selected[self.kind]
                        selected.remove(cid) if cid in selected else selected.add(cid)
                        self.draft.scanned=False
                        self._item_state(self.getControl(self.list_id).getListItem(pos),cid in selected)
                        self._selection_status()
                elif controlId in (13,14):
                    self.draft.selected[self.kind]={str(g['category_id']) for g in self._entries} if controlId==13 else set()
                    self.draft.scanned=False
                    for pos,group in enumerate(self._entries):
                        self._item_state(self.getControl(self.list_id).getListItem(pos),str(group['category_id']) in self.draft.selected[self.kind])
                    self._selection_status()
                elif controlId==15: self.choose_epg()
                elif controlId==16: self.close()
                elif controlId==17:
                    self.status(0,tr(32713))
                    self.work(lambda:self.draft.scan(self.cancel.is_set,self.status),self.scanned)
            elif self.stage=='summary' and controlId==16:
                self.stage='groups';self.render();self.setFocusId(self.list_id if self._entries else 17)
            elif self.stage=='summary' and controlId==17:
                self.status(0,tr(32716));self.work(lambda:self.draft.save(self.cancel.is_set),self.saved)
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
            return
        super().onAction(action)
    def _choose_start_channel(self):
        """Optional first-run start group / channel from staged, selected data.

        Only the temporary staging SQLite is read; preferences are published
        together with the account by Draft.save() after explicit Save.
        """
        if not self.draft.selected['live'] or not self.draft.report.get('live'):
            return
        dlg = xbmcgui.Dialog()
        if not dlg.yesno('XCMate – Startsender',
                         'Jetzt Startgruppe und Startsender auswählen? '
                         'Das startet noch keine Wiedergabe.'):
            return
        categories = [g for g in self.draft.categories['live']
                      if str(g['category_id']) in self.draft.selected['live']]
        if not categories:
            return
        selected = dlg.select('XCMate – Startgruppe', [
            str(g.get('category_name') or g['category_id']) for g in categories])
        if selected < 0:
            return
        group = categories[selected]
        cid = str(group['category_id'])
        from library_index import Reader
        reader = Reader(self.draft.pid, self.draft.index, timeout=.5,
                        query_seconds=2)
        offset = 0
        while True:
            rows, total = reader.page('live', category=cid, offset=offset,
                                      limit=100)
            if not rows:
                dlg.notification('XCMate', 'Keine Sender in dieser Startgruppe')
                return
            options = [str(r.get('name') or r.get('sid') or '') for r in rows]
            more = offset + len(rows) < total
            if more:
                options.append('Weitere Sender anzeigen ...')
            index = dlg.select('XCMate – Startsender', options)
            if index < 0:
                return
            if more and index == len(rows):
                offset += len(rows)
                continue
            if index >= len(rows):
                return
            channel = rows[index]
            sid = str(channel.get('sid') or channel.get('stream_id') or '')
            if not sid:
                return
            self.draft.data['start_group_id'] = cid
            self.draft.data['start_stream_id'] = sid
            self.draft.data['autoplay_start'] = False
            return

    def scanned(self,result):
        self.stage='summary'
        self.render()
        try:
            self._choose_start_channel()
        except (ValueError, OSError, RuntimeError) as exc:
            from utils import warn
            warn('XCMate start-channel preview skipped: '+type(exc).__name__)
        self.render()

    def saved(self,portal):
        self._gui()
        self.result=portal
        # The just-imported catalog is already complete; do not immediately
        # enqueue the same provider scan a second time.
        self.close()



def open_setup(data):
    from setup_draft import Draft
    import xbmcaddon
    draft=Draft(data)
    try:
        window=SetupWindow('XCMateSetup.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
        window.configure(draft);window.run();return window.result
    finally:
        if 'window' not in locals(): draft.dispose()

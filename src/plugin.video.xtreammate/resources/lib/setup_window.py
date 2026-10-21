"""One native XML setup flow. All source work runs on a cancellable worker."""
import threading
from concurrent.futures import ThreadPoolExecutor
import xbmcgui
from localization import tr


def _failure_details(exc):
    """Show only preapproved failure reasons: never echo provider URLs or credentials."""
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
    def configure_work(self):
        self._closed=False;self.busy=False;self.cancel=threading.Event()
        self._pool=ThreadPoolExecutor(max_workers=1);self._lock=threading.RLock();self._future=None
    def status(self,percent,text):
        with self._lock:
            if not self._closed:
                self.getControl(3).setText(str(text));self.getControl(4).setPercent(max(0,min(100,percent)))
    def work(self,job,apply):
        if self.busy or self._closed: return
        self.busy=True
        self._future=self._pool.submit(job)
        def completed(future):
            with self._lock:
                self.busy=False
                if self._closed:
                    self.dispose();return
                try: result=future.result()
                except InterruptedError: self.close();return
                except Exception as exc:
                    self.failed_work(exc)
                    return
                apply(result)
        self._future.add_done_callback(completed)
    def failed_work(self,exc):
        code,message=_failure_details(exc)
        try:
            from utils import warn
            # No exception text, host, username, password or URL in Kodi logs.
            warn('XCMate setup: stage={} code={} type={}'.format(
                getattr(self,'stage','unknown'),code,type(exc).__name__))
        except Exception:
            pass
        self.status(0,'{} [{}]'.format(message,code))

    def dispose(self): pass
    def close(self):
        with self._lock:
            if self._closed: return
            self._closed=True;self.cancel.set();super().close()
            self._pool.shutdown(wait=False,cancel_futures=True)
            if self._future is None or self._future.done(): self.dispose()
    def onAction(self,action):
        if action.getId() in (9,10,92): self.close()
        # Kodi handles arrows and OK natively. Do not replay the same key here.


class SetupWindow(WorkWindow):
    def configure(self,draft):
        self.configure_work();self.draft=draft;self.kind='live';self.stage='discover';self.result=None
        self._entries=[]
    def _show_discover_ui(self):
        self.getControl(2).setLabel(tr(32700))
        for ident in (10,11,12,13,14,15,16,17,100):
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
        if self.stage!='discover': self.render();return
        self._start_discovery()

    def dispose(self): self.draft.dispose()

    def failed_work(self,exc):
        super().failed_work(exc)
        if self.stage=='discover':
            self.stage='failed'
            for ident in (10,11,12,13,14,15,16,100):
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
        self.setFocusId(100 if self._entries else 17)
    def render(self):
        for ident,label in ((10,32701),(11,32702),(12,32703),(13,32704),(14,32705),(15,32706),(16,32710),(17,32709 if self.stage=='summary' else 32707),(18,32708)):
            self.getControl(ident).setLabel(tr(label))
        for ident in (10,11,12,13,14,15,16,17,18,100):
            self.getControl(ident).setVisible(self.stage in ('groups','summary'))
        self.getControl(100).reset();self._entries=[]
        if self.stage=='groups':
            self.status(0,tr(32712))
            self._entries=self.draft.categories[self.kind]
            self.getControl(100).addItems([xbmcgui.ListItem(('☑ ' if str(g['category_id']) in self.draft.selected[self.kind] else '☐ ')+str(g['category_name'])) for g in self._entries])
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
        self.draft.epg_sources=sources
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
                    self.setFocusId(100 if self._entries else 17)
                elif controlId==100:
                    pos=self.getControl(100).getSelectedPosition()
                    if 0<=pos<len(self._entries):
                        cid=str(self._entries[pos]['category_id']);selected=self.draft.selected[self.kind]
                        selected.remove(cid) if cid in selected else selected.add(cid)
                        self.render();self.getControl(100).selectItem(pos);self.setFocusId(100)
                elif controlId in (13,14):
                    self.draft.selected[self.kind]={str(g['category_id']) for g in self._entries} if controlId==13 else set();self.render()
                elif controlId==15: self.choose_epg()
                elif controlId==16: self.close()
                elif controlId==17:
                    self.status(0,tr(32713))
                    self.work(lambda:self.draft.scan(self.cancel.is_set,self.status),self.scanned)
            elif self.stage=='summary' and controlId==16:
                self.stage='groups';self.render();self.setFocusId(100)
            elif self.stage=='summary' and controlId==17:
                self.status(0,tr(32716));self.work(lambda:self.draft.save(self.cancel.is_set),self.saved)
        except (ValueError,OSError) as exc: self.status(0,tr(32743,type(exc).__name__))
    def onAction(self,action):
        if action.getId()==117 and not self.busy and self.stage=='groups' and self.draft.data['type']=='m3u':
            pos=self.getControl(100).getSelectedPosition()
            if not 0<=pos<len(self._entries): return
            target=xbmcgui.Dialog().select(tr(32736),[tr(32701),tr(32702),tr(32703)])
            if target<0: return
            group=self._entries[pos];cid=str(group['category_id']);kind=('live','vod','series')[target]
            from m3u_store import group as update_group
            update_group(self.draft.playlist,group['category_name'],kind,cid)
            self.draft.selected[self.kind].discard(cid)
            self.draft.categories[self.kind].remove(group);self.draft.categories[kind].append(group);self.render()
            return
        super().onAction(action)
    def scanned(self,result): self.stage='summary';self.render()
    def saved(self,portal):
        self.result=portal
        # Scheduling is local. Image and EPG workers remain asynchronous.
        try:
            from catalog_sync import request
            for kind in ('live','vod','series'):
                if portal.get('include_'+kind): request(portal,kind,priority=5)
        except Exception:
            from utils import warn
            warn('XCMate setup: background registration deferred')
        finally: self.close()



def open_setup(data):
    from setup_draft import Draft
    import xbmcaddon
    draft=Draft(data)
    try:
        window=SetupWindow('XCMateSetup.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p')
        window.configure(draft);window.doModal();return window.result
    finally:
        if 'window' not in locals(): draft.dispose()

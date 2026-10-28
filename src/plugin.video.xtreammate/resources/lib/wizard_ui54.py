"""Actual wizard: authenticate → selected catalog → publish → optional EPG.

Native controls belong to the owner; workers receive plain data callbacks only.
Legacy direct data APIs remain callable for existing import/verification tests.
"""
import functools


def phase_panel(w,phase):
    w.stage=phase
    for cid in (5,6,10,11,12,13,14,15,100,101,102):w.getControl(cid).setVisible(False)
    w.getControl(3).setHeight(380);w.getControl(4).setPosition(45,485)
    w.setProperty('XCMate.SetupKind','')
    for cid in (16,17,18):w.getControl(cid).setVisible(True)
    w.getControl(19).setVisible(False)
    w.getControl(2).setLabel('Schritt 4/4 · EPG · Portal bereits gespeichert')
    for cid,label in ((16,'EPG später fortsetzen'),(17,'EPG jetzt fortsetzen'),(18,'Ohne EPG zu XCMate')):w.getControl(cid).setLabel(label)
    w.status(None,'Portal erfolgreich gespeichert. Live-TV, Filme und Serien sind bereits nutzbar.\nEPG-Quellen können unabhängig fortgesetzt werden.\nAbgeschlossene Quellen werden vor Wiederverwendung geprüft.')
    w.setFocusId(17)


def start_epg(w,portal):
    from wizard_epg54 import run
    w.stage='epg_running';w.getControl(2).setLabel('Schritt 4/4 · EPG · Portal bleibt erhalten')
    for cid in (16,17,19):w.getControl(cid).setVisible(False)
    w.getControl(18).setVisible(True);w.getControl(18).setLabel('EPG abbrechen / später')
    w.setFocusId(18)
    cancel=w.cancel.is_set;status=w._data_state.status
    w.work(lambda:run(portal,cancel,status),lambda state:finished_epg(w,state))


def finished_epg(w,state):
    phase_panel(w,'epg_ready' if state.get('phase') in ('READY','NONE') else 'epg_pending')
    if w.stage=='epg_ready':
        w.getControl(16).setVisible(False);w.getControl(17).setLabel('Zu XCMate')
        w.status(100,'Portal und konfigurierte EPG-Quellen sind vollständig geprüft.\nDie Einrichtung ist abgeschlossen.')
    else:
        from epg_report53 import meaning,advice
        w.status(None,'Portal ist gespeichert und nutzbar.\nEPG noch nicht vollständig abgeschlossen.\n'+meaning(state.get('code'))+'\n'+advice(state.get('code'))+'\nJetzt oder später fortsetzen; keine erneute Katalogeinrichtung erforderlich.')


def phased(cls):
    old={n:getattr(cls,n) for n in ('configure','_start_discovery','discovered','scanned','saved','failed_work','onClick','onAction','render','working')}
    def enabled(w):return bool(getattr(w.draft,'phased54',False))
    def auth(w):
        from wizard_deadline48 import discovery
        draft=w.draft;cancel=w.cancel.is_set;status=w._data_state.status
        @discovery
        def authenticate(d,cancel,status):return d.adapter.authenticate(cancel,lambda count:status(None,'Verbindung prüfen · '+str(count)+' Datensätze'))
        w.stage='authenticate';w._show_discover_ui();w.getControl(2).setLabel('Schritt 1/4 · Xtream-Verbindung' if draft.data['type']=='xtream' else 'Schritt 1/4 · Verbindung')
        w.status(None,'Verbindung und Zugangsdaten werden tatsächlich geprüft …')
        w.work(lambda:authenticate(draft,cancel,status),lambda value:authenticated(w,value))
    def authenticated(w,value):
        if value is False:raise ValueError('authentication failed')
        s=getattr(w.draft,'resume53',None)
        if s:s.authenticated53=True;s.checkpoint(w.draft,'authenticated')
        import xbmcgui
        text='Verbindung erfolgreich. Zugangsdaten bestätigt.'
        w.status(100,text);xbmcgui.Dialog().notification('XCMate',text)
        w.stage='discover';w.getControl(2).setLabel('Schritt 2/4 · Verfügbare Gruppen ermitteln')
        draft=w.draft;cancel=w.cancel.is_set;status=w._data_state.status
        from wizard_deadline48 import discovery
        @discovery
        def categories(d,cancel,status):
            for kind in ('live','vod','series'):
                if cancel():raise InterruptedError('setup cancelled')
                from wizard_catalog54 import LABELS
                status(None,LABELS[kind]+': Gruppen werden geladen')
                d.categories[kind]=d.adapter.categories(kind,remote=True)
                status(None,LABELS[kind]+': '+str(len(d.categories[kind]))+' verfügbare Gruppen')
            if not any(d.categories.values()):raise ValueError('no usable categories')
            s=getattr(d,'resume53',None)
            if s and not s.checkpoint(d,'groups',categories=True):raise OSError('DRAFT_CHECKPOINT_FAILED')
            return d.categories
        w.work(lambda:categories(draft,cancel,status),w.discovered)
    @functools.wraps(old['configure'])
    def configure(w,draft):old['configure'](w,draft)
    def start(w):
        if enabled(w):return auth(w)
        return old['_start_discovery'](w)
    def discovered(w,result):
        old['discovered'](w,result)
        if enabled(w):w.getControl(2).setLabel('Schritt 2/4 · Gruppen auswählen')
    def scanned(w,result):
        old['scanned'](w,result)
        if enabled(w):
            w.getControl(2).setLabel('Schritt 3/4 · Katalog geprüft · Portal speichern')
            w.getControl(17).setLabel('Portal sicher speichern')
    def saved(w,portal):
        if not enabled(w):return old['saved'](w,portal)
        w.result=portal;w._mark51('SETUP_SAVE_END');phase_panel(w,'epg_pending')
        from wizard_epg54 import plans
        # No source fetch in the GUI: configuration existence is sufficient.
        if not w.draft.epg_sources and not w.draft.provider_epg:finished_epg(w,dict(phase='NONE'))
        s=getattr(w.draft,'resume53',None)
        if s:s.checkpoint(w.draft,w.stage)
    def failed(w,exc):
        if not enabled(w):return old['failed_work'](w,exc)
        if w.result:
            phase_panel(w,'epg_pending')
            from setup_window import _failure_details
            w.status(None,'Portal bleibt gespeichert. EPG kann später fortgesetzt werden.\n'+_failure_details(exc)[1]);return
        phase=w.stage;old['failed_work'](w,exc)
        if phase in ('authenticate','discover','failed'):
            w.stage='failed'
            for cid in (16,17,18,19):w.getControl(cid).setVisible(True)
            for cid,label in ((16,'Zurück / Bearbeiten'),(17,'Erneut prüfen'),(18,'Später fortsetzen'),(19,'Passwort anzeigen/ausblenden')):w.getControl(cid).setLabel(label)
            w.setFocusId(17)
    def click(w,cid):
        if enabled(w):
            if w.stage.startswith('epg_'):
                if cid==18:w.close();return
                if w.busy:return
                if cid==16:w.close();return
                if cid==17:
                    if w.stage=='epg_ready':w.close()
                    else:start_epg(w,w.result)
                return
            if w.stage=='failed' and not w.busy and cid==19:
                s=getattr(w.draft,'resume53',None)
                if s:s.checkpoint(w.draft);s.action='password54';w.close()
                return
            if w.stage=='groups' and cid==17 and not w.busy:w.getControl(2).setLabel('Schritt 3/4 · Ausgewählte Inhalte importieren')
        return old['onClick'](w,cid)
    def action(w,event):
        if enabled(w) and w.stage.startswith('epg_') and event.getId() in (9,10,92):w.close();return
        return old['onAction'](w,event)
    def render(w):
        old['render'](w)
        if enabled(w):
            w.getControl(2).setLabel('Schritt 2/4 · Gruppen auswählen' if w.stage=='groups' else 'Schritt 3/4 · Geprüften Katalog speichern')
    def working(w):
        old['working'](w)
        if enabled(w) and w.stage=='epg_running':w.getControl(18).setLabel('EPG abbrechen / später')
    for name,method in [('configure',configure),('_start_discovery',start),('discovered',discovered),('scanned',scanned),('saved',saved),('failed_work',failed),('onClick',click),('onAction',action),('render',render),('working',working)]:setattr(cls,name,method)
    return cls


def open_published(portal):
    from setup_window import WorkWindow
    from wizard_session51 import acquire
    import xbmcaddon
    release=acquire();configured=False
    class EPGWindow54(WorkWindow):
        def onInit(self):
            if self._initialized:return
            self._initialized=True;phase_panel(self,'epg_pending')
        def onClick(self,cid):
            if cid==18:self.close();return
            if self.busy:return
            if cid==16:self.close()
            elif cid==17:
                if self.stage=='epg_ready':self.close()
                else:start_epg(self,self.result)
        def failed_work(self,exc):
            phase_panel(self,'epg_pending');self.status(None,'EPG nicht abgeschlossen. Das gespeicherte Portal bleibt nutzbar. Verbindung, Quelle und Sicherungsstatus prüfen.')
    try:
        w=EPGWindow54('XCMateSetup.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p');w.configure_work();w.result=portal;w._data_state.cleanup=release;configured=True
        w.run()
    except BaseException:
        if not configured:release()
        raise
    return portal

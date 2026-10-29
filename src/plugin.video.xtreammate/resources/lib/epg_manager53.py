"""Single owner-pumped source manager and readable report on existing APIs."""
import time
from concurrent.futures import ThreadPoolExecutor
import xbmcgui
from menu_icons45 import select
from owner_dispatch import OwnerDispatch,native_init


class Manager53(OwnerDispatch,xbmcgui.WindowXMLDialog):
    _native_surface='dialog'
    def configure(self,portal):
        self._configure_owner();self.portal=portal;self._pool=ThreadPoolExecutor(max_workers=1)
        self._generation=0;self._closed=False;self.rows=[];self.mode='sources';self._last=0;self.scroll=0;self.next_action=None
    @native_init
    def onInit(self):
        self.getControl(101).setLabel('XCMate · EPG-Manager')
        for cid,label in [(401,'Quellen hinzufügen'),(402,'Jetzt aktualisieren'),(403,'Aktualisierungsbericht anzeigen'),(404,'Quellenliste'),(405,'Großes EPG / Senderzuordnung'),(406,'Zurück'),(407,'Automatisches Intervall'),(408,'Bericht nach oben'),(409,'Bericht nach unten')]:self.getControl(cid).setLabel(label)
        self._load();self.setFocusId(401)
    def _load(self):
        from epg_report53 import overview
        self.mode='sources';self.getControl(300).setVisible(False);self.getControl(200).setVisible(True)
        self.getControl(102).setLabel('Gespeicherte Quellen werden gelesen …')
        def load():
            from wizard_epg54 import pending
            return overview(self.portal),pending(self.portal)
        def ready(value):
            rows,self._setup_pending54=value;self._loaded(rows)
        self._request(load,ready)
    def _loaded(self,rows):
        from epg_report53 import meaning
        self.rows=rows;control=self.getControl(200);pos=control.getSelectedPosition();control.reset()
        items=[]
        for row in rows:
            saved=row['saved'];counts=(str(saved.get('channels',0))+' Sender · '+str(saved.get('programmes',0))+' Sendungen') if row['statistics_code']=='READY' else 'Bestand derzeit nicht sicher lesbar'
            items.append(xbmcgui.ListItem(('✓ ' if row['enabled'] else '○ ')+str(row['rank'])+' · '+row['name'],label2=meaning(row['code'])+' · '+counts))
        control.addItems(items)
        if items:control.selectItem(min(pos,len(items)-1))
        from epg_schedule53 import interval
        self.getControl(102).setLabel('Automatisch alle '+str(interval()//3600)+' Stunden · OK: Quelle verwalten · Einzelzuordnung im großen EPG')
        self.getControl(402).setLabel('EPG-Einrichtung fortsetzen' if getattr(self,'_setup_pending54',False) else 'Jetzt aktualisieren')
        self._detail()
    def _detail(self):
        if self.mode!='sources' or not self.rows:return
        row=self.rows[min(self.getControl(200).getSelectedPosition(),len(self.rows)-1)]
        from epg_report53 import stamp
        saved=row['saved']
        self.getControl(103).setText('Letzter Erfolg: '+stamp(row['last_success'])+'\nLetzter protokollierter Fehler: '+stamp(row['last_failure'])+'\nGespeicherter Zeitraum: '+stamp(saved.get('first'))+' bis '+stamp(saved.get('last')))
    def onFocus(self,cid):
        if cid==200:self._detail()
    def _query_failed(self,exc):self.getControl(102).setLabel('Lokaler EPG-Zugriff derzeit nicht möglich. Daten bleiben erhalten.')
    def _reports(self):
        from epg_report53 import history
        def ready(runs):
            if not runs:self.getControl(102).setLabel('Noch kein abgeschlossener Aktualisierungsbericht vorhanden.');return
            from epg_report53 import stamp,meaning,describe
            choice=select(xbmcgui.Dialog(),'Aktualisierungsbericht anzeigen',[stamp(r.get('started'))+' · '+meaning(r.get('code')) for r in reversed(runs)])
            if not 0<=choice<len(runs):return
            self.mode='report';self.scroll=0;self.getControl(200).setVisible(False);self.getControl(103).setText('')
            self.getControl(300).setVisible(True);self.getControl(300).setText(describe(runs[-1-choice],self.portal));self.getControl(300).scroll(0)
            self.getControl(102).setLabel('Bericht mit „nach oben / nach unten“ lesen · Zurück führt zur Quellenliste.')
            self.setFocusId(409)
        self._request(lambda:history(self.portal['id']),ready)
    def onClick(self,cid):
        if cid==406:
            if self.mode=='report':self._load();self.setFocusId(404)
            else:self.close()
            return
        if self._pending_future:return
        import epg_sources as sources
        if cid==401:
            choice=select(xbmcgui.Dialog(),'EPG-Quelle hinzufügen',['Deutschland / Österreich / Schweiz','XMLTV-Adresse','XMLTV-Datei','Zurück'])
            if choice==0:sources._choose_preset(self.portal)
            elif choice in (1,2):
                uri=xbmcgui.Dialog().input('XMLTV-Adresse (HTTP/HTTPS)') if choice==1 else xbmcgui.Dialog().browse(1,'XMLTV-Datei auswählen','files','.xml|.gz|.xml.gz',False,False,'')
                if uri:
                    name=xbmcgui.Dialog().input('Name dieser EPG-Quelle',defaultt='XMLTV')
                    try:sources.add_source(self.portal['id'],name,uri,local=choice==2)
                    except (OSError,ValueError):xbmcgui.Dialog().ok('XCMate EPG','Quelle nicht hinzugefügt. Adresse, Dateityp und Schreibrechte prüfen.')
            self._load()
        elif cid==402:
            if getattr(self,'_setup_pending54',False):
                self.next_action='resume_epg54';self.close();return
            from epg import request_refresh
            ok=request_refresh(self.portal['id'],self.portal,force=True)
            self.getControl(102).setLabel('Aktualisierung angefordert; Speicherung noch nicht bestätigt.' if ok else 'Aktualisierung blockiert. Bestehende EPG-Sicherung und laufende Importe prüfen.')
        elif cid==403:self._reports()
        elif cid==404:self._load()
        elif cid==405:self.next_action='guide';self.close()
        elif cid==407:
            values=[24,6,12,48];choice=select(xbmcgui.Dialog(),'Automatischer EPG-Download',[str(h)+' Stunden' for h in values])
            if 0<=choice<len(values):
                import xbmcaddon
                xbmcaddon.Addon().setSetting('epg_refresh_hours',str(values[choice]))
            self._load()
        elif cid in (408,409) and self.mode=='report':
            self.scroll=max(0,self.scroll+(-12 if cid==408 else 12));self.getControl(300).scroll(self.scroll)
        elif cid==200 and self.rows:
            row=self.rows[self.getControl(200).getSelectedPosition()]
            if row['id']=='provider':
                if xbmcgui.Dialog().yesno('Anbieter-EPG','Anbieter-EPG '+('deaktivieren?' if row['enabled'] else 'aktivieren?')):
                    import portals
                    portals.update(self.portal['id'],dict(provider_epg_enabled=not row['enabled']));self.portal=dict(self.portal,provider_epg_enabled=not row['enabled'])
            else:sources._manage_source(self.portal,row['record'])
            self._load()
    def onAction(self,action):
        if action.getId() in (9,10,92):self.onClick(406)
        elif action.getId() in (3,4) and self.mode=='sources':self._detail()
    def close(self):
        self._gui()
        if self._closed:return
        self._closed=True;self._generation+=1
        if self._pending_future:self._pending_future.cancel()
        self._pending_future=self._pending_apply=None;self._pool.shutdown(wait=False,cancel_futures=True);super().close()


def manage(portal):
    import xbmcaddon
    w=Manager53('XCMateEPGManager53.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p');w.configure(portal);w.run()
    return w.next_action

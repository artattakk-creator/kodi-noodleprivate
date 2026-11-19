"""Single owner-pumped source manager and readable report on existing APIs."""
import time
from concurrent.futures import ThreadPoolExecutor
import xbmcgui
from menu_icons45 import select
from owner_dispatch import OwnerDispatch,native_init

AGENT_DELIVERY_LABELS={
    'CHECKING':'Manifest wird geprüft',
    'PRIVATE_PENDING':'Private Bereitstellung ausstehend',
    'IMPORT_PENDING':'Agent-Import ausstehend',
    'CURRENT':'Agent-Bestand aktuell',
}


class Manager53(OwnerDispatch,xbmcgui.WindowXMLDialog):
    _native_surface='dialog'
    def configure(self,portal):
        self._configure_owner()
        self.portal=portal
        self._pool=ThreadPoolExecutor(max_workers=1)
        self._inventory_pool=ThreadPoolExecutor(max_workers=1)
        self._inventory_future=None
        self._inventory_generation=0
        self._status_future94=None
        self._generation=0
        self._closed=False
        self._job94={}
        self._agent_delivery=''
        self.rows=[]
        self.mode='sources'
        self.scroll=0
        self.next_action=None
    @native_init
    def onInit(self):
        self.getControl(101).setLabel('XCMate · EPG-Manager')
        self.getControl(412).setLabel(__import__('localization').tr(38030))
        for cid,label in [(401,'Zusätzliche Quellen hinzufügen'),(402,'Jetzt aktualisieren'),(403,'Aktualisierungsbericht anzeigen'),(404,'Quellenliste'),(405,'Großes EPG / Senderzuordnung'),(406,'Zurück'),(407,'Automatisches Intervall'),(408,'Bericht nach oben'),(409,'Bericht nach unten')]:self.getControl(cid).setLabel(label)
        self.getControl(413).setLabel(__import__('localization').tr(38831))
        self.getControl(413).setEnabled(False)
        self._load();self.setFocusId(401)
    def _load(self):
        from epg_report53 import configured
        self._set_mode('sources')
        portal=self.portal
        if portal.get('type')=='xtream':
            portal=dict(portal,provider_epg_enabled=True)
        self._set_rows(self._pending_rows(configured(portal)))
        self._inventory()
        self.getControl(410).setLabel('Anbieter-EPG · Grundversorgung' if self.portal.get('type')=='xtream' else 'Anbieter-EPG')
        self.getControl(410).setEnabled(False)
        self.getControl(411).setEnabled(bool(getattr(self,'_setup_pending54',False)))
        self._set_status()

        def load():
            from wizard_epg54 import pending
            from portals import get_by_id
            portal=get_by_id(self.portal['id']) or self.portal
            if portal.get('type')=='xtream':
                portal=__import__('provider_baseline96').migrate_portal(portal)
            return portal,configured(portal),pending(portal)

        def ready(value):
            self.portal,items,self._setup_pending54=value
            self.getControl(411).setEnabled(self._setup_pending54)
            keys=lambda rows:[(r['id'],r['key'],r['enabled'],r['name']) for r in rows]
            if keys(items)!=keys(self.rows):
                self._set_rows(self._pending_rows(items))
                self._inventory()
            self._set_status()

        self._request(load,ready)
        self._next_status58=0

    def _pending_rows(self,items):
        # Keep dated evidence while a configuration-identical source is rescanned.
        previous={r['key']:r for r in self.rows}
        defaults=dict(saved={},code='WAITING',statistics_code='PENDING',last_success=0,last_failure=0)
        return [
            {**defaults, **previous.get(item['key'],{}), **item, 'inventory95':'PENDING'}
            for item in items
        ]

    def _inventory(self):
        from epg_report53 import overview
        self._inventory_generation+=1
        generation=self._inventory_generation
        if self._inventory_future is not None:
            self._inventory_future.cancel()
        portal=self.portal
        items=[{k:r[k] for k in ('id','key','name','rank','enabled','record') if k in r} for r in self.rows]

        def collect():
            from ui_jobs86 import cancelled,scope
            import xbmc
            monitor=xbmc.Monitor()
            abort=getattr(monitor,'abortRequested',lambda:False)
            with scope(lambda:self._closed or generation!=self._inventory_generation or abort(),seconds=10):
                return overview(portal,items,cancel=cancelled)

        self._inventory_future=self._inventory_pool.submit(collect)

    def _set_rows(self,rows):
        control=self.getControl(200)
        current=[r['key'] for r in self.rows]
        incoming=[r['key'] for r in rows]
        if incoming!=current:
            pos=max(0,control.getSelectedPosition())
            selected=current[pos] if pos<len(current) else None
            control.reset()
            control.addItems([xbmcgui.ListItem('') for _ in rows])
            if rows:
                control.selectItem(incoming.index(selected) if selected in incoming else min(pos,len(rows)-1))
        self.rows=rows
        for i,row in enumerate(rows):
            title=('✓ ' if row['enabled'] else '○ ')+str(row['rank'])+' · '+row['name']
            control.getListItem(i).setLabel(title)
        self._render_rows()

    def _render_rows(self):
        from epg_progress94 import row as job_row
        from epg_report53 import meaning
        control=self.getControl(200)
        for i,source in enumerate(self.rows):
            saved=source['saved']
            code=source.get('inventory95')
            if code=='READY':
                counts=f"{saved.get('channels',0)} XMLTV-Kanäle · {saved.get('programmes',0)} Programme gespeichert"
            elif source.get('historical95') or saved.get('programmes'):
                counts=f"Letzter bestätigter Bestand · {saved['programmes']} Programme"
            elif code=='PENDING':
                counts='Gespeicherter Bestand wird geprüft'
            else:
                counts='Inventur · '+str(code or 'UNBEKANNT')+' · Bestand derzeit nicht bestätigt'
            item=control.getListItem(i)
            key=source['key']
            observation=self._job94.get('sources',{}).get(key,{})
            if observation:
                source['last_attempt66']=max(source.get('last_attempt66',0),self._job94.get('ack',0))
            value=job_row(self._job94,key) if observation and source['enabled'] else {}
            status=value.get('text')
            if key=='agent' and source['enabled'] and self._agent_delivery and not value.get('busy'):
                status=self._agent_delivery+' · '+counts
            item.setLabel2(status or ((meaning(source['code']) if source['enabled'] else 'Deaktiviert')+' · '+counts))
            item.setProperty('Stats94',value.get('stats',''))
            item.setProperty('Busy94','true' if value.get('busy') else '')
            percent=value.get('percent')
            item.setProperty('Percent94',str(percent or 0))
            item.setProperty('KnownTotal94','true' if percent is not None else '')
        self._detail()

    def _set_status(self):
        from epg_gate95 import message
        from epg_progress94 import summary
        from epg_schedule53 import interval
        job=self._job94
        blocked=getattr(self,'_gate_block95',None)
        if self.mode=='report' and not self._live_report:
            text='Bericht mit „nach oben / nach unten“ lesen · Zurück führt zur Quellenliste.'
        elif blocked and job.get('requested',0)<blocked[0]:
            text=message(blocked[1])
        elif job:
            text=summary(job)
        else:
            prefix='Anbieter-EPG als Grundversorgung · ' if self.portal.get('type')=='xtream' else ''
            text=prefix+'Automatisch alle '+str(min(interval(),86400)//3600)+' Stunden · Menü: Senderabdeckung'
        if text!=getattr(self,'_status_text',None):
            self._status_text=text
            self.getControl(102).setLabel(text)

    def _job_poll94(self):
        self._next_status58=time.monotonic()+.5
        pid=self.portal['id']
        observe_agent=any(source['key']=='agent' and source['enabled'] for source in self.rows)

        def read():
            from epg_jobs94 import snapshot
            delivery=''
            if observe_agent:
                from epg_agent100 import state
                status=state()
                delivery=AGENT_DELIVERY_LABELS.get(status.get('code'),'')
                if status.get('remote')=='ERROR':
                    delivery='Agent-Aktualisierung vorübergehend nicht verfügbar'
            return snapshot(pid),delivery

        self._status_future94=self._pool.submit(read)

    def _job_loaded94(self,job):
        if not job:
            return
        from epg_jobs94 import ACTIVE,TERMINAL
        previous=self._job94
        self._job94=job
        active=job.get('state') in ACTIVE
        if active!=(previous.get('state') in ACTIVE):
            self.getControl(413).setEnabled(active)
            self.getControl(402).setEnabled(not active)
        if self.mode=='sources' or self._live_report:
            self._set_status()
        if job.get('sources')!=previous.get('sources') or job.get('state')!=previous.get('state'):
            self._render_rows()
        if job!=previous and self.mode=='report' and self._live_report:
            self._render_live_report()
        if (job.get('state') in TERMINAL and previous.get('state') in ACTIVE and
                job.get('id')==previous.get('id')):
            self._inventory()

    def _detail(self):
        if self.mode!='sources' or not self.rows:
            return
        from epg_progress94 import row as job_row
        from epg_report53 import stamp
        pos=max(0,min(self.getControl(200).getSelectedPosition(),len(self.rows)-1))
        source=self.rows[pos]
        saved=source['saved']
        observation=self._job94.get('sources',{}).get(source['key'],{})
        finish=self._job94.get('finished',0) if observation.get('phase')=='DONE' else 0
        attempt=source.get('last_attempt66')
        verified=observation.get('verified')
        if verified is not None and observation.get('phase')=='DONE':
            left=observation.get('first')
            right=observation.get('last')
        else:
            left,right=saved.get('first'),saved.get('last')
        lines=['Letzter Versuch · '+stamp(attempt)+'   Erfolg · '+stamp(finish or source['last_success']),
               'Gespeichert · '+stamp(left)+' bis '+stamp(right)]
        if observation:
            lines.append(job_row(self._job94,source['key'])['text'])
        else:
            lines.append('Letzter protokollierter Fehler · '+stamp(source['last_failure']))
        self.getControl(103).setText('\n'.join(lines))
    def onFocus(self,cid):
        if cid==200:self._detail()
    def _query_failed(self,exc):self.getControl(102).setLabel('EPG-Zugriff oder Speichern nicht bestätigt. Daten bleiben erhalten.')
    def _refresh_ready95(self,ok):
        if ok:
            self._gate_block95=None
            self._refresh_until58=time.monotonic()+600;self._next_status58=0
            self._status_text=None
            self.getControl(102).setLabel('Aktualisierung angefordert; Dienstübernahme noch ausstehend.')
        else:
            from epg_status import read
            from epg_gate95 import message
            code=read(self.portal['id']).get('refresh',{}).get('code','UNAVAILABLE')
            self._gate_block95=(time.time(),code)
            self.getControl(102).setLabel(message(code))
    def _set_mode(self,mode):
        self.mode=mode
        report=mode=='report'
        for cid in (200,103,401,402,403,405,407,410,411,412):
            self.getControl(cid).setVisible(not report)
        for cid in (300,408,409):
            self.getControl(cid).setVisible(report)
        navigation={
            404:(413,408,406,406),406:(413,409,404,404),
            408:(404,404,409,409),409:(406,406,408,408),
            413:(409,406,404,406),
        } if report else {
            200:(412,401,412,404),401:(200,404,403,402),402:(200,405,401,403),
            403:(200,406,402,404),404:(401,407,403,405),405:(402,412,404,406),
            406:(403,413,405,407),407:(404,401,406,412),
            412:(405,200,411,413),413:(406,200,412,411),
        }
        for cid,neighbors in navigation.items():
            self.getControl(cid).setNavigation(*(self.getControl(n) for n in neighbors))

    def _show_report(self,text='',*,live=False):
        self._set_mode('report')
        self.scroll=0
        self._live_report=live
        self._report_text=None
        self._set_report_text(text)
        self._set_status()
        self.setFocusId(409)

    def _set_report_text(self,text):
        if text!=self._report_text:
            self._report_text=text
            self.getControl(300).setText(text)
            self.getControl(300).scroll(self.scroll)

    def _render_live_report(self):
        from epg_progress94 import report
        self._set_report_text(report(self._job94,{r['key']:r['name'] for r in self.rows}))

    def _reports(self):
        from epg_report53 import describe,history,meaning,stamp
        from epg_jobs94 import ACTIVE,snapshot
        pid=self.portal['id']

        def ready(value):
            runs,job=value
            live=job.get('state') in ACTIVE
            if live and not runs:
                self._job_loaded94(job)
                self._show_report(live=True)
                self._render_live_report()
                return
            if not runs:
                self.getControl(102).setLabel('Noch kein abgeschlossener Aktualisierungsbericht vorhanden.')
                return
            options=[stamp(r.get('started'))+' · '+meaning(r.get('code')) for r in reversed(runs)]
            if live:
                options.insert(0,'Laufende Aktualisierung')
            choice=select(xbmcgui.Dialog(),'Aktualisierungsbericht anzeigen',options)
            if not 0<=choice<len(options):
                return
            if live and choice==0:
                self._job_loaded94(job)
                self._show_report(live=True)
                self._render_live_report()
            else:
                self._show_report(describe(runs[-1-choice+int(live)],self.portal))

        self._request(lambda:(history(pid),snapshot(pid)),ready)

    def _leave_report(self):
        self._set_mode('sources')
        self._status_text=None
        self._set_status()
        self._detail()
        self.setFocusId(403)
    def onClick(self,cid):
        if cid==406:
            if self.mode=='report':
                self._leave_report()
            else:
                self.close()
            return
        if self.mode=='report' and cid==404:
            self._leave_report()
            return
        if self._pending_future:return
        if self.mode=='report' and cid not in (408,409,413):
            return
        import epg_sources as sources
        if cid==413:
            job=getattr(self,'_job94',{})
            if job.get('id'):self._request(lambda:__import__('epg_jobs94').cancel(self.portal['id'],job['id']),lambda value:None)
            return
        if cid==410:
            self._toggle_provider58()
        elif cid==401:
            choice=select(xbmcgui.Dialog(),'EPG-Quelle hinzufügen',['Deutschland / Österreich / Schweiz','XMLTV-Adresse','XMLTV-Datei',__import__('localization').tr(38030),'Zurück'])
            if choice==0:sources._choose_preset(self.portal)
            elif choice in (1,2):
                uri=xbmcgui.Dialog().input('XMLTV-Adresse (HTTP/HTTPS)') if choice==1 else xbmcgui.Dialog().browse(1,'XMLTV-Datei auswählen','files','.xml|.gz|.xml.gz',False,False,'')
                if uri and __import__('epg_config94').confirm_enable(self.portal):
                    name=xbmcgui.Dialog().input('Name dieser EPG-Quelle',defaultt='XMLTV')
                    try:
                        from provider_epg58 import add_source
                        add_source(self.portal,name,uri,local=choice==2)
                    except (OSError,ValueError) as exc:xbmcgui.Dialog().ok('XCMate EPG','Diese Adresse ist bereits die Anbieter-Grundversorgung. Jetzt aktualisieren wählen.' if str(exc)=='DUPLICATE_PROVIDER_FEED' else 'Quelle nicht hinzugefügt. Adresse, Dateityp und Schreibrechte prüfen.')
            if choice==3:
                self.next_action='international73';self.close();return
            self._load()
        elif cid==412:
            self.next_action='international73';self.close();return
        elif cid==411 and getattr(self,'_setup_pending54',False):
            self.next_action='resume_epg54';self.close();return
        elif cid==402:
            from portals import get_by_id
            self.portal=get_by_id(self.portal['id']) or self.portal
            if not __import__('epg_config94').confirm_enable(self.portal):return
            self.portal=get_by_id(self.portal['id']) or self.portal
            from epg import request_refresh
            self.getControl(102).setLabel('Importfreigabe wird unabhängig geprüft …')
            self._request(lambda:request_refresh(self.portal['id'],self.portal,force=True),self._refresh_ready95,seconds=35)
        elif cid==403:self._reports()
        elif cid==404:self._load()
        elif cid==405:self.next_action='guide';self.close()
        elif cid==407:
            values=[24,6,12];choice=select(xbmcgui.Dialog(),'Automatischer EPG-Download',[str(h)+' Stunden' for h in values])
            if 0<=choice<len(values):
                import xbmcaddon
                xbmcaddon.Addon().setSetting('epg_refresh_hours',str(values[choice]))
            self._load()
        elif cid in (408,409) and self.mode=='report':
            self.scroll=max(0,self.scroll+(-12 if cid==408 else 12));self.getControl(300).scroll(self.scroll)
        elif cid==200 and self.rows:
            row=self.rows[self.getControl(200).getSelectedPosition()]
            if row['id']=='provider':
                self._toggle_provider58()
                return
            if row['id']=='agent':
                self.next_action='epg_agent100'
                self.close()
                return
            sources._manage_source(self.portal,row['record'])
            self._load()
    def pump(self):
        super().pump()
        if self._closed:
            return
        inventory=self._inventory_future
        if inventory is not None and inventory.done():
            self._inventory_future=None
            try:
                rows=inventory.result()
            except (OSError,ValueError):
                rows=[dict(row,inventory95='INVENTORY_UNAVAILABLE') for row in self.rows]
            self._set_rows(rows)
        status94=self._status_future94
        if status94 is not None and status94.done():
            self._status_future94=None
            try:
                job,delivery=status94.result()
            except (OSError,ValueError):
                pass
            else:
                changed=delivery!=self._agent_delivery
                self._agent_delivery=delivery
                self._job_loaded94(job)
                if changed:
                    self._render_rows()
        if not self._pending_future and self._status_future94 is None and time.monotonic()>=getattr(self,'_next_status58',0):
            self._job_poll94()
    def _coverage66(self):
        from epg_coverage66 import report
        from stream_epg import active_streams
        from itertools import islice
        def ready(rows):
            from epg_report53 import stamp
            meanings={'READY':'Jetzt/Danach lokal bereit','UNMAPPED':'Keine eindeutige Zuordnung','SOURCE_EMPTY':'Keine gespeicherten Quellereignisse','EVENT_OUT_OF_WINDOW':'Lücke oder Ereignis außerhalb der aktuellen Zeit','STALE':'Gespeicherte Abdeckung abgelaufen','DB_UNAVAILABLE':'Datenbank momentan nicht lesbar'}
            lines=['Lokale Senderabdeckung · kein Netzabruf']
            for row in rows:lines.extend(['',row.get('name') or 'Sender '+row['sid'],meanings.get(row['code'],row['code']),stamp(row.get('first'))+' bis '+stamp(row.get('last'))])
            self._show_report('\n'.join(lines))
            self.getControl(102).setLabel('Lokale Prüfung der ersten bis zu 512 aktivierten Sender · Zurück: Quellenliste')
        self._request(lambda:report(self.portal,list(islice(active_streams(self.portal),512))),ready)

    def _probe84(self):
        from programme_probe84 import report
        def ready(text):
            self._show_report(text)
            self.getControl(102).setLabel('Explizite TMDB-Probe · keine Token/URLs im Bericht · GUI-Nachweis getrennt')
        self._request(lambda:report(self.portal,lambda:self._closed),ready)

    def _toggle_provider58(self):
        if self.portal.get('type')=='xtream':
            xbmcgui.Dialog().ok('Anbieter-EPG · Grundversorgung',__import__('provider_baseline96').MESSAGE)
    def onAction(self,action):
        if action.getId() in (9,10,92):self.onClick(406)
        elif action.getId()==117 and self.mode=='sources' and not self._pending_future:
            choice=select(xbmcgui.Dialog(),'EPG-Diagnose',['Lokale Senderabdeckung','TMDB-Bildkette und Cache-Inventur'])
            if choice==0:self._coverage66()
            elif choice==1:self._probe84()
        elif action.getId() in (3,4) and self.mode=='sources':self._detail()
    def close(self):
        self._gui()
        if self._closed:return
        self._closed=True;self._generation+=1
        self._inventory_generation+=1
        if self._inventory_future is not None:self._inventory_future.cancel()
        self._inventory_pool.shutdown(wait=False,cancel_futures=True)
        if self._pending_future:self._pending_future.cancel()
        if self._status_future94 is not None:self._status_future94.cancel()
        self._pending_future=self._pending_apply=None;self._pool.shutdown(wait=False,cancel_futures=True);super().close()


def manage(portal):
    import xbmcaddon
    while True:
        w=Manager53('XCMateEPGManager53.xml',xbmcaddon.Addon().getAddonInfo('path'),'Default','720p');w.configure(portal);w.run()
        if w.next_action=='epg_agent100':
            from epg_agent100_ui import show
        elif w.next_action=='international73':
            from international_ui73 import show
        else:
            return w.next_action
        show(portal)

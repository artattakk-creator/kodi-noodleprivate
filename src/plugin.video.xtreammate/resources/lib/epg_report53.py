"""Bounded local import history; counts come from committed existing guide tables.

No source URLs, event text, credentials or second EPG database. Reads run on a
worker, never on sender focus. A queued request is not a successful download.
"""
import contextlib,hashlib,json,os,re,sqlite3,tempfile,threading,time
from urllib.parse import quote
_local=threading.local()
SUCCESS={'READY','PARTIAL_PRESERVED','UNCHANGED','VERIFIED','READY_NO_NOW','PARTIAL_SUCCESS'}
BLOCKED={'BACKUP_REQUIRED','IMPORT_BUSY_OR_LOCK_UNAVAILABLE','WAIT_ACTIVE_CATALOG','CANCELLED','NO_NEW_GUIDE'}
MAX_BYTES=1048576


def path(pid):
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'epg_history53_'+hashlib.sha256(str(pid).encode()).hexdigest()[:24]+'.json')


def history(pid):
    try:
        with open(path(pid),encoding='utf-8') as f:raw=f.read(MAX_BYTES+1)
        value=json.loads(raw) if len(raw)<=MAX_BYTES else {}
        return [r for r in value['runs'] if isinstance(r,dict)][-16:] if isinstance(value,dict) and value.get('version')==1 and isinstance(value.get('runs'),list) else []
    except (OSError,ValueError,KeyError,TypeError):return []


def store(pid,run):
    from profile_transaction import writing
    temp=None
    try:
        with writing(timeout=.1):
            runs=(history(pid)+[run])[-16:];raw=json.dumps(dict(version=1,runs=runs),ensure_ascii=False).encode()
            while len(raw)>MAX_BYTES and len(runs)>1:
                runs.pop(0);raw=json.dumps(dict(version=1,runs=runs),ensure_ascii=False).encode()
            if len(raw)>MAX_BYTES:return False
            target=path(pid)
            if os.path.islink(target):return False
            fd,temp=tempfile.mkstemp(prefix='.epg-history53-',dir=os.path.dirname(target))
            with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
            os.replace(temp,target);temp=None
        return True
    except (OSError,ValueError):return False
    finally:
        if temp:
            try:os.unlink(temp)
            except OSError:pass


def statistics(pid, **options):
    from epg_inventory95 import collect
    from guide_store import path as guide_path
    return collect(str(pid),guide_path(),**options)


def started(pid,key,identity,rank):
    run=getattr(_local,'run',None)
    if not run or run['pid']!=str(pid):return
    if len(run['sources'])>=128:return
    run['sources'][identity]=dict(key=key,id=identity,rank=rank,started=time.time(),code='RUNNING')


def source_done(pid,identity,code,counts=None,outcome=None):
    run=getattr(_local,'run',None)
    if not run or run['pid']!=str(pid):return
    row=run['sources'].get(identity)
    if row is None:return
    counts=counts or {}
    row.update(code=code,finished=time.time());row['seconds']=round(row['finished']-row['started'],3)
    for key in ('channels','programmes','stored','bytes','min_start66','max_end66','mapped_channels66','stored_unique66','selected_streams66','matched_streams66','committed','committed_channels','verified','verified_channels','verified_first','verified_last'):
        value=counts.get(key)
        if isinstance(value,(int,float)) and value>=0:row[key]=value
    http_status=counts.get('http_status')
    if type(http_status) is int and 100<=http_status<=599:
        row['http_status']=http_status
    for field in ('raw_horizon102','profiles102'):
        if field in counts:
            row[field]=counts[field]
    revision66=counts.get('revision66','')
    if re.fullmatch(r'[0-9a-f]{64}',revision66):row['revision66']=revision66
    for key in ('added','corrected','conflicts'):
        value=(outcome or {}).get(key)
        if isinstance(value,int) and value>=0:row[key]=value


@contextlib.contextmanager
def observing(pid,automatic=False):
    previous=getattr(_local,'run',None)
    run=dict(pid=str(pid),started=time.time(),automatic=bool(automatic),sources={},code='RUNNING')
    before=statistics(pid);_local.run=run
    try:yield run
    finally:
        try:
            from epg_status import read
            status=read(pid).get('refresh',{})
            if status.get('at',0)>=run['started']:run['code']=status.get('code','UNAVAILABLE')
            elif run.get('result'):run['code']='READY'
            else:run['code']='NO_NEW_GUIDE'
            run['finished']=time.time();run['seconds']=round(run['finished']-run['started'],3)
            after=statistics(pid);run['before']=before;run['after']=after
            stored={r['id']:r for r in after['sources']}
            for identity,row in run['sources'].items():
                if identity in stored:row['saved']=stored[identity]
                if row['code']=='RUNNING':row['code']='CANCELLED'
            run['sources']=list(run['sources'].values());run.pop('pid',None);run.pop('result',None)
            if not store(pid,run):
                from utils import warn
                warn('EPG53_REPORT_WRITE_FAILED')
        except Exception:pass  # Telemetry never converts a successful import to failure.
        finally:_local.run=previous


def label(value,fallback='XMLTV-Quelle'):
    value=str(value or '').replace('\n',' ').replace('\r',' ')[:100]
    if '://' in value or '@' in value or re.search(r'(?i)(password|passwort|token|username)\s*[=:]',value):return fallback
    return value or fallback


def stamp(value):return time.strftime('%d.%m.%Y %H:%M',time.localtime(value)) if value else 'noch nicht bestätigt'


def meaning(code):
    if code in ('DB_BUSY','BACKUP_GATE_TIMEOUT','BACKUP_MISSING','BACKUP_RECEIPT_MISMATCH','BACKUP_DIR_UNAVAILABLE','DB_SCHEMA_MISSING','DB_AUTHORIZATION_MISSING','DB_AUTHORIZATION_CHANGED','DB_INTERRUPTED','STORAGE_IO','STORAGE_FULL','STORAGE_ACCESS_DENIED','IMPORT_AUTHORIZED'):
        return __import__('epg_gate95').message(code)
    return {'REQUESTED':'Auftrag gespeichert; Übernahme durch den Dienst ausstehend','SERVICE_NOT_CONFIRMED':'Dienstübernahme noch nicht bestätigt; Dienststatus prüfen','DOWNLOADING':'XMLTV wird heruntergeladen','PARSING':'XMLTV wird gelesen und Sendern zugeordnet','SAVING':'EPG wird gespeichert','SOURCE_UNAVAILABLE':'Anbieter liefert keine XMLTV-Adresse','EMPTY_GUIDE':'Keine nutzbaren Sendungen im gelieferten XMLTV','NO_CHANNEL_MATCH':'XMLTV enthält Sendungen, aber keine passende eindeutige Senderzuordnung','INVALID_XMLTV':'Ungültiges XMLTV; Import verworfen','DOWNLOAD_TIMEOUT':'Zeitüberschreitung beim Download','DOWNLOAD_FAILED':'Download nicht möglich; Verbindung oder HTTP-Status prüfen','PARSE_TIMEOUT':'Zeitüberschreitung beim XMLTV-Lesen','PARSE_FAILED':'XMLTV konnte nicht verarbeitet werden','GZIP_INVALID':'Komprimierte XMLTV-Datei ungültig','CACHE_WRITE_FAILED':'Lokaler EPG-Cache konnte nicht gespeichert werden','STATUS_UNVERIFIED':'Früherer Status nicht durch gespeicherte Daten bestätigt','NO_SAVED_PROGRAMMES':'Noch keine gespeicherten Sendungen bestätigt','READY':'Erfolgreich gespeichert','READY_NO_NOW':'Gespeichert; aktuell keine laufende Sendung','PARTIAL_SUCCESS':'Teilweise erfolgreich','PARTIAL_PRESERVED':'Gespeichert; widersprüchliche Einträge geschützt','UNCHANGED':'Unverändert bestätigt','BACKUP_REQUIRED':'Verifizierte EPG-Sicherung erforderlich','WAIT_ACTIVE_CATALOG':'Senderkatalog noch nicht bereit','NO_NEW_GUIDE':'Keine neue gültige Programmliste','CANCELLED':'Abgebrochen; bisherige Daten bleiben erhalten','IMPORT_BUSY_OR_LOCK_UNAVAILABLE':'Ein EPG-Import läuft bereits','RUNNING':'Wird aktualisiert','DISABLED':'Deaktiviert','WAITING':'Noch kein Lauf bestätigt'}.get(code,'Aktualisierung fehlgeschlagen; bisherige Daten bleiben erhalten')


def advice(code):
    if code in ('DB_BUSY','BACKUP_GATE_TIMEOUT','DB_INTERRUPTED'):return 'Laufende Arbeit abwarten und Importfreigabe erneut prüfen. Keine neue Sicherung, keine Daten löschen.'
    if code in ('BACKUP_MISSING','BACKUP_RECEIPT_MISMATCH','BACKUP_DIR_UNAVAILABLE','DB_AUTHORIZATION_MISSING','DB_SCHEMA_MISSING','STORAGE_IO','STORAGE_ACCESS_DENIED'):return 'Vorhandene Sicherung und Diagnose prüfen. Keine blinde neue Sicherung und kein Zurücksetzen.'
    if code in SUCCESS:return 'Fehlende Tage oder Bilder können von der Quelle fehlen. Gespeicherten Zeitraum unten prüfen.'
    if code=='BACKUP_REQUIRED':return 'Die vorhandene EPG-Sicherungsfunktion ausführen und BACKUP_VERIFIED abwarten. Keine Datenbank löschen.'
    if code=='NO_CHANNEL_MATCH':return 'EPG-ID und Quellenzuordnung im großen EPG prüfen. Vorschau verwenden; bisherige Zuordnungen bleiben erhalten.'
    if code=='EMPTY_GUIDE':return 'Die Quelle enthält keine nutzbaren Sendungen im gespeicherten Zeitfenster. Andere konfigurierte Quelle prüfen.'
    if code=='SOURCE_UNAVAILABLE':return 'Anbieteradresse oder eine tatsächlich verfügbare eigene XMLTV-Adresse prüfen; keine Adresse erraten.'
    if code=='WAIT_ACTIVE_CATALOG':return 'Zuerst den vorhandenen Senderkatalog fertig laden lassen.'
    if code=='IMPORT_BUSY_OR_LOCK_UNAVAILABLE':return 'Laufenden Import abwarten; keine zweite Aktualisierung starten.'
    return 'Quelle, Internetverbindung und freien Speicher prüfen. Später gezielt erneut versuchen; keine Daten zurücksetzen.'


def configured(portal):
    from epg_sources import configuration
    from guide_publish44 import source_id
    result=[dict(id='provider',key='provider',name='Anbieter-EPG',rank=0,enabled=portal.get('provider_epg_enabled',True))]
    try:
        sources=configuration(portal['id'])['sources']
    except (OSError,ValueError,TypeError):
        sources=[]
    for rank,s in enumerate(sources,1):
        result.append(dict(id=source_id(s,rank),key=__import__('epg_status').source_key(s),name=label(s.get('name')),rank=rank,enabled=s.get('enabled',True),record=s))
    try:
        from epg_agent100 import SOURCE_RANK, enabled
    except ModuleNotFoundError as exc:
        if exc.name!='epg_agent100':
            raise
    else:
        result.append(dict(id='agent',key='agent',name='XCMate EPG Agent',rank=SOURCE_RANK,enabled=enabled()))
    return result


def overview(portal, items=None, *, cancel=None):
    from epg_status import read
    pid=portal['id']
    stats=statistics(pid) if cancel is None else statistics(pid,cancel=cancel)
    runs=history(pid);state=read(pid);rows=[]
    stored={source['id']:source for source in stats['sources']}
    observations={}
    for run in runs:
        for source in run.get('sources',[]):
            observations.setdefault(source.get('id'),[]).append(source)
    for item in configured(portal) if items is None else items:
        row=dict(item);events=observations.get(item['id'],[])
        saved=stored.get(item['id'],{})
        legacy=state.get(item['key'],{});last=events[-1] if events else legacy
        if legacy.get('at',0)>last.get('finished',last.get('at',0)):last=legacy
        refresh=state.get('refresh',{})
        cache=state.get('cache',{})
        if item['id']=='provider' and item['enabled']:
            if cache.get('code')=='WAIT_ACTIVE_CATALOG' and cache.get('at',0)>last.get('finished',last.get('at',0)):last=cache
            if refresh.get('code')=='REQUESTED' and refresh.get('at',0)>last.get('finished',last.get('at',0)):
                last=dict(refresh)
                if time.time()-refresh.get('at',0)>15:last['code']='SERVICE_NOT_CONFIRMED'
        row.update(code=last.get('code','WAITING') if item['enabled'] else 'DISABLED',saved=saved,statistics_code=stats['code'])
        row['inventory95']=saved.get('code',stats['code'])
        if row['inventory95']!='READY':
            prior=next((s for s in reversed(events) if s.get('verified') or s.get('saved',{}).get('programmes')),None)
            if prior:
                previous=prior.get('saved',{})
                if previous.get('programmes') is None:
                    previous=dict(programmes=prior['verified'],first=prior.get('verified_first'),last=prior.get('verified_last'))
                    if 'verified_channels' in prior:
                        previous['channels']=prior['verified_channels']
                row['saved']=dict(previous)
                row['historical95']=True
            # A busy current inventory never revokes an older verified import.
        elif row['code'] in SUCCESS and not saved.get('programmes'):row['code']='NO_SAVED_PROGRAMMES'
        row['progress59']={k:last[k] for k in ('bytes','programmes','count','http_status','failure_stage') if k in last}
        row['last_success']=max([s.get('finished',0) for s in events if s.get('code') in SUCCESS]+[legacy.get('last_success',0)])
        row['last_failure']=max([s.get('finished',0) for s in events if s.get('code') not in SUCCESS]+[0])
        row['last_attempt66']=max([s.get('started',0) for s in events]+[legacy.get('at',0)])
        row['revision66']=next((s.get('revision66','') for s in reversed(events) if s.get('revision66')),'')
        raw=next((s for s in reversed(events) if s.get('raw_horizon102')), {})
        row['raw_horizon102']=raw.get('raw_horizon102')
        row['raw_attempt102']=raw.get('finished')

        row['next_refresh66']=row['last_success']+min(__import__('epg_schedule53').interval(),86400) if row['last_success'] else 0
        rows.append(row)
    return rows



def horizon_summary(title,horizon):
    if not horizon:
        return title+' · Abdeckung nicht ermittelt'
    continuous=horizon.get('last_contiguous_day')
    if horizon.get('channel_limit'):
        coverage='Sendergrenze der Diagnose erreicht'
    elif continuous:
        coverage='Tägliche Starts je Sender bis höchstens '+continuous
    else:
        coverage='Keine tägliche Folge ab dem ersten Berichtstag'
    return title+' · '+stamp(horizon.get('first'))+' bis '+stamp(horizon.get('last'))+' · '+coverage


def horizon_table(horizon):
    return ['Datum · Sender mit Start · Sendungsstarts']+[
        day['date']+' · '+str(day['channels'] if day['channels'] is not None else 'unbekannt')
        +' · '+str(day['programmes']) for day in horizon.get('days',[])
    ]


def source_report(source,previous_success):
    lines=[]
    if source.get('http_status') is not None:
        lines.append('HTTP '+str(source['http_status']))
    if source.get('finished'):
        lines.append('Importversuch · '+stamp(source['finished'])+' · letzter Erfolg · '+stamp(previous_success))
    raw=source.get('raw_horizon102')
    if raw:
        lines.append(horizon_summary('Geliefertes XMLTV vor Zuordnung und Zeitfilter',raw))
        lines.extend(horizon_table(raw))
    for profile in source.get('profiles102',[]):
        lines+=['',horizon_summary('Schema-5-Profil '+profile['profile'].upper()+' / '+profile['variant'],profile.get('horizon')),
                'Quelle erzeugt · '+stamp(profile['generated'])+' · SHA-256 geprüft · '+profile['sha256'][:16]]
        if profile.get('http_status') is not None:
            lines.append('HTTP '+str(profile['http_status']))
        if profile.get('matched') is not None:
            lines.append('IPTV-Zuordnungen zu Profilkanälen · '+str(profile['matched']))
        if profile.get('horizon'):
            lines.extend(horizon_table(profile['horizon']))
    saved=source.get('saved',{}).get('horizon102')
    lines.append(horizon_summary('Im Quellbestand gespeichert',saved))
    if saved:
        lines.extend(horizon_table(saved))
    return lines

def describe(run,portal):
    names={r['id']:r['name'] for r in configured(portal)}
    lines=['Automatische Aktualisierung' if run.get('automatic') else 'Manuelle Aktualisierung',
           'Beginn: '+stamp(run.get('started')),'Dauer: '+str(run.get('seconds',0))+' Sekunden',meaning(run.get('code')),'',advice(run.get('code'))]
    gate95=__import__('epg_gate95').latest(__import__('guide_store').path())
    if gate95:lines+=['','Letzte unabhängige Importfreigabe: '+meaning(gate95['code']),stamp(gate95.get('checked_at'))+' · '+str(gate95.get('elapsed_ms',0))+' ms']
    after=run.get('after',{});before=run.get('before',{})
    if after.get('programmes') is not None:
        lines+=['','Gespeicherte Programme: '+str(after['programmes']),'Zeitraum: '+stamp(after.get('first'))+' bis '+stamp(after.get('last'))]
        horizon=after.get('horizon102')
        lines.append(horizon_summary('Zusammengeführter Cache',horizon))
        if horizon:
            lines.extend(horizon_table(horizon))
        if before.get('programmes') is not None:lines.append('Bestand vorher / nachher: '+str(before['programmes'])+' / '+str(after['programmes']))
    else:lines+=['','Gespeicherter Zeitraum derzeit nicht sicher lesbar. Keine Aussage über fehlende Daten.']
    sources=run.get('sources',[]);good=sum(s.get('code') in SUCCESS for s in sources)
    lines+=['','Quellen: '+str(good)+' erfolgreich, '+str(len(sources)-good)+' nicht erfolgreich']
    previous={}
    for past in history(portal['id']):
        if past.get('started',0)>=run.get('started',0):
            continue
        for row in past.get('sources',[]):
            if row.get('code') in SUCCESS:
                previous[row['id']]=row.get('finished')
    for s in sources:
        lines+=['','[B]'+names.get(s['id'],'Früher konfigurierte Quelle')+'[/B]',meaning(s.get('code')),
                'Dauer: '+str(s.get('seconds',0))+' Sekunden']
        if 'bytes' in s:
            lines.append('Gelesene Bytes: '+str(s['bytes']))
        if 'programmes' in s:
            lines.append('Gelesen: '+str(s.get('channels',0))+' XMLTV-Kanäle / '+str(s['programmes'])+' Programme')
        elif 'channels' in s and 'stored' in s:
            lines.append('Geladen: '+str(s['channels'])+' Sender (XMLTV) / '+str(s['stored'])+' passende Sendungen')
        if 'selected_streams66' in s:
            lines.append('Zugeordnete IPTV-Streams: '+str(s.get('matched_streams66',0))+' / '+str(s['selected_streams66']))
        for channels,programmes,title in (
            ('mapped_channels66','stored_unique66','Staging'),
            ('committed_channels','committed','DB-Commit'),
            ('verified_channels','verified','Readback bestätigt'),
        ):
            if programmes in s:
                count=str(s[channels])+' XMLTV-Kanäle / ' if channels in s else ''
                lines.append(title+': '+count+str(s[programmes])+' Programme')
        if s.get('revision66'):lines.append('Quellrevision: '+s['revision66'][:16])
        if s.get('min_start66') and s.get('max_end66'):
            lines.append('Zuordnung und Zeitfilter · '+stamp(s['min_start66'])+' bis '+stamp(s['max_end66']))
        saved=s.get('saved',{})
        if saved.get('programmes') is not None:
            lines+=['Gespeichert: '+str(saved.get('channels',0))+' XMLTV-Kanäle / '+str(saved['programmes'])+' Programme',
                    stamp(saved.get('first'))+' bis '+stamp(saved.get('last'))]
        lines.extend(source_report(s,s.get('finished') if s.get('code') in SUCCESS else previous.get(s['id'])))
        if any(k in s for k in ('added','corrected','conflicts')):lines.append('Neu: '+str(s.get('added',0))+' · aktualisiert: '+str(s.get('corrected',0))+' · Konflikte bewahrt: '+str(s.get('conflicts',0)))
        if s.get('code') not in SUCCESS:
            lines.append(advice(s.get('code')))
    return '\n'.join(lines)

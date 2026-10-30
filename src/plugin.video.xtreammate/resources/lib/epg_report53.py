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


def statistics(pid):
    from guide_store import path as guide_path
    filename=guide_path();db=None
    if not os.path.isfile(filename):return dict(code='NOT_CREATED',sources=[],programmes=0,first=None,last=None)
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN');end=time.monotonic()+1
        db.set_progress_handler(lambda:int(time.monotonic()>end),1000)
        row=db.execute('SELECT count(*),min(start),max(stop) FROM programmes WHERE pid=?',(str(pid),)).fetchone()
        sources=[dict(id=r[0],channels=r[1],programmes=r[2],first=r[3],last=r[4]) for r in db.execute('SELECT source_id,count(DISTINCT cid),count(*),min(start),max(stop) FROM guide44_inputs WHERE pid=? GROUP BY source_id LIMIT 129',(str(pid),))]
        if len(sources)>128:return dict(code='BUDGET',sources=[],programmes=None,first=None,last=None)
        return dict(code='READY',sources=sources,programmes=row[0],first=row[1],last=row[2])
    except (OSError,sqlite3.Error):return dict(code='UNAVAILABLE',sources=[],programmes=None,first=None,last=None)
    finally:
        if db is not None:db.close()


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
    row.update(code=code,finished=time.time());row['seconds']=round(row['finished']-row['started'],3)
    for key in ('channels','stored','bytes'):
        value=(counts or {}).get(key)
        if isinstance(value,(int,float)) and value>=0:row[key]=value
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
    return {'REQUESTED':'Auftrag gespeichert; Übernahme durch den Dienst ausstehend','SERVICE_NOT_CONFIRMED':'Dienstübernahme noch nicht bestätigt; Dienststatus prüfen','DOWNLOADING':'XMLTV wird heruntergeladen','PARSING':'XMLTV wird gelesen und Sendern zugeordnet','SAVING':'EPG wird gespeichert','SOURCE_UNAVAILABLE':'Anbieter liefert keine XMLTV-Adresse','EMPTY_GUIDE':'Keine nutzbaren Sendungen im gelieferten XMLTV','NO_CHANNEL_MATCH':'XMLTV enthält Sendungen, aber keine passende eindeutige Senderzuordnung','INVALID_XMLTV':'Ungültiges XMLTV; Import verworfen','DOWNLOAD_TIMEOUT':'Zeitüberschreitung beim Download','DOWNLOAD_FAILED':'Download nicht möglich; Verbindung oder HTTP-Status prüfen','PARSE_TIMEOUT':'Zeitüberschreitung beim XMLTV-Lesen','PARSE_FAILED':'XMLTV konnte nicht verarbeitet werden','GZIP_INVALID':'Komprimierte XMLTV-Datei ungültig','CACHE_WRITE_FAILED':'Lokaler EPG-Cache konnte nicht gespeichert werden','STATUS_UNVERIFIED':'Früherer Status nicht durch gespeicherte Daten bestätigt','NO_SAVED_PROGRAMMES':'Noch keine gespeicherten Sendungen bestätigt','READY':'Erfolgreich gespeichert','READY_NO_NOW':'Gespeichert; aktuell keine laufende Sendung','PARTIAL_SUCCESS':'Teilweise erfolgreich','PARTIAL_PRESERVED':'Gespeichert; widersprüchliche Einträge geschützt','UNCHANGED':'Unverändert bestätigt','BACKUP_REQUIRED':'Verifizierte EPG-Sicherung erforderlich','WAIT_ACTIVE_CATALOG':'Senderkatalog noch nicht bereit','NO_NEW_GUIDE':'Keine neue gültige Programmliste','CANCELLED':'Abgebrochen; bisherige Daten bleiben erhalten','IMPORT_BUSY_OR_LOCK_UNAVAILABLE':'Ein EPG-Import läuft bereits','RUNNING':'Wird aktualisiert','DISABLED':'Deaktiviert','WAITING':'Noch kein Lauf bestätigt'}.get(code,'Aktualisierung fehlgeschlagen; bisherige Daten bleiben erhalten')


def advice(code):
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
    for rank,s in enumerate(configuration(portal['id'])['sources'],1):
        result.append(dict(id=source_id(s,rank),key=__import__('epg_status').source_key(s),name=label(s.get('name')),rank=rank,enabled=s.get('enabled',True),record=s))
    return result


def overview(portal):
    from epg_status import read
    stats=statistics(portal['id']);runs=history(portal['id']);state=read(portal['id']);rows=[]
    for item in configured(portal):
        row=dict(item);events=[s for run in runs for s in run.get('sources',[]) if s.get('id')==item['id']]
        saved=next((s for s in stats['sources'] if s['id']==item['id']),{})
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
        if row['code'] in SUCCESS:
            if stats['code']!='READY':row['code']='STATUS_UNVERIFIED'
            elif not saved.get('programmes'):row['code']='NO_SAVED_PROGRAMMES'
        row['progress59']={k:last[k] for k in ('bytes','programmes','count','http_status','failure_stage') if k in last}
        row['last_success']=max([s.get('finished',0) for s in events if s.get('code') in SUCCESS]+[legacy.get('last_success',0)])
        row['last_failure']=max([s.get('finished',0) for s in events if s.get('code') not in SUCCESS]+[0])
        rows.append(row)
    return rows


def describe(run,portal):
    names={r['id']:r['name'] for r in configured(portal)}
    lines=['Automatische Aktualisierung' if run.get('automatic') else 'Manuelle Aktualisierung',
           'Beginn: '+stamp(run.get('started')),'Dauer: '+str(run.get('seconds',0))+' Sekunden',meaning(run.get('code')),'',advice(run.get('code'))]
    after=run.get('after',{});before=run.get('before',{})
    if after.get('code')=='READY':
        lines+=['','Gespeicherte Programme: '+str(after['programmes']),'Zeitraum: '+stamp(after.get('first'))+' bis '+stamp(after.get('last'))]
        if before.get('programmes') is not None:lines.append('Bestand vorher / nachher: '+str(before['programmes'])+' / '+str(after['programmes']))
    else:lines+=['','Gespeicherter Zeitraum derzeit nicht sicher lesbar. Keine Aussage über fehlende Daten.']
    sources=run.get('sources',[]);good=sum(s.get('code') in SUCCESS for s in sources)
    lines+=['','Quellen: '+str(good)+' erfolgreich, '+str(len(sources)-good)+' nicht erfolgreich']
    for s in sources:
        lines+=['','[B]'+names.get(s['id'],'Früher konfigurierte Quelle')+'[/B]',meaning(s.get('code')),
                'Geladen: '+str(s.get('channels',0))+' Sender / '+str(s.get('stored',0))+' passende Sendungen',
                'Dauer: '+str(s.get('seconds',0))+' Sekunden']
        saved=s.get('saved',{})
        if saved:lines+=['Gespeichert: '+str(saved.get('channels',0))+' Sender / '+str(saved.get('programmes',0))+' Sendungen',stamp(saved.get('first'))+' bis '+stamp(saved.get('last'))]
        if any(k in s for k in ('added','corrected','conflicts')):lines.append('Neu: '+str(s.get('added',0))+' · aktualisiert: '+str(s.get('corrected',0))+' · Konflikte bewahrt: '+str(s.get('conflicts',0)))
        if s.get('code') not in SUCCESS:lines.append(advice(s.get('code')))
    return '\n'.join(lines)

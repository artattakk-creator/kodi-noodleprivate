"""Post-publication, independently resumable EPG sources on the existing guide.

Same cross-interpreter portal lease, import budget, backup gate and source
publisher as regular refresh. No fixed job duration. Receipts contain no URLs
or secrets; only completely validated and re-read sources can be skipped.
"""
import hashlib,json,os,sqlite3,time,uuid
from urllib.parse import quote


def path(portal):
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'epg_setup54_'+hashlib.sha256(str(portal['id']).encode()).hexdigest()[:24]+'.json')


def read(portal):
    from wizard_resume53 import read_file
    try:
        value=read_file(path(portal))
        return value if isinstance(value,dict) and value.get('version')==1 and value.get('pid')==str(portal['id']) else None
    except (OSError,ValueError,TypeError):return None


def write(portal,state):
    # Existing profile permissions are not changed by the private-file writer.
    import tempfile,stat
    filename=path(portal);temp=None;raw=json.dumps(state,separators=(',',':')).encode()
    if len(raw)>1024*1024 or os.path.islink(filename):raise OSError('EPG_CHECKPOINT_UNSAFE')
    fd,temp=tempfile.mkstemp(prefix='.epg-setup54-',dir=os.path.dirname(filename))
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(temp,filename);temp=None
    finally:
        if temp:
            try:os.unlink(temp)
            except OSError:pass


def prepare(portal):
    state=read(portal)
    if state is None:
        from epg_sources import configuration
        enabled=portal.get('provider_epg_enabled',True) or any(s.get('enabled',True) for s in configuration(portal['id'])['sources'])
        state=dict(version=1,pid=str(portal['id']),phase='PENDING' if enabled else 'NONE',sources={},updated=time.time())
        write(portal,state)
    return state


def pending(portal):
    state=read(portal)
    return bool(state and state.get('phase') not in ('READY','NONE'))


def signature(portal,source,rank):
    from epg_sources import configuration
    from library_index import connect
    db=connect();heads=[]
    try:
        if db is not None:heads=[tuple(r) for r in db.execute("SELECT cid,generation FROM heads WHERE pid=? AND kind='live' ORDER BY cid",(str(portal['id']),))]
    finally:
        if db is not None:db.close()
    conf=configuration(portal['id'])
    # Only a one-way configuration identity is persisted, never the URI.
    return hashlib.sha256(json.dumps([54,source,rank,heads,conf['mappings'],getattr(conf['mappings'],'sources48',{})],sort_keys=True).encode()).hexdigest()


def stored(portal,identity,cancel=lambda:False,status=lambda *a:None):
    from guide_store import path as guide_path
    if not os.path.isfile(guide_path()):return None
    db=sqlite3.connect('file:'+quote(guide_path(),safe='/')+'?mode=ro',uri=True,timeout=.1)
    try:
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        # Cancels cooperatively even inside quick_check / large SQL sorting.
        db.set_progress_handler(lambda:int(cancel()),1000)
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':return None
        h=hashlib.sha256();count=0;first=None;last=None
        for row in db.execute('SELECT cid,start,stop,title,description,rank FROM guide44_inputs WHERE pid=? AND source_id=? ORDER BY cid,start,stop',(str(portal['id']),identity)):
            if cancel():raise InterruptedError('EPG_CANCELLED')
            h.update(json.dumps(row,ensure_ascii=False,separators=(',',':')).encode());h.update(b'\n');count+=1
            first=row[1] if first is None else min(first,row[1]);last=row[2] if last is None else max(last,row[2])
            if count%1024==0:status(None,'Gespeicherte EPG-Daten werden geprüft · '+str(count)+' Sendungen')
        return dict(rows=count,digest=h.hexdigest(),first=first,last=last)
    except sqlite3.Error:
        if cancel():raise InterruptedError('EPG_CANCELLED')
        return None
    finally:db.close()


def plans(portal):
    from epg_sources import configuration
    from guide_publish44 import source_id
    from epg_status import source_key
    from source_adapters import for_portal
    result=[]
    if portal.get('provider_epg_enabled',True):
        try:uri=portal.get('epg_url') or for_portal(portal).get_xmltv_epg_url() or ''
        except Exception:uri=''
        result.append(('provider','provider',dict(uri=uri,local=not uri.startswith(('http://','https://')),_plan_error54=not bool(uri)),0,'Anbieter-EPG'))
    from epg_report53 import label
    for rank,s in enumerate(configuration(portal['id'])['sources'],1):
        if s.get('enabled',True):result.append((source_id(s,rank),source_key(s),s,rank,label(s.get('name'))))
    return result


def run(portal,cancel=lambda:False,status=lambda *a:None):
    from portals import get_by_id
    if get_by_id(portal['id']) is None:raise ValueError('EPG_REQUIRES_PUBLISHED_PORTAL')
    from stream_epg import portal_lease44
    with portal_lease44(portal['id']) as held:
        if not held:raise OSError('EPG_IMPORT_BUSY')
        return _run(portal,cancel,status)


def _run(portal,cancel,status):
    from epg_gate46 import access
    from guide_store import path as guide_path
    from stream_epg import active_streams,import_source,publish_stages44,discard_stages44
    from epg_sources import configuration
    from epg_status import update
    from epg_report53 import observing,started,source_done
    state=prepare(portal);state.update(phase='RUNNING',updated=time.time());write(portal,state)
    try:configured=plans(portal)
    except Exception:
        state.update(phase='PARTIAL',code='SOURCE_UNAVAILABLE');write(portal,state);raise
    if not configured:
        state['phase']='NONE';write(portal,state);return state
    streams=list(active_streams(portal));mappings=configuration(portal['id'])['mappings']
    if not streams:
        state.update(phase='PARTIAL',code='WAIT_ACTIVE_CATALOG');write(portal,state);return state
    try:
        with observing(portal['id']) as report:
            authorized=None
            for number,(identity,key,source,rank,name) in enumerate(configured,1):
                if cancel():raise InterruptedError('EPG_CANCELLED')
                prefix='EPG-Quelle '+str(number)+' von '+str(len(configured))+' · '+name
                if source.get('_plan_error54'):
                    state['sources'][identity]=dict(code='SOURCE_UNAVAILABLE');write(portal,state)
                    started(portal['id'],key,identity,rank);source_done(portal['id'],identity,'SOURCE_UNAVAILABLE')
                    update(portal['id'],key,'SOURCE_UNAVAILABLE',running=False)
                    status(None,prefix+'\nQuelle derzeit nicht verfügbar; weitere Quellen werden unabhängig geprüft.')
                    continue
                fingerprint=signature(portal,source,rank);old=state['sources'].get(identity,{})
                if old.get('code')=='READY' and old.get('fingerprint')==fingerprint and 0<=time.time()-old.get('completed',0)<86400:
                    actual=stored(portal,identity,cancel,status)
                    if actual and actual==old.get('verified'):
                        status(None,prefix+'\nBereits vollständig geprüft · '+str(actual['rows'])+' Sendungen');continue
                if authorized is None:
                    authorized=access(guide_path())
                    if authorized not in ('READY','NOT_CREATED'):
                        state.update(phase='PARTIAL',code=authorized);write(portal,state)
                        update(portal['id'],'refresh',authorized,running=False)
                        return state
                previous_generation=old.get('generation','')
                if isinstance(previous_generation,str) and len(previous_generation)==32 and all(c in '0123456789abcdef' for c in previous_generation):
                    exists=False
                    if os.path.isfile(guide_path()):
                        db=sqlite3.connect('file:'+quote(guide_path(),safe='/')+'?mode=ro',uri=True,timeout=.1)
                        try:exists=bool(db.execute("SELECT 1 FROM sqlite_master WHERE name='xml_stage'").fetchone())
                        finally:db.close()
                    if exists:discard_stages44([dict(generation=previous_generation,meta_pid46=str(portal['id']))])
                generation=uuid.uuid4().hex
                state['sources'][identity]=dict(code='RUNNING',fingerprint=fingerprint,generation=generation);write(portal,state)
                started(portal['id'],key,identity,rank);stage=None
                def progress(value):
                    phase={'DOWNLOAD':'Download läuft','PARSE':'XMLTV-Datei wird verarbeitet und Sendern zugeordnet','SAVING':'EPG-Daten werden gespeichert'}.get(value['phase'],'Quelle wird geprüft')
                    status(None,prefix+'\n'+phase+'\n'+str(value.get('bytes',0))+' Bytes · '+str(value.get('programmes',0))+' Sendungen gelesen · '+str(value.get('stored',0))+' zugeordnet')
                status(None,prefix+'\nDownload läuft')
                try:
                    stage=import_source(portal['id'],source,rank,streams,mappings,cancel=cancel,stage_only=True,progress=progress,generation54=generation)
                    status(None,prefix+'\nEPG-Daten werden gespeichert')
                    outcome=publish_stages44(portal['id'],[stage],cancel=cancel)[0]
                    actual=stored(portal,identity,cancel,status)
                    if not actual or not actual['rows']:raise ValueError('EPG_PUBLICATION_UNVERIFIED')
                    state['sources'][identity]=dict(code='READY',fingerprint=fingerprint,completed=time.time(),verified=actual)
                    write(portal,state)
                    counts=stage['counts'];update(portal['id'],key,'READY',running=False,source_index=rank,channels=counts['channels'],programmes=counts['stored'],bytes=counts['bytes'])
                    source_done(portal['id'],identity,'READY',counts,outcome)
                    status(None,prefix+'\nQuelle erfolgreich abgeschlossen · '+str(actual['rows'])+' gespeicherte Sendungen')
                except InterruptedError:raise
                except Exception as exc:
                    from epg_errors import failure_details
                    code,fields=failure_details(exc,getattr(exc,'xcmate_stage','MERGE'))
                    state['sources'][identity]=dict(code=code,fingerprint=fingerprint);write(portal,state)
                    update(portal['id'],key,code,running=False,**fields);source_done(portal['id'],identity,code)
                    status(None,prefix+'\nQuelle nicht abgeschlossen. Portal und bisherige Daten bleiben erhalten.')
                finally:
                    if stage:discard_stages44([stage])
            state['phase']='READY' if all(state['sources'].get(p[0],{}).get('code')=='READY' for p in configured) else 'PARTIAL'
            state.update(updated=time.time(),code=state['phase']);write(portal,state)
            update(portal['id'],'refresh','READY' if state['phase']=='READY' else 'PARTIAL_SUCCESS',running=False,loaded=sum(state['sources'].get(p[0],{}).get('code')=='READY' for p in configured),failed=sum(state['sources'].get(p[0],{}).get('code')!='READY' for p in configured))
            report['result']=state['phase']=='READY'
            return state
    except BaseException:
        state.update(phase='PARTIAL',updated=time.time());write(portal,state)
        update(portal['id'],'refresh','CANCELLED',running=False)
        raise

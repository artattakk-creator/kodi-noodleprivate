"""Large XMLTV imports: streaming SAX → staged SQLite → shared fast snapshot.

Only enabled sender IDs/names are persisted; failed sources retain prior rows.
An explicit/manual bulk refresh is separate from startup short-EPG preparation.
"""
from contextlib import contextmanager
import os
import sqlite3
import time
import uuid


def active_streams(portal):
    from library_index import Reader
    reader=Reader(portal['id']);offset=0
    while True:
        rows,total=reader.page('live',offset=offset,limit=100)
        yield from rows
        offset+=len(rows)
        if not rows or offset>=total: break


@contextmanager
def source_stream(source,cancel=lambda:False):
    uri=source['uri']
    if source.get('_agent_artwork'):
        with open(uri, 'rb') as stream:
            yield stream
    elif source.get('local'):
        import xbmcvfs
        class Reader:
            def __init__(self): self.file=xbmcvfs.File(uri)
            def read(self,n): return b'' if n==0 else bytes(self.file.readBytes(n))
        stream=Reader()
        try: yield stream
        finally: stream.file.close()
    else:
        from utils import http_stream
        with http_stream(uri,cancel=cancel) as stream: yield stream


def import_source(pid,source,source_index,streams,mappings,filename=None,cancel=lambda:False,stage_only=False,progress=None,generation54=None):
    from epg_progress54 import Progress
    progress54=Progress(progress)
    from guide_store import connect,path
    from epg_sources import _channel_name_key
    from xmltv_stream import parse
    from epg_horizon102 import Coverage
    from import_budget import check_space
    db=connect(filename,write=True);target=filename or path();generation=generation54 or uuid.uuid4().hex
    if len(generation)!=32 or any(c not in '0123456789abcdef' for c in generation):db.close();raise ValueError('INVALID_IMPORT_GENERATION')
    from guide_publish44 import require
    try:require(db)
    except Exception:db.close();raise
    db.execute('''CREATE TABLE IF NOT EXISTS xml_stage(generation TEXT,cid TEXT,start INTEGER,stop INTEGER,
        title TEXT,description TEXT,PRIMARY KEY(generation,cid,start,stop))''')
    # No executable source content, URLs or provider credentials enter SQLite.
    ids=set();names={};aliases={};channel_names={};variant_names53={}
    stream_rows53={str(row['sid']):row for row in streams}
    for row in streams:
        sid=row['sid'];eid=str(mappings.get(sid) or row.get('epg_channel_id') or '')
        if eid: ids.add(eid);aliases[sid]=eid
        key=_channel_name_key(row.get('name'))
        if key:names.setdefault(key,[]).append(sid)
    from programme_store46 import Stage as ProgrammeStage46
    metadata46=ProgrammeStage46(pid,generation,source_index,filename,source_identity=__import__('guide_publish44').source_id(source,source_index))
    batch=[];stored=0;unique94=0;now=time.time();keep_stage=False;right46=__import__('programme_index46').bounds(now)[1]
    left=__import__('guide_store').day_window(-7,now)[0]
    raw_horizon=Coverage(now)
    agent_artwork=source.get('_agent_artwork')
    agent_channels={};agent_icons={};agent_matched=False
    if agent_artwork:
        from epg_agent100_art import event_art, validator
        admit_agent_art=validator()
    staged_channels=set()
    def flush():
        nonlocal unique94
        if not batch: return
        check_space(target,sum(len(r[-1])+len(r[-2]) for r in batch)*4)
        with db:
            before94=db.total_changes
            db.executemany('INSERT OR IGNORE INTO xml_stage VALUES(?,?,?,?,?,?)',batch)
            unique94+=db.total_changes-before94
            db.executemany('UPDATE xml_stage SET title=?,description=? WHERE generation=? AND cid=? AND start=? AND stop=? AND length(description)<?',[(r[4],r[5],*r[:4],len(r[5])) for r in batch])
        staged_channels.update(r[1] for r in batch)
        batch.clear()
        progress54.emit('STAGING',stored=unique94,staged_channels=len(staged_channels))
    def channel(cid,name):
        metadata46.channel48(cid,name)
        if agent_artwork:
            agent_channels[cid]=name
            return
        key=_channel_name_key(name)
        # Only requested names are remembered. Ambiguous XMLTV names do not
        # overwrite provider/manual IDs; match conservatively at source end.
        if key in names:
            from epg_variant53 import compatible
            if not any(compatible(stream_rows53[str(sid)].get('name'),stream_rows53[str(sid)].get('epg_channel_id'),name,cid) for sid in names[key]):return
            variant_names53[cid]=name
            if key in channel_names and channel_names[key]!=cid: channel_names[key]=None
            elif key not in channel_names: channel_names[key]=cid
            ids.add(cid)
    def channel_icon(cid,url):
        if cid not in agent_icons and admit_agent_art(url):
            agent_icons[cid]=url
    def programme(event):
        nonlocal stored,agent_matched
        raw_horizon.add(event['channel'],event['start_timestamp'],event['stop_timestamp'])
        if agent_artwork and not agent_matched:
            from epg_agent100_import import match
            aliases.clear();aliases.update(match(agent_channels,streams,mappings))
            ids.clear();ids.update(aliases.values())
            agent_matched=True
        if event['channel'] not in ids or event['stop_timestamp']<=left: return
        if not event['name']: return
        if event['start_timestamp']>=right46:return
        if agent_artwork:
            references=event_art(event,admit_agent_art)
            if references:event['agent_art']=references
            event.pop('screenshot_uri',None)  # Keep only the admitted references.
        metadata46.add(event)  # Independent cache may keep real feed days11–20.
        batch.append((generation,event['channel'],event['start_timestamp'],event['stop_timestamp'],event['name'],event['descr']))
        stored+=1
        if len(batch)>=256: flush()
    try:
        # A previous interrupted stage is invisible. Cleanup affects staging
        # only, never a published programme or user's source configuration.
        # Each import owns only its generation; no deletion of another stage.
        phase='DOWNLOAD'
        http_status=None
        try:
            parse_options=dict(include_icons=True,include_images=True,strict_images=True,
                               channel_image=channel_icon,max_seconds=720) if agent_artwork else {}
            with source_stream(source,cancel=cancel) as stream:
                phase='PARSE'
                http_status=getattr(stream,'http_status',None)
                if progress:counts=parse(progress54.wrap(stream),channel,programme,cancel,progress=progress54.parsed,**parse_options)
                else:counts=parse(stream,channel,programme,cancel,**parse_options)
        except Exception as exc:
            try:
                exc.xcmate_stage=phase
                if http_status is not None:
                    exc.epg_counts102=dict(http_status=http_status)
            except Exception: pass
            raise
        counts['raw_horizon102']=raw_horizon.result()
        if http_status is not None:
            counts['http_status']=http_status
        if source.get('_agent_folder102'):
            from epg_agent_hub5 import coverage_report
            counts['profiles102']=coverage_report(source['_agent_folder102'],aliases)
        flush();metadata46.flush()
        progress54.emit('MATCHING',force=True,stored=unique94)
        if not stored:
            from epg_errors import EmptyGuideError
            error=EmptyGuideError('No matching current programmes')
            error.xcmate_no_match59=bool(counts.get('programmes'))
            error.epg_counts102=dict(counts,selected_streams66=len(streams),matched_streams66=0)
            raise error
        for key,sids in (() if agent_artwork else names.items()):
            cid=channel_names.get(key)
            if cid:
                for sid in sids:
                    from epg_variant53 import compatible
                    if not compatible(stream_rows53[str(sid)].get('name'),stream_rows53[str(sid)].get('epg_channel_id'),variant_names53.get(cid,''),cid):continue
                    if sid not in mappings and (sid not in aliases or aliases[sid] not in ids): aliases[sid]=cid
                    # An absent provider EPG ID can be repaired by an exact,
                    # unambiguous source name; manual mapping always wins.
                    elif sid not in mappings and not db.execute('SELECT 1 FROM xml_stage WHERE generation=? AND cid=? LIMIT 1',(generation,aliases[sid])).fetchone(): aliases[sid]=cid
        check_space(target)
        with db:
            from epg_events import clean_stage
            clean_stage(db,'xml_stage',' WHERE generation=?',(generation,))
        from epg_source66 import receipt
        counts.update(receipt(db,generation))
        counts['stored']=counts['stored_unique66']
        counts['selected_streams66']=len(streams)
        counts['matched_streams66']=sum(bool(db.execute('SELECT 1 FROM xml_stage WHERE generation=? AND cid=? LIMIT 1',(generation,cid)).fetchone()) for cid in aliases.values())
        progress54.emit('MATCHING',force=True,stored=counts['stored'],
                        matched=counts['matched_streams66'],matched_channels=counts['mapped_channels66'],
                        staged_channels=counts['mapped_channels66'],selected_streams=len(streams))
        stage=dict(generation=generation,source=source,index=source_index,aliases=aliases,meta_pid46=str(pid),metadata_ok46=not metadata46.failed,index_ok46=not metadata46.facts46.failed,
                   now=now,counts=dict(counts),streams52=streams,mappings52=mappings,proofs52={str(row['sid']):('manual' if str(row['sid']) in mappings else 'name' if channel_names.get(_channel_name_key(row.get('name')))==aliases.get(str(row['sid'])) and __import__('epg_variant53').compatible(row.get('name'),row.get('epg_channel_id'),variant_names53.get(aliases.get(str(row['sid'])),''),aliases.get(str(row['sid']))) else 'provider_id') for row in streams})
        if agent_artwork:
            if metadata46.failed or metadata46.facts46.failed:
                raise OSError('AGENT_METADATA_STAGING_FAILED')
            stage['proofs52']={sid:('manual' if sid in mappings else 'name') for sid in aliases}
            stage['agent_icons']=agent_icons
        if stage_only:
            keep_stage=True
            return stage
        outcome=publish_stages44(pid,[stage],filename,cancel)[0]
        counts.update(publish_code=outcome['code'],added=outcome['added'],corrected=outcome['corrected'],conflicts=outcome['conflicts'])
        return counts
    finally:
        # SQL rollback restores the complete previous guide on ENOSPC or error.
        db.rollback()
        if not keep_stage:
            metadata46.finish(False)
            try:
                with db: db.execute('DELETE FROM xml_stage WHERE generation=?',(generation,))
            except Exception: pass
        db.close()


def discard_stages44(stages,filename=None):
    if not stages:return
    from guide_store import connect
    db=connect(filename,write=True)
    try:
        with db:
            for stage in stages:db.execute('DELETE FROM xml_stage WHERE generation=?',(stage['generation'],))
        from programme_store46 import finish as finish_metadata46
        for stage in stages:finish_metadata46(stage.get('meta_pid46',''),stage['generation'],False,filename)
    finally:db.close()


def publish_stages44(pid,stages,filename=None,cancel=lambda:False):
    """All verified sources become visible at one commit/revision, never midway."""
    from guide_store import connect
    from guide_publish44 import publish,source_id
    db=connect(filename,write=True);outcomes=[];proofs94=[];revision='stream-'+uuid.uuid4().hex
    try:
        with db:
            old=db.execute('SELECT revision FROM guide_meta WHERE pid=?',(pid,)).fetchone()
            changed=False
            for stage in stages:
                if cancel():raise InterruptedError('EPG import cancelled')
                generation=stage['generation']
                outcome=publish(db,pid,'xml_stage','generation=?',(generation,),source=source_id(stage['source'],stage['index']),
                    rank=stage['index'],revision=revision,now=stage['now'],cancel=cancel,correct_times66=True)
                outcomes.append(outcome)
                before=db.total_changes
                for alias,cid in (() if stage['source'].get('_agent_artwork') else stage['aliases'].items()):
                    if db.execute('SELECT 1 FROM xml_stage WHERE generation=? AND cid=? LIMIT 1',(generation,cid)).fetchone():
                        db.execute('INSERT OR IGNORE INTO guide_alias VALUES(?,?,?)',(pid,alias,cid))
                changed=changed or db.total_changes!=before
                db.execute('DELETE FROM xml_stage WHERE generation=?',(generation,))
            current=db.execute('SELECT revision FROM guide_meta WHERE pid=?',(pid,)).fetchone()
            if changed or current!=old:db.execute('INSERT OR REPLACE INTO guide_meta VALUES(?,?,?)',(pid,revision,time.time()))
            if outcomes:
                import json
                totals={k:sum(o[k] for o in outcomes) for k in ('incoming','added','corrected','conflicts')}
                code='PARTIAL_PRESERVED' if totals['conflicts'] else 'VERIFIED' if totals['added'] or totals['corrected'] else 'UNCHANGED'
                db.execute('INSERT OR REPLACE INTO guide44_outcomes VALUES(?,?,?)',(pid,code,json.dumps(totals)))
            if cancel():raise InterruptedError('EPG import cancelled')
            from epg_readback94 import digest
            for stage in stages:
                identity94=source_id(stage['source'],stage['index'])
                expected94=digest(db,pid,identity94,cancel)
                proof_revision94=db.execute('SELECT revision FROM guide_meta WHERE pid=?',(pid,)).fetchone()[0]
                proofs94.append((stage,identity94,expected94,proof_revision94))
            if getattr(cancel,'fresh',cancel)():raise InterruptedError('EPG import cancelled')
        from epg_readback94 import verify
        from guide_store import path as guide_path94
        for stage,identity94,expected94,proof_revision94 in proofs94:
            observe94=stage.get('observe94',lambda *a,**k:None)
            observe94('READBACK',committed=expected94['rows'],committed_channels=expected94['channels'])
            stage['verified94']=verify(filename or guide_path94(),pid,identity94,expected94,
                                       proof_revision94,cancel,lambda count:observe94('READBACK',readback_rows=count))
            observe94('CLEANUP',verified=stage['verified94']['rows'],
                      verified_channels=stage['verified94']['channels'],raw_deleted_bytes=0)
        from programme_store46 import finish as finish_metadata46
        for stage in stages:
            finish_metadata46(pid,stage['generation'],stage.get('metadata_ok46',True),filename,index_ok46=stage.get('index_ok46',True),index_publish46=True)
            from epg_merge52 import publish_aliases
            publish_aliases(pid,source_id(stage['source'],stage['index']),stage['aliases'],stage.get('streams52',()),stage.get('mappings52',{}),filename,proofs=stage.get('proofs52'))
            agent_index=stage['source'].get('_agent_artwork')
            if agent_index:
                from epg_agent100_art import bind_streams
                bind_streams(agent_index,pid,stage['aliases'],stage['agent_icons'])
        if filename is None and proofs94:
            try:
                cleanup94=__import__('epg_cleanup94').confirmed(pid,proofs94[-1][3])
                for stage in stages:
                    stage['cleanup94']=cleanup94
                    stage.get('observe94',lambda *a,**k:None)('CLEANUP',free_before=cleanup94['free_before'],free_after=cleanup94['free_after'],raw_deleted_bytes=0)
            except (OSError,ValueError,sqlite3.Error):
                # A failed inventory is not an import failure and authorizes
                # no deletion. Leave explicit evidence instead of success.
                for stage in stages:stage['cleanup94']=dict(code='CLEANUP_UNVERIFIED',raw_deleted_bytes=0)
        return outcomes
    finally:db.close()


@contextmanager
def portal_lease44(pid):
    """OS releases this nonblocking advisory lease even after interpreter death."""
    import hashlib
    from guide_store import path
    filename=path()+'.refresh44-'+hashlib.sha256(str(pid).encode()).hexdigest()[:24]+'.lock'
    os.makedirs(os.path.dirname(filename),exist_ok=True)
    f=open(filename,'a+b');locked=False
    try:
        try:
            import fcntl
            fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB);locked=True
        except ImportError:
            # No unsafe parallel importer on unsupported platforms.
            pass
        except (OSError,BlockingIOError):pass
        yield locked
    finally:
        if locked:fcntl.flock(f.fileno(),fcntl.LOCK_UN)
        f.close()


def fast_snapshot(pid,streams,mappings):
    from guide_store import events
    now=int(time.time());result={}
    for row in streams:
        sid=row['sid'];key=mappings.get(sid) or sid
        rows,_=events(pid,key,now,now+2*86400,limit=4)
        if not rows and not mappings.get(sid): rows,_=events(pid,row.get('epg_channel_id',''),now,now+2*86400,limit=4)
        if not rows: continue
        entries=[dict(channel=r['cid'],name=r['title'],descr=r['description'],start_timestamp=r['start'],stop_timestamp=r['stop'],_source_index=r['source']) for r in rows]
        canonical=entries[0]['channel']
        result[canonical]=entries;result[sid]=entries
    return result


def refresh(portal,force=False,cancel=lambda:False):
    from epg_status import update
    with portal_lease44(portal['id']) as held:
        if not held:
            update(portal['id'],'refresh','IMPORT_BUSY_OR_LOCK_UNAVAILABLE',running=False)
            return {}
        return _refresh44(portal,force,cancel)


def _refresh44(portal,force=False,cancel=lambda:False):
    from guide_store import path as guide_path46
    from epg_gate46 import access as refresh_access46
    filename=guide_path46()
    state46=refresh_access46(filename)
    if (state46 == 'DB_AUTHORIZATION_MISSING' and portal.get('epg_show', True)
            and (portal.get('_agent_source') or {}).get('_agent_public102') and not cancel()):
        from guide_backup44 import authorize
        authorize(filename, cancel, current_schema_only=True)
        state46=refresh_access46(filename)
    if state46 not in ('READY','NOT_CREATED'):
        from epg_status import update
        update(portal['id'],'refresh',state46,running=False)
        return {}
    from epg_sources import configuration
    from epg_status import update,source_key
    from epg_errors import failure_details
    from source_adapters import for_portal
    from epg import _save_disk,_mem_set
    pid=portal['id']
    identity94=portal.get('_epg_job94')
    def observe94(key,phase,**counts):
        if identity94:
            try:__import__('epg_jobs94').observe(pid,identity94,key,phase,**counts)
            except OSError:update(pid,'telemetry94','STATUS_WRITE_DEFERRED',running=True)
    if not portal.get('epg_show',True):
        update(pid,'refresh','EPG_DISABLED',running=False);return {}
    from guide_store import connect
    from guide_publish44 import ready
    db=connect()
    try:allowed=ready(db)
    finally:db.close()
    if not allowed:
        update(pid,'refresh','BACKUP_REQUIRED',running=False)
        return {}
    streams=list(active_streams(portal));config=configuration(pid)
    if not streams:
        update(pid,'cache','WAIT_ACTIVE_CATALOG',running=False)
        from catalog_sync import request
        request(portal,'live',portal.get('start_group_id',''),priority=0)
        return {}
    if not portal.get('epg_show',True): return {}
    from epg_report53 import started as source_started53,source_done as source_done53
    selected53=portal.get('_epg_sources53')
    agent_source=portal.get('_agent_source')
    provider_failure52=0;uri=''
    if portal.get('provider_epg_enabled',True) and (selected53 is None or 'provider' in selected53):
        try:uri=portal.get('epg_url') or for_portal(portal).get_xmltv_epg_url() or ''
        except Exception as exc:
            code,fields=failure_details(exc,'DOWNLOAD')
            update(pid,'provider',code,running=False,**fields);provider_failure52=1
            source_started53(pid,'provider','provider',0);source_done53(pid,'provider',code,fields)
            observe94('provider','FAILED',error_code=code)
    if portal.get('provider_epg_enabled',True) and (selected53 is None or 'provider' in selected53) and not uri and not provider_failure52:
        provider_failure52=1
        update(pid,'provider','SOURCE_UNAVAILABLE',running=False)
        source_started53(pid,'provider','provider',0);source_done53(pid,'provider','SOURCE_UNAVAILABLE')
        observe94('provider','FAILED',error_code='SOURCE_UNAVAILABLE')
    provider=dict(uri=uri,local=not uri.startswith(('http://','https://')))
    sources=([('provider',provider,0)] if uri and portal.get('provider_epg_enabled',True) else [])+[(source_key(s),s,i) for i,s in enumerate(config['sources'],1) if s.get('enabled',True)]
    if agent_source:
        from epg_agent100 import SOURCE_RANK, SOURCE_ID
        sources.append((SOURCE_ID,agent_source,SOURCE_RANK))
    if selected53 is not None:
        from guide_publish44 import source_id
        sources=[s for s in sources if source_id(s[1],s[2]) in selected53]
    successes=0;failures=provider_failure52;stages=[]
    for number94,(key,source,index) in enumerate(sources,1):
        observe94(key,'DOWNLOAD',source_index=number94,sources=len(sources))
        if cancel(): break
        identity53=__import__('guide_publish44').source_id(source,index)
        source_started53(pid,key,identity53,index)
        update(pid,key,'RUNNING',running=True,source_index=index)
        try:
            last_progress59=[0,'',0]
            def progress59(value):
                now59=time.monotonic()
                if now59-last_progress59[0]<.5 and value.get('phase')==last_progress59[1] and value.get('matched',0)==last_progress59[2]:return
                last_progress59[:]=[now59,value.get('phase'),value.get('matched',0)]
                extra={name:value[name] for name in ('staged_channels','matched_channels','selected_streams') if name in value}
                observe94(key,value.get('phase','PARSE'),bytes=value.get('bytes',0),total_bytes=value.get('total_bytes',0),channels=value.get('channels',0),programmes=value.get('programmes',0),staged=value.get('stored',0),matched=value.get('matched',0),**extra)
                code59={'DOWNLOAD':'DOWNLOADING','PARSE':'PARSING','STAGING':'SAVING','MATCHING':'PARSING'}.get(value.get('phase'),'RUNNING')
                update(pid,key,code59,running=True,source_index=index,bytes=value.get('bytes',0),programmes=value.get('programmes',0),channels=value.get('channels',0),count=value.get('stored',0))
            stage=import_source(pid,source,index,streams,config['mappings'],cancel=cancel,stage_only=True,progress=progress59)
            stage['key']=key;stage['observe94']=lambda phase,_key=key,**counts:observe94(_key,phase,**counts);stages.append(stage)
            update(pid,key,'VERIFIED',running=True,source_index=index)
        except Exception as exc:
            code,fields=failure_details(exc,getattr(exc,'xcmate_stage','MERGE'))
            observe94(key,'FAILED',error_code=code)
            update(pid,key,code,running=False,source_index=index,**fields);failures+=1
            source_done53(pid,identity53,code,dict(getattr(exc,'epg_counts102',{}),**fields))
    if cancel():
        discard_stages44(stages)
        for stage in stages:update(pid,stage['key'],'CANCELLED',running=False)
        update(pid,'refresh','CANCELLED',running=False)
        return {}
    try:
        for stage94 in stages:stage94['observe94']('COMMIT')
        outcomes=publish_stages44(pid,stages,cancel=cancel) if stages else []
    except Exception as exc:
        discard_stages44(stages)
        code,fields=failure_details(exc,'MERGE')
        for stage in stages:
            stage['observe94']('FAILED',error_code=code)
            update(pid,stage['key'],code,running=False,**fields)
            identity53=__import__('guide_publish44').source_id(stage['source'],stage['index'])
            source_done53(pid,identity53,code,dict(stage['counts'],**fields))
        update(pid,'refresh',code,running=False,**fields)
        return {}
    for stage,outcome in zip(stages,outcomes):
        counts=stage['counts'];successes+=1
        verified95=stage['verified94']
        final=dict(committed=verified95['rows'],verified=verified95['rows'],
                   committed_channels=verified95['channels'],verified_channels=verified95['channels'])
        stage['observe94']('DONE',matched=counts.get('matched_streams66',0),
                           staged=counts.get('stored_unique66',counts['stored']),
                           matched_channels=counts['mapped_channels66'],staged_channels=counts['mapped_channels66'],
                           selected_streams=counts['selected_streams66'],
                           first=verified95['first'],last=verified95['last'],**final)
        history_counts95=dict(counts,verified_first=verified95['first'],verified_last=verified95['last'],**final)
        source_done53(pid,__import__('guide_publish44').source_id(stage['source'],stage['index']),'PARTIAL_PRESERVED' if outcome['code']=='PARTIAL_PRESERVED' else 'READY',history_counts95,outcome)
        update(pid,stage['key'],'PARTIAL_PRESERVED' if outcome['code']=='PARTIAL_PRESERVED' else 'READY',running=False,
            source_index=stage['index'],channels=counts['channels'],programmes=counts['stored'],bytes=counts['bytes'])
    if agent_source:
        receipt=portal.get('_agent_result')
        if outcomes:
            stage=stages[-1];counts=stage['counts'];verified=stage['verified94']['rows']
            receipt.update(code='READY',read=counts['programmes'],mapped_channels=counts['mapped_channels66'],
                           matched=counts['matched_streams66'],committed=verified,verified=verified)
            update(pid,'refresh','READY',running=False,loaded=1)
        else:
            from epg_status import read
            state=read(pid).get('agent',{})
            receipt.update(code=state.get('code','NO_NEW_GUIDE'))
            update(pid,'refresh',receipt['code'],running=False)
        return {}
    result=fast_snapshot(pid,streams,config['mappings'])
    if successes and result:
        _save_disk(pid,result);_mem_set(pid,result)
        from epg_sources import _channels_cache_key
        from utils import cache_set
        # Mapping chooser receives the relevant canonical IDs after a large
        # import too; user configuration itself is never overwritten.
        cache_set(_channels_cache_key(pid),{str(e.get('channel')):r.get('name','')
            for r in streams for e in result.get(r['sid'],[])[:1]})
        update(pid,'refresh','READY' if not failures else 'PARTIAL_SUCCESS',running=False,loaded=successes,failed=failures)
        return result
    update(pid,'refresh','READY_NO_NOW' if successes else 'NO_NEW_GUIDE',running=False,loaded=successes,failed=failures)
    return {}

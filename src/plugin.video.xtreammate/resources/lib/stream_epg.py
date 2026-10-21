"""Large XMLTV imports: streaming SAX → staged SQLite → shared fast snapshot.

Only enabled sender IDs/names are persisted; failed sources retain prior rows.
An explicit/manual bulk refresh is separate from startup short-EPG preparation.
"""
from contextlib import contextmanager
import os
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
    if source.get('local'):
        import xbmcvfs
        class Reader:
            def __init__(self): self.file=xbmcvfs.File(uri)
            def read(self,n): return bytes(self.file.readBytes(n))
        stream=Reader()
        try: yield stream
        finally: stream.file.close()
    else:
        from utils import http_stream
        with http_stream(uri,cancel=cancel) as stream: yield stream


def import_source(pid,source,source_index,streams,mappings,filename=None,cancel=lambda:False):
    from guide_store import connect,path
    from epg_sources import _channel_name_key
    from xmltv_stream import parse
    from import_budget import check_space
    db=connect(filename,write=True);target=filename or path();generation=uuid.uuid4().hex
    db.execute('''CREATE TABLE IF NOT EXISTS xml_stage(generation TEXT,cid TEXT,start INTEGER,stop INTEGER,
        title TEXT,description TEXT,PRIMARY KEY(generation,cid,start,stop))''')
    # No executable source content, URLs or provider credentials enter SQLite.
    ids=set();names={};aliases={};channel_names={}
    for row in streams:
        sid=row['sid'];eid=str(mappings.get(sid) or row.get('epg_channel_id') or '')
        if eid: ids.add(eid);aliases[sid]=eid
        key=_channel_name_key(row.get('name'))
        names.setdefault(key,[]).append(sid)
    batch=[];stored=0;now=time.time()
    def flush():
        if not batch: return
        check_space(target,sum(len(r[-1])+len(r[-2]) for r in batch)*4)
        with db: db.executemany('''INSERT INTO xml_stage VALUES(?,?,?,?,?,?) ON CONFLICT(generation,cid,start,stop) DO UPDATE SET title=excluded.title,description=excluded.description WHERE length(excluded.description)>length(xml_stage.description)''',batch)
        batch.clear()
    def channel(cid,name):
        key=_channel_name_key(name)
        # Only requested names are remembered. Ambiguous XMLTV names do not
        # overwrite provider/manual IDs; match conservatively at source end.
        if key in names:
            if key in channel_names and channel_names[key]!=cid: channel_names[key]=None
            elif key not in channel_names: channel_names[key]=cid
            ids.add(cid)
    def programme(event):
        nonlocal stored
        if event['channel'] not in ids or event['stop_timestamp']<=now or event['start_timestamp']>=now+10*86400: return
        if not event['name']: return
        batch.append((generation,event['channel'],event['start_timestamp'],event['stop_timestamp'],event['name'],event['descr']))
        stored+=1
        if len(batch)>=256: flush()
    try:
        # A previous interrupted stage is invisible. Cleanup affects staging
        # only, never a published programme or user's source configuration.
        with db: db.execute('DELETE FROM xml_stage')
        phase='DOWNLOAD'
        try:
            with source_stream(source,cancel=cancel) as stream:
                phase='PARSE'
                counts=parse(stream,channel,programme,cancel)
        except Exception as exc:
            try: exc.xcmate_stage=phase
            except Exception: pass
            raise
        flush()
        if not stored:
            from epg_errors import EmptyGuideError
            raise EmptyGuideError('No matching current programmes')
        for key,sids in names.items():
            cid=channel_names.get(key)
            if cid:
                for sid in sids:
                    if sid not in mappings and (sid not in aliases or aliases[sid] not in ids): aliases[sid]=cid
                    # An absent provider EPG ID can be repaired by an exact,
                    # unambiguous source name; manual mapping always wins.
                    elif sid not in mappings and not db.execute('SELECT 1 FROM xml_stage WHERE generation=? AND cid=? LIMIT 1',(generation,aliases[sid])).fetchone(): aliases[sid]=cid
        check_space(target)
        with db:
            from epg_events import clean_stage
            clean_stage(db,'xml_stage',' WHERE generation=?',(generation,))
            # The atomic publication can use disk journals but never builds
            # Python lists of all events. Prior future days outside coverage
            # survive shorter successful feeds.
            for cid,begin,end in db.execute('SELECT cid,min(start),max(stop) FROM xml_stage WHERE generation=? GROUP BY cid',(generation,)):
                db.execute('DELETE FROM programmes WHERE pid=? AND source=? AND cid=? AND start<? AND stop>?',
                           (pid,source_index,cid,end,begin))
            # Provider / earlier external source wins an overlapping interval.
            db.execute('''INSERT OR REPLACE INTO programmes
              SELECT ?,s.cid,s.start,s.stop,s.title,s.description,? FROM xml_stage s
              WHERE generation=? AND NOT EXISTS (SELECT 1 FROM programmes p
                WHERE p.pid=? AND p.cid=s.cid AND p.source<?)''',
                (pid,source_index,generation,pid,source_index))
            for alias,cid in aliases.items():
                if db.execute('SELECT 1 FROM xml_stage WHERE generation=? AND cid=? LIMIT 1',(generation,cid)).fetchone():
                    db.execute('INSERT OR REPLACE INTO guide_alias VALUES(?,?,?)',(pid,alias,cid))
            db.execute('DELETE FROM programmes WHERE stop<?',(now-86400,))
            db.execute('INSERT OR REPLACE INTO guide_meta VALUES(?,?,?)',(pid,'stream-'+generation,time.time()))
            db.execute('DELETE FROM xml_stage WHERE generation=?',(generation,))
        counts['stored']=stored
        return counts
    finally:
        # SQL rollback restores the complete previous guide on ENOSPC or error.
        db.rollback()
        try:
            with db: db.execute('DELETE FROM xml_stage WHERE generation=?',(generation,))
        except Exception: pass
        db.close()


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
    from epg_sources import configuration
    from epg_status import update,source_key
    from epg_errors import failure_details
    from source_adapters import for_portal
    from epg import _save_disk,_mem_set
    pid=portal['id'];streams=list(active_streams(portal));config=configuration(pid)
    if not streams:
        update(pid,'cache','WAIT_ACTIVE_CATALOG',running=False)
        from catalog_sync import request
        request(portal,'live',portal.get('start_group_id',''),priority=0)
        return {}
    if not portal.get('epg_show',True): return {}
    xc=for_portal(portal);uri=portal.get('epg_url') or xc.get_xmltv_epg_url()
    provider=dict(uri=uri,local=not uri.startswith(('http://','https://')))
    sources=([('provider',provider,0)] if uri and portal.get('provider_epg_enabled',True) else [])+[(source_key(s),s,i) for i,s in enumerate(config['sources'],1) if s.get('enabled',True)]
    successes=failures=0
    for key,source,index in sources:
        if cancel(): break
        update(pid,key,'RUNNING',running=True,source_index=index)
        try:
            counts=import_source(pid,source,index,streams,config['mappings'],cancel=cancel)
            update(pid,key,'READY',running=False,source_index=index,channels=counts['channels'],programmes=counts['stored'],bytes=counts['bytes'])
            successes+=1
        except Exception as exc:
            code,fields=failure_details(exc,getattr(exc,'xcmate_stage','MERGE'))
            update(pid,key,code,running=False,source_index=index,**fields);failures+=1
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
    update(pid,'refresh','NO_NEW_GUIDE',running=False,loaded=successes,failed=failures)
    return {}

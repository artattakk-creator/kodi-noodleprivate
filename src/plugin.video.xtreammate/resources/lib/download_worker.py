"""One finite, streamed direct-media transfer. No HTTP in Kodi input callbacks."""
import hashlib,os,re,time,uuid
from urllib.error import HTTPError
from urllib.parse import urlsplit
from download_sources import DownloadFailure,validate,container
from media_files import FileFailure

CHUNK=64*1024


from download_redirect import open_source


def destination(media,ident,extension):
    from media_files import join,safe_name,mkdir
    root=media['target'];mkdir(root)
    name='Download - '+safe_name(media.get('series_title') or media['title'])
    if media['kind']=='episode':
        name+=' - S'+str(int(media['season'])).zfill(2)+'E'+str(int(media['episode'])).zfill(2)
    return join(root,name+' -- '+ident[:20]+'.'+extension)


def _hash(uri,limit,cancel=lambda:False):
    if uri.startswith('smb://'):
        from download_smb import digest
        return digest(uri,limit,cancel)
    from media_files import reader
    digest=hashlib.sha256();size=0
    with reader(uri) as stream:
        while True:
            if cancel():raise InterruptedError()
            data=stream.read(CHUNK)
            if not data:break
            size+=len(data)
            if size>limit:raise DownloadFailure('PART_CHANGED')
            digest.update(data)
    if size!=limit:raise DownloadFailure('PART_CHANGED')
    return digest.hexdigest()


def run_one(cancel=lambda:False,resolver=None,opener=None):
    import download_store as store
    from download_sources import resolve
    import media_files as files
    job=store.claim()
    if not job:return False
    ident,owner=job['id'],job['owner'];media=job['media'];part=job['part'];output=None;response=None
    digest=hashlib.sha256();count=0;total=0;last=time.monotonic();last_bytes=0
    try:
        import download_targets as targets
        caps=files.probe(media['target'])
        workspace=targets.stage_root() if caps['staging'] else media['target']
        # Repair only a completely verified own publish interrupted after rename.
        if job['file'] and files.exists(job['file']):
            if (not caps['staging'] or targets.recoverable(ident,job['file'])) and job['total']>0 and files.size(job['file'])==job['total'] and _hash(job['file'],job['total'])==job['digest']:
                store.finish(ident,owner,'COMPLETE');return True
            if not (caps['staging'] and targets.owned(ident,job['file'])):raise DownloadFailure('TARGET_EXISTS')
        if job['file'] and job['total']>0 and job['bytes']==job['total'] and files.owned_part(part,ident) and files.exists(part) and _hash(part,job['total'])==job['digest']:
            connection=store.db()
            try:
                with connection:changed=connection.execute("UPDATE jobs SET state=? WHERE id=? AND owner=? AND state='RUNNING'",('TRANSFERRING' if caps['staging'] else 'PUBLISHING',ident,owner)).rowcount
            finally:connection.close()
            if not changed:raise InterruptedError()
            final=_publish(job,part,job['file'],job['total'],job['digest'],caps,cancel)
            store.checkpoint(ident,owner,file=final);store.finish(ident,owner,'COMPLETE');return True
        url,headers=(resolver or resolve)(media);fingerprint=hashlib.sha256(url.encode()).hexdigest()
        offset=job['bytes'] if job['code'] not in ('SOURCE_CHANGED','PART_CHANGED','BAD_RANGE') and job['fingerprint'].split(':')[0]==fingerprint and (job['etag'] and not job['etag'].startswith('W/') or job['modified']) else 0
        if offset and job['total'] and offset>=job['total']:offset=0
        if offset and (not files.owned_part(part,ident) or not files.exists(part) or files.size(part)!=offset or _hash(part,offset)!=job['digest']):offset=0
        headers=dict(headers)
        if offset:headers.update(Range='bytes='+str(offset)+'-',**{'If-Range':job['etag'] if job['etag'] and not job['etag'].startswith('W/') else job['modified']})
        response=opener(url,headers) if opener else open_source(url,headers,pid=media['pid'],job_id=ident)
        final_fingerprint=getattr(response,'source_fingerprint','')
        if final_fingerprint:
            fingerprint+=':'+final_fingerprint
            if offset and job['fingerprint']!=fingerprint:raise DownloadFailure('SOURCE_CHANGED')
        status=getattr(response,'status',200);h=response.headers
        if h.get('Content-Encoding','identity').lower()!='identity':raise DownloadFailure('UNSUPPORTED_SOURCE')
        mime=h.get('Content-Type','').lower()
        if any(k in mime for k in ('text/','json','mpegurl','dash+xml')):raise DownloadFailure('UNSUPPORTED_SOURCE')
        length=h.get('Content-Length','')
        if not str(length).isdigit() or int(length)<=0:raise DownloadFailure('LENGTH_REQUIRED')
        etag=str(h.get('ETag',''))[:512];modified=str(h.get('Last-Modified',''))[:128]
        if status==206:
            match=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',str(h.get('Content-Range','')))
            if not offset or not match or int(match[1])!=offset or int(match[2])+1!=int(match[3]) or int(length)!=int(match[3])-offset:raise DownloadFailure('BAD_RANGE')
            total=int(match[3])
            if (job['total'] and total!=job['total']) or (job['etag'] and etag!=job['etag']) or (not job['etag'] and job['modified'] and modified!=job['modified']):raise DownloadFailure('SOURCE_CHANGED')
        elif status==200:offset=0;total=int(length)
        else:raise DownloadFailure('HTTP_ERROR')
        if total>files.file_limit(media['target']):raise DownloadFailure('FILE_LIMIT')
        files.mkdir(media['target']);files.capacity(workspace,total)
        files.capacity(media['target'],total)
        newpart=files.join(workspace,'.xcmate-'+ident+'-'+uuid.uuid4().hex+'.part')
        output=files.writer(newpart)
        if offset:
            with files.reader(part) as prior:
                while count<offset:
                    if cancel():raise InterruptedError()
                    data=prior.read(min(CHUNK,offset-count))
                    if not data:raise DownloadFailure('PART_CHANGED')
                    output.write(data);digest.update(data);count+=len(data)
        files.flush(output)
        previous=part;part=newpart
        state=store.checkpoint(ident,owner,part=part,bytes=count,total=total,etag=etag,modified=modified,fingerprint=fingerprint,digest=digest.hexdigest())
        if previous and previous!=part and files.owned_part(previous,ident) and files.exists(previous):files.remove(previous)
        first=b'';extension='';final='';last=time.monotonic();last_bytes=count
        if offset:
            with files.reader(part) as prior:first=prior.read(CHUNK)
            extension=container(first);final=destination(media,ident,extension)
        while count<total:
            if cancel() or state!='RUNNING':raise InterruptedError()
            data=response.read(min(CHUNK,total-count))
            if not data:raise DownloadFailure('TRUNCATED')
            if not extension:
                first+=data
                # Collect a sufficient format probe before writing any payload.
                if len(first)<min(1024,total):continue
                extension=container(first);final=destination(media,ident,extension);data=first;first=b''
            files.capacity(workspace,len(data));output.write(data);digest.update(data);count+=len(data)
            now=time.monotonic()
            if now-last>=.5:
                files.flush(output)
                state=store.checkpoint(ident,owner,bytes=count,digest=digest.hexdigest(),speed=(count-last_bytes)/max(.001,now-last))
                last=now;last_bytes=count
                # Bound cancellation latency even for a very fast local server.
        if response.read(1):raise DownloadFailure('LENGTH_MISMATCH')
        files.flush(output);output.close();output=None
        if not final:raise DownloadFailure('INVALID_MEDIA')
        if files.size(part)!=total:raise DownloadFailure('TARGET_WRITE')
        state=store.checkpoint(ident,owner,bytes=count,total=total,digest=digest.hexdigest(),file=final,speed=0)
        if cancel() or state!='RUNNING':raise InterruptedError()
        # Claim publication before rename: Stop/Cancel cannot turn a completed
        # file into a cancelled row between filesystem and metadata publication.
        connection=store.db()
        try:
            with connection:
                changed=connection.execute("UPDATE jobs SET state=? WHERE id=? AND owner=? AND state='RUNNING'",('TRANSFERRING' if caps['staging'] else 'PUBLISHING',ident,owner)).rowcount
        finally:connection.close()
        if not changed:raise InterruptedError()
        final=_publish(job,part,final,total,digest.hexdigest(),caps,cancel)
        store.checkpoint(ident,owner,file=final);store.finish(ident,owner,'COMPLETE')
    except InterruptedError:
        if output is not None:
            try:files.flush(output);store.checkpoint(ident,owner,bytes=count,digest=digest.hexdigest(),speed=0)
            except (OSError,RuntimeError):pass
        store.finish(ident,owner,'PAUSED','INTERRUPTED' if cancel() else '')
    except Exception as error:
        if output is not None:
            try:files.flush(output);store.checkpoint(ident,owner,bytes=count,digest=digest.hexdigest(),speed=0)
            except (OSError,RuntimeError):pass
        code=getattr(error,'code',None)
        if not isinstance(code,str):
            from art_errors import classify
            errno=getattr(error,'errno',None)
            code='FILE_LIMIT' if errno==27 else 'NO_SPACE' if errno==28 else 'TARGET_WRITE' if errno in (13,30) else 'TARGET_UNAVAILABLE' if errno==2 else classify(error)
        transient=code in ('TIMEOUT','DNS_ERROR','CONNECTION_ERROR','NETWORK_ERROR','HTTP_SERVER','TRUNCATED')
        from transfer_diagnostics import encode,mark
        reason=encode(error,code);mark('DOWNLOAD','FAILED',reason)
        store.fail(ident,owner,reason,transient)
    finally:
        if response is not None:response.close()
        if output is not None:output.close()
    return True


def _publish(job,part,final,total,digest,caps,cancel):
    import download_store as store,download_targets as targets
    ident,owner=job['id'],job['owner'];last=[0]
    def stopped():
        if cancel():return True
        row=store.get(ident)
        return not row or row['owner']!=owner or row['state'] not in ('TRANSFERRING','PUBLISHING')
    def progress(count):
        now=time.monotonic()
        if now-last[0]>=.5:
            store.checkpoint(ident,owner,copy_bytes=count);last[0]=now
    def destination(uri):store.checkpoint(ident,owner,file=uri,copy_bytes=0)
    def claim():
        if cancel():return False
        connection=store.db()
        try:
            with connection:return bool(connection.execute("UPDATE jobs SET state='PUBLISHING' WHERE id=? AND owner=? AND state='TRANSFERRING'",(ident,owner)).rowcount)
        finally:connection.close()
    return targets.publish(part,final,ident,total,digest,caps,stopped,progress,destination,claim)

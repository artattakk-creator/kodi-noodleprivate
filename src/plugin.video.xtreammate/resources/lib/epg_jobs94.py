"""Private, cross-interpreter control/observations for the existing EPG worker.

No URLs, account IDs, titles, credentials or exception strings are accepted.
An ACK proves lock acquisition by the worker, not merely thread submission.
"""
import contextlib,hashlib,json,os,re,tempfile,time,uuid
ACTIVE={'QUEUED','RUNNING','CANCELLING'}
TERMINAL={'DONE','PARTIAL','FAILED','CANCELLED','INTERRUPTED','SERVICE_NOT_CONFIRMED'}
FAILURES={'DNS_FAILED','TLS_FAILED','DOWNLOAD_TIMEOUT','PARSE_TIMEOUT','DOWNLOAD_FAILED','PARSE_FAILED','HTTP_COMPRESSION_FAILED','GZIP_INVALID','INVALID_XMLTV','XMLTV_UNSAFE_DECLARATION','NO_CHANNEL_MATCH','EMPTY_GUIDE','SQLITE_BUSY','SQLITE_FULL','SQLITE_IO','SQLITE_ERROR','SQLITE_CANCELLED','RESERVE_BLOCKED','EPG_READBACK_MISMATCH','EPG_READBACK_REVISION_CHANGED','SOURCE_UNAVAILABLE','BACKUP_REQUIRED','CANCELLED'}
PHASES={'QUEUED','DOWNLOAD','PARSE','MATCHING','STAGING','COMMIT','READBACK','CLEANUP','DONE','FAILED','CANCELLED','WAIT_CATALOG'}
COUNTERS={'bytes','total_bytes','channels','programmes','matched','staged','committed','verified','source_index','sources','free_before','free_after','raw_deleted_bytes','first','last'}


def path(pid):
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'epg_job94_'+hashlib.sha256(str(pid).encode()).hexdigest()[:24]+'.json')


def read(pid):
    try:
        filename=path(pid)
        if os.path.islink(filename):return {}
        with open(filename,encoding='utf-8') as stream:raw=stream.read(131073)
        if len(raw)>131072:return {}
        value=json.loads(raw)
        if not isinstance(value,dict) or not re.fullmatch('[a-f0-9]{32}',str(value.get('id',''))):return {}
        if value.get('state') not in ACTIVE|TERMINAL:return {}
        return value
    except (OSError,ValueError,TypeError):return {}


@contextlib.contextmanager
def locked(pid):
    import fcntl
    filename=path(pid)
    fd=os.open(filename+'.lock',os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0),0o600)
    try:
        # Status/control operations are small, never encompass network or SQL.
        end=time.monotonic()+.15
        while True:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);break
            except BlockingIOError:
                if time.monotonic()>=end:raise OSError('EPG_STATUS_BUSY')
                time.sleep(.005)
        yield
    finally:os.close(fd)


def write(pid,value):
    filename=path(pid);temp=None
    fd,temp=tempfile.mkstemp(prefix='.epg-job94-',dir=os.path.dirname(filename))
    try:
        from wizard_storage71 import protect
        protect(temp,fd=fd)
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            fd=None;raw=json.dumps(value,separators=(',',':'))
            if len(raw.encode())>131072:raise OSError('EPG_STATUS_BUDGET')
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.replace(temp,filename);temp=None
    finally:
        if fd is not None:os.close(fd)
        if temp:os.unlink(temp)


def request(pid,force=False):
    with locked(pid):
        old=read(pid);now=time.time()
        if old.get('state') in ACTIVE:
            # A queued request is reusable until the worker confirms it or the
            # explicit confirmation deadline expires; never spawn duplicates.
            if old['state']!='QUEUED' or now-old.get('requested',0)<=15:return old
        value=dict(version=1,id=uuid.uuid4().hex,state='QUEUED',requested=now,force=bool(force),cancel=False,phase='QUEUED',sources={})
        write(pid,value);return value


def acknowledge(pid,identity):
    with locked(pid):
        value=read(pid);now=time.time()
        if value.get('id')!=identity or value.get('state')!='QUEUED' or value.get('cancel'):return False
        if now-value['requested']>15:
            value.update(state='SERVICE_NOT_CONFIRMED');write(pid,value);return False
        value.update(state='RUNNING',ack=now,progress=now,phase_started=now)
        write(pid,value);return True


def observe(pid,identity,key,phase,**counts):
    if phase not in PHASES or not (key in ('refresh','provider') or re.fullmatch('[a-f0-9]{24}',key)):raise ValueError('EPG_STATUS_INVALID')
    safe={k:int(v) for k,v in counts.items() if k in COUNTERS and isinstance(v,(int,float)) and 0<=v<=2**63-1}
    if counts.get('error_code') in FAILURES:safe['error_code']=counts['error_code']
    with locked(pid):
        value=read(pid)
        if value.get('id')!=identity or value.get('state') not in ('RUNNING','CANCELLING'):return False
        rows=value['sources'];previous=rows.get(key,{})
        row=dict(previous,**safe,phase=phase);now=time.time()
        changed=any(previous.get(k)!=v for k,v in row.items())
        if changed:row['progress']=now;value['progress']=now
        if previous.get('phase')!=phase:
            row['phase_started']=now
            row.setdefault('phases',{})[phase]=dict(at=now)
        if key not in rows and len(rows)>=128:return False
        rows[key]=row;value.update(phase=phase,source=key)
        write(pid,value);return True


def cancelled(pid,identity):
    value=read(pid)
    return value.get('id')!=identity or bool(value.get('cancel'))


def cancel(pid,identity):
    with locked(pid):
        value=read(pid)
        if value.get('id')!=identity or value.get('state') not in ACTIVE:return False
        value.update(cancel=True,state='CANCELLED' if value['state']=='QUEUED' else 'CANCELLING')
        write(pid,value);return True


def finish(pid,identity,state):
    if state not in TERMINAL:raise ValueError('EPG_STATUS_INVALID')
    with locked(pid):
        value=read(pid)
        if value.get('id')!=identity:return False
        value.update(state='CANCELLED' if value.get('cancel') else state,finished=time.time())
        write(pid,value);return True


def snapshot(pid,now=None):
    value=read(pid);now=time.time() if now is None else now
    if not value:return value
    value=dict(value)
    if value['state']=='QUEUED' and now-value['requested']>15:value['state']='SERVICE_NOT_CONFIRMED'
    value['stalled']=False
    if value['state']=='RUNNING':
        phase=value.get('phase');limit={'DOWNLOAD':45,'PARSE':90,'MATCHING':90,'STAGING':90,'COMMIT':30,'READBACK':90,'CLEANUP':30}.get(phase,90)
        value['stalled']=now-value.get('progress',value.get('ack',now))>limit
    return value


def reconcile(pid):
    """Service-only recovery: require the OS import lease to prove no owner.

    Never infer worker death from a slow download or a stale progress timer.
    The service calls this only when its own warmup thread is not alive.
    """
    value=read(pid)
    if value.get('state') not in ('RUNNING','CANCELLING') or time.time()-value.get('ack',0)<5:return False
    from stream_epg import portal_lease44
    with portal_lease44(pid) as held:
        if not held:return False
        return finish(pid,value['id'],'INTERRUPTED')


def adopt(pid,identity,requested,force=False):
    """Upgrade bridge for a still-running pre-.94 root's Window request."""
    if not re.fullmatch('[a-f0-9]{32}',str(identity)) or not isinstance(requested,(int,float)) or not 0<=time.time()-requested<=15:return None
    with locked(pid):
        value=read(pid)
        if value.get('state') in ACTIVE:return value
        value=dict(version=1,id=identity,state='QUEUED',requested=requested,force=bool(force),cancel=False,phase='QUEUED',sources={})
        write(pid,value);return value

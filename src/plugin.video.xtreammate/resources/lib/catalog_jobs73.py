"""Durable full-catalog intents, reusing the published streaming/atomic writer.

One group per service turn, same inter-interpreter writer lock as .72/delta.
Private journal contains no credentials or URLs. No deletion on absent replies.
"""
import hashlib
import json
import os
import time
import tempfile
import uuid
from profile_transaction import writing, reading
from vodsync_api72 import ACTIONS, SyncError, failure
from vodsync72 import Session

KINDS = ('live', 'vod', 'series')
CONTRACTS = dict(ACTIONS, live=('get_live_categories', 'get_live_streams', 'stream_id'))
_cache = None
_verified = {}


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(), 'catalog_jobs73.json')


def _read():
    try:
        with open(path(), encoding='utf-8') as stream:
            raw = stream.read(8*1024*1024+1)
        if len(raw) > 8*1024*1024: raise SyncError('JOB_BUDGET')
        value = json.loads(raw)
        if value.get('version') != 1 or not isinstance(value.get('jobs'), list): raise SyncError('JOB_SCHEMA')
        return value
    except FileNotFoundError: return dict(version=1, jobs=[])


def _save(value):
    from wizard_storage71 import protect
    from import_budget import check_space
    raw = json.dumps(value).encode()
    if len(raw) > 8*1024*1024: raise SyncError('JOB_BUDGET')
    check_space(path(), len(raw)*2+65536)
    fd,temp=tempfile.mkstemp(prefix='.catalog73-',dir=os.path.dirname(path()))
    try:
        protect(temp,fd=fd)
        with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        fd=None;os.replace(temp,path());temp=None
    finally:
        if fd is not None:os.close(fd)
        if temp and os.path.exists(temp):os.unlink(temp)
    global _cache
    _cache = value


def jobs():
    with reading(): return _read()['jobs']


def request(portal, kinds=KINDS, epg=False):
    kinds = [k for k in KINDS if k in kinds]
    if not kinds: raise SyncError('NO_SELECTION')
    if portal.get('type') != 'xtream': raise SyncError('SOURCE_TYPE')
    with writing():
        value = _read()
        prior = next((r for r in value['jobs'] if r['pid'] == str(portal['id']) and
                      (r['state'] in ('WAITING', 'RUNNING') or r.get('resume'))), None)
        if prior: return prior['id']
        row = dict(id=uuid.uuid4().hex, pid=str(portal['id']), kinds=kinds, epg=bool(epg),
                   state='WAITING', created=time.time(), updated=time.time(), processed=0,
                   committed=0, counts={k:0 for k in kinds}, cursor=0, units=None,
                   code='', attempts=0, next_at=0, resume=True, cancel=False)
        # Bound only our terminal diagnostic history. No catalog data removed.
        value['jobs'] = [r for r in value['jobs'] if r['state'] in ('WAITING','RUNNING') or r.get('resume')][-32:] + [
            r for r in value['jobs'] if r['state'] not in ('WAITING','RUNNING') and not r.get('resume')][-16:] + [row]
        _save(value)
        return row['id']


def control(token, resume=False):
    with writing():
        value = _read()
        row = next(r for r in value['jobs'] if r['id'] == token)
        if resume:
            if row['state'] == 'RUNNING': return
            row.update(state='WAITING', resume=True, cancel=False, next_at=0, attempts=0, code='')
        else:
            row.update(cancel=True, resume=False)
            if row['state'] != 'RUNNING': row.update(state='INTERRUPTED', code='USER_CANCELLED')
        row['updated'] = time.time(); _save(value)


def _update(token, **fields):
    with writing():
        value = _read(); row = next(r for r in value['jobs'] if r['id'] == token)
        # Cancellation belongs to the user, never overwrite it with an old worker.
        fields.pop('cancel', None)
        row.update(fields, updated=time.time())
        if row.get('cancel'):
            row.update(state='INTERRUPTED',resume=False,code='USER_CANCELLED')
        _save(value)
        return dict(row)


class FullSession(Session):
    contracts = CONTRACTS
    def __init__(self, portal, kinds):
        super().__init__(portal, kinds, allowed=KINDS)

    def activate(self, kind, cid, cancel):
        # A refresh does NOT re-enable disabled groups or content areas, change
        # auto-new preferences, start group/channel or any other portal setting.
        if cancel(): raise SyncError('CANCELLED')
        self.ensure_connection()


def run_next(cancel=lambda: False):
    """Worker-only. Real EOF/commit/cold-readback before advancing cursor."""
    if cancel() or not os.path.isfile(path()): return False
    with reading(): value = _read()
    global _cache
    _cache = value
    job = next((dict(r) for r in value['jobs'] if r.get('resume') and not r.get('cancel') and
                r['state'] in ('WAITING', 'RUNNING', 'INTERRUPTED') and r.get('next_at',0) <= time.time()), None)
    if job is None: return False
    from portals import get_by_id
    from vodsync_store72 import backup, verify_backup, upsert
    from library_index import Reader
    session = None
    try:
        portal = get_by_id(job['pid'])
        if not portal or not portal.get('enabled', True): raise SyncError('PORTAL_UNAVAILABLE')
        session = FullSession(portal, job['kinds'])
        # Acquiring the shared writer proves the old interpreter is no longer
        # writing; only now may a crashed RUNNING intent be resumed.
        if job.get('account') and job['account'] != session.account: raise SyncError('CONNECTION_CHANGED')
        job = _update(job['id'], state='RUNNING', account=session.account, code='', owner=session.token)
        last = [0.0]
        def stopped():
            if cancel(): return True
            if time.monotonic() >= last[0]:
                last[0] = time.monotonic()+.25
                with reading(): current = next(r for r in _read()['jobs'] if r['id']==job['id'])
                stopped.user = current.get('cancel', False)
            return getattr(stopped, 'user', False)
        def progress(percent, detail):
            if time.monotonic()-progress.at < .5 and detail.get('phase') not in ('VERIFY','COMMIT'): return
            progress.at = time.monotonic()
            _update(job['id'], phase=detail.get('phase',''), group_read=detail.get('read',0),
                    group_stored=detail.get('new',0)+detail.get('changed',0)+detail.get('unchanged',0))
        progress.at = 0
        if job['units'] is None:
            from vodsync_api72 import authenticate, iterate, identity
            authenticate(session.client, stopped)
            units=[];seen=set()
            for kind in job['kinds']:
                for group in iterate(session.client, kind, categories=True, cancel=stopped, contracts=CONTRACTS):
                    cid = identity(group.get('category_id', group.get('id')))
                    name = group.get('category_name') or group.get('name')
                    if not isinstance(name,str) or not name.strip(): raise SyncError('SCHEMA')
                    if (kind,cid) in seen or len(units)>=20000: raise SyncError('CATEGORY_BUDGET')
                    seen.add((kind,cid)); units.append([kind,dict(category_id=cid,category_name=name[:512])])
            if not units: raise SyncError('SOURCE_EMPTY')
            job = _update(job['id'], units=units, phase='BACKUP',groups_found={k:sum(a==k for a,g in units) for k in job['kinds']})
        if not job.get('backup'):
            from group_selection import _read as selections
            with writing():
                target=backup(session.pid, session.kinds, session.filename, session.folder,
                    selections().get('_v2',{}).get(session.pid,{}), stopped, allowed=KINDS)
            job = _update(job['id'], backup=target)
        verify_once(job['backup'])
        if job['cursor'] < len(job['units']):
            kind, group = job['units'][job['cursor']]
            job = _update(job['id'], kind=kind, group=group['category_name'], group_number=job['cursor']+1,
                          group_total=len(job['units']), group_read=0, group_stored=0)
            try:
                result=upsert(session,kind,group,stopped,progress)
            except SyncError as exc:
                if exc.code not in ('SOURCE_EMPTY','FILTERED_SOURCE'): raise
                # Empty API response never erases a previously valid generation.
                # Record explicit empty evidence; retained rows remain readable.
                result=dict(read=getattr(exc,'counts72',{}).get('read',0),stored=0)
                job.setdefault('empty',[])
                job['empty'].append([kind,group['category_id']])
            totals=dict(job['counts']);totals[kind]+=result['stored']
            job=_update(job['id'], cursor=job['cursor']+1, processed=job['processed']+result['read'],
                        committed=job['committed']+int(result['stored']>0), counts=totals,
                        empty=job.get('empty',[]), attempts=0)
            try:
                from widget_refresh45 import publish
                from widget_data41 import snapshot
                rows,code=snapshot(portal,kind,background=True)
                publish(portal,kind,rows,code=code)
            except (ImportError,AttributeError,OSError,RuntimeError,ValueError,TypeError): pass
        if stopped(): raise SyncError('CANCELLED')
        if job['cursor'] == len(job['units']):
            readback={k:Reader(session.pid,session.filename).page(k,limit=1)[1] for k in session.kinds}
            epgcode='NOT_REQUESTED'
            if job.get('epg'):
                from epg import request_refresh
                epgcode='REQUESTED' if request_refresh(session.pid,portal,force=True) else 'DEFERRED'
            _update(job['id'],state='DONE',resume=False,code='',readback=readback,epg_state=epgcode)
        else: _update(job['id'], state='WAITING', code='')
        return True
    except Exception as exc:
        problem=failure(exc)
        if problem.code=='BUSY':
            _update(job['id'],state='WAITING',code='WRITER_BUSY',next_at=time.time()+3)
            return False
        if problem.code=='CANCELLED':
            _update(job['id'],state='INTERRUPTED',code='USER_CANCELLED' if not cancel() else 'SERVICE_STOP',
                    resume=bool(cancel()))
        else:
            attempts=job.get('attempts',0)+1
            retry=problem.code in ('NETWORK','TIMEOUT','SQLITE','HTTP','RATE_LIMIT') and attempts<3
            _update(job['id'],state='WAITING' if retry else 'FAILED',code=problem.code,
                    attempts=attempts,resume=retry,next_at=time.time()+min(300,15*2**attempts))
        return True
    finally:
        if session is not None: session.close()


def verify_once(filename):
    """Cold verify each process/revision; no rehash of a large backup per group."""
    from vodsync_store72 import verify_backup
    def identity():
        return tuple((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
            for s in (os.stat(filename),os.stat(filename+'.json')))
    before=identity()
    if _verified.get(filename)==before:return
    verify_backup(filename,allowed=KINDS)
    if identity()!=before:raise SyncError('BACKUP_VERIFY')
    _verified[filename]=before
    while len(_verified)>64:_verified.pop(next(iter(_verified)))

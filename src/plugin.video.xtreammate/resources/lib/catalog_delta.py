"""Durable explicit Xtream group worklist; never refresh unrelated groups.

Small internal JSON intents avoid depending on a locked catalogue DB when the
user saves group selection. Service owns network/index IO and bounded retries.
"""
import json
import os
import tempfile
import time
import uuid
from profile_transaction import writing,reading


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'catalog_delta_v1.json')


def _read():
    try:
        with open(path(),encoding='utf-8') as stream:value=json.load(stream)
        if value.get('version')==1 and isinstance(value.get('jobs'),dict):return value
    except FileNotFoundError:pass
    return dict(version=1,jobs={})


def _save(value):
    from import_budget import check_space
    data=json.dumps(value,sort_keys=True).encode();check_space(path(),len(data)*2+65536)
    fd,temp=tempfile.mkstemp(prefix='.catalog-delta-',dir=os.path.dirname(path()))
    try:
        with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.replace(temp,path());temp=''
    finally:
        if temp:
            try:os.unlink(temp)
            except OSError:pass


def request(portal,kind,cid):
    return request_many(portal,kind,[cid],retry=True,missing=True)


def request_many(portal,kind,categories,retry=False,missing=False):
    if kind not in ('live','vod','series') or portal.get('type')!='xtream':return
    with writing(timeout=.1):
        value=_read();changed=False
        for cid in categories:
            key=json.dumps([str(portal['id']),kind,str(cid)]);prior=value['jobs'].get(key)
            if prior:
                if prior['code'] in ('PENDING','RUNNING'):continue
                if prior['code']=='READY' and not missing:continue
                if prior['code'] in ('FAILED','CANCELLED','EMPTY_SOURCE') and not retry:continue
            value['jobs'][key]=dict(pid=str(portal['id']),kind=kind,cid=str(cid),code='PENDING',attempts=0,next_at=0,updated=time.time(),stored=0,received=0)
            changed=True
        if len(value['jobs'])>8192:raise ValueError('CATALOG_JOB_BUDGET')
        if changed:_save(value)


def states(pid,kind):
    with reading(timeout=.05):
        rows=[row for row in _read()['jobs'].values() if row['pid']==str(pid) and row['kind']==kind]
    if kind=='series':
        from catalog_delta52 import progress
        rows=progress(pid,kind,rows)
    return sorted(rows,key=lambda row:row['updated'],reverse=True)


def pending(pid,kind):return any(row['code'] in ('PENDING','RUNNING') for row in states(pid,kind))


from catalog_delta52 import serial_worker


@serial_worker
def run_next(cancel=lambda:False):
    if not os.path.isfile(path()) or cancel():return False
    now=time.time()
    with writing(timeout=.1):
        value=_read();selected=next(((key,row) for key,row in value['jobs'].items() if row['code'] in ('PENDING','RUNNING','FAILED') and row['attempts']<3 and row['next_at']<=now),None)
        if selected is None:return False
        key,job=selected;job=dict(job,code='RUNNING',next_at=now+330,updated=now,owner=uuid.uuid4().hex);value['jobs'][key]=job;_save(value)
    from catalog_delta52 import cancellation
    stopped=cancellation(key,job['owner'],cancel)
    try:
        from portals import get_by_id
        from xtream import XtreamClient
        from library_index import sync_kind,Reader,sync_state
        portal=get_by_id(job['pid'])
        if not portal or not portal.get('enabled',True):raise ValueError('PORTAL_UNAVAILABLE')
        from group_selection import load
        enabled=load(job['pid'],job['kind'])
        if enabled is not None and job['cid'] not in enabled:
            job.update(code='CANCELLED',attempts=3);raise InterruptedError()
        client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
        sync_kind(portal,client,job['kind'],job['cid'],cancel=stopped,max_groups=1,only_categories={job['cid']})
        statuses=sync_state(job['pid'],job['kind'])
        state=next((row for row in statuses if row['cid']==job['cid']),None)
        if stopped():raise InterruptedError()
        if state and state['updated']>=job['updated'] and state['code'] in ('FAILED','CANCELLED'):raise OSError('IMPORT_PENDING')
        reader=Reader(job['pid'])
        if not reader._query('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?',(job['pid'],job['kind'],job['cid'])):raise OSError('IMPORT_PENDING')
        rows,total=reader.page(job['kind'],category=job['cid'],limit=1)
        job.update(code='READY' if total else 'EMPTY_SOURCE',stored=total,received=(state or {}).get('received',total),updated=time.time())
    except InterruptedError:job.update(code='CANCELLED',attempts=3,updated=time.time())
    except Exception:job.update(code='FAILED',attempts=job['attempts']+1,next_at=time.time()+min(300,15*2**job['attempts']),updated=time.time())
    with writing(timeout=.1):
        value=_read()
        # A new explicit selection cannot be overwritten by this old completion.
        if value['jobs'].get(key,{}).get('owner')==job['owner']:
            value['jobs'][key]=job;_save(value)
    return True

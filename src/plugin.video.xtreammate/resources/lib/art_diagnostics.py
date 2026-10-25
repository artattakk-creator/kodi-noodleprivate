"""Numeric artwork observations across Kodi interpreters; no source URLs/IDs.

Heartbeat properties distinguish unknown/stale service observations from a
proved stopped worker. Reading status never starts a worker or repairs a DB.
"""
import json
import os
import sqlite3
import threading
import time
from urllib.parse import quote

_lock=threading.Lock()
_last={}
_phases={}
ROLES=frozenset(('request','enrol','service','worker','transfer','logo'))
CODES=frozenset(('REQUESTED','ENQUEUED','IDLE','ACTIVE','STOPPED','START_FAILED','PAUSED',
    'FETCH_BEGIN','READY','NO_SOURCE','INVALID_SOURCE','INVALID_IMAGE','PENDING','RUNNING',
    'DB_BUSY','DB_UNAVAILABLE','CACHE_ERROR','DISK_FULL','BUDGET_FULL','NETWORK_ERROR',
    'HTTP_AUTH','HTTP_NOT_FOUND','HTTP_RATE_LIMIT','HTTP_SERVER','HTTP_CLIENT','DNS_ERROR',
    'TLS_ERROR','TIMEOUT','CONNECTION_ERROR','RESERVE_BLOCKED','BLOCKED_REAL_DISK','PHYSICAL_ENOSPC',
    'MEMORY_PRESSURE','BUSY','READONLY','CORRUPT','SCHEMA_ERROR','SPACE_FULL','IO_ERROR','SQL_ERROR','LOCK_UNSUPPORTED','CAPACITY_UNKNOWN','METADATA_RESERVE_BLOCKED','STORAGE_OFFLINE','DYNAMIC_URL_APPROVED','DYNAMIC_SOURCE_UNAVAILABLE','UNKNOWN'))
FIELDS=frozenset(('items','valid_source','no_source','invalid_source','live_sources','vod_sources',
    'series_sources','source_cover','source_stream_icon','source_movie_image','source_cover_big',
    'inbox','inbox_due','worker_alive','enrol_alive','paused','stopped','bytes','expected_bytes',
    'free','total','reserve','budget','at','background_catalogues'))


def publish(role,code,reason='',**fields):
    if role not in ROLES or code not in CODES:return
    value=dict(code=code,at=time.time())
    if reason in CODES:value['reason']=reason
    for key,number in fields.items():
        if key in FIELDS and isinstance(number,(int,float,bool)) and 0<=number<=10**15:
            value[key]=int(number)
    try:
        import xbmc,xbmcgui
        now=time.monotonic()
        with _lock:
            if not _last:_phases.clear()
            prior=_last.get(role)
            # Same state is observed at most once per two seconds; a new
            # failure/source sample becomes visible immediately.
            signature={k:v for k,v in value.items() if k!='at'}
            if prior and prior[1]==signature and now-prior[0]<2:return
            _last[role]=(now,signature)
            key=(role,code,reason)
            previous,count=_phases.get(key,(float('-inf'),0));count+=1
            interval=2 if code in ('FETCH_BEGIN','READY') else 10 if code in ('REQUESTED','ENQUEUED') else 60
            log_due=now-previous>=interval
            _phases[key]=(now if log_due else previous,0 if log_due else count)
        xbmcgui.Window(10000).setProperty('XCMate.Artwork.'+role,json.dumps(value,separators=(',',':')))
        # No exception text, provider hostname, filename, URL digest or ID.
        if log_due:xbmc.log('[XCMate][ARTWORK] role='+role+' '+json.dumps(dict(value,events=count),sort_keys=True),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError,TypeError,ValueError):pass


def observation(role):
    if role not in ROLES:return dict(code='UNKNOWN')
    try:
        import xbmcgui
        raw=xbmcgui.Window(10000).getProperty('XCMate.Artwork.'+role)
        value=json.loads(raw) if raw and len(raw)<=4096 else {}
        if not isinstance(value,dict) or not 0<=time.time()-float(value.get('at',0))<=(600 if role in ('request','transfer','enrol','logo') else 10):
            return dict(code='UNKNOWN')
        result=dict(code=value.get('code') if value.get('code') in CODES else 'UNKNOWN')
        if value.get('reason') in CODES:result['reason']=value['reason']
        for key,number in value.items():
            if key in FIELDS and isinstance(number,(int,float,bool)) and 0<=number<=10**15:result[key]=number
        return result
    except (ImportError,AttributeError,RuntimeError,TypeError,ValueError,OverflowError):return dict(code='UNKNOWN')


def sources(items,valid):
    counts=dict(items=0,valid_source=0,no_source=0,invalid_source=0,live_sources=0,vod_sources=0,series_sources=0,
                source_cover=0,source_stream_icon=0,source_movie_image=0,source_cover_big=0)
    for item in items[:48]:
        if not isinstance(item,dict):continue
        counts['items']+=1
        values=[item.get(field) for field in ('cover','stream_icon','movie_image','cover_big')]
        present=any(values);accepted=any(valid(value) for value in values)
        counts['valid_source' if accepted else 'invalid_source' if present else 'no_source']+=1
        if accepted and item.get('kind') in ('live','vod','series'):counts[item['kind']+'_sources']+=1
        for field,value in zip(('cover','stream_icon','movie_image','cover_big'),values):
            counts['source_'+field]+=int(valid(value))
    publish('request','REQUESTED',**counts)


def enrol_failure(error):
    from artwork_db import classify,diagnostic
    if isinstance(error,sqlite3.Error):
        reason=classify(error)
        code='DB_BUSY' if reason=='BUSY' or diagnostic().get('code')=='BUSY' else 'DB_UNAVAILABLE'
    else:
        reason='UNKNOWN';code='DISK_FULL' if getattr(error,'errno',None)==28 else 'CACHE_ERROR'
    publish('enrol',code,reason=reason)
    return code


def queue_details(cancel=lambda:False):
    from artwork_db import path,_lock,_unlock,classify
    if cancel() or not os.path.isfile(path()):return dict(code='UNKNOWN')
    db=None;fd=None
    try:
        fd=_lock();db=sqlite3.connect('file:'+quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.025)
        db.execute('PRAGMA query_only=ON');deadline=time.monotonic()+.15
        db.set_progress_handler(lambda:int(cancel() or time.monotonic()>deadline),1000)
        db.execute('BEGIN')
        row=db.execute('''SELECT max(CASE WHEN status='READY' THEN updated ELSE 0 END),
          max(CASE WHEN status='RUNNING' OR attempts>0 THEN updated ELSE 0 END),
          sum(CASE WHEN attempts>=3 AND status!='READY' THEN 1 ELSE 0 END),
          min(CASE WHEN attempts<3 AND status!='READY' THEN next_at ELSE NULL END) FROM jobs''').fetchone()
        lease=db.execute('SELECT until FROM worker WHERE id=1').fetchone()
        return dict(code='OK',last_ready_at=row[0] or 0,last_attempt_at=row[1] or 0,
                    exhausted=row[2] or 0,next_at=row[3],lease_until=lease[0] if lease else None)
    except (OSError,sqlite3.Error) as error:
        return dict(code='DB_BUSY' if classify(error)=='BUSY' else 'DB_UNAVAILABLE')
    finally:
        if db is not None:db.close()
        _unlock(fd)


def augment(value,cancel=lambda:False):
    from art_storage import explain
    from media_art import MAX_BYTES
    value['expected_bytes']=MAX_BYTES
    value['storage_result']=explain(value,MAX_BYTES,value.get('bytes'))
    value['observations']={role:observation(role) for role in ROLES}
    if value.get('code')=='OK' and not cancel():value['queue_details']=queue_details(cancel)
    # Metadata lives beside the job DB; it can be on a different mount from
    # an existing artwork directory. Only numeric capacity leaves this helper.
    try:
        import shutil
        from artwork_db import path
        from import_budget import RESERVE
        value['metadata_free']=shutil.disk_usage(os.path.dirname(path())).free
        value['metadata_reserve']=RESERVE
    except OSError:pass
    return value

"""Counts and fixed stage codes only; never names, addresses or raw errors."""
import hashlib
import json
import sqlite3
import time
import uuid

_flow = uuid.uuid4().hex[:12]
_seen = {}
_indexed = {}
STAGES = ('INDEX','SELECT','ASSETS','ITEMS','DIRECTORY','SKIN',
          'SQL_STATE','SQL_GROUPS','SQL_HEADS','SQL_LEGACY_PRESENCE','SQL_V2_KEYS','SQL_LEGACY_KEYS','SQL_PAYLOAD')
COUNTS = frozenset(('provider_received','sync_stored','indexed','groups','selected','items',
    'poster_sources','logo_sources','local_images','dynamic_images','placeholders',
    'event_count','matched_images','directory_ok','image_reference','decode_verified','queries','query_ms'))


def note(pid, kind, stage, code='READY', **counts):
    if kind not in ('live','vod','series') or stage not in STAGES:
        return {}
    if not isinstance(code,str) or not code.replace('_','').isalnum() or len(code)>64:
        code='UNAVAILABLE'
    values = {k:max(-1,min(10000000,int(v))) for k,v in counts.items()
              if k in COUNTS and isinstance(v,(int,bool))}
    portal = hashlib.sha256(str(pid).encode()).hexdigest()[:12]
    signature = (code,tuple(sorted((k,v) for k,v in values.items() if k!='query_ms')))
    key = (portal,kind,stage)
    old = _seen.get(key)
    now = time.monotonic()
    if not old or old[0]!=signature or now-old[1]>=60:
        _seen[key]=(signature,now)
        if len(_seen)>96:
            _seen.pop(next(iter(_seen)))
        try:
            import xbmc
            text=' '.join(k+'='+str(v) for k,v in sorted(values.items()))
            xbmc.log('[XCMate][WIDGET47] flow='+_flow+' portal='+portal+' kind='+kind+
                     ' stage='+stage+' code='+code+' '+text,xbmc.LOGINFO)
        except (ImportError,AttributeError,RuntimeError):
            pass
    return dict(code=code,**values)


def save(pid,kind,stage,value):
    from programme_assets47 import writer
    from programme_index46 import encoded
    db=None
    try:
        db=writer()
        with db:
            db.execute('INSERT OR REPLACE INTO widget_diagnostics47 VALUES(?,?,?,?,?)',
                (str(pid),kind,stage,encoded(value),time.time()))
    except (OSError,sqlite3.Error,ValueError):
        pass
    finally:
        if db is not None:
            db.close()


def inspect_index(portal,kind,rows,code):
    """Worker-only exact count if affordable, unknown (-1) on budget/lock.

    Import counters describe received/stored sync rows, not distinct provider
    titles. No provider API/large JSON read is triggered to obtain a count.
    """
    if kind not in ('live','vod','series'):
        return
    pid=str(portal['id'])
    key=(pid,kind)
    if time.monotonic()<_indexed.get(key,0):
        return
    _indexed[key]=time.monotonic()+60
    from library_index import path
    from urllib.parse import quote
    db=None
    counts=dict(provider_received=-1,sync_stored=-1,indexed=-1,groups=-1,selected=len(rows))
    try:
        db=sqlite3.connect('file:'+quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.02)
        db.execute('PRAGMA query_only=ON')
        deadline=time.monotonic()+.1
        db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        sync=db.execute('SELECT sum(received),sum(stored) FROM sync_status WHERE pid=? AND kind=?',(pid,kind)).fetchone()
        if sync and sync[0] is not None:
            counts.update(provider_received=sync[0],sync_stored=sync[1] or 0)
        counts['groups']=db.execute('SELECT count(*) FROM groups WHERE pid=? AND kind=?',(pid,kind)).fetchone()[0]
        counts['indexed']=db.execute('SELECT count(DISTINCT sid) FROM readable_titles WHERE pid=? AND kind=?',(pid,kind)).fetchone()[0]
    except (sqlite3.Error,OSError):
        pass
    finally:
        if db is not None:
            db.close()
    value=note(pid,kind,'INDEX',code,**counts)
    save(pid,kind,'INDEX',value)


def counts(values):
    from media_art import valid_source
    import os
    local=dynamic=placeholder=events=matched=0
    for value in values:
        image=value.get('art',{}).get('thumb','')
        if valid_source(str(image).partition('|')[0]):
            dynamic+=1
        elif image and '/resources/media/' not in image.replace('\\','/'):
            local+=1
        else:
            placeholder+=1
        props=value.get('props',{})
        if props.get('XCMate.ProgrammeTitle46') and value.get('_programme46',{}).get('title'):
            events+=1
        if props.get('XCMate.ProgrammeDisplay47')=='PROGRAMME_IMAGE':
            matched+=1
    return dict(items=len(values),local_images=local,dynamic_images=dynamic,
                placeholders=placeholder,event_count=events,matched_images=matched)


def describe(pid,kind,values):
    return note(pid,kind,'ITEMS',**counts(values))


def status(pid):
    """Small private status view; texture references are not pixel evidence."""
    from programme_index46 import connect
    db=None
    values={}
    try:
        db=connect(False)
        if db is not None:
            for kind,stage,data,updated in db.execute(
                    'SELECT kind,stage,data,updated FROM widget_diagnostics47 WHERE pid=?',(str(pid),)):
                if kind in ('live','vod','series') and stage in STAGES and len(data)<4096:
                    values[kind+' '+stage]=dict(json.loads(data),age_seconds=max(0,int(time.time()-updated)))
    except (OSError,sqlite3.Error,ValueError,TypeError):
        pass
    finally:
        if db is not None:
            db.close()
    from programme_snapshot47 import status as programme_status
    return dict(stages=values,programme=programme_status(pid),skin_render='ANDROID_NOT_TESTED',
        texture_decode='NOT_OBSERVABLE_VIA_LISTITEM',unknown_count=-1)

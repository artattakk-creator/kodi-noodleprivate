"""Read-only rich-event propagation and fixed-code end-to-end evidence.

No title-only image matching, feed refresh, focus network or guide migration.
Source metadata is eligible only after exact source/text/interval verification.
"""
import hashlib
import json
import time
_seen={};_budgets={}


def trace(stage,event=None,code='READY',rows=0,duration_ms=0):
    stages={'SOURCE','MATCH','LOCAL_EVENT','IMAGE','CACHE','LISTITEM','FOCUS','MINI'}
    codes={'READY','NO_EPG','NO_SOURCE_FACTS','NO_IMAGE','PENDING','READY_STALE','IMAGE_DECODER_MISSING','LOCAL_IMAGE_MISSING','SOURCE_UNAVAILABLE','UNAVAILABLE',
           'NO_YEAR','NOT_CLASSIFIED_MOVIE','TMDB_DISABLED','TMDB_TOKEN_MISSING','NO_MATCH','NO_VALID_URL',
           'HELPER_AVAILABLE','HELPER_NOT_AVAILABLE','HELPER_VERSION_UNSUPPORTED','HELPER_LOOKUP_OK',
           'HELPER_NO_ID','HELPER_ART_MISSING','HELPER_BACKGROUND_UNAVAILABLE','HELPER_TIMEOUT',
           'NO_UNIQUE_MATCH','IMAGE_URL_VERIFIED','IMAGE_SHARED_EVENT',
           'BLOCKED_IMAGE_HOST_OR_URL','BLOCKED_CREDENTIAL_URL','AWAITING_BACKGROUND_REFRESH','URL_EXPIRED'}
    if stage not in stages:return
    code=code if code in codes else 'UNAVAILABLE'
    event=event or {}
    digest=hashlib.sha256(str(event.get('key','')).encode()).hexdigest()[:12]
    signature=(stage,digest,code)
    now=time.monotonic()
    if now-_seen.get(signature,-1e9)<60:return
    minute=int(now//60);budget=(minute,stage)
    if _budgets.get(budget,0)>=16:return
    _budgets[budget]=_budgets.get(budget,0)+1
    for old in list(_budgets):
        if old[0]<minute:_budgets.pop(old,None)
    _seen[signature]=now
    if len(_seen)>1024:_seen.pop(next(iter(_seen)))
    source=event.get('epg_source46',event.get('source_key46',''))
    source='XMLTV' if str(source).startswith('external:') else 'PROVIDER' if source=='provider' else 'UNKNOWN'
    try:
        import xbmc
        xbmc.log('[XCMate][PROGRAMME48] stage='+stage+' event='+digest+' source='+source+' code='+code+' rows='+str(max(0,int(rows)))+' duration_ms='+str(round(max(0,duration_ms),1)),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError,MemoryError):pass


def enrich(pid,cid,rows,source=None,sid48=None,revision48=None):
    from programme_store46 import read
    result=[]
    for raw in rows:
        value=dict(raw)
        if value.get('_fused52'):
            result.append(value);continue
        event=dict(start=value['start_timestamp'],stop=value['stop_timestamp'],title=value['name'],description=value['descr'],source=value.get('source',0))
        rich=None
        if sid48 is not None:
            from programme_index46 import event as cached_event
            from programme_events46 import key
            candidate=dict(event,pid=str(pid),sid=str(sid48),canonical=str(cid),revision=revision48)
            candidate['key']=key(pid,sid48,candidate)
            for field in ('source_key46','fact_revision46'):
                if value.get(field):candidate[field]=value[field]
            cached=cached_event(candidate)
            if cached:
                from programme_index46 import FIELDS
                rich={k:cached[k] for k in FIELDS if k in cached and k not in ('pid','sid','canonical','key','start','stop','title','description','source','revision','code')}
        if rich is None:rich=read(pid,cid,event,verify_source=True)
        if source and rich.get('epg_source46')!=source:rich={}
        value.update(rich)
        value['_metadata_verified48']=bool(rich.get('epg_source46') and not rich.get('metadata_code46'))
        result.append(value)
    return result


def source_metadata(event):
    from programme_store46 import metadata
    result=metadata(event)
    for key in ('xmltv_image','provider_image','subtitle','genre','episode_label','year','season','episode','cast','director','epg_source46','epg_text46','source_key46','fact_revision46','field_sources52','updated52'):
        if event.get(key) not in (None,'',[]):result[key]=event[key]
    return result

"""Pure event identity shared by the guide, mini, infobar and native widgets.

No files, database connections, HTTP, callbacks or configuration writes here.
Canonical IDs and source facts survive RAM-only Now/Next rollover.
"""


def identify(pid, sid, canonical, events):
    from programme_events46 import key
    result = []
    for event in events:
        value = dict(event)
        value['programme_key47'] = key(pid, sid, value)
        value['canonical46'] = str(canonical or '')
        result.append(value)
    return result


def bind(pid, channel, info, canonical=None):
    extra = channel.extra if hasattr(channel, 'extra') else channel
    sid = str(extra.get('sid', extra.get('stream_id', '')))
    value = dict(info)
    canonical = str(canonical if canonical is not None else value.get('canonical46', ''))
    value['canonical46'] = canonical
    value['events'] = identify(pid, sid, canonical, value.get('events', []))
    event = next((e for e in value['events'] if e.get('start') == value.get('start')
                  and e.get('stop') == value.get('stop') and e.get('title') == value.get('now')), None)
    value['programme_key47'] = event['programme_key47'] if event else ''
    return value


def fallback_window(pid, channels, mappings, start, stop, limit=48):
    """Read the already published additive cache if the master is unavailable.

    This creates neither guide nor cache; explicit mappings still win. Only
    verified, previously committed facts from currently configured sources are
    eligible. The primary guide remains authoritative whenever readable.
    """
    from programme_index46 import connect, window
    from local_epg import View, channel_keys
    import sqlite3
    db = None
    try:
        db = connect(False)
        if db is None:
            return None
    except (OSError, ValueError, sqlite3.Error,ImportError,AttributeError):
        return None
    finally:
        if db is not None:
            db.close()
    view = View()
    view.code = 'SHARED_LASTGOOD47'
    for channel in channels[:16]:
        sid, keys = channel_keys(channel, mappings)
        from epg_binding48 import binding
        selected48=binding(mappings,sid)
        for ident in keys:
            view.canonical[ident] = ident
            if selected48:view[ident] = window(pid, ident, start, stop, limit=limit,source48=selected48['source'])
            else:
                from epg_merge52 import window as merged_window52
                view[ident]=merged_window52(pid,sid,ident,start,stop,limit=limit,manual=bool(mappings.get(sid)))
    return view if any(view.values()) else None


def status(pid):
    """Bounded population checks; a schema/READY flag is not a filled guide."""
    from programme_index46 import connect
    import sqlite3,time
    db=None
    value=dict(facts=-1,prepared_events=-1,channels=-1,asset_references=-1,
               artwork_sample=0,artwork_sample_ready=0,artwork_sample_local_files=0,artwork_sample_missing_files=0,
               artwork_sample_codes={},asset_sample_codes={},image_decoder='UNAVAILABLE',artwork_sample_online_urls55=0)
    try:
        import PIL.Image
        value['image_decoder']='PIL_AVAILABLE_ANDROID_DECODE_NOT_TESTED'
    except ImportError:
        value['image_decoder']='IMAGE_DECODER_MISSING'
    try:
        db=connect(False)
        if db is None:
            return dict(value,code='NOT_CREATED')
        deadline=time.monotonic()+.1
        db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        for name,table in (('facts','facts'),('prepared_events','events'),('channels','channels47'),('asset_references','asset_refs47')):
            try:value[name]=db.execute('SELECT count(*) FROM '+table+' WHERE pid=?',(str(pid),)).fetchone()[0]
            except sqlite3.Error:pass
        import json
        from art_errors import CODES
        codes=set(CODES)|{'READY','READY_STALE','NO_IMAGE','PENDING','MEMORY_PRESSURE','CACHE_ERROR',
            'PROGRAMME_CACHE_BUDGET','IMAGE_DECODER_MISSING','UNSAFE_SOURCE','REDIRECT_BLOCKED','CONTENT_TYPE',
            'CONTENT_ENCODING','IMAGE_LIMIT','RESPONSE_LIMIT','RESEARCH_BUSY','DYNAMIC_APPROVED','DNS_UNAVAILABLE',
            'INVALID_LOCAL_IMAGE','PENDING_LOCAL_DOWNLOAD','LOCAL_HEADER_VALID','INVALID_SOURCE','NO_SOURCE',
            'URL_EXPIRED','BLOCKED_IMAGE_HOST_OR_URL','BLOCKED_CREDENTIAL_URL','AWAITING_BACKGROUND_REFRESH',
            'IMAGE_PREFLIGHT_FAILED','BLOCKED_NO_AUTHORIZED_API','PROGRAMME_DB_UNAVAILABLE'}
        def count_code(bucket,data):
            code=data.get('code','');code=code if code in codes else 'OTHER_CODE'
            bucket[code]=bucket.get(code,0)+1
        for raw, in db.execute('SELECT a.data FROM events e JOIN artwork a ON a.event_key=e.event_key WHERE e.pid=? LIMIT 128',(str(pid),)):
            if len(raw)>16384:continue
            art=json.loads(raw);value['artwork_sample']+=1
            count_code(value['artwork_sample_codes'],art)
            if art.get('code') in ('READY','READY_STALE') and art.get('source')!='placeholder':
                value['artwork_sample_ready']+=1
                import os
                from programme_art46 import root
                online=bool(art.get('url_version55')==1 and art.get('source_url'))
                value['artwork_sample_online_urls55']+=int(online)
                found=os.path.dirname(art.get('image',''))==root() and os.path.isfile(art.get('image',''))
                value['artwork_sample_local_files']+=int(found)
                value['artwork_sample_missing_files']+=int(not found and not online)
        try:
            for raw, in db.execute('SELECT data FROM asset_refs47 WHERE pid=? LIMIT 128',(str(pid),)):
                if len(raw)<=16384:count_code(value['asset_sample_codes'],json.loads(raw))
        except sqlite3.Error:pass
        code='DATA_EMPTY' if value['facts']==value['prepared_events']==0 else 'LOCAL_TEXT_AND_ART_REFERENCES' if value['artwork_sample_ready'] else 'LOCAL_TEXT_WITHOUT_MATCHED_ART'
        return dict(value,code=code)
    except (OSError,sqlite3.Error,ValueError,TypeError):
        return dict(value,code='POPULATION_UNAVAILABLE')
    finally:
        if db is not None:db.close()

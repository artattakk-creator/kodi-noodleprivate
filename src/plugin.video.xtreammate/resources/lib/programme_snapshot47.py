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
    except (OSError, ValueError, sqlite3.Error):
        return None
    finally:
        if db is not None:
            db.close()
    view = View()
    view.code = 'SHARED_LASTGOOD47'
    for channel in channels[:16]:
        sid, keys = channel_keys(channel, mappings)
        for ident in keys:
            view.canonical[ident] = ident
            view[ident] = window(pid, ident, start, stop, limit=limit)
    return view


def status(pid):
    """Bounded population checks; a schema/READY flag is not a filled guide."""
    from programme_index46 import connect
    import sqlite3,time
    db=None
    value=dict(facts=-1,prepared_events=-1,channels=-1,asset_references=-1,
               artwork_sample=0,artwork_sample_ready=0,image_decoder='UNAVAILABLE')
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
        for raw, in db.execute('SELECT a.data FROM events e JOIN artwork a ON a.event_key=e.event_key WHERE e.pid=? LIMIT 128',(str(pid),)):
            if len(raw)>16384:continue
            art=json.loads(raw);value['artwork_sample']+=1
            if art.get('code') in ('READY','READY_STALE') and art.get('source')!='placeholder':value['artwork_sample_ready']+=1
        code='DATA_EMPTY' if value['facts']==value['prepared_events']==0 else 'LOCAL_TEXT_AND_ART_REFERENCES' if value['artwork_sample_ready'] else 'LOCAL_TEXT_WITHOUT_MATCHED_ART'
        return dict(value,code=code)
    except (OSError,sqlite3.Error,ValueError,TypeError):
        return dict(value,code='POPULATION_UNAVAILABLE')
    finally:
        if db is not None:db.close()

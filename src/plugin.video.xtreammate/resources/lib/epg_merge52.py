"""Merge verified retained source facts on the existing shared read path.

No new EPG database, source requests, configuration writes or destructive
retention. Published intervals win conflicts; only proven same events donate
missing facts. Different channel IDs require an explicit per-source station proof.
"""
import bisect,hashlib,json,sqlite3,time

from epg_agent_catalog103 import EVENT_FIELDS

DETAILS = ('descr', 'subtitle', 'genre', 'season', 'episode', 'episode_label', 'year',
           'cast', 'cast_roles', 'director', 'age_rating', 'country', 'original_title', 'work_id',
           'external_ids', '_work_ids_verified85', 'xmltv_image', 'provider_image',
           'agent_art', 'xmltv_date', 'language', 'xmltv_title_lang',
           'xmltv_tmdb_id', 'xmltv_tmdb_score')
EVENT_FIELDS = ('name', 'start_timestamp', 'stop_timestamp')


def _external_ids(event):
    raw = event.get('external_ids')
    if not event.get('_work_ids_verified85') or not isinstance(raw, dict):
        return {}
    result = {}
    for key in ('imdb_id', 'tvdb_id', 'tvrage_id'):
        value = str(raw.get(key, '')).strip().casefold()
        if key == 'imdb_id':
            value = value.removeprefix('tt')
        if value.isascii() and value.isdigit() and 0 < len(value) <= 12:
            result[key] = int(value)
    return result


def _work_identity(event):
    value = event.get('work_id')
    if not isinstance(value, str) or not value.strip():
        return None
    namespace, separator, key = value.strip().partition(':')
    if not separator:
        namespace, key = '', namespace
    if not key:
        return None
    if key.isascii() and key.isdigit():
        key = key.lstrip('0') or '0'
    return namespace.casefold(), key


def same(a, b, cid):
    from epg_events import normalize, duplicate, title_key
    aa, bb = normalize(a, cid), normalize(b, cid)
    if not aa or not bb or not duplicate(aa, bb):
        return False
    if any(a.get(key) and b.get(key) and title_key(a[key]) != title_key(b[key])
           for key in ('subtitle', 'year', 'xmltv_tmdb_id')):
        return False
    left, right = _external_ids(a), _external_ids(b)
    if any(left[key] != right[key] for key in left.keys() & right.keys()):
        return False
    left_work, right_work = _work_identity(a), _work_identity(b)
    return not (left_work and right_work and left_work[0] == right_work[0] and left_work != right_work)


def _provenance(event, source, cid):
    if not source:
        return {}
    origin = dict(source=source, channel=str(cid))
    fields = {field: origin for field in (*EVENT_FIELDS, *DETAILS)
              if event.get(field) and not field.startswith('_')}
    fields.update(('agent_art.' + role, origin) for role in event.get('agent_art', {}))
    fields.update(event.get('field_sources52', {}))
    return fields


def retained(previous,incoming):
    """A shorter refresh of the very same source event is not a metadata wipe."""
    if not same(previous,incoming,incoming.get('channel','')):return incoming
    if previous.get('descr') and incoming.get('descr') and previous['descr'].strip()!=incoming['descr'].strip():return incoming
    value=dict(incoming)
    for field in DETAILS:
        if field=='xmltv_tmdb_score' and previous.get('xmltv_tmdb_id')!=value.get('xmltv_tmdb_id'):continue
        if not value.get(field) and previous.get(field):value[field]=previous[field]
    value['epg_text46']=hashlib.sha256(str(value.get('descr',''))[:4096].encode()).hexdigest()
    return value


def merge(primary,donors,cid,limit=256):
    """Pure deterministic interval union and per-field source provenance."""
    from epg_events import normalize,deduplicate
    def form(raw):
        n=normalize(raw,cid)
        if not n:return None
        value=dict(raw,name=n['title'],descr=n['description'],start_timestamp=n['start'],stop_timestamp=n['stop'],channel=str(cid))
        origin = raw.get('source_key46') or raw.get('epg_source46')
        if origin:
            value['field_sources52'] = _provenance(value, origin, raw.get('channel') or cid)
        return value
    accepted=[v for raw in deduplicate(primary,channel=cid) if (v:=form(raw))]
    def indices():
        accepted.sort(key=lambda p:(p['start_timestamp'],p['stop_timestamp']))
        starts=[];ends=[];last=0
        for item in accepted:
            starts.append(item['start_timestamp']);last=max(last,item['stop_timestamp']);ends.append(last)
        return starts,ends
    starts,ends=indices()
    for raw in sorted(donors,key=lambda e:(e.get('_source_index',0),e['start_timestamp'],e['stop_timestamp'],e.get('source_key46',''))):
        donor=form(raw)
        if not donor:continue
        a,b=donor['start_timestamp'],donor['stop_timestamp']
        lo=bisect.bisect_left(starts,a-120);hi=bisect.bisect_right(starts,a+120)
        peer=next((p for p in accepted[lo:hi] if same(p,donor,cid)),None)
        if peer is not None:
            # Same title/time with contradictory nonempty descriptions may be
            # a different episode. Keep the authoritative text/source guard.
            if peer.get('descr') and donor.get('descr') and peer['descr'].strip()!=donor['descr'].strip():continue
            source=donor.get('source_key46') or donor.get('epg_source46')
            if not source:continue
            origins = dict(peer.get('field_sources52', {}))
            donor_origins = donor.get('field_sources52', {})
            donated = False
            if (str(raw.get('channel') or cid) == str(cid)
                    and peer.get('source') == donor.get('source')
                    and (a, b) == (peer['start_timestamp'], peer['stop_timestamp'])
                    and peer['descr'] == donor['descr']):
                # Exact archive proof for the base time and text, even where
                # the master row only has a numeric priority.
                for field in (*EVENT_FIELDS, 'descr'):
                    if field in donor_origins:
                        origins.setdefault(field, donor_origins[field])
                peer.setdefault('epg_source46', source)
                peer.setdefault('source_key46', source)
            for field in DETAILS:
                if field == 'xmltv_tmdb_score' and donor.get('xmltv_tmdb_id') != peer.get('xmltv_tmdb_id'):
                    continue
                if field == 'external_ids' and not _external_ids(donor):
                    continue
                if field == '_work_ids_verified85' and donor.get('external_ids') != peer.get('external_ids'):
                    continue
                if field == 'cast_roles' and donor.get('cast') != peer.get('cast'):
                    continue
                if not peer.get(field) and donor.get(field):
                    peer[field] = donor[field]
                    if field in donor_origins:
                        origins[field] = donor_origins[field]
                    donated = True
                    if field == 'agent_art':
                        origins.update((key, value) for key, value in donor_origins.items()
                                       if key.startswith('agent_art.'))
                elif field == 'agent_art' and donor.get(field):
                    additional = {role: ref for role, ref in donor[field].items()
                                  if role not in peer[field]}
                    if additional:
                        peer[field] = dict(peer[field], **additional)
                        origins.update(('agent_art.' + role, donor_origins['agent_art.' + role])
                                       for role in additional)
                        donated = True
            if donor.get('_agent_event104') and not peer.get('_agent_event104'):
                peer.update((key, donor[key]) for key in EVENT_FIELDS if key in donor)
                donated = True
            if origins:
                peer['field_sources52'] = origins
            if donated:
                peer['epg_text46'] = hashlib.sha256(peer['descr'][:4096].encode()).hexdigest()
                peer['_fused52'] = True
                peer['_metadata_verified48'] = True
                peer['fact_revision46'] = hashlib.sha256(json.dumps(
                    [peer.get('fact_revision46'), donor.get('fact_revision46'), origins],
                    sort_keys=True).encode()).hexdigest()
                peer['updated52'] = max(peer.get('updated52', 0), donor.get('updated52', 0))
            continue
        before=bisect.bisect_left(starts,a);after=bisect.bisect_left(starts,b)
        if after>before or before and ends[before-1]>a:continue
        donor['_fused52']=True;donor['_metadata_verified48']=True
        accepted.append(donor)
        starts,ends=indices()
    return sorted(accepted,key=lambda e:(e['start_timestamp'],e['stop_timestamp']))[:min(256,max(1,limit))]


def publish_aliases(pid,source,aliases,streams,mappings,guide=None,proofs=None):
    """Worker-only additive SID/source/CID proof; no master schema migration."""
    from programme_index46 import connect
    db=None
    try:
        db=connect(True,guide)
        with db:
            db.execute('''CREATE TABLE IF NOT EXISTS source_aliases52(pid TEXT,sid TEXT,source_id TEXT,cid TEXT,proof TEXT,PRIMARY KEY(pid,sid,source_id))''')
            records=[]
            for row in streams:
                sid=str(row['sid']);cid=aliases.get(sid)
                if not cid:continue
                # The source importer supplies each station proof explicitly.
                proof=(proofs or {}).get(sid,'manual' if mappings.get(sid) else 'provider_id')
                records.append((str(pid),sid,source,str(cid),proof))
            if source=='agent':
                db.execute('DELETE FROM source_aliases52 WHERE pid=? AND source_id=?',(str(pid),source))
            db.executemany('INSERT OR REPLACE INTO source_aliases52 VALUES(?,?,?,?,?)',records)
        return True
    except (OSError,sqlite3.Error,ValueError):return False
    finally:
        if db is not None:db.close()


def proven_targets(db, pid, sid, allowed):
    """Read cross-CID station proofs shared by the guide and its diagnostics."""
    try:
        return [(source, cid) for source, cid in db.execute(
            "SELECT source_id,cid FROM source_aliases52 WHERE pid=? AND sid=? "
            "AND proof IN ('name','provider_id') LIMIT 32", (str(pid), str(sid)))
                if source in allowed]
    except sqlite3.OperationalError:
        return []  # Profiles without a verified source alias table.


def window(pid,sid,cid,start,stop,primary=(),limit=256,manual=False,guide=None):
    """Read retained facts and source aliases using bounded indexed queries."""
    from programme_index46 import connect,ranks,read_fact
    db=None;donors=[]
    try:
        db=connect(False,guide)
        if db is None:return list(primary)
        deadline=time.monotonic()+.06;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        allowed=ranks(pid);targets=[(None,str(cid))]
        indexed_agent = False
        if not manual:
            proven = proven_targets(db, pid, sid, allowed)
            agent_cid = next((channel for source, channel in proven if source == 'agent'), None)
            if agent_cid:
                from epg_agent_catalog103 import IndexReadError, for_portal, programmes, ready

                folder = for_portal(pid)
                indexed_agent = ready(folder)
                if indexed_agent:
                    try:
                        donors.extend(programmes(folder, agent_cid, start, stop, limit=limit))
                    except IndexReadError:
                        pass
                    primary = [row for row in primary if row.get('source') != allowed['agent']
                               and row.get('source_key46') != 'agent']
            targets.extend((source, channel) for source, channel in proven
                           if channel != str(cid) and (source != 'agent' or not indexed_agent))
        for source,channel in targets:
            sql='SELECT source_id,fingerprint,data,updated FROM facts WHERE pid=? AND cid=? AND start<? AND stop>?'
            args=[str(pid),channel,stop,start]
            if source:sql+=' AND source_id=?';args.append(source)
            sql+=' ORDER BY start,stop LIMIT ?';args.append(min(1024,max(128,limit*4)))
            for identity,fingerprint,data,updated in db.execute(sql,args):
                if identity not in allowed or (identity == 'agent' and indexed_agent) or len(data)>24576:continue
                value=read_fact(data)
                if identity=='compatibility' and primary:
                    # Legacy facts still require exact authoritative text and
                    # one unambiguous archived origin. This also preserves
                    # their fingerprint when a previously sidecar-only day
                    # now becomes part of the repaired master horizon.
                    peer=next((p for p in primary if p['start_timestamp']==value['start_timestamp'] and p['stop_timestamp']==value['stop_timestamp'] and p['name']==value['name'] and p['descr']==value['descr']),None)
                    if peer is None:continue
                    from programme_store46 import origin_matches
                    event=dict(start=peer['start_timestamp'],stop=peer['stop_timestamp'],title=peer['name'],source=peer.get('source',0))
                    if not origin_matches(pid,channel,event,identity,guide):continue
                value.update(_source_index=allowed[identity],source=allowed[identity],source_key46=identity,fact_revision46=fingerprint,updated52=updated)
                donors.append(value)
        primary = [dict(row, source_key46='provider', epg_source46='provider')
                   if row.get('source') == 0 and 'provider' in allowed else row
                   for row in primary]
        return merge(primary,donors,str(cid),limit)
    except (OSError,sqlite3.Error,ValueError,KeyError,TypeError):return list(primary)
    finally:
        if db is not None:db.close()

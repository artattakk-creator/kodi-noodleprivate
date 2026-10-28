"""Merge verified retained source facts on the existing shared read path.

No new EPG database, source requests, configuration writes or destructive
retention. Published intervals win conflicts; only proven same events donate
missing facts. Different channel IDs require an explicit per-source name match.
"""
import bisect,hashlib,json,sqlite3,time

DETAILS=('descr','subtitle','genre','season','episode','episode_label','year','cast','director','xmltv_image','provider_image')


def same(a,b,cid):
    from epg_events import normalize,duplicate
    aa=normalize(a,cid);bb=normalize(b,cid)
    return bool(aa and bb and duplicate(aa,bb))


def retained(previous,incoming):
    """A shorter refresh of the very same source event is not a metadata wipe."""
    if not same(previous,incoming,incoming.get('channel','')):return incoming
    value=dict(incoming)
    for field in DETAILS:
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
            origins=dict(peer.get('field_sources52',{}))
            for field in DETAILS:
                if not peer.get(field) and donor.get(field):
                    peer[field]=donor[field]
                    origins[field]=dict(source=source,channel=str(raw.get('channel') or cid))
            # Only fields from a verified exact/near-identical source record
            # are donated; episode/season conflicts fail same().
            if origins:
                peer['field_sources52']=origins
                peer['epg_source46']=peer.get('epg_source46') or source
                peer['epg_text46']=hashlib.sha256(peer['descr'][:4096].encode()).hexdigest()
                peer['_fused52']=True;peer['_metadata_verified48']=True
                peer['fact_revision46']=hashlib.sha256(json.dumps([peer.get('fact_revision46'),donor.get('fact_revision46'),origins],sort_keys=True).encode()).hexdigest()
                peer['updated52']=max(peer.get('updated52',0),donor.get('updated52',0))
            continue
        before=bisect.bisect_left(starts,a);after=bisect.bisect_left(starts,b)
        if after>before or before and ends[before-1]>a:continue
        donor['_fused52']=True;donor['_metadata_verified48']=True
        source=donor.get('source_key46') or donor.get('epg_source46')
        donor['field_sources52']={key:dict(source=source,channel=str(raw.get('channel') or cid)) for key in DETAILS if donor.get(key)}
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
                # Automatic different-CID aliases are produced only by the
                # existing unambiguous exact normalized channel-name matcher.
                proof=(proofs or {}).get(sid,'manual' if mappings.get(sid) else 'provider_id')
                records.append((str(pid),sid,source,str(cid),proof))
            db.executemany('INSERT OR REPLACE INTO source_aliases52 VALUES(?,?,?,?,?)',records)
        return True
    except (OSError,sqlite3.Error,ValueError):return False
    finally:
        if db is not None:db.close()


def window(pid,sid,cid,start,stop,primary=(),limit=256,manual=False,guide=None):
    """Read retained facts and source aliases using bounded indexed queries."""
    from programme_index46 import connect,ranks
    db=None;donors=[]
    try:
        db=connect(False,guide)
        if db is None:return list(primary)
        deadline=time.monotonic()+.06;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        allowed=ranks(pid);targets=[(None,str(cid))]
        if not manual:
            try:
                targets.extend((source,channel) for source,channel in db.execute('SELECT source_id,cid FROM source_aliases52 WHERE pid=? AND sid=? AND proof=\'name\' LIMIT 32',(str(pid),str(sid))) if source in allowed and channel!=str(cid))
            except sqlite3.OperationalError:pass  # Existing profiles have no aliases until a verified refresh.
        for source,channel in targets:
            sql='SELECT source_id,fingerprint,data,updated FROM facts WHERE pid=? AND cid=? AND start<? AND stop>?'
            args=[str(pid),channel,stop,start]
            if source:sql+=' AND source_id=?';args.append(source)
            sql+=' ORDER BY start,stop LIMIT ?';args.append(min(1024,max(128,limit*4)))
            for identity,fingerprint,data,updated in db.execute(sql,args):
                # Compatibility facts have no independently verified source
                # identity. Preserve the existing text/origin verifier rather
                # than treating them as qualified metadata donors.
                if identity not in allowed or identity=='compatibility' and primary or len(data)>24576:continue
                value=json.loads(data);value.update(_source_index=allowed[identity],source=allowed[identity],source_key46=identity,fact_revision46=fingerprint,updated52=updated)
                donors.append(value)
        return merge(primary,donors,str(cid),limit)
    except (OSError,sqlite3.Error,ValueError,KeyError,TypeError):return list(primary)
    finally:
        if db is not None:db.close()

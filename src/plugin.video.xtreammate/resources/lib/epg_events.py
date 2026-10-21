"""Deterministic event normalization shared by disk imports and local views."""
import re
import unicodedata


def integer(value):
    try: return int(float(value))
    except (ValueError, TypeError, OverflowError): return 0


def title_key(value):
    return re.sub(r'\W+', ' ', unicodedata.normalize('NFKC', str(value or '')).casefold()).strip()


def normalize(event, channel=''):
    if not isinstance(event, dict): return None
    start=integer(event.get('start_timestamp') or event.get('start'))
    stop=integer(event.get('stop_timestamp') or event.get('end_timestamp') or event.get('stop'))
    title=str(event.get('name') or event.get('title') or '').strip()
    if start<=0 or stop<=start or not title: return None
    return dict(event,start=start,stop=stop,title=title,
                description=str(event.get('descr') or event.get('description') or ''),
                _canonical=str(channel or event.get('channel') or event.get('cid') or ''))


def duplicate(a,b):
    if a['_canonical']!=b['_canonical'] or title_key(a['title'])!=title_key(b['title']): return False
    for key in ('episode_id','episode_num','episode','season','sub_title','sub-title'):
        if a.get(key) and b.get(key) and str(a[key])!=str(b[key]): return False
    overlap=min(a['stop'],b['stop'])-max(a['start'],b['start'])
    return (abs(a['start']-b['start'])<=120 and abs(a['stop']-b['stop'])<=120
            and overlap>0 and overlap>=.9*max(a['stop']-a['start'],b['stop']-b['start']))


def _rank(e):
    source=integer(e.get('_source_index',e.get('source',0)))
    # Existing source policy: provider, ordered external feeds, short fallback.
    priority=source if source>=0 else 1000000
    return (priority,-len(e['description']),-bool(e.get('episode_id') or e.get('episode_num')),
            e['start'],e['stop'],e['title'],e['description'])


def deduplicate(events,channel='',decisions=None):
    """Collapse only near-identical strongly overlapping slots, never neighbours.

    The caller supplies one canonical channel (aliases already resolved), or
    each row carries its own channel/cid. Inputs and legacy caches stay intact.
    """
    rows=[r for e in events if (r:=normalize(e,channel)) is not None]
    rows.sort(key=lambda e:(e['_canonical'],e['start'],e['stop'],_rank(e)))
    output=[];recent={}
    for row in rows:
        key=(row['_canonical'],title_key(row['title']))
        indices=[i for i in recent.get(key,[]) if row['start']-output[i]['start']<=120]
        recent[key]=indices
        candidate=next((i for i in indices if duplicate(output[i],row)),None)
        if candidate is None:
            indices.append(len(output));output.append(row);continue
        old=output[candidate]
        keep=min((old,row),key=_rank)
        output[candidate]=keep
        if decisions is not None and len(decisions)<64:
            decisions.append(dict(title=title_key(keep['title'])[:160],
                starts=[old['start'],row['start']],stops=[old['stop'],row['stop']],
                kept_start=keep['start'],source=keep.get('_source_index',keep.get('source',0))))
    return sorted(output,key=lambda e:(e['_canonical'],e['start'],e['stop'],_rank(e)))


def clean_stage(db,table,where='',args=()):
    """Bounded, channel-at-a-time SQLite cleanup before atomic publication.

    A moving 120-second buffer bounds memory independently of XMLTV size.
    Table names are internal constants, never provider/user input.
    """
    if table not in ('incoming','xml_stage'): raise ValueError('stage table')
    query='SELECT rowid,cid,start,stop,title,description'+(',source' if table=='incoming' else '')+' FROM '+table+where+' ORDER BY cid,start,stop'
    pending=[]
    for raw in db.execute(query,args):
        row=normalize(dict(cid=raw[1],start=raw[2],stop=raw[3],title=raw[4],description=raw[5],source=raw[6] if table=='incoming' else 0,_rowid=raw[0]))
        pending=[p for p in pending if p['_canonical']==row['_canonical'] and row['start']-p['start']<=120]
        old=next((p for p in pending if duplicate(p,row)),None)
        if old is None:
            if len(pending)>=512: raise ValueError('EPG dense interval budget')
            pending.append(row);continue
        keep=min((old,row),key=_rank);drop=row if keep is old else old
        db.execute('DELETE FROM '+table+' WHERE rowid=?',(drop['_rowid'],))
        if keep is row: pending.remove(old);pending.append(row)

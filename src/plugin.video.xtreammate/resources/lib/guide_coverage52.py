"""Explicit read-only channel/day/source coverage, never an import or cleanup."""
import hashlib,os,sqlite3,time
from urllib.parse import quote


def union_seconds(intervals,left,right):
    total=0;end=left
    for a,b in sorted(intervals):
        a=max(left,a,end);b=min(right,b)
        if b>a:total+=b-a;end=b
    return total


def inspect(pid,sid,cid,guide=None,now=None):
    from guide_store import path,day_window
    from programme_index46 import connect,ranks
    from epg_sources import configuration
    from epg_binding48 import binding
    filename=guide or path();db=aux=None
    if not os.path.isfile(filename):return dict(code='NOT_CREATED')
    deadline=time.monotonic()+.5
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.03)
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN');db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        selected=binding(configuration(pid)['mappings'],sid);allowed=ranks(pid)
        targets={(source,str(cid)) for source in allowed if source!='compatibility'}
        if selected:targets={(selected['source'],selected['channel'])}
        aux=connect(False,guide)
        if aux is not None:aux.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        if aux is not None and not selected:
            try:targets.update((source,channel) for source,channel in aux.execute("SELECT source_id,cid FROM source_aliases52 WHERE pid=? AND sid=? AND proof='name' LIMIT 32",(str(pid),str(sid))) if source in allowed)
            except sqlite3.OperationalError:pass
        left=day_window(-7,now)[0];right=day_window(21,now)[0];matrix=[];source_summary=[]
        for source,channel in sorted(targets):
            if time.monotonic()>deadline:raise TimeoutError()
            records=db.execute('SELECT start,stop FROM guide44_inputs WHERE pid=? AND source_id=? AND cid=? AND start<? AND stop>? ORDER BY start,stop LIMIT 10001',(str(pid),source,channel,right,left)).fetchall()
            if len(records)>10000:return dict(code='COVERAGE_BUDGET',coverage=None)
            # .46 retained days 11–20 in the shared facts table before the
            # master horizon was repaired. Include those genuine stored rows
            # without requiring another network import; count each slot once.
            if aux is not None:
                facts=aux.execute('SELECT start,stop FROM facts WHERE pid=? AND source_id=? AND cid=? AND start<? AND stop>? ORDER BY start,stop LIMIT 10001',(str(pid),source,channel,right,left)).fetchall()
                records=sorted(set(map(tuple,records))|set(map(tuple,facts)))
                if len(records)>10000:return dict(code='COVERAGE_BUDGET',coverage=None)
            if not records:continue
            source_summary.append(dict(source=source,channel=hashlib.sha256(channel.encode()).hexdigest()[:12],events=len(records),first=min(r[0] for r in records),last=max(r[1] for r in records)))
            for day in range(-7,21):
                a,b=day_window(day,now);rows=[r for r in records if r[0]<b and r[1]>a]
                seconds=union_seconds(rows,a,b)
                matrix.append(dict(source=source,channel=source_summary[-1]['channel'],day=day,date=time.strftime('%Y-%m-%d',time.localtime(a)),events=len(rows),covered_seconds=seconds,day_seconds=b-a,coverage=round(seconds/(b-a),6)))
        meta=db.execute('SELECT updated FROM guide_meta WHERE pid=?',(str(pid),)).fetchone()
        return dict(code='READY',last_good=meta[0] if meta else None,sources=source_summary,matrix=matrix)
    except (OSError,sqlite3.Error,TimeoutError,ValueError):return dict(code='COVERAGE_UNAVAILABLE',coverage=None)
    finally:
        if db is not None:db.close()
        if aux is not None:aux.close()

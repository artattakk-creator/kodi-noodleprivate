"""Index-backed widget candidates; never ORDER a UNION materialized view.

Read thin keys before loading at most 24 complete payloads. Works with existing
legacy/v2 indexes; no schema migration, write connection or COUNT/GROUP BY.
"""
import json


def groups(reader,kind):
    if not hasattr(reader,'_groups44'):reader._groups44={}
    if kind not in reader._groups44:
        from group_selection import enabled_ids
        rows=reader._query('SELECT * FROM groups WHERE pid=? AND kind=? ORDER BY ordinal',(reader.pid,kind))
        allowed=enabled_ids(reader.pid,kind,[dict(category_id=g['cid']) for g in rows]);reader._selections[kind]=allowed
        reader._groups44[kind]=[g for g in rows if g['cid'] in allowed]
    return reader._groups44[kind]


def get(reader,kind,sid):
    groups(reader,kind)
    sql='''/* direct44 */ SELECT i.payload FROM items_v2 i JOIN heads h USING(pid,kind,cid,generation)
      WHERE i.pid=? AND i.kind=? AND i.sid=? AND i.cid IN(SELECT cid FROM selected_categories) LIMIT 1'''
    rows=reader._query(sql,(reader.pid,kind,str(sid)),kind)
    if not rows:
        rows=reader._query('''/* direct44 */ SELECT t.payload FROM titles t WHERE t.pid=? AND t.kind=? AND t.sid=?
          AND t.cid IN(SELECT cid FROM selected_categories) AND NOT EXISTS(SELECT 1 FROM heads h WHERE h.pid=t.pid AND h.kind=t.kind AND h.cid=t.cid) LIMIT 1''',(reader.pid,kind,str(sid)),kind)
    return json.loads(rows[0]['payload']) if rows else None


def small(reader,kind,category=None,limit=24,pin=None):
    groups(reader,kind);limit=min(24,max(1,int(limit)))
    allowed=reader._selections[kind]
    if category is not None and str(category) not in allowed:return []
    # A title can be in many enabled groups. Bound thin candidates by that
    # multiplicity, not a fixed 4x payload limit which can yield only 2 titles.
    cap=min(4096,limit*max(1,len(allowed)))
    where='i.pid=? AND i.kind=? AND i.cid IN(SELECT cid FROM selected_categories)';args=[reader.pid,kind]
    if category is not None:where+=' AND i.cid=?';args.append(str(category))
    v2index='group_order_v2' if kind=='live' and category is not None else 'recent_v2'
    order='i.ordinal' if kind=='live' else 'i.added DESC'
    v2=reader._query('''/* direct44 */ SELECT i.sid,i.cid,i.generation,i.added,i.ordinal FROM items_v2 i INDEXED BY '''+v2index+''' JOIN heads h USING(pid,kind,cid,generation) WHERE '''+where+' ORDER BY '+order+' LIMIT ?',args+[cap],kind)
    legacy_where=where.replace('i.','t.')
    order='t.ordinal' if kind=='live' else 't.added DESC,t.ordinal'
    old=reader._query('''/* direct44 */ SELECT t.sid,t.cid,t.added,t.ordinal FROM titles t WHERE '''+legacy_where+''' AND NOT EXISTS(SELECT 1 FROM heads h WHERE h.pid=t.pid AND h.kind=t.kind AND h.cid=t.cid) ORDER BY '''+order+' LIMIT ?',args+[cap],kind)
    keys=[dict(r,_table='items_v2') for r in v2]+[dict(r,_table='titles') for r in old]
    keys.sort(key=lambda r:(r['ordinal'],r['sid'],r['cid']) if kind=='live' else (r['added'] is None,-(r['added'] or 0),r['ordinal'],r['sid'],r['cid']))
    chosen=[];seen=set()
    for row in keys:
        if row['sid'] in seen:continue
        seen.add(row['sid']);chosen.append(row)
        if len(chosen)==limit:break
    payloads={}
    for table in ('items_v2','titles'):
        records=[r for r in chosen if r['_table']==table]
        if not records:continue
        clauses=[];parameters=[reader.pid,kind]
        for record in records:
            if table=='items_v2':clauses.append('(cid=? AND generation=? AND sid=?)');parameters.extend((record['cid'],record['generation'],record['sid']))
            else:clauses.append('(sid=?)');parameters.append(record['sid'])
        rows=reader._query('/* direct44 */ SELECT sid,payload FROM '+table+' WHERE pid=? AND kind=? AND ('+' OR '.join(clauses)+')',parameters)
        for value in rows:payloads[value['sid']]=json.loads(value['payload'])
    rows=[payloads[r['sid']] for r in chosen if r['sid'] in payloads]
    if pin:
        pinned=get(reader,kind,pin)
        if pinned and (category is None or str(pinned.get('category_id',''))==str(category)):
            rows=[pinned]+[r for r in rows if r['sid']!=str(pin)]
    return rows[:limit]

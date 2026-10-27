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
    heads=reader._query('SELECT cid FROM heads WHERE pid=? AND kind=?',(reader.pid,kind))
    headed={r['cid'] for r in heads}
    v2=reader._query('''/* direct44 */ SELECT i.sid,i.cid,i.generation,i.added,i.ordinal FROM items_v2 i INDEXED BY '''+v2index+''' JOIN heads h USING(pid,kind,cid,generation) WHERE '''+where+' ORDER BY '+order+' LIMIT ?',args+[cap],kind) if headed.intersection(allowed) else []
    legacy_where=where.replace('i.','t.')
    order='t.ordinal' if kind=='live' else 't.added DESC,t.ordinal'
    # Retained legacy payloads are deliberately not deleted by v2 sync. A
    # global anti-join can scan that entire archive to prove there are no
    # eligible old rows, exhausting every widget invocation's same budget.
    # Exclude replaced groups BEFORE touching titles; force the matching
    # ordering index to avoid sorting a large legacy movie catalogue.
    legacy_groups=set(allowed)-headed
    if category is not None:legacy_groups.intersection_update((str(category),))
    if legacy_groups:
        # Configured groups can be empty or not imported. Prove existence by
        # one category-index seek per group, rather than scanning every old
        # movie to discover that those groups have no retained rows.
        populated=reader._query('''/* direct44 */ SELECT g.cid FROM groups g WHERE g.pid=? AND g.kind=?
          AND g.cid IN(SELECT cid FROM selected_categories)
          AND NOT EXISTS(SELECT 1 FROM heads h WHERE h.pid=g.pid AND h.kind=g.kind AND h.cid=g.cid)
          AND EXISTS(SELECT 1 FROM titles t INDEXED BY category_titles WHERE t.pid=g.pid AND t.kind=g.kind AND t.cid=g.cid LIMIT 1)''',(reader.pid,kind),kind)
        legacy_groups.intersection_update(r['cid'] for r in populated)
    old=[]
    if legacy_groups:
        index='category_titles' if kind=='live' and category is not None else 'recent_titles'
        legacy_where+=' AND t.cid NOT IN(SELECT cid FROM heads WHERE pid=? AND kind=?)'
        old=reader._query('''/* direct44 */ SELECT t.sid,t.cid,t.added,t.ordinal FROM titles t INDEXED BY '''+index+' WHERE '+legacy_where+' ORDER BY '+order+' LIMIT ?',args+[reader.pid,kind,cap],kind)
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

"""Movie payload point reads over the existing catalog, without schema writes.

Putting 24 OR branches after only (pid, kind) makes SQLite choose identity_v2
and scan every movie. UNION ALL keeps each complete primary key independently
searchable. The successful series reader deliberately keeps its existing path.
"""
import json


def expand_keys(v2,legacy,limit,cap,fetch_v2,fetch_legacy):
    """Start with 24 keys, expand only if actual cross-group duplicates require it.

    .46 fetched up to 4096 keys solely because many groups were enabled, even
    when the first 24 were already distinct. The active SQL budget still limits
    pathological duplicate catalogs; no large Python payload is materialized.
    """
    while len({r['sid'] for r in v2+legacy})<limit and cap<4096 and (len(v2)==cap or len(legacy)==cap):
        cap=min(4096,cap*2)
        v2=fetch_v2(cap)
        legacy=fetch_legacy(cap)
    return v2,legacy


def payloads(reader, records, table):
    if table not in ('items_v2', 'titles'):
        raise ValueError('WIDGET_TABLE')
    statements, args = [], []
    for record in records[:24]:
        if table == 'items_v2':
            statements.append('SELECT sid,payload FROM items_v2 '
                              'WHERE pid=? AND kind=? AND cid=? AND generation=? AND sid=?')
            args.extend((reader.pid, 'vod', record['cid'], record['generation'], record['sid']))
        else:
            statements.append('SELECT sid,payload FROM titles WHERE pid=? AND kind=? AND sid=?')
            args.extend((reader.pid, 'vod', record['sid']))
    if not statements:
        return {}
    rows = reader._query('/* direct44 */ ' + ' UNION ALL '.join(statements), args)
    return {row['sid']: json.loads(row['payload']) for row in rows}

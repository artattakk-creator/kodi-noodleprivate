"""Private scoped backup and non-destructive group generations for published IDs.

No call to the new-portal wizard writer, replace_catalog, cache deletion, or
provider-wide sync. Staging never changes a readable head until EOF + verify.
"""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid

from vodsync_api72 import SyncError, identity


def schema(db):
    db.executescript('''CREATE TABLE IF NOT EXISTS vodsync72_units(
      pid TEXT,kind TEXT,cid TEXT,account TEXT,generation TEXT,state TEXT,
      rows INTEGER,digest TEXT,counts TEXT,updated REAL,
      PRIMARY KEY(pid,kind,cid));''')
    db.commit()


def group_digest(db, pid, kind, cid, generation=None):
    h = hashlib.sha256(); count = 0
    sql = ('SELECT sid,ordinal,title,search,added,payload FROM items_v2 WHERE pid=? AND kind=? AND cid=? AND generation=? ORDER BY sid'
           if generation else 'SELECT sid,ordinal,title,search,added,payload FROM readable_titles WHERE pid=? AND kind=? AND cid=? ORDER BY sid')
    args = (pid, kind, cid, generation) if generation else (pid, kind, cid)
    for row in db.execute(sql, args):
        h.update(json.dumps(tuple(row), ensure_ascii=False, separators=(',', ':')).encode()); h.update(b'\n'); count += 1
    return count, h.hexdigest()


def backup(pid, kinds, filename, folder, selections, cancel=lambda: False):
    """Only this portal's active VOD/series metadata; no account/token files."""
    from library_index import connect
    from wizard_storage71 import protect
    from wizard_resume53 import write_file
    from import_budget import check_space
    target = Path(folder) / ('before-' + uuid.uuid4().hex + '.sqlite')
    fd = os.open(str(target), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    protect(str(target), fd=fd); os.close(fd)
    source = connect(filename); dest = sqlite3.connect(str(target))
    try:
        dest.executescript('''CREATE TABLE titles(pid TEXT,kind TEXT,sid TEXT,cid TEXT,ordinal INTEGER,title TEXT,search TEXT,added INTEGER,payload TEXT);
          CREATE TABLE groups(pid TEXT,kind TEXT,cid TEXT,title TEXT,ordinal INTEGER);
          CREATE TABLE catalog(pid TEXT,kind TEXT,revision TEXT,updated REAL);
          CREATE TABLE selection(kind TEXT PRIMARY KEY,payload TEXT);''')
        source.execute('BEGIN')
        for kind in kinds:
            if cancel(): raise SyncError('CANCELLED')
            estimate = source.execute('SELECT coalesce(sum(length(payload)),0) FROM readable_titles WHERE pid=? AND kind=?', (pid, kind)).fetchone()[0]
            check_space(str(target), estimate * 3)
            for table in ('titles', 'groups', 'catalog'):
                rows = source.execute('SELECT * FROM ' + ('readable_titles' if table == 'titles' else table) + ' WHERE pid=? AND kind=?', (pid, kind))
                columns = 9 if table == 'titles' else 5 if table == 'groups' else 4
                while True:
                    if cancel(): raise SyncError('CANCELLED')
                    batch = rows.fetchmany(256)
                    if not batch: break
                    check_space(str(target), sum(len(str(tuple(row))) for row in batch)*3)
                    dest.executemany('INSERT INTO ' + table + ' VALUES(' + ','.join('?' * columns) + ')', batch)
            dest.execute('INSERT INTO selection VALUES(?,?)', (kind, json.dumps(selections.get(kind))))
        dest.commit()
        if dest.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise SyncError('BACKUP_VERIFY')
        # Verify complete scoped row counts and metadata with independent reads.
        for kind in kinds:
            for table in ('titles', 'groups', 'catalog'):
                def digest(database, name):
                    h = hashlib.sha256(); count = 0
                    for row in database.execute('SELECT * FROM ' + name + ' WHERE pid=? AND kind=? ORDER BY 1,2,3,4', (pid, kind)):
                        if cancel(): raise SyncError('CANCELLED')
                        h.update(json.dumps(tuple(row), ensure_ascii=False).encode()); h.update(b'\n'); count += 1
                    return count, h.hexdigest()
                if digest(source, 'readable_titles' if table == 'titles' else table) != digest(dest, table): raise SyncError('BACKUP_VERIFY')
    finally:
        source.close(); dest.close()
    with target.open('rb') as stream:
        os.fsync(stream.fileno()); digest = hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else _sha(stream)
    write_file(str(target) + '.json', dict(schema=1, sha256=digest, kinds=list(kinds), credentials=False))
    verify_backup(str(target))
    return str(target)


def _sha(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(65536), b''): h.update(chunk)
    return h.hexdigest()


def verify_backup(filename):
    from wizard_storage71 import readable
    if not readable(filename) or not readable(filename + '.json'):
        raise SyncError('BACKUP_PRIVACY')
    with open(filename + '.json', encoding='utf-8') as stream: manifest = json.load(stream)
    with open(filename, 'rb') as stream: actual = _sha(stream)
    if actual != manifest['sha256']: raise SyncError('BACKUP_VERIFY')
    from urllib.parse import quote
    db = sqlite3.connect('file:' + quote(filename, safe='/') + '?mode=ro', uri=True)
    try:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': raise SyncError('BACKUP_VERIFY')
        if db.execute("SELECT count(*) FROM titles WHERE kind NOT IN ('vod','series')").fetchone()[0]: raise SyncError('BACKUP_SCOPE')
    finally: db.close()
    return manifest


def upsert(session, kind, group, cancel, status):
    from library_index import connect, FIELDS, normalized
    from latest_media import added_timestamp
    from import_budget import check_space
    from vodsync_api72 import iterate, ACTIONS
    pid, cid = session.pid, str(group['category_id'])
    db = connect(session.filename, write=True)
    generation = uuid.uuid4().hex
    counts = dict(read=0, new=0, changed=0, unchanged=0, skipped=0, errors=0)
    try:
        previous = db.execute('SELECT * FROM vodsync72_units WHERE pid=? AND kind=? AND cid=?', (pid, kind, cid)).fetchone()
        if previous and previous['account'] == session.account and previous['state'] == 'COMMITTED':
            head = db.execute('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?', (pid, kind, cid)).fetchone()
            if head and head[0] == previous['generation'] and group_digest(db, pid, kind, cid, head[0]) == (previous['rows'], previous['digest']):
                # Only an interrupted activation is resumed; a fully completed
                # run is intentionally scanned again for new/changed titles.
                session.activate(kind, cid, cancel)
                with db: db.execute("UPDATE vodsync72_units SET state='DONE' WHERE pid=? AND kind=? AND cid=?", (pid, kind, cid))
                return dict(json.loads(previous['counts']), resumed=True)
        before = group_digest(db, pid, kind, cid)
        old_head = db.execute('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?', (pid, kind, cid)).fetchone()
        old_head = old_head[0] if old_head else None
        # Clean only this operation's abandoned private staging, never a head.
        if previous and previous['state'] == 'RUNNING':
            with db:
                db.execute('DELETE FROM items_v2 WHERE pid=? AND kind=? AND cid=? AND generation=? AND NOT EXISTS(SELECT 1 FROM heads WHERE pid=? AND kind=? AND cid=? AND generation=?)',
                           (pid, kind, cid, previous['generation'], pid, kind, cid, previous['generation']))
        with db:
            db.execute('INSERT INTO items_v2 SELECT pid,kind,sid,cid,?,ordinal,title,search,added,payload FROM readable_titles WHERE pid=? AND kind=? AND cid=?', (generation, pid, kind, cid))
            db.execute('INSERT OR REPLACE INTO vodsync72_units VALUES(?,?,?,?,?,?,?,?,?,?)', (pid, kind, cid, session.account, generation, 'RUNNING', 0, '', '{}', time.time()))
        db.execute('CREATE TEMP TABLE seen(sid TEXT PRIMARY KEY)')
        ordinal = db.execute('SELECT coalesce(max(ordinal),0) FROM items_v2 WHERE pid=? AND kind=? AND cid=? AND generation=?', (pid, kind, cid, generation)).fetchone()[0]
        batch = []
        def flush():
            if cancel(): raise SyncError('CANCELLED')
            check_space(session.filename, sum(len(r[-1]) for r in batch)*4)
            with db:
                db.executemany('INSERT OR REPLACE INTO items_v2 VALUES(?,?,?,?,?,?,?,?,?,?)', batch)
                session.heartbeat(db)
            batch.clear()
            status(None, dict(phase=kind.upper() + '_ITEMS', kind=kind, **counts))
        for item in iterate(session.client, kind, cid=cid, cancel=cancel):
            if cancel(): raise SyncError('CANCELLED')
            counts['read'] += 1
            actual = identity(item.get('category_id'))
            if actual != cid:
                counts['skipped'] += 1
                continue  # A provider ignoring category_id may not touch peers.
            sid = identity(item.get(ACTIONS[kind][2]))
            try: db.execute('INSERT INTO seen VALUES(?)', (sid,))
            except sqlite3.IntegrityError: raise SyncError('DUPLICATE_ID') from None
            title = item.get('name')
            if not isinstance(title, str) or not title.strip(): raise SyncError('SCHEMA')
            old = db.execute('SELECT ordinal,payload,added FROM items_v2 WHERE pid=? AND kind=? AND cid=? AND generation=? AND sid=?', (pid, kind, cid, generation, sid)).fetchone()
            payload = json.loads(old['payload']) if old else {}
            # Absent/empty provider artwork must not destroy retained metadata.
            for key in FIELDS:
                if key not in item or item[key] in (None, '', []): continue
                value = item[key]
                if isinstance(value, str): payload[key] = value[:4096]
                elif isinstance(value, (int, float, bool)): payload[key] = value
                elif isinstance(value, list): payload[key] = [str(v)[:4096] for v in value[:8] if isinstance(v, (str, int, float))]
            added = added_timestamp(item.get('added')) or added_timestamp(item.get('date_added')) or (old['added'] if old else None)
            payload.update(sid=sid, category_id=cid, name=title[:512], kind=kind, added_at=added)
            counts['new' if old is None else 'unchanged' if json.loads(old['payload']) == payload else 'changed'] += 1
            ordinal += int(old is None)
            batch.append((pid, kind, sid, cid, generation, old['ordinal'] if old else ordinal, title[:512], normalized(title), added, json.dumps(payload, ensure_ascii=False)))
            if len(batch) >= 256: flush()
        flush()
        if not counts['new'] + counts['changed'] + counts['unchanged']:
            raise SyncError('FILTERED_SOURCE' if counts['read'] else 'SOURCE_EMPTY')
        status(None, dict(phase='VERIFY', kind=kind, **counts))
        rows, digest = group_digest(db, pid, kind, cid, generation)
        if rows != before[0] + counts['new']: raise SyncError('READBACK')
        if cancel(): raise SyncError('CANCELLED')
        session.ensure_connection()
        status(None, dict(phase='COMMIT', kind=kind, **counts))
        with db:
            db.execute('BEGIN IMMEDIATE')
            current = db.execute('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?', (pid, kind, cid)).fetchone()
            if (current[0] if current else None) != old_head or group_digest(db, pid, kind, cid) != before:
                raise SyncError('CONCURRENT_CHANGE')
            if cancel(): raise SyncError('CANCELLED')
            db.execute('INSERT OR REPLACE INTO heads VALUES(?,?,?,?,?)', (pid, kind, cid, generation, time.time()))
            db.execute('INSERT OR REPLACE INTO catalog VALUES(?,?,?,?)', (pid, kind, generation, time.time()))
            position = db.execute('SELECT ordinal FROM groups WHERE pid=? AND kind=? AND cid=?', (pid, kind, cid)).fetchone()
            position = position[0] if position else db.execute('SELECT coalesce(max(ordinal),0)+1 FROM groups WHERE pid=? AND kind=?', (pid, kind)).fetchone()[0]
            db.execute('INSERT OR REPLACE INTO groups VALUES(?,?,?,?,?)', (pid, kind, cid, str(group['category_name']), position))
            db.execute("UPDATE vodsync72_units SET state='COMMITTED',rows=?,digest=?,counts=?,updated=? WHERE pid=? AND kind=? AND cid=?", (rows, digest, json.dumps(counts), time.time(), pid, kind, cid))
        # Independent connection, after transaction completion, not in-memory
        # counters or a read of this connection's uncommitted state.
        check = connect(session.filename)
        try:
            head = check.execute('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?', (pid, kind, cid)).fetchone()
            if not head or head[0] != generation or group_digest(check, pid, kind, cid, generation) != (rows, digest):
                raise SyncError('READBACK')
        finally: check.close()
        session.activate(kind, cid, cancel)
        with db: db.execute("UPDATE vodsync72_units SET state='DONE' WHERE pid=? AND kind=? AND cid=?", (pid, kind, cid))
        # Bound growth of our own replaced generations, after verified backup,
        # cold readback and activation. Never prune another writer's generation
        # or any readable head, title, artwork file or user database.
        if previous and previous['state'] == 'DONE' and previous['generation'] == old_head:
            while True:
                with db:
                    cursor = db.execute('''DELETE FROM items_v2 WHERE rowid IN
                      (SELECT i.rowid FROM items_v2 i WHERE pid=? AND kind=? AND cid=? AND generation=?
                       AND NOT EXISTS(SELECT 1 FROM heads h WHERE h.pid=i.pid AND h.kind=i.kind AND h.cid=i.cid AND h.generation=i.generation) LIMIT 256)''',
                       (pid, kind, cid, old_head))
                if cursor.rowcount < 256: break
        return dict(counts, stored=rows)
    except Exception as exc:
        from vodsync_api72 import failure
        problem = failure(exc); problem.counts72 = dict(counts, errors=1)
        raise problem from None
    finally:
        db.close()

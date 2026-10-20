"""Selective non-Xtream category imports into existing versioned SQLite index."""
import os
import time
import uuid


def sync_kind(portal,kind,force=False,cancel=lambda:False,requested_at=None,local_only=False):
    from library_index import connect,import_group,_sync_note
    from source_adapters import for_portal
    from group_selection import enabled_ids,load
    from m3u_store import path as playlist_path,connect as playlist_connect
    adapter=for_portal(portal);pid=str(portal['id'])
    if not local_only and not portal.get('include_'+kind,True): return
    db=connect(write=True);owner=uuid.uuid4().hex
    try:
        with db:
            lease=db.execute('SELECT until FROM sync_leases WHERE pid=? AND kind=?',(pid,kind)).fetchone()
            if lease and lease[0]>time.time(): return
            db.execute('INSERT OR REPLACE INTO sync_leases VALUES(?,?,?,?)',(pid,kind,owner,time.time()+330))
        groups=adapter.categories(kind)
        if portal['type']=='m3u':
            filename=playlist_path(pid)
            updated=modified=0
            if os.path.isfile(filename):
                saved=playlist_connect(filename)
                try:
                    row=saved.execute("SELECT v FROM meta WHERE k='updated'").fetchone();updated=float(row[0]) if row else 0
                    row=saved.execute("SELECT v FROM meta WHERE k='modified'").fetchone();modified=float(row[0]) if row else 0
                finally: saved.close()
            if not local_only and ((force and (requested_at is None or updated<requested_at)) or not updated or time.time()-updated>12*3600):
                adapter.authenticate(cancel)
            groups=adapter.categories(kind,remote=True)
        elif force or not groups:
            groups=adapter.categories(kind,remote=True)
        allowed=enabled_ids(pid,kind,groups)
        if not portal.get('source_schema') and load(pid,kind) is None:
            # Existing non-Xtream sources need explicit category opt-in.
            # Discover metadata, preserve legacy routes, do not import countries.
            allowed=set()
        with db:
            db.executemany('INSERT OR REPLACE INTO groups VALUES(?,?,?,?,?)',[(pid,kind,str(g['category_id']),str(g['category_name']),i) for i,g in enumerate(groups)])
        if portal['type']=='m3u':
            # Private group kinds are authoritative after an explicit edit.
            valid={str(g['category_id']) for g in groups}
            stale=[r[0] for r in db.execute('SELECT cid FROM groups WHERE pid=? AND kind=?',(pid,kind)) if r[0] not in valid]
            with db: db.executemany('DELETE FROM groups WHERE pid=? AND kind=? AND cid=?',[(pid,kind,cid) for cid in stale])
        completed=set()
        for group in groups:
            cid=str(group['category_id'])
            if cid not in allowed or cid in completed: continue
            if cancel(): return
            head=db.execute('SELECT updated FROM heads WHERE pid=? AND kind=? AND cid=?',(pid,kind,cid)).fetchone()
            if not force and head and time.time()-head[0]<12*3600 and (portal['type']!='m3u' or head[0]>=modified): continue
            with db: db.execute('UPDATE sync_leases SET until=? WHERE pid=? AND kind=? AND owner=?',(time.time()+330,pid,kind,owner))
            _sync_note(pid,kind,cid,'INDEXING')
            try:
                counts=import_group(pid,kind,cid,adapter.entries(kind,cid,cancel,allowed=allowed),cancel=cancel,allowed=allowed)
                completed.update(counts['categories'])
                _sync_note(pid,kind,cid,'READY',counts)
            except Exception as exc:
                # The local editor can intentionally disable/delete the final
                # row. An authoritative empty PRIVATE playlist may publish an
                # empty head; empty/error provider responses may never do so.
                empty=False
                if portal['type']=='m3u' and isinstance(exc,ValueError):
                    from m3u_store import entries
                    empty=next(entries(playlist_path(pid),kind,cid),None) is None
                if empty:
                    with db:
                        generation=uuid.uuid4().hex
                        db.execute('INSERT OR REPLACE INTO heads VALUES(?,?,?,?,?)',(pid,kind,cid,generation,time.time()))
                        db.execute('INSERT OR REPLACE INTO catalog VALUES(?,?,?,?)',(pid,kind,generation,time.time()))
                    _sync_note(pid,kind,cid,'READY',dict(received=0,stored=0,discarded=0))
                else: _sync_note(pid,kind,cid,'FAILED',exc=exc)
        # Additive marker only after a usable local import; no account rewrite.
        from portals import update
        if not portal.get('source_schema') and db.execute('SELECT 1 FROM catalog WHERE pid=? AND kind=?',(pid,kind)).fetchone(): update(pid,{'source_schema':1})
    finally:
        with db: db.execute('DELETE FROM sync_leases WHERE pid=? AND kind=? AND owner=?',(pid,kind,owner))
        db.close()

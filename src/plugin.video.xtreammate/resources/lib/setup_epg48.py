"""Promote only a new wizard ID's source proof and rich facts, never old IDs.

The .47 wizard copied plain programmes but omitted source archive + sidecars;
images/cast and source-qualified manual mapping could not survive that Save.
No existing guide schema is migrated and its verified-backup gate is required.
"""
import os
import sqlite3

GUIDE_TABLES=('guide_meta','guide_alias','programmes','guide44_inputs','guide44_ranges','guide44_outcomes')
FACT_TABLES=('facts','fact_versions','source_channels48')


def gate():
    from guide_store import path
    from epg_gate46 import access
    if access(path()) not in ('READY','NOT_CREATED'):
        from setup_draft import SaveError
        raise SaveError('XM-SETUP-EPG-BACKUP')


def promote(draft,cancel):
    from programme_index46 import path as index_path,connect as index_connect
    from programme_store46 import path as meta_path,connect as meta_connect
    if os.path.isfile(index_path(draft.guide)):
        db=index_connect(True)
        try:
            # Additive source-name table; no guide migration/cleanup.
            db.execute('CREATE TABLE IF NOT EXISTS source_channels48(pid TEXT,source_id TEXT,cid TEXT,name TEXT,PRIMARY KEY(pid,source_id,cid))');db.commit()
            draft._copy(index_path(draft.guide),db,FACT_TABLES,cancel)
        finally:db.close()
    if os.path.isfile(meta_path(draft.guide)):
        db=meta_connect(True)
        try:draft._copy(meta_path(draft.guide),db,('metadata',),cancel)
        finally:db.close()


def rollback(draft):
    """Remove unpublished new-ID rows only after an explicitly failed Save."""
    from programme_index46 import path as index_path
    from programme_store46 import path as meta_path
    for filename,tables in ((index_path(),FACT_TABLES),(meta_path(),('metadata',))):
        if not os.path.isfile(filename):continue
        db=sqlite3.connect(filename,timeout=.1)
        try:
            existing={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            with db:
                for table in tables:
                    if table in existing:db.execute('DELETE FROM '+table+' WHERE pid=?',(draft.pid,))
        finally:db.close()


def verify(draft):
    from programme_index46 import path as index_path
    from programme_store46 import path as meta_path
    from setup_draft import SaveError
    from guide_store import path as guide_path
    for original,destination,tables in ((draft.guide,guide_path(),GUIDE_TABLES),(index_path(draft.guide),index_path(),FACT_TABLES),(meta_path(draft.guide),meta_path(),('metadata',))):
        if not os.path.isfile(original):continue
        a=sqlite3.connect(original);b=sqlite3.connect(destination)
        try:
            present={r[0] for r in a.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            for table in tables:
                if table not in present:continue
                columns=a.execute('PRAGMA table_info('+table+')').fetchall()
                order=','.join(r[1] for r in sorted(columns,key=lambda r:r[5]) if r[5])
                # Verify exact new-ID source facts, not just a filled schema.
                for left,right in __import__('itertools').zip_longest(
                    a.execute('SELECT * FROM '+table+' WHERE pid=? ORDER BY '+order,(draft.pid,)),
                    b.execute('SELECT * FROM '+table+' WHERE pid=? ORDER BY '+order,(draft.pid,))):
                    if left!=right:raise SaveError('XM-SETUP-VERIFY')
        finally:a.close();b.close()

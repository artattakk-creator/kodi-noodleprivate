"""Persisted, de-duplicated category work; one service-owned network importer."""
import time
import sqlite3


def request(portal,kind,preferred='',priority=10,force=False):
    from library_index import request_sync
    try: request_sync(portal,kind,preferred,priority,force)
    except (OSError,RuntimeError,sqlite3.Error) as exc:
        from utils import warn
        from artwork_db import classify
        warn('Catalogue request: code='+classify(exc)+' sqlite='+str(getattr(exc,'sqlite_errorcode',0)&255)+' error='+type(exc).__name__)


def run_next(cancel=lambda:False):
    from library_index import connect,sync_kind
    from portals import get_by_id
    from xtream import XtreamClient
    db=connect(write=True)
    try:
        # Claim by delete before work. A crash is restarted by bootstrap and
        # the lease expires; published category heads survive unchanged.
        with db:
            row=db.execute('SELECT * FROM sync_requests ORDER BY priority,requested LIMIT 1').fetchone()
            if not row: return False
            job=dict(row)
            db.execute('DELETE FROM sync_requests WHERE pid=? AND kind=?',(job['pid'],job['kind']))
    finally: db.close()
    portal=get_by_id(job['pid'])
    if not portal or not portal.get('enabled',True) or portal.get('type') not in ('xtream','m3u','stb'): return True
    if portal['type']!='xtream':
        from source_sync import sync_kind as sync_source
        sync_source(portal,job['kind'],bool(job['force']),cancel,job['requested'])
        return True
    client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
    more=sync_kind(portal,client,job['kind'],job['preferred'],bool(job['force']),cancel,
                   max_groups=1,requested_at=job['requested'])
    if more and not cancel():
        db=connect(write=True)
        try:
            with db: db.execute('INSERT OR IGNORE INTO sync_requests VALUES(?,?,?,?,?,?)',
                (job['pid'],job['kind'],job['priority'],job['preferred'],job['force'],job['requested']))
        finally: db.close()
    return True

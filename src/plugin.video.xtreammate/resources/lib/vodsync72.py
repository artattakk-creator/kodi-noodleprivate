"""Explicit existing-portal VOD rescan, sharing the existing writer lock.

All methods are worker-only. A session owns its lock until the last worker has
finished, including cancellation/owner-window destruction. No timer is added.
"""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid

from vodsync_api72 import SyncError, failure, KINDS


def connection(portal):
    return tuple(portal.get(k) for k in ('id', 'type', 'xc_host', 'xc_user', 'xc_pass', 'enabled'))


def emit(session, phase, kind='', count=0, error=None):
    """Fixed fields only: never stringify errors, portal IDs, names or URLs."""
    try:
        import xbmc
        problem = failure(error) if error else None
        message = '[XCMate][VODSYNC] session=' + session.token[:12] + ' portal=' + session.anonymous
        message += ' phase=' + phase + ' kind=' + (kind if kind in KINDS else 'both')
        message += ' count=' + str(max(0, int(count))) + ' ms=' + str(int((time.monotonic()-session.started)*1000))
        if problem: message += ' code=' + problem.code + ' http=' + str(problem.http) + ' errno=' + str(problem.number)
        xbmc.log(message, xbmc.LOGINFO)
    except (ImportError, AttributeError, RuntimeError):
        pass


class Session:
    def __init__(self, portal, kinds=KINDS, filename=None, allowed=KINDS):
        from library_index import connect, path
        from wizard_storage71 import protect
        from wizard_resume53 import private_folder
        from utils import addon_data_dir
        from vodsync_store72 import schema
        self.fd = None; self.closed = False; self.backup = None
        self.portal = dict(portal); self.pid = str(portal['id'])
        self.kinds = tuple(k for k in allowed if k in kinds)
        self.filename = filename or path()
        self.token = uuid.uuid4().hex; self.started = time.monotonic()
        self.anonymous = hashlib.sha256((self.token + self.pid).encode()).hexdigest()[:12]
        # Private journal fingerprint only, never logged or in backup manifests.
        self.account = hashlib.sha256(json.dumps([portal.get(k) for k in ('id', 'type', 'xc_host', 'xc_user')]).encode()).hexdigest()
        self.groups = {}; self.errors = {}; self.results = []
        self.folder = os.path.join(addon_data_dir(), 'vodsync72')
        if not self.kinds: raise SyncError('SCOPE')
        if portal.get('type') != 'xtream': raise SyncError('SOURCE_TYPE')
        from xtream import XtreamClient
        self.client = XtreamClient(portal['xc_host'], portal['xc_user'], portal['xc_pass'])
        try:
            import fcntl
            self.fd = os.open(os.path.join(addon_data_dir(), '.catalog-delta52.lock'),
                              os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
            protect(os.path.join(addon_data_dir(), '.catalog-delta52.lock'), fd=self.fd)
            try: fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError: raise SyncError('BUSY') from None
            private_folder(self.folder)
            db = connect(self.filename, write=True)
            try:
                schema(db); protect(self.filename)
                for suffix in ('-wal', '-shm'):
                    if os.path.exists(self.filename + suffix): protect(self.filename + suffix)
                with db:
                    db.execute('BEGIN IMMEDIATE')
                    for kind in self.kinds:
                        lease = db.execute('SELECT owner,until FROM sync_leases WHERE pid=? AND kind=?', (self.pid, kind)).fetchone()
                        if lease and lease['until'] > time.time(): raise SyncError('BUSY')
                    self.heartbeat(db, acquire=True)
            finally: db.close()
        except BaseException:
            self.close(); raise

    def heartbeat(self, db, acquire=False):
        for kind in self.kinds:
            if acquire:
                db.execute('INSERT OR REPLACE INTO sync_leases VALUES(?,?,?,?)', (self.pid, kind, self.token, time.time()+330))
            else:
                cursor = db.execute('UPDATE sync_leases SET until=? WHERE pid=? AND kind=? AND owner=?', (time.time()+330, self.pid, kind, self.token))
                if cursor.rowcount != 1: raise SyncError('LEASE_LOST')

    def ensure_connection(self):
        from portals import get_by_id
        current = get_by_id(self.pid)
        if not current or connection(current) != connection(self.portal): raise SyncError('CONNECTION_CHANGED')
        return current

    def discover(self, cancel=lambda: False, status=lambda *a: None):
        from vodsync_api72 import authenticate, categories, check_error
        self.ensure_connection(); emit(self, 'AUTH'); status(None, dict(phase='AUTH'))
        user = authenticate(self.client, cancel)
        for kind in self.kinds:
            phase = kind.upper() + '_CATEGORIES'; emit(self, phase); status(None, dict(phase=phase, kind=kind))
            try:
                check_error(user, kind)
                self.groups[kind] = categories(self.client, kind, cancel)
                if not self.groups[kind]: self.errors[kind] = 'SOURCE_EMPTY'
                else: self.errors.pop(kind, None)
                emit(self, phase, kind, len(self.groups[kind]))
            except Exception as exc:
                problem = failure(exc)
                if problem.code == 'CANCELLED': raise problem from None
                self.groups[kind] = []; self.errors[kind] = problem.code; emit(self, 'FAILED', kind, error=problem)
        return self.groups

    def activate(self, kind, cid, cancel):
        """Append verified groups only; preserve every existing selection/flag.

        The COMMITTED receipt and generation are in the same transaction. If
        Kodi dies before this short, serialized activation, retry verifies that
        receipt and completes activation without importing a partial group.
        """
        from profile_transaction import writing
        from group_selection import _read, _state, save, load
        from portals import update, get_by_id
        from library_index import connect
        if cancel(): raise SyncError('CANCELLED')
        with writing():
            self.ensure_connection()
            state = _state(_read(), self.pid, kind)
            db = connect(self.filename)
            try: existing = {r[0] for r in db.execute('SELECT cid FROM groups WHERE pid=? AND kind=?', (self.pid, kind))}
            finally: db.close()
            chosen = (state['enabled'] if state else existing) | {cid}
            known = (state['known'] if state else existing) | {cid}
            save(self.pid, sorted(chosen), kind=kind, known=sorted(known), auto_new=state['auto_new'] if state else False)
            # Only the two requested content flags can change. Credentials,
            # portal identity, Live start group and all unrelated fields stay.
            if get_by_id(self.pid).get('include_' + kind) is not True:
                if not update(self.pid, {'include_' + kind: True}): raise SyncError('ACTIVATION')
            if cid not in load(self.pid, kind) or not get_by_id(self.pid).get('include_' + kind): raise SyncError('ACTIVATION_READBACK')
            # Adjust our in-memory snapshot only for fields we own, not access.
            self.portal['include_' + kind] = True

    def run(self, selected, cancel=lambda: False, status=lambda *a: None):
        from library_index import connect, Reader
        from group_selection import _read
        from profile_transaction import writing
        from vodsync_store72 import backup, verify_backup, upsert
        self.ensure_connection()
        units = [(kind, g) for kind in self.kinds for g in self.groups.get(kind, []) if str(g['category_id']) in set(map(str, selected.get(kind, [])))]
        if not units: raise SyncError('NO_SELECTION')
        if cancel(): raise SyncError('CANCELLED')
        if self.backup: verify_backup(self.backup)
        status(None, dict(phase='BACKUP'))
        with writing():
            active = self.ensure_connection()
            raw = _read().get('_v2', {}).get(self.pid, {})
            snapshot = {kind: dict(state=raw.get(kind), include=active.get('include_' + kind, True)) for kind in self.kinds}
            self.backup = backup(self.pid, self.kinds, self.filename, self.folder, snapshot, cancel)
        verify_backup(self.backup)
        report = dict(state='DONE', groups_found={k: len(self.groups.get(k, [])) for k in self.kinds},
                      groups_selected={k: sum(a == k for a, _ in units) for k in self.kinds},
                      groups_committed=0, errors=[dict(kind=k, code=v) for k, v in self.errors.items()],
                      read=0, new=0, changed=0, unchanged=0, skipped=0, readback={})
        for n, (kind, group) in enumerate(units):
            if cancel(): report['state'] = 'CANCELLED'; break
            status(int(100*n/len(units)), dict(phase=kind.upper() + '_ITEMS', kind=kind, group=n+1, groups=len(units)))
            try:
                counts = upsert(self, kind, group, cancel, status)
                for key in ('read', 'new', 'changed', 'unchanged', 'skipped'): report[key] += counts[key]
                report['groups_committed'] += 1
                emit(self, 'COMMIT', kind, counts.get('stored', 0))
            except Exception as exc:
                problem = failure(exc); emit(self, 'FAILED', kind, error=problem)
                for key in ('read', 'skipped'): report[key] += getattr(problem, 'counts72', {}).get(key, 0)
                report['errors'].append(dict(kind=kind, code=problem.code))
                if problem.code == 'CANCELLED': report['state'] = 'CANCELLED'; break
                if problem.code in ('SPACE', 'READONLY', 'PERMISSION', 'SQLITE', 'LEASE_LOST', 'CONNECTION_CHANGED', 'AUTH', 'FORBIDDEN', 'RATE_LIMIT', 'TIMEOUT', 'NETWORK', 'TLS', 'HTTP', 'ENDPOINT_MISSING'): break
        if report['errors'] and report['state'] == 'DONE': report['state'] = 'PARTIAL' if report['groups_committed'] else 'FAILED'
        for kind in self.kinds:
            report['readback'][kind] = Reader(self.pid, self.filename).page(kind, limit=1)[1]
        # Same revision contract already observed by XCMate media windows and
        # widget_data41. Publish only media frames, no Live or texture reset.
        if report['groups_committed']:
            for kind in self.kinds:
                try:
                    rows, _ = Reader(self.pid, self.filename).rail(kind)
                    if rows:
                        from widget_refresh45 import publish
                        publish(self.portal, kind, rows)
                except (OSError, RuntimeError, ValueError, sqlite3.Error):
                    report['errors'].append(dict(kind=kind, code='WIDGET_DEFERRED'))
        if report['errors'] and report['state'] == 'DONE': report['state'] = 'PARTIAL' if report['groups_committed'] else 'FAILED'
        emit(self, 'READBACK', count=sum(report['readback'].values()))
        status(100, dict(phase='RESULT', **report))
        self.results.append(report)
        return report

    def close(self):
        if self.closed: return
        self.closed = True
        if self.fd is not None:
            try:
                db = sqlite3.connect(self.filename, timeout=.2)
                try:
                    with db: db.execute('DELETE FROM sync_leases WHERE owner=?', (self.token,))
                finally: db.close()
            except sqlite3.Error: pass
            finally: os.close(self.fd); self.fd = None

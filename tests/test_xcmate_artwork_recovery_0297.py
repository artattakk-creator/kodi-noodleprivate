"""Real SQLite corruption/WAL/lock fixtures; no private device database needed."""
import hashlib
import importlib
import json
from pathlib import Path
import sqlite3
import struct
import sys
import time
import threading
import types
import unittest
import zlib
from unittest import mock
from xcmate027_fixture import Fixture


class ArtworkRecoveryTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('artwork_db','art_store'):sys.modules.pop(name,None)
        self.health=importlib.import_module('artwork_db')
        self.store=importlib.import_module('art_store')
        self.path=Path(self.health.path())
        self.warn=mock.Mock();sys.modules['utils'].warn=self.warn

    def seed(self):
        db=self.health.connect()
        with db:
            for n in range(8):
                db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?)',
                           (str(n),'https://private.invalid/SECRET/'+str(n),'PENDING',n,0,0,1,0))
        db.close()

    def break_index(self):
        self.seed()
        db=sqlite3.connect(self.path)
        row=db.execute("SELECT type,name,tbl_name,rootpage,sql FROM sqlite_master WHERE name='art_pending'").fetchone()
        version=db.execute('PRAGMA schema_version').fetchone()[0]
        db.execute('PRAGMA writable_schema=ON')
        db.execute("DELETE FROM sqlite_master WHERE name='art_pending'")
        db.execute('PRAGMA schema_version='+str(version+1));db.commit();db.close()
        db=sqlite3.connect(self.path)
        db.execute("INSERT INTO jobs VALUES('later','PRIVATE','PENDING',1,0,0,1,0)");db.commit()
        db.execute('PRAGMA writable_schema=ON')
        db.execute('INSERT INTO sqlite_master(type,name,tbl_name,rootpage,sql) VALUES(?,?,?,?,?)',row)
        db.execute('PRAGMA schema_version='+str(version+2));db.commit();db.close()

    def break_table(self):
        self.seed()
        db=sqlite3.connect(self.path)
        page=db.execute("SELECT rootpage FROM sqlite_master WHERE name='jobs'").fetchone()[0]
        size=db.execute('PRAGMA page_size').fetchone()[0];db.close()
        with self.path.open('r+b') as stream:
            stream.seek((page-1)*size);stream.write(b'\xff')

    def digest(self):return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def integrity(self,filename=None):
        db=sqlite3.connect(filename or self.path)
        try:return [r[0] for r in db.execute('PRAGMA integrity_check')]
        finally:db.close()

    def test_real_index_only_corruption_repaired_with_immutable_consistent_backup(self):
        self.break_index();self.assertNotEqual(self.integrity(),['ok'])
        db=sqlite3.connect(self.path)
        before=list(db.execute('SELECT * FROM jobs NOT INDEXED ORDER BY rowid'));db.close()
        value=self.health.maintain(force=True)
        self.assertEqual(value['code'],'INDEX_REPAIRED');self.assertEqual(self.integrity(),['ok'])
        db=sqlite3.connect(self.path)
        self.assertEqual(list(db.execute('SELECT * FROM jobs NOT INDEXED ORDER BY rowid')),before);db.close()
        backup=self.folder/'artwork_db_backups'/value['backup']
        self.assertNotEqual(self.integrity(backup),['ok'],'original backup was altered by trial REINDEX')
        self.assertEqual(self.health.maintain()['code'],'INDEX_REPAIRED')
        self.assertEqual(len(list(backup.parent.glob('*.sqlite'))),1)

    def test_table_page_corruption_is_never_automatically_recreated(self):
        self.break_table();before=self.digest()
        result=self.health.maintain(force=True)
        self.assertEqual(result['code'],'RECOVERY_REQUIRED');self.assertEqual(self.digest(),before)
        self.assertEqual(self.health.rebuild()['code'],'CONFIRMATION_REQUIRED')
        self.assertEqual(self.digest(),before)
        self.assertTrue((self.folder/'artwork_db_backups'/result['backup']).is_file())

    def test_confirmed_rebuild_adopts_real_images_and_preserves_unrelated_profile_bytes(self):
        self.break_table()
        def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',8,8,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\x10\x20\x30'*8)*8))+chunk(b'IEND',b'')
        images=self.folder/'media_art_v1';images.mkdir();image=images/('a'*64+'.img');image.write_bytes(png)
        bad=images/('b'*64+'.img');bad.write_bytes(b'bad image')
        protected={}
        for name in ('portals.json','favourites.json','guide.sqlite','resume.json'):
            p=self.folder/name;p.write_bytes(b'PRIVATE-BYTES-'+name.encode());protected[p]=p.read_bytes()
        result=self.health.rebuild(confirmed=True)
        self.assertEqual(result['code'],'QUEUE_REBUILT');self.assertEqual(self.integrity(),['ok'])
        self.assertTrue(result['background_paused'])
        self.assertEqual(image.read_bytes(),png);self.assertEqual(bad.read_bytes(),b'bad image')
        self.assertEqual({p:p.read_bytes() for p in protected},protected)
        db=self.health.connect()
        try:
            jobs=list(db.execute('SELECT * FROM jobs'))
            self.assertEqual(len(jobs),1);self.assertEqual(jobs[0]['ident'],'a'*64)
            self.assertEqual(jobs[0]['url'],'');self.assertEqual(jobs[0]['status'],'READY')
        finally:db.close()
        # A queue rebuild must not restart a background sweep of the catalogue.
        with mock.patch.object(self.index,'Reader',side_effect=AssertionError('unexpected catalogue sweep')):
            self.store.prefetch_selected()
        self.store.retry();self.assertFalse(self.health.diagnostic()['background_paused'])

    def test_healthy_database_is_not_rebuilt_even_with_confirmation(self):
        self.seed();before=self.digest()
        self.assertEqual(self.health.rebuild(confirmed=True)['code'],'OK')
        self.assertEqual(self.digest(),before)

    def test_failed_backup_space_check_never_changes_source(self):
        self.break_index();before=self.digest()
        with mock.patch('import_budget.check_space',side_effect=OSError(28,'SECRET disk')):
            result=self.health.maintain(force=True)
        self.assertEqual(result['code'],'SPACE_FULL');self.assertEqual(result['phase'],'BACKUP')
        self.assertEqual(self.digest(),before);self.assertNotIn('SECRET',json.dumps(result))

    def test_cancellation_before_backup_completion_retains_corrupt_source(self):
        self.break_index();before=self.digest()
        result=self.health.maintain(force=True,cancel=lambda:True)
        self.assertEqual(result['code'],'CANCELLED');self.assertEqual(self.digest(),before)
        self.assertFalse(list((self.folder/'artwork_db_backups').glob('*.sqlite')))

    def test_online_backup_contains_committed_wal_rows(self):
        self.seed();keeper=sqlite3.connect(self.path)
        self.addCleanup(keeper.close)
        self.assertEqual(keeper.execute('PRAGMA journal_mode=WAL').fetchone()[0],'wal')
        keeper.execute("INSERT INTO jobs VALUES('wal','PRIVATE','PENDING',1,0,0,1,0)");keeper.commit()
        self.assertTrue(Path(str(self.path)+'-wal').exists())
        result=self.health.maintain(force=True)
        self.assertEqual(result['code'],'OK')
        backup=sqlite3.connect(self.folder/'artwork_db_backups'/result['backup'])
        try:self.assertEqual(backup.execute("SELECT count(*) FROM jobs WHERE ident='wal'").fetchone()[0],1)
        finally:backup.close()

    def test_active_xcmate_connection_prevents_maintenance_and_recovery(self):
        self.seed();db=self.health.connect()
        try:
            before=self.digest()
            self.assertEqual(self.health.maintain(force=True)['code'],'BUSY')
            self.assertEqual(self.health.rebuild(confirmed=True)['code'],'BUSY')
            self.assertEqual(self.digest(),before)
        finally:db.close()

    def test_incompatible_schema_is_reported_and_never_automatically_dropped(self):
        db=sqlite3.connect(self.path);db.execute('CREATE TABLE jobs(ident TEXT,url TEXT)')
        db.execute("INSERT INTO jobs VALUES('old','PRIVATE')");db.commit();db.close()
        before=self.digest();result=self.health.maintain(force=True)
        self.assertEqual(result['code'],'SCHEMA_ERROR');self.assertEqual(self.digest(),before)
        self.assertEqual(self.health.rebuild()['code'],'CONFIRMATION_REQUIRED')

    def test_wal_sidecars_held_by_legacy_reader_block_atomic_queue_replacement(self):
        self.break_table();keeper=sqlite3.connect(self.path);self.addCleanup(keeper.close)
        keeper.execute('PRAGMA journal_mode=WAL')
        keeper.execute('UPDATE worker SET until=17');keeper.commit()
        inode=self.path.stat().st_ino
        result=self.health.rebuild(confirmed=True)
        self.assertEqual(result['code'],'BUSY');self.assertEqual(self.path.stat().st_ino,inode)
        self.assertTrue(Path(str(self.path)+'-wal').exists())

    def test_unsupported_file_lock_leaves_normal_queue_access_available(self):
        self.seed()
        with mock.patch.object(self.health,'fcntl',None):
            self.assertEqual(self.health.maintain(force=True)['code'],'LOCK_UNSUPPORTED')
            self.assertEqual(self.health.rebuild(confirmed=True)['code'],'LOCK_UNSUPPORTED')
            self.health.connect().close()

    def test_readonly_diagnostic_remains_accurate_when_state_file_cannot_be_written(self):
        self.seed()
        with mock.patch.object(self.health,'_lock',side_effect=PermissionError(13,'PRIVATE')),\
             mock.patch.object(self.health,'_save',return_value=None):
            result=self.health.maintain(force=True)
        self.assertEqual(result['code'],'READONLY');self.assertEqual(result['phase'],'LOCK')

    def test_diagnostic_progress_ui_never_runs_inside_the_database_worker(self):
        ui=importlib.import_module('artwork_health_ui');owner=threading.get_ident();calls=[]
        def gui_call(*args):
            calls.append(threading.get_ident());self.assertEqual(threading.get_ident(),owner)
        progress=types.SimpleNamespace(create=gui_call,close=gui_call,iscanceled=lambda:False)
        def job(cancel):
            self.assertNotEqual(threading.get_ident(),owner);return dict(code='OK')
        with mock.patch.object(ui.xbmcgui,'DialogProgress',return_value=progress,create=True),\
             mock.patch.object(ui.xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=lambda seconds:False),create=True):
            self.assertEqual(ui._work(job)['code'],'OK')
        self.assertEqual(set(calls),{owner})

    def test_sqlite_writer_busy_is_classified_and_retries_are_bounded_across_reload(self):
        self.seed();writer=sqlite3.connect(self.path);writer.execute('BEGIN IMMEDIATE')
        self.health._initialized.clear()
        try:
            with self.assertRaises(sqlite3.OperationalError):self.health.connect()
            self.assertEqual(self.health.diagnostic()['code'],'BUSY')
            for _ in range(10):
                with self.assertRaises(self.health.ArtworkDBUnavailable):self.health.connect()
            self.health=importlib.reload(self.health)
            with self.assertRaises(self.health.ArtworkDBUnavailable):self.health.connect()
            self.assertEqual(self.warn.call_count,1)
        finally:writer.rollback();writer.close()
        self.health.reset_retry();self.health.connect().close()

    def test_readonly_and_schema_diagnostics_never_include_private_exception_text(self):
        self.seed();before=self.digest()
        with mock.patch.object(self.health,'_lock',side_effect=PermissionError(13,'SECRET /private/path')):
            with self.assertRaises(PermissionError):self.health.connect()
        self.assertEqual(self.health.diagnostic()['code'],'READONLY');self.assertEqual(self.digest(),before)
        self.assertNotIn('SECRET',str(self.warn.call_args));self.assertNotIn('/private/path',json.dumps(self.health.diagnostic()))
        self.health.reset_retry();db=self.health.connect()
        try:
            with self.assertRaises(sqlite3.OperationalError):db.execute('SELECT PRIVATE_SECRET_COLUMN FROM jobs')
        finally:db.close()
        self.assertEqual(self.health.diagnostic()['code'],'SCHEMA_ERROR')
        self.assertNotIn('PRIVATE_SECRET_COLUMN',str(self.warn.call_args))

    def test_atomic_schema_failure_rolls_back_and_preserves_jobs(self):
        db=sqlite3.connect(self.path)
        db.executescript("CREATE TABLE jobs(ident TEXT PRIMARY KEY,url TEXT,status TEXT,priority INTEGER,attempts INTEGER,next_at REAL,updated REAL,bytes INTEGER); CREATE TABLE worker(id INTEGER PRIMARY KEY,until REAL);INSERT INTO worker VALUES(1,0);")
        db.execute("INSERT INTO jobs VALUES('old','PRIVATE','READY',0,0,0,0,123)");db.commit();db.close()
        execute=self.health._Connection.execute
        def fail(connection,sql,parameters=()):
            if sql.startswith('ALTER TABLE'):raise sqlite3.OperationalError('SECRET migration')
            return execute(connection,sql,parameters)
        with mock.patch.object(self.health._Connection,'execute',fail):
            with self.assertRaises(sqlite3.OperationalError):self.health.connect()
        db=sqlite3.connect(self.path)
        self.assertEqual(db.execute('SELECT bytes FROM jobs').fetchone()[0],123)
        self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='scan'").fetchone());db.close()
        self.health.reset_retry();db=self.health.connect()
        self.assertIn('owner',{r[1] for r in db.execute('PRAGMA table_info(worker)')});db.close()


class StartRouteTests(Fixture,unittest.TestCase):
    def test_valid_home_start_finishes_success_before_unchanged_direct_player(self):
        self.router._params['action']='home_start'
        def play():
            self.assertEqual(self.ends,[((7,True),{'cacheToDisc':False})])
        self.router._play_start_direct=mock.Mock(side_effect=play)
        self.routes.dispatch(self.router)
        self.router._play_start_direct.assert_called_once();self.assertEqual(self.builtins,[])

    def test_missing_start_channel_keeps_failure_and_never_plays(self):
        self.portal['start_stream_id']='missing';self.router._params['action']='home_start'
        self.router._play_start_direct=mock.Mock()
        self.routes.dispatch(self.router)
        self.assertEqual(self.ends[-1][0],(7,False));self.router._play_start_direct.assert_not_called()

    def test_runplugin_handle_does_not_complete_a_nonexistent_directory(self):
        self.router._handle=-1;self.router._params['action']='home_start'
        self.router._play_start_direct=mock.Mock()
        self.routes.dispatch(self.router)
        self.assertFalse(self.ends);self.router._play_start_direct.assert_called_once()


if __name__=='__main__':unittest.main()

"""Read-only status under real SQLite contention; no private device data."""
import ast,hashlib,importlib,sqlite3,sys,time,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,LIB

class ArtStatusTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('artwork_db','art_store','artwork_health_ui'):sys.modules.pop(name,None)
        self.health=importlib.import_module('artwork_db');self.store=importlib.import_module('art_store')
        self.dbpath=Path(self.health.path());db=self.health.connect()
        with db:db.execute("INSERT INTO jobs VALUES('a','PRIVATE','READY',0,0,0,1,123)")
        db.close()

    def test_ten_status_reads_under_exclusive_lock_keep_partial_budget_and_return_bounded(self):
        writer=sqlite3.connect(self.dbpath);writer.execute('BEGIN EXCLUSIVE')
        before=self.dbpath.read_bytes();start=time.monotonic()
        try:
            for _ in range(10):
                value=self.store.status();self.assertEqual(value['code'],'BUSY')
                self.assertEqual(value['budget'],0);self.assertIsNone(value['counts'])
                self.assertIn('free',value)
        finally:writer.rollback();writer.close()
        self.assertLess(time.monotonic()-start,1.5);self.assertEqual(self.dbpath.read_bytes(),before)

    def test_reserved_writer_does_not_block_readonly_statistics_and_no_adoption(self):
        writer=sqlite3.connect(self.dbpath);writer.execute('BEGIN IMMEDIATE')
        images=self.folder/'media_art_v1';images.mkdir();(images/('b'*64+'.img')).write_bytes(b'old image')
        try:
            with mock.patch.object(self.store,'connect',side_effect=AssertionError('status writer')),mock.patch.object(self.store,'used',side_effect=AssertionError('status adoption')):
                value=self.store.status()
            self.assertEqual(value['counts'],{'READY':1});self.assertEqual(value['bytes'],123)
        finally:writer.rollback();writer.close()
        db=self.health.connect();self.assertEqual(db.execute('SELECT count(*) FROM jobs').fetchone()[0],1);db.close()

    def test_empty_worker_never_requests_immediate_writer_lock(self):
        db=self.health.connect()
        with db:db.execute('DELETE FROM jobs')
        db.close();writer=sqlite3.connect(self.dbpath);writer.execute('BEGIN IMMEDIATE')
        try:self.assertFalse(self.store.run_one())
        finally:writer.rollback();writer.close()

    def test_complete_schema_can_open_under_another_reserved_writer(self):
        self.health._initialized.clear();writer=sqlite3.connect(self.dbpath);writer.execute('BEGIN IMMEDIATE')
        try:self.health.connect().close()
        finally:writer.rollback();writer.close()

    def test_busy_warns_once_per_minute_across_interpreter_reload_preserving_integrity(self):
        self.health._healthy('OK');warn=mock.Mock();sys.modules['utils'].warn=warn
        for _ in range(6):
            self.health._failure(sqlite3.OperationalError('database is locked PRIVATE'),'QUERY')
            self.health=importlib.reload(self.health)
        self.assertEqual(warn.call_count,1);self.assertEqual(self.health.diagnostic()['integrity_code'],'OK')
        self.assertNotIn('PRIVATE',str(warn.call_args))

    def test_snapshot_does_not_create_missing_database_or_adopt_any_file(self):
        self.dbpath.unlink();self.assertEqual(self.health.snapshot()['code'],'NOT_CREATED');self.assertFalse(self.dbpath.exists())

    def test_status_route_opens_textviewer_with_busy_message_and_completes_once(self):
        ui=importlib.import_module('artwork_health_ui');self.router._params['action']='art_status'
        with mock.patch.object(ui,'_work',side_effect=lambda job:job(lambda:False)),mock.patch.object(self.health,'snapshot',return_value=dict(code='BUSY',counts=None,bytes=None)):
            self.routes.dispatch(self.router)
        self.dialog.textviewer.assert_called_once();self.assertIn('belegt',self.dialog.textviewer.call_args.args[1])
        self.assertEqual(len(self.ends),1)

    def test_failure_classes_are_whitelisted_without_private_exception_message(self):
        diag=importlib.import_module('boot_diagnostics');sys.modules['xbmc'].log=log=mock.Mock();sys.modules['xbmc'].LOGINFO=1
        for name in ('ArtworkDBUnavailable','OperationalError','DatabaseError'):diag.mark('ART_STATUS_COUNTS_FAILED',error=name)
        self.assertNotIn('OTHER',str(log.call_args_list))

    def test_legacy_native_settings_finishes_directory_before_open(self):
        tree=ast.parse((LIB/'main.py').read_text());fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_open_settings')
        calls=[];ns={'ADDON':types.SimpleNamespace(openSettings=lambda:calls.append('open'))}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'settings','exec'),ns)
        ns['_open_settings'](types.SimpleNamespace(_end_directory=lambda **kw:calls.append(kw)))
        self.assertEqual(calls,[dict(succeeded=True,cacheToDisc=False),'open'])

    def test_read_cancel_and_corrupt_error_do_not_trigger_any_repair(self):
        with mock.patch.object(self.health,'maintain',side_effect=AssertionError('repair')):
            self.assertEqual(self.health.snapshot(lambda:True)['code'],'CANCELLED')
            self.dbpath.write_bytes(b'not a database')
            value=self.store.status();self.assertEqual(value['code'],'CORRUPT');self.assertIn('budget',value)
            self.assertEqual(self.dbpath.read_bytes(),b'not a database')

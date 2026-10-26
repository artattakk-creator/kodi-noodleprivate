"""Real lock/missing/schema fixtures; no automatic DB repair or reset."""
import importlib,sqlite3,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_artwork_02920 as model

class SQLite38(unittest.TestCase):
    def setUp(self):
        self.m=model.Artwork20Tests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.db=importlib.import_module('artwork_db')

    def test_missing_job_database_is_unknown_without_creating_one(self):
        path=Path(self.db.path());self.assertFalse(path.exists());value=self.db.snapshot()
        self.assertEqual(value['code'],'NOT_CREATED');self.assertFalse(path.exists())

    def test_schema_error_is_not_claimed_as_zero_images_or_automatically_repaired(self):
        path=Path(self.db.path());conn=sqlite3.connect(path);conn.execute('CREATE TABLE unrelated(value)');conn.commit();conn.close();before=path.read_bytes()
        result=self.db.snapshot();self.assertEqual(result['code'],'SCHEMA_ERROR');self.assertIsNone(result['counts']);self.assertEqual(path.read_bytes(),before)

    def test_actual_exclusive_sqlite_lock_reports_busy_and_preserves_ready(self):
        conn=self.m.store.connect();conn.execute('PRAGMA journal_mode=DELETE');conn.execute('BEGIN EXCLUSIVE')
        try:
            value=self.db.snapshot();self.assertEqual(value['code'],'BUSY');self.assertIsNone(value['counts'])
        finally:conn.rollback();conn.close()
        self.assertEqual(self.db.snapshot()['code'],'OK')

    def test_query_budget_interrupt_distinguished_from_corruption_and_busy(self):
        self.assertEqual(self.db.classify(sqlite3.OperationalError('interrupted')),'QUERY_TIMEOUT')
        self.assertEqual(self.db.classify(sqlite3.OperationalError('database is locked')),'BUSY')
        self.assertEqual(self.db.classify(sqlite3.OperationalError('database disk image is malformed')),'CORRUPT')

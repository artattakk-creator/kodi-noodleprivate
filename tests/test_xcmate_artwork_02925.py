"""Real rollback/WAL locks, one coherent read and private failure reporting."""
import hashlib
import importlib
import sqlite3
import threading
import time
import unittest
import io
import sys
from unittest import mock

import test_xcmate_artwork_02920 as old
from xcmate027_fixture import Fixture


class Artwork25Tests(Fixture,unittest.TestCase):
    seed=old.Artwork20Tests.seed
    row=old.Artwork20Tests.row

    def setUp(self):
        super().setUp()
        for name in ('artwork_db','art_store','art_storage'):sys.modules.pop(name,None)
        self.health=importlib.import_module('artwork_db');self.store=importlib.import_module('art_store')
        self.art=importlib.reload(importlib.import_module('media_art'))
        patch=mock.patch.object(self.art,'request');patch.start();self.addCleanup(patch.stop)
        from PIL import Image
        output=io.BytesIO();Image.new('RGB',(108,162)).save(output,format='PNG')
        self.http=sys.modules['utils'].http_get;self.http.side_effect=None;self.http.return_value=(output.getvalue(),{})

    def test_short_exclusive_lock_recovers_without_enrolment_or_http(self):
        url='https://private.invalid/TOKEN';self.seed([url],status='PENDING',attempts=1)
        db=sqlite3.connect(self.health.path(),check_same_thread=False)
        db.execute('BEGIN EXCLUSIVE')
        release=threading.Event()
        def unlock():
            release.wait(.055);db.rollback()
        worker=threading.Thread(target=unlock);worker.start()
        try:
            values,code=self.health.image_snapshot([self.store.key(url)])
            self.assertEqual(code,'OK');self.assertEqual(values[self.store.key(url)]['attempts'],1)
        finally:release.set();worker.join();db.close()
        self.http.assert_not_called();self.assertEqual(self.row(url)['status'],'PENDING')

    def test_persistent_lock_has_finite_retry_and_busy_overrides_stale_inbox_error(self):
        url='https://private.invalid/TOKEN';self.seed([url],status='TIMEOUT')
        self.art._inbox[url]=(0,1,0,0);self.art._enqueue_code='NETWORK_ERROR'
        db=sqlite3.connect(self.health.path());db.execute('BEGIN EXCLUSIVE')
        before=time.monotonic()
        try:
            report=self.art.poster_report(dict(cover=url))
            self.assertEqual(report['status'],'DB_BUSY');self.assertEqual(report['database'],'DB_BUSY')
            self.assertNotIn('TOKEN',str(report));self.assertLess(time.monotonic()-before,.7)
        finally:db.rollback();db.close()
        self.assertEqual(self.row(url)['status'],'TIMEOUT');self.http.assert_not_called()

    def test_committed_wal_read_works_during_writer_and_preserves_journal_mode(self):
        url='https://private.invalid/TOKEN';self.seed([url],status='DNS_ERROR',attempts=2)
        db=sqlite3.connect(self.health.path())
        self.assertEqual(db.execute('PRAGMA journal_mode=WAL').fetchone()[0],'wal')
        db.execute('BEGIN IMMEDIATE');db.execute("UPDATE jobs SET status='READY'")
        try:
            report=self.art.poster_report(dict(cover=url))
            self.assertEqual(report['status'],'DNS_ERROR');self.assertEqual(report['attempts'],2)
            self.assertEqual(db.execute('PRAGMA journal_mode').fetchone()[0],'wal')
        finally:db.rollback();db.close()
        self.assertEqual(self.row(url)['status'],'DNS_ERROR')

    def test_report_reads_status_and_counters_in_one_query_without_urls(self):
        url='https://private.invalid/TOKEN';self.seed([url],status='HTTP_NOT_FOUND',attempts=2)
        original=self.health.sqlite3.connect
        with mock.patch.object(self.health.sqlite3,'connect',wraps=original) as connect:
            report=self.art.poster_report(dict(cover=url))
        self.assertEqual(connect.call_count,1);self.assertEqual(report['attempts'],2)
        self.assertEqual(report['status'],'HTTP_NOT_FOUND');self.assertNotIn('TOKEN',str(report))
        self.assertNotIn('url',str(report).lower())

    def test_busy_lookup_keeps_ready_file_bytes_and_reports_local_ready(self):
        url='https://private.invalid/TOKEN';filename=self.art.fetch(url)
        from pathlib import Path
        before=hashlib.sha256(Path(filename).read_bytes()).hexdigest()
        with mock.patch.object(self.health,'image_snapshot',return_value=({},'DB_BUSY')):
            self.assertEqual(self.art.diagnose(dict(cover=url))['poster'],'READY')
        self.assertEqual(hashlib.sha256(Path(filename).read_bytes()).hexdigest(),before)
        self.assertEqual(self.row(url)['status'],'READY')

    def test_cancelled_snapshot_does_not_create_database_or_files(self):
        before=set(self.folder.rglob('*'))
        self.assertEqual(self.health.image_snapshot(['0'*64],cancel=lambda:True),({},'CANCELLED'))
        self.assertEqual(set(self.folder.rglob('*')),before)

    def test_initial_writer_query_recovers_short_lock_without_busy_health_poison(self):
        url='https://private.invalid/TOKEN';self.seed([url],status='PENDING',attempts=1)
        own=self.store.connect();external=sqlite3.connect(self.health.path(),check_same_thread=False)
        external.execute('BEGIN EXCLUSIVE');release=threading.Event()
        def unlock():release.wait(.065);external.rollback()
        worker=threading.Thread(target=unlock);worker.start()
        try:
            with own:own.execute('UPDATE jobs SET priority=-10 WHERE ident=?',(self.store.key(url),))
        finally:release.set();worker.join();external.close();own.close()
        self.assertNotEqual(self.health.diagnostic().get('code'),'BUSY')
        self.assertEqual(self.row(url)['priority'],-10)
        self.assertEqual(self.row(url)['attempts'],1);self.http.assert_not_called()


if __name__=='__main__':unittest.main()

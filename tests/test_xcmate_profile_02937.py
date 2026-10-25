"""SAFE-01/02/03/06/07: cloned profiles only, no Android acceptance."""
import hashlib
import importlib
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
from unittest import mock
from xcmate027_fixture import LIB


class Profile37(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0,str(LIB));self.addCleanup(lambda:sys.path.remove(str(LIB)))
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        patch=mock.patch.dict(sys.modules,{'utils':types.SimpleNamespace(addon_data_dir=lambda:str(self.root))});patch.start();self.addCleanup(patch.stop)
        self.config=importlib.import_module('artwork_config')

    def test_missing_marker_is_internal_until_positive_fresh_preflight(self):
        self.assertEqual(self.config.read()['mode'],'internal')
        self.assertEqual(list(self.root.iterdir()),[])
        self.assertEqual(self.config.initialize()['mode'],'dynamic')
        self.assertEqual(self.config.initialize(),self.config.read())

    def test_existing_empty_art_or_logo_directory_is_legacy(self):
        for name in ('media_art_v1','tv_logos'):
            with self.subTest(name=name):
                (self.root/name).mkdir()
                self.assertEqual(self.config.initialize()['mode'],'internal')
                self.assertTrue((self.root/name).is_dir())

    def test_existing_portal_settings_or_database_never_means_fresh(self):
        for name in ('portals.json','settings.xml','media_art_jobs_v1.sqlite','library_v1.sqlite','media_state_v1.sqlite','guide_v1.sqlite'):
            temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
            self.root=Path(temp.name);(self.root/name).write_bytes(b'original-fixture')
            before=hashlib.sha256((self.root/name).read_bytes()).hexdigest()
            self.assertEqual(self.config.initialize()['mode'],'internal')
            self.assertEqual(hashlib.sha256((self.root/name).read_bytes()).hexdigest(),before)

    def test_zero_ready_legacy_job_queue_is_preserved_byte_for_byte(self):
        import sqlite3
        path=self.root/'media_art_jobs_v1.sqlite';db=sqlite3.connect(path)
        db.execute('CREATE TABLE jobs(status TEXT)');db.executemany('INSERT INTO jobs VALUES(?)',[('DISK_FULL',)]*97+[('PENDING',)]*21+[('RUNNING',)])
        db.commit();db.close();original=path.read_bytes()
        self.assertEqual(self.config.initialize()['mode'],'internal');self.assertEqual(path.read_bytes(),original)
        self.config.choose('dynamic');self.assertEqual(path.read_bytes(),original)
        self.assertEqual(self.config.initialize()['mode'],'dynamic')

    def test_explicit_mode_and_strategy_survive_repeated_initialize(self):
        self.config.initialize();self.config.choose('internal',strategy='all')
        before=self.config.read()
        for _ in range(5):self.assertEqual(self.config.initialize(),before)
        self.assertEqual(before['strategy'],'all')

    def test_two_profiles_have_independent_modes_and_namespaces(self):
        first=self.config.initialize();a=self.root
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        second=self.config.initialize();self.config.choose('internal')
        self.assertNotEqual(first['profile'],second['profile'])
        self.root=a;self.assertEqual(self.config.read()['mode'],'dynamic')

    def test_torn_config_is_conservative_and_never_erases_images(self):
        (self.root/self.config.NAME).write_text('{broken')
        folder=self.root/'media_art_v1';folder.mkdir();image=folder/('a'*64+'.img');image.write_bytes(b'keep')
        self.assertEqual(self.config.initialize()['mode'],'internal');self.assertEqual(image.read_bytes(),b'keep')

    def test_failed_atomic_commit_keeps_existing_choice_and_retry_is_idempotent(self):
        self.config.initialize();before=(self.root/self.config.NAME).read_bytes()
        with mock.patch.object(self.config.os,'replace',side_effect=OSError('WRITE_FAILED')):
            with self.assertRaises(OSError):self.config.choose('internal')
        self.assertEqual((self.root/self.config.NAME).read_bytes(),before)
        self.assertEqual(self.config.initialize()['mode'],'dynamic')

    def test_concurrent_fresh_entry_service_preflight_produces_one_marker(self):
        rows=[]
        workers=[threading.Thread(target=lambda:rows.append(self.config.initialize())) for _ in range(4)]
        for worker in workers:worker.start()
        for worker in workers:worker.join(2)
        self.assertEqual(len(rows),4);self.assertTrue(all(row==rows[0] for row in rows))
        self.assertEqual(rows[0]['mode'],'dynamic')

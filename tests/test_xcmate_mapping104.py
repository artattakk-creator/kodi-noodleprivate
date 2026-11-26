"""Issue 519 regressions using real SQLite station queries and mapping workers."""
from concurrent.futures import Future
from contextlib import closing
import os
import sqlite3
import sys
import time
import unittest
from unittest import mock

from xcmate027_fixture import Fixture, LIB
import test_xcmate_mini_mapping_02996 as mini

sys.path.insert(0, str(LIB))


class StationSearch104(Fixture, unittest.TestCase):
    def catalogue(self, stations):
        from epg_agent100 import _save, profile
        from epg_agent_catalog103 import INDEX
        from epg_agent_github import XMLTV_FILE
        from mapping_search482 import normal

        generation = 'a' * 64
        folder = profile() / ('candidate-' + generation)
        folder.mkdir(parents=True)
        (folder / XMLTV_FILE).touch()
        (folder / 'manifest.json').write_text('{}')
        _save(profile(), dict(code='READY', generation=generation))
        with closing(sqlite3.connect(folder / INDEX)) as db, db:
            db.executescript('''CREATE TABLE channels(cid TEXT PRIMARY KEY, name TEXT NOT NULL,
                name_key TEXT NOT NULL, id_key TEXT NOT NULL, first INTEGER, last INTEGER,
                cid_fold TEXT NOT NULL) WITHOUT ROWID;
                CREATE INDEX channel_name ON channels(name_key,cid);
                CREATE INDEX channel_cid_fold ON channels(cid_fold,cid);
                CREATE TABLE channel_grams(gram TEXT,cid TEXT,PRIMARY KEY(gram,cid)) WITHOUT ROWID;
                CREATE TABLE channel_aliases(cid TEXT,name TEXT,name_key TEXT,PRIMARY KEY(cid,name)) WITHOUT ROWID;
                CREATE INDEX channel_alias_key ON channel_aliases(name_key,cid);''')
            for cid, name, first, last in stations:
                keys = normal(name), normal(cid)
                db.execute('INSERT INTO channels VALUES(?,?,?,?,?,?,?)',
                           (cid, name, *keys, first, last, cid.casefold()))
                grams = {key[pos:pos+3] for key in keys for pos in range(len(key)-2)}
                db.executemany('INSERT INTO channel_grams VALUES(?,?)',
                               [(gram, cid) for gram in sorted(grams)])
        return folder

    def test_sixx_search_visits_only_selective_index_entries_with_twenty_thousand_channels(self):
        from mapping_search482 import search

        self.catalogue([('s1.sixx.de', 'sixx', 10, 100), ('s4.SIXX.at', 'SIXX', 10, 100)] +
                       [(f'other-{n:05d}', f'Unrelated {n:05d}', 10, 100) for n in range(19998)])
        def measure(db, cancel):
            # Permit at most 10,000 SQLite VM steps independently of CPU load.
            # A .103 scan uses about 200,000 steps on this same catalogue.
            visits = iter(range(100))
            db.set_progress_handler(lambda: int(cancel() or next(visits, None) is None), 100)
        with mock.patch('mapping_search482._deadline', side_effect=measure):
            rows = search('p', 'agent', 'DE| SIXX HEVC')
        self.assertEqual([row['id'] for row in rows], ['s1.sixx.de', 's4.SIXX.at'])

    def test_dmax_keeps_explicit_id_and_offers_scheduled_de_before_empty_export_alias(self):
        from mapping_search482 import search

        self.catalogue([('s1.DMAX.de', 'DMAX', 10, 100), ('s4.DMAX.at', 'DMAX', 10, 100),
                        ('s0.DMax.de', 'DE| DMAX HEVC', None, None),
                        ('s6.DMAX+1.de', 'DMAX +1', 10, 100)])
        self.assertEqual([row['id'] for row in search('p', 'agent', 'DE| DMAX HEVC')],
                         ['s1.DMAX.de', 's4.DMAX.at', 's0.DMax.de'])
        self.assertEqual(search('p', 'agent', 'S0.DMAX.DE')[0]['id'], 's0.DMax.de')
        self.assertEqual([row['id'] for row in search('p', 'agent', 'MAX')],
                         ['s0.DMax.de', 's1.DMAX.de', 's4.DMAX.at', 's6.DMAX+1.de'])

    def test_display_name_alias_is_searchable_without_changing_channel_id(self):
        from epg_agent_catalog103 import INDEX
        from mapping_search482 import search

        folder = self.catalogue([('s1.sixx.de', 'sixx', 10, 100)])
        with closing(sqlite3.connect(folder / INDEX)) as db, db:
            db.execute("INSERT INTO channel_aliases VALUES('s1.sixx.de','Six Television','sixtelevision')")
            db.execute("INSERT INTO channel_grams VALUES('tel','s1.sixx.de')")
        for query in ('Six Television', 'Television'):
            with self.subTest(query=query):
                self.assertEqual([row['id'] for row in search('p', 'agent', query)], ['s1.sixx.de'])

    def test_exact_name_and_fragments_share_pagination_without_duplicate_ids(self):
        from mapping_search482 import search

        self.catalogue([(f'A{n:03d}', 'sixx', 10, 100) for n in range(106)] +
                       [('s1.sixx.de', 'sixx', 10, 100), ('z-sixx-info', 'SIXX Info', 10, 100)])
        first = search('p', 'agent', 'DE| SIXX HEVC')
        second = search('p', 'agent', 'DE| SIXX HEVC', 100)
        self.assertEqual([row['id'] for row in first], ['s1.sixx.de'] + [f'A{n:03d}' for n in range(99)])
        self.assertEqual([row['id'] for row in second], [f'A{n:03d}' for n in range(99, 106)] +
                         ['z-sixx-info'])
        self.assertEqual(search('p', 'agent', 'DE| SIXX HEVC', 200), [])


class Identity104(unittest.TestCase):
    def test_codec_qualified_dmax_id_cannot_be_confused_with_at_or_shifted_id(self):
        from epg_agent100_import import match

        stations = {'s1.DMAX.de': 'DMAX', 's4.DMAX.at': 'DMAX', 's5.DMax.de': 'DE| DMAX HEVC',
                    's8.DMAX+1.de': 'DMAX +1'}
        rows = [dict(sid='de', name='DMAX HEVC', epg_channel_id='DMax.de.HEVC'),
                dict(sid='at', name='DMAX HD', epg_channel_id='DMAX.at@HD'),
                dict(sid='shift', name='DMAX +1 FHD', epg_channel_id='DMAX+1.de'),
                dict(sid='unknown', name='DMAX HEVC')]
        selected, proofs, ambiguous, unmatched = match(stations, rows, {}, available={'s1.DMAX.de',
                                                  's4.DMAX.at', 's8.DMAX+1.de'}, evidence=True)
        self.assertEqual(selected, {'de': 's1.DMAX.de', 'at': 's4.DMAX.at', 'shift': 's8.DMAX+1.de'})
        self.assertEqual(set(proofs), {'de', 'at', 'shift'})
        self.assertEqual((ambiguous, unmatched), (1, 0))


class MappingErrors104(unittest.TestCase):
    def setUp(self):
        owner = mini.MiniMapping96(methodName='runTest')
        owner.setUp()
        self.addCleanup(owner.doCleanups)
        self.dialog = owner.dialog
        self.fixture = owner.fixture

    def test_local_agent_worker_deadline_reports_read_timeout(self):
        self.dialog.source = {'id': 'agent', 'name': 'EPG-Agent'}
        self.dialog._job_started482 = time.monotonic() - 13
        self.dialog.future = Future()
        self.dialog.pump()
        self.assertIn('(EPG_READ_TIMEOUT)', self.dialog.getControl(103).text)
        self.assertFalse(self.dialog.getControl(405).enabled)

    def test_sqlite_save_timeout_preserves_the_previous_binding(self):
        self.dialog._preview()
        before = self.fixture.sources._load_all()
        error = sqlite3.OperationalError('private sqlite context')
        error.sqlite_errorname = 'SQLITE_INTERRUPT'
        with mock.patch.object(self.fixture.sources, '_write_all', side_effect=error):
            self.dialog.onClick(405)
        self.assertEqual(self.fixture.sources._load_all(), before)
        self.assertFalse(self.dialog.saved)
        self.assertIn('(SQLITE_WRITE_TIMEOUT)', self.dialog.getControl(103).text)
        self.assertNotIn('private sqlite context', self.dialog.getControl(103).text)


class ManualIndex104(Fixture, unittest.TestCase):
    def test_confirmed_agent_binding_reads_directly_without_a_guide_database(self):
        import test_xcmate_mapping103 as prior
        from epg_agent100 import _save, profile
        from epg_agent_catalog103 import build
        from epg_binding48 import Mappings
        from guide_store import path
        from local_epg import window

        self.xml = prior.AgentGuide103.xml.__get__(self)
        folder = prior.AgentGuide103.candidate(self, [('s1.DMAX.de', 'DMAX')],
                                               [('s1.DMAX.de', 'Indexed DMAX', '')])
        build(folder, lambda: False)
        _save(profile(), dict(code='READY', generation='a' * 64))
        self.assertFalse(os.path.exists(path()))
        mappings = Mappings({'1': 's1.DMAX.de'}, {'1': dict(source='agent', channel='s1.DMAX.de')})
        stations = [dict(sid='1', name='DMAX HEVC', epg_channel_id='DMax.de')]
        view = window('p', stations, mappings, self.now, self.now + 3600, strict48=True)
        self.assertIsNotNone(view)
        indexed = view.channels['1']['s1.DMAX.de']
        self.assertEqual([(event['name'], event['source_key46']) for event in indexed], [('Indexed DMAX', 'agent')])
        empty = window('p', stations, mappings, self.now + 86400, self.now + 90000, strict48=True)
        self.assertEqual(empty.channels['1']['s1.DMAX.de'], [])

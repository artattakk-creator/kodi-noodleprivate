"""Agent previews and imports use locally verified generation rows."""
import gzip
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from xcmate027_fixture import Fixture, LIB

sys.path.insert(0, str(LIB))


class CompleteIndex104(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        from epg_agent_github import XMLTV_FILE

        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        self.folder = Path(root.name) / ('candidate-' + 'a' * 64)
        self.folder.mkdir()
        self.feed = self.folder / XMLTV_FILE
        self.feed.write_bytes(gzip.compress(b"""<tv>
        <channel id="s1.DMAX.de"><display-name>DMAX</display-name><display-name>Alias DE</display-name></channel>
        <channel id="s4.DMAX.at"><display-name>DMAX</display-name></channel>
        <programme channel="s1.DMAX.de" start="20261126172500 +0100" stop="20261126180000 +0100">
          <title>Fixture DE</title><title lang="en">Alternate fixture title</title><desc>Feed text</desc><date>2024</date>
          <credits><actor role="Presenter">Test Person</actor></credits>
          <episode-num system="xmltv_ns">1.2.</episode-num><episode-num system="tmdb">tv/12345</episode-num>
          <image type="poster" orient="P" system="tmdb">https://image.tmdb.org/t/p/w500/fixture.jpg</image>
        </programme>
        <programme channel="s4.DMAX.at" start="20261126172500 +0100" stop="20261126180000 +0100">
          <title>Fixture AT</title><episode-num system="tmdb">movie/678</episode-num>
        </programme>
        </tv>"""))
        saved = dict(status="PUBLIC_READY", channel_count=2, programme_count=2,
                     image_counts={'poster': 1}, staged_sha256=hashlib.sha256(self.feed.read_bytes()).hexdigest())
        import json
        (self.folder / 'manifest.json').write_text(json.dumps(saved))

    def test_unmapped_agent_preview_never_opens_the_feed_after_verification(self):
        from epg_agent_catalog103 import build
        from epg_candidate53 import Candidates

        build(self.folder, lambda: False)
        old_source = {'_agent_folder102': self.folder, '_agent_generation103': 'a' * 64,
                      'uri': str(self.feed), '_agent_artwork': 'legacy-artwork'}
        with mock.patch('epg_agent100.installed_source', return_value=old_source), \
                mock.patch('programme_index46.bounds', return_value=(1795500000, 1795900000)), \
                mock.patch('stream_epg.source_stream', side_effect=AssertionError('preview reopened XMLTV')):
            rows = Candidates().programmes({'id': 'p'}, 'agent', 's1.DMAX.de', lambda: False)
        self.assertEqual([row['name'] for row in rows], ['Fixture DE'])
        self.assertEqual(rows[0]['cast_roles'], {'Test Person': 'Presenter'})
        self.assertEqual(rows[0]['xmltv_tmdb_id'], 'tv/12345')
        self.assertEqual(rows[0]['agent_art']['poster']['orient'], 'P')

    def test_work_search_retains_exact_qualified_airing_and_episode(self):
        from epg_agent_catalog103 import build, art_reference, search_art

        build(self.folder, lambda: False)
        rows, more = search_art(self.folder, 'Fixture DE', work_id='tv/12345',
                                season=2, episode=3, role='poster')
        self.assertFalse(more)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(search_art(self.folder, 'Alternate fixture', role='poster'), (rows, False))
        self.assertEqual((row['channel'], row['work_id'], row['year']), ('s1.DMAX.de', 'tv/12345', 2024))
        self.assertEqual(art_reference(self.folder, row['channel'], row['start_timestamp'],
                                       row['stop_timestamp'], 'poster', 'agent_tmdb',
                                       row['reference']['url']), row)
        self.assertIsNone(art_reference(self.folder, 's4.DMAX.at', row['start_timestamp'],
                                        row['stop_timestamp'], 'poster', 'agent_tmdb',
                                        row['reference']['url']))

    def test_cancelled_upgrade_preserves_legacy_channels_file(self):
        import sqlite3
        from epg_agent_catalog103 import INDEX, build

        filename = self.folder / INDEX
        with sqlite3.connect(filename) as db:
            db.execute('CREATE TABLE channels(cid TEXT PRIMARY KEY)')
            db.execute('INSERT INTO channels VALUES(?)', ('legacy',))
        before = filename.read_bytes()
        with self.assertRaises(InterruptedError):
            build(self.folder, lambda: True)
        self.assertEqual(filename.read_bytes(), before)


    def test_cancelled_new_generation_leaves_prior_index_readable_during_staging(self):
        from queue import Queue
        import shutil
        import threading

        from epg_agent100 import local_candidate
        from epg_agent_catalog103 import build, programmes, ready

        build(self.folder, lambda: False)
        newer = self.folder.with_name('candidate-' + 'b' * 64)
        shutil.copytree(self.folder, newer, ignore=shutil.ignore_patterns('*.sqlite'))
        record = dict(generation='b' * 64, portals={'p': {'generation': 'a' * 64}})
        writing, release, stop = threading.Event(), threading.Event(), threading.Event()
        reports = Queue()

        def progress(_):
            writing.set()
            release.wait(3)

        def stage():
            try:
                build(newer, stop.is_set, progress=progress)
            except Exception as exc:
                reports.put(type(exc))

        worker = threading.Thread(target=stage)
        worker.start()
        try:
            self.assertTrue(writing.wait(3))
            active = local_candidate('p', self.folder.parent, record)
            self.assertEqual(active, self.folder)
            self.assertEqual(programmes(active, 's1.DMAX.de', 1795500000, 1795900000)[0]['name'], 'Fixture DE')
        finally:
            stop.set()
            release.set()
            worker.join(4)
        self.assertFalse(worker.is_alive())
        self.assertIs(reports.get(timeout=1), InterruptedError)
        self.assertFalse(ready(newer))


    def test_verified_work_airings_remain_queryable_without_any_artwork(self):
        from epg_agent_catalog103 import build, search_art, work_events

        build(self.folder, lambda: False)
        rows, more = work_events(self.folder, 'movie/678')
        self.assertFalse(more)
        self.assertEqual([(row['channel'], row['title']) for row in rows], [('s4.DMAX.at', 'Fixture AT')])
        self.assertEqual(search_art(self.folder, work_id='movie/678'), ([], False))

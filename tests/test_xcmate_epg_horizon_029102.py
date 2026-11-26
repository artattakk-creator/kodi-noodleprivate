"""Verified feed and cache coverage across Kodi local dates."""
import contextlib
import importlib
import io
import time
import unittest
from pathlib import Path
from unittest import mock

from xcmate027_fixture import Fixture


class Horizon102(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.guide = importlib.import_module('guide_store')
        self.stream = importlib.import_module('stream_epg')
        self.inventory = importlib.import_module('epg_inventory95')
        import epg_sources
        epg_sources._channel_name_key = lambda name: str(name).casefold()

    def start(self, offset):
        return self.guide.day_window(offset, self.now)[0] + 3600

    def feed(self, index, entries, streams):
        def stamp(value):
            return time.strftime('%Y%m%d%H%M%S +0000', time.gmtime(value))

        channels = sorted({cid for cid, day in entries})
        xml = '<tv>' + ''.join(
            f'<channel id="{cid}"><display-name>{cid}</display-name></channel>'
            for cid in channels
        ) + ''.join(
            f'<programme channel="{cid}" start="{stamp(self.start(day))}"'
            f' stop="{stamp(self.start(day) + 1800)}"><title>{cid} {day}</title></programme>'
            for cid, day in entries
        ) + '</tv>'

        @contextlib.contextmanager
        def source(*args, **kwargs):
            data = io.BytesIO(xml.encode())
            data.http_status = 200
            yield data

        with mock.patch.object(self.stream, 'source_stream', source):
            return self.stream.import_source('p', dict(uri='https://fixture.invalid/feed/' + str(index)),
                                             index, streams, {})

    def test_raw_3_7_14_day_feeds_merged_cache_and_outlier(self):
        stream = dict(sid='1', epg_channel_id='match', name='match')
        for index, days in enumerate((3, 7, 14)):
            with self.subTest(days=days):
                entries = [('match', day) for day in range(days)]
                entries += [('unmapped', 18), ('match', 23)]
                result = self.feed(index, entries, [stream])
                raw = result['raw_horizon102']
                self.assertEqual(raw['first'], self.start(0))
                self.assertEqual(raw['last'], self.start(23) + 1800)
                self.assertEqual(raw['last_contiguous_day'], raw['days'][days - 1]['date'])
                self.assertEqual(raw['days'][18]['channels'], 1)
                self.assertEqual(raw['days'][18]['programmes'], 1)
                self.assertEqual(result['matched_streams66'], 1)
                self.assertEqual(result['http_status'], 200)

        stats = self.inventory.collect('p', self.guide.path(), now=self.now)
        self.assertEqual(stats['programmes'], 14)
        self.assertEqual(stats['last'], self.start(13) + 1800)
        self.assertEqual(stats['horizon102']['days'][18]['programmes'], 0)
        self.assertEqual(stats['horizon102']['last_contiguous_day'],
                         stats['horizon102']['days'][13]['date'])
        self.assertEqual(sorted(row['horizon102']['days'][2]['channels']
                                for row in stats['sources']), [1, 1, 1])
        self.assertEqual(sorted(row['programmes'] for row in stats['sources']), [3, 7, 14])

        stale = self.inventory.collect('p', self.guide.path(), now=self.start(14))
        self.assertIsNone(stale['horizon102']['last_contiguous_day'])
        self.assertEqual(stale['programmes'], stats['programmes'])
        self.assertNotEqual(stale['horizon102']['days'][0]['date'],
                            stats['horizon102']['days'][0]['date'])

    def test_disjoint_channels_do_not_create_continuous_coverage(self):
        from epg_horizon102 import Coverage

        horizon = Coverage(self.now)
        horizon.add('first', self.start(0), self.start(0) + 1800)
        for day in range(1, 7):
            horizon.add('second', self.start(day), self.start(day) + 1800)
        result = horizon.result()
        self.assertEqual(result['last_contiguous_day'], result['days'][0]['date'])
        self.assertEqual([day['channels'] for day in result['days'][:7]], [1] * 7)


    def test_report_keeps_delivered_span_when_import_has_no_matches(self):
        from epg_errors import EmptyGuideError
        from epg_report53 import describe, history, observing, source_done, started
        from guide_publish44 import source_id

        source = dict(uri='https://fixture.invalid/feed/1')
        identity = source_id(source, 1)
        with observing('p'):
            started('p', 'fixture', identity, 1)
            with self.assertRaises(EmptyGuideError) as failure:
                self.feed(1, [('foreign', 0), ('foreign', 13)], [])
            source_done('p', identity, 'NO_CHANNEL_MATCH', failure.exception.epg_counts102)

        saved = history('p')[-1]
        row = saved['sources'][0]
        self.assertEqual(row['raw_horizon102']['last'], self.start(13) + 1800)
        self.assertEqual(row['matched_streams66'], 0)
        self.assertEqual(row['http_status'], 200)
        report = describe(saved, self.portal)
        self.assertIn('HTTP 200', report)
        self.assertIn('Geliefertes XMLTV vor Zuordnung und Zeitfilter', report)
        self.assertIn(row['raw_horizon102']['days'][13]['date'] + ' · 1 · 1', report)
        self.assertNotIn(source['uri'], report)

    def test_merge_readback_is_read_only(self):
        self.feed(0, [('match', 0)], [dict(sid='1', epg_channel_id='match', name='match')])
        path = Path(self.guide.path())
        before = path.read_bytes()
        report = self.inventory.collect('p', str(path), now=self.now)
        self.assertEqual(report['horizon102']['days'][0]['programmes'], 1)
        self.assertEqual(path.read_bytes(), before)

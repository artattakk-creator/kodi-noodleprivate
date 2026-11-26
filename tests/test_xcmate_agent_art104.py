from pathlib import Path
import unittest
from unittest import mock

from xcmate027_fixture import Fixture
import test_xcmate_artwork_roles_499 as roles_fixture


FIXTURE = Path(__file__).parent / 'fixtures' / 'epg-agent-519' / 'artwork.xml'


class AgentArtwork104(Fixture, unittest.TestCase):
    event = roles_fixture.ArtworkRoles499.event
    preflight = roles_fixture.ArtworkRoles499.preflight

    def setUp(self):
        super().setUp()
        self.options.update(epg_agent_enabled=True, programme_tmdb46=False, tmdb_research43=False,
                            programme_tvmaze67=False, programme_helper57=False, programme_catalog57=False)

    def feed_events(self):
        from epg_agent100_art import event_art, validator
        from xmltv_stream import parse

        rows = {}
        admit = validator()
        def record(event):
            rows[event['channel']] = dict(event, agent_art=event_art(event, admit))
        with FIXTURE.open('rb') as stream:
            parse(stream, lambda *_: None, record, include_images=True, include_icons=True)
        return rows

    def programme(self, raw):
        return dict(raw, start=raw['start_timestamp'], stop=raw['stop_timestamp'],
                    title=raw['name'], description=raw['descr'], epg_source46='agent',
                    _metadata_verified48=True, _agent_generation103='fixture-generation',
                    _agent_event104='fixture-event')

    def test_public_feed_reference_absence_and_present_roles_are_distinct(self):
        from programme_events46 import visible

        rows = self.feed_events()
        schluempfe = self.programme(rows['s1.KIKA.de'])
        series = self.programme(rows['s1.13th.Street.Universal.de'])
        self.assertEqual(schluempfe['title'], 'Die Schlümpfe')
        self.assertEqual(len(schluempfe['cast']), 6)
        self.assertEqual(schluempfe['agent_art'], {})
        self.assertEqual(set(series['agent_art']), {'backdrop', 'poster', 'legacy_icon'})

        for event, reason in ((schluempfe, 'AGENT_REFERENCE_MISSING'), (series, 'READY')):
            info = dict(events=[event], start=event['start'], stop=event['stop'], now=event['title'])
            with mock.patch('programme_index46.event', side_effect=AssertionError('GUI DB read')), \
                 mock.patch('programme_flow48.trace') as trace:
                described = visible(self.portal, dict(sid='1', name='Channel'), info)
            self.assertEqual(described['art_source_code104'], reason)
            self.assertEqual(described.get('_agent_generation103'), 'fixture-generation')
            self.assertTrue(any(call.args[:1] == ('SOURCE',) and call.args[2] == reason
                                for call in trace.call_args_list))
        self.assertEqual(described['xmltv_tmdb_id'], 'tv/2734')

    def test_generation_and_event_identity_affect_job_and_receipt_identity(self):
        from programme_requests68 import identity
        from programme_image69 import fingerprint

        event = self.event(('backdrop',))
        first = dict(event, _agent_generation103='one', _agent_event104='event')
        second = dict(first, _agent_generation103='two')
        self.assertNotEqual(identity(first), identity(second))
        self.assertNotEqual(fingerprint(first, 'agent_tmdb'), fingerprint(second, 'agent_tmdb'))

    def test_manual_backdrop_beats_automatic_still_in_detail(self):
        from agent_work103 import _id
        from agent_programme100 import candidates
        from programme_urls55 import resolve

        event = dict(self.event(('backdrop', 'episode_still')), _detail93=True)
        selected = next(row for row in candidates(event) if row['role81'] == 'backdrop')
        mapping = dict(source='agent_event103', id=_id(selected), agent103={'backdrop': _id(selected)})
        with mock.patch('programme_mapping85.current', return_value=mapping), \
             mock.patch('programme_urls55.probe', side_effect=self.preflight):
            result = resolve(event, url_mode69=True)
        self.assertEqual(result['role81'], 'backdrop')
        self.assertTrue(result['manual85'])

    def test_feed_missing_art_does_not_surface_optional_library_failure(self):
        from programme_urls55 import resolve

        event = dict(self.event(()), epg_source46='agent', _agent_event104='event')
        self.options['programme_catalog57'] = True
        with mock.patch('programme_library77.available', return_value=False):
            result = resolve(event, allow_lookup=True, url_mode69=True)
        self.assertEqual(result['code'], 'AGENT_REFERENCE_MISSING')

    def index_row(self, role='backdrop'):
        value = self.event((role,))['agent_art'][role]
        return dict(reference=value, role=role, channel='other.station.de', title='Both airings',
                    start_timestamp=10, stop_timestamp=20, work_id='tv/99', year=2011,
                    season=2, episode_number=3)

    def test_indexed_manual_candidate_reverified_by_exact_origin_after_restart(self):
        from agent_work103 import search, verify
        from programme_mapping85 import reload, set_mapping
        from programme_urls55 import resolve

        event = dict(self.event(()), epg_source46='agent')
        row = self.index_row()
        with mock.patch('epg_agent100.local_candidate', return_value=FIXTURE.parent), \
             mock.patch('epg_agent_catalog103.search_art', create=True, return_value=([row], False)) as find_work, \
             mock.patch('epg_agent_catalog103.art_references', create=True, return_value=[row]) as ref, \
             mock.patch('programme_urls55.probe', side_effect=self.preflight):
            rows = search(event, query='Both airings', role='backdrop')['rows']
            self.assertEqual(rows[0]['year'], 2011)
            self.assertEqual(rows[0]['channel'], 'other.station.de')
            self.assertEqual(find_work.call_args.kwargs['role'], 'backdrop')
            picked = verify(event, rows[0], lambda:False)
            set_mapping(event, picked)
            self.properties.clear()
            self.assertTrue(reload())
            result = resolve(event, url_mode69=True)
            self.assertGreaterEqual(ref.call_count, 2)
        self.assertEqual(result['source_url'], row['reference']['url'])
        self.assertTrue(result['manual85'])

    def test_feed_wide_episode_still_requires_verified_work_and_episode(self):
        from agent_work103 import search

        event = dict(self.event(()), _agent_event104='event', xmltv_tmdb_id='tv/99', season=2, episode=4)
        row = self.index_row('episode_still')
        with mock.patch('epg_agent100.local_candidate', return_value=FIXTURE.parent), \
             mock.patch('epg_agent_catalog103.search_art', create=True, return_value=([row], False)):
            self.assertEqual(search(event, role='episode_still')['rows'], [])
            self.assertEqual(len(search(dict(event, episode=3), role='episode_still')['rows']), 1)

    def test_verified_work_reuse_rejects_same_title_from_a_different_work(self):
        from programme_urls55 import resolve

        event = dict(self.event(()), _agent_event104='event', xmltv_tmdb_id='tv/99', title='Both airings')
        matching = self.index_row()
        remake = dict(matching, work_id='tv/909', year=2021)
        with mock.patch('epg_agent100.local_candidate', return_value=FIXTURE.parent), \
             mock.patch('epg_agent_catalog103.search_art', create=True, return_value=([remake], False)), \
             mock.patch('programme_urls55.probe', side_effect=AssertionError('Unrelated work image')):
            self.assertEqual(resolve(event, url_mode69=True)['source'], 'placeholder')
        with mock.patch('epg_agent100.local_candidate', return_value=FIXTURE.parent), \
             mock.patch('epg_agent_catalog103.search_art', create=True, return_value=([matching], False)), \
             mock.patch('programme_urls55.probe', side_effect=self.preflight):
            result = resolve(event, url_mode69=True)
        self.assertEqual(result['match'], 'EXACT_AGENT_WORK')
        self.assertTrue(result['decoded88'])

    def test_prefetch_uses_shared_failure_receipt_until_feed_policy_changes(self):
        import importlib.util
        from epg_handoff63 import profile_scope
        from media_sources43 import SourceError
        from programme_requests68 import agent_failure, completed
        import programme_urls55

        event = self.event(('backdrop',))
        with mock.patch('programme_urls55.probe', side_effect=SourceError('DNS_ERROR')):
            completed(event, programme_urls55.resolve(event, url_mode69=True))
        self.assertTrue(agent_failure(event))
        spec = importlib.util.spec_from_file_location('agent_queue104', programme_urls55.__file__)
        worker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(worker)
        with mock.patch.object(worker, '_thread', mock.Mock(is_alive=lambda:True)):
            self.assertFalse(worker.enqueue(event))
        self.properties['XCMate.Agent103.Variant.' + profile_scope()] = 'standard'
        self.assertFalse(agent_failure(event))

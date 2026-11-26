"""Isolated Agent remapping, station compatibility and source provenance."""
import contextlib
import gzip
import io
import sqlite3
import time
import unittest
from unittest import mock

from test_xcmate_epg_agent100 import AgentCycleTests
from xcmate027_fixture import Fixture


class StationProofs103(unittest.TestCase):
    def test_qualified_dotted_ids_and_country_prefixes_disambiguate_names(self):
        from epg_agent100_import import match

        channels = {'s1.Fixture.de': 'Fixture', 's4.Fixture.at': 'Fixture',
                    's2.Fixture+1.de': 'Fixture +1', 's5.Other.de': 'Other SD',
                    's6.Other.at': 'Other HD'}
        streams = [
            dict(sid='id', name='Fixture HEVC', epg_channel_id='Fixture.de'),
            dict(sid='exact', name='DE| Fixture FHD HEVC', epg_channel_id='s1.Fixture.de'),
            dict(sid='name', name='DE| Fixture HEVC'),
            dict(sid='unknown', name='Fixture HEVC'),
            dict(sid='conflict', name='AT| Fixture HEVC', epg_channel_id='Fixture.de'),
            dict(sid='shift', name='DE| Fixture +1 HEVC'),
            dict(sid='quality', name='DE| Other HD'),
        ]
        self.assertEqual(match(channels, streams, {}),
                         {'id': 's1.Fixture.de', 'exact': 's1.Fixture.de',
                          'name': 's1.Fixture.de', 'shift': 's2.Fixture+1.de'})

    def test_same_broadcast_hd_and_fhd_can_share_qualified_id(self):
        from epg_agent100_import import match

        self.assertEqual(match({'s1.Fixture.de': 'Fixture HD'},
                               [dict(sid='1', name='DE| Fixture FHD HEVC',
                                     epg_channel_id='Fixture.de')], {}),
                         {'1': 's1.Fixture.de'})


class MappingScope103(unittest.TestCase):
    def test_local_catalogue_change_reprocesses_retained_candidate_without_network(self):
        cycle = AgentCycleTests(methodName='runTest')
        cycle.setUp()
        self.addCleanup(cycle.doCleanups)
        with mock.patch('epg_agent100_import.mapping_scope', create=True, return_value='first') as scope:
            first = cycle.run_at(100_000)
            scope.return_value = 'updated'
            second = cycle.run_at(100_060)
            cycle.run_at(100_120)
        self.assertEqual((first['code'], second['code']), ('CURRENT', 'CURRENT'))
        self.assertEqual(len(cycle.fetch_calls), 1)
        self.assertEqual(len(cycle.installs), 2)


class AgentGuide103(Fixture, unittest.TestCase):
    def xml(self, channels, programmes):
        def stamp(value):
            return time.strftime('%Y%m%d%H%M%S +0000', time.gmtime(value))

        start, stop = stamp(self.now - 60), stamp(self.now + 1800)
        return ('<tv>' + ''.join(f'<channel id="{cid}"><display-name>{name}</display-name></channel>'
                                 for cid, name in channels)
                + ''.join(f'<programme channel="{cid}" start="{start}" stop="{stop}">'
                          f'<title>{title}</title>{metadata}</programme>'
                          for cid, title, metadata in programmes) + '</tv>').encode()

    def candidate(self, channels, programmes):
        from epg_agent100 import profile
        from epg_agent_github import XMLTV_FILE
        folder = profile() / ('candidate-' + 'a' * 64)
        folder.mkdir(parents=True)
        (folder / 'manifest.json').write_text('{"status":"PUBLIC_READY","channel_count":%d}' % len(channels))
        (folder / XMLTV_FILE).write_bytes(gzip.compress(self.xml(channels, programmes)))
        return folder

    def test_agent_is_visible_when_no_source_count_exists(self):
        from mapping_search482 import source_rows

        rows = source_rows({'id': 'p'})
        self.assertIn(('agent', 'NO_LOCAL_INDEX'), [(r['id'], r['local_code']) for r in rows])

    def test_agent_catalogue_includes_unmapped_channels_after_zero_match(self):
        from epg_agent100 import _save, profile
        from epg_agent100_import import install
        from epg_binding48 import channels

        names = [(f'cid-{number:03}', f'Fixture {number:03}') for number in range(501)]
        folder = self.candidate(names, [('cid-500', 'Programme', '')])
        _save(profile(), dict(code='IMPORT_PENDING', remote='AVAILABLE', generation='a' * 64))
        with mock.patch('epg._refresh_portal_epg', return_value={}, create=True):
            install({'id': 'p'}, folder, lambda: False)
        pages = [channels('p', 'agent', '', offset, strict482=True) for offset in range(0, 501, 100)]
        self.assertEqual([len(page) for page in pages], [100, 100, 100, 100, 100, 1])
        self.assertEqual([row['id'] for row in channels('p', 'agent', 'Fixture 500', strict482=True)],
                         ['cid-500'])

    def test_same_generation_only_imports_new_cids_and_reuses_existing_cids(self):
        from epg_agent100 import SOURCE_RANK
        from epg_agent100_art import build
        from epg_agent_catalog103 import build as catalogue
        from epg_binding48 import Mappings
        from epg_variant53 import channel_name_key
        from guide_store import path
        from stream_epg import import_source, publish_stages44

        folder = self.candidate([('first', 'First'), ('second', 'Second')], [
            ('first', 'First programme', ''), ('second', 'Second programme', '')])
        catalogue(folder, lambda: False)
        source = {'id': 'agent', 'uri': str(folder/'xcmate-epg.xml.gz'),
                  '_agent_artwork': str(build(folder, lambda: False)), '_agent_folder102': folder}
        first = dict(sid='1', name='First', epg_channel_id='first')
        second = dict(sid='2', name='Unmatched', epg_channel_id='missing')
        manual = Mappings({'2': 'second'}, {'2': {'channel': 'second', 'source': 'agent'}})
        with mock.patch('epg_sources._channel_name_key', channel_name_key, create=True):
            import_source('p', source, SOURCE_RANK, [first], Mappings())
            source['_agent_incremental103'] = True
            delta = import_source('p', source, SOURCE_RANK, [first, second], manual, stage_only=True)
            self.assertEqual(delta['counts']['stored'], 1)
            publish_stages44('p', [delta])
            extra = dict(first, sid='3')
            with mock.patch('stream_epg.source_stream', side_effect=AssertionError('no second scan')):
                import_source('p', source, SOURCE_RANK, [first, second, extra], manual)
        with sqlite3.connect(path()) as db:
            self.assertEqual(db.execute("SELECT cid,title FROM guide44_inputs WHERE source_id='agent' ORDER BY cid").fetchall(),
                             [('first', 'First programme'), ('second', 'Second programme')])

    def test_empty_or_incompatible_id_candidates_allow_one_compatible_scheduled_name(self):
        from epg_agent100 import SOURCE_RANK
        from epg_agent100_art import build
        from epg_agent_catalog103 import build as catalogue
        from epg_variant53 import channel_name_key
        from stream_epg import import_source

        folder = self.candidate([('s1.Test.de', 'Test station'), ('s2.TestAlt.de', 'DE| Test station HEVC'),
                                 ('s3.Test.at', 'Test station'), ('s4.Mixed.de', 'AT| Mixed'),
                                 ('s5.MixedStation.de', 'Mixed')],
                                [('s1.Test.de', 'Mapped', ''), ('s3.Test.at', 'Foreign', ''),
                                 ('s4.Mixed.de', 'Conflict', ''), ('s5.MixedStation.de', 'Correct', '')])
        catalogue(folder, lambda: False)
        source = {'id': 'agent', 'uri': str(folder/'xcmate-epg.xml.gz'),
                  '_agent_artwork': str(build(folder, lambda: False)), '_agent_folder102': folder}
        rows = [dict(sid='1', name='DE| Test station HEVC', epg_channel_id='TestAlt.de'),
                dict(sid='2', name='DE| Mixed HD', epg_channel_id='Mixed.de')]
        with mock.patch('epg_sources._channel_name_key', channel_name_key, create=True):
            stage = import_source('p', source, SOURCE_RANK, rows, {}, stage_only=True)
        self.assertEqual(stage['aliases'], {'1': 's1.Test.de', '2': 's5.MixedStation.de'})
        self.assertEqual(stage['proofs52'], {'1': 'name', '2': 'name'})

    def test_manual_agent_binding_does_not_erase_provider_import(self):
        from epg_binding48 import Mappings
        from epg_variant53 import channel_name_key
        from stream_epg import import_source

        stream = dict(sid='1', name='Portal station', epg_channel_id='provider-id')
        raw = self.xml([('provider-id', 'Guide station')], [('provider-id', 'Provider still works', '')])
        with mock.patch('epg_sources._channel_name_key', channel_name_key, create=True):
            with mock.patch('stream_epg.source_stream', return_value=contextlib.nullcontext(io.BytesIO(raw))):
                counts = import_source('p', {'uri': 'https://synthetic.invalid'}, 0, [stream],
                                       Mappings({'1': 'agent-id'}, {'1': {'channel': 'agent-id', 'source': 'agent'}}))
        self.assertEqual(counts['stored'], 1)

    def test_explicit_id_proof_merges_artwork_and_metadata_with_provenance(self):
        from epg_agent100 import SOURCE_RANK
        from epg_agent100_art import build
        from epg_binding48 import Mappings
        from epg_merge52 import publish_aliases
        from epg_variant53 import channel_name_key
        from local_epg import window
        from stream_epg import import_source

        agent_cid = 's1.Provider.de'
        agent = self.candidate([(agent_cid, 'Different station label')], [
            (agent_cid, 'Same series', '<country>DE</country>'
             '<image type="poster" system="tmdb">https://image.tmdb.org/t/p/w500/test.jpg</image>')])
        stream = dict(sid='1', name='Provider label', epg_channel_id='Provider.de')
        xml = self.xml([('Provider.de', 'Provider label')], [('Provider.de', 'Same series', '')])
        with mock.patch('epg_sources._channel_name_key', channel_name_key, create=True):
            with mock.patch('stream_epg.source_stream', return_value=contextlib.nullcontext(io.BytesIO(xml))):
                import_source('p', {'uri': 'https://synthetic.invalid'}, 0, [stream], Mappings())
            try:
                import_source('p', {'id': 'agent', 'uri': str(agent / 'xcmate-epg.xml.gz'),
                                    '_agent_artwork': str(build(agent, lambda: False))},
                              SOURCE_RANK, [stream], Mappings())
            except ValueError as error:
                self.fail(f'Qualified Agent import failed before the read path: {error}')
        self.assertTrue(publish_aliases('p', 'agent', {'1': agent_cid}, [stream], {},
                                        proofs={'1': 'provider_id'}))
        row = window('p', [stream], Mappings(), self.now, self.now + 3600)['Provider.de'][0]
        self.assertEqual(row['country'], 'DE')
        self.assertEqual(row['field_sources52']['country'], {'source': 'agent', 'channel': agent_cid})
        self.assertEqual(row['field_sources52']['start_timestamp'], {'source': 'provider', 'channel': 'Provider.de'})
        self.assertEqual(row['field_sources52']['agent_art.poster'], {'source': 'agent', 'channel': agent_cid})


if __name__ == '__main__':
    unittest.main()

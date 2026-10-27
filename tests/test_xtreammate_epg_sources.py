"""Independent XtreamMate XMLTV-source tests (Kodi device not required)."""
import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from hashlib import sha256
from pathlib import Path
from unittest import mock

LIB = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/resources/lib'
sys.path.insert(0, str(LIB))


class EpgSourceTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.directory = folder.name
        self.cache = {}
        utils = types.ModuleType('utils')
        utils.addon_data_dir = lambda: self.directory
        utils.cache_key = lambda s: sha256(s.encode('utf-8')).hexdigest()
        utils.cache_get = lambda key, max_age=0: self.cache.get(key)
        utils.cache_set = lambda key, value: self.cache.__setitem__(key, value)
        utils.http_get = lambda uri, timeout=20, **kwargs: (b'<tv/>', {})
        utils.error = lambda message: None
        p = mock.patch.dict(sys.modules, {'utils': utils})
        p.start()
        self.addCleanup(p.stop)
        spec = importlib.util.spec_from_file_location('test_xtream_epg_sources', LIB / 'epg_sources.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_sources_and_manual_mappings_survive_reload(self):
        item = self.module.add_source('portal-A', 'DE XMLTV',
                                      'https://example.test/tv.xml.gz')
        self.module.set_mapping('portal-A', '1001', 'welt.de')
        self.assertEqual(self.module.configuration('portal-A')['sources'][0]['id'], item['id'])
        self.assertEqual(self.module.configuration('portal-A')['mappings'], {'1001': 'welt.de'})
        self.assertEqual(self.module.configuration('portal-B')['sources'], [])
        self.assertTrue(os.path.isfile(self.module._file_path()))

    def test_rejects_duplicate_and_unsafe_sources(self):
        with self.assertRaises(ValueError):
            self.module.add_source('p', 'bad', 'file:///etc/secret')
        with self.assertRaises(ValueError):
            self.module.add_source('p', 'bad', 'ftp://example.test/tv.xml')
        self.module.add_source('p', 'ok', 'https://example.test/list.xml')
        with self.assertRaises(ValueError):
            self.module.add_source('p', 'again', 'https://example.test/list.xml')

    def test_merge_keeps_built_in_and_overrides_when_mapping_exists(self):
        self.module.add_source('p', 'Extra', 'https://example.test/list.xml')
        self.module.set_mapping('p', '1001', 'sky.de')
        own = {'zdf.de': [{'name': 'ZDF Heute'}],
               'welt.de': [{'name': 'veraltet'}]}
        def parse(raw):
            return ({'welt.de': 'WELT HD', 'sky.de': 'Sky Cinema'}, {'welt.de': [{'name':'WELT News','start_timestamp':100,'stop_timestamp':200}], 'sky.de': [{'name': 'Sky News','start_timestamp':100,'stop_timestamp':200}]})
        result, ok, fails = self.module.merge_sources('p', own, parse)
        self.assertEqual((ok, fails), (1, 0))
        self.assertEqual(result['zdf.de'][0]['name'], 'ZDF Heute')
        self.assertEqual(result['welt.de'][0]['name'], 'veraltet')
        self.assertEqual(result['1001'][0]['name'], 'Sky News')
        self.assertEqual(self.module.available_channels('p'), {'welt.de': 'WELT HD', 'sky.de':'Sky Cinema'})

    def test_regional_presets_are_opt_in_and_idempotent(self):
        self.assertEqual(self.module.configuration('p')['sources'], [])
        first = self.module.add_presets('p', ['de_master', 'at_epgshare', 'ch_epgshare'])
        self.assertEqual(len(first), 3)
        self.assertEqual(self.module.add_presets('p', ['ch_epgshare']), [])
        self.assertEqual(len(self.module.configuration('p')['sources']), 3)
        self.assertEqual(self.module.configuration('q')['sources'], [])
        with self.assertRaises(ValueError):
            self.module.add_presets('p', ['unknown'])

    def test_normalized_names_require_exact_station_identity(self):
        self.assertEqual(self.module._channel_name_key('DE | Sky Cinema Action HD'),
                         self.module._channel_name_key('Sky Cinema Action'))
        self.assertNotEqual(self.module._channel_name_key('Sky Cinema Thriller HD'),
                            self.module._channel_name_key('Sky Cinema Action HD'))

    def test_failed_external_url_preserves_provider_guide(self):
        self.module.add_source('p', 'invalid', 'https://example.test/missing.xml')
        with mock.patch.object(self.module, '_read_source', side_effect=OSError('offline')):
            result, loaded, failed = self.module.merge_sources('p',
                       {'welt.de':[{'name':'News'}]}, lambda raw: ({}, {}))
        self.assertEqual((loaded, failed), (0, 1))
        self.assertEqual(result['welt.de'][0]['name'], 'News')

    def test_priority_disable_and_remove(self):
        a = self.module.add_source('p', 'A', 'https://example.test/a.xml')
        b = self.module.add_source('p', 'B', 'https://example.test/b.xml')
        self.assertTrue(self.module.edit_source('p', b['id'], 'up'))
        self.assertEqual([x['name'] for x in self.module.configuration('p')['sources']], ['B', 'A'])
        self.assertTrue(self.module.edit_source('p', a['id'], 'toggle'))
        self.assertFalse(self.module.configuration('p')['sources'][1]['enabled'])
        self.assertTrue(self.module.edit_source('p', b['id'], 'delete'))
        self.assertEqual([x['name'] for x in self.module.configuration('p')['sources']], ['A'])

    def test_xml_bytes_limit_and_gzip(self):
        import gzip
        compressed = gzip.compress(b'<tv><programme/></tv>')
        with mock.patch.object(self.module, 'http_get', return_value=(compressed, {})):
            out = self.module._read_source({'uri':'https://example.test/a.gz', 'local':False})
        self.assertEqual(gzip.decompress(out), b'<tv><programme/></tv>')
        with mock.patch.object(self.module, 'http_get', return_value=(b'<!DOCTYPE tv>', {})):
            with self.assertRaises(ValueError):
                self.module._read_source({'uri':'https://example.test/tv.xml', 'local':False})

    def test_repo_wires_routes_and_epg_merging(self):
        main = (LIB / 'main.py').read_text(encoding='utf-8')
        epg = (LIB / 'epg.py').read_text(encoding='utf-8')
        self.assertIn("'epg_sources'        : self._epg_sources", main)
        self.assertIn("action='epg_sources', pid=pid", main)
        self.assertIn('merge_sources(', epg)
        settings = (LIB.parent / 'settings.xml').read_text(encoding='utf-8')
        self.assertIn('id="epg_sources_manager"', settings)


if __name__ == '__main__':
    unittest.main()

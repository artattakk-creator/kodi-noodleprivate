"""XtreamMate 0.1.3 catalog-cache regression tests without a Kodi box."""
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest import mock
from hashlib import sha256

LIB = Path(__file__).resolve().parent.parent / 'src/plugin.video.xtreammate/resources/lib'

class CacheTests(unittest.TestCase):
    def setUp(self):
        self.entries = {}
        self.calls = []
        u = types.ModuleType('utils')
        u.cache_key = lambda value: sha256(value.encode()).hexdigest()
        u.cache_get = lambda key, max_age=3600: self.entries.get(key)
        u.cache_set = lambda key, value: self.entries.__setitem__(key, value)
        def http_get(url, params=None):
            self.calls.append((url, params))
            return json.dumps([]).encode(), {}
        u.http_get = http_get
        u.setting_int = lambda *args: 15
        u.error = u.warn = u.info = u.debug = lambda *args: None
        self.patch = mock.patch.dict(sys.modules, {'utils': u})
        self.patch.start()
        self.addCleanup(self.patch.stop)
        spec = importlib.util.spec_from_file_location('xm_013_xtream', LIB / 'xtream.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.client = mod.XtreamClient('https://one.invalid', 'user', 'pass')
        self.other = mod.XtreamClient('https://two.invalid', 'user', 'pass')
    def test_servers_have_distinct_indexes(self):
        self.assertNotEqual(self.client._cache_key('get_live_streams'), self.other._cache_key('get_live_streams'))
    def test_cached_only_does_not_call_server(self):
        self.assertIsNone(self.client.get_cached_catalog('get_live_streams'))
        self.assertEqual(self.calls, [])
    def test_group_filter_live_vod_series(self):
        for name, method in [('get_live_streams', self.client.get_live_streams),
                             ('get_vod_streams', self.client.get_vod_streams),
                             ('get_series', self.client.get_series)]:
            self.entries[self.client._cache_key(name)] = [
                {'category_id': 'DE', 'name': 'RTL'},
                {'category_id': 'EN', 'name': 'BBC'},
                {'category_id': 'DE', 'name': 'ZDF'}]
            self.assertEqual([x['name'] for x in method('DE')], ['RTL', 'ZDF'])
        self.assertEqual(self.calls, [])
    def test_explicit_refresh_uses_api(self):
        self.client.get_live_streams(force_refresh=True)
        self.assertEqual(len(self.calls), 1)

if __name__ == '__main__':
    unittest.main()

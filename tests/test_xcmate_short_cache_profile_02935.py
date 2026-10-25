"""Cache timeout fallback and bounded phase logs; no network or decoder masking."""
import importlib,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class ShortCacheProfile35(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.views=importlib.import_module('epg_views')
        self.raw={'epg_listings':[dict(title='Real cached programme',start_timestamp=self.now-60,stop_timestamp=self.now+60)]}
    def test_timeout_of_extended_cache_preserves_valid_four_event_cache_without_network(self):
        client=types.SimpleNamespace(_get_json=mock.Mock(side_effect=[TimeoutError('PRIVATE'),self.raw]))
        result=self.views.cached_short_guide(client,'private-id',now=self.now)
        self.assertEqual(result['now'],'Real cached programme');self.assertEqual(result['stop'],self.now+60)
        self.assertTrue(all(c.kwargs['cached_only'] for c in client._get_json.call_args_list))
        self.assertEqual(len(client._get_json.call_args_list),2)
    def test_legacy_cache_failure_does_not_replace_working_extended_cache(self):
        client=types.SimpleNamespace(_get_json=mock.Mock(side_effect=[self.raw,OSError('PRIVATE')]))
        self.assertEqual(self.views.cached_short_guide(client,'1',now=self.now)['now'],'Real cached programme')
    def test_both_cache_variants_unavailable_return_neutral_without_writes_or_retry_loop(self):
        before=set(self.folder.iterdir());client=types.SimpleNamespace(_get_json=mock.Mock(side_effect=TimeoutError('PRIVATE')))
        result=self.views.cached_short_guide(client,'1',now=self.now)
        self.assertEqual(result['now'],'');self.assertEqual(result['stop'],0);self.assertEqual(client._get_json.call_count,2)
        self.assertEqual(set(self.folder.iterdir()),before)
    def test_repeated_worker_phases_aggregate_counts_and_total_wait_without_losing_final(self):
        profile=importlib.import_module('search_profile');logs=[];xbmc=sys.modules['xbmc'];xbmc.LOGINFO=1
        with mock.patch.object(xbmc,'log',side_effect=lambda value,*a:logs.append(value),create=True),mock.patch.object(profile.time,'monotonic_ns',return_value=10**10):
            p=profile.SearchProfile('a'*32,'b'*32)
            for _ in range(1000):p.emit('WORKER_BEGIN',queue_ms=2)
            p.emit('SCAN_FINAL',once=True,rows=1)
        self.assertEqual(len(logs),3)
        worker=[line for line in logs if 'phase=WORKER_BEGIN' in line]
        self.assertEqual(sum(int(line.split('events=')[1].split()[0]) for line in worker),1000)
        self.assertEqual(sum(int(line.split('queue_ms=')[1].split()[0]) for line in worker),2000)
        self.assertIn('SCAN_FINAL',logs[-1])

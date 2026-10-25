"""Real local SQLite/files plus strict Kodi models. Android gates remain open."""
import hashlib
import importlib
import importlib.util
import json
import os
import sys
import time
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture, LIB


def key(action,extra=None):
    return hashlib.sha256(json.dumps([action,extra],sort_keys=True).encode()).hexdigest()


class Search36(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.search=importlib.import_module('search_data')
        self.inventory=importlib.import_module('short_cache_inventory')
        self.client._cache_key=key
        self.entries=[dict(stream_id=str(i),category_id='a',name='Station '+str(i),epg_channel_id='xml'+str(i)) for i in range(2764)]
        self.index.replace_catalog('p','live',self.entries,self.catalogs['get_live_categories'])

    def finish(self,query):
        cursor=self.search.LiveSearch(self.portal,query,self.index.Reader('p'),self.now)
        snapshots=[]
        for _ in range(2048):
            rows,code=cursor.step();snapshots.append((list(rows),code))
            if cursor.done:return cursor,snapshots
        self.fail('unbounded enrichment')

    def touch(self,sid,limit=12,root=None):
        path=(root or self.folder)/(key('get_short_epg',dict(stream_id=str(sid),limit=limit))+'.json')
        path.write_text('{}');return path

    def test_sparse_tail_cache_is_visited_directly_without_2763_absent_reads(self):
        self.touch('2763',4);calls=[]
        def cached(client,sid,now=None):
            calls.append(sid)
            return dict(now='Verified local programme',stop=self.now+60)
        with mock.patch('epg_views.cached_short_guide',side_effect=cached):
            cursor,states=self.finish('Verified local programme')
        self.assertEqual(calls,['2763']);self.assertEqual(cursor.short_rows,1)
        self.assertEqual(states[-1][0][0]['sid'],'2763')
        self.assertEqual(cursor.counts['programme_hits'],1)
        self.assertEqual(states[0][1],'EPG_PARTIAL')

    def test_empty_inventory_stops_without_any_cache_read_or_network(self):
        before=set(self.folder.iterdir())
        with mock.patch('epg_views.cached_short_guide') as cached:
            cursor,states=self.finish('Absent programme')
        cached.assert_not_called();self.assertTrue(cursor.done);self.assertEqual(states[-1][0],[])
        self.assertEqual(set(self.folder.iterdir())-before,{self.folder/'xcmate_diagnostic_epg_search.json'})

    def test_private_and_custom_cache_roots_are_both_considered(self):
        custom=self.folder/'custom';custom.mkdir();self.touch('2763',root=custom)
        with mock.patch.object(sys.modules['utils'],'cache_dir',return_value=str(custom)):
            found=self.inventory.candidates(self.client,[dict(sid='2763'),dict(sid='1')])
        self.assertEqual(found,[dict(sid='2763')])

    def test_unreadable_inventory_retains_legacy_cache_only_path(self):
        self.client._cache_key=key
        with mock.patch.object(self.inventory.os,'scandir',side_effect=PermissionError('PRIVATE')):
            self.assertIsNone(self.inventory.candidates(self.client,[dict(sid='1')]))
        client=types.SimpleNamespace(_get_json=mock.Mock(return_value={}))
        self.assertIsNone(self.inventory.candidates(client,[dict(sid='1')]))

    def test_cancelled_or_over_budget_inventory_never_claims_absence(self):
        self.assertIsNone(self.inventory.candidates(self.client,[dict(sid='1')],lambda:True))
        root='smb://private/cache'
        with mock.patch.object(sys.modules['utils'],'cache_dir',return_value=root),mock.patch.object(sys.modules['xbmcvfs'],'listdir',return_value=([],['x']*100001),create=True):
            self.assertIsNone(self.inventory.candidates(self.client,[dict(sid='1')]))

    def test_corrupt_existing_cache_is_attempted_once_and_does_not_loop(self):
        self.touch('1')
        with mock.patch('epg_views.cached_short_guide',side_effect=ValueError('PRIVATE')) as cached:
            cursor,states=self.finish('Missing')
        self.assertEqual(cached.call_count,1);self.assertTrue(cursor.done)
        self.assertEqual(states[-1][0],[])

    def test_mapping_wins_and_missing_manual_id_does_not_use_short_cache(self):
        self.touch('2763')
        with mock.patch.object(sys.modules['epg_sources'],'configuration',return_value=dict(mappings={'2763':'missing'},sources=[])),mock.patch('epg_views.cached_short_guide') as cached:
            cursor,states=self.finish('Any programme')
        cached.assert_not_called();self.assertEqual(cursor.counts['manual_missing'],1)

    def test_guide_now_and_search_now_agree_and_unknown_title_is_not_invented(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'xml2763':[dict(channel='canonical',name='Proven Now',start_timestamp=self.now-60,stop_timestamp=self.now+60)]})
        cursor,states=self.finish('Proven Now')
        self.assertEqual(states[-1][0][0]['_now_title'],'Proven Now')
        rows,_=guide.events('p','xml2763',self.now,self.now+1)
        self.assertEqual(rows[0]['title'],states[-1][0][0]['_now_title'])
        self.assertEqual(self.finish('Not present in guide')[1][-1][0],[])

    def test_name_results_still_precede_inventory_and_epg_sql(self):
        cursor=self.search.LiveSearch(self.portal,'Station 2763',self.index.Reader('p'),self.now)
        with mock.patch.object(self.inventory,'candidates',side_effect=AssertionError('too early')),mock.patch.object(self.search,'_now_events',side_effect=AssertionError('too early')):
            rows,code=cursor.step()
        self.assertEqual([r['sid'] for r in rows],['2763']);self.assertEqual(code,'EPG_PARTIAL')

    def test_fifty_thousand_channels_read_only_the_existing_tail_cache(self):
        entries=[dict(stream_id=str(i),category_id='a',name='Station '+str(i)) for i in range(50000)]
        self.index.replace_catalog('p','live',entries,self.catalogs['get_live_categories'])
        self.touch('49999',4)
        with mock.patch('epg_views.cached_short_guide',return_value=dict(now='Tail programme',stop=self.now+60)) as cached:
            cursor,states=self.finish('Tail programme')
        self.assertEqual(cached.call_count,1);self.assertEqual(cursor.position,50000)
        self.assertEqual(states[-1][0][0]['sid'],'49999')

    def test_requested_numeric_phases_and_visible_programme_are_logged(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'xml2763':[dict(name='Proven',start_timestamp=self.now-10,stop_timestamp=self.now+60)]})
        logs=[];xbmc=sys.modules['xbmc'];xbmc.LOGINFO=1
        with mock.patch.object(xbmc,'log',side_effect=lambda v,*a:logs.append(v),create=True):
            w=self.media_window();self.dialog.input.return_value='Proven';w._search();w.onClick(700)
            for _ in range(64):
                w._pool.drain();w.pump()
                if not w._pool.jobs:break
        joined='\n'.join(logs)
        for phase in ('INDEX_QUERY_DONE','NOW_LOCAL_MATCH','ENRICHMENT_STARTED','CACHE_BATCH_DONE','NO_PROGRESS_STOP','VISIBLE_FIRST_PROGRAMME','FINAL'):
            self.assertIn('phase='+phase,joined)
        self.assertNotIn('Proven',joined);self.assertNotIn('xml2763',joined)
        self.assertNotIn('SECRET',joined)


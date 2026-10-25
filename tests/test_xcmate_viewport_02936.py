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


class Viewport36(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.guide=importlib.import_module('guide_store')
        self.viewport=importlib.import_module('guide_viewport')
        self.data=importlib.import_module('tv_data')
        self.channel=types.SimpleNamespace(tvg_id='xml',extra={'stream_id':'1'})

    def install(self):
        self.guide.import_cache('p',{'xml':[dict(channel='canonical',name='Now',start_timestamp=self.now-60,stop_timestamp=self.now+60),
            dict(channel='canonical',name='Next',start_timestamp=self.now+60,stop_timestamp=self.now+600)]})

    def test_snapshot_reads_only_requested_db_channels_without_global_epg_cache(self):
        self.install();before=(self.folder/'guide_v1.sqlite').read_bytes()
        snapshot=self.data.GuideSnapshot(self.portal,self.client);snapshot.request([self.channel])
        with mock.patch.object(sys.modules['epg'],'load_cache',side_effect=AssertionError('whole EPG')),mock.patch.object(sys.modules['epg'],'_mem_clear',side_effect=AssertionError('global cache clear')):
            snapshot.refresh()
        info=snapshot.get('1',self.now)
        self.assertEqual((info['now'],info['next']),('Now','Next'))
        self.assertEqual(before,(self.folder/'guide_v1.sqlite').read_bytes())
        with mock.patch.object(self.viewport,'cache',side_effect=AssertionError('disk in GUI')):
            self.assertEqual(snapshot.get('1',self.now+61)['now'],'Next')

    def test_viewport_is_bounded_and_manual_mapping_cannot_use_provider_fallback(self):
        self.install()
        channels=[types.SimpleNamespace(tvg_id='xml',extra={'stream_id':str(i)}) for i in range(50000)]
        result=self.viewport.cache('p',channels,{'1':'missing'},self.now)
        self.assertLessEqual(len(result),33)
        self.assertEqual(result['missing'],[])
        info=importlib.import_module('epg_views').resolve_guide(result,'xml','1',self.now,self.client,{'1':'missing'})
        self.assertEqual(info['now'],'');self.assertEqual(info['mapping'],'MANUAL')

    def test_missing_database_is_not_created_and_legacy_cache_remains_usable(self):
        self.assertIsNone(self.viewport.cache('p',[self.channel],{},self.now))
        self.assertFalse((self.folder/'guide_v1.sqlite').exists())
        self.cache['xml']=[dict(name='Legacy',start_timestamp=self.now-1,stop_timestamp=self.now+60)]
        snapshot=self.data.GuideSnapshot(self.portal,self.client);snapshot.request([self.channel]);snapshot.refresh()
        self.assertEqual(snapshot.get('1',self.now)['now'],'Legacy')

    def test_corrupt_database_returns_unknown_without_replacing_or_mutating_it(self):
        path=self.folder/'guide_v1.sqlite';path.write_bytes(b'corrupt')
        self.assertIsNone(self.viewport.cache('p',[self.channel],{},self.now))
        self.assertEqual(path.read_bytes(),b'corrupt')

    def test_catalog_uses_selected_index_rows_without_reading_full_provider_json(self):
        catalogue=importlib.import_module('live_catalog')
        original=self.client.get_cached_catalog
        def cached(action):
            if action=='get_live_streams':raise AssertionError('full provider JSON')
            return original(action)
        self.client.get_cached_catalog=cached
        groups,rows=catalogue.read(self.portal,self.client)
        self.assertEqual(len(rows),3);self.assertEqual(rows[0]['stream_id'],'1')
        self.assertEqual(len(groups),2)

    def test_catalog_does_not_fall_back_behind_an_unavailable_index(self):
        catalogue=importlib.import_module('live_catalog')
        with mock.patch.object(self.index.Reader,'state',side_effect=self.index.IndexReadError('locked')):
            _,rows=catalogue.read(self.portal,self.client)
        self.assertIsNone(rows)

    def test_newly_enabled_group_keeps_legacy_cached_channels_before_index_import(self):
        catalogue=importlib.import_module('live_catalog')
        self.index.replace_catalog('p','live',self.catalogs['get_live_streams'],self.catalogs['get_live_categories'],allowed={'a'})
        groups,rows=catalogue.read(self.portal,self.client)
        self.assertEqual(rows,self.catalogs['get_live_streams']);self.assertEqual(len(groups),2)


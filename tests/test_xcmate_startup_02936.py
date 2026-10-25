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


class Startup36(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();sys.modules['xbmcgui'].WindowDialog=object
        self.start=importlib.import_module('live_start')
        self.client.live_stream_url=lambda sid,ext:'https://provider.invalid/live/u/SECRET/'+sid+'.'+ext

    def test_ready_index_uses_one_sender_without_full_catalog_read(self):
        self.client.get_cached_catalog=mock.Mock(side_effect=AssertionError('whole catalogue'))
        row=self.start.channel(self.portal,self.client)
        self.assertEqual(row['stream_id'],'1');self.assertEqual(row['name'],'House of Dragon TV')
        self.client.get_cached_catalog.assert_not_called()

    def test_disabled_group_or_missing_indexed_sender_never_falls_back(self):
        groups=importlib.import_module('group_selection');groups.save('p',set(),kind='live')
        self.client.get_cached_catalog=mock.Mock(side_effect=AssertionError('bypass selection'))
        self.assertIsNone(self.start.channel(self.portal,self.client))
        self.portal['start_stream_id']='foreign'
        self.assertIsNone(self.start.channel(self.portal,self.client))

    def test_locked_index_does_not_start_expensive_catalog_fallback(self):
        with mock.patch.object(self.index.Reader,'state',side_effect=self.index.IndexReadError('locked')):
            self.assertIsNone(self.start.channel(self.portal,self.client))

    def test_cold_legacy_cache_is_read_once_without_http(self):
        os.unlink(self.index.path())
        self.client.get_cached_catalog=mock.Mock(return_value=self.catalogs['get_live_streams'])
        self.assertEqual(self.start.channel(self.portal,self.client)['stream_id'],'1')
        self.client.get_cached_catalog.assert_called_once_with('get_live_streams')

    def test_cold_streaming_fallback_stops_at_match_and_handles_missing_file(self):
        os.unlink(self.index.path())
        self.client.iter_catalog=mock.Mock(return_value=iter(self.catalogs['get_live_streams']))
        self.assertEqual(self.start.channel(self.portal,self.client)['stream_id'],'1')
        self.client.iter_catalog.assert_called_once_with('get_live_streams',cached_only=True)
        def missing(*a,**kw):raise FileNotFoundError('PRIVATE');yield
        self.client.iter_catalog=missing
        self.assertIsNone(self.start.channel(self.portal,self.client))

    def test_home_validation_passes_metadata_to_resolver_without_second_lookup(self):
        self.router._params['action']='home_start';self.router._handle=-1
        self.router._play_start_direct=mock.Mock()
        with mock.patch.object(self.start,'channel',wraps=self.start.channel) as lookup:
            self.routes.dispatch(self.router)
        self.assertEqual(lookup.call_count,1);self.router._play_start_direct.assert_called_once()
        self.assertEqual(self.router._start_channel['stream_id'],'1')

    def test_manual_resolver_and_direct_start_keep_their_native_player_contracts(self):
        spec=importlib.util.spec_from_file_location('startup36_main',LIB/'main.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        item=types.SimpleNamespace(getPath=lambda:'https://provider.invalid/live/u/SECRET/1.ts',setProperty=lambda *a:None)
        with mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=lambda *a,**kw:item)),mock.patch('play_intent.before_play',return_value=True),mock.patch('live_recovery.tag_live_item'):
            router=module.Router(['plugin://plugin.video.xtreammate','7','?pid=p'])
            sys.modules['xbmc'].Player=lambda:types.SimpleNamespace(play=mock.Mock(side_effect=AssertionError('direct play in resolver')))
            router._play_start()
            sys.modules['xbmcplugin'].setResolvedUrl.assert_called_once_with(7,True,item)
            sys.modules['xbmcplugin'].setResolvedUrl.reset_mock();played=mock.Mock()
            sys.modules['xbmc'].Player=lambda:types.SimpleNamespace(play=played)
            router._play_start_direct();played.assert_called_once_with(item.getPath(),item)
            sys.modules['xbmcplugin'].setResolvedUrl.assert_not_called()


"""Non-Xtream navigation uses real Omega dialog callbacks and tagged ownership."""
import importlib
import json
import sys
import types
import unittest
from unittest import mock
import test_xcmate_kodi21_overlay as omega
from xcmate027_fixture import QueuedPool


class SourceNavigationTests(unittest.TestCase):
    def setUp(self):
        omega.OverlayLifecycleTests.setUp(self)
        self.portal=dict(self.portal,type='m3u',start_stream_id='opaque-a')
        categories=[dict(category_id='a',category_name='A')]
        streams=[dict(stream_id='opaque-'+suffix,category_id='a',name=suffix.upper()) for suffix in ('a','b','c')]
        self.client.get_cached_catalog=lambda action:categories if action=='get_live_categories' else streams
        self.client.play_uri=mock.Mock(return_value=('https://stream.invalid/opaque',{'User-Agent':'provider'}))
        modules={'live_overlay':self.module,'source_adapters':types.SimpleNamespace(for_portal=lambda p:self.client),
                 'xbmcplugin':types.SimpleNamespace()}
        patch=mock.patch.dict(sys.modules,modules);patch.start();self.addCleanup(patch.stop)
        sys.modules.pop('source_live',None);self.sources=importlib.import_module('source_live')
        patch=mock.patch.object(self.sources,'ThreadPoolExecutor',QueuedPool);patch.start();self.addCleanup(patch.stop)
        self.session=self.module.announce('p','opaque-a');self.tag=self.session
        self.player.getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda key:json.dumps(self.tag))
        self.nav=self.sources.SourceNavigator(self.portal,'opaque-a');self.addCleanup(self.nav.close);self.nav.show()
        self.item=types.SimpleNamespace(getPath=lambda:'https://stream.invalid/prepared',getVideoInfoTag=lambda:types.SimpleNamespace(setUniqueIDs=lambda value:None))
        patch=mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=mock.Mock(return_value=self.item)))
        patch.start();self.addCleanup(patch.stop)

    def test_native_nondecimal_channel_list_ok_defers_resolution_and_player_to_service_tick(self):
        self.assertTrue(self.nav.owns_playback());self.assertFalse(hasattr(self.nav,'onInit'))
        self.nav.native(1);self.nav.native(4);self.nav.native(7)
        self.client.play_uri.assert_not_called();self.player.play.assert_not_called()
        self.nav._source_pool.drain();self.client.play_uri.assert_called_once_with('live','opaque-b')
        self.player.play.assert_not_called();self.nav.tick();self.player.play.assert_called_once()
        self.assertEqual(self.nav.sid,'opaque-b')
        session=json.loads(self.props[self.module.SESSION_KEY]);self.assertEqual(session['sid'],'opaque-b')
        self.tag=session;self.assertTrue(self.nav.owns_playback())

    def test_foreign_player_tag_discards_completed_tune_without_play_or_stop(self):
        self.nav._tune(self.nav.index.by_sid['opaque-b']);self.nav._source_pool.drain()
        self.tag=dict(self.session,nonce='foreign')
        self.nav.tick();self.player.play.assert_not_called();self.player.stop.assert_not_called()
        self.assertFalse(self.nav.owns_playback())
        self.nav.native(7);self.assertTrue(self.nav._closed)

    def test_rapid_zap_coalesces_stale_jobs_and_preserves_final_target(self):
        self.nav._zap(1);self.nav._zap(1)
        self.client.play_uri.assert_not_called();self.nav._source_pool.drain()
        self.client.play_uri.assert_called_once_with('live','opaque-c')
        self.nav.tick();self.assertEqual(self.nav.sid,'opaque-c');self.player.play.assert_called_once()

    def test_close_during_pending_link_never_restarts_player(self):
        self.nav._zap(1);self.nav.close();self.nav._source_pool.drain();self.nav.tick()
        self.client.play_uri.assert_not_called();self.player.play.assert_not_called()

    def test_completed_background_catalog_rebuild_is_applied_without_remote_calls(self):
        self.client._local_urls={}
        groups=[dict(category_id='a',category_name='A')]
        streams=[dict(stream_id='opaque-a',category_id='a',name='Updated A')]
        adapter=types.SimpleNamespace(get_cached_catalog=lambda action:groups if action=='get_live_categories' else streams,_local_urls={})
        with mock.patch.dict(sys.modules,library_index=types.SimpleNamespace(Reader=lambda pid:types.SimpleNamespace(state=lambda kind:dict(revision='new'))),
                             source_adapters=types.SimpleNamespace(for_portal=lambda portal:adapter)):
            self.nav._catalog_next=0;self.nav.tick()
            self.assertEqual(self.nav.index.by_sid['opaque-a'].name,'A')
            self.nav._source_pool.drain()
            self.client.get_cached_catalog=lambda action:self.client._catalog_snapshot[action]
            self.nav.tick()
        self.assertEqual(self.nav.index.by_sid['opaque-a'].name,'Updated A')
        self.client.play_uri.assert_not_called();self.player.play.assert_not_called()

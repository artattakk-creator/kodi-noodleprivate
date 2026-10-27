"""#245: committed Home race and invalidated InfoTag after a confirmed Stop."""
import importlib
import sys
import time
import unittest
from unittest import mock
import test_xcmate_live_stop_02917 as old


class LiveReturn47(unittest.TestCase):
    def setUp(self):
        self.m=old.StopTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.guard=importlib.import_module('live_return47')
        self.jobs=importlib.import_module('exit_jobs')

    def home(self):
        self.assertTrue(self.m.exit.request(self.m.nav))
        value=self.m.exit.state();value['phase']='home';self.m.exit._save(value);self.m.playing=False
        return value

    def test_committed_home_is_not_overwritten_by_a_stale_modal_blocked_poll(self):
        self.home();original=self.guard.guard
        def competing(value):
            self.m.exit._save(dict(value,phase='complete'))
            return original(value)
        with mock.patch.object(self.guard,'guard',side_effect=competing),mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=True):
            self.m.exit._poll(self.m.nav)
        self.assertEqual(self.m.exit.state()['phase'],'complete')
        self.assertFalse(self.m.builtins);self.assertEqual(self.m.stops,0)

    def test_new_selection_between_stop_done_and_return_never_gets_old_home(self):
        self.home();original=self.guard.guard
        def replaced(value):
            self.m.exit.new_selection()
            return original(value)
        with mock.patch.object(self.guard,'guard',side_effect=replaced):self.m.exit._poll(self.m.nav)
        self.assertIsNone(self.m.exit.state());self.assertFalse(self.m.builtins)

    def test_foreign_modal_is_not_closed_or_ignored_before_one_home_request(self):
        self.home()
        with mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=True):
            for _ in range(8):self.m.exit._poll(self.m.nav)
        self.assertFalse(self.m.builtins);self.assertEqual(self.m.exit.state()['phase'],'home')
        for _ in range(8):self.m.exit._poll(self.m.nav)
        self.assertEqual(len(self.m.builtins),1)
        self.assertEqual(self.m.exit.state()['phase'],'complete')

    def test_confirmed_stop_with_transient_playing_flag_and_no_tag_waits_without_second_stop(self):
        value=self.home();value['phase']='stopping';self.m.exit._save(value)
        self.jobs.save(dict(token=['live',self.m.session],phase='complete',at=time.time(),deadline=time.monotonic()+5,
                            worker_done=True,stop_started=True,result='complete'))
        self.m.playing=True
        self.m.player.getVideoInfoTag=mock.Mock(side_effect=RuntimeError('Kodi item already gone'))
        self.assertTrue(self.m.exit._poll(self.m.nav))
        self.assertEqual(self.m.exit.state()['phase'],'stopping')
        self.assertTrue(self.m.exit.state()['player_wait47'])
        self.assertEqual(self.m.stops,0);self.assertFalse(self.m.builtins)
        self.m.playing=False
        for _ in range(4):self.m.exit._poll(self.m.nav)
        self.assertEqual(self.m.exit.state()['phase'],'complete');self.assertEqual(len(self.m.builtins),1)

    def test_genuinely_foreign_playback_after_stop_is_still_protected(self):
        value=self.home();value['phase']='stopping';self.m.exit._save(value);self.m.playing=True
        with mock.patch('playback_exit.identity',return_value=('media',dict(self.m.session,nonce='foreign',kind='vod'))):
            self.m.exit._poll(self.m.nav)
        self.assertEqual(self.m.exit.state()['phase'],'failed');self.assertFalse(self.m.builtins);self.assertEqual(self.m.stops,0)

    def test_background_catalog_model_is_reused_without_building_channels_on_gui(self):
        catalog=importlib.import_module('live_catalog');future=catalog.prepare(self.m.portal,self.m.client,force=True)
        future.result(timeout=5)
        nav=self.m.live.LiveNavigator.__new__(self.m.live.LiveNavigator)
        nav.portal=self.m.portal;nav.xc=self.m.client;nav.sid='1';nav._catalog_future39=future
        with mock.patch('iptv.Channel',side_effect=AssertionError('Channel built on GUI')):
            self.assertTrue(nav._load_catalog_from_disk())
        self.assertIs(nav.index,future.model47['index'])
        self.assertEqual(len(nav.channels),3)

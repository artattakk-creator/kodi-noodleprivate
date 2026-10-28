"""Long Home playback return, foreign ownership and existing native strategy."""
import importlib
import sys
import time
import unittest
from unittest import mock
import test_xcmate_live_stop_02917 as old

class LiveExit48(unittest.TestCase):
    def setUp(self):
        self.m=old.StopTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.trace=importlib.import_module('live_trace48')
    def home(self):
        self.assertTrue(self.m.exit.request(self.m.nav));value=self.m.exit.state()
        value.update(phase='home',origin_window48=10000);self.m.exit._save(value);self.m.playing=False;return value
    def test_home_widget_stop_returns_to_existing_kodi_home_exactly_once(self):
        self.home()
        for _ in range(12):self.m.exit._poll(self.m.nav)
        self.assertEqual(self.m.builtins,['ActivateWindow(Home)']);self.assertEqual(self.m.stops,0)
        self.assertEqual(self.m.exit.state()['phase'],'complete')
    def test_actual_home_needs_no_reentering_root_or_container_reload(self):
        self.home()
        with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowId',return_value=10000):
            self.m.exit._poll(self.m.nav)
        self.assertEqual(self.m.exit.state()['phase'],'complete');self.assertFalse(self.m.builtins)
    def test_foreign_native_window_holds_home_without_stopping_or_closing_it(self):
        self.home()
        with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowId',return_value=13099):
            for _ in range(3):self.m.exit._poll(self.m.nav)
        self.assertEqual(self.m.exit.state()['phase'],'home');self.assertFalse(self.m.builtins)
    def test_foreign_modal_still_blocks_home_transition(self):
        self.home()
        with mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=True):self.m.exit._poll(self.m.nav)
        self.assertFalse(self.m.builtins);self.assertEqual(self.m.stops,0)
    def test_normal_app_entry_retains_original_xcmate_return_path(self):
        self.home();value=self.m.exit.state();value.pop('origin_window48');self.m.exit._save(value)
        self.m.exit._poll(self.m.nav)
        self.assertEqual(self.m.exit.state()['phase'],'complete');self.assertIn('action=xcmate_home',self.m.builtins[-1])
    def test_stop_request_after_twenty_minutes_remains_same_session_not_new_autoplay(self):
        self.m.session['at']=time.time()-1200
        # Existing fixture tag returns this same mutable immutable-item identity.
        self.assertTrue(self.m.exit.request(self.m.nav))
        self.assertEqual(self.m.exit.state()['session']['nonce'],self.m.session['nonce'])
        for _ in range(4):self.assertTrue(self.m.exit.request(self.m.nav))
        self.assertEqual(self.m.stops,0);self.assertEqual(self.m.exit.state()['phase'],'requested')
    def test_background_suspension_during_exit_never_queries_locked_player(self):
        self.home();s=importlib.import_module('startup48')
        with mock.patch.object(sys.modules['xbmc'],'Player',side_effect=AssertionError('native query during Stop')),mock.patch('exit_jobs.blocked',return_value=False):
            self.assertTrue(s.suspended())
    def test_exit_diagnostics_whitelist_and_hash_private_identifiers(self):
        value=self.home();value['session']['pid']='PRIVATE_PORTAL';value['session']['nonce']='PRIVATE_NONCE'
        with mock.patch.object(sys.modules['xbmc'],'log',create=True) as log,mock.patch.object(sys.modules['xbmc'],'LOGINFO',1,create=True):
            self.trace._last.clear();self.trace.observe(value,dict(phase='timeout',native_posted=True,worker_done=False))
            message=log.call_args.args[0]
        self.assertNotIn('PRIVATE',message);self.assertIn('age_seconds=',message);self.assertIn('ack=0',message)

    def test_completed_live_exit_does_not_suspend_movie_widget_refresh_or_optional_jobs(self):
        value=self.home();value['phase']='complete';self.m.exit._save(value)
        with mock.patch('exit_jobs.blocked',return_value=False):self.assertFalse(importlib.import_module('startup48').suspended())

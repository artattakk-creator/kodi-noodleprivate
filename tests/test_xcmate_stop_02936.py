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


class Stop36(unittest.TestCase):
    def setUp(self):
        import test_xcmate_live_stop_02917 as model
        self.m=model.StopTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)

    def test_two_navigators_cannot_restart_same_session_stop_home_or_deadline(self):
        m=self.m;m.exit.request(m.nav);prior=m.exit.state()
        another=types.SimpleNamespace(**vars(m.nav));another._exiting=False
        self.assertTrue(m.exit.request(another));self.assertEqual(m.exit.state(),prior)
        m.finish();complete=m.exit.state();another._exiting=False
        self.assertTrue(m.exit.request(another));self.assertEqual(m.exit.state(),complete)
        for _ in range(20):m.exit.poll(another)
        self.assertEqual(m.stops,1);self.assertEqual(len(m.builtins),1)

    def test_existing_home_is_revealed_without_reloading_its_plugin_url(self):
        m=self.m;m.current_folder='plugin://plugin.video.xtreammate/?pid=p&action=xcmate_home'
        m.exit.request(m.nav);m.finish()
        self.assertEqual(m.builtins,['ActivateWindow(Videos)'])

    def test_already_active_matching_home_needs_no_directory_request(self):
        m=self.m;m.current_folder='plugin://plugin.video.xtreammate/?action=xcmate_home&pid=p'
        m.exit.request(m.nav);m.ready();m.exit.poll(m.nav)
        with mock.patch.object(sys.modules['xbmc'],'getCondVisibility',side_effect=lambda c:c=='Window.IsActive(videos)'):
            m.exit.poll(m.nav);m.exit.poll(m.nav)
        self.assertEqual(m.builtins,[]);self.assertEqual(m.exit.state()['phase'],'complete')

    def test_foreign_portal_home_is_not_mistaken_for_requested_home(self):
        m=self.m;m.current_folder='plugin://plugin.video.xtreammate/?action=xcmate_home&pid=other'
        m.exit.request(m.nav);m.finish()
        self.assertEqual(len(m.builtins),1);self.assertIn('pid=p',m.builtins[0])

    def test_twenty_stop_back_home_cycles_allow_only_one_completion_each(self):
        m=self.m
        for i in range(20):
            m.current_folder='plugin://plugin.video.xtreammate/?action=home_live&pid=p'
            m.session=dict(m.session,nonce='session'+str(i));m.tag=json.dumps(m.session)
            m.properties[m.exit.SESSION]=m.tag;m.exit.new_selection();m.playing=True
            m.nav._exiting=False;m.nav._closed=False;m.nav._owned_token=('live',m.session)
            m.exit.request(m.nav);m.exit.request(m.nav);m.finish()
        self.assertEqual(m.stops,20);self.assertEqual(len(m.builtins),20)

    def test_reentrant_directory_completion_is_exactly_once_and_negative_handle_is_idle(self):
        m=self.m;boot=importlib.import_module('boot_diagnostics')
        for _ in range(20):boot.finish_directory(m.router,True,cacheToDisc=False)
        self.assertEqual(len(m.ends),1)
        m.router._handle=-1;m.router._directory_done=False
        boot.finish_directory(m.router,True,cacheToDisc=False);self.assertEqual(len(m.ends),1)


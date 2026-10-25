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


class Timing36(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.timing=importlib.import_module('live_timing')
        self.logs=[];xbmc=sys.modules['xbmc'];xbmc.LOGINFO=1
        p=mock.patch.object(xbmc,'log',side_effect=lambda v,*a:self.logs.append(v),create=True);p.start();self.addCleanup(p.stop)

    def test_route_markers_are_fixed_numeric_and_menu_boundary_is_explicit(self):
        value=self.timing.begin(self.router,menu=True);self.timing.begin(self.router,menu=True)
        self.timing.emit(value,'PLAY_INVOKED',rows=1,private='SECRET',network=0)
        self.assertEqual(sum('IR_MENU_CLICK' in x for x in self.logs),1)
        self.assertEqual(sum('ROUTE_ACCEPTED' in x for x in self.logs),1)
        self.assertIn('menu_route=1',self.logs[0]);self.assertNotIn('SECRET',''.join(self.logs))
        self.timing.emit(value,'PRIVATE');self.assertEqual(len(self.logs),3)

    def test_player_video_marker_requires_matching_item_and_legal_time_state(self):
        session=dict(pid='p',sid='1',nonce='secret-session',at=time.time())
        value=self.timing.begin(self.router);self.timing.bind(value,session)
        player=types.SimpleNamespace(getTime=lambda:0)
        sys.modules['xbmc'].Player=lambda:player
        with mock.patch('playback_exit.identity',return_value=('live',dict(session,nonce='foreign'))):
            self.timing.observe()
        self.assertFalse(any('FIRST_VIDEO' in x for x in self.logs))
        with mock.patch('playback_exit.identity',return_value=('live',session)):
            self.timing.observe();self.timing.observe()
        self.assertEqual(sum('PLAYER_STARTED' in x for x in self.logs),1)
        self.assertEqual(sum('FIRST_VIDEO_DETECTED' in x for x in self.logs),1)
        self.assertNotIn('secret-session',''.join(self.logs))

    def test_infotag_race_is_guarded_and_private_error_is_not_logged(self):
        self.timing.bind(self.timing.begin(self.router),dict(nonce='secret'))
        with mock.patch('playback_exit.identity',side_effect=RuntimeError('PRIVATE no media')):
            for _ in range(20):self.timing.observe()
        self.assertEqual(sum('PLAYER_STATE_UNAVAILABLE' in x for x in self.logs),1)
        self.assertNotIn('PRIVATE',''.join(self.logs))

    def test_remote_and_visible_markers_measure_cold_and_warm_without_layout_change(self):
        nav=types.SimpleNamespace(channels=[1],mode='info')
        self.timing.nav_ready(nav);self.timing.remote(nav,'ok');self.timing.visible(nav)
        self.timing.remote(nav,'ok');self.timing.visible(nav)
        nav.mode='channels';self.timing.remote(nav,'left');self.timing.visible(nav)
        info=[x for x in self.logs if 'INFO_WINDOW_VISIBLE' in x]
        self.assertIn('cold=1',info[0]);self.assertIn('cold=0',info[1])
        self.assertTrue(any('MINI_CHANNELS_VISIBLE' in x for x in self.logs))


"""Owned playback return: real progress SQLite, explicit Kodi window state."""
import importlib
import json
import sys
import time
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture


class ExitTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        sys.modules.pop('playback_exit',None);self.exit=importlib.import_module('playback_exit')
        self.progress=importlib.import_module('media_progress');self.progress._current=self.progress._last=None
        self.session=dict(pid='p',sid='1',nonce='own',at=time.time(),kind='vod')
        self.playing=True;self.media_id='own';self.live_id='';self.position=743;self.duration=2700
        self.stops=[]
        def stop():
            if self.session['kind']!='live':
                self.assertEqual(self.state.progress('p',self.session['kind'],'1',self.session.get('series_id',''),self.session.get('season',''))['position'],743)
            self.stops.append(1);self.playing=False
        self.player=types.SimpleNamespace(isPlayingVideo=lambda:self.playing,getTime=lambda:self.position,
            getTotalTime=lambda:self.duration,stop=stop,getVideoInfoTag=lambda:types.SimpleNamespace(
                getUniqueID=lambda key:self.media_id if key=='xcmate_media' else self.live_id))
        sys.modules['xbmc'].Player=lambda:self.player
        self.properties[self.progress.PROPERTY]=json.dumps(self.session)

    def test_movie_and_episode_return_checkpoint_before_single_stop(self):
        for kind in ('vod','episode'):
            with self.subTest(kind=kind):
                self.playing=True;self.session.update(kind=kind,series_id='series',season='2',episode='3')
                self.properties[self.progress.PROPERTY]=json.dumps(self.session)
                self.assertFalse(self.exit.poll(self.player,fullscreen=True))
                self.assertTrue(self.exit.poll(self.player,fullscreen=False))
                self.assertFalse(self.exit.poll(self.player,fullscreen=False))
                self.assertEqual(self.properties.get(self.progress.PROPERTY,''),'')
        self.assertEqual(len(self.stops),2)

    def test_overlay_back_and_buffering_do_not_stop(self):
        self.assertFalse(self.exit.poll(self.player,fullscreen=False))
        for _ in range(5): self.exit.poll(self.player,fullscreen=True)
        self.assertFalse(self.stops)
        self.assertTrue(self.exit.poll(self.player,fullscreen=False))

    def test_foreign_replacement_wrong_account_and_stale_marker_never_stop(self):
        self.exit.poll(self.player,fullscreen=True)
        self.media_id='foreign';self.assertFalse(self.exit.poll(self.player,fullscreen=False))
        self.media_id='own';self.assertFalse(self.exit.stop_owned(self.player,pid='other'))
        self.session['at']=0;self.properties[self.progress.PROPERTY]=json.dumps(self.session)
        self.assertFalse(self.exit.stop_owned(self.player));self.assertFalse(self.stops)

    def test_item_replacement_during_checkpoint_never_stops_foreign_stream(self):
        def replaced(*args): self.media_id='foreign'
        with mock.patch.object(self.state,'save_progress',side_effect=replaced):
            self.assertFalse(self.exit.stop_owned(self.player))
        self.assertFalse(self.stops)

    def test_final_sample_is_not_overwritten_by_old_periodic_checkpoint(self):
        self.progress._current=dict(self.session);self.progress._last=(700,2700)
        self.assertTrue(self.exit.stop_owned(self.player))
        self.progress.poll(self.player,now=999)
        self.assertEqual(self.state.progress('p','vod','1')['position'],743)

    def test_media_window_reinit_after_fullscreen_stops_owned_movie(self):
        w=self.media_window();w.onInit()
        self.assertEqual(len(self.stops),1)
        w.onInit();self.assertEqual(len(self.stops),1)

    def test_live_overlay_back_does_not_stop_but_actual_navigation_does(self):
        self.session['kind']='live';self.media_id='';self.live_id=json.dumps(self.session)
        self.exit.poll(self.player,fullscreen=True)
        # Dialog-level Back leaves fullscreen visible even when the marker was
        # cleared by closing the overlay; the immutable playing-item tag stays.
        self.properties.pop('XtreamMate.LiveSession',None)
        self.exit.poll(self.player,fullscreen=True);self.assertFalse(self.stops)
        self.assertTrue(self.exit.poll(self.player,fullscreen=False));self.assertEqual(len(self.stops),1)

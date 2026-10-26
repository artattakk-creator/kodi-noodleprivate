"""Exit service keeps ticking under blocked native stop/SQLite; no device claim."""
import importlib
import json
import sys
import threading
import time
import unittest
from unittest import mock
import test_xcmate_exit_040 as legacy


class Exit37(unittest.TestCase):
    def setUp(self):
        self.m=legacy.ExitTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        sys.modules.pop('exit_jobs',None);self.jobs=importlib.import_module('exit_jobs')

    def start(self):
        value=self.jobs.state();value['not_before']=0;self.jobs.save(value);self.jobs.poll()

    def drain(self):
        self.start();self.jobs._thread.join(2)
        self.assertFalse(self.jobs._thread.is_alive())

    def test_native_callback_publishes_without_checkpoint_stop_or_thread(self):
        with mock.patch.object(self.m.state,'save_progress',side_effect=AssertionError('GUI SQLite')):
            self.assertTrue(self.jobs.request(self.m.player))
            self.assertIsNone(self.jobs._thread);self.assertEqual(self.m.stops,[])
        self.assertEqual(self.jobs.state()['phase'],'pending')

    def test_movie_episode_worker_checkpoints_before_exactly_one_stop(self):
        for kind in ('vod','episode'):
            self.m.playing=True;self.m.session.update(nonce=kind,kind=kind,series_id='series',season='1');self.m.media_id=kind
            self.m.properties[self.m.progress.PROPERTY]=json.dumps(self.m.session)
            self.assertTrue(self.jobs.request(self.m.player));self.assertTrue(self.jobs.request(self.m.player))
            self.drain();self.assertEqual(self.jobs.state()['phase'],'complete')
        self.assertEqual(len(self.m.stops),2)

    def test_stuck_native_stop_cannot_block_service_tick_or_spawn_retry(self):
        entered=threading.Event();release=threading.Event();calls=[]
        def stop():calls.append(1);entered.set();release.wait(3)
        self.m.player.stop=stop
        try:
            self.jobs.request(self.m.player);self.start();self.assertTrue(entered.wait(1))
            for _ in range(20):self.assertTrue(self.jobs.poll())
            value=self.jobs.state();value['deadline']=0;self.jobs.save(value)
            self.assertFalse(self.jobs.poll());self.assertEqual(self.jobs.state()['phase'],'timeout')
            self.assertFalse(self.jobs.request(self.m.player));self.assertEqual(calls,[1])
        finally:release.set();self.jobs._thread.join(2)

    def test_player_replacement_after_intent_never_stops_foreign_video(self):
        self.jobs.request(self.m.player);self.m.media_id='foreign';self.drain()
        self.assertEqual(self.m.stops,[]);self.assertEqual(self.jobs.state()['phase'],'failed')

    def test_sqlite_busy_has_bounded_checkpoint_and_does_not_prevent_stop(self):
        self.m.player.stop=lambda:self.m.stops.append(1)
        import sqlite3
        with mock.patch.object(self.m.state,'save_progress',side_effect=sqlite3.OperationalError('locked')) as save:
            self.jobs.request(self.m.player);self.drain()
        self.assertEqual(len(self.m.stops),1);self.assertEqual(save.call_args.kwargs,dict(timeout=.05))

    def test_native_overlay_release_precedes_background_stop(self):
        import test_xcmate_live_stop_02917 as model
        m=model.StopTests(methodName='runTest');m.setUp();self.addCleanup(m.doCleanups)
        sys.modules.pop('exit_jobs',None);jobs=importlib.import_module('exit_jobs')
        original=m.player.stop
        def stop():self.assertTrue(m.nav._closed);original()
        m.player.stop=stop
        m.exit.request(m.nav);m.ready();m.exit._poll(m.nav)
        self.assertTrue(m.nav._closed);self.assertEqual(m.stops,0)
        value=jobs.state();value['not_before']=0;jobs.save(value);jobs.poll();jobs._thread.join(2)
        from exit37_fixture import process_native_live_stop
        process_native_live_stop()
        self.assertEqual(m.stops,1)

    def test_busy_exit_checkpoint_retries_are_finite_and_preserve_existing_bookmark(self):
        import sqlite3
        self.m.state.save_progress(self.m.session,700,2700)
        self.m.player.stop=lambda:self.m.stops.append(1)
        with mock.patch.object(self.m.state,'save_progress',side_effect=sqlite3.OperationalError('locked')) as save:
            self.jobs.request(self.m.player);self.drain()
            for index in range(20):self.m.progress._retry_exit_checkpoint(time.monotonic()+100+index*60)
        self.assertEqual(save.call_count,4)  # Initial snapshot + three bounded retries.
        self.assertEqual(self.m.state.progress('p','vod','1')['position'],700)
